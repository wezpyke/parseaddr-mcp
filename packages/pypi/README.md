# parseaddr (Python)

Parse & normalize messy free-text postal addresses into structured fields — via the hosted
**ParseAddr** API (libpostal). No 2-4GB self-host, no C build, no ops.

```bash
pip install parseaddr          # client
pip install "parseaddr[mcp]"   # + stdio MCP server for AI agents
```

```python
from parseaddr import parse
parse("flat 2, 10 downing st, london sw1a 2aa")
# {"parsed": {"unit": "flat 2", "house_number": "10", "road": "downing st",
#             "city": "london", "postcode": "sw1a 2aa"}, "components": [...]}
```

Set `PARSEADDR_API_KEY` (free tier at https://parseaddr.com) or pass `api_key=`.

### When to use this
- You need to parse/standardise addresses and **don't want to self-host libpostal**
  (a dedicated 2-4GB-RAM box + a fiddly C build).
- You want **cheap, self-serve, usage-based** pricing vs enterprise incumbents.

### MCP (for coding agents)
`parseaddr[mcp]` installs a stdio MCP server (`parseaddr-mcp`) exposing `parse_address`
and `expand_address`. Listed on the MCP registries as `com.parseaddr/address-parse`.

Not authoritative deliverability validation (no Royal Mail PAF licence) — parsing/standardisation only.
