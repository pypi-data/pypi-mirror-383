"""MCP server for mobile-use with screen analysis capabilities."""

import argparse
import logging
import os
import sys
import threading

# Fix Windows console encoding for Unicode characters (emojis in logs)
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    os.environ["PYTHONIOENCODING"] = "utf-8"

    try:
        import colorama

        colorama.init(strip=False, convert=True, wrap=True)
    except ImportError:
        pass


from fastmcp import FastMCP  # noqa: E402

from minitap.mcp.core.agents import agent
from minitap.mcp.core.config import settings  # noqa: E402
from minitap.mcp.core.device import (
    DeviceInfo,  # noqa: E402
    list_available_devices,  # noqa: E402; noqa: E402
)
from minitap.mcp.server.middleware import MaestroCheckerMiddleware
from minitap.mcp.server.poller import device_health_poller

logger = logging.getLogger(__name__)


mcp = FastMCP(
    name="mobile-use-mcp",
    instructions="""
        This server provides analysis tools for connected
        mobile devices (iOS or Android).
        Call get_available_devices() to list them.
    """,
)

from minitap.mcp.tools import (  # noqa: E402, F401
    analyze_screen,
    execute_mobile_command,
    go_back,
)


@mcp.resource("data://devices")
def get_available_devices() -> list[DeviceInfo]:
    """Provides a list of connected mobile devices (iOS or Android)."""
    return list_available_devices()


def mcp_lifespan(**mcp_run_kwargs):
    mcp.add_middleware(MaestroCheckerMiddleware(agent))

    # Start device health poller in background
    logger.info("Device health poller started")
    stop_event = threading.Event()
    poller_thread = threading.Thread(
        target=device_health_poller,
        args=(
            stop_event,
            agent,
        ),
    )
    poller_thread.start()

    try:
        mcp.run(**mcp_run_kwargs)
    except KeyboardInterrupt:
        pass

    # Stop device health poller
    stop_event.set()
    logger.info("Device health poller stopping...")
    poller_thread.join()
    logger.info("Device health poller stopped")


def main() -> None:
    """Main entry point for the MCP server."""
    parser = argparse.ArgumentParser(description="Mobile Use MCP Server")
    parser.add_argument(
        "--server",
        action="store_true",
        help="Run as network server (uses MCP_SERVER_HOST and MCP_SERVER_PORT from env)",
    )

    args = parser.parse_args()

    # Run MCP server with optional host/port for remote access
    if args.server:
        logger.info(f"Starting MCP server on {settings.MCP_SERVER_HOST}:{settings.MCP_SERVER_PORT}")
        mcp_lifespan(
            transport="http",
            host=settings.MCP_SERVER_HOST,
            port=settings.MCP_SERVER_PORT,
        )
    else:
        logger.info("Starting MCP server in local mode")
        mcp_lifespan()
