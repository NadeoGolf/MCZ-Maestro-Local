from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .client import MczMaestroClient
from .const import (
    CONF_HOST,
    CONF_OPEN_TIMEOUT,
    CONF_PORT,
    CONF_RECV_TIMEOUT,
    CONF_RETRIES,
    DEFAULT_OPEN_TIMEOUT,
    DEFAULT_RECV_TIMEOUT,
    DEFAULT_RETRIES,
)
from .coordinator import MczMaestroConfigEntry, MczMaestroCoordinator
from .helpers import option_float, option_int, reload_options

PLATFORMS = [
    Platform.CLIMATE,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.SELECT,
    Platform.NUMBER,
    Platform.FAN,
]


async def async_setup_entry(hass: HomeAssistant, entry: MczMaestroConfigEntry) -> bool:
    client = MczMaestroClient(
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        open_timeout=option_float(entry, CONF_OPEN_TIMEOUT, DEFAULT_OPEN_TIMEOUT),
        recv_timeout=option_float(entry, CONF_RECV_TIMEOUT, DEFAULT_RECV_TIMEOUT),
        retries=option_int(entry, CONF_RETRIES, DEFAULT_RETRIES),
    )

    coordinator = MczMaestroCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: MczMaestroConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_update_listener(hass: HomeAssistant, entry: MczMaestroConfigEntry) -> None:
    """Reload after options changes, except for thermostat settings read live."""
    coordinator = entry.runtime_data
    if reload_options(entry.options) == coordinator.reload_options:
        # Refresh entity states and let the thermostat re-evaluate with the new values.
        coordinator.async_update_listeners()
        return
    await hass.config_entries.async_reload(entry.entry_id)
