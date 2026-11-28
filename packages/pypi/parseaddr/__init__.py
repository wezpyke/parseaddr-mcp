"""parseaddr: small client for the hosted ParseAddr (libpostal) API.

    from parseaddr import parse, expand
    parse("flat 2, 10 downing st, london sw1a 2aa")   # -> {"input": ..., "parsed": {...}, "components": [...]}

Set your key via PARSEADDR_API_KEY or pass api_key=. Free key at https://parseaddr.com.

Calls are tagged `X-Parseaddr-Client: pkg-pypi/<ver>` so the server can count calls from
this package (the MCP server tags `mcp/<ver>`). Keep the header.
"""
from __future__ import annotations

import os
from typing import Any, Optional

import httpx

__version__ = "0.1.0"
__all__ = ["parse", "expand", "ParseAddrError", "__version__"]

DEFAULT_BASE = "https://api.parseaddr.com"
_CLIENT = f"pkg-pypi/{__version__}"


class ParseAddrError(Exception):
    """The API answered with an error status (401 bad key, 429 cap reached, ...)."""

    def __init__(self, status: int, detail: Any):
        super().__init__(f"parseaddr: {status} {detail}")
        self.status = status
        self.detail = detail


def _key(api_key: Optional[str]) -> str:
    k = api_key or os.getenv("PARSEADDR_API_KEY", "")
    if not k:
        raise ValueError("No API key. Set PARSEADDR_API_KEY or pass api_key=. Free key: https://parseaddr.com")
    return k


def _post(path: str, body: dict, api_key: Optional[str], base_url: Optional[str], timeout: float) -> dict:
    address = body.get("address")
    if not isinstance(address, str) or not address.strip():
        raise ValueError("address must be a non-empty string")
    base = (base_url or os.getenv("PARSEADDR_API_BASE") or DEFAULT_BASE).rstrip("/")
    r = httpx.post(
        f"{base}{path}",
        json=body,
        headers={"Authorization": f"Bearer {_key(api_key)}", "X-Parseaddr-Client": _CLIENT},
        timeout=timeout,
    )
    if r.is_error:
        try:
            payload = r.json()
        except ValueError:
            payload = None
        detail = payload.get("detail", r.text) if isinstance(payload, dict) else r.text
        raise ParseAddrError(r.status_code, detail)
    return r.json()


def parse(
    address: str,
    api_key: Optional[str] = None,
    *,
    language: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout: float = 15,
) -> dict:
    """Parse a free-text address into structured components."""
    body = {"address": address, "language": language} if language else {"address": address}
    return _post("/v1/parse", body, api_key, base_url, timeout)


def expand(
    address: str,
    api_key: Optional[str] = None,
    *,
    base_url: Optional[str] = None,
    timeout: float = 15,
) -> dict:
    """Expand/normalize an address into variants for dedup and matching."""
    return _post("/v1/expand", {"address": address}, api_key, base_url, timeout)
