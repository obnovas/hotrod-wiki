"""Fill docs/data/geo.yml with coordinates for front-matter cities that lack them (a dev tool, not run in the build).

Coordinates come only from public-domain U.S. government data:
  1. Census Bureau Gazetteer files (place, county subdivision, county): the internal point (INTPTLAT/INTPTLONG)
     of the matching place. Download from https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html
  2. USGS GNIS Domestic Names (populated places, "Populated Place" class) for neighborhoods and named sites that are
     not Census places (Van Nuys, Hollywood, Bonneville Salt Flats). https://www.usgs.gov/us-board-on-geographic-names

Usage:
  python scripts/geocode_places.py --gaz DIR [--gnis DIR] [--write]
DIR holds the unzipped *_Gaz_place_national.txt, *_Gaz_cousubs_national.txt, *_Gaz_counties_national.txt
(and for --gnis, DomesticNames_XX.txt per state). Existing entries in geo.yml are never changed. Anything it cannot
match exactly is listed and left out: add it by hand only from a source you can cite (`source:` on the entry).
"""
import argparse
import csv
import glob
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import geo_lib  # noqa: E402

SUFFIX = re.compile(r"\s+(city|town|village|CDP|borough|municipality|township|charter township|city and borough|"
                    r"unified government \(balance\)|metro government \(balance\)|metropolitan government \(balance\)|"
                    r"consolidated government \(balance\)|city \(balance\)|urban county|corporation)$", re.I)


def load_gaz(d):
    out = {}  # (USPS, name lower) -> (lat, lon, label, kind)
    seen, amb = {}, set()
    for kind, pat in (("county", "*_Gaz_counties_national.txt"), ("cousub", "*_Gaz_cousubs_national.txt"),
                      ("place", "*_Gaz_place_national.txt")):  # place last so it wins
        for f in glob.glob(str(Path(d) / pat)):
            with open(f, encoding="latin-1") as fh:
                r = csv.reader(fh, delimiter="\t")
                head = [h.strip() for h in next(r)]
                iu, inm, ila, ilo = head.index("USPS"), head.index("NAME"), head.index("INTPTLAT"), head.index("INTPTLONG")
                for row in r:
                    nm = row[inm].strip()
                    base = nm if kind == "county" else SUFFIX.sub("", nm)
                    key = (row[iu], base.lower())
                    rec = (float(row[ila]), float(row[ilo].strip()), nm, kind)
                    if key in seen.get(kind, {}):
                        prev = seen[kind][key]
                        # two places with one name in a state: take the incorporated one when exactly one is
                        # incorporated (Burbank city over Burbank CDP); otherwise never pick
                        pi, ri = not prev[2].endswith(" CDP"), not nm.endswith(" CDP")
                        if kind == "place" and pi != ri:
                            rec = prev if pi else rec
                            amb.discard((kind, key))
                        else:
                            amb.add((kind, key))
                    seen.setdefault(kind, {})[key] = rec
                    out[key] = rec
    for kind, key in amb:
        if out.get(key) and out[key][3] == kind:
            out[key] = None
    return out


def load_gnis(d):
    """Exact name matches; a name with more than one feature of the same class in a state is left out."""
    found = {}
    for f in glob.glob(str(Path(d) / "**" / "DomesticNames_*.txt"), recursive=True):
        with open(f, encoding="utf-8-sig") as fh:
            r = csv.DictReader(fh, delimiter="|")
            for row in r:
                cls = row.get("feature_class")
                if cls not in ("Populated Place", "Flat", "Airport", "Locale", "Civil"):
                    continue
                st = geo_lib.STATE_ABBR.get(row.get("state_name"))
                key = (st, row["feature_name"].lower())
                found.setdefault(key, {}).setdefault(cls, []).append(
                    (float(row["prim_lat_dec"]), float(row["prim_long_dec"]),
                     f"{row['feature_name']} ({cls}, {row['county_name']} County, GNIS {row['feature_id']})", cls))
    out = {}
    for key, by in found.items():
        for cls in ("Populated Place", "Flat", "Airport", "Locale", "Civil"):
            if cls in by:
                out[key] = by[cls][0] if len(by[cls]) == 1 else None
                break
    return out


# Article spelling -> gazetteer name, where the federal record uses another form. Say why.
ALIASES = {
    "Butte, Montana": "Butte-Silver Bow (balance)",       # consolidated city-county since 1977
    "Hallandale, Florida": "Hallandale Beach",            # renamed Hallandale Beach in 1999
    "Brownstown Township, Michigan": "Brownstown",        # county subdivision 'Brownstown charter township'
    "Cahokia, Illinois": "Cahokia Heights",               # merged into Cahokia Heights in 2021 (not Cahokia township,
                                                          # Macoupin County, 60 miles north)
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gaz", required=True)
    ap.add_argument("--gnis")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    gaz = load_gaz(a.gaz)
    gnis = load_gnis(a.gnis) if a.gnis else {}
    geo = geo_lib.load_geo()
    places = geo["places"]
    need = sorted({c for m in geo_lib.story_meta().values() for c in (m.get("cities") or [])} - set(places))
    added, missing = 0, []
    for c in need:
        town, _, state = c.rpartition(", ")
        st = geo_lib.STATE_ABBR.get(state)
        if not st:
            missing.append((c, "not a U.S. state")); continue
        town = ALIASES.get(c, town)
        hit = gaz.get((st, town.lower()))
        if hit is None and (st, town.lower()) in gaz:
            missing.append((c, "ambiguous name in state")); continue
        src = "Census Gazetteer 2024"
        if not hit and gnis:
            hit = gnis.get((st, town.lower()))
            src = "USGS GNIS"
            if hit is None and (st, town.lower()) in gnis:
                missing.append((c, "ambiguous name in GNIS")); continue
        if not hit:
            missing.append((c, "no exact match" if (st, town.lower()) not in gaz else "ambiguous name in state")); continue
        lat, lon, label, kind = hit
        prec = {"county": "county", "Flat": "site", "Airport": "site"}.get(kind, "town")
        places[c] = {"lat": round(lat, 4), "lon": round(lon, 4), "precision": prec, "source": f"{src}: {label}"}
        added += 1
        if kind != "place":
            print(f"  REVIEW    {c}: matched a {kind} ({label}), not a Census place; check it is the right one")
    print(f"{len(need)} cities without coordinates; {added} matched")
    for c, why in missing:
        print(f"  LEFT OUT  {c}  ({why})")
    if a.write:
        geo_lib.save_geo(geo)
        print("wrote", geo_lib.GEO_FILE)


if __name__ == "__main__":
    main()
