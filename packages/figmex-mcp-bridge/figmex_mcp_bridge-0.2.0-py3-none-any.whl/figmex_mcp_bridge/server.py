from __future__ import annotations

import logging
import json
from typing import Any, Dict, Optional

from fastmcp import FastMCP

from pydantic import BaseModel, model_validator

from .bridge import FigmaBridge, FigmaEvent

logger = logging.getLogger(__name__)


bridge = FigmaBridge()


class InvokeCommandInput(BaseModel):
    command: str
    args: Optional[Dict[str, Any]] = None

    @model_validator(mode="before")
    @classmethod
    def coerce_input(cls, value: Any) -> Dict[str, Any]:
        if isinstance(value, dict):
            data = dict(value)
        elif isinstance(value, str):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                parsed = value
            if isinstance(parsed, dict):
                data = dict(parsed)
            elif isinstance(parsed, str):
                data = {"command": parsed}
            else:
                raise ValueError("Input must be an object or a JSON string representing an object/command")
        else:
            raise ValueError("Input must be an object or a JSON string representing an object/command")

        if "params" in data and "args" not in data:
            data["args"] = data.pop("params")

        args = data.get("args")
        if isinstance(args, dict):
            if "nodeId" in args and "id" not in args:
                args["id"] = args.pop("nodeId")
            if "nodeIds" in args and "ids" not in args:
                args["ids"] = args.pop("nodeIds")

        return data


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
        await bridge.wait_until_bootstrapped()
        return {
            "commands": bridge.supported_commands,
            "definitions": bridge.command_definitions,
        }

    @mcp.tool()
    async def describe_figma_commands() -> Dict[str, Any]:
        """Detailed Figmex command reference, including argument metadata."""
        await bridge.wait_until_bootstrapped()
        return {"definitions": bridge.command_definitions}

    return mcp


__all__ = ["create_server"]
