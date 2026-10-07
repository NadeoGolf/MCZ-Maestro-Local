from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import logging
from typing import Any, Awaitable, Callable, TypeVar

import websockets

from .const import DEFAULT_COMMAND_RECV_TIMEOUT, DEFAULT_OPEN_TIMEOUT, DEFAULT_RECV_TIMEOUT, DEFAULT_RETRIES
from .protocol import build_command, build_status_request, command_to_update, merge_status, parse_status_message

_LOGGER = logging.getLogger(__name__)
_T = TypeVar("_T")


class MczMaestroError(Exception):
    """MCZ Maestro communication error."""


class MczMaestroClient:
    def __init__(
        self,
        host: str,
        port: int,
        *,
        open_timeout: float = DEFAULT_OPEN_TIMEOUT,
        recv_timeout: float = DEFAULT_RECV_TIMEOUT,
        command_recv_timeout: float = DEFAULT_COMMAND_RECV_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
    ) -> None:
        self.host = host
        self.port = port
        self.uri = f"ws://{host}:{port}"
        self.open_timeout = max(1.0, float(open_timeout))
        self.recv_timeout = max(0.5, float(recv_timeout))
        self.command_recv_timeout = max(0.5, float(command_recv_timeout))
        self.retries = max(0, int(retries))
        self._lock = asyncio.Lock()
        self._last_status: dict[str, Any] = {}

        self.status_requests = 0
        self.commands_sent = 0
        self.communication_errors = 0
        self.last_raw_message: str | None = None
        self.last_raw_frame: str | None = None
        self.last_command: str | None = None
        self.last_command_payload: str | None = None
        self.last_error: str | None = None
        self.last_success_at: str | None = None

    async def get_status(self) -> dict[str, Any]:
        async with self._lock:
            return await self._with_retries("lecture", self._get_status_once)

    async def send_command(self, command: str, value: Any) -> None:
        payload = build_command(command, value)

        async def _send() -> None:
            await self._send_command_once(command, value, payload)

        async with self._lock:
            await self._with_retries("commande", _send)

    async def _get_status_once(self) -> dict[str, Any]:
        async with websockets.connect(self.uri, open_timeout=self.open_timeout, close_timeout=1) as websocket:
            payload = build_status_request()
            _LOGGER.debug("MCZ status request: %s", payload)
            await websocket.send(payload)
            self.status_requests += 1

            current = dict(self._last_status)
            # The stove may answer with one full frame or several delta messages.
            for _ in range(8):
                try:
                    raw = await asyncio.wait_for(websocket.recv(), timeout=self.recv_timeout)
                except asyncio.TimeoutError:
                    break
                update = self._parse_update(raw)
                current = merge_status(current, update)

            self._last_status = current
            self._mark_success()
            return current

    async def _send_command_once(self, command: str, value: Any, payload: str) -> None:
        async with websockets.connect(self.uri, open_timeout=self.open_timeout, close_timeout=1) as websocket:
            _LOGGER.debug("MCZ send: %s", payload)
            await websocket.send(payload)
            self.commands_sent += 1
            self.last_command = command
            self.last_command_payload = payload

            optimistic_update = command_to_update(command, value)
            if optimistic_update:
                self._last_status = merge_status(self._last_status, optimistic_update)

            # Some firmwares only acknowledge by closing/remaining silent; others send a delta.
            for _ in range(3):
                try:
                    raw = await asyncio.wait_for(websocket.recv(), timeout=self.command_recv_timeout)
                except asyncio.TimeoutError:
                    break
                update = self._parse_update(raw)
                self._last_status = merge_status(self._last_status, update)

            self._mark_success()

    async def _with_retries(self, operation: str, func: Callable[[], Awaitable[_T]]) -> _T:
        last_err: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                return await func()
            except Exception as err:  # noqa: BLE001 - websocket stack raises several exception types
                last_err = err
                self.communication_errors += 1
                self.last_error = f"{type(err).__name__}: {err}"
                if attempt >= self.retries:
                    break
                _LOGGER.debug(
                    "MCZ %s failed, retrying (%s/%s): %s",
                    operation,
                    attempt + 1,
                    self.retries,
                    err,
                    exc_info=True,
                )
                await asyncio.sleep(0.5 * (attempt + 1))

        raise MczMaestroError(f"Erreur {operation} WebSocket MCZ: {last_err}") from last_err

    def _parse_update(self, raw: str | bytes) -> dict[str, Any]:
        raw_text = raw.decode(errors="ignore") if isinstance(raw, bytes) else str(raw)
        self.last_raw_message = raw_text
        _LOGGER.debug("MCZ recv: %s", raw_text)
        update = parse_status_message(raw)
        if raw_frame := update.get("raw_frame"):
            self.last_raw_frame = str(raw_frame)
        return update

    def _mark_success(self) -> None:
        self.last_success_at = datetime.now(timezone.utc).isoformat()
        self.last_error = None

    @property
    def diagnostics(self) -> dict[str, Any]:
        """Return communication diagnostics without exposing credentials."""
        return {
            "uri": f"ws://***:{self.port}",
            "open_timeout": self.open_timeout,
            "recv_timeout": self.recv_timeout,
            "command_recv_timeout": self.command_recv_timeout,
            "retries": self.retries,
            "status_requests": self.status_requests,
            "commands_sent": self.commands_sent,
            "communication_errors": self.communication_errors,
            "last_command": self.last_command,
            "last_command_payload": self.last_command_payload,
            "last_error": self.last_error,
            "last_success_at": self.last_success_at,
            "last_raw_message": self.last_raw_message,
            "last_raw_frame": self.last_raw_frame,
        }
