"""Models module."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum, unique
from typing import TYPE_CHECKING, Required, TypedDict

from deebot_client.util.enum import StrEnumWithXml

if TYPE_CHECKING:
    from deebot_client.capabilities import Capabilities
    from deebot_client.const import DataType

ApiDeviceInfo = TypedDict(
    "ApiDeviceInfo",
    {
        "class": Required[str],
        "company": Required[str],
        "deviceName": str,
        "did": Required[str],
        "name": Required[str],
        "nick": str,
        "resource": Required[str],
    },
    total=False,
)


@dataclass(frozen=True)
class StaticDeviceInfo:
    """Static device info."""

    data_type: DataType
    capabilities: Capabilities


@dataclass(frozen=True)
class DeviceInfo:
    """Device info."""

    api: ApiDeviceInfo
    static: StaticDeviceInfo


@dataclass(frozen=True)
class Room:
    """Room representation."""

    name: str
    id: int
    coordinates: str


@unique
class State(IntEnum):
    """State representation."""

    IDLE = 1
    CLEANING = 2
    RETURNING = 3
    DOCKED = 4
    ERROR = 5
    PAUSED = 6


@unique
class CleanAction(StrEnumWithXml):
    """Enum class for all possible clean actions."""

    START = "start", "s"
    PAUSE = "pause", "p"
    RESUME = "resume", "r"
    STOP = "stop", "h"


@unique
class CleanMode(StrEnumWithXml):
    """Enum class for all possible clean modes."""

    AUTO = "auto", "auto"
    SPOT_AREA = "spotArea", "SpotArea"
    CUSTOM_AREA = "customArea", "spot"


@dataclass(frozen=True)
class Credentials:
    """Credentials representation."""

    token: str
    user_id: str
    expires_at: int = 0
