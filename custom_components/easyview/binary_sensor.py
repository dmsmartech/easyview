"""Binary sensor platform for EasyView."""

from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_HIGH_THRESHOLD, CONF_LOW_THRESHOLD, DEFAULT_HIGH_MG_DL, DEFAULT_LOW_MG_DL, DOMAIN, MMOL_DL_TO_MG_DL
from .coordinator import EasyViewDataUpdateCoordinator
from .device import EasyViewDevice

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up EasyView binary sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    sensors = []
    for index in range(len(coordinator.data)):
        sensors.extend([
            EasyViewBinarySensor(coordinator, index, "is_high", "Is High", config_entry),
            EasyViewBinarySensor(coordinator, index, "is_low", "Is Low", config_entry),
        ])

    async_add_entities(sensors)


class EasyViewBinarySensor(EasyViewDevice, BinarySensorEntity):
    """Binary sensor for high/low glucose alerts."""

    def __init__(
        self,
        coordinator: EasyViewDataUpdateCoordinator,
        index: int,
        key: str,
        name: str,
        config_entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator, index)
        self.index = index
        self.key = key
        self._attr_name = name
        self._config_entry = config_entry
        self._attr_unique_id = f"{coordinator.data[index]['username']}_{key}"

    def _glucose_mg_dl(self) -> float:
        s = self.coordinator.data[self.index]["sensor_status"]
        return s.get("glucose", 0) * MMOL_DL_TO_MG_DL

    def _threshold(self, key: str, default: int) -> int:
        return self._config_entry.options.get(key, default)

    @property
    def is_on(self) -> bool:
        glucose = self._glucose_mg_dl()
        if self.key == "is_high":
            return glucose > self._threshold(CONF_HIGH_THRESHOLD, DEFAULT_HIGH_MG_DL)
        if self.key == "is_low":
            return glucose < self._threshold(CONF_LOW_THRESHOLD, DEFAULT_LOW_MG_DL)
        return False

    @property
    def icon(self):
        if self.key == "is_high":
            return "mdi:arrow-up-circle" if self.is_on else "mdi:arrow-up-circle-outline"
        return "mdi:arrow-down-circle" if self.is_on else "mdi:arrow-down-circle-outline"
