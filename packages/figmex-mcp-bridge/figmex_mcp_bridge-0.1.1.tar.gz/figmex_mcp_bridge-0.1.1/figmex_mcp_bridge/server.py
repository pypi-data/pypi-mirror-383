from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastmcp import FastMCP

from pydantic import BaseModel

from .bridge import FigmaBridge, FigmaEvent

logger = logging.getLogger(__name__)


bridge = FigmaBridge()


class InvokeCommandInput(BaseModel):
    command: str
    args: Optional[Dict[str, Any]] = None


async def _log_events(event: FigmaEvent) -> None:
    logger.debug("Figma event %s", event.event)


async def create_server() -> FastMCP:
    """Factory for fastmcp run or the CLI to bootstrap the bridge."""
    await bridge.start()
    bridge.register_event_consumer(_log_events)

    mcp = FastMCP("Figmex MCP Bridge")

    @mcp.tool()
    async def invoke_figma_command(params: InvokeCommandInput) -> Any:
        """Call a Figmex command exposed by the plugin."""
        logger.info("Invoking Figma command '%s'", params.command)
        return await bridge.execute(params.command, params.args)

    @mcp.tool()
    async def list_figma_commands() -> Dict[str, Any]:
        """Return the commands advertised by the Figmex plugin."""
        return {"commands": bridge.supported_commands}

    return mcp


__all__ = ["create_server"]
