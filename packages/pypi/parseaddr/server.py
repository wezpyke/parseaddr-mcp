"""ParseAddr stdio MCP server (distributed via the `parseaddr` PyPI package).

Launched by MCP registries / Smithery as `parseaddr-mcp`. Exposes `parse_address`
and `expand_address` tools that call the hosted ParseAddr API. Tags every call
`X-Parseaddr-Client: mcp/<ver>` — the server-side attribution for the agent channel.

Requires the `mcp` extra:  pip install "parseaddr[mcp]"
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import __version__
from . import _post as _client_post

mcp = FastMCP("parseaddr")


def _post(path: str, address: str) -> dict:
    # Same request, key lookup and errors as the library; tagged mcp/<ver> instead of pkg-pypi/<ver>.
    return _client_post(path, {"address": address}, None, None, 15, client=f"mcp/{__version__}")


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
