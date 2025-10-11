"""Device capabilities module."""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field, fields, is_dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

from deebot_client.events import (
    AdvancedModeEvent,
    AvailabilityEvent,
    BatteryEvent,
    BorderSwitchEvent,
    CachedMapInfoEvent,
    CarpetAutoFanBoostEvent,
    ChildLockEvent,
    CleanCountEvent,
    CleanLogEvent,
    CleanPreferenceEvent,
    ContinuousCleaningEvent,
    CrossMapBorderWarningEvent,
    CustomCommandEvent,
    CutDirectionEvent,
    ErrorEvent,
    Event,
    FanSpeedEvent,
    FanSpeedLevel,
    LifeSpan,
    LifeSpanEvent,
    MajorMapEvent,
    MapChangedEvent,
    MapSetType,
    MapTraceEvent,
    MoveUpWarningEvent,
    MultimapStateEvent,
    NetworkInfoEvent,
    OtaEvent,
    PositionsEvent,
    ReportStatsEvent,
    RoomsEvent,
    SafeProtectEvent,
    StateEvent,
    StationEvent,
    StatsEvent,
    SweepModeEvent,
    TotalStatsEvent,
    TrueDetectEvent,
    VoiceAssistantStateEvent,
    VolumeEvent,
    WorkMode,
    WorkModeEvent,
    auto_empty,
    water_info,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from _typeshed import DataclassInstance

    from deebot_client.command import Command, CommandWithMessageHandling
    from deebot_client.commands import StationAction
    from deebot_client.events.efficiency_mode import EfficiencyMode, EfficiencyModeEvent
    from deebot_client.models import CleanAction, CleanMode


def _get_events(
    capabilities: DataclassInstance | type[DataclassInstance],
) -> MappingProxyType[type[Event], list[Command]]:
    events = {}
    for field_ in fields(capabilities):
        if not field_.init:
            continue
        field_value = getattr(capabilities, field_.name)
        if isinstance(field_value, CapabilityEvent):
            events[field_value.event] = field_value.get
        elif is_dataclass(field_value):
            events.update(_get_events(field_value))

    return MappingProxyType(events)


@dataclass(frozen=True)
class CapabilityEvent[E: Event]:
    """Capability for an event with get command."""

    event: type[E]
    get: list[Command]


@dataclass(frozen=True)
class CapabilitySet[E: Event, **P](CapabilityEvent[E]):
    """Capability setCommand with event."""

    set: Callable[P, CommandWithMessageHandling]


@dataclass(frozen=True)
class CapabilitySetEnable[E: Event](CapabilitySet[E, [bool]]):
    """Capability for SetEnableCommand with event."""


@dataclass(frozen=True)
class CapabilityExecute[**P]:
    """Capability to execute a command."""

    execute: Callable[P, Command]


@dataclass(frozen=True, kw_only=True)
class CapabilityTypes[T]:
    """Capability to specify types support."""

    types: tuple[T, ...]


@dataclass(frozen=True, kw_only=True)
class CapabilityExecuteTypes[T](CapabilityTypes[T], CapabilityExecute[[T]]):
    """Capability to execute a command with types."""


@dataclass(frozen=True, kw_only=True)
class CapabilitySetTypes[E: Event, **P, T](CapabilitySet[E, P], CapabilityTypes[T]):
    """Capability for set command and types."""


@dataclass(frozen=True, kw_only=True)
class CapabilityNumber[E: Event, **P](CapabilitySet[E, P]):
    """Capability for a number entity with min and max."""

    min: int
    max: int


@dataclass(frozen=True, kw_only=True)
class CapabilityCleanAction:
    """Capabilities for clean action."""

    command: Callable[[CleanAction], Command]
    area: Callable[[CleanMode, str, int], Command] | None = None


@dataclass(frozen=True, kw_only=True)
class CapabilityClean:
    """Capabilities for clean."""

    action: CapabilityCleanAction
    continuous: CapabilitySetEnable[ContinuousCleaningEvent] | None = None
    count: CapabilitySet[CleanCountEvent, [int]] | None = None
    log: CapabilityEvent[CleanLogEvent] | None = None
    preference: CapabilitySetEnable[CleanPreferenceEvent] | None = None
    work_mode: CapabilitySetTypes[WorkModeEvent, [WorkMode | str], WorkMode] | None = (
        None
    )


@dataclass(frozen=True)
class CapabilityCustomCommand[E: Event](CapabilityEvent[E]):
    """Capability custom command."""

    set: Callable[[str, Any], Command]


@dataclass(frozen=True, kw_only=True)
class CapabilityLifeSpan(CapabilityEvent[LifeSpanEvent], CapabilityTypes[LifeSpan]):
    """Capabilities for life span."""

    reset: Callable[[LifeSpan], Command]


@dataclass(frozen=True, kw_only=True)
class CapabilityMap:
    """Capabilities for map."""

    cached_info: CapabilityEvent[CachedMapInfoEvent]
    changed: CapabilityEvent[MapChangedEvent]
    clear: CapabilityExecute[[]] | None = None
    major: CapabilityEvent[MajorMapEvent] | CapabilitySet[MajorMapEvent, [str]]
    minor: CapabilityExecute[[int, str]]
    multi_state: CapabilitySetEnable[MultimapStateEvent] | None = None
    position: CapabilityEvent[PositionsEvent]
    relocation: CapabilityExecute[[]] | None = None
    rooms: CapabilityEvent[RoomsEvent]
    set: CapabilityExecute[[str, MapSetType]]
    trace: CapabilityEvent[MapTraceEvent]


@dataclass(frozen=True, kw_only=True)
class CapabilityStats:
    """Capabilities for statistics."""

    clean: CapabilityEvent[StatsEvent]
    report: CapabilityEvent[ReportStatsEvent]
    total: CapabilityEvent[TotalStatsEvent]


@dataclass(frozen=True, kw_only=True)
class CapabilitySettings:
    """Capabilities for settings."""

    advanced_mode: CapabilitySetEnable[AdvancedModeEvent] | None = None
    carpet_auto_fan_boost: CapabilitySetEnable[CarpetAutoFanBoostEvent] | None = None
    efficiency_mode: (
        CapabilitySetTypes[EfficiencyModeEvent, [EfficiencyMode | str], EfficiencyMode]
        | None
    ) = None
    border_switch: CapabilitySetEnable[BorderSwitchEvent] | None = None
    child_lock: CapabilitySetEnable[ChildLockEvent] | None = None
    cut_direction: CapabilitySet[CutDirectionEvent, [int]] | None = None
    moveup_warning: CapabilitySetEnable[MoveUpWarningEvent] | None = None
    cross_map_border_warning: CapabilitySetEnable[CrossMapBorderWarningEvent] | None = (
        None
    )
    safe_protect: CapabilitySetEnable[SafeProtectEvent] | None = None
    ota: CapabilitySetEnable[OtaEvent] | CapabilityEvent[OtaEvent] | None = None
    sweep_mode: CapabilitySetEnable[SweepModeEvent] | None = None
    true_detect: CapabilitySetEnable[TrueDetectEvent] | None = None
    voice_assistant: CapabilitySetEnable[VoiceAssistantStateEvent] | None = None
    volume: CapabilitySet[VolumeEvent, [int]] | None = None


@dataclass(frozen=True, kw_only=True)
class CapabilityStation:
    """Capabilities for the station."""

    action: CapabilityExecuteTypes[StationAction]
    auto_empty: CapabilitySetTypes[
        auto_empty.AutoEmptyEvent,
        [bool | None, auto_empty.Frequency | str | None],
        auto_empty.Frequency,
    ]
    state: CapabilityEvent[StationEvent]


@dataclass(frozen=True, kw_only=True)
class CapabilityWater:
    """Capabilities for water."""

    amount: (
        CapabilitySetTypes[
            water_info.WaterAmountEvent,
            [water_info.WaterAmount | str],
            water_info.WaterAmount,
        ]
        | CapabilityNumber[water_info.WaterCustomAmountEvent, [int]]
    )
    mop_attached: CapabilityEvent[water_info.MopAttachedEvent]


@dataclass(frozen=True, kw_only=True)
class Capabilities(ABC):
    """Capabilities."""

    device_type: DeviceType = field(kw_only=False)

    availability: CapabilityEvent[AvailabilityEvent]
    battery: CapabilityEvent[BatteryEvent]
    charge: CapabilityExecute[[]]
    clean: CapabilityClean
    custom: CapabilityCustomCommand[CustomCommandEvent]
    error: CapabilityEvent[ErrorEvent]
    fan_speed: (
        CapabilitySetTypes[FanSpeedEvent, [FanSpeedLevel | str], FanSpeedLevel] | None
    ) = None
    life_span: CapabilityLifeSpan
    map: CapabilityMap | None = None
    network: CapabilityEvent[NetworkInfoEvent]
    play_sound: CapabilityExecute[[]]
    settings: CapabilitySettings
    state: CapabilityEvent[StateEvent]
    station: CapabilityStation | None = None
    stats: CapabilityStats
    water: CapabilityWater | None = None

    _events: MappingProxyType[type[Event], list[Command]] = field(init=False)

    def __post_init__(self) -> None:
        """Post init."""
        object.__setattr__(self, "_events", _get_events(self))

    def get_refresh_commands(self, event: type[Event]) -> list[Command]:
        """Return refresh command for given event."""
        return self._events.get(event, [])


class DeviceType(StrEnum):
    """Device type."""

    VACUUM = "vacuum"
    MOWER = "mower"
