# parseaddr (Python)

Parse & normalize messy free-text postal addresses into structured fields — via the hosted
**ParseAddr** API (libpostal). No 2-4GB self-host, no C build, no ops.

**[Get a free API key](https://parseaddr.com/?utm_source=jev&utm_medium=pypi&utm_campaign=traffic_2026_09#get-key)**
— email only, no card, 2,000 calls/month. Then run a first parse to activate:

```bash
curl -s https://api.parseaddr.com/v1/parse \
  -H "Authorization: Bearer pa_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"address":"flat 2, 10 downing st, london sw1a 2aa"}'
```

`parseaddr` is **not on PyPI yet** (pypi.org 404). From the repo root:

```bash
pip install ./packages/pypi
# later, for the stdio MCP extra:
# pip install "./packages/pypi[mcp]"
```

```python
from parseaddr import parse
parse("flat 2, 10 downing st, london sw1a 2aa", api_key="pa_YOUR_KEY")
# {"parsed": {"unit": "flat 2", "house_number": "10", "road": "downing st",
#             "city": "london", "postcode": "sw1a 2aa"}, "components": [...]}
```

Set `PARSEADDR_API_KEY` and you can omit `api_key=`.

### When to use this
- You need to parse/standardise addresses and **don't want to self-host libpostal**
  (a dedicated 2-4GB-RAM box + a fiddly C build).
- You want **cheap, self-serve, usage-based** pricing vs enterprise incumbents.
- Job write-up: [parse messy addresses API](https://parseaddr.com/parse-messy-addresses-api).

### MCP (for coding agents)
**[Get a free API key](https://parseaddr.com/?utm_source=jev&utm_medium=mcp&utm_campaign=traffic_2026_09#get-key)**
for the agent channel, then set `PARSEADDR_API_KEY`.

`parseaddr[mcp]` installs a stdio MCP server (`parseaddr-mcp`) exposing `parse_address`
and `expand_address`. Registry listings as `com.parseaddr/address-parse` are pending;
until they go live, install the extra from this repo.

Not authoritative deliverability validation (no Royal Mail PAF licence) — parsing/standardisation only.
See [address validation vs parsing](https://parseaddr.com/address-validation-vs-parsing).
