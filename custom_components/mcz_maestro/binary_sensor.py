from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


@dataclass(frozen=True)
class MczBinarySensorDescription(BinarySensorEntityDescription):
    """Description d'un capteur binaire MCZ."""


BINARY_SENSORS: tuple[MczBinarySensorDescription, ...] = (
)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(MczMaestroBinarySensor(coordinator, entry, description) for description in BINARY_SENSORS)


class MczMaestroBinarySensor(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, description: MczBinarySensorDescription):
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self):
        value = self.coordinator.data.get(self.entity_description.key)
        if value is None:
            return None
        return bool(value)
