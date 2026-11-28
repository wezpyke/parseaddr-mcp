"""Run the same 300 inputs from results.json through two open-source parsers and score all three
with one rule. usaddress (Python) and parse-address (npm) are US-focused; this measures how they do
on the UK and international cases parseaddr is sold for, and on the 24 US cases they are built for.

    pip install usaddress && npm install parse-address   # in <dir>
    python benchmarks/compare_oss.py benchmarks/results.json <dir> > benchmarks/oss-results.json

Scoring is run.py's norm() plus one extra leniency, applied to every parser: street-type words
are reduced to one spelling (street/st, avenue/ave, road/rd, ...), because parse-address
abbreviates them and the labels mix both spellings.
"""
import json, subprocess, sys
from importlib.metadata import version
from pathlib import Path

import usaddress

TYPES = {"street": "st", "avenue": "ave", "road": "rd", "drive": "dr", "boulevard": "blvd", "lane": "ln",
         "place": "pl", "crescent": "cres", "parade": "pde", "promenade": "prom", "north": "n", "south": "s",
         "east": "e", "west": "w", "northwest": "nw"}


def norm(field, value):
    v = " ".join(str(value).casefold().replace(",", " ").replace(".", " ").split())
    if field == "postcode":
        return v.replace(" ", "")
    if field in ("road", "unit"):
        return " ".join(TYPES.get(w, w) for w in v.split())
    return v


ROAD = ("StreetNamePreModifier", "StreetNamePreDirectional", "StreetNamePreType", "StreetName",
        "StreetNamePostType", "StreetNamePostDirectional")
UNIT = ("OccupancyType", "OccupancyIdentifier", "SubaddressType", "SubaddressIdentifier")
SINGLE = {"house_number": ("AddressNumber",), "city": ("PlaceName",), "state": ("StateName",),
          "postcode": ("ZipCode",), "country": ("CountryName",)}


def from_usaddress(text):
    tokens = usaddress.parse(text)
    pick = lambda labels: " ".join(t for t, l in tokens if l in labels)
    out = {f: pick(ls) for f, ls in SINGLE.items()}
    out["road"], out["unit"] = pick(ROAD), pick(UNIT)
    return {k: v for k, v in out.items() if v}


def from_parse_address(d):
    j = lambda *ks: " ".join(str(d[k]) for k in ks if d.get(k))
    out = {"house_number": j("number"), "road": j("prefix", "street", "type", "suffix"),
           "unit": j("sec_unit_type", "sec_unit_num"), "city": j("city"), "state": j("state"), "postcode": j("zip")}
    return {k: v for k, v in out.items() if v}


def score(rows):
    fields = sorted({f for r in rows for f in r["expected"]})
    per = {f: f"{sum(f in r['correct'] for r in rows if f in r['expected'])}/{sum(f in r['expected'] for r in rows)}"
           for f in fields}
    return {"cases": len(rows), "all_fields_correct": sum(len(r["correct"]) == len(r["expected"]) for r in rows),
            "per_field": per}


def main():
    src = json.load(open(sys.argv[1], encoding="utf-8"))
    cases = src["cases"]
    pa = json.loads(subprocess.run(["node", str(Path(__file__).with_name("parse_address.js")), sys.argv[2]], input=json.dumps([c["input"] for c in cases]),
                                   capture_output=True, text=True, check=True).stdout)
    parsers = {"parseaddr": [c["parsed"] for c in cases],
               "usaddress": [from_usaddress(c["input"]) for c in cases],
               "parse-address": [from_parse_address(d) for d in pa]}
    out = {"source": "results.json run_at " + src["run_at"], "usaddress": version("usaddress"),
           "parse_address": json.load(open(f"{sys.argv[2]}/node_modules/parse-address/package.json"))["version"], "summary": {}, "cases": []}
    us = lambda c: c["input"].lower().endswith("usa") or (c["group"] == "international" and c["expected"].get("state") in {"ny", "dc", "il", "ca", "wa", "tx"})
    for name, outputs in parsers.items():
        rows = []
        for c, parsed in zip(cases, outputs):
            ok = [f for f, v in c["expected"].items() if norm(f, parsed.get(f, "")) == norm(f, v)]
            rows.append({"group": c["group"], "us": us(c), "expected": c["expected"], "correct": ok})
            if name != "parseaddr":
                out["cases"].append({"parser": name, "input": c["input"], "parsed": parsed, "correct": ok})
        out["summary"][name] = {"uk": score([r for r in rows if r["group"] == "uk"]),
                                "international_non_us": score([r for r in rows if r["group"] == "international" and not r["us"]]),
                                "us": score([r for r in rows if r["us"]])}
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
