from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry

from .const import CONF_MODEL, CONF_NAME, DEFAULT_MODEL, DEFAULT_NAME, DOMAIN, MANUFACTURER


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
