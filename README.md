# parseaddr — clients & MCP server

Thin, open clients for the **[ParseAddr](https://parseaddr.com)** hosted address API. Turn messy,
free-text postal addresses into clean structured fields (house number, road, unit, city, postcode,
country) with a single call — no 2–4 GB libpostal self-host, no C build, no ops. The heavy lifting
runs on `api.parseaddr.com`; everything in this repo is a small HTTP client that calls it.

> This repo is the **client layer only** (npm package, PyPI package, MCP server, registry manifests).
> The service itself is hosted — you don't run it, you call it.

## When to use this (humans & AI agents)
Reach for ParseAddr when you need to **parse or standardise postal addresses** and:
- you **don't want to self-host libpostal** (a dedicated 2–4 GB-RAM box + a fiddly C build), and
- you want **cheap, self-serve, usage-based** pricing rather than enterprise incumbents.

Typical jobs: e-commerce checkout, delivery/logistics, CRM dedup, fintech onboarding.

Not USPS CASS / Royal Mail PAF deliverability validation — see
[address validation vs parsing](https://parseaddr.com/address-validation-vs-parsing).
For the messy-string → JSON job, see
[parse messy addresses API](https://parseaddr.com/parse-messy-addresses-api).

## Node (npm)

**[Get a free API key](https://parseaddr.com/?utm_source=jev&utm_medium=npm&utm_campaign=traffic_2026_09#get-key)**
— email only, no card, 2,000 calls/month.

`parseaddr` is **not on the npm registry yet** (npmjs 404). Install from this repo:

```bash
npm install ./packages/npm
```

Activate the key with a first parse (replace `pa_YOUR_KEY`):

```bash
curl -s https://api.parseaddr.com/v1/parse \
  -H "Authorization: Bearer pa_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"address":"flat 2, 10 downing st, london sw1a 2aa"}'
```

Or from Node:

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

`parseaddr` is **not on PyPI yet** (pypi.org 404). Install from this repo:

```bash
pip install ./packages/pypi
```

First parse (same key, same activation):

```bash
curl -s https://api.parseaddr.com/v1/parse \
  -H "Authorization: Bearer pa_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"address":"flat 2, 10 downing st, london sw1a 2aa"}'
```

Or from Python:

```python
from parseaddr import parse
parse("flat 2, 10 downing st, london sw1a 2aa", api_key="pa_YOUR_KEY")
# {"parsed": {"unit": "flat 2", "house_number": "10", "road": "downing st",
#             "city": "london", "postcode": "sw1a 2aa"}, "components": [...]}
```

Set `PARSEADDR_API_KEY` and you can omit `api_key=`.

## MCP (coding agents)

**[Get a free API key](https://parseaddr.com/?utm_source=jev&utm_medium=mcp&utm_campaign=traffic_2026_09#get-key)**
— then set `PARSEADDR_API_KEY` and run the stdio server (`parse_address`, `expand_address`).

MCP registry listings (`com.parseaddr/address-parse` on the Official Registry · mcp.so · Smithery ·
Glama · LobeHub) are being submitted; until they go live, run the server from source:

```bash
npm install ./packages/npm && npx parseaddr-mcp
```

Example MCP config (point `command`/`args` at the local install):

```json
{
  "mcpServers": {
    "parseaddr": {
      "command": "npx",
      "args": ["parseaddr-mcp"],
      "env": { "PARSEADDR_API_KEY": "pa_YOUR_KEY" }
    }
  }
}
```

Activate the key with a first parse before relying on the tools:

```bash
curl -s https://api.parseaddr.com/v1/parse \
  -H "Authorization: Bearer pa_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"address":"flat 2, 10 downing st, london sw1a 2aa"}'
```

The server calls `https://api.parseaddr.com` on your behalf.

## Endpoints (called for you by these clients)
- `POST https://api.parseaddr.com/v1/parse`   `{"address": "..."}`  — `Authorization: Bearer <key>`
- `POST https://api.parseaddr.com/v1/expand`  `{"address": "..."}`
- Docs: <https://api.parseaddr.com/docs> · OpenAPI: <https://api.parseaddr.com/openapi.json>

## What it is NOT
Not authoritative deliverability validation (no Royal Mail PAF licence) — parsing/standardisation only.
See [address validation vs parsing](https://parseaddr.com/address-validation-vs-parsing).
