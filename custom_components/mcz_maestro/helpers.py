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


def option_float(entry: ConfigEntry, key: str, default: float) -> float:
    """Return a numeric option, falling back to the default when invalid."""
    try:
        return float(entry.options.get(key, default))
    except (TypeError, ValueError):
        return default


def option_int(entry: ConfigEntry, key: str, default: int) -> int:
    """Return an integer option, falling back to the default when invalid."""
    try:
        return int(entry.options.get(key, default))
    except (TypeError, ValueError):
        return default


def _entry_text(entry: ConfigEntry, key: str, default: str) -> str:
    """Return a text option, then a config data value, then a default."""
    value = entry.options.get(key, entry.data.get(key, default))
    return str(value).strip() or default


def device_info(entry: ConfigEntry) -> dict[str, Any]:
    """Return common device info for all entities."""
    return {
        "identifiers": {(DOMAIN, entry.entry_id)},
        "name": _entry_text(entry, CONF_NAME, DEFAULT_NAME),
        "manufacturer": MANUFACTURER,
        "model": _entry_text(entry, CONF_MODEL, DEFAULT_MODEL),
    }


def reload_options(options: Any) -> dict[str, Any]:
    """Return the options whose change requires reloading the integration."""
    return {key: value for key, value in options.items() if key not in LIVE_OPTION_KEYS}
