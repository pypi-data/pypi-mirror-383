"""Battery messages."""

from __future__ import annotations

from typing import TYPE_CHECKING

from deebot_client.events import BatteryEvent
from deebot_client.logging_filter import get_logger
from deebot_client.message import HandlingResult
from deebot_client.messages.xml.common import XmlMessage

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element

    from deebot_client.event_bus import EventBus

_LOGGER = get_logger(__name__)


class BatteryInfo(XmlMessage):
    """BatteryInfo message."""

    NAME = "BatteryInfo"

    @classmethod
    def _handle_xml(cls, event_bus: EventBus, xml: Element) -> HandlingResult:
        """Handle xml message and notify the correct event subscribers.

        :return: A message response
        """
        if (battery := xml.find("battery")) is None or (
            power := battery.attrib.get("power")
        ) is None:
            return HandlingResult.analyse()

        if power.isdecimal() and (power_int := int(power)) >= 0:
            event_bus.notify(BatteryEvent(power_int))
            return HandlingResult.success()

        _LOGGER.error("Invalid battery power level received %s", power)
        return HandlingResult.analyse()
