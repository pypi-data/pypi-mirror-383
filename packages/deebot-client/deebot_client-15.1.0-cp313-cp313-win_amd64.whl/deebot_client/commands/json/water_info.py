"""Water info commands."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING, Any

from deebot_client.command import InitParam
from deebot_client.events.water_info import (
    MopAttachedEvent,
    SweepType,
    WaterAmount,
    WaterAmountEvent,
    WaterCustomAmountEvent,
    WaterSweepTypeEvent,
)
from deebot_client.message import HandlingResult
from deebot_client.util import get_enum

from .common import JsonGetCommand, JsonSetCommand

if TYPE_CHECKING:
    from deebot_client.event_bus import EventBus


class GetWaterInfo(JsonGetCommand):
    """Get water info command."""

    NAME = "getWaterInfo"

    @classmethod
    def _handle_body_data_dict(
        cls, event_bus: EventBus, data: dict[str, Any]
    ) -> HandlingResult:
        """Handle message->body->data and notify the correct event subscribers.

        :return: A message response
        """
        if "amount" in data:
            event_bus.notify(WaterAmountEvent(WaterAmount(int(data["amount"]))))

        if "customAmount" in data:
            event_bus.notify(WaterCustomAmountEvent(int(data["customAmount"])))

        if (mop_attached := data.get("enable")) is not None:
            event_bus.notify(MopAttachedEvent(bool(mop_attached)))

        if sweep_type := data.get("sweepType"):
            event_bus.notify(WaterSweepTypeEvent(SweepType(int(sweep_type))))

        return HandlingResult.success()


class SetWaterInfo(JsonSetCommand):
    """Set water info command."""

    NAME = "setWaterInfo"
    get_command = GetWaterInfo
    _mqtt_params = MappingProxyType(
        {
            "amount": InitParam(WaterAmount, optional=True),
            "customAmount": InitParam(int, "custom_amount", optional=True),
            "enable": None,  # Remove it as we don't can set it (App includes it)
            "sweepType": InitParam(SweepType, "sweep_type", optional=True),
        }
    )

    def __init__(
        self,
        amount: WaterAmount | str | None = None,
        custom_amount: int | None = None,
        sweep_type: SweepType | str | None = None,
    ) -> None:
        params = {}
        if amount is not None:
            if custom_amount is not None:
                raise ValueError("Only one of amount or custom_amount can be provided.")

            if isinstance(amount, str):
                amount = get_enum(WaterAmount, amount)
            params["amount"] = amount.value
        elif custom_amount is not None:
            params["customAmount"] = custom_amount
        else:
            raise ValueError("Either amount or custom_amount must be provided.")

        if sweep_type:
            if isinstance(sweep_type, str):
                sweep_type = get_enum(SweepType, sweep_type)
            params["sweepType"] = sweep_type.value
        super().__init__(params)
