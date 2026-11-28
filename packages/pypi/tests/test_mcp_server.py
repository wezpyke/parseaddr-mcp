import asyncio

import pytest

pytest.importorskip("mcp")

from parseaddr import server  # noqa: E402


def test_server_lists_both_tools():
    names = sorted(t.name for t in asyncio.run(server.mcp.list_tools()))
    assert names == ["expand_address", "parse_address"]
