from __future__ import annotations

from dataclasses import dataclass, field

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


PROFILE_OPTIONS = {
    "Manuel (0)": 0,
    "Dynamique (1)": 1,
    "Nuit (2)": 2,
    "Confort (3)": 3,
    "Puissance (4)": 4,
    "Manuel étendu (10)": 10,
    "Dynamique étendu (11)": 11,
}


@dataclass(frozen=True)
class MczSelectDescription(SelectEntityDescription):
    """Description d'une sélection MCZ."""

    command: str = ""
    min_level: int | None = None
    max_level: int | None = None
    value_options: dict[str, int] = field(default_factory=dict)
    enabled_by_default: bool = True


SELECTS: tuple[MczSelectDescription, ...] = (
    MczSelectDescription(
        key="power_level",
        name="Puissance",
        command="Power_Level",
        icon="mdi:fire",
        min_level=1,
        max_level=5,
    ),
    MczSelectDescription(
        key="profile",
        name="Profil",
        command="Profile",
        icon="mdi:tune-variant",
        value_options=PROFILE_OPTIONS,
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(MczMaestroSelect(coordinator, entry, description) for description in SELECTS)


class MczMaestroSelect(CoordinatorEntity, RestoreEntity, SelectEntity):
    """Liste déroulante pour les valeurs MCZ à choix limité."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, description: MczSelectDescription):
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}_select"
        self._attr_options = self._build_options(description)
        self._attr_device_info = coordinator.device_info
        self._restored_option: str | None = None

    @property
    def entity_registry_enabled_default(self) -> bool:
        return self.entity_description.enabled_by_default

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if self._option_from_value(self.coordinator.data.get(self.entity_description.key)) is not None:
            return

        last_state = await self.async_get_last_state()
        if last_state is None or last_state.state in {"unknown", "unavailable", "none", "None"}:
            return

        option = self._option_from_input(last_state.state)
        if option is not None:
            self._restored_option = option

    @property
    def current_option(self) -> str | None:
        option = self._option_from_value(self.coordinator.data.get(self.entity_description.key))
        if option is None:
            return self._restored_option

        self._restored_option = option
        return option

    async def async_select_option(self, option: str) -> None:
        value = self._value_from_option(option)
        if value is None:
            raise ValueError(f"Unsupported MCZ option for {self.entity_description.key}: {option}")

        self._restored_option = option
        self.async_write_ha_state()
        await self.coordinator.client.send_command(self.entity_description.command, value)
        await self.coordinator.async_request_refresh()

    @staticmethod
    def _build_options(description: MczSelectDescription) -> list[str]:
        if description.value_options:
            return list(description.value_options)
        if description.min_level is not None and description.max_level is not None:
            return [str(level) for level in range(description.min_level, description.max_level + 1)]
        return []

    def _option_from_input(self, value) -> str | None:
        if value in self.options:
            return value
        return self._option_from_value(value)

    def _option_from_value(self, value) -> str | None:
        if value is None or value == "":
            return None

        if self.entity_description.value_options:
            numeric = self._int_from_value(value)
            if numeric is None:
                return None
            for option, option_value in self.entity_description.value_options.items():
                if option_value == numeric:
                    return option
            return None

        numeric = self._int_from_value(value)
        if numeric is None:
            return None
        option = str(numeric)
        return option if option in self.options else None

    def _value_from_option(self, option: str) -> int | None:
        if self.entity_description.value_options:
            return self.entity_description.value_options.get(option)
        numeric = self._int_from_value(option)
        if numeric is None:
            return None
        return numeric if str(numeric) in self.options else None

    @staticmethod
    def _int_from_value(value) -> int | None:
        try:
            if value is None or value == "":
                return None
            return int(float(value))
        except (TypeError, ValueError):
            return None
