#!/usr/bin/env python3
"""Main entry point for mcp-server-flockx."""

import os
import sys
from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.openapi import RouteMap, MCPType
import httpx


def main():
    """Main entry point for the MCP server."""
    # Load environment variables from .env
    load_dotenv()

    # Get API key from environment
    flockx_api_key = os.getenv("FLOCKX_API_KEY")
    if not flockx_api_key:
        print("Error: FLOCKX_API_KEY environment variable not set", file=sys.stderr)
        print("", file=sys.stderr)
        print("To get your API key:", file=sys.stderr)
        print("  1. Sign up at https://agents.flockx.io", file=sys.stderr)
        print("  2. Go to your profile", file=sys.stderr)
        print("  3. Copy your API key", file=sys.stderr)
        print("", file=sys.stderr)
        print("Then set it in your environment:", file=sys.stderr)
        print("  export FLOCKX_API_KEY='your-api-key-here'", file=sys.stderr)
        print("", file=sys.stderr)
        print("Or add it to your MCP configuration.", file=sys.stderr)
        return 1

    try:
        client = httpx.AsyncClient(
            base_url="https://api.flockx.io/api",
            headers={
                "Authorization": f"Token {flockx_api_key}",
            },
        )
        openapi_spec = httpx.get("https://api.flockx.io/api/openapi.json").json()

        # Create the MCP server
        server = FastMCP.from_openapi(
            openapi_spec=openapi_spec,
            client=client,
            name="flockx-mcp",
            # Convert all routes to tools by default
            route_maps=[RouteMap(mcp_type=MCPType.TOOL)],
        )

        # Run in stdio mode for Cursor integration
        server.run()
        return 0

    except KeyboardInterrupt:
        print("\nShutdown requested... exiting", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"Error starting MCP server: {e}", file=sys.stderr)
        return 1


# Support being run as a module
if __name__ == "__main__":
    sys.exit(main())
