import asyncio

import pytest

pytest.importorskip("mcp")

from parseaddr import server  # noqa: E402
from test_client import LAST, base  # noqa: E402,F401  (reuses the local fake API)


def test_server_lists_both_tools():
    names = sorted(t.name for t in asyncio.run(server.mcp.list_tools()))
    assert names == ["expand_address", "parse_address"]


def test_tool_call_uses_client_with_mcp_tag(base, monkeypatch):  # noqa: F811
    monkeypatch.setenv("PARSEADDR_API_KEY", "pa_agent")
    monkeypatch.setenv("PARSEADDR_API_BASE", base)
    assert server.parse_address("10 downing st")["parsed"] == {"road": "downing st"}
    assert LAST["headers"]["Authorization"] == "Bearer pa_agent"
    assert LAST["headers"]["X-Parseaddr-Client"].startswith("mcp/")
