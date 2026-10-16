"""Shared logic for the Web of influence page.

Used by hooks/connections_hook.py (renders at build time and fails the build on errors) and by
scripts/check_connections.py (the same checks from the command line).

Data file: docs/data/connections.yml  (nodes + edges; every edge names a supporting page and verbatim evidence)
Output   : a static, dependency-free SVG graph, a filterable relationship legend and a full text table.
"""
from __future__ import annotations

import html
import math
import random
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import highlights_lib as hl  # noqa: E402  (norm, md_to_url, _rel, esc)

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
DATA = DOCS / "data" / "connections.yml"

NODE_TYPES = {
    "company": "Company or brand",
    "person": "Person",
    "place": "Place or strip",
    "club": "Club or scene",
    "institution": "Institution or program",
}
EDGE_TYPES = {
    "founded": "Founded / built",
    "partnered": "Partnered",
    "employed": "Employed / worked for",
    "customer": "Customer / supplier",
    "acquired": "Acquired / merged",
    "patent": "Patent chain",
    "promotion": "Promotion / advertising",
    "mentor": "Mentor / influence",
    "scene": "Same scene or event",
    "hometown": "Hometown / home base",
}
FLAGS = {"none": "", "conflict": "⚠ Sources conflict", "single-source": "◐ Single source"}
GROUPS = {"big-names": "The Big Names", "garage-born": "Garage-born shops"}
MAX_LABEL = 96


# ------------------------------------------------------------------ loading / validation
def load(path: Path = DATA) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    data.setdefault("nodes", [])
    data.setdefault("edges", [])
    return data


def _page_text(rel: str, cache: dict) -> str | None:
    if rel not in cache:
        p = DOCS / rel
        cache[rel] = hl.norm(p.read_text(encoding="utf-8")) if p.is_file() else None
    return cache[rel]


def validate(data: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warns: list[str] = []
    cache: dict = {}
    nodes = data["nodes"]
    ids: dict = {}
    for n in nodes:
        nid = n.get("id")
        if not nid:
            errors.append(f"node without id: {n}")
            continue
        if nid in ids:
            errors.append(f"duplicate node id: {nid}")
        ids[nid] = n
        for f in ("label", "type", "page"):
            if not n.get(f):
                errors.append(f"node {nid}: missing {f}")
        if n.get("type") and n["type"] not in NODE_TYPES:
            errors.append(f"node {nid}: unknown type {n['type']!r}")
        if n.get("type") == "company" and n.get("group") not in GROUPS:
            errors.append(f"node {nid}: company needs group big-names or garage-born")
        if n.get("page") and _page_text(n["page"], cache) is None:
            errors.append(f"node {nid}: page not found: {n['page']}")
    seen = set()
    degree = {i: 0 for i in ids}
    for i, e in enumerate(data["edges"]):
        tag = f"edge #{i + 1} ({e.get('from')} -> {e.get('to')})"
        for f in ("from", "to", "type", "label", "page", "evidence"):
            if not e.get(f):
                errors.append(f"{tag}: missing {f}")
        for end in ("from", "to"):
            if e.get(end) and e[end] not in ids:
                errors.append(f"{tag}: unknown node {e[end]!r}")
        if e.get("from") == e.get("to"):
            errors.append(f"{tag}: edge to itself")
        if e.get("type") and e["type"] not in EDGE_TYPES:
            errors.append(f"{tag}: unknown relationship type {e['type']!r}")
        if e.get("flag", "none") not in FLAGS:
            errors.append(f"{tag}: unknown flag {e.get('flag')!r}")
        if len(str(e.get("label", ""))) > MAX_LABEL:
            errors.append(f"{tag}: label longer than {MAX_LABEL} characters")
        key = (e.get("from"), e.get("to"), e.get("type"), e.get("page"))
        if key in seen:
            errors.append(f"{tag}: duplicate edge")
        seen.add(key)
        if e.get("from") in degree:
            degree[e["from"]] += 1
        if e.get("to") in degree:
            degree[e["to"]] += 1
        page = e.get("page")
        if page:
            text = _page_text(page, cache)
            if text is None:
                errors.append(f"{tag}: supporting page not found: {page}")
            else:
                ev = e["evidence"] if isinstance(e.get("evidence"), list) else [e.get("evidence", "")]
                for phrase in ev:
                    if not phrase or hl.norm(str(phrase)) not in text:
                        errors.append(f"{tag}: evidence phrase not found in {page}: {phrase!r}")
        # an edge must be documented on a page that is one of its two endpoints' pages, or a third page
        # that names both ends; we require the endpoint labels' key words only as a soft warning.
    for nid, d in degree.items():
        if d == 0:
            errors.append(f"node {nid}: no edges (an orphan does not belong in the graph)")
    # every company profile in the department must be a node (keeps the graph in step with the pages)
    covered = {n.get("page") for n in nodes if n.get("type") == "company"}
    for p in sorted((DOCS / "companies").glob("*.md")):
        rel = "companies/" + p.name
        if p.name in ("index.md", "web-of-influence.md"):
            continue
        if rel not in covered:
            errors.append(f"companies page without a company node: {rel}")
    # connected graph?
    adj: dict = {i: set() for i in ids}
    for e in data["edges"]:
        if e.get("from") in adj and e.get("to") in adj:
            adj[e["from"]].add(e["to"])
            adj[e["to"]].add(e["from"])
    if ids:
        start = next(iter(ids))
        seen_n, stack = {start}, [start]
        while stack:
            for m in adj[stack.pop()]:
                if m not in seen_n:
                    seen_n.add(m)
                    stack.append(m)
        if len(seen_n) != len(ids):
            warns.append("graph has separate islands: " + ", ".join(sorted(set(ids) - seen_n)))
    return errors, warns


# ------------------------------------------------------------------ layout (deterministic force-directed + label de-overlap)
W, H = 1240, 900          # nominal canvas the force layout is scaled to; the final viewBox is fitted to the result
PAD_X, PAD_Y = 170, 50
FONT_PX = {"company": 8.1, "other": 6.9}   # rough text width per character, in viewBox units


def _label_w(n: dict) -> float:
    return len(n["label"]) * (FONT_PX["company"] if n["type"] == "company" else FONT_PX["other"]) + 24


def layout(data: dict) -> tuple[dict, tuple[float, float, float, float]]:
    rnd = random.Random(1947)
    nodes = data["nodes"]
    idx = {n["id"]: i for i, n in enumerate(nodes)}
    n = len(nodes)
    order = sorted(range(n), key=lambda i: (nodes[i]["type"], nodes[i].get("group", ""), nodes[i]["label"]))
    pos = [[0.0, 0.0] for _ in range(n)]
    for k, i in enumerate(order):
        a = 2 * math.pi * k / n
        pos[i] = [math.cos(a) * 0.45 + rnd.uniform(-0.03, 0.03), math.sin(a) * 0.45 + rnd.uniform(-0.03, 0.03)]
    edges = [(idx[e["from"]], idx[e["to"]]) for e in data["edges"]]
    k_opt = 0.24
    t = 0.14
    for _ in range(700):
        disp = [[0.0, 0.0] for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                dx, dy = pos[i][0] - pos[j][0], pos[i][1] - pos[j][1]
                d = math.hypot(dx, dy) or 0.001
                f = (k_opt * k_opt) / d
                disp[i][0] += dx / d * f
                disp[i][1] += dy / d * f
                disp[j][0] -= dx / d * f
                disp[j][1] -= dy / d * f
        for a, b in edges:
            dx, dy = pos[a][0] - pos[b][0], pos[a][1] - pos[b][1]
            d = math.hypot(dx, dy) or 0.001
            f = (d * d) / k_opt
            disp[a][0] -= dx / d * f
            disp[a][1] -= dy / d * f
            disp[b][0] += dx / d * f
            disp[b][1] += dy / d * f
        for i in range(n):
            disp[i][0] -= pos[i][0] * 0.25
            disp[i][1] -= pos[i][1] * 0.25
        for i in range(n):
            d = math.hypot(*disp[i]) or 0.001
            step = min(d, t)
            pos[i][0] += disp[i][0] / d * step
            pos[i][1] += disp[i][1] / d * step
        t = max(0.002, t * 0.992)
    xs = [p[0] for p in pos]
    ys = [p[1] for p in pos]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    P = []
    for p in pos:
        P.append([PAD_X + (p[0] - minx) / ((maxx - minx) or 1) * (W - 2 * PAD_X),
                  PAD_Y + (p[1] - miny) / ((maxy - miny) or 1) * (H - 2 * PAD_Y)])
    # de-overlap: each node owns a box = marker + its label on the outward side
    def boxes():
        cx = sum(p[0] for p in P) / n
        out = []
        for i, nd in enumerate(nodes):
            x, y = P[i]
            w = _label_w(nd)
            if x >= cx:
                out.append((x - 14, y - 12, x + 14 + w, y + 12))
            else:
                out.append((x - 14 - w, y - 12, x + 14, y + 12))
        return out
    for _ in range(400):
        moved = False
        bx = boxes()
        for i in range(n):
            for j in range(i + 1, n):
                a, b = bx[i], bx[j]
                ox = min(a[2], b[2]) - max(a[0], b[0])
                oy = min(a[3], b[3]) - max(a[1], b[1])
                if ox > 0 and oy > 0:
                    moved = True
                    if oy <= ox * 0.8:       # nudge vertically first: labels stack more easily than they slide
                        s = (oy / 2 + 2) * (1 if P[i][1] <= P[j][1] else -1)
                        P[i][1] -= s
                        P[j][1] += s
                    else:
                        s = (ox / 2 + 2) * (1 if P[i][0] <= P[j][0] else -1)
                        P[i][0] -= s
                        P[j][0] += s
        if not moved:
            break
    bx = boxes()
    vb = (min(b[0] for b in bx) - 20, min(b[1] for b in bx) - 20,
          max(b[2] for b in bx) + 20, max(b[3] for b in bx) + 20)
    out = {nd["id"]: (round(P[i][0], 1), round(P[i][1], 1)) for i, nd in enumerate(nodes)}
    return out, vb


# ------------------------------------------------------------------ rendering
def _node_url(page_url: str, md: str) -> str:
    return hl._rel(page_url, hl.md_to_url(md))


def _shape(n: dict, x: float, y: float) -> str:
    t = n["type"]
    if t == "company":
        r = 13 if n.get("group") == "big-names" else 11
        return f'<circle cx="{x}" cy="{y}" r="{r}"/>'
    if t == "person":
        return f'<rect x="{x - 8}" y="{y - 8}" width="16" height="16" rx="3"/>'
    if t == "place":
        return f'<polygon points="{x},{y - 10} {x + 10},{y} {x},{y + 10} {x - 10},{y}"/>'
    if t == "club":
        return f'<polygon points="{x},{y - 10} {x + 10},{y + 8} {x - 10},{y + 8}"/>'
    pts = " ".join(f"{x + 10 * math.cos(math.pi / 3 * k):.1f},{y + 10 * math.sin(math.pi / 3 * k):.1f}" for k in range(6))
    return f'<polygon points="{pts}"/>'


def render_graph(data: dict, page_url: str) -> str:
    pos, vb = layout(data)
    nodes = {n["id"]: n for n in data["nodes"]}
    cx = sum(p[0] for p in pos.values()) / len(pos)
    cy = sum(p[1] for p in pos.values()) / len(pos)
    deg: dict = {i: [] for i in nodes}
    for k, e in enumerate(data["edges"]):
        deg[e["from"]].append(k)
        deg[e["to"]].append(k)
    esc = hl.esc
    parts = [
        f'<svg class="hr-web__svg" viewBox="{vb[0]:.0f} {vb[1]:.0f} {vb[2] - vb[0]:.0f} {vb[3] - vb[1]:.0f}" role="group" aria-labelledby="hr-web-title hr-web-desc" '
        'xmlns="http://www.w3.org/2000/svg">',
        f'<title id="hr-web-title">Web of influence: {len(nodes)} companies, people, places and clubs and the '
        f'{len(data["edges"])} documented connections between them</title>',
        '<desc id="hr-web-desc">Each line is a connection backed by a wiki page. A full text table follows the diagram.</desc>',
        '<g class="hr-web__edges">',
    ]
    for k, e in enumerate(data["edges"]):
        x1, y1 = pos[e["from"]]
        x2, y2 = pos[e["to"]]
        flag = e.get("flag", "none")
        parts.append(
            f'<line class="hr-web__edge hr-web__edge--{e["type"]}{" is-" + flag if flag != "none" else ""}" '
            f'data-edge="{k}" data-type="{e["type"]}" data-a="{e["from"]}" data-b="{e["to"]}" '
            f'x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"><title>{esc(nodes[e["from"]]["label"])} — {esc(EDGE_TYPES[e["type"]].lower())} — '
            f'{esc(nodes[e["to"]]["label"])}: {esc(e["label"])}</title></line>'
        )
    parts.append("</g>")
    parts.append('<g class="hr-web__nodes">')
    for nid, n in nodes.items():
        x, y = pos[nid]
        right = x >= cx
        dx = 18 if right else -18
        anchor = "start" if right else "end"
        cls = f'hr-web__node hr-web__node--{n["type"]}' + (f' hr-web__node--{n["group"]}' if n.get("group") else "")
        label = esc(n["label"])
        summary = "; ".join(esc(data["edges"][k]["label"]) for k in deg[nid][:3])
        parts.append(
            f'<a class="{cls}" href="{esc(_node_url(page_url, n["page"]))}" data-node="{nid}" '
            f'aria-label="{label}, {esc(NODE_TYPES[n["type"]].lower())}, {len(deg[nid])} connections">'
            f'<title>{label} ({esc(NODE_TYPES[n["type"]])}): {summary}</title>'
            f'{_shape(n, x, y)}<text x="{x + dx}" y="{y + 4}" text-anchor="{anchor}">{label}</text></a>'
        )
    parts.append("</g></svg>")
    return "\n".join(parts)


def render_legend(data: dict) -> str:
    used_edge = sorted({e["type"] for e in data["edges"]}, key=list(EDGE_TYPES).index)
    chips = "".join(
        f'<label class="hr-web__chip hr-web__chip--{t}"><input type="checkbox" data-filter="{t}" checked> '
        f'<span class="hr-web__swatch"></span>{html.escape(EDGE_TYPES[t])}</label>'
        for t in used_edge
    )
    shapes = "".join(
        f'<li><span class="hr-web__key hr-web__key--{t}" aria-hidden="true"></span>{html.escape(NODE_TYPES[t])}</li>'
        for t in NODE_TYPES
        if any(n["type"] == t for n in data["nodes"])
    )
    return (
        '<div class="hr-web__controls">'
        f'<fieldset class="hr-web__filters"><legend>Show relationships</legend>{chips}</fieldset>'
        f'<ul class="hr-web__shapes" aria-label="Shape key">{shapes}'
        '<li><span class="hr-web__key hr-web__key--dashed" aria-hidden="true"></span>⚠ Sources conflict</li>'
        '<li><span class="hr-web__key hr-web__key--dotted" aria-hidden="true"></span>◐ Single source</li></ul>'
        '<p class="hr-web__hint" id="hr-web-panel" aria-live="polite">Hover over a name or tab to it to light up its connections; '
        'each name links to the page that documents it.</p></div>'
    )


def render_table(data: dict, page_url: str) -> str:
    nodes = {n["id"]: n for n in data["nodes"]}
    esc = hl.esc
    rows = []
    for e in sorted(data["edges"], key=lambda e: (nodes[e["from"]]["label"].lower(), nodes[e["to"]]["label"].lower())):
        a, b = nodes[e["from"]], nodes[e["to"]]
        flag = FLAGS[e.get("flag", "none")]
        page = e["page"]
        rows.append(
            "<tr>"
            f'<td><a href="{esc(_node_url(page_url, a["page"]))}">{esc(a["label"])}</a></td>'
            f'<td>{esc(EDGE_TYPES[e["type"]])}</td>'
            f'<td><a href="{esc(_node_url(page_url, b["page"]))}">{esc(b["label"])}</a></td>'
            f'<td>{esc(e["label"])}{" <strong>" + esc(flag) + "</strong>" if flag else ""}</td>'
            f'<td><a href="{esc(_node_url(page_url, page))}">{esc(page.rsplit("/", 1)[-1][:-3].replace("-", " "))}</a></td>'
            "</tr>"
        )
    return (
        '<div class="hr-web__table-wrap"><table class="hr-web__table"><caption class="hr-sr">All connections in the web of '
        'influence, with the wiki page that documents each one</caption>'
        '<thead><tr><th scope="col">From</th><th scope="col">Relationship</th><th scope="col">To</th>'
        '<th scope="col">What the page says</th><th scope="col">Evidence page</th></tr></thead><tbody>'
        + "".join(rows)
        + "</tbody></table></div>"
    )


def render_stats(data: dict) -> str:
    c = sum(1 for n in data["nodes"] if n["type"] == "company")
    p = sum(1 for n in data["nodes"] if n["type"] == "person")
    pl = sum(1 for n in data["nodes"] if n["type"] in ("place", "club", "institution"))
    return (
        f'<p class="hr-web__stats"><strong>{len(data["nodes"])}</strong> names '
        f'({c} companies, {p} people, {pl} places, clubs and programs) · '
        f'<strong>{len(data["edges"])}</strong> documented connections</p>'
    )
