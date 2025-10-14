import asyncio
from enum import Enum
from typing import Any


class EventContext(Enum):
    SERVER = 0
    DEVICE = 1
    CLIENT = 2


class EventId(Enum):
    CLIENT_CONNECTED = 0
    CLIENT_DISCONNECTED = 1
    DEVICE_CONNECTED = 2
    DEVICE_DISCONNECTED = 3
    SEND_LOCATIONS = 4
    SEND_CHANNELS = 5
    SEND_CHANNEL_RELATIONS = 6
    SEND_SCENES = 7
    GET_CHANNEL_STATE = 8
    CHANNEL_STATE_RESULT = 9
    CHANNEL_REGISTER_VALUE = 10
    CHANNEL_VALUE_CHANGED = 11
    CHANNEL_SET_VALUE = 12
    DEVICE_CONFIG = 13
    DEVICE_CONFIG_RESULT = 14
    REQUEST = 15
    RESPONSE = 16


Payload = tuple[Any, ...] | None


class EventQueue:
    def __init__(self) -> None:
        self._queue = asyncio.Queue[tuple[EventId, Payload]]()

    async def add(self, event_id: EventId, payload: Payload = None) -> None:
        await self._queue.put((event_id, payload))

    async def get(self) -> tuple[EventId, Payload]:
        return await self._queue.get()
