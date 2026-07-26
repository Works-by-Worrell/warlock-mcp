import argparse
import logging
import os
import sys

from . import resources, tools
from .core import mcp
from .resources.skills import load_dynamic_skills_tools

# Configure logging to go strictly to stderr
logger = logging.getLogger(__name__)

# Prevent Ruff from stripping registration side effects
_ = (resources, tools)


def main():
    parser = argparse.ArgumentParser("Warlock MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default=os.environ.get("FASTMCP_TRANSPORT", "stdio"),
        help="Transport protocol to use (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host address to bind to when running Streamable HTTP (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", 8080)),
        help="Port to bind to when running Streamable HTTP (default: 8080)",
    )
    parser.add_argument("--log-file", help="Path to write log output (redirects from stderr)")

    args = parser.parse_args()

    log_handlers = []

    if args.log_file:
        log_dir = os.path.dirname(os.path.abspath(args.log_file))
        os.makedirs(log_dir, exist_ok=True)
        log_handlers.append(logging.FileHandler(args.log_file))
    else:
        log_handlers.append(logging.StreamHandler(sys.stderr))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=log_handlers,
        force=True,
    )
    logging.getLogger("warlock").setLevel(logging.DEBUG)

    load_dynamic_skills_tools()

    if args.transport == "streamable-http":
        logger.info(
            f"Starting Warlock MCP Server in Streamable HTTP Mode on http://{args.host}:{args.port}/mcp"
        )
        mcp.settings.host = args.host
        mcp.settings.port = int(args.port)
        mcp.settings.transport_security.enable_dns_rebinding_protection = False
        mcp.run(transport="streamable-http")
    else:
        logger.info("Starting Warlock MCP Server in stdio mode")
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
