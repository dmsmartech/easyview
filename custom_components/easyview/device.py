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
        """Initialize the base device entity."""
        super().__init__(coordinator, context=index)
        entry = coordinator.data[index]
        sensor = entry["sensor_status"]
        unique_device_id = entry["username"]        # email — для identifiers и unique_id
        display_name = entry.get("patient_name") or entry["username"]   # имя пациента
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_device_id)},
            name=display_name,
            model=sensor.get("deviceType", "Medtrum CGM"),
            manufacturer=NAME,
            sw_version=VERSION,
        )
        _LOGGER.debug("EasyViewDevice initialized for %s (%s)", display_name, unique_device_id)