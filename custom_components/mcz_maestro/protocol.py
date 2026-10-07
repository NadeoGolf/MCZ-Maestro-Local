from __future__ import annotations

import json
import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)

STATUS_REQUEST = "C|RecuperoInfo"

COMMAND_IDS: dict[str, int] = {
    "Power": 34,
    "Active_Mode": 35,
    "Power_Level": 36,
    "Fan_State": 37,
    "DuctedFan1": 38,
    "DuctedFan2": 39,
    "Eco_Mode": 41,
    "Temperature_Setpoint": 42,
    "Silent_Mode": 45,
    "Sound_Effects": 50,
    "Summer_Mode": 58,
    "Profile": 149,
}

BOOL_COMMANDS = {
    "Active_Mode",
    "Eco_Mode",
    "Silent_Mode",
    "Sound_Effects",
    "Summer_Mode",
}

INT_COMMANDS = {
    "Power_Level",
    "Fan_State",
    "DuctedFan1",
    "DuctedFan2",
    "Profile",
}

# MCZ Maestro RecuperoInfo positional mapping, based on maestrogateway/messages.py.
# Position 0 is the frame type. Positions start at 1 for Stove_State.
POSITIONAL_FIELDS: list[str | None] = [None] * 61
POSITIONAL_FIELDS[1] = "Stove_State"
POSITIONAL_FIELDS[2] = "Fan_State"
POSITIONAL_FIELDS[3] = "DuctedFan1"
POSITIONAL_FIELDS[4] = "DuctedFan2"
POSITIONAL_FIELDS[5] = "Fume_Temperature"
POSITIONAL_FIELDS[6] = "Ambient_Temperature"
POSITIONAL_FIELDS[7] = "Puffer_Temperature"
POSITIONAL_FIELDS[8] = "Boiler_Temperature"
POSITIONAL_FIELDS[9] = "NTC3_Temperature"
POSITIONAL_FIELDS[10] = "Candle_Condition"
POSITIONAL_FIELDS[11] = "ACTIVE_Set"
POSITIONAL_FIELDS[12] = "RPM_Fam_Fume"
POSITIONAL_FIELDS[13] = "RPM_WormWheel_Set"
POSITIONAL_FIELDS[14] = "RPM_WormWheel_Live"
POSITIONAL_FIELDS[16] = "Pump_PWM"
POSITIONAL_FIELDS[17] = "Brazier"
POSITIONAL_FIELDS[18] = "Profile"
POSITIONAL_FIELDS[20] = "Active_Mode"
POSITIONAL_FIELDS[21] = "Active_Live"
POSITIONAL_FIELDS[22] = "Control_Mode"
POSITIONAL_FIELDS[23] = "Eco_Mode"
POSITIONAL_FIELDS[24] = "Silent_Mode"
POSITIONAL_FIELDS[25] = "Chronostat"
POSITIONAL_FIELDS[26] = "Temperature_Setpoint"
POSITIONAL_FIELDS[27] = "Boiler_Setpoint"
POSITIONAL_FIELDS[28] = "Temperature_Motherboard"
# Power_Level is intentionally not parsed from RecuperoInfo positional frames.
# On the tested EGO Air setup this position can contain unrelated values such
# as 14 while the actual user-selected power is 4. Power is updated only from
# explicit JSON deltas {"Power_Level": x} or from optimistic command updates.
POSITIONAL_FIELDS[30] = "FirmwareVersion"
POSITIONAL_FIELDS[31] = "DatabaseID"
POSITIONAL_FIELDS[32] = "Date_Time_Hours"
POSITIONAL_FIELDS[33] = "Date_Time_Minutes"
POSITIONAL_FIELDS[34] = "Date_Day_Of_Month"
POSITIONAL_FIELDS[35] = "Date_Month"
POSITIONAL_FIELDS[36] = "Date_Year"
POSITIONAL_FIELDS[37] = "Total_Operating_Hours"
POSITIONAL_FIELDS[38] = "Hours_Of_Operation_In_Power1"
POSITIONAL_FIELDS[39] = "Hours_Of_Operation_In_Power2"
POSITIONAL_FIELDS[40] = "Hours_Of_Operation_In_Power3"
POSITIONAL_FIELDS[41] = "Hours_Of_Operation_In_Power4"
POSITIONAL_FIELDS[42] = "Hours_Of_Operation_In_Power5"
POSITIONAL_FIELDS[43] = "Hours_To_Service"
POSITIONAL_FIELDS[44] = "Minutes_To_Switch_Off"
POSITIONAL_FIELDS[45] = "Number_Of_Ignitions"
POSITIONAL_FIELDS[46] = "Active_Temperature"
# Pellet_Sensor at position 47 is intentionally not exposed for this setup.
POSITIONAL_FIELDS[48] = "Celcius_Or_Fahrenheit"
POSITIONAL_FIELDS[49] = "Sound_Effects"
POSITIONAL_FIELDS[50] = "Sleep"
POSITIONAL_FIELDS[51] = "Mode"
POSITIONAL_FIELDS[59] = "Return_Temperature"
POSITIONAL_FIELDS[60] = "AntiFreeze"

TEMPERATURE_FIELDS = {
    "Ambient_Temperature",
    "Puffer_Temperature",
    "Boiler_Temperature",
    "NTC3_Temperature",
    "Temperature_Setpoint",
    "Boiler_Setpoint",
    "Temperature_Motherboard",
    "Return_Temperature",
}

TIMESPAN_FIELDS = {
    "Total_Operating_Hours",
    "Hours_Of_Operation_In_Power1",
    "Hours_Of_Operation_In_Power2",
    "Hours_Of_Operation_In_Power3",
    "Hours_Of_Operation_In_Power4",
    "Hours_Of_Operation_In_Power5",
}

BOOL_FIELDS = {
    "Power",
    "Eco_Mode",
    "Silent_Mode",
    "Active_Mode",
    "Sound_Effects",
    "Alarm",
    "Summer_Winter",
    "Mode",
    "Control_Mode",
    "Chronostat",
    "Celcius_Or_Fahrenheit",
    "Sleep",
    "AntiFreeze",
    "Diagnostics",
}

INT_FIELDS = {
    "Fan_State",
    "DuctedFan1",
    "DuctedFan2",
    "Power_Level",
    "Stove_State",
    "Fume_Temperature",
    "RPM_Fam_Fume",
    "Candle_Condition",
    "ACTIVE_Set",
    "RPM_WormWheel_Set",
    "RPM_WormWheel_Live",
    "Pump_PWM",
    "Brazier",
    "Profile",
    "Active_Live",
    "FirmwareVersion",
    "DatabaseID",
    "Date_Time_Hours",
    "Date_Time_Minutes",
    "Date_Day_Of_Month",
    "Date_Month",
    "Date_Year",
    "Hours_To_Service",
    "Minutes_To_Switch_Off",
    "Number_Of_Ignitions",
    "Active_Temperature",
}

KEY_MAP = {
    "Power": "power",
    "Stove_State": "stove_state",
    "Fan_State": "fan_state",
    "DuctedFan1": "ducted_fan_1",
    "DuctedFan2": "ducted_fan_2",
    "Fume_Temperature": "fume_temperature",
    "Ambient_Temperature": "ambient_temperature",
    "Puffer_Temperature": "puffer_temperature",
    "Boiler_Temperature": "boiler_temperature",
    "NTC3_Temperature": "ntc3_temperature",
    "Candle_Condition": "candle_condition",
    "ACTIVE_Set": "active_set",
    "Temperature_Setpoint": "temperature_setpoint",
    "Boiler_Setpoint": "boiler_setpoint",
    "Temperature_Motherboard": "motherboard_temperature",
    "Power_Level": "power_level",
    "Eco_Mode": "eco_mode",
    "Silent_Mode": "silent_mode",
    "Active_Mode": "active_mode",
    "Sound_Effects": "sound_effects",
    "Profile": "profile",
    "Alarm": "alarm",
    "Alarm_Code": "alarm_code",
    "Summer_Winter": "summer_winter",
    "Mode": "summer_mode",
    "Control_Mode": "control_mode",
    "Chronostat": "chronostat",
    "Active_Live": "active_live",
    "Date_Time_Hours": "stove_time_hours",
    "Date_Time_Minutes": "stove_time_minutes",
    "Date_Day_Of_Month": "stove_day_of_month",
    "Date_Month": "stove_month",
    "Date_Year": "stove_year",
    "RPM_Fam_Fume": "rpm_fume_fan",
    "RPM_WormWheel_Set": "rpm_wormwheel_set",
    "RPM_WormWheel_Live": "rpm_wormwheel_live",
    "Pump_PWM": "pump_pwm",
    "Brazier": "brazier",
    "FirmwareVersion": "firmware_version",
    "DatabaseID": "database_id",
    "Total_Operating_Hours": "total_operating_hours",
    "Hours_Of_Operation_In_Power1": "hours_power_1",
    "Hours_Of_Operation_In_Power2": "hours_power_2",
    "Hours_Of_Operation_In_Power3": "hours_power_3",
    "Hours_Of_Operation_In_Power4": "hours_power_4",
    "Hours_Of_Operation_In_Power5": "hours_power_5",
    "Hours_To_Service": "hours_to_service",
    "Minutes_To_Switch_Off": "minutes_to_switch_off",
    "Number_Of_Ignitions": "number_of_ignitions",
    "Active_Temperature": "active_temperature",
    "Celcius_Or_Fahrenheit": "celsius_or_fahrenheit",
    "Sleep": "sleep",
    "Return_Temperature": "return_temperature",
    "AntiFreeze": "antifreeze",
    "Diagnostics": "diagnostics_mode",
}

STOVE_POWER_BY_STATE: dict[int, int] = {
    0: 0, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1,
    10: 1, 11: 1, 12: 1, 13: 1, 14: 1, 15: 1, 30: 0, 31: 1, 40: 1,
    41: 1, 42: 1, 43: 1, 44: 0, 45: 0, 46: 0, 48: 0, 49: 0, 50: 0,
    51: 0, 52: 0, 53: 0, 54: 0, 55: 0, 56: 0, 57: 0, 58: 0, 59: 0,
    60: 0, 61: 0, 62: 0, 63: 0, 64: 0, 65: 0, 66: 0, 67: 0, 69: 0,
}

STOVE_STATE_LABELS: dict[int, str] = {
    0: "Éteint",
    1: "Contrôle chaud/froid",
    2: "Nettoyage à froid",
    3: "Chargement granulés à froid",
    4: "Allumage 1 à froid",
    5: "Allumage 2 à froid",
    6: "Nettoyage à chaud",
    7: "Chargement granulés à chaud",
    8: "Allumage 1 à chaud",
    9: "Allumage 2 à chaud",
    10: "Stabilisation",
    11: "Puissance 1",
    12: "Puissance 2",
    13: "Puissance 3",
    14: "Puissance 4",
    15: "Puissance 5",
    30: "Diagnostics",
    31: "Allumé",
    40: "Extinction",
    41: "Refroidissement",
    42: "Nettoyage bas",
    43: "Nettoyage haut",
    44: "Déblocage vis sans fin",
    45: "Auto Eco",
    46: "Veille",
    48: "Diagnostics",
    49: "Chargement vis sans fin",
    50: "Erreur A01 - échec allumage",
    51: "Erreur A02 - absence flamme",
    52: "Erreur A03 - surchauffe réservoir",
    53: "Erreur A04 - température fumées trop élevée",
    54: "Erreur A05 - obstruction conduit / vent",
    56: "Erreur A09 - sonde fumées",
    57: "Erreur A11 - motoréducteur",
    58: "Erreur A13 - température carte mère",
    63: "Erreur A21 - pressostat",
    64: "Erreur A22 - sonde ambiante",
}


def build_status_request() -> str:
    return STATUS_REQUEST


def build_command(command: str, value: Any) -> str:
    if command not in COMMAND_IDS:
        raise ValueError(f"Unsupported MCZ command: {command}")

    command_id = COMMAND_IDS[command]

    if command == "Power":
        value = 1 if _to_bool(value) else 40
    elif command == "Temperature_Setpoint":
        # MCZ encodes half degrees: 20.5 C => 41.
        value = int(round(float(value) * 2))
    elif command in BOOL_COMMANDS:
        value = 1 if _to_bool(value) else 0
    elif command in INT_COMMANDS:
        value = int(float(value))
    else:
        value = float(value)

    return f"C|WriteParametri|{command_id}|{value}"


def parse_status_message(raw: str | bytes) -> dict[str, Any]:
    if isinstance(raw, bytes):
        raw = raw.decode(errors="ignore")

    raw = raw.strip()
    if not raw:
        return {}

    if raw.startswith("{"):
        try:
            return normalize_status(json.loads(raw))
        except json.JSONDecodeError:
            _LOGGER.debug("Invalid MCZ JSON payload: %s", raw)
            return {"raw_message": raw}

    if "|" in raw:
        return normalize_status(_parse_pipe_frame(raw))

    return {"raw_message": raw}


def _parse_pipe_frame(raw: str) -> dict[str, Any]:
    parts = raw.split("|")
    data: dict[str, Any] = {}

    for index, value in enumerate(parts):
        if index >= len(POSITIONAL_FIELDS):
            break
        field = POSITIONAL_FIELDS[index]
        if not field:
            continue
        parsed = _parse_mcz_value(value)
        if parsed is not None:
            data[field] = parsed

    data["Raw_Frame"] = raw
    return data


def _parse_mcz_value(value: str) -> Any:
    value = value.strip()
    if value == "":
        return None

    try:
        return int(value, 16)
    except ValueError:
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value


def normalize_status(data: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}

    for source_key, value in data.items():
        target_key = KEY_MAP.get(source_key)
        if target_key is None:
            continue

        if source_key in TEMPERATURE_FIELDS:
            normalized[target_key] = _to_float(value, divide_by_two=True)
        elif source_key in TIMESPAN_FIELDS:
            normalized[target_key] = _to_hours(value)
        elif source_key in BOOL_FIELDS:
            normalized[target_key] = _to_bool(value)
        elif source_key in INT_FIELDS:
            normalized[target_key] = _to_int(value)
        else:
            normalized[target_key] = value

    stove_state = normalized.get("stove_state")
    if isinstance(stove_state, int):
        normalized.setdefault("power", bool(STOVE_POWER_BY_STATE.get(stove_state, 0)))
        normalized["stove_state_label"] = STOVE_STATE_LABELS.get(stove_state, str(stove_state))
        normalized["diagnostics_mode"] = stove_state in {30, 48}

    if "Brazier" in data and "brazier" in normalized:
        normalized["brazier_label"] = "OK" if normalized["brazier"] == 0 else "CLR"

    # Do not derive Power_Level from Stove_State. Stove_State 11..15 is the
    # combustion state label, not necessarily the configured power level.

    if "Raw_Frame" in data:
        normalized["raw_frame"] = data["Raw_Frame"]

    normalized["raw"] = data
    return normalized


def command_to_update(command: str, value: Any) -> dict[str, Any]:
    """Return an optimistic normalized state update for a successfully sent command."""
    if command == "Power":
        return {"power": bool(_to_bool(value))}
    if command == "Power_Level":
        return {"power_level": _to_int(value)}
    if command == "Fan_State":
        return {"fan_state": _to_int(value)}
    if command == "DuctedFan1":
        return {"ducted_fan_1": _to_int(value)}
    if command == "DuctedFan2":
        return {"ducted_fan_2": _to_int(value)}
    if command == "Eco_Mode":
        return {"eco_mode": _to_bool(value)}
    if command == "Silent_Mode":
        return {"silent_mode": _to_bool(value)}
    if command == "Active_Mode":
        return {"active_mode": _to_bool(value)}
    if command == "Sound_Effects":
        return {"sound_effects": _to_bool(value)}
    if command == "Summer_Mode":
        return {"summer_mode": _to_bool(value)}
    if command == "Temperature_Setpoint":
        return {"temperature_setpoint": _to_float(value)}
    if command == "Profile":
        return {"profile": _to_int(value)}
    return {}


def merge_status(previous: dict[str, Any] | None, update: dict[str, Any]) -> dict[str, Any]:
    """Merge delta updates because MCZ often only returns changed values."""
    merged = dict(previous or {})
    for key, value in update.items():
        if key == "raw" and isinstance(value, dict):
            previous_raw = merged.get("raw") if isinstance(merged.get("raw"), dict) else {}
            merged["raw"] = {**previous_raw, **value}
        else:
            merged[key] = value
    return merged


def _to_float(value: Any, divide_by_two: bool = False) -> float | None:
    try:
        if value is None or value == "":
            return None
        result = float(value)
        return result / 2 if divide_by_two else result
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> int | None:
    try:
        if value is None or value == "":
            return None
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _to_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "on", "yes", "open", "opened", "active", "enabled"}:
        return True
    if text in {"0", "false", "off", "no", "closed", "inactive", "disabled"}:
        return False
    try:
        return int(float(text)) != 0
    except ValueError:
        return None


def _to_hours(value: Any) -> float | None:
    """Convert MCZ timespan values to hours.

    RecuperoInfo frames contain seconds as hexadecimal integers. JSON emitted by
    maestrogateway can already be formatted as H:MM:SS, so both forms are accepted.
    """
    if value is None or value == "":
        return None
    if isinstance(value, str) and ":" in value:
        try:
            hours, minutes, seconds = value.split(":", 2)
            return int(hours) + int(minutes) / 60 + int(seconds) / 3600
        except (TypeError, ValueError):
            return None
    try:
        return float(value) / 3600
    except (TypeError, ValueError):
        return None
