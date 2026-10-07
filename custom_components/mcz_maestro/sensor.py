from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfTemperature, UnitOfTime
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


@dataclass(frozen=True)
class MczSensorDescription(SensorEntityDescription):
    """Description d'un capteur MCZ."""

    enabled_by_default: bool = True


SENSORS: tuple[MczSensorDescription, ...] = (
    MczSensorDescription(
        key="stove_state_label",
        name="État",
        icon="mdi:stove",
    ),
    MczSensorDescription(
        key="ambient_temperature",
        name="Température ambiante",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MczSensorDescription(
        key="temperature_setpoint",
        name="Consigne native",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-cog",
    ),
    MczSensorDescription(
        key="fume_temperature",
        name="Température fumées",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MczSensorDescription(
        key="rpm_fume_fan",
        name="Ventilateur fumées",
        native_unit_of_measurement="tr/min",
        icon="mdi:fan",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MczSensorDescription(
        key="total_operating_hours",
        name="Heures totales fonctionnement",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:timer-outline",
        enabled_by_default=False,
    ),
    MczSensorDescription(
        key="hours_to_service",
        name="Heures avant entretien",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:wrench-clock",
        enabled_by_default=False,
    ),
    MczSensorDescription(
        key="minutes_to_switch_off",
        name="Minutes avant extinction",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:timer-sand",
        enabled_by_default=False,
    ),
    MczSensorDescription(
        key="number_of_ignitions",
        name="Nombre d'allumages",
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:counter",
        enabled_by_default=False,
    ),
    MczSensorDescription(
        key="motherboard_temperature",
        name="Température carte mère",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:developer-board",
        enabled_by_default=False,
    ),
    MczSensorDescription(
        key="rpm_wormwheel_live",
        name="RPM vis sans fin live",
        native_unit_of_measurement="tr/min",
        icon="mdi:screw-machine-flat-top",
        state_class=SensorStateClass.MEASUREMENT,
        enabled_by_default=False,
    ),
    MczSensorDescription(
        key="rpm_wormwheel_set",
        name="RPM vis sans fin consigne",
        native_unit_of_measurement="tr/min",
        icon="mdi:screw-machine-flat-top",
        state_class=SensorStateClass.MEASUREMENT,
        enabled_by_default=False,
    ),
    MczSensorDescription(
        key="pump_pwm",
        name="Pompe PWM",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:pump",
        state_class=SensorStateClass.MEASUREMENT,
        enabled_by_default=False,
    ),
    MczSensorDescription(
        key="firmware_version",
        name="Version firmware",
        icon="mdi:chip",
        enabled_by_default=False,
    ),
    MczSensorDescription(
        key="database_id",
        name="Database ID",
        icon="mdi:database",
        enabled_by_default=False,
    ),
    MczSensorDescription(
        key="active_live",
        name="Active live",
        icon="mdi:motion-sensor",
        enabled_by_default=False,
    ),
    MczSensorDescription(
        key="active_temperature",
        name="Température Active",
        icon="mdi:thermometer-lines",
        enabled_by_default=False,
    ),
    MczSensorDescription(
        key="brazier_label",
        name="Brasier",
        icon="mdi:fire-circle",
        enabled_by_default=False,
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(MczMaestroSensor(coordinator, entry, description) for description in SENSORS)


class MczMaestroSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, description: MczSensorDescription):
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = coordinator.device_info

    @property
    def entity_registry_enabled_default(self) -> bool:
        return self.entity_description.enabled_by_default

    @property
    def native_value(self):
        return self.coordinator.data.get(self.entity_description.key)
