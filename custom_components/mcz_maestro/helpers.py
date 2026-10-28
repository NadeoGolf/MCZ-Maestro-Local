from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry

from .const import (
    CONF_AWAY_TEMPERATURE,
    CONF_COLD_TOLERANCE,
    CONF_HOT_TOLERANCE,
    CONF_MIN_CYCLE_DURATION_SECONDS,
    CONF_MODEL,
    CONF_NAME,
    DEFAULT_MODEL,
    DEFAULT_NAME,
    DOMAIN,
    MANUFACTURER,
)

# Thermostat settings read live by the climate entity: changing them must not
# reload the integration (reconnection, unavailable entities, min cycle reset).
LIVE_OPTION_KEYS = {
    CONF_AWAY_TEMPERATURE,
    CONF_COLD_TOLERANCE,
    CONF_HOT_TOLERANCE,
    CONF_MIN_CYCLE_DURATION_SECONDS,
}


def entry_value(entry: ConfigEntry, key: str, default: Any) -> Any:
    """Return an option value, then a config data value, then a default."""
    if key in entry.options:
        return entry.options[key]
    if key in entry.data:
        return entry.data[key]
    return default


def device_name(entry: ConfigEntry) -> str:
    """Return the user-visible device name."""
    return str(entry_value(entry, CONF_NAME, DEFAULT_NAME)).strip() or DEFAULT_NAME


def device_model(entry: ConfigEntry) -> str:
    """Return the configured MCZ model."""
    return str(entry_value(entry, CONF_MODEL, DEFAULT_MODEL)).strip() or DEFAULT_MODEL


def device_info(entry: ConfigEntry) -> dict[str, Any]:
    """Return common device info for all entities."""
    return {
        "identifiers": {(DOMAIN, entry.entry_id)},
        "name": device_name(entry),
        "manufacturer": MANUFACTURER,
        "model": device_model(entry),
    }


def reload_options(options: Any) -> dict[str, Any]:
    """Return the options whose change requires reloading the integration."""
    return {key: value for key, value in options.items() if key not in LIVE_OPTION_KEYS}
