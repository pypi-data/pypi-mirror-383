from __future__ import annotations

import asyncio
import base64
import copy
import hashlib
from dataclasses import dataclass, field

from suplalite import encoding, proto
from suplalite.server.events import EventQueue


class ServerState:
    def __init__(self) -> None:
        self._started = False
        self._lock = asyncio.Lock()

        self._next_client_id = 1
        self._client_guid_to_id: dict[str, int] = {}
        self._clients: dict[int, ClientState] = {}
        self._client_connections: set[int] = set()
        self._client_events: dict[int, EventQueue] = {}

        self._device_guid_to_id: dict[str, int] = {}
        self._devices: dict[int, DeviceState] = {}
        self._channels: dict[int, ChannelState] = {}
        self._device_connections: set[int] = set()
        self._device_events: dict[int, EventQueue] = {}

        self._icons: dict[str, Icon] = {}
        self._icons_by_id: dict[int, Icon] = {}

        self._scenes: dict[int, SceneState] = {}

    def server_started(self) -> None:
        self._started = True

    @property
    def lock(self) -> asyncio.Lock:
        return self._lock

    def add_client(self, guid: bytes) -> int:
        if str(guid) in self._client_guid_to_id:
            return self._client_guid_to_id[str(guid)]
        client_id = self._next_client_id
        self._next_client_id += 1
        self._clients[client_id] = ClientState(client_id, guid, False)
        self._client_guid_to_id[str(guid)] = client_id
        return client_id

    def client_connected(self, client_id: int, events: EventQueue) -> bool:
        if client_id in self._client_connections:
            return False
        self._client_connections.add(client_id)
        self._client_events[client_id] = events
        self._clients[client_id].online = True
        self._clients[client_id].authorized = False
        return True

    def client_disconnected(self, client_id: int) -> None:
        self._client_connections.remove(client_id)
        del self._client_events[client_id]
        self._clients[client_id].online = False
        self._clients[client_id].authorized = False
        self._clients[client_id].sent_channels = False
        self._clients[client_id].next_channel_batch = 0
        self._clients[client_id].sent_channel_relations = False
        self._clients[client_id].sent_scenes = False
        self._clients[client_id].next_scene_batch = 0

    def set_client_authorized(self, client_id: int) -> None:
        self._clients[client_id].authorized = True

    def set_client_sent_channels(self, client_id: int) -> None:
        self._clients[client_id].sent_channels = True

    def set_client_next_channel_batch(self, client_id: int) -> None:
        self._clients[client_id].next_channel_batch += 1

    def set_client_sent_channel_relations(self, client_id: int) -> None:
        self._clients[client_id].sent_channel_relations = True

    def set_client_sent_scenes(self, client_id: int) -> None:
        self._clients[client_id].sent_scenes = True

    def set_client_next_scene_batch(self, client_id: int) -> None:
        self._clients[client_id].next_scene_batch += 1

    def get_clients(self) -> dict[int, ClientState]:
        return copy.deepcopy(self._clients)

    def get_client(self, client_id: int) -> ClientState:
        return copy.deepcopy(self._clients[client_id])

    def get_client_events(self, client_id: int) -> EventQueue:
        return self._client_events[client_id]

    def get_device_id(self, guid: bytes) -> int:
        return self._device_guid_to_id[str(guid)]

    def add_device(
        self,
        name: str,
        guid: bytes,
        manufacturer_id: int,
        product_id: int,
    ) -> int:
        assert self._started is False
        device_id = len(self._devices) + 1
        device = DeviceState(
            name,
            device_id,
            guid,
            False,
            manufacturer_id,
            product_id,
            proto.PROTO_VERSION,
        )
        self._devices[device_id] = device
        self._device_guid_to_id[str(guid)] = device_id
        return device_id

    def add_channel(
        self,
        device_id: int,
        name: str,
        caption: str,
        typ: proto.ChannelType,
        func: proto.ChannelFunc,
        flags: proto.ChannelFlag,
        alt_icon: int = 0,
        config: ChannelConfig | None = None,
        icons: list[bytes] | None = None,
    ) -> int:
        assert self._started is False
        channel_id = len(self._channels) + 1

        user_icon = 0
        if icons is not None:
            user_icon = self.add_icons(icons)

        channel = ChannelState(
            name,
            channel_id,
            device_id,
            caption,
            typ,
            func,
            flags,
            alt_icon,
            user_icon,
            config,
        )
        self._channels[channel_id] = channel
        self._devices[device_id].channel_ids.append(channel_id)
        return channel_id

    def add_icons(self, icons: list[bytes]) -> int:
        data = [base64.b64encode(icon).decode() for icon in icons]
        key = ",".join(data)
        if key in self._icons:
            return self._icons[key].id

        # Generate a 6-bit integer from the hash of the icon data
        # to provide a unique id based on the content of the image.
        # The SUPLA app caches images based on id number, so the id number
        # needs to change if the image content changes
        icon_id = int(hashlib.sha1(key.encode("utf-8")).hexdigest()[:6], 16)
        icon = Icon(icon_id, data)
        self._icons[key] = icon
        self._icons_by_id[icon.id] = icon
        return icon.id

    def get_icons(self) -> list[Icon]:
        return copy.deepcopy(list(self._icons.values()))

    def get_icon(self, icon_id: int) -> Icon:
        return self._icons_by_id[icon_id]

    def get_devices(self) -> dict[int, DeviceState]:
        return copy.deepcopy(self._devices)

    def get_channels(self) -> dict[int, ChannelState]:
        return copy.deepcopy(self._channels)

    def get_device(self, device_id: int) -> DeviceState:
        return copy.deepcopy(self._devices[device_id])

    def get_device_channels(self, device_id: int) -> dict[int, ChannelState]:
        return copy.deepcopy(
            {
                channel.id: channel
                for channel in self._channels.values()
                if channel.device_id == device_id
            }
        )

    def get_channel(self, channel_id: int) -> ChannelState:
        return copy.deepcopy(self._channels[channel_id])

    def get_channel_by_name(self, name: str) -> ChannelState:
        for channel in self._channels.values():
            if channel.name == name:
                return copy.deepcopy(channel)
        raise KeyError

    def device_connected(
        self, device_id: int, proto_version: int, events: EventQueue
    ) -> bool:
        if device_id in self._device_connections:
            return False
        self._device_connections.add(device_id)
        self._device_events[device_id] = events
        self._devices[device_id].online = True
        self._devices[device_id].proto_version = proto_version
        return True

    def device_disconnected(self, device_id: int) -> None:
        self._device_connections.remove(device_id)
        del self._device_events[device_id]
        self._devices[device_id].online = False

    def set_channel_value(self, channel_id: int, value: bytes) -> None:
        self._channels[channel_id].value = value
        # Note: if the value is non-zero, save the value as the "last value"
        # For example, used to preserve dimmer brightness across on/off actions
        if self._should_set_last(self._channels[channel_id].type, value):
            self._channels[channel_id].last_value = value

    def _should_set_last(self, channel_type: proto.ChannelType, value: bytes) -> bool:
        if channel_type == proto.ChannelType.DIMMER:
            return encoding.decode(proto.TDimmerChannel_Value, value)[0].brightness > 0
        return False

    def get_device_events(self, device_id: int) -> EventQueue:
        return self._device_events[device_id]

    def add_scene(
        self,
        name: str,
        caption: str,
        channels: list[SceneChannelState],
        alt_icon: int = 0,
        icons: list[bytes] | None = None,
    ) -> None:
        assert self._started is False
        scene_id = len(self._scenes) + 1

        user_icon = 0
        if icons is not None:
            user_icon = self.add_icons(icons)

        self._scenes[scene_id] = SceneState(
            name, scene_id, caption, alt_icon, user_icon, channels
        )

    def get_scenes(self) -> dict[int, SceneState]:
        return copy.deepcopy(self._scenes)

    def get_scene(self, scene_id: int) -> SceneState:
        return copy.deepcopy(self._scenes[scene_id])


@dataclass
class ClientState:
    id: int
    guid: bytes
    online: bool
    authorized: bool = False
    sent_channels: bool = False
    next_channel_batch: int = 0
    sent_channel_relations: bool = False
    sent_scenes: bool = False
    next_scene_batch: int = 0


@dataclass
class DeviceState:
    name: str
    id: int
    guid: bytes
    online: bool
    manufacturer_id: int
    product_id: int
    proto_version: int
    channel_ids: list[int] = field(default_factory=list)


@dataclass
class ChannelConfig:
    pass


@dataclass
class GeneralPurposeMeasurementChannelConfig(ChannelConfig):
    value_divider: int = 0
    value_multiplier: int = 0
    value_added: int = 0
    value_precision: int = 0
    unit_before_value: str = ""
    unit_after_value: str = ""
    no_space_before_value: bool = True
    no_space_after_value: bool = True


@dataclass
class ChannelState:
    name: str
    id: int
    device_id: int
    caption: str
    type: proto.ChannelType
    func: proto.ChannelFunc
    flags: proto.ChannelFlag
    alt_icon: int
    user_icon: int
    config: ChannelConfig | None
    value: bytes = b"\x00\x00\x00\x00\x00\x00\x00\x00"
    last_value: bytes | None = None


@dataclass
class SceneState:
    name: str
    id: int
    caption: str
    alt_icon: int
    user_icon: int
    channels: list[SceneChannelState] = field(default_factory=list)


@dataclass
class SceneChannelState:
    name: str
    action: proto.ActionType
    params: bytes | None = None


@dataclass
class Icon:
    id: int
    data: list[str]
