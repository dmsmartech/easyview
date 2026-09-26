"""Base device entity for EasyView integration."""

from __future__ import annotations

import logging

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN, NAME, VERSION
from .coordinator import EasyViewDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class EasyViewDevice(CoordinatorEntity):
    """Base entity representing a Medtrum EasyView CGM user."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: EasyViewDataUpdateCoordinator, index: int) -> None:
        super().__init__(coordinator, context=index)
        entry = coordinator.data[index]
        sensor = entry["sensor_status"]
        unique_device_id = entry["username"]
        self._attr_unique_id = unique_device_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_device_id)},
            name=entry["username"],
            model=sensor.get("deviceType", "Medtrum CGM"),
            manufacturer=NAME,
            sw_version=VERSION,
        )
        _LOGGER.debug("EasyViewDevice initialized for %s", entry["username"])
