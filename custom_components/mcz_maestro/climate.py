from __future__ import annotations

from datetime import datetime, timezone

from homeassistant.components.climate import ClimateEntity, HVACAction
from homeassistant.components.climate.const import ClimateEntityFeature, HVACMode
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_CONTROL_MODE,
    CONF_COLD_TOLERANCE,
    CONF_HOT_TOLERANCE,
    CONF_AWAY_TEMPERATURE,
    CONF_MIN_CYCLE_DURATION_SECONDS,
    CONF_STOVE_TYPE,
    CONTROL_MODE_HA_THERMOSTAT,
    CONTROL_MODE_NATIVE_SETPOINT,
    DEFAULT_AWAY_TEMPERATURE,
    DEFAULT_STOVE_TYPE,
    DEFAULT_COLD_TOLERANCE,
    DEFAULT_HOT_TOLERANCE,
    DEFAULT_MIN_CYCLE_SECONDS,
    DEFAULT_TARGET_TEMPERATURE,
    DOMAIN,
)

ATTR_PRESET_MODE = "preset_mode"
PRESET_AWAY = "away"
PRESET_NONE = "none"


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MczMaestroClimate(coordinator, entry)])


class MczMaestroClimate(CoordinatorEntity, RestoreEntity, ClimateEntity):
    """MCZ climate entity.

    Deux modes sont disponibles dans les options de l'intégration:
    - home_assistant_thermostat: Home Assistant régule ON/OFF avec hystérésis.
    - mcz_native_setpoint: la consigne est envoyée au poêle avec Temperature_Setpoint.
    """

    _attr_has_entity_name = True
    _attr_name = None
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = 0.5
    _attr_min_temp = 10
    _attr_max_temp = 32
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
    _attr_preset_modes = [PRESET_NONE, PRESET_AWAY]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_climate"
        self._attr_device_info = coordinator.device_info
        self._target_temperature = DEFAULT_TARGET_TEMPERATURE
        self._preset_mode = PRESET_NONE
        self._hvac_mode = HVACMode.OFF
        self._regulating = False
        self._last_power_command: datetime | None = None

    @property
    def control_mode(self) -> str:
        return self.entry.options.get(CONF_CONTROL_MODE, CONTROL_MODE_HA_THERMOSTAT)

    @property
    def native_control_enabled(self) -> bool:
        return self.control_mode == CONTROL_MODE_NATIVE_SETPOINT

    @property
    def cold_tolerance(self) -> float:
        return float(self.entry.options.get(CONF_COLD_TOLERANCE, DEFAULT_COLD_TOLERANCE))

    @property
    def hot_tolerance(self) -> float:
        return float(self.entry.options.get(CONF_HOT_TOLERANCE, DEFAULT_HOT_TOLERANCE))

    @property
    def away_temperature(self) -> float:
        return float(self.entry.options.get(CONF_AWAY_TEMPERATURE, DEFAULT_AWAY_TEMPERATURE))

    @property
    def min_cycle_duration_seconds(self) -> int:
        try:
            return int(self.entry.options.get(CONF_MIN_CYCLE_DURATION_SECONDS, DEFAULT_MIN_CYCLE_SECONDS))
        except (TypeError, ValueError):
            return DEFAULT_MIN_CYCLE_SECONDS

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if (last_state := await self.async_get_last_state()) is None:
            return

        if last_state.state in {HVACMode.OFF, HVACMode.HEAT}:
            self._hvac_mode = HVACMode(last_state.state)

        restored_preset = last_state.attributes.get(ATTR_PRESET_MODE)
        if restored_preset in self.preset_modes:
            self._preset_mode = restored_preset

        restored_normal_target = last_state.attributes.get("normal_target_temperature")
        if restored_normal_target is not None:
            try:
                self._target_temperature = float(restored_normal_target)
            except (TypeError, ValueError):
                pass
        elif self._preset_mode != PRESET_AWAY:
            restored_target = last_state.attributes.get(ATTR_TEMPERATURE)
            if restored_target is not None:
                try:
                    self._target_temperature = float(restored_target)
                except (TypeError, ValueError):
                    pass

    @property
    def current_temperature(self):
        return self.coordinator.data.get("ambient_temperature")

    @property
    def target_temperature(self):
        if self._preset_mode == PRESET_AWAY:
            return self.away_temperature

        if self.native_control_enabled:
            native_target = self.coordinator.data.get("temperature_setpoint")
            if native_target is not None:
                try:
                    return float(native_target)
                except (TypeError, ValueError):
                    pass

        return self._target_temperature

    @property
    def preset_mode(self):
        return self._preset_mode

    @property
    def hvac_mode(self):
        return self._hvac_mode

    @property
    def hvac_action(self):
        if self._hvac_mode == HVACMode.OFF:
            return HVACAction.OFF
        if self.coordinator.data.get("power"):
            return HVACAction.HEATING
        return HVACAction.IDLE

    @property
    def extra_state_attributes(self):
        return {
            "control_mode": self.control_mode,
            "stove_type": self.entry.options.get(CONF_STOVE_TYPE, DEFAULT_STOVE_TYPE),
            "setpoint_sent_to_stove": self.native_control_enabled,
            "normal_target_temperature": self._target_temperature,
            "native_temperature_setpoint": self.coordinator.data.get("temperature_setpoint"),
            "away_temperature": self.away_temperature,
            "cold_tolerance": self.cold_tolerance,
            "hot_tolerance": self.hot_tolerance,
            "min_cycle_duration_seconds": self.min_cycle_duration_seconds,
            "stove_power": self.coordinator.data.get("power"),
            "stove_state": self.coordinator.data.get("stove_state_label"),
            "raw_stove_state": self.coordinator.data.get("stove_state"),
            "power_level": self.coordinator.data.get("power_level"),
            "eco_mode": self.coordinator.data.get("eco_mode"),
            "silent_mode": self.coordinator.data.get("silent_mode"),
            "active_mode": self.coordinator.data.get("active_mode"),
            "summer_mode": self.coordinator.data.get("summer_mode"),
        }

    async def async_set_temperature(self, **kwargs):
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return

        self._target_temperature = float(temperature)
        if self._preset_mode == PRESET_AWAY:
            self._preset_mode = PRESET_NONE

        self.async_write_ha_state()

        if self.native_control_enabled:
            await self.coordinator.client.send_command("Temperature_Setpoint", self._target_temperature)
            await self.coordinator.async_request_refresh()
            return

        await self._async_regulate()

    async def async_set_preset_mode(self, preset_mode):
        if preset_mode not in self.preset_modes:
            raise ValueError(f"Unsupported preset mode: {preset_mode}")

        self._preset_mode = preset_mode
        self.async_write_ha_state()

        if self.native_control_enabled:
            await self.coordinator.client.send_command("Temperature_Setpoint", self.target_temperature)
            await self.coordinator.async_request_refresh()
            return

        await self._async_regulate()

    async def async_set_hvac_mode(self, hvac_mode):
        if hvac_mode == HVACMode.OFF:
            self._hvac_mode = HVACMode.OFF
            await self._async_send_power(False, bypass_min_cycle=True)
        elif hvac_mode == HVACMode.HEAT:
            self._hvac_mode = HVACMode.HEAT
            if self.native_control_enabled:
                await self.coordinator.client.send_command("Temperature_Setpoint", self.target_temperature)
                await self._async_send_power(True, bypass_min_cycle=True)
            else:
                await self._async_regulate()

        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self):
        self._hvac_mode = HVACMode.HEAT
        self.async_write_ha_state()
        if self.native_control_enabled:
            await self.coordinator.client.send_command("Temperature_Setpoint", self.target_temperature)
            await self._async_send_power(True, bypass_min_cycle=True)
            await self.coordinator.async_request_refresh()
            return
        await self._async_regulate()

    async def async_turn_off(self):
        self._hvac_mode = HVACMode.OFF
        await self._async_send_power(False, bypass_min_cycle=True)
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    def _handle_coordinator_update(self) -> None:
        super()._handle_coordinator_update()
        if self._hvac_mode == HVACMode.HEAT and not self.native_control_enabled:
            self.hass.async_create_task(self._async_regulate())

    async def _async_regulate(self) -> None:
        if self._regulating or self._hvac_mode != HVACMode.HEAT or self.native_control_enabled:
            return

        current = self.current_temperature
        target = self.target_temperature
        if current is None or target is None:
            return

        try:
            current = float(current)
            target = float(target)
        except (TypeError, ValueError):
            return

        stove_power = bool(self.coordinator.data.get("power"))

        self._regulating = True
        try:
            if current <= target - self.cold_tolerance and not stove_power:
                await self._async_send_power(True)
                await self.coordinator.async_request_refresh()
            elif current >= target + self.hot_tolerance and stove_power:
                await self._async_send_power(False)
                await self.coordinator.async_request_refresh()
        finally:
            self._regulating = False

    async def _async_send_power(self, power: bool, bypass_min_cycle: bool = False) -> None:
        now = datetime.now(timezone.utc)
        if not bypass_min_cycle and self._last_power_command is not None:
            elapsed = (now - self._last_power_command).total_seconds()
            if elapsed < self.min_cycle_duration_seconds:
                return

        await self.coordinator.client.send_command("Power", power)
        self._last_power_command = now
