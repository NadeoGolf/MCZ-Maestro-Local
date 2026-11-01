from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import MczMaestroConfigEntry
from .entity import MczMaestroEntity

SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="stove_state_label",
        name="État",
        icon="mdi:stove",
    ),
    SensorEntityDescription(
        key="ambient_temperature",
        name="Température ambiante",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="temperature_setpoint",
        name="Consigne native",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-cog",
    ),
    SensorEntityDescription(
        key="fume_temperature",
        name="Température fumées",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="rpm_fume_fan",
        name="Ventilateur fumées",
        native_unit_of_measurement="tr/min",
        icon="mdi:fan",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="total_operating_hours",
        name="Heures totales fonctionnement",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:timer-outline",
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="hours_to_service",
        name="Heures avant entretien",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:wrench-clock",
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="minutes_to_switch_off",
        name="Minutes avant extinction",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:timer-sand",
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="number_of_ignitions",
        name="Nombre d'allumages",
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:counter",
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="motherboard_temperature",
        name="Température carte mère",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:developer-board",
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="rpm_wormwheel_live",
        name="RPM vis sans fin live",
        native_unit_of_measurement="tr/min",
        icon="mdi:screw-machine-flat-top",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="rpm_wormwheel_set",
        name="RPM vis sans fin consigne",
        native_unit_of_measurement="tr/min",
        icon="mdi:screw-machine-flat-top",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="pump_pwm",
        name="Pompe PWM",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:pump",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="firmware_version",
        name="Version firmware",
        icon="mdi:chip",
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="database_id",
        name="Database ID",
        icon="mdi:database",
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="active_live",
        name="Active live",
        icon="mdi:motion-sensor",
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="active_temperature",
        name="Température Active",
        icon="mdi:thermometer-lines",
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="brazier_label",
        name="Brasier",
        icon="mdi:fire-circle",
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: MczMaestroConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(MczMaestroSensor(coordinator, description) for description in SENSORS)


class MczMaestroSensor(MczMaestroEntity, SensorEntity):
    def __init__(self, coordinator, description: SensorEntityDescription):
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self):
        return self.coordinator.data.get(self.entity_description.key)
