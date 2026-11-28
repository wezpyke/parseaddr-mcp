import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

import parseaddr
from parseaddr import ParseAddrError, expand, parse

REPLIES = {
    "/v1/parse": (200, {"input": "10 downing st", "components": [{"label": "road", "value": "downing st"}], "parsed": {"road": "downing st"}}),
    "/v1/expand": (200, {"input": "100 main st", "variants": ["100 main street"]}),
}
LAST = {}


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        LAST.clear()
        LAST.update(path=self.path, headers=dict(self.headers), body=body)
        auth = self.headers.get("Authorization")
        if auth == "Bearer bad":
            status, payload = 401, {"detail": "Invalid API key."}
        elif auth == "Bearer text":
            status, payload = 502, "Bad Gateway"
        elif auth == "Bearer capped":
            status, payload = 429, {"detail": "Monthly cap reached."}
        else:
            status, payload = REPLIES.get(self.path, (404, {"detail": "not found"}))
        data = payload.encode() if isinstance(payload, str) else json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


@pytest.fixture(scope="module")
def base():
    srv = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    monkeypatch.delenv("PARSEADDR_API_KEY", raising=False)
    monkeypatch.delenv("PARSEADDR_API_BASE", raising=False)
    LAST.clear()


def test_parse_sends_key_header_and_body(base):
    out = parse("10 downing st", api_key="pa_test", base_url=base)
    assert out["parsed"] == {"road": "downing st"}
    assert LAST["path"] == "/v1/parse"
    assert LAST["headers"]["Authorization"] == "Bearer pa_test"
    assert LAST["headers"]["X-Parseaddr-Client"] == f"pkg-pypi/{parseaddr.__version__}"
    assert LAST["body"] == {"address": "10 downing st"}


def test_language_hint_only_when_given(base):
    parse("10 downing st", api_key="k", base_url=base, language="en")
    assert LAST["body"] == {"address": "10 downing st", "language": "en"}


def test_expand_returns_variants(base):
    assert expand("100 main st", api_key="k", base_url=base + "/")["variants"] == ["100 main street"]
    assert LAST["path"] == "/v1/expand"


def test_key_and_base_from_env(base, monkeypatch):
    monkeypatch.setenv("PARSEADDR_API_KEY", "pa_env")
    monkeypatch.setenv("PARSEADDR_API_BASE", base)
    parse("10 downing st")
    assert LAST["headers"]["Authorization"] == "Bearer pa_env"


def test_missing_key_fails_before_request(base):
    with pytest.raises(ValueError, match="No API key"):
        parse("10 downing st", base_url=base)
    assert LAST == {}


def test_empty_address_fails_before_request(base):
    with pytest.raises(ValueError, match="non-empty"):
        parse("   ", api_key="k", base_url=base)
    assert LAST == {}


@pytest.mark.parametrize("key,status,detail", [("bad", 401, "Invalid API key."), ("capped", 429, "Monthly cap reached."), ("text", 502, "Bad Gateway")])
def test_http_errors_raise_parseaddr_error(base, key, status, detail):
    with pytest.raises(ParseAddrError) as e:
        parse("x", api_key=key, base_url=base)
    assert e.value.status == status
    assert e.value.detail == detail
