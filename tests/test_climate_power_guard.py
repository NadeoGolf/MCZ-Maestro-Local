"""Regression tests for redundant MCZ power-off commands.

The production climate entity imports Home Assistant. This small, isolated
method test allows checking the stove-state guard without a HA installation.
"""

from __future__ import annotations

import ast
import asyncio
from datetime import datetime, timedelta, timezone
import logging
from pathlib import Path

import pytest

CLIMATE_PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "mcz_maestro"
    / "climate.py"
)


def _power_method():
    module = ast.parse(CLIMATE_PATH.read_text(encoding="utf-8"))
    entity = next(
        node for node in module.body
        if isinstance(node, ast.ClassDef) and node.name == "MczMaestroClimate"
    )
    method = next(
        node for node in entity.body
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "_async_send_power"
    )
    isolated = ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[]))
    namespace = {
        "datetime": datetime,
        "timezone": timezone,
        "_LOGGER": logging.getLogger(__name__),
    }
    exec(compile(isolated, str(CLIMATE_PATH), "exec"), namespace)
    return namespace["_async_send_power"]


class _FakeClient:
    def __init__(self):
        self.commands = []

    async def send_command(self, command, value):
        self.commands.append((command, value))


class _FakeCoordinator:
    def __init__(self, status):
        self.data = status
        self.client = _FakeClient()

    async def async_send_command(self, command, value):
        await self.client.send_command(command, value)


class _FakeClimate:
    def __init__(self, status):
        self.coordinator = _FakeCoordinator(status)
        self._last_power_command = None
        self.min_cycle_duration_seconds = 600


@pytest.mark.parametrize("state", [0, 40, 41, "0", "40", "41"])
def test_off_is_not_sent_for_off_or_cooling_stove(state):
    entity = _FakeClimate({"stove_state": state, "power": True})
    asyncio.run(_power_method()(entity, False, bypass_min_cycle=True))
    assert entity.coordinator.client.commands == []
    assert entity._last_power_command is None


@pytest.mark.parametrize("state", [1, 11, 15, 31, 42, 43, 45, 46, 30])
def test_off_is_sent_for_other_stove_states(state):
    entity = _FakeClimate({"stove_state": state, "power": True})
    asyncio.run(_power_method()(entity, False, bypass_min_cycle=True))
    assert entity.coordinator.client.commands == [("Power", False)]
    assert entity._last_power_command is not None


@pytest.mark.parametrize("status", [{}, {"power": False}, {"stove_state": "invalid"}, {"stove_state": None}])
def test_unknown_stove_state_does_not_block_off(status):
    entity = _FakeClimate(status)
    asyncio.run(_power_method()(entity, False, bypass_min_cycle=True))
    assert entity.coordinator.client.commands == [("Power", False)]


def test_turn_on_is_not_blocked_by_off_guard():
    entity = _FakeClimate({"stove_state": 0})
    asyncio.run(_power_method()(entity, True, bypass_min_cycle=True))
    assert entity.coordinator.client.commands == [("Power", True)]


def test_off_obeys_minimum_cycle_when_not_bypassed():
    entity = _FakeClimate({"stove_state": 11})
    entity._last_power_command = datetime.now(timezone.utc) - timedelta(seconds=20)
    asyncio.run(_power_method()(entity, False))
    assert entity.coordinator.client.commands == []
