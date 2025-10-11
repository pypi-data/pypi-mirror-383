"""Device module."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from contextlib import suppress
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Final

from deebot_client.events.network import NetworkInfoEvent
from deebot_client.message import HandlingState
from deebot_client.mqtt_client import MqttClient, SubscriberInfo
from deebot_client.util import cancel

from .command import Command
from .event_bus import EventBus
from .events import (
    AvailabilityEvent,
    CleanLogEvent,
    CustomCommandEvent,
    FirmwareEvent,
    LifeSpanEvent,
    PositionsEvent,
    StateEvent,
    StatsEvent,
    TotalStatsEvent,
)
from .logging_filter import get_logger
from .map import Map
from .messages import get_message
from .models import DeviceInfo, State
from .rs.map import PositionType

if TYPE_CHECKING:
    from .authentication import Authenticator
    from .command import DeviceCommandResult
    from .message import MessagePayloadType

_LOGGER = get_logger(__name__)
_AVAILABLE_CHECK_INTERVAL = 60

DeviceCommandExecute = Callable[[Command], Coroutine[Any, Any, dict[str, Any]]]


class Device:
    """Device representation."""

    def __init__(
        self,
        device_info: DeviceInfo,
        authenticator: Authenticator,
    ) -> None:
        self._device_info = device_info
        self.device_info: Final = device_info.api
        self.capabilities: Final = device_info.static.capabilities
        self._authenticator = authenticator

        self._semaphore = asyncio.Semaphore(3)
        self._state: StateEvent | None = None
        self._last_time_available: datetime = datetime.now(tz=UTC)
        self._available_task: asyncio.Task[Any] | None = None
        self._running_tasks: set[asyncio.Future[Any]] = set()
        self._unsubscribe: Callable[[], None] | None = None

        self.fw_version: str | None = None
        self.mac: str | None = None
        self.events: Final[EventBus] = EventBus(self.execute_command, self.capabilities)

        self.map: Final[Map | None] = (
            Map(self.execute_command, self.events, self.capabilities.map)
            if self.capabilities.map
            else None
        )

        async def on_pos(event: PositionsEvent) -> None:
            if self._state == StateEvent(State.DOCKED):
                return

            deebot = next(
                (p for p in event.positions if p.type == PositionType.DEEBOT), None
            )

            if deebot and any(
                p
                for p in event.positions
                if p.type == PositionType.CHARGER
                and p.x == deebot.x
                and p.y == deebot.y
            ):
                # Deebot is on charger and the status is not docked
                # Request refresh for the state
                self.events.request_refresh(StateEvent)

        self.events.subscribe(PositionsEvent, on_pos)

        async def on_state(event: StateEvent) -> None:
            if event.state == State.DOCKED:
                self.events.request_refresh(CleanLogEvent)
                self.events.request_refresh(TotalStatsEvent)

        self.events.subscribe(StateEvent, on_state)

        async def on_stats(_: StatsEvent) -> None:
            self.events.request_refresh(LifeSpanEvent)

        self.events.subscribe(StatsEvent, on_stats)

        async def on_custom_command(event: CustomCommandEvent) -> None:
            self._handle_message(event.name, event.response)

        self.events.subscribe(CustomCommandEvent, on_custom_command)

        async def on_network(event: NetworkInfoEvent) -> None:
            self.mac = event.mac

        self.events.subscribe(NetworkInfoEvent, on_network)

        async def on_firmware(event: FirmwareEvent) -> None:
            self.fw_version = event.version

        self.events.subscribe(FirmwareEvent, on_firmware)

    async def execute_command(self, command: Command) -> dict[str, Any]:
        """Execute given command.

        Returns
        -------
            command_response (dict[str, Any]) The command raw response.

        """
        return (await self._execute_command(command)).raw_response

    async def initialize(self, client: MqttClient) -> None:
        """Initialize vacumm bot, which includes MQTT-subscription and starting the available check."""
        if self._unsubscribe is None:
            self._unsubscribe = await client.subscribe(
                SubscriberInfo(self._device_info, self.events, self._handle_message)
            )

        if self._available_task is None or self._available_task.done():
            self._available_task = asyncio.create_task(self._available_task_worker())
            self._running_tasks.add(self._available_task)
            self._available_task.add_done_callback(self._running_tasks.discard)

    async def teardown(self) -> None:
        """Tear down bot including stopping task and unsubscribing."""
        if self._unsubscribe:
            self._unsubscribe()
            self._unsubscribe = None

        for task in self._running_tasks.copy():
            if task.cancel():
                with suppress(asyncio.CancelledError):
                    await task
        self._running_tasks.clear()

        await self.events.teardown()
        if self.map:
            await self.map.teardown()

    async def _available_task_worker(self) -> None:
        while True:
            if (datetime.now(tz=UTC) - self._last_time_available).total_seconds() > (
                _AVAILABLE_CHECK_INTERVAL - 1
            ):
                tasks: set[asyncio.Future[Any]] = set()
                try:
                    for command in self.capabilities.get_refresh_commands(
                        AvailabilityEvent
                    ):
                        tasks.add(asyncio.create_task(self._execute_command(command)))

                    result = await asyncio.gather(*tasks)
                    self._set_available(available=all(r.device_reached for r in result))
                except Exception:
                    _LOGGER.debug(
                        "An exception occurred during the available check",
                        exc_info=True,
                    )
                    await cancel(tasks)
            await asyncio.sleep(_AVAILABLE_CHECK_INTERVAL)

    async def _execute_command(
        self,
        command: Command,
    ) -> DeviceCommandResult:
        """Execute given command."""
        async with self._semaphore:
            result = await command.execute(
                self._authenticator, self.device_info, self.events
            )
            if result.device_reached:
                self._set_available(available=True)

            return result

    def _set_available(self, *, available: bool) -> None:
        """Set available."""
        if available:
            self._last_time_available = datetime.now(tz=UTC)

        self.events.notify(AvailabilityEvent(available=available))

    def _create_request_command_task(self, requested_commands: list[Command]) -> None:
        """Create a task to execute the requested commands."""

        async def task_group_runner() -> None:
            async with asyncio.TaskGroup() as tg:
                for cmd in requested_commands:
                    tg.create_task(self._execute_command(cmd))

        task = asyncio.create_task(task_group_runner())
        self._running_tasks.add(task)
        task.add_done_callback(self._running_tasks.discard)

    def _handle_message(
        self, message_name: str, message_data: MessagePayloadType
    ) -> None:
        """Handle the given message.

        :param message_name: message name
        :param message_data: message data
        :return: None
        """
        self._set_available(available=True)

        try:
            _LOGGER.debug("Try to handle message %s: %s", message_name, message_data)

            if message := get_message(message_name, self._device_info.static.data_type):
                result = message.handle(self.events, message_data)
                if result.state == HandlingState.SUCCESS and result.requested_commands:
                    _LOGGER.debug(
                        "Message %s requested commands: %s",
                        message_name,
                        result.requested_commands,
                    )
                    self._create_request_command_task(result.requested_commands)

        except Exception:
            _LOGGER.exception("An exception occurred during handling message")
