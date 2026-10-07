from __future__ import annotations

from dataclasses import dataclass
import math

from homeassistant.components.fan import FanEntity, FanEntityDescription, FanEntityFeature
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

AUTO_PRESET = "Auto"


@dataclass(frozen=True)
class MczFanDescription(FanEntityDescription):
    """Description d'un ventilateur MCZ."""
    command: str = ""
    max_manual_level: int = 5
    auto_level: int = 6


FANS: tuple[MczFanDescription, ...] = (
    MczFanDescription(
        key="fan_state",
        name="Ventilateur poêle",
        command="Fan_State",
    ),
    MczFanDescription(
        key="ducted_fan_1",
        name="Ventilateur couloir",
        command="DuctedFan1",
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(MczMaestroFan(coordinator, entry, description) for description in FANS)


class MczMaestroFan(CoordinatorEntity, FanEntity):
    _attr_has_entity_name = True
    _attr_supported_features = FanEntityFeature.SET_SPEED | FanEntityFeature.PRESET_MODE
    _attr_preset_modes = [AUTO_PRESET]

    def __init__(self, coordinator, entry, description: MczFanDescription):
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}_fan"
        self._attr_speed_count = description.max_manual_level
        self._last_non_zero_level = 1
        self._attr_device_info = coordinator.device_info

    def _current_level(self) -> int | None:
        value = self.coordinator.data.get(self.entity_description.key)
        try:
            if value is None:
                return None
            level = int(float(value))
        except (TypeError, ValueError):
            return None

        max_known = max(self.entity_description.max_manual_level, self.entity_description.auto_level)
        level = max(0, min(level, max_known))
        if 0 < level <= self.entity_description.max_manual_level:
            self._last_non_zero_level = level
        return level

    @property
    def is_on(self) -> bool | None:
        level = self._current_level()
        if level is None:
            return None
        return level > 0

    @property
    def percentage(self) -> int | None:
        level = self._current_level()
        if level is None:
            return None
        if level == self.entity_description.auto_level:
            return None
        if level <= 0:
            return 0
        return round((level / self.entity_description.max_manual_level) * 100)

    @property
    def preset_mode(self) -> str | None:
        level = self._current_level()
        if level == self.entity_description.auto_level:
            return AUTO_PRESET
        return None

    async def async_set_percentage(self, percentage: int) -> None:
        if percentage <= 0:
            level = 0
        else:
            level = math.ceil((percentage / 100) * self.entity_description.max_manual_level)
            level = max(1, min(level, self.entity_description.max_manual_level))

        await self.coordinator.client.send_command(self.entity_description.command, float(level))
        await self.coordinator.async_request_refresh()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        if preset_mode != AUTO_PRESET:
            return
        await self.coordinator.client.send_command(self.entity_description.command, float(self.entity_description.auto_level))
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, percentage: int | None = None, preset_mode: str | None = None, **kwargs) -> None:
        if preset_mode == AUTO_PRESET:
            await self.async_set_preset_mode(AUTO_PRESET)
            return
        if percentage is not None:
            await self.async_set_percentage(percentage)
            return

        level = self._current_level()
        if level is None or level <= 0 or level == self.entity_description.auto_level:
            level = self._last_non_zero_level or 1

        await self.coordinator.client.send_command(self.entity_description.command, float(level))
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.client.send_command(self.entity_description.command, 0.0)
        await self.coordinator.async_request_refresh()
