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

## Install

```bash
pip install parseaddr          # Python:  from parseaddr import parse
npm  install parseaddr         # Node:    import { parse } from "parseaddr"
```

> PyPI and npm publish are pending — until the packages land on the registries,
> install from this repo: `pip install ./packages/pypi` · `npm install ./packages/npm`
> (or add them to your toolchain from source). The API itself is live today.

Get a free API key at <https://parseaddr.com>, then:

```python
from parseaddr import parse
parse("flat 2, 10 downing st, london sw1a 2aa", api_key="pa_...")
# -> {"unit": "flat 2", "house_number": "10", "road": "downing st", "city": "london", "postcode": "sw1a 2aa"}
```

## MCP (coding agents)
stdio server **`parseaddr-mcp`** — tools `parse_address`, `expand_address`. MCP registry
listings (`com.parseaddr/address-parse` on the Official Registry · mcp.so · Smithery ·
Glama · LobeHub) are being submitted; until they go live, run the server from source:

```bash
npm install ./packages/npm && npx parseaddr-mcp   # or add ./packages/npm to your MCP config
```

Set `PARSEADDR_API_KEY` in the environment; the server calls `https://api.parseaddr.com` on your behalf.

## Endpoints (called for you by these clients)
- `POST https://api.parseaddr.com/v1/parse`   `{"address": "..."}`  — `Authorization: Bearer <key>`
- `POST https://api.parseaddr.com/v1/expand`  `{"address": "..."}`
- Docs: <https://api.parseaddr.com/docs> · OpenAPI: <https://api.parseaddr.com/openapi.json>

## What it is NOT
Not authoritative deliverability validation (no Royal Mail PAF licence) — parsing/standardisation only.
