# parseaddr (Python)

Turn a messy address string into structured fields with one call to the hosted
[ParseAddr](https://parseaddr.com) API. It runs libpostal for you, so you skip the 2-4 GB
model download and the C build that `pip install postal` needs.

**[Get a free API key](https://parseaddr.com/?utm_source=jev&utm_medium=pypi&utm_campaign=traffic_2026_09#get-key)**:
email only, no card, 2,000 calls a month.

```bash
pip install parseaddr
```

```python
from parseaddr import parse, expand

r = parse("flat 2, 10 downing st, london sw1a 2aa", api_key="pa_YOUR_KEY")
r["parsed"]
# {'unit': 'flat 2', 'house_number': '10', 'road': 'downing st', 'city': 'london', 'postcode': 'sw1a 2aa'}

expand("100 main st", api_key="pa_YOUR_KEY")["variants"]
# ['100 main saint', '100 main street']
```

Set `PARSEADDR_API_KEY` and you can leave out `api_key`. Python 3.9 or later.

## Options

| Argument | Default | |
|---|---|---|
| `api_key` | `PARSEADDR_API_KEY` | Your key |
| `language=` | none | `parse` only. ISO hint such as `"en"` |
| `base_url=` | `PARSEADDR_API_BASE`, then `https://api.parseaddr.com` | |
| `timeout=` | `15` seconds | |

## Errors

A non-2xx answer raises `ParseAddrError` with `status` and `detail`:

```python
from parseaddr import parse, ParseAddrError

try:
    parse("10 downing st", api_key="pa_wrong")
except ParseAddrError as e:
    print(e.status, e.detail)  # 401 Invalid API key.
```

401 is a missing or unknown key, 403 a disabled key, 429 the monthly cap or a rate limit (then `detail` may be an object).
A missing key or an empty address raises `ValueError` before any request is sent.

## MCP server for coding agents

```bash
pip install "parseaddr[mcp]"
PARSEADDR_API_KEY=pa_YOUR_KEY parseaddr-mcp
```

The `mcp` extra needs Python 3.10 or later. That starts a stdio MCP server with tools `parse_address` and `expand_address`.
Or skip the install and use the hosted server:
`claude mcp add --transport http parseaddr https://api.parseaddr.com/mcp --header "Authorization: Bearer pa_YOUR_KEY"`.

## What it does not do

It parses and standardises. It does not check that an address can receive mail (no USPS CASS
or Royal Mail PAF). See [address validation vs parsing](https://parseaddr.com/address-validation-vs-parsing).

MIT licence. Source: [wezpyke/parseaddr-mcp](https://github.com/wezpyke/parseaddr-mcp).
