from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
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
    DOMAIN,
)
from .coordinator import MczMaestroCoordinator

PLATFORMS = ["climate", "sensor", "switch", "select", "number", "fan"]


def _option_float(entry: ConfigEntry, key: str, default: float) -> float:
    try:
        return float(entry.options.get(key, default))
    except (TypeError, ValueError):
        return default


def _option_int(entry: ConfigEntry, key: str, default: int) -> int:
    try:
        return int(entry.options.get(key, default))
    except (TypeError, ValueError):
        return default


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    client = MczMaestroClient(
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        open_timeout=_option_float(entry, CONF_OPEN_TIMEOUT, DEFAULT_OPEN_TIMEOUT),
        recv_timeout=_option_float(entry, CONF_RECV_TIMEOUT, DEFAULT_RECV_TIMEOUT),
        retries=_option_int(entry, CONF_RETRIES, DEFAULT_RETRIES),
    )

    coordinator = MczMaestroCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the integration after options are changed."""
    await hass.config_entries.async_reload(entry.entry_id)
