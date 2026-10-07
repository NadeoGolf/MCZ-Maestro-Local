from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_HOST, DOMAIN, INTEGRATION_VERSION

TO_REDACT = {CONF_HOST}


def _safe_data(data: dict[str, Any] | None) -> dict[str, Any]:
    if not data:
        return {}

    # Keep the raw decoded values and last frame available for troubleshooting.
    # They normally contain stove telemetry, not credentials.
    return dict(data)


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data.get(DOMAIN, {}).get(entry.entry_id)

    return {
        "integration": {
            "domain": DOMAIN,
            "version": INTEGRATION_VERSION,
        },
        "entry": {
            "title": entry.title,
            "entry_id": entry.entry_id,
            "data": async_redact_data(dict(entry.data), TO_REDACT),
            "options": dict(entry.options),
        },
        "coordinator": {
            "last_update_success": getattr(coordinator, "last_update_success", None),
            "update_interval": str(getattr(coordinator, "update_interval", None)),
            "data": _safe_data(getattr(coordinator, "data", None)),
        },
        "client": getattr(getattr(coordinator, "client", None), "diagnostics", {}),
    }
