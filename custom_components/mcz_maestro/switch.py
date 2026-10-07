from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


@dataclass(frozen=True)
class MczSwitchDescription(SwitchEntityDescription):
    """Description d'un switch MCZ."""

    command: str = ""
    icon_on: str | None = None
    icon_off: str | None = None
    enabled_by_default: bool = True


SWITCHES: tuple[MczSwitchDescription, ...] = (
    MczSwitchDescription(
        key="power",
        name="Alimentation",
        command="Power",
        icon_on="mdi:fire",
        icon_off="mdi:power",
    ),
    MczSwitchDescription(
        key="eco_mode",
        name="Mode Eco",
        command="Eco_Mode",
        icon_on="mdi:leaf",
        icon_off="mdi:leaf-off",
    ),
    MczSwitchDescription(
        key="silent_mode",
        name="Mode Silent",
        command="Silent_Mode",
        icon_on="mdi:volume-off",
        icon_off="mdi:volume-high",
    ),
    MczSwitchDescription(
        key="active_mode",
        name="Mode Active",
        command="Active_Mode",
        icon_on="mdi:motion-sensor",
        icon_off="mdi:motion-sensor-off",
    ),
    MczSwitchDescription(
        key="sound_effects",
        name="Sons touches",
        command="Sound_Effects",
        icon_on="mdi:volume-high",
        icon_off="mdi:volume-off",
    ),
    MczSwitchDescription(
        key="summer_mode",
        name="Mode hiver/été",
        command="Summer_Mode",
        icon_on="mdi:weather-sunny",
        icon_off="mdi:snowflake",
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(MczMaestroSwitch(coordinator, entry, description) for description in SWITCHES)


class MczMaestroSwitch(CoordinatorEntity, SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, description: MczSwitchDescription):
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = coordinator.device_info

    @property
    def entity_registry_enabled_default(self) -> bool:
        return self.entity_description.enabled_by_default

    @property
    def is_on(self):
        value = self.coordinator.data.get(self.entity_description.key)
        if value is None:
            return None
        return bool(value)

    @property
    def icon(self):
        if self.is_on:
            return self.entity_description.icon_on or self.entity_description.icon
        return self.entity_description.icon_off or self.entity_description.icon

    async def async_turn_on(self, **kwargs):
        await self.coordinator.client.send_command(self.entity_description.command, True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.client.send_command(self.entity_description.command, False)
        await self.coordinator.async_request_refresh()
