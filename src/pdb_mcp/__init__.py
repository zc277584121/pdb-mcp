"""PDB MCP Server - A Model Context Protocol server for Python debugging"""

import asyncio
import atexit

import mcp.server.stdio

from .server import get_app, get_session

__version__ = "0.0.1"

# Export public API
__all__ = ["main", "get_app", "get_session"]


async def amain() -> None:
    """Async main entry point for the MCP server"""
    app = get_app()
    session = get_session()

    # Cleanup on exit
    atexit.register(session.cleanup)

    # Run the server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def main() -> None:
    """Main entry point for the MCP server"""
    asyncio.run(amain())


if __name__ == "__main__":
    main()
