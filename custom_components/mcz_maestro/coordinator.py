from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import MczMaestroClient, MczMaestroError
from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN
from .helpers import device_info, reload_options

_LOGGER = logging.getLogger(__name__)


def _scan_interval(entry: ConfigEntry) -> int:
    try:
        value = int(entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
    except (TypeError, ValueError):
        value = DEFAULT_SCAN_INTERVAL
    return max(5, value)


class MczMaestroCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: MczMaestroClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=_scan_interval(entry)),
            always_update=False,
        )
        self.entry = entry
        self.client = client
        # Options snapshot used to decide whether an options update needs a reload.
        self.reload_options = reload_options(entry.options)

    @property
    def device_info(self) -> dict[str, Any]:
        return device_info(self.entry)

    async def async_send_command(self, command: str, value: Any) -> None:
        """Send a command, reporting communication failures as readable HA errors."""
        try:
            await self.client.send_command(command, value)
        except MczMaestroError as err:
            raise HomeAssistantError(str(err)) from err

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.client.get_status()
        except MczMaestroError as err:
            raise UpdateFailed(str(err)) from err
