from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from textwrap import dedent
from typing import Optional

from .server import create_server


async def _serve_stdio(log_level: str) -> None:
    logging.basicConfig(level=getattr(logging, log_level.upper(), logging.INFO))
    mcp = await create_server()
    await mcp.run_stdio_async(show_banner=False)


async def _serve_http(host: str, port: int, log_level: str) -> None:
    logging.basicConfig(level=getattr(logging, log_level.upper(), logging.INFO))
    mcp = await create_server()
    await mcp.run_http_async(host=host, port=port, show_banner=False)


def _print_config(name: str, as_http: bool, host: str, port: int) -> None:
    if not as_http:
        snippet = f"""\
[mcp_servers.{name}]
command = "figmex-mcp-bridge"
args = ["serve"]
# Optional timeouts
startup_timeout_sec = 30
tool_timeout_sec = 60
"""
    else:
        snippet = f"""\
experimental_use_rmcp_client = true

[mcp_servers.{name}]
command = "figmex-mcp-bridge"
args = ["serve-http", "--host", "{host}", "--port", "{port}"]
url = "http://{host}:{port}/mcp"
startup_timeout_sec = 30
tool_timeout_sec = 60
"""
    print(dedent(snippet).strip())


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="figmex-mcp-bridge",
        description="Figmex MCP bridge launcher.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    serve_parser = subparsers.add_parser(
        "serve",
        help="Run the bridge as a stdio MCP server (recommended for Codex CLI).",
    )
    serve_parser.add_argument("--log-level", default="INFO")

    http_parser = subparsers.add_parser(
        "serve-http",
        help="Run the bridge as an HTTP MCP server.",
    )
    http_parser.add_argument("--host", default="127.0.0.1")
    http_parser.add_argument("--port", type=int, default=3845)
    http_parser.add_argument("--log-level", default="INFO")

    config_parser = subparsers.add_parser(
        "config",
        help="Print a config snippet for Codex CLI.",
    )
    config_parser.add_argument("--name", default="figmex")
    config_parser.add_argument(
        "--http",
        action="store_true",
        help="Generate a snippet for HTTP transport instead of stdio.",
    )
    config_parser.add_argument("--host", default="127.0.0.1")
    config_parser.add_argument("--port", type=int, default=3845)

    args = parser.parse_args(argv)

    if args.command == "serve":
        asyncio.run(_serve_stdio(args.log_level))
        return 0

    if args.command == "serve-http":
        asyncio.run(_serve_http(args.host, args.port, args.log_level))
        return 0

    if args.command == "config":
        _print_config(args.name, args.http, args.host, args.port)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
