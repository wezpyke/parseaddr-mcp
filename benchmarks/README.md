# Accuracy and latency check

`run.py` sends 300 addresses to the live API (`POST https://api.parseaddr.com/v1/parse`) and compares each parsed field with a hand-written label.

- 50 UK and 25 international base addresses are in `addresses.json`. Each one is sent in 4 formats (tidy with commas, lower case with no commas, upper case, and with a flat or apartment number, or without the country), so there are 200 UK cases and 100 international ones.
- The addresses are written in real formats. They are not checked for existence, and we wrote the set ourselves, so treat it as a sanity check, not an independent benchmark. Real customer data will be messier.
- A first run found 3 mistakes in our own labels, which we fixed before this run: the apartment cases expected a country the input did not contain, upper-casing turned ß into SS, and the Irish and New Zealand addresses were written in European order. No parser output was changed.
- `results.json` holds every input, label, parsed output and time from the run on 28 November 2026 (10:57 UTC), from a cloud machine over HTTPS.

## Result, 28 November 2026

| Field | UK (200) | International (100) |
|---|---|---|
| house_number | 200/200 | 100/100 |
| road | 200/200 | 100/100 |
| postcode | 200/200 | 100/100 |
| city | 197/200 | 96/100 |
| unit | 50/50 | 12/12 |
| state | none | 40/40 |
| country | none | 63/63 |
| Every labelled field right | 197/200 | 96/100 |

Latency per call, measured by the script: median 161 ms, 95th percentile 198 ms.

The 7 misses: "67 Park Lane, Croydon CR0 1JD" returns `croydon` as `city_district`, not `city`, in all 3 formats. "1 Macquarie St, Sydney, NSW 2000" returns `sydney` as `suburb` in all 4.

## Run it yourself

```
PARSEADDR_API_KEY=pa_... python benchmarks/run.py > results.json
```

It uses 300 calls of your monthly allowance and needs only the Python standard library.

## Two open-source parsers on the same inputs

`compare_oss.py` sends the 300 inputs stored in `results.json` through [usaddress](https://github.com/datamade/usaddress) 0.5.16 (Python) and [parse-address](https://www.npmjs.com/package/parse-address) 1.1.2 (npm), and scores all three parsers with one rule: `run.py`'s matching plus street types counted either way (street or st), because parse-address abbreviates them. Both libraries are built for US addresses, so the US cases are counted on their own. Every output is in `oss-results.json` (run 28 November 2026).

| Every labelled field right | usaddress | parse-address | parseaddr |
|---|---|---|---|
| US (24) | 24/24 | 12/24 (it has no country field) | 24/24 |
| UK (200) | 0/200 | 0/200 | 197/200 |
| Other countries (76) | 3/76 | 0/76 | 72/76 |

On UK input usaddress finds 0 of 200 postcodes: "14 High Street, Oxford OX1 4AG" becomes `OccupancyType: Oxford`, `OccupancyIdentifier: OX1 4AG`. parse-address returns `{ number: '14', street: 'High', type: 'St' }` and drops the rest.

```
pip install usaddress
npm install --prefix /tmp/pa parse-address
python benchmarks/compare_oss.py benchmarks/results.json /tmp/pa > benchmarks/oss-results.json
```
