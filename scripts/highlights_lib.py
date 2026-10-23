"""Shared logic for the home-page Highlights slider.

Used by hooks/highlights_hook.py (renders at build time and fails the build on
errors) and by scripts/update_highlights.py (add / check / list / archive).

Data file: docs/data/highlights.yml
"""
from __future__ import annotations

import datetime as _dt
import html
import posixpath
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
DATA = DOCS / "data" / "highlights.yml"
CREDITS = DOCS / "reference" / "image-credits.md"
IMAGES = DOCS / "assets" / "images"

SOURCE_TYPES = [
    "Local news", "Oral history", "Obituary", "Club newsletter", "Municipal record",
    "Historical marker", "Family account", "Local history site", "Forum post",
    "Archive", "Patent", "Trade press", "Museum / HOF",
]
# Source types that count as local / homegrown on their own.
GRASSROOTS_TYPES = {
    "Local news", "Oral history", "Obituary", "Club newsletter", "Municipal record",
    "Historical marker", "Family account", "Local history site", "Forum post",
}
FLAGS = {"none": "", "conflict": "⚠ Sources conflict", "single-source": "◐ Single source"}
CONFIDENCE = ["High", "Medium-High", "Medium", "Low-Medium", "Low"]
REQUIRED = ["id", "headline", "teaser", "link", "evidence", "source_type", "confidence", "flag", "added", "grassroots"]
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
MAX_TEASER_CHARS = 320
MAX_HEADLINE_CHARS = 110


# ---------------------------------------------------------------- loading
def load(path: Path = DATA) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    data.setdefault("settings", {})
    data["settings"].setdefault("max_featured", 16)
    data.setdefault("highlights", [])
    for h in data["highlights"]:
        a = h.get("added")
        if isinstance(a, (_dt.date, _dt.datetime)):
            h["added"] = a.isoformat()[:10]
    return data


def ordered(data: dict) -> tuple[list[dict], list[dict]]:
    """Newest first (date desc, file order within a date). Returns (featured, archived)."""
    items = list(enumerate(data["highlights"]))
    items.sort(key=lambda t: (_neg_date(t[1].get("added", "")), t[0]))
    flat = [h for _, h in items]
    n = int(data["settings"]["max_featured"])
    return flat[:n], flat[n:]


def _neg_date(s: str):
    return tuple(-int(x) for x in re.findall(r"\d+", str(s))[:3]) or (0,)


# ---------------------------------------------------------------- text helpers
def norm(text: str) -> str:
    t = text
    t = re.sub(r"\[\^[^\]]+\]", "", t)                    # footnote refs
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)        # links -> text
    t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    t = t.replace("—", "-").replace("–", "-").replace("\u00ad", "")
    t = re.sub(r"[*_`]", "", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


def slugify(text: str) -> str:
    # same algorithm as Markdown's toc extension default slugify
    t = re.sub(r"[^\w\s-]", "", text.strip().lower())
    return re.sub(r"[-\s]+", "-", t).strip("-")


def headings(md: str) -> set[str]:
    out = set()
    for m in re.finditer(r"^#{1,6}\s+(.*?)\s*#*\s*$", md, re.M):
        h = m.group(1)
        idm = re.search(r"\{[^}]*#([\w-]+)[^}]*\}\s*$", h)
        if idm:  # an explicit { #id } (attr_list) replaces the generated slug
            out.add(idm.group(1))
            continue
        out.add(slugify(re.sub(r"[*_`]", "", h)))
    return out


def credits() -> dict[str, dict]:
    """Parse docs/reference/image-credits.md table rows keyed by filename."""
    out: dict[str, dict] = {}
    if not CREDITS.exists():
        return out
    for line in CREDITS.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*`([^`]+)`\s*\|(.*)\|\s*$", line)
        if not m:
            continue
        cols = [c.strip() for c in m.group(2).split("|")]
        if len(cols) < 5:
            continue
        desc, creator, date, source, lic = cols[0], cols[1], cols[2], cols[3], cols[4]
        lic = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", lic)
        src = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", source)
        out[m.group(1)] = dict(creator=creator, license=lic, source=src, date=date, desc=desc)
    return out


# ---------------------------------------------------------------- validation
def validate(data: dict, strict_style: bool = False) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warns: list[str] = []
    seen: set[str] = set()
    creds = credits()
    for i, h in enumerate(data["highlights"]):
        hid = h.get("id", f"#{i}")
        e = lambda msg: errors.append(f"[{hid}] {msg}")  # noqa: E731
        w = lambda msg: warns.append(f"[{hid}] {msg}")  # noqa: E731
        for k in REQUIRED:
            if k not in h or h[k] in (None, ""):
                e(f"missing field '{k}'")
        if errors and any(m.startswith(f"[{hid}] missing") for m in errors):
            continue
        if not ID_RE.match(str(h["id"])):
            e("id must be lowercase letters, digits and hyphens")
        if h["id"] in seen:
            e("duplicate id")
        seen.add(h["id"])
        if len(h["headline"]) > MAX_HEADLINE_CHARS:
            e(f"headline longer than {MAX_HEADLINE_CHARS} chars")
        if len(h["teaser"]) > MAX_TEASER_CHARS:
            e(f"teaser longer than {MAX_TEASER_CHARS} chars")
        sentences = [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\"'])", h["teaser"].strip()) if s]
        if len(sentences) > 2:
            (e if strict_style else w)(f"teaser has {len(sentences)} sentences (limit 2)")
        types = h["source_type"] if isinstance(h["source_type"], list) else [h["source_type"]]
        for t in types:
            if t not in SOURCE_TYPES:
                e(f"unknown source_type '{t}' (allowed: {', '.join(SOURCE_TYPES)})")
        if h["confidence"] not in CONFIDENCE:
            e(f"confidence must be one of {CONFIDENCE}")
        if h["flag"] not in FLAGS:
            e(f"flag must be one of {list(FLAGS)}")
        if not isinstance(h["grassroots"], bool):
            e("grassroots must be true or false")
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(h["added"])):
            e("added must be YYYY-MM-DD")
        # link
        link, _, anchor = str(h["link"]).partition("#")
        target = DOCS / link
        if not link.endswith(".md") or not target.exists():
            e(f"link target not found: docs/{link}")
            continue
        md = target.read_text(encoding="utf-8")
        if anchor and anchor not in headings(md):
            e(f"anchor '#{anchor}' not found in {link}")
        # evidence: every phrase must occur verbatim (normalized) in the article
        ev = h["evidence"] if isinstance(h["evidence"], list) else [h["evidence"]]
        body = norm(md)
        for phrase in ev:
            if norm(str(phrase)) not in body:
                e(f"evidence phrase not found in {link}: {phrase!r}")
        # numbers in headline/teaser must exist in the article
        for num in re.findall(r"\d[\d,.]*\d|\d", h["headline"] + " " + h["teaser"]):
            n = num.rstrip(".,")
            if n not in body and n.replace(",", "") not in body.replace(",", ""):
                e(f"number '{n}' in headline/teaser does not appear in {link}")
        # image
        img = h.get("image")
        if img:
            if not (IMAGES / img).exists():
                e(f"image not found: docs/assets/images/{img}")
            if img not in creds:
                e(f"image '{img}' has no row in docs/reference/image-credits.md")
        # grassroots consistency
        if h["grassroots"] and not any(t in GRASSROOTS_TYPES for t in types):
            w("marked grassroots but source_type is not a local/homegrown type")
    return errors, warns


def batch_report(data: dict, day: str | None = None) -> list[str]:
    """Check the nightly standard for one 'added' date: 2-4 highlights, most grassroots."""
    msgs = []
    days = sorted({h["added"] for h in data["highlights"]})
    day = day or (days[-1] if days else None)
    if not day:
        return ["no highlights"]
    batch = [h for h in data["highlights"] if h["added"] == day]
    g = sum(1 for h in batch if h["grassroots"])
    msgs.append(f"batch {day}: {len(batch)} highlights, {g} grassroots")
    if len(batch) < 2:
        msgs.append("  STANDARD: add at least 2 highlights per round")
    if len(batch) > 4 and len(days) > 1:
        msgs.append("  STANDARD: add at most 4 highlights per round")
    if batch and g * 2 < len(batch):
        msgs.append("  STANDARD: at least half of each round's highlights should be grassroots")
    return msgs


# ---------------------------------------------------------------- rendering
def _rel(from_page_url: str, target_url: str) -> str:
    start = from_page_url.rstrip("/") or "."
    r = posixpath.relpath(target_url or ".", start)
    if target_url == "" or r == ".":
        return "./"
    return r + ("/" if not r.endswith("/") and not re.search(r"\.[a-z0-9]+$", r) else "")


def md_to_url(link: str) -> str:
    path, _, anchor = link.partition("#")
    if path.endswith("/index.md"):
        url = path[: -len("index.md")]
    elif path == "index.md":
        url = ""
    else:
        url = path[:-3] + "/"
    return url + (("#" + anchor) if anchor else "")


def link_href(page_url: str, link: str) -> str:
    url = md_to_url(link)
    path, _, anchor = url.partition("#")
    rel = _rel(page_url, path)
    return rel + (("#" + anchor) if anchor else "")


def asset_href(page_url: str, filename: str) -> str:
    start = page_url.rstrip("/") or "."
    return posixpath.relpath("assets/images/" + filename, start)


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def _chips(h: dict) -> str:
    types = h["source_type"] if isinstance(h["source_type"], list) else [h["source_type"]]
    out = []
    if h["grassroots"]:
        out.append('<span class="hr-badge" title="Drawn mainly from local news, oral history, obituaries, club or municipal records">Local &amp; grassroots</span>')
    for t in types:
        out.append(f'<span class="hr-chip hr-chip--src">{esc(t)}</span>')
    if h["flag"] != "none":
        out.append(f'<span class="hr-chip hr-chip--{esc(h["flag"])}">{esc(FLAGS[h["flag"]])}</span>')
    conf = h["confidence"]
    cls = "high" if conf.startswith("High") or conf == "Medium-High" else ("low" if conf.startswith("Low") else "mid")
    out.append(f'<span class="hr-chip hr-chip--{cls}" title="Confidence rating">{esc(conf)}</span>')
    return " ".join(out)


def card(h: dict, page_url: str, idx: int, total: int, creds: dict, eager: bool) -> str:
    href = link_href(page_url, h["link"])
    media = ""
    if h.get("image"):
        c = creds.get(h["image"], {})
        credit = f'Photo: {c.get("creator","")}, {c.get("license","")}' if c else ""
        if h.get("image_note"):
            credit = f'{h["image_note"]} {credit}'.strip()
        alt = h.get("image_alt") or ""
        lazy = "" if eager else 'loading="lazy" '
        src = esc(asset_href(page_url, h["image"]))
        media = (
            '<div class="hr-hl-media">'
            f'<img class="off-glb" src="{src}" alt="{esc(alt)}" {lazy}decoding="async">'
            f'<span class="hr-hl-credit">{esc(credit)}</span></div>'
        )
    else:
        media = '<div class="hr-hl-media hr-hl-media--plain" aria-hidden="true"><span>' + esc((h.get("eras") or [""])[0]) + "</span></div>"
    tags = [*(h.get("eras") or []), *(h.get("regions") or [])]
    meta = " · ".join(esc(t) for t in tags)
    added = esc(h["added"])
    return (
        f'<li class="hr-hl-slide" id="hl-{esc(h["id"])}" '
        f'data-grassroots="{"true" if h["grassroots"] else "false"}">'
        f'<article class="hr-hl-card" role="group" aria-roledescription="slide" aria-label="{idx} of {total}">{media}<div class="hr-hl-body">'
        f'<p class="hr-hl-chips">{_chips(h)}</p>'
        f'<h3 class="hr-hl-headline"><a href="{esc(href)}">{esc(h["headline"])}</a></h3>'
        f'<p class="hr-hl-teaser">{esc(h["teaser"])}</p>'
        f'<p class="hr-hl-meta">{meta}{" · " if meta else ""}Added {added}</p>'
        f'<a class="hr-hl-more" href="{esc(href)}">Read the full story <span aria-hidden="true">→</span></a>'
        "</div></article></li>"
    )


def render_slider(data: dict, page_url: str) -> str:
    featured, _ = ordered(data)
    creds = credits()
    n = len(featured)
    if not n:
        return ""
    slides = "".join(card(h, page_url, i + 1, n, creds, eager=(i == 0)) for i, h in enumerate(featured))
    g = sum(1 for h in featured if h["grassroots"])
    arch = link_href(page_url, "highlights-archive.md")
    return (
        '<section class="hr-highlights" id="hr-highlights" aria-roledescription="carousel" '
        'aria-labelledby="hr-hl-title" data-autoplay="7000">'
        '<script>document.currentScript.parentNode.classList.add("hr-hl--js")</script>'
        '<div class="hr-hl-head"><h2 id="hr-hl-title">Highlights</h2>'
        f'<p class="hr-hl-sub">Surprising finds from the wiki. {g} of {n} come from local news, obituaries, '
        'oral histories and other homegrown sources. '
        f'<a href="{esc(arch)}">Highlights archive</a></p></div>'
        f'<div class="hr-hl-viewport"><ul class="hr-hl-track">{slides}</ul></div>'
        "</section>"
    )


def render_archive(data: dict, page_url: str) -> str:
    _, archived = ordered(data)
    if not archived:
        return '<p><em>Nothing has rotated out yet. When the slider holds more than the newest '  \
               f'{data["settings"]["max_featured"]} highlights, older ones move here automatically.</em></p>'
    rows = []
    for h in archived:
        href = link_href(page_url, h["link"])
        types = h["source_type"] if isinstance(h["source_type"], list) else [h["source_type"]]
        badge = '<span class="hr-badge">Local &amp; grassroots</span> ' if h["grassroots"] else ""
        flag = f' <span class="hr-chip hr-chip--{esc(h["flag"])}">{esc(FLAGS[h["flag"]])}</span>' if h["flag"] != "none" else ""
        chips = " ".join('<span class="hr-chip hr-chip--src">' + esc(t) + "</span>" for t in types)
        rows.append(
            f'<li class="hr-arch-item"><p class="hr-hl-chips">{badge}{chips}{flag}</p>'
            f'<h3><a href="{esc(href)}">{esc(h["headline"])}</a></h3>'
            f'<p>{esc(h["teaser"])}</p><p class="hr-hl-meta">Added {esc(h["added"])}</p></li>'
        )
    return '<ul class="hr-arch">' + "".join(rows) + "</ul>"
