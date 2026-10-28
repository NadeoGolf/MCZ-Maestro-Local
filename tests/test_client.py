"""Client tests with a fake WebSocket, without Home Assistant or a stove."""

from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path
import sys
import types

import pytest

COMPONENT = Path(__file__).resolve().parents[1] / "custom_components" / "mcz_maestro"
PACKAGE = "mcz_maestro_client_test"


class _FakeWebSocket:
    def __init__(self, messages):
        self.messages = list(messages)
        self.sent = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def send(self, payload):
        self.sent.append(payload)

    async def recv(self):
        if self.messages:
            return self.messages.pop(0)
        await asyncio.sleep(3600)


def _load_client(messages):
    websockets = types.ModuleType("websockets")
    websockets.connect = lambda *args, **kwargs: _FakeWebSocket(messages)
    sys.modules["websockets"] = websockets

    package = types.ModuleType(PACKAGE)
    package.__path__ = [str(COMPONENT)]
    sys.modules[PACKAGE] = package
    for name in ("const", "protocol", "client"):
        spec = importlib.util.spec_from_file_location(f"{PACKAGE}.{name}", COMPONENT / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    return sys.modules[f"{PACKAGE}.client"]


def _client(module):
    return module.MczMaestroClient("stove.local", 81, recv_timeout=0.5, retries=0)


def test_status_without_any_answer_is_an_error():
    module = _load_client([])
    client = _client(module)
    with pytest.raises(module.MczMaestroError):
        asyncio.run(client.get_status())
    assert client.last_error is not None


def test_status_with_answer_is_returned():
    module = _load_client(['{"Temperature_Setpoint": 41}'])
    client = _client(module)
    status = asyncio.run(client.get_status())
    assert status["temperature_setpoint"] == 20.5
    assert client.last_error is None
