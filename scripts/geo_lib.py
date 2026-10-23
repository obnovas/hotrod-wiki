"""Story map data: coordinates (docs/data/geo.yml) joined to article front matter.

Used by hooks/map_hook.py (writes assets/data/hr-map.json at build time), scripts/check_articles.py (the build
gate: a story naming a city or strip with no entry in geo.yml fails the build) and scripts/geocode_places.py.
See docs/reference/article-schema.md#story-map-coordinates."""
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
GEO_FILE = DOCS / "data" / "geo.yml"

STATE_ABBR = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO",
    "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC", "Washington, D.C.": "DC", "Florida": "FL",
    "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI",
    "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
    "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI",
    "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
    "D.C.": "DC", "Puerto Rico": "PR",
}
PRECISIONS = ("town", "county", "site")


def load_geo():
    g = yaml.safe_load(GEO_FILE.read_text()) if GEO_FILE.exists() else {}
    g = g or {}
    for k in ("places", "strips", "not_mapped"):
        g[k] = g.get(k) or {}
    return g


def save_geo(g):
    """Rewrite geo.yml keeping the header comment block."""
    head = []
    if GEO_FILE.exists():
        for line in GEO_FILE.read_text().splitlines():
            if line.startswith("#") or not line.strip():
                head.append(line)
            else:
                break
    out = "\n".join(head).rstrip() + "\n\n" if head else ""
    for sec in ("places", "strips", "not_mapped"):
        out += f"{sec}:\n"
        for k in sorted(g.get(sec) or {}, key=str.lower):
            v = g[sec][k]
            line = yaml.safe_dump({k: v}, default_flow_style=isinstance(v, dict), allow_unicode=True,
                                  sort_keys=False, width=1000).strip()
            if isinstance(v, dict):
                line = line[1:-1]  # drop the outer braces of the one-item flow mapping
            out += "  " + line + "\n"
        out += "\n"
    GEO_FILE.write_text(out.rstrip() + "\n")


def story_meta():
    """rel -> front matter for every story page that is not a hub."""
    import articles_lib
    out = {}
    for rel in articles_lib.articles():
        meta, _ = articles_lib.split_front((DOCS / rel).read_text())
        if not meta.get("hub"):
            out[rel] = meta
    return out


def check(metas, geo=None):
    """Errors and warnings for the build gate. `metas` is rel -> front matter (hubs are skipped here)."""
    g = geo or load_geo()
    errors, warns = [], []
    places, strips, nm = g["places"], g["strips"], g["not_mapped"]
    for k, v in places.items():
        if not isinstance(v, dict) or not all(isinstance(v.get(x), (int, float)) for x in ("lat", "lon")):
            errors.append(f"docs/data/geo.yml: places '{k}' needs numeric lat and lon"); continue
        if not (17 <= v["lat"] <= 72 and -180 <= v["lon"] <= -64):
            errors.append(f"docs/data/geo.yml: places '{k}' is outside the United States ({v['lat']}, {v['lon']})")
        if v.get("precision") not in PRECISIONS:
            errors.append(f"docs/data/geo.yml: places '{k}' precision must be one of {PRECISIONS}")
        if not str(v.get("source") or "").strip():
            errors.append(f"docs/data/geo.yml: places '{k}' needs a source note")
    for k, v in strips.items():
        v = v or {}
        if v.get("place") not in places:
            errors.append(f"docs/data/geo.yml: strip '{k}' points at '{v.get('place')}', which has no entry under places")
    for k, v in nm.items():
        if not str(v or "").strip():
            errors.append(f"docs/data/geo.yml: not_mapped '{k}' needs a reason")
    used = set()
    for rel, meta in metas.items():
        if meta.get("hub"):
            continue
        for c in meta.get("cities") or []:
            used.add(c)
            if c in nm:
                continue
            if c not in places:
                errors.append(f"{rel}: city '{c}' has no coordinates in docs/data/geo.yml (add it under places, "
                              f"from the Census Gazetteer or GNIS, or under not_mapped with a reason)")
        for s in meta.get("strips") or []:
            used.add(s)
            if s not in strips and s not in nm:
                errors.append(f"{rel}: strip '{s}' has no entry in docs/data/geo.yml strips (map it to its town, "
                              f"or list it under not_mapped with a reason)")
    for k in nm:
        if k in places or k in strips:
            errors.append(f"docs/data/geo.yml: '{k}' is both mapped and under not_mapped")
    return errors, warns


def era_of(meta):
    eras = [str(e) for e in (meta.get("eras") or [])]
    return str(meta.get("era") or (eras[0] if eras else ""))


def build(metas, urls, geo=None):
    """The map JSON: one pin per place, each listing the stories set there."""
    g = geo or load_geo()
    places, strips = g["places"], g["strips"]
    pins = {}
    stories = []
    for rel, meta in sorted(metas.items()):
        if meta.get("hub") or rel not in urls:
            continue
        here = {}  # place -> [strip names]
        for c in meta.get("cities") or []:
            if c in places:
                here.setdefault(c, [])
        for s in meta.get("strips") or []:
            p = (strips.get(s) or {}).get("place")
            # a strip pins its story only where the story itself is set (a passing mention elsewhere does not)
            if p in here:
                here[p].append(s)
        if not here and not meta.get("states"):
            continue
        idx = len(stories)
        stories.append({
            "t": re.sub(r"\s+", " ", str(meta.get("title") or "")).strip(),
            "u": urls[rel],
            "s": str(meta.get("summary") or "").strip(),
            "e": era_of(meta),
            "es": [str(e) for e in meta.get("eras") or []],
            "r": meta.get("region") or "",
            "d": meta.get("department") or rel.split("/")[0],
        })
        for p, ss in here.items():
            pin = pins.setdefault(p, {"n": p, "lat": places[p]["lat"], "lon": places[p]["lon"],
                                      "st": STATE_ABBR.get(p.rpartition(", ")[2], ""),
                                      "pr": places[p].get("precision", "town"), "x": [], "strips": []})
            pin["x"].append(idx)
            for s in ss:
                if s not in pin["strips"]:
                    pin["strips"].append(s)
    return {"stories": stories, "pins": sorted(pins.values(), key=lambda p: p["n"])}


# --- Albers USA (the composite projection of d3-geo's geoAlbersUsa, written out so the build needs no JS) -----
# Scale 1300 and translate (487.5, 305) match the vendored us-atlas states-albers-10m.json (a 975 x 610 frame).
import math  # noqa: E402

_K, _TX, _TY = 1300.0, 487.5, 305.0


def _conic(par0, par1, rot, center, k, tx, ty):
    y0, y1 = math.radians(par0), math.radians(par1)
    sy0 = math.sin(y0)
    n = (sy0 + math.sin(y1)) / 2
    c = 1 + sy0 * (2 * n - sy0)
    r0 = math.sqrt(c) / n

    def raw(lam, phi):
        r = math.sqrt(c - 2 * n * math.sin(phi)) / n
        return r * math.sin(lam * n), r0 - r * math.cos(lam * n)

    cx, cy = raw(math.radians(center[0]), math.radians(center[1]))

    def proj(lon, lat):
        lam = math.radians(((lon + rot + 180) % 360) - 180)
        px, py = raw(lam, math.radians(lat))
        return tx + k * (px - cx), ty - k * (py - cy)
    return proj


_L48 = _conic(29.5, 45.5, 96, (-0.6, 38.7), _K, _TX, _TY)
_AK = _conic(55, 65, 154, (-2, 58.5), _K * 0.35, _TX - 0.307 * _K, _TY + 0.201 * _K)
_HI = _conic(8, 18, 157, (-3, 19.9), _K, _TX - 0.205 * _K, _TY + 0.212 * _K)


def project(lon, lat):
    """(lon, lat) -> (x, y) in the 975 x 610 frame of states-albers-10m.json."""
    if lat > 50 and lon < -129:
        return _AK(lon, lat)
    if lat < 23 and lon < -150:
        return _HI(lon, lat)
    return _L48(lon, lat)


# --- state outlines from the vendored us-atlas TopoJSON (vendor/us-atlas/states-albers-10m.json) ---------------
ATLAS = ROOT / "vendor" / "us-atlas" / "states-albers-10m.json"
FIPS = {"01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE", "11": "DC",
        "12": "FL", "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY",
        "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN", "28": "MS", "29": "MO", "30": "MT",
        "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND", "39": "OH",
        "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT",
        "50": "VT", "51": "VA", "53": "WA", "54": "WV", "55": "WI", "56": "WY", "72": "PR"}


def _simplify(pts, tol):
    """Radial-distance thinning: drop points within `tol` of the last kept point (arc ends always kept)."""
    if tol <= 0 or len(pts) < 3:
        return pts
    out = [pts[0]]
    for p in pts[1:-1]:
        if abs(p[0] - out[-1][0]) + abs(p[1] - out[-1][1]) >= tol:
            out.append(p)
    out.append(pts[-1])
    return out


def _d(pts, closed, nd):
    """Compact SVG path data: an absolute move, then relative line steps rounded to `nd` decimals."""
    q = 10 ** nd
    ip = [(round(x * q), round(y * q)) for x, y in pts]
    steps, last = [], ip[0]
    for p in ip[1:]:
        dx, dy = p[0] - last[0], p[1] - last[1]
        if dx or dy:
            steps.append((dx, dy))
            last = p

    def f(v):
        t = f"{v / q:.{nd}f}".rstrip("0").rstrip(".") if nd else str(v)
        return t.replace("0.", ".", 1) if t.startswith("0.") else t.replace("-0.", "-.", 1)
    if (closed and len(steps) < 2) or not steps:
        return ""
    s = "M" + f(ip[0][0]) + "," + f(ip[0][1]) + "l"
    for dx, dy in steps:
        b = f(dy)
        s += f(dx) + ("" if b.startswith("-") else ",") + b
        s += "" if False else " "
    s = s.rstrip() + ("z" if closed else "")
    return s.replace(" -", "-")


def state_paths(tol=0.35, nd=1):
    """[(abbr, name, svg path d)] for every state in the atlas's 975 x 610 frame, plus (interior borders, coastline).

    `tol` thins each shared arc the same way, so state fills and border lines still meet exactly."""
    import json
    t = json.loads(ATLAS.read_text())
    (sx, sy), (tx, ty) = t["transform"]["scale"], t["transform"]["translate"]
    arcs = []
    for a in t["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in a:
            x += dx
            y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(_simplify(pts, tol))

    def ring(ix):
        out = []
        for i in ix:
            pts = arcs[i] if i >= 0 else arcs[~i][::-1]
            out.extend(pts if not out else pts[1:])
        return out

    out = []
    use = {}
    for g in t["objects"]["states"]["geometries"]:
        polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
        d = "".join(_d(ring(r), True, nd) for p in polys for r in p)
        for p in polys:
            for r in p:
                for i in r:
                    use.setdefault(i if i >= 0 else ~i, set()).add(g["id"])
        out.append((FIPS.get(g["id"], g["id"]), g["properties"]["name"], d))

    def mesh(sel):
        return "".join(_d(arcs[i], False, nd) for i in sel)
    inner = mesh(i for i, ids in sorted(use.items()) if len(ids) > 1)
    coast = mesh(i for i, ids in sorted(use.items()) if len(ids) == 1)
    return sorted(out), (inner, coast)
