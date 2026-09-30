"""Config flow for EasyView integration."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_UNIT_OF_MEASUREMENT, CONF_USERNAME
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    EasyViewApiAuthenticationError,
    EasyViewApiCommunicationError,
    EasyViewApiClient,
    EasyViewApiError,
)
from .const import (
    CONF_HIGH_THRESHOLD,
    CONF_LOW_THRESHOLD,
    DEFAULT_HIGH_MG_DL,
    DEFAULT_LOW_MG_DL,
    DOMAIN,
    LOGGER,
    MG_DL,
    MMOL_L,
    MMOL_L_TO_MG_DL,
)

_LOGGER = logging.getLogger(__name__)

# Границы порогов в разных единицах
THRESHOLD_LIMITS = {
    MG_DL: {
        "high": {"min": 100, "max": 400, "step": 1, "default": DEFAULT_HIGH_MG_DL},
        "low":  {"min": 40,  "max": 120, "step": 1, "default": DEFAULT_LOW_MG_DL},
    },
    MMOL_L: {
        "high": {"min": 5.5, "max": 22.2, "step": 0.1,
                 "default": round(DEFAULT_HIGH_MG_DL / MMOL_L_TO_MG_DL, 1)},
        "low":  {"min": 2.2, "max": 6.7,  "step": 0.1,
                 "default": round(DEFAULT_LOW_MG_DL / MMOL_L_TO_MG_DL, 1)},
    },
}


def _to_mg_dl(value: float, unit: str) -> int:
    """Convert a threshold value to mg/dL for storage."""
    if unit == MMOL_L:
        return round(value * MMOL_L_TO_MG_DL)
    return int(value)


def _from_mg_dl(value: int, unit: str) -> float:
    """Convert a stored mg/dL threshold to the given unit for display."""
    if unit == MMOL_L:
        return round(value / MMOL_L_TO_MG_DL, 1)
    return value


class EasyViewFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for EasyView."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the flow."""
        self._user_input: dict | None = None
        self._unit: str = MG_DL

    async def async_step_user(self, user_input: dict | None = None):
        """Step 1: credentials and unit of measurement."""
        errors = {}
        if user_input is not None:
            try:
                await self._test_credentials(
                    user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
                )
            except EasyViewApiAuthenticationError as exc:
                LOGGER.warning(exc)
                errors["base"] = "auth"
            except EasyViewApiCommunicationError as exc:
                LOGGER.error(exc)
                errors["base"] = "connection"
            except EasyViewApiError as exc:
                LOGGER.exception(exc)
                errors["base"] = "unknown"
            else:
                self._user_input = user_input
                self._unit = user_input[CONF_UNIT_OF_MEASUREMENT]
                return await self.async_step_thresholds()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_USERNAME): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.EMAIL)
                ),
                vol.Required(CONF_PASSWORD): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                ),
                vol.Required(CONF_UNIT_OF_MEASUREMENT, default=MG_DL): vol.In({MG_DL, MMOL_L}),
            }),
            errors=errors,
        )

    async def async_step_thresholds(self, user_input: dict | None = None):
        """Step 2: alert thresholds in the selected unit."""
        if user_input is not None:
            options = {
                CONF_HIGH_THRESHOLD: _to_mg_dl(user_input[CONF_HIGH_THRESHOLD], self._unit),
                CONF_LOW_THRESHOLD: _to_mg_dl(user_input[CONF_LOW_THRESHOLD], self._unit),
            }
            data = dict(self._user_input)
            return self.async_create_entry(
                title=data[CONF_USERNAME],
                data=data,
                options=options,
            )

        limits = THRESHOLD_LIMITS[self._unit]

        return self.async_show_form(
            step_id="thresholds",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_HIGH_THRESHOLD,
                    default=limits["high"]["default"],
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=limits["high"]["min"],
                        max=limits["high"]["max"],
                        step=limits["high"]["step"],
                        unit_of_measurement=self._unit,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(
                    CONF_LOW_THRESHOLD,
                    default=limits["low"]["default"],
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=limits["low"]["min"],
                        max=limits["low"]["max"],
                        step=limits["low"]["step"],
                        unit_of_measurement=self._unit,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
            }),
            description_placeholders={"unit": self._unit},
        )

    async def async_step_reauth(self, user_input: dict | None = None):
        """Handle re-authentication."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input: dict | None = None):
        """Handle re-authentication confirmation."""
        errors = {}
        reauth_entry: ConfigEntry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )

        if user_input is not None:
            try:
                await self._test_credentials(
                    user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
                )
            except EasyViewApiAuthenticationError as exc:
                LOGGER.warning(exc)
                errors["base"] = "auth"
            except EasyViewApiCommunicationError as exc:
                LOGGER.error(exc)
                errors["base"] = "connection"
            except EasyViewApiError as exc:
                LOGGER.exception(exc)
                errors["base"] = "unknown"
            else:
                self.hass.config_entries.async_update_entry(
                    reauth_entry, data={**reauth_entry.data, **user_input}
                )
                await self.hass.config_entries.async_reload(reauth_entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_USERNAME,
                    default=reauth_entry.data.get(CONF_USERNAME, ""),
                ): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.EMAIL)
                ),
                vol.Required(CONF_PASSWORD): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                ),
            }),
            description_placeholders={"username": reauth_entry.data.get(CONF_USERNAME, "")},
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry):
        """Return the options flow handler."""
        return EasyViewOptionsFlowHandler(config_entry)

    async def _test_credentials(self, username: str, password: str) -> None:
        """Validate credentials by attempting login."""
        client = EasyViewApiClient(
            username=username,
            password=password,
            session=async_get_clientsession(self.hass),
        )
        await client.async_login()


class EasyViewOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow to configure glucose alert thresholds."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None):
        """Show the options form with thresholds in the configured unit."""
        unit = self.config_entry.data.get(CONF_UNIT_OF_MEASUREMENT, MG_DL)
        limits = THRESHOLD_LIMITS[unit]

        if user_input is not None:
            return self.async_create_entry(title="", data={
                CONF_HIGH_THRESHOLD: _to_mg_dl(user_input[CONF_HIGH_THRESHOLD], unit),
                CONF_LOW_THRESHOLD: _to_mg_dl(user_input[CONF_LOW_THRESHOLD], unit),
            })

        current = self.config_entry.options
        high_mg_dl = current.get(CONF_HIGH_THRESHOLD, DEFAULT_HIGH_MG_DL)
        low_mg_dl = current.get(CONF_LOW_THRESHOLD, DEFAULT_LOW_MG_DL)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_HIGH_THRESHOLD,
                    default=_from_mg_dl(high_mg_dl, unit),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=limits["high"]["min"],
                        max=limits["high"]["max"],
                        step=limits["high"]["step"],
                        unit_of_measurement=unit,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(
                    CONF_LOW_THRESHOLD,
                    default=_from_mg_dl(low_mg_dl, unit),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=limits["low"]["min"],
                        max=limits["low"]["max"],
                        step=limits["low"]["step"],
                        unit_of_measurement=unit,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
            }),
            description_placeholders={"unit": unit},
        )