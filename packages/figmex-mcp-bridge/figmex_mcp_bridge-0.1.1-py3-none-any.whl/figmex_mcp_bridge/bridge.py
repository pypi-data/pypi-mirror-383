from __future__ import annotations

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, Optional

import websockets
from websockets.server import WebSocketServer, WebSocketServerProtocol

logger = logging.getLogger(__name__)


@dataclass
class FigmaEvent:
    event: str
    payload: Any


class FigmaBridge:
    """Manages a websocket connection to the Figmex plugin."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8787,
        *,
        connection_timeout: float = 30.0,
    ) -> None:
        self.host = host
        self.port = port
        self.connection_timeout = connection_timeout

        self._server: Optional[WebSocketServer] = None
        self._socket: Optional[WebSocketServerProtocol] = None
        self._pending: Dict[str, asyncio.Future[Any]] = {}
        self._connected = asyncio.Event()
        self._supported_commands: list[str] = []
        self._event_consumers: list[Callable[[FigmaEvent], Awaitable[None]]] = []
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        """Start the websocket server."""
        if self._server is not None:
            return

        self._server = await websockets.serve(
            self._handle_connection,
            self.host,
            self.port,
            ping_interval=None,
        )
        logger.info("Figmex bridge listening on ws://%s:%s", self.host, self.port)

    async def stop(self) -> None:
        """Stop the websocket server."""
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
        await self._close_connection()

    async def _handle_connection(
        self,
        websocket: WebSocketServerProtocol,
        _path: str,
    ) -> None:
        logger.info("Figma plugin connected from %s", websocket.remote_address)

        async with self._lock:
            await self._close_connection()
            self._socket = websocket
            self._connected.set()

        try:
            async for raw in websocket:
                try:
                    message = json.loads(raw)
                except json.JSONDecodeError as exc:
                    logger.warning("Invalid JSON from plugin: %s", exc)
                    continue
                await self._dispatch_message(message)
        except websockets.ConnectionClosed:
            logger.info("Figma plugin disconnected")
        finally:
            async with self._lock:
                await self._close_connection()

    async def _close_connection(self) -> None:
        if self._socket:
            try:
                await self._socket.close()
            except Exception as exc:  # noqa: BLE001
                logger.debug("Error closing websocket: %s", exc)
        self._socket = None
        self._connected.clear()
        self._supported_commands = []
        for request_id, future in list(self._pending.items()):
            if not future.done():
                future.set_exception(ConnectionError("Disconnected from Figma plugin"))
            self._pending.pop(request_id, None)

    async def _dispatch_message(self, message: Dict[str, Any]) -> None:
        message_type = message.get("type")
        if message_type == "bootstrap":
            payload = message.get("payload", {})
            commands = payload.get("supportedCommands", [])
            self._supported_commands = list(commands)
            logger.info("Plugin bootstrap received (%d commands)", len(commands))
            return

        if message_type == "mcp-response":
            request_id = message.get("requestId")
            if not request_id:
                logger.warning("Response missing requestId: %s", message)
                return
            future = self._pending.get(request_id)
            if not future:
                logger.warning("No pending request for id %s", request_id)
                return
            if future.done():
                logger.debug("Future already resolved for id %s", request_id)
                return
            if message.get("ok"):
                future.set_result(message.get("result"))
            else:
                error = message.get("error", {})
                future.set_exception(RuntimeError(error.get("message", "Unknown error")))
            return

        if message_type == "mcp-event":
            event_name = message.get("event", "unknown")
            event_payload = message.get("payload")
            logger.debug("Received event %s", event_name)
            await self._publish_event(FigmaEvent(event_name, event_payload))
            return

        logger.debug("Unhandled message: %s", message_type)

    async def _publish_event(self, event: FigmaEvent) -> None:
        if not self._event_consumers:
            return
        await asyncio.gather(
            *(consumer(event) for consumer in self._event_consumers),
            return_exceptions=True,
        )

    async def wait_until_connected(self, timeout: Optional[float] = None) -> None:
        """Wait until the plugin is connected."""
        timeout = timeout or self.connection_timeout
        try:
            await asyncio.wait_for(self._connected.wait(), timeout=timeout)
        except asyncio.TimeoutError as exc:
            raise TimeoutError(
                f"Figma plugin did not connect within {timeout} seconds."
            ) from exc

    async def execute(self, command: str, args: Optional[Dict[str, Any]] = None) -> Any:
        """Send a command to the Figma plugin and await the response."""
        await self.wait_until_connected()
        if self._socket is None:
            raise ConnectionError("Figma plugin is not connected.")

        request_id = uuid.uuid4().hex
        payload: Dict[str, Any] = {
            "type": "mcp-command",
            "requestId": request_id,
            "command": {"name": command},
        }
        if args:
            payload["command"]["args"] = args

        future: asyncio.Future[Any] = asyncio.get_running_loop().create_future()
        self._pending[request_id] = future

        try:
            await self._socket.send(json.dumps(payload))
            result = await asyncio.wait_for(future, timeout=30.0)
            return result
        except asyncio.TimeoutError as exc:
            raise TimeoutError(f"Command '{command}' timed out.") from exc
        finally:
            self._pending.pop(request_id, None)

    def register_event_consumer(
        self,
        consumer: Callable[[FigmaEvent], Awaitable[None]],
    ) -> None:
        """Register a callback for streaming events."""
        self._event_consumers.append(consumer)

    @property
    def supported_commands(self) -> list[str]:
        return list(self._supported_commands)
