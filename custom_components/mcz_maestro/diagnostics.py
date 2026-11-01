from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from .const import CONF_HOST, DOMAIN, INTEGRATION_VERSION
from .coordinator import MczMaestroConfigEntry

TO_REDACT = {CONF_HOST}
REDACTED = "**REDACTED**"


def _redact_host(value: Any, host: str) -> Any:
    """Mask the stove address in free text (entry title, unique id, error messages)."""
    if not host:
        return value
    if isinstance(value, str):
        return value.replace(host, REDACTED)
    if isinstance(value, dict):
        return {key: _redact_host(item, host) for key, item in value.items()}
    return value


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: MczMaestroConfigEntry) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data
    host = str(entry.data.get(CONF_HOST) or "")

    # Decoded values and the last raw frame are kept for troubleshooting:
    # they contain stove telemetry, not credentials.
    return _redact_host({
        "integration": {
            "domain": DOMAIN,
            "version": INTEGRATION_VERSION,
        },
        "entry": {
            "title": entry.title,
            "entry_id": entry.entry_id,
            "unique_id": entry.unique_id,
            "data": async_redact_data(dict(entry.data), TO_REDACT),
            "options": dict(entry.options),
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "update_interval": str(coordinator.update_interval),
            "data": dict(coordinator.data or {}),
        },
        "client": coordinator.client.diagnostics,
    }, host)
