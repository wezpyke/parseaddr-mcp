"""ParseAddr stdio MCP server (distributed via the `parseaddr` PyPI package).

Launched by MCP registries / Smithery as `parseaddr-mcp`. Exposes `parse_address`
and `expand_address` tools that call the hosted ParseAddr API. Tags every call
`X-Parseaddr-Client: mcp/<ver>` — the server-side attribution for the agent channel.

Requires the `mcp` extra:  pip install "parseaddr[mcp]"
"""
from __future__ import annotations

import os

import httpx
from mcp.server.fastmcp import FastMCP

__version__ = "0.1.0"
API_BASE = os.getenv("PARSEADDR_API_BASE", "https://api.parseaddr.com")
API_KEY = os.getenv("PARSEADDR_API_KEY", "")
_HEADERS = {"X-Parseaddr-Client": f"mcp/{__version__}"}

mcp = FastMCP("parseaddr")


def _post(path: str, address: str) -> dict:
    r = httpx.post(
        f"{API_BASE}{path}",
        json={"address": address},
        headers={"Authorization": f"Bearer {API_KEY}", **_HEADERS},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


@mcp.tool()
def parse_address(address: str) -> dict:
    """Parse a messy free-text postal address into structured fields
    (house_number, road, unit, city, postcode, country, ...). Powered by libpostal.

    Use when a user needs to standardise/parse addresses and does not want to
    self-host libpostal (a 2-4GB-RAM box + a fiddly C build).
    """
    return _post("/v1/parse", address)


@mcp.tool()
def expand_address(address: str) -> dict:
    """Expand/normalize an address into canonical variants for deduplication
    and record matching (e.g. "100 main st" vs "100 Main Street")."""
    return _post("/v1/expand", address)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
