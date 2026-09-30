"""DataUpdateCoordinator for EasyView."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EasyViewApiAuthenticationError, EasyViewApiClient, EasyViewApiError
from .const import DOMAIN, LOGGER, REFRESH_RATE_MIN

_LOGGER = logging.getLogger(__name__)


class EasyViewDataUpdateCoordinator(DataUpdateCoordinator):
    """Manages periodic polling from the EasyView API."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: EasyViewApiClient,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        self.client = client
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=REFRESH_RATE_MIN),
            config_entry=config_entry,
        )

    async def _async_update_data(self):
        """Fetch latest data from EasyView."""
        try:
            return await self.client.async_get_data()
        except EasyViewApiAuthenticationError as exc:
            _LOGGER.error("Authentication error: %s", exc)
            raise ConfigEntryAuthFailed(exc) from exc
        except EasyViewApiError as exc:
            _LOGGER.error("API error: %s", exc)
            raise UpdateFailed(exc) from exc