from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import MczMaestroConfigEntry
from .entity import MczMaestroEntity


@dataclass(frozen=True)
class MczSwitchDescription(SwitchEntityDescription):
    """Description d'un switch MCZ."""

    command: str = ""
    icon_on: str | None = None
    icon_off: str | None = None


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


async def async_setup_entry(
    hass: HomeAssistant, entry: MczMaestroConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(MczMaestroSwitch(coordinator, description) for description in SWITCHES)


class MczMaestroSwitch(MczMaestroEntity, SwitchEntity):
    entity_description: MczSwitchDescription

    def __init__(self, coordinator, description: MczSwitchDescription):
        super().__init__(coordinator, description.key)
        self.entity_description = description

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
        await self._async_send_and_refresh(self.entity_description.command, True)

    async def async_turn_off(self, **kwargs):
        await self._async_send_and_refresh(self.entity_description.command, False)
