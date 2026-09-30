"""Sensor platform for EasyView."""

from __future__ import annotations

from datetime import datetime, timezone
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_UNIT_OF_MEASUREMENT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    GLUCOSE_TREND_ICON,
    GLUCOSE_TREND_MESSAGE,
    GLUCOSE_VALUE_ICON,
    MG_DL,
    MMOL_DL_TO_MG_DL,
    MMOL_L,
    SENSOR_STATUS_MESSAGE,
)
from .coordinator import EasyViewDataUpdateCoordinator
from .device import EasyViewDevice

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up EasyView sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    custom_unit = config_entry.data.get(CONF_UNIT_OF_MEASUREMENT, MG_DL)

    sensors = []
    for index in range(len(coordinator.data)):
        sensors.extend([
            EasyViewSensor(coordinator, index, "glucose", custom_unit),
            EasyViewSensor(coordinator, index, "trend", None),
            EasyViewSensor(coordinator, index, "status", None),
            EasyViewSensor(coordinator, index, "battery", "%"),
            EasyViewSensor(coordinator, index, "delay", "min"),
        ])

    async_add_entities(sensors)


class EasyViewSensor(EasyViewDevice, SensorEntity):
    """Sensor entity for EasyView CGM data."""

    def __init__(
        self,
        coordinator: EasyViewDataUpdateCoordinator,
        index: int,
        key: str,
        uom: str | None,
    ) -> None:
        super().__init__(coordinator, index)
        self.index = index
        self.key = key
        self._attr_translation_key = key
        self._attr_native_unit_of_measurement = uom
        entry = coordinator.data[index]
        self._attr_unique_id = f"{entry['username']}_{key}"

    def _sensor(self) -> dict:
        return self.coordinator.data[self.index]["sensor_status"]

    @property
    def native_value(self):
        """Return the current sensor value."""
        s = self._sensor()

        if self.key == "glucose":
            glucose_mmol = s.get("glucose", 0)
            if self._attr_native_unit_of_measurement == MMOL_L:
                return round(float(glucose_mmol), 1)
            return round(glucose_mmol * MMOL_DL_TO_MG_DL)

        if self.key == "trend":
            rate = s.get("glucoseRate", 0)
            return GLUCOSE_TREND_MESSAGE.get(rate, "Unknown")

        if self.key == "status":
            status_code = s.get("status")
            return SENSOR_STATUS_MESSAGE.get(status_code, f"Unknown ({status_code})")

        if self.key == "battery":
            value = s.get("batteryPercent")
            if value is not None:
                return round(float(value) * 100)

        if self.key == "delay":
            update_time = s.get("updateTime")
            if update_time:
                last_update = datetime.fromtimestamp(update_time, tz=timezone.utc)
                delta = datetime.now(tz=timezone.utc) - last_update
                return int(delta.total_seconds() / 60)

        return None

    @property
    def icon(self):
        """Return the appropriate trend icon for glucose sensors."""
        if self.key in ("glucose", "trend"):
            rate = self._sensor().get("glucoseRate", 0)
            return GLUCOSE_TREND_ICON.get(rate, GLUCOSE_VALUE_ICON)
        if self.key == "battery":
            return "mdi:battery"
        if self.key == "status":
            return "mdi:heart-pulse"
        return GLUCOSE_VALUE_ICON

    @property
    def extra_state_attributes(self):
        """Return extra attributes for the glucose sensor."""
        if self.key != "glucose":
            return None
        s = self._sensor()
        update_time = s.get("updateTime")
        return {
            "sensor_id": s.get("sensorId"),
            "serial": s.get("serial"),
            "sequence": s.get("sequence"),
            "device_type": s.get("deviceType"),
            "last_update": datetime.fromtimestamp(update_time, tz=timezone.utc).isoformat() if update_time else None,
        }