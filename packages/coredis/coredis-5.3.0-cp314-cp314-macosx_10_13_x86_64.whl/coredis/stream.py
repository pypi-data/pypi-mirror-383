from __future__ import annotations

from typing import Any

from deprecated.sphinx import versionadded

from coredis._utils import EncodingInsensitiveDict, nativestr
from coredis.client import Client
from coredis.exceptions import (
    ResponseError,
    StreamConsumerInitializationError,
    StreamDuplicateConsumerGroupError,
)
from coredis.response.types import StreamEntry
from coredis.tokens import PureToken
from coredis.typing import (
    AnyStr,
    ClassVar,
    Generator,
    Generic,
    KeyT,
    MutableMapping,
    Parameters,
    StringT,
    TypedDict,
    ValueT,
)


class StreamParameters(TypedDict):
    #: Starting ``identifier`` for the consumer. If not present it will start
    #: from the latest entry
    identifier: StringT


class State(TypedDict, total=False):
    identifier: StringT | None
    pending: bool | None


class Consumer(Generic[AnyStr]):
    state: MutableMapping[KeyT, State]
    DEFAULT_START_ID: ClassVar[bytes] = b"0-0"

    def __init__(
        self,
        client: Client[AnyStr],
        streams: Parameters[KeyT],
        buffer_size: int = 0,
        timeout: int | None = 0,
        **stream_parameters: StreamParameters,
    ):
        """
        Standalone stream consumer that starts reading from the latest entry
        of each stream provided in :paramref:`streams`.

        The latest entry is determined by calling :meth:`coredis.Redis.xinfo_stream`
        and using the :data:`last-entry` attribute
        at the point of initializing the consumer instance or on first fetch (whichever comes
        first). If the stream(s) do not exist at the time of consumer creation, the
        consumer will simply start from the minimum identifier (``0-0``)

        :param client: The redis client to use
        :param streams: the stream identifiers to consume from
        :param buffer_size: Size of buffer (per stream) to maintain. This
         translates to the maximum number of stream entries that are fetched
         on each request to redis.
        :param timeout: Maximum amount of time in milliseconds to block for new
         entries to appear on the streams the consumer is reading from.
        :param stream_parameters: Mapping of optional parameters to use
         by stream for the streams provided in :paramref:`streams`.
        """
        self.client: Client[AnyStr] = client
        self.streams: set[KeyT] = set(streams)
        self.state: MutableMapping[StringT, State] = EncodingInsensitiveDict(
            {stream: stream_parameters.get(nativestr(stream), {}) for stream in streams}
        )
        self.buffer: MutableMapping[AnyStr, list[StreamEntry]] = EncodingInsensitiveDict({})
        self.buffer_size = buffer_size
        self.timeout = timeout
        self._initialized = False
        self._initialized_streams: dict[StringT, bool] = {}

    def chunk_streams(self) -> list[dict[ValueT, StringT]]:
        import coredis.client

        if isinstance(self.client, coredis.client.RedisCluster):
            return [
                {stream: self.state[stream].get("identifier", None) or self.DEFAULT_START_ID}
                for stream in self.streams
            ]
        else:
            return [
                {
                    stream: self.state[stream].get("identifier", None) or self.DEFAULT_START_ID
                    for stream in self.streams
                }
            ]

    async def initialize(self, partial: bool = False) -> Consumer[AnyStr]:
        if self._initialized and not partial:
            return self

        for stream in self.streams:
            if partial and self._initialized_streams.get(stream):
                continue
            try:
                info = await self.client.xinfo_stream(stream)
                if info:
                    last_entry = info["last-entry"]
                    if last_entry:
                        self.state[stream].setdefault("identifier", last_entry.identifier)
            except ResponseError:
                pass
            self._initialized_streams[stream] = True
        self._initialized = True
        return self

    async def add_stream(self, stream: StringT, identifier: StringT | None = None) -> bool:
        """
        Adds a new stream identifier to this consumer

        :param stream: The stream identifier
        :return: ``True`` if the stream was added successfully, ``False`` otherwise
        """
        self.streams.add(stream)
        self.state.setdefault(stream, {"identifier": identifier} if identifier else {})
        await self.initialize(partial=True)
        return stream in self._initialized_streams

    def __await__(self) -> Generator[Any, None, Consumer[AnyStr]]:
        return self.initialize().__await__()

    def __aiter__(self) -> Consumer[AnyStr]:
        """
        Returns the instance of the consumer itself which can be iterated over
        """
        return self

    async def __anext__(self) -> tuple[AnyStr, StreamEntry]:
        """
        Returns the next available stream entry available from any of
        :paramref:`Consumer.streams`.

        :raises: :exc:`StopIteration` if no more entries are available
        """
        stream, entry = await self.get_entry()
        if not (stream and entry):
            raise StopAsyncIteration()
        return stream, entry

    async def get_entry(self) -> tuple[AnyStr | None, StreamEntry | None]:
        """
        Fetches the next available entry from the streams specified in
        :paramref:`Consumer.streams`. If there were any entries
        previously fetched and buffered, they will be returned before
        making a new request to the server.
        """
        await self.initialize()
        cur = None
        cur_stream = None
        for stream, buffer_entries in list(self.buffer.items()):
            if buffer_entries:
                cur_stream, cur = stream, self.buffer[stream].pop(0)
                break
        else:
            consumed_entries: dict[AnyStr, tuple[StreamEntry, ...]] = {}
            for chunk in self.chunk_streams():
                consumed_entries.update(
                    await self.client.xread(
                        chunk,
                        count=self.buffer_size + 1,
                        block=(self.timeout if (self.timeout and self.timeout > 0) else None),
                    )
                    or {}
                )
            for stream, entries in consumed_entries.items():
                if entries:
                    if not cur:
                        cur = entries[0]
                        cur_stream = stream
                        if entries[1:]:
                            self.buffer.setdefault(stream, []).extend(entries[1:])
                    else:
                        self.buffer.setdefault(stream, []).extend(entries)
        if cur and cur_stream:
            self.state[cur_stream]["identifier"] = cur.identifier
        return cur_stream, cur


class GroupConsumer(Consumer[AnyStr]):
    DEFAULT_START_ID: ClassVar[bytes] = b">"

    def __init__(
        self,
        client: Client[AnyStr],
        streams: Parameters[KeyT],
        group: StringT,
        consumer: StringT,
        buffer_size: int = 0,
        auto_create: bool = True,
        auto_acknowledge: bool = False,
        start_from_backlog: bool = False,
        timeout: int | None = None,
        **stream_parameters: StreamParameters,
    ):
        """
        A member of a stream consumer group. The consumer has an identical
        interface as :class:`coredis.stream.Consumer`.

        :param client: The redis client to use
        :param streams: The stream identifiers to consume from
        :param group: The name of the group this consumer is part of
        :param consumer: The unique name (within :paramref:`group`) of the consumer
        :param auto_create: If True the group will be created upon initialization
         or first fetch if it doesn't already exist.
        :param auto_acknowledge: If ``True`` the stream entries fetched will be fetched
         without needing to be acknowledged with :meth:`coredis.Redis.xack` to remove
         them from the pending entries list.
        :param start_from_backlog: If ``True`` the consumer will start by fetching any pending
         entries from the pending entry list before considering any new messages
         not seen by any other consumer in the :paramref:`group`
        :param buffer_size: Size of buffer (per stream) to maintain. This
         translates to the maximum number of stream entries that are fetched
         on each request to redis.
        :param timeout: Maximum amount of time to block for new
         entries to appear on the streams the consumer is reading from.
        :param stream_parameters: Mapping of optional parameters to use
         by stream for the streams provided in :paramref:`streams`.


        .. warning:: Providing an ``identifier`` in ``stream_parameters`` has a different
           meaning for a group consumer. If the value is any valid identifier other than ``>``
           the consumer will only access the history of pending messages. That is, the set of
           messages that were delivered to this consumer (identified by :paramref:`consumer`)
           and never acknowledged.
        """
        super().__init__(
            client,  # type: ignore[arg-type]
            streams,
            buffer_size,
            timeout,
            **stream_parameters,
        )
        self.group = group
        self.consumer = consumer
        self.auto_create = auto_create
        self.auto_acknowledge = auto_acknowledge
        self.start_from_backlog = start_from_backlog

    async def initialize(self, partial: bool = False) -> GroupConsumer[AnyStr]:
        if not self._initialized or partial:
            group_presence: dict[KeyT, bool] = {
                stream: stream in self._initialized_streams for stream in self.streams
            }
            for stream in self.streams:
                try:
                    if self._initialized_streams.get(stream):
                        continue
                    group_presence[stream] = (
                        len(
                            [
                                info
                                for info in [
                                    EncodingInsensitiveDict(d)
                                    for d in await self.client.xinfo_groups(stream)
                                ]
                                if nativestr(info["name"]) == self.group
                            ]
                        )
                        == 1
                    )
                    if group_presence[stream] and self.start_from_backlog:
                        self.state[stream]["pending"] = True
                        self.state[stream]["identifier"] = "0-0"
                except ResponseError:
                    self.state[stream].setdefault("identifier", ">")

            if not (self.auto_create or all(group_presence.values())):
                missing_streams = self.streams - {
                    k for k in group_presence if not group_presence[k]
                }
                raise StreamConsumerInitializationError(
                    f"Consumer group: {self.group!r} does not exist for streams: {missing_streams}"
                )
            for stream in self.streams:
                if self.auto_create and not group_presence.get(stream):
                    try:
                        await self.client.xgroup_create(
                            stream, self.group, PureToken.NEW_ID, mkstream=True
                        )
                    except StreamDuplicateConsumerGroupError:  # noqa
                        pass
                self._initialized_streams[stream] = True
                self.state[stream].setdefault("identifier", ">")

            self._initialized = True
        return self

    @versionadded(version="4.12.0")
    async def add_stream(self, stream: StringT, identifier: StringT | None = ">") -> bool:
        """
        Adds a new stream identifier to this consumer

        :param stream: The stream identifier
        :param identifier: The identifier to start consuming from. For group
         consumers this should almost always be ``>`` (the default).

        :return: ``True`` if the stream was added successfully, ``False`` otherwise
        """
        return await super().add_stream(stream, identifier)

    def __await__(self) -> Generator[Any, None, GroupConsumer[AnyStr]]:
        return self.initialize().__await__()

    def __aiter__(self) -> GroupConsumer[AnyStr]:
        """
        Returns the instance of the consumer itself which can be iterated over
        """
        return self

    async def get_entry(self) -> tuple[AnyStr | None, StreamEntry | None]:
        """
        Fetches the next available entry from the streams specified in
        :paramref:`GroupConsumer.streams`. If there were any entries
        previously fetched and buffered, they will be returned before
        making a new request to the server.
        """
        await self.initialize()

        cur = None
        cur_stream = None
        for stream, buffer_entries in list(self.buffer.items()):
            if buffer_entries:
                cur_stream, cur = stream, self.buffer[stream].pop(0)
                break
        else:
            consumed_entries: dict[AnyStr, tuple[StreamEntry, ...]] = {}
            for chunk in self.chunk_streams():
                consumed_entries.update(
                    await self.client.xreadgroup(
                        self.group,
                        self.consumer,
                        count=self.buffer_size + 1,
                        block=(self.timeout if (self.timeout and self.timeout > 0) else None),
                        noack=self.auto_acknowledge,
                        streams=chunk,
                    )
                    or {}
                )
            for stream, entries in consumed_entries.items():
                if entries:
                    if not cur:
                        cur = entries[0]
                        cur_stream = stream
                        if entries[1:]:
                            self.buffer.setdefault(stream, []).extend(entries[1:])

                    else:
                        self.buffer.setdefault(stream, []).extend(entries)
                    if self.state[stream].get("pending"):
                        self.state[stream]["identifier"] = entries[-1].identifier
                else:
                    if self.state[stream].get("pending"):
                        self.state[stream].pop("identifier", None)
                        self.state[stream].pop("pending", None)
                        if not cur:
                            return await self.get_entry()
        return cur_stream, cur
