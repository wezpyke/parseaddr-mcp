"""
parseaddr MCP server — the agent-native distribution centrepiece.

Exposes an `parse_address` tool over the Model Context Protocol so any MCP-capable
coding agent (Claude, Cursor, etc.) can clean addresses by calling our hosted API.
We list this server in the MCP registries (mcp.so, Smithery, Glama, LobeHub) so agents
discover it — machine-to-machine distribution, zero human posting.

Scaffold: correct shape. Requires `pip install mcp httpx` and PARSEADDR_API_KEY in env.
"""
from __future__ import annotations

import os
import httpx
from mcp.server.fastmcp import FastMCP

__version__ = "0.1.0"
API_BASE = os.getenv("PARSEADDR_API_BASE", "https://api.parseaddr.com")
API_KEY = os.getenv("PARSEADDR_API_KEY", "")

# Attribution: agent tool-calls carry no referrer/UTM, so the ONLY way to prove the
# agent-native channel is this server-side client header. The API tags each key's
# first-touch source from it. Do NOT remove — it's the Phase-3 hands-off-proof metric.
_CLIENT_HEADER = {"X-Parseaddr-Client": f"mcp/{__version__}"}

mcp = FastMCP("parseaddr")


@mcp.tool()
def parse_address(address: str) -> dict:
    """Parse a messy free-text postal address into structured fields
    (house_number, road, unit, city, postcode, country, ...). Powered by libpostal.

    Args:
        address: the raw address string, e.g. "flat 2, 10 downing st, london sw1a 2aa"
    Returns:
        dict with `parsed` (label->value) and `components` (ordered pairs).
    """
    r = httpx.post(
        f"{API_BASE}/v1/parse",
        json={"address": address},
        headers={"Authorization": f"Bearer {API_KEY}", **_CLIENT_HEADER},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    mcp.run()
