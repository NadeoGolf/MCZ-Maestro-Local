from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .client import MczMaestroClient, MczMaestroError
from .const import (
    CONF_CONTROL_MODE,
    CONF_HOST,
    CONF_MODEL,
    CONF_NAME,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_STOVE_TYPE,
    CONTROL_MODE_HA_THERMOSTAT,
    CONTROL_MODE_OPTIONS,
    DEFAULT_HOST,
    DEFAULT_MODEL,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_STOVE_TYPE,
    DOMAIN,
    STOVE_TYPE_OPTIONS,
)


def _options_schema(options: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional(CONF_NAME, default=options.get(CONF_NAME, DEFAULT_NAME)): str,
            vol.Optional(CONF_MODEL, default=options.get(CONF_MODEL, DEFAULT_MODEL)): str,
            vol.Optional(
                CONF_STOVE_TYPE,
                default=options.get(CONF_STOVE_TYPE, DEFAULT_STOVE_TYPE),
            ): vol.In(STOVE_TYPE_OPTIONS),
            vol.Optional(
                CONF_CONTROL_MODE,
                default=options.get(CONF_CONTROL_MODE, CONTROL_MODE_HA_THERMOSTAT),
            ): vol.In(CONTROL_MODE_OPTIONS),
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            ): vol.All(int, vol.Range(min=5, max=300)),
        }
    )


class MczMaestroConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return MczMaestroOptionsFlow()

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            client = MczMaestroClient(
                host=user_input[CONF_HOST],
                port=user_input[CONF_PORT],
            )
            try:
                await client.get_status()
            except MczMaestroError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"MCZ {user_input[CONF_HOST]}",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                }
            ),
            errors=errors,
        )


class MczMaestroOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=_options_schema({**self.config_entry.data, **self.config_entry.options}),
        )
