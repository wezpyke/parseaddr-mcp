"""parseaddr — tiny client for the hosted ParseAddr (libpostal) API.

    from parseaddr import parse, expand
    parse("flat 2, 10 downing st, london sw1a 2aa")   # -> {"parsed": {...}, "components": [...]}

Set your key via PARSEADDR_API_KEY or pass api_key=. Free tier at https://parseaddr.com.

Scaffold: correct shape, not yet published. `parse`/`expand` calls are tagged
`X-Parseaddr-Client: pkg-pypi/<ver>` so the package channel is attributable (the MCP
server tags `mcp/<ver>`). Do NOT drop the header — it's the Phase-3 hands-off-proof metric.
"""
from __future__ import annotations

import os
from typing import Optional

import httpx

__version__ = "0.1.0"
API_BASE = os.getenv("PARSEADDR_API_BASE", "https://api.parseaddr.com")
_CLIENT = f"pkg-pypi/{__version__}"


def _key(api_key: Optional[str]) -> str:
    k = api_key or os.getenv("PARSEADDR_API_KEY", "")
    if not k:
        raise ValueError("No API key. Set PARSEADDR_API_KEY or pass api_key=. Free key: https://parseaddr.com")
    return k


def _post(path: str, address: str, api_key: Optional[str]) -> dict:
    r = httpx.post(
        f"{API_BASE}{path}",
        json={"address": address},
        headers={"Authorization": f"Bearer {_key(api_key)}", "X-Parseaddr-Client": _CLIENT},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


def parse(address: str, api_key: Optional[str] = None) -> dict:
    """Parse a free-text address into structured components."""
    return _post("/v1/parse", address, api_key)


def expand(address: str, api_key: Optional[str] = None) -> dict:
    """Expand/normalize an address into variants for dedup and matching."""
    return _post("/v1/expand", address, api_key)
