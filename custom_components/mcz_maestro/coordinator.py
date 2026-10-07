from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import MczMaestroClient, MczMaestroError
from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN
from .helpers import device_info

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

    @property
    def device_info(self) -> dict[str, Any]:
        return device_info(self.entry)

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.client.get_status()
        except MczMaestroError as err:
            raise UpdateFailed(str(err)) from err
