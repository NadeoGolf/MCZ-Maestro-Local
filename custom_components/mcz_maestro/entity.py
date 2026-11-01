from __future__ import annotations

from typing import Any

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import MczMaestroCoordinator


class MczMaestroEntity(CoordinatorEntity[MczMaestroCoordinator]):
    """Common base for all MCZ entities attached to the stove device."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: MczMaestroCoordinator, unique_suffix: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{unique_suffix}"
        self._attr_device_info = coordinator.device_info

    async def _async_send_and_refresh(self, command: str, value: Any) -> None:
        await self.coordinator.async_send_command(command, value)
        await self.coordinator.async_request_refresh()
