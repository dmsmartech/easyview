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
)

_LOGGER = logging.getLogger(__name__)


class EasyViewFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for EasyView."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        """Handle initial configuration step."""
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
                options = {
                    CONF_HIGH_THRESHOLD: user_input.pop(CONF_HIGH_THRESHOLD),
                    CONF_LOW_THRESHOLD: user_input.pop(CONF_LOW_THRESHOLD),
                }
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME],
                    data=user_input,
                    options=options,
                )

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
                vol.Required(CONF_HIGH_THRESHOLD, default=DEFAULT_HIGH_MG_DL): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=100, max=400, step=1, unit_of_measurement=MG_DL, mode=selector.NumberSelectorMode.BOX)
                ),
                vol.Required(CONF_LOW_THRESHOLD, default=DEFAULT_LOW_MG_DL): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=40, max=120, step=1, unit_of_measurement=MG_DL, mode=selector.NumberSelectorMode.BOX)
                ),
            }),
            errors=errors,
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
        """Show the options form."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self.config_entry.options
        unit = self.config_entry.data.get(CONF_UNIT_OF_MEASUREMENT, MG_DL)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_HIGH_THRESHOLD,
                    default=current.get(CONF_HIGH_THRESHOLD, DEFAULT_HIGH_MG_DL),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=100, max=400, step=1, unit_of_measurement=unit, mode=selector.NumberSelectorMode.BOX
                    )
                ),
                vol.Required(
                    CONF_LOW_THRESHOLD,
                    default=current.get(CONF_LOW_THRESHOLD, DEFAULT_LOW_MG_DL),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=40, max=120, step=1, unit_of_measurement=unit, mode=selector.NumberSelectorMode.BOX
                    )
                ),
            }),
        )