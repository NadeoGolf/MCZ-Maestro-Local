from __future__ import annotations

import importlib.util
from pathlib import Path

PROTOCOL_PATH = Path(__file__).resolve().parents[1] / "custom_components" / "mcz_maestro" / "protocol.py"
spec = importlib.util.spec_from_file_location("mcz_maestro_protocol", PROTOCOL_PATH)
protocol = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(protocol)

build_command = protocol.build_command
command_to_update = protocol.command_to_update
merge_status = protocol.merge_status
normalize_status = protocol.normalize_status
parse_status_message = protocol.parse_status_message


def test_build_power_commands():
    assert build_command("Power", True) == "C|WriteParametri|34|1"
    assert build_command("Power", False) == "C|WriteParametri|34|40"


def test_build_safe_commands():
    assert build_command("Power_Level", 3) == "C|WriteParametri|36|3"
    assert build_command("Temperature_Setpoint", 20.5) == "C|WriteParametri|42|41"
    assert build_command("Eco_Mode", True) == "C|WriteParametri|41|1"
    assert build_command("Silent_Mode", False) == "C|WriteParametri|45|0"
    assert build_command("Active_Mode", True) == "C|WriteParametri|35|1"
    assert build_command("Sound_Effects", False) == "C|WriteParametri|50|0"
    assert build_command("Profile", 4) == "C|WriteParametri|149|4"


def test_json_delta_normalization():
    parsed = parse_status_message('{"Temperature_Setpoint": 41, "Eco_Mode": 1}')
    assert parsed["temperature_setpoint"] == 20.5
    assert parsed["eco_mode"] is True


def test_pipe_frame_core_values():
    # Indexes: 1=state, 5=fume temp, 6=ambient temp, 23=eco, 24=silent, 26=setpoint.
    parts = ["01"] + ["00"] * 60
    parts[1] = "0B"
    parts[5] = "9B"
    parts[6] = "2F"
    parts[23] = "01"
    parts[24] = "00"
    parts[26] = "29"
    parts[37] = "00000E10"  # 3600 seconds = 1 hour
    parsed = parse_status_message("|".join(parts))
    assert parsed["stove_state"] == 11
    assert parsed["stove_state_label"] == "Puissance 1"
    assert parsed["power"] is True
    assert parsed["fume_temperature"] == 155
    assert parsed["ambient_temperature"] == 23.5
    assert parsed["eco_mode"] is True
    assert parsed["silent_mode"] is False
    assert parsed["temperature_setpoint"] == 20.5
    assert parsed["total_operating_hours"] == 1


def test_no_positional_power_level_derivation():
    parts = ["01"] + ["00"] * 60
    parts[1] = "0E"  # Stove_State = Power 4 state
    parts[29] = "0E"  # intentionally ignored
    parsed = parse_status_message("|".join(parts))
    assert "power_level" not in parsed


def test_merge_status_keeps_previous_raw_values():
    merged = merge_status({"raw": {"A": 1}, "power": False}, {"raw": {"B": 2}, "power": True})
    assert merged["raw"] == {"A": 1, "B": 2}
    assert merged["power"] is True


def test_command_to_update_temperature_setpoint():
    assert command_to_update("Temperature_Setpoint", 21.5) == {"temperature_setpoint": 21.5}


def test_normalize_timespan_string_from_gateway():
    parsed = normalize_status({"Total_Operating_Hours": "307:00:00"})
    assert parsed["total_operating_hours"] == 307
