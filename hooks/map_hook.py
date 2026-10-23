"""Story map hook (docs/reference/story-map.md).

  * on_files         : reads every story's front matter and its built URL.
  * on_page_markdown : replaces <!-- hr:story-map --> on the map page with the map itself: era and region chips,
                       an inline SVG of the states (from vendor/us-atlas, projected Albers USA) with one pin per
                       place, a legend, the pin sheet, and a plain list of every place by state (works without JS).
  * on_page_context  : gives every story with a pin a "See on the map" link in its head (`hr.map_url`), and the
                       home page a small map teaser (`hr_map`).
  * on_post_build    : writes site/assets/hr-map.json (stories + pins) for docs/javascripts/storymap.js.
Coordinates live in docs/data/geo.yml; scripts/check_articles.py fails the build when a story names a city or strip
that has no entry there (scripts/geo_lib.py: check).
"""
import html as H
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import geo_lib  # noqa: E402

PAGE = "reference/story-map.md"
MARK = "<!-- hr:story-map -->"
ERA_CHIPS = [("", "All eras", ""), ("1930s", "1930s", "e30"), ("1940s", "1940s", "e30"), ("1950s", "1950s", "e50"),
             ("1960s", "1960s", "e60"), ("1970s", "1970s", "e70"), ("1980s", "1980s+", "e80")]
ERA_KEY = {"1950s": "e50", "1960s": "e60", "1970s": "e70"}
REGION_CHIPS = ["West", "Southwest", "Northwest", "Midwest", "South", "Northeast", "National"]
STATE_NAME = {v: k for k, v in geo_lib.STATE_ABBR.items() if len(k) > 4 and k != "Washington, D.C."}
_S = {}


def era_skin(decade):
    if not decade:
        return ""
    y = int(decade[:4]) if decade[:4].isdigit() else 0
    if y and y < 1950:
        return "e30"
    if y >= 1980:
        return "e80"
    return ERA_KEY.get(decade, "")


def era_bucket(decade):
    """The chip a decade belongs to: 1930s and earlier -> 1930s; 1980s and later -> 1980s."""
    y = int(decade[:4]) if decade[:4].isdigit() else 0
    if not y:
        return ""
    return "1930s" if y < 1940 else "1980s" if y >= 1980 else decade


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def on_config(config):
    _S.clear()
    _S["geo"] = geo_lib.load_geo()
    _S["states"], _S["mesh"] = geo_lib.state_paths()
    _S["t_states"], _S["t_mesh"] = geo_lib.state_paths(tol=1.5, nd=0)  # lighter outlines for the home teaser
    return config


def on_files(files, config):
    urls = {}
    for f in files.documentation_pages():
        urls[f.src_uri] = f.url
    metas = geo_lib.story_meta()
    data = geo_lib.build(metas, urls, _S["geo"])
    # every story's states (front matter + its pins), for the state shading
    by_url = {s["u"]: s for s in data["stories"]}
    for rel, m in metas.items():
        u = urls.get(rel)
        if u in by_url:
            sts = {geo_lib.STATE_ABBR.get(x) for x in (m.get("states") or [])} - {None}
            by_url[u]["sts"] = sorted(sts)
            by_url[u]["b"] = sorted({era_bucket(e) for e in by_url[u]["es"]} - {""})
            by_url[u]["k"] = era_skin(by_url[u]["e"])
    for p in data["pins"]:
        p["x0"], p["y0"] = (round(v, 1) for v in geo_lib.project(p["lon"], p["lat"]))
        p["id"] = slug(p["n"])
        for i in p["x"]:
            st = data["stories"][i]
            if p["st"] and p["st"] not in st.setdefault("sts", []):
                st["sts"] = sorted(set(st["sts"]) | {p["st"]})
    _S["data"] = data
    _S["src_of"] = {}
    for rel in metas:
        if rel in urls:
            _S["src_of"][urls[rel]] = rel
    _S["pin_of_url"] = {}
    for p in data["pins"]:
        for i in p["x"]:
            _S["pin_of_url"].setdefault(data["stories"][i]["u"], p["id"])
    return files


def rel_href(target_url, here_url):
    return "../" * here_url.count("/") + target_url


def svg(here, teaser=False):
    d = _S["data"]
    aria = ('aria-hidden="true"' if teaser else
            'role="group" aria-label="Map of the United States with a pin for each town in the archive"')
    out = [f'<svg class="hr-map__svg" viewBox="0 0 975 610" preserveAspectRatio="xMidYMid meet" {aria}>']
    states, mesh = (_S["t_states"], _S["t_mesh"]) if teaser else (_S["states"], _S["mesh"])
    out.append('<g class="hr-map__states">')
    for ab, name, dd in states:
        if teaser:
            out.append(f'<path d="{dd}"/>')
        else:
            out.append(f'<path class="hr-map__st" data-st="{ab}" d="{dd}"><title>{H.escape(name)}</title></path>')
    out.append("</g>")
    out.append(f'<path class="hr-map__mesh" d="{mesh[0]}"/><path class="hr-map__coast" d="{mesh[1]}"/>')
    out.append('<g class="hr-map__pins">')
    for i, p in enumerate(d["pins"]):
        n = len(p["x"])
        r = 3.2 + 1.6 * (n ** 0.5) if teaser else 6
        if teaser:
            out.append(f'<circle class="hr-map__tpin" cx="{p["x0"]}" cy="{p["y0"]}" r="{r:.1f}"/>')
        else:
            out.append(f'<g class="hr-pin" data-i="{i}" transform="translate({p["x0"]} {p["y0"]})">'
                       f'<circle class="hr-pin__dot" r="{r}"/></g>')
    out.append("</g></svg>")
    return "".join(out)


def page_html(here):
    d = _S["data"]
    n_st, n_pin = len(d["stories"]), len(d["pins"])
    chips = "".join(
        f'<button type="button" class="hr-mchip" data-era-chip="{v}"{f" data-era={chr(34)}{k}{chr(34)}" if k else ""} '
        f'aria-pressed="{"true" if not v else "false"}"{" title=" + chr(34) + "1930s and earlier" + chr(34) if v == "1930s" else ""}>{H.escape(lab)}</button>'
        for v, lab, k in ERA_CHIPS)
    regions = "".join(f'<button type="button" class="hr-mchip hr-mchip--sm" data-region-chip="{r}" aria-pressed="false">{r}</button>'
                      for r in REGION_CHIPS)
    # the plain list: every pin by state (also the no-JS and screen-reader route into the stories)
    by_state = {}
    for p in d["pins"]:
        by_state.setdefault(p["st"], []).append(p)
    rows = []
    for st in sorted(by_state, key=lambda s: STATE_NAME.get(s, s)):
        items = []
        for p in sorted(by_state[st], key=lambda p: p["n"]):
            links = " · ".join(f'<a href="{rel_href(d["stories"][i]["u"], here)}">{H.escape(d["stories"][i]["t"])}</a>' for i in p["x"])
            items.append(f'<li id="place-{p["id"]}"><strong>{H.escape(p["n"].rpartition(", ")[0])}</strong>: {links}</li>')
        rows.append(f'<h3>{H.escape(STATE_NAME.get(st, st))}</h3><ul>{"".join(items)}</ul>')
    return f'''
<div class="hr-map" id="hr-map" data-hr-map data-stories="{n_st}" data-pins="{n_pin}">
  <div class="hr-map__bar">
    <div class="hr-map__chips" role="group" aria-label="Era">{chips}</div>
    <button type="button" class="hr-map__regbtn" aria-expanded="false" aria-controls="hr-map-regions">Region</button>
  </div>
  <div class="hr-map__chips hr-map__regions" id="hr-map-regions" role="group" aria-label="Region" hidden>{regions}</div>
  <p class="hr-map__count" aria-live="polite"><b>{n_st}</b> stories in <b>{n_pin}</b> places, all eras</p>
  <div class="hr-map__layout">
    <div class="hr-map__main">
      <div class="hr-map__stage">{svg(here)}</div>
      <div class="hr-map__tools">
        <p class="hr-map__hint">Tap a pin or a state. Pinch, or use the buttons, to zoom.</p>
        <div class="hr-map__zoom" role="group" aria-label="Zoom"><button type="button" data-zoom="out" aria-label="Zoom out">&minus;</button><button type="button" data-zoom="in" aria-label="Zoom in">+</button><button type="button" data-zoom="reset" class="hr-map__reset" aria-label="Show the whole country">&#8634;</button></div>
      </div>
      <div class="hr-map__legend" aria-hidden="true">
        <span class="hr-map__lg-pin"><i></i>A town in the stories; the number is how many</span>
        <span class="hr-map__lg-pin hr-map__lg-grp"><i></i>Several towns close together: tap to list them</span>
        <span class="hr-map__lg-scale"><em>Stories per state</em><i class="q1"></i><i class="q2"></i><i class="q3"></i><i class="q4"></i><i class="q5"></i><small>1</small><small>12+</small></span>
      </div>
    </div>
    <div class="hr-map__sheet" role="dialog" aria-modal="false" aria-labelledby="hr-map-sheet-h" hidden>
      <div class="hr-map__card">
        <div class="hr-map__grab" aria-hidden="true"></div>
        <div class="hr-map__head"><div><p class="hr-map__kicker"></p><p class="hr-map__h" id="hr-map-sheet-h" role="heading" aria-level="2"></p></div>
          <button type="button" class="hr-map__close" aria-label="Close"><svg class="hr-ico" aria-hidden="true"><use xlink:href="#hr-i-close"/></svg></button></div>
        <div class="hr-map__body"></div>
      </div>
    </div>
  </div>
</div>

<details class="hr-map__list" markdown="0"><summary>Every place on the map, by state ({n_pin} places)</summary>
<div class="hr-map__cols">{"".join(rows)}</div>
</details>
'''


def on_page_markdown(markdown, page, config, files):
    if page.file.src_uri == PAGE and MARK in markdown:
        markdown = markdown.replace(MARK, page_html(page.url))
    return markdown


def on_page_context(context, page, config, nav):
    pid = _S.get("pin_of_url", {}).get(page.url)
    if pid and isinstance(context.get("hr"), dict):
        # shown in the story head's meta line, beside "n open questions"
        context["hr"]["map_url"] = rel_href("reference/story-map/", page.url) + "?place=" + pid
    if page.file.src_uri == "index.md" and _S.get("data"):
        d = _S["data"]
        states = {s for st in d["stories"] for s in st.get("sts", [])}
        context["hr_map"] = {"svg": svg(page.url, teaser=True), "pins": len(d["pins"]), "stories": len(d["stories"]),
                             "states": len(states)}
    return context


def on_post_build(config):
    d = _S.get("data")
    if not d:
        return
    out = {"stories": [{k: s.get(k) for k in ("t", "u", "s", "e", "k", "b", "r", "d", "sts")} for s in d["stories"]],
           "pins": [{k: p[k] for k in ("id", "n", "st", "pr", "x0", "y0", "x", "strips")} for p in d["pins"]],
           "states": {ab: name for ab, name, _ in _S["states"]}}
    f = Path(config["site_dir"]) / "assets" / "hr-map.json"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
