"""Accuracy and latency check against the live API.

    PARSEADDR_API_KEY=pa_... python benchmarks/run.py > benchmarks/results.json

Each base address in addresses.json becomes 4 inputs, so 50 UK addresses give 200 cases and
25 international ones give 100. A field counts as a match when the parsed value equals the
label after case-folding (so ß matches ss), dropping commas and full stops, and (for postcodes) removing spaces.
Latency is the wall-clock time of each POST /v1/parse as seen by this script, over HTTPS.
"""
import json
import os
import statistics
import sys
import time
import urllib.request
from pathlib import Path

API = os.getenv("PARSEADDR_API", "https://api.parseaddr.com/v1/parse")
HERE = Path(__file__).parent


def uk_cases(num, road, city, pc):
    label = {"house_number": num, "road": road, "city": city, "postcode": pc}
    return [
        (f"{num.upper()} {road.title()}, {city.title()} {pc}", label),
        (f"{num} {road} {city} {pc.lower()}", label),
        (f"{num.upper()} {road.upper()}, {city.upper()}, {pc.replace(' ', '')}", label),
        (f"flat 2, {num} {road}, {city} {pc.lower()}", {**label, "unit": "flat 2"}),
    ]


def intl_cases(cc, num, road, city, pc, country, state):
    label = {"house_number": num, "road": road, "city": city, "postcode": pc}
    if state:
        label["state"] = state
    if cc in ("us", "ca", "au", "ie", "nz"):
        tail = f"{state.upper()} {pc.upper()}" if state else pc.upper()
        name = country.upper() if cc == "us" else country.title()
        full = f"{num} {road.title()}, {city.title()}, {tail}, {name}"
        bare = f"{num} {road} {city} {state + ' ' if state else ''}{pc} {country}"
        nocountry = f"{num} {road}, {city}, {tail}"
        fourth = (f"apt 3, {num} {road}, {city}, {tail}", {**label, "unit": "apt 3"})
    else:
        full = f"{road.title()} {num}, {pc.upper()} {city.title()}, {country.title()}"
        bare = f"{road} {num} {pc} {city} {country}"
        nocountry = f"{road} {num}, {pc} {city}"
        fourth = (f"{road.upper()} {num}, {pc.upper()} {city.upper()}, {country.upper()}", {**label, "country": country})
    with_country = {**label, "country": country}
    return [(full, with_country), (bare, with_country), (nocountry, label), fourth]


def norm(field, value):
    v = " ".join(str(value).casefold().replace(",", " ").replace(".", " ").split())
    return v.replace(" ", "") if field == "postcode" else v


def call(key, address):
    req = urllib.request.Request(API, data=json.dumps({"address": address}).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    t = time.perf_counter()
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    return body["parsed"], (time.perf_counter() - t) * 1000


def summarise(rows):
    fields = sorted({f for r in rows for f in r["expected"]})
    per_field = {}
    for f in fields:
        have = [r for r in rows if f in r["expected"]]
        ok = sum(1 for r in have if f in r["correct"])
        per_field[f] = {"cases": len(have), "correct": ok, "rate": round(ok / len(have), 3)}
    all_ok = sum(1 for r in rows if len(r["correct"]) == len(r["expected"]))
    ms = sorted(r["ms"] for r in rows)
    return {
        "cases": len(rows),
        "all_fields_correct": all_ok,
        "all_fields_rate": round(all_ok / len(rows), 3),
        "per_field": per_field,
        "latency_ms": {"median": round(statistics.median(ms)), "p95": round(ms[int(0.95 * (len(ms) - 1))])},
    }


def main():
    key = os.environ["PARSEADDR_API_KEY"]
    data = json.loads((HERE / "addresses.json").read_text(encoding="utf-8"))
    groups = {"uk": [c for a in data["uk"] for c in uk_cases(*a)],
              "international": [c for a in data["international"] for c in intl_cases(*a)]}
    out = {"api": API, "run_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "groups": {}, "cases": []}
    for name, cases in groups.items():
        rows = []
        for address, expected in cases:
            parsed, ms = call(key, address)
            correct = [f for f, v in expected.items() if norm(f, parsed.get(f, "")) == norm(f, v)]
            rows.append({"group": name, "input": address, "expected": expected, "parsed": parsed,
                         "correct": correct, "ms": round(ms, 1)})
        out["groups"][name] = summarise(rows)
        out["cases"].extend(rows)
    out["all"] = summarise(out["cases"])
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
