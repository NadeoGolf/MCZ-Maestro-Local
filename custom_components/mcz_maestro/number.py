from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.const import UnitOfTemperature, UnitOfTime
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_AWAY_TEMPERATURE,
    CONF_COLD_TOLERANCE,
    CONF_HOT_TOLERANCE,
    CONF_MIN_CYCLE_DURATION_SECONDS,
    DEFAULT_AWAY_TEMPERATURE,
    DEFAULT_COLD_TOLERANCE,
    DEFAULT_HOT_TOLERANCE,
    DEFAULT_MIN_CYCLE_SECONDS,
    DOMAIN,
)


@dataclass(frozen=True)
class MczNumberDescription(NumberEntityDescription):
    """Description d'une commande numerique MCZ."""

    command: str = ""
    option_key: str = ""
    default_value: float | int | None = None
    enabled_by_default: bool = False


NUMBERS: tuple[MczNumberDescription, ...] = (
    MczNumberDescription(
        key="temperature_setpoint",
        name="Consigne native MCZ",
        command="Temperature_Setpoint",
        native_min_value=10,
        native_max_value=32,
        native_step=0.5,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-cog",
        enabled_by_default=False,
    ),
    MczNumberDescription(
        key="cold_tolerance_config",
        name="Tolerance froide thermostat",
        option_key=CONF_COLD_TOLERANCE,
        default_value=DEFAULT_COLD_TOLERANCE,
        native_min_value=0,
        native_max_value=10,
        native_step=0.1,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-chevron-down",
        entity_category=EntityCategory.CONFIG,
        enabled_by_default=True,
    ),
    MczNumberDescription(
        key="hot_tolerance_config",
        name="Tolerance chaude thermostat",
        option_key=CONF_HOT_TOLERANCE,
        default_value=DEFAULT_HOT_TOLERANCE,
        native_min_value=0,
        native_max_value=10,
        native_step=0.1,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-chevron-up",
        entity_category=EntityCategory.CONFIG,
        enabled_by_default=True,
    ),
    MczNumberDescription(
        key="away_temperature_config",
        name="Temperature absence thermostat",
        option_key=CONF_AWAY_TEMPERATURE,
        default_value=DEFAULT_AWAY_TEMPERATURE,
        native_min_value=5,
        native_max_value=32,
        native_step=0.5,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:home-export-outline",
        entity_category=EntityCategory.CONFIG,
        enabled_by_default=True,
    ),
    MczNumberDescription(
        key="min_cycle_duration_config",
        name="Duree minimale cycle thermostat",
        option_key=CONF_MIN_CYCLE_DURATION_SECONDS,
        default_value=DEFAULT_MIN_CYCLE_SECONDS,
        native_min_value=0,
        native_max_value=86400,
        native_step=60,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        icon="mdi:timer-sync-outline",
        entity_category=EntityCategory.CONFIG,
        enabled_by_default=True,
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(MczMaestroNumber(coordinator, entry, description) for description in NUMBERS)


class MczMaestroNumber(CoordinatorEntity, RestoreEntity, NumberEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, description: MczNumberDescription):
        super().__init__(coordinator)
        self.entry = entry
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}_number"
        self._attr_device_info = coordinator.device_info
        self._attr_entity_category = description.entity_category
        self._restored_value: float | None = None

    @property
    def entity_registry_enabled_default(self) -> bool:
        return self.entity_description.enabled_by_default

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if self.entity_description.option_key:
            return

        if self.coordinator.data.get(self.entity_description.key) is not None:
            return

        last_state = await self.async_get_last_state()
        if last_state is None or last_state.state in {"unknown", "unavailable", "none", "None"}:
            return

        try:
            value = float(last_state.state)
        except (TypeError, ValueError):
            return

        if self.native_min_value <= value <= self.native_max_value:
            self._restored_value = value

    @property
    def native_value(self):
        if self.entity_description.option_key:
            value = self.entry.options.get(
                self.entity_description.option_key,
                self.entity_description.default_value,
            )
            return self._coerce_in_range(value, self.entity_description.default_value)

        value = self.coordinator.data.get(self.entity_description.key)
        if value is None:
            return self._restored_value

        value = self._coerce_in_range(value, self._restored_value)
        if value is not None:
            self._restored_value = value
        return value

    def _coerce_in_range(self, value: Any, fallback: Any = None):
        try:
            value = float(value)
        except (TypeError, ValueError):
            return fallback

        if value < self.native_min_value or value > self.native_max_value:
            return fallback

        if float(self.native_step or 1).is_integer() and float(value).is_integer():
            return int(value)
        return value

    def _normalize_value(self, value: float):
        value = float(value)
        step = float(self.native_step or 1)
        value = round(value / step) * step
        if value < self.native_min_value:
            value = self.native_min_value
        elif value > self.native_max_value:
            value = self.native_max_value

        if step.is_integer():
            return int(value)
        return round(value, 3)

    async def async_set_native_value(self, value: float):
        value = self._normalize_value(value)

        if self.entity_description.option_key:
            new_options = dict(self.entry.options)
            new_options[self.entity_description.option_key] = value
            self.hass.config_entries.async_update_entry(self.entry, options=new_options)
            self.async_write_ha_state()
            return

        self._restored_value = value
        self.async_write_ha_state()
        await self.coordinator.client.send_command(self.entity_description.command, value)
        await self.coordinator.async_request_refresh()
