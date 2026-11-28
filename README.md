# parseaddr: hosted MCP server and API clients

ParseAddr turns messy postal addresses into structured fields: house number, road, unit, city,
postcode and country. It runs libpostal for you on `api.parseaddr.com`, so you skip the 2 to 4 GB
self-host and the C build.

The MCP server is hosted, so there is nothing to install. The npm and PyPI packages are not
published yet (`npm install parseaddr` and `pip install parseaddr` return 404). Install them from
GitHub. Both read `PARSEADDR_API_KEY`.

- Python: `pip install "git+https://github.com/wezpyke/parseaddr-mcp.git#subdirectory=packages/pypi"`
- Node: `git clone https://github.com/wezpyke/parseaddr-mcp.git && npm install ./parseaddr-mcp/packages/npm`

## MCP server: hosted, Streamable HTTP

- Endpoint: `https://api.parseaddr.com/mcp` (Streamable HTTP). Nothing to install or run.
- Auth: send your key as `Authorization: Bearer $PARSEADDR_API_KEY`.
- Tools: `parse_address` and `expand_address`.
- Server card: <https://api.parseaddr.com/mcp/server-card>. Listed on the
  [Official MCP Registry](https://registry.modelcontextprotocol.io/v0/servers?search=parseaddr) as
  `com.parseaddr/address-parse`.
- Free tier: 2,000 calls a month, no card.
  **[Get a free key](https://parseaddr.com/?utm_source=jev&utm_medium=mcp&utm_campaign=traffic_2026_09#get-key)**.
- Paid plans start at £19 a month for 25,000 calls. See <https://parseaddr.com/pricing>.

Claude Code:

```bash
export PARSEADDR_API_KEY=pa_YOUR_KEY
claude mcp add --transport http parseaddr https://api.parseaddr.com/mcp \
  --header "Authorization: Bearer $PARSEADDR_API_KEY"
```

Cursor and other clients that take a JSON config for an HTTP server. Replace `pa_YOUR_KEY` with
your key:

```json
{
  "mcpServers": {
    "parseaddr": {
      "url": "https://api.parseaddr.com/mcp",
      "headers": { "Authorization": "Bearer pa_YOUR_KEY" }
    }
  }
}
```

Activate the key with a first parse:

```bash
curl -s https://api.parseaddr.com/v1/parse \
  -H "Authorization: Bearer $PARSEADDR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"address":"flat 2, 10 downing st, london sw1a 2aa"}'
```

## When to use this (humans and AI agents)
Reach for ParseAddr when you need to **parse or standardise postal addresses** and:
- you **don't want to self-host libpostal** (a dedicated 2 to 4 GB RAM box and a C build), and
- you want **self-serve, usage-based** pricing.

Typical jobs: e-commerce checkout, delivery and logistics, CRM dedup, fintech onboarding.

Not USPS CASS / Royal Mail PAF deliverability validation. See
[address validation vs parsing](https://parseaddr.com/address-validation-vs-parsing).
For the messy-string to JSON job, see
[parse messy addresses API](https://parseaddr.com/parse-messy-addresses-api).

## Node (npm)

**[Get a free API key](https://parseaddr.com/?utm_source=jev&utm_medium=npm&utm_campaign=traffic_2026_09#get-key)**
— email only, no card, 2,000 calls/month.

Install from GitHub (see the top of this page), then:

```js
import { parse } from "parseaddr";
await parse("flat 2, 10 downing st, london sw1a 2aa", { apiKey: "pa_YOUR_KEY" });
// { parsed: { unit: "flat 2", house_number: "10", road: "downing st",
//             city: "london", postcode: "sw1a 2aa" }, components: [...] }
```

Set `PARSEADDR_API_KEY` and you can omit `{ apiKey }`.

## Python (pip)

**[Get a free API key](https://parseaddr.com/?utm_source=jev&utm_medium=pypi&utm_campaign=traffic_2026_09#get-key)**
— email only, no card, 2,000 calls/month.

Install from GitHub (see the top of this page), then:

```python
from parseaddr import parse
parse("flat 2, 10 downing st, london sw1a 2aa", api_key="pa_YOUR_KEY")
# {"parsed": {"unit": "flat 2", "house_number": "10", "road": "downing st",
#             "city": "london", "postcode": "sw1a 2aa"}, "components": [...]}
```

Set `PARSEADDR_API_KEY` and you can omit `api_key=`.

## Local stdio MCP server (optional)

The hosted server above is the main way in. If your client only speaks stdio, the npm package
ships one. It calls `https://api.parseaddr.com` with your key:

```bash
git clone https://github.com/wezpyke/parseaddr-mcp.git
npm install ./parseaddr-mcp/packages/npm
PARSEADDR_API_KEY=pa_YOUR_KEY npx parseaddr-mcp
```

## Endpoints (called for you by these clients)
- `POST https://api.parseaddr.com/v1/parse`   `{"address": "..."}`  — `Authorization: Bearer <key>`
- `POST https://api.parseaddr.com/v1/expand`  `{"address": "..."}`
- Docs: <https://api.parseaddr.com/docs> · OpenAPI: <https://api.parseaddr.com/openapi.json>

## What it is NOT
Not authoritative deliverability validation (no Royal Mail PAF licence) — parsing/standardisation only.
See [address validation vs parsing](https://parseaddr.com/address-validation-vs-parsing).

## Publishing (maintainers)
Both packages publish with one command. It runs both test suites, refuses a version that is
already live, then uploads:

```bash
NPM_TOKEN=npm_... PYPI_TOKEN=pypi-... scripts/publish.sh   # DRY_RUN=1 to stop before upload
```

Tests on their own: `cd packages/npm && npm install && npm test` (9 tests, including two MCP
stdio checks) and `cd packages/pypi && pip install -e ".[mcp,test]" && pytest` (12 tests).
