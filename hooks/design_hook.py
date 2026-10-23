"""MkDocs hook: editorial/magazine layer for the Hot Rod History site.

Everything here is *additive* and derived from the Markdown the researchers and editors already write.
Nothing in the .md files has to change for a new article to get the full magazine treatment.

What it does (build time only, no runtime cost):
  * on_page_content : lifts the H1 out of the body (the template renders it as the feature headline), parses the
                      "Article record" admonition into a timing-slip, classifies figures (wide / plate / tall),
                      adds srcset thumbnails, marks the lede paragraph (drop cap), classes blockquotes as pull quotes,
                      wraps the ⚠ / ◐ flags, labels the footnote list, turns the timeline table into a real timeline,
                      groups the people/company index by letter, tags table columns on reference pages.
  * on_page_context : gives every template an `hr` dict (kind, era, department, record, hero image, related stories,
                      previous/next in department, ...) plus site-wide `hr_site` (departments, stats, era strip,
                      timeline ribbon, notebook leads, story of the day, overheard quotes).
  * on_post_build   : writes small JPEG thumbnails to site/assets/thumbs/ when Pillow is available (the templates
                      fall back to the full-size image when a thumbnail is missing).

Optional front-matter (all additive): deck, era (1930s..1980s), region, featured (home), template.
"""
import datetime
import hashlib
import html as htmlmod
import logging
import re
import statistics
import struct
from html.parser import HTMLParser
from pathlib import Path

log = logging.getLogger("mkdocs.hooks.design")

INFO = {}      # src_uri -> dict
import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import related_lib  # noqa: E402  (front-matter overlap scoring)
import quick_answers_lib  # noqa: E402  (Quick answers links in Keep reading)

SITE = {}      # site-wide, filled lazily in on_page_context
IMG_DIMS = {}  # abs path -> (w, h)

ERA_ORDER = ["e30", "e50", "e60", "e70", "e80"]
ERA_LABEL = {"e30": "Dry lakes · 1930s–40s", "e50": "Turquoise & cream · 1950s", "e60": "Candy & flake · 1960s",
             "e70": "Earth tones · 1970s", "e80": "Neon & chrome · 1980s"}
ERA_SHORT = {"e30": "1930s–40s", "e50": "1950s", "e60": "1960s", "e70": "1970s", "e80": "1980s"}
FRONT_ERA = {"1920s": "e30", "1930s": "e30", "1940s": "e30", "1950s": "e50", "1960s": "e60", "1970s": "e70", "1980s": "e80",
             "1990s": "e80", "e30": "e30", "e50": "e50", "e60": "e60", "e70": "e70", "e80": "e80"}

# Department presentation defaults, keyed by first path segment of the section index (or page stem).
DEPT = {
    "eras": ("sun", "The calendar: decade by decade, from the dry lakes to Pro Street."),
    "people": ("person", "Machinists, racers, publishers and the families behind them."),
    "companies": ("piston", "Garage-born speed shops, the big aftermarket names they grew into, and the map of who connected to whom."),
    "cars": ("car", "Streamliners and gassers, car by car, and the techniques that built them."),
    "customs": ("flame", "The style: lead sleds, chops and the builders of Kustom Kulture."),
    "street-rodding": ("wheel", "NSRA, the early Nationals, the 1948 rule and fiberglass bodies."),
    "media": ("paper", "Magazines, Trend Books, model kits and shows: how the hobby was publicized and sold."),
    "drag-racing": ("flag", "Strips, clubs and timing associations, and the rules and arguments around them."),
    "places": ("pin", "Regional scenes beyond California, plus the cruise strips and hangouts."),
    "voices": ("quote", "In their own words: racers, builders, families and fans."),
    "reference": ("book", "Timeline, index, patents, credits, standards, the research trail and the bibliography."),
}
NO_THUMB = {"reference", "index"}
REF_PAGES = ("about/", "reference/", "bibliography.md", "research-trail.md", "highlights-archive.md", "taxonomy.md", "contribute.md", "style-guide.md")

TAG_RE = re.compile(r"<[^>]+>")


# ---------------------------------------------------------------- small helpers
def text_of(fragment):
    t = TAG_RE.sub("", fragment)
    t = htmlmod.unescape(t)
    return re.sub(r"\s+", " ", t).strip()


def clean_inline(fragment):
    """Plain text without footnote refs/permalinks."""
    fragment = re.sub(r"<sup[^>]*>.*?</sup>", "", fragment, flags=re.S)
    fragment = re.sub(r'<a class="headerlink".*?</a>', "", fragment, flags=re.S)
    return text_of(fragment)


def truncate(t, n):
    if len(t) <= n:
        return t
    cut = t[:n].rsplit(" ", 1)[0].rstrip(",;:—-")
    return cut + "…"


def img_size(path):
    """(w, h) for png/jpg/gif/webp/svg without Pillow."""
    p = str(path)
    if p in IMG_DIMS:
        return IMG_DIMS[p]
    dims = None
    try:
        with open(p, "rb") as f:
            d = f.read(65536)
        if d[:8] == b"\x89PNG\r\n\x1a\n":
            dims = struct.unpack(">II", d[16:24])
        elif d[:2] == b"\xff\xd8":
            i = 2
            while i < len(d) - 9:
                if d[i] != 0xFF:
                    i += 1
                    continue
                m = d[i + 1]
                if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
                    h, w = struct.unpack(">HH", d[i + 5:i + 9])
                    dims = (w, h)
                    break
                i += 2 + struct.unpack(">H", d[i + 2:i + 4])[0]
        elif d[:6] in (b"GIF87a", b"GIF89a"):
            dims = struct.unpack("<HH", d[6:10])
        elif d[:4] == b"RIFF" and d[8:12] == b"WEBP":
            if d[12:16] == b"VP8 ":
                w, h = struct.unpack("<HH", d[26:30])
                dims = (w & 0x3FFF, h & 0x3FFF)
            elif d[12:16] == b"VP8X":
                dims = (1 + int.from_bytes(d[24:27], "little"), 1 + int.from_bytes(d[27:30], "little"))
    except Exception:  # pragma: no cover
        dims = None
    IMG_DIMS[p] = dims
    return dims


class TopLevelP(HTMLParser):
    """Find the character offsets of the first top-level <p> (depth 0) whose text is long enough."""
    BLOCKS = {"div", "blockquote", "figure", "ul", "ol", "table", "details", "section", "aside", "nav", "dl"}

    def __init__(self, html):
        super().__init__(convert_charrefs=False)
        self.html = html
        self.lines = [0]
        for m in re.finditer(r"\n", html):
            self.lines.append(m.end())
        self.depth = 0
        self.found = None
        self.in_p = False
        self.p_start = None
        self.p_text = ""
        self.min_len = 90

    def _off(self):
        l, c = self.getpos()
        return self.lines[l - 1] + c

    def handle_starttag(self, tag, attrs):
        if tag in self.BLOCKS:
            self.depth += 1
        elif tag == "p" and self.depth == 0 and self.found is None:
            self.in_p, self.p_start, self.p_text = True, self._off(), ""

    def handle_endtag(self, tag):
        if tag in self.BLOCKS:
            self.depth = max(0, self.depth - 1)
        elif tag == "p" and self.in_p:
            self.in_p = False
            if len(self.p_text.strip()) >= self.min_len and self.found is None:
                self.found = self.p_start

    def handle_data(self, data):
        if self.in_p:
            self.p_text += data


def mark_lede(html):
    p = TopLevelP(html)
    try:
        p.feed(html)
    except Exception:  # pragma: no cover
        return html
    if p.found is None:
        return html
    seg = html[p.found:p.found + 3]
    if re.match(r"<p>\s*<(strong|em|b|a)\b", html[p.found:p.found + 40]):
        return html
    if seg == "<p>":
        return html[:p.found] + '<p class="hr-lede">' + html[p.found + 3:]
    return html


# ---------------------------------------------------------------- record box
REC_RE = re.compile(r'<div class="admonition abstract">\s*<p class="admonition-title">(.*?)</p>\s*<p>(.*?)</p>\s*</div>', re.S)


def parse_record(html):
    m = REC_RE.search(html)
    if not m:
        return html, None
    body = m.group(2)
    parts = [p.strip() for p in re.split(r"\s+·\s+", body)]
    rec = {"fields": [], "link": None, "title": text_of(m.group(1))}
    for part in parts:
        km = re.match(r"<strong>([^<:]+):?</strong>:?\s*(.*)$", part, re.S)
        if km:
            rec["fields"].append((km.group(1).strip(), km.group(2).strip()))
        elif part.startswith("<a "):
            rec["link"] = part
        else:
            return html, None
    keys = {k.lower(): v for k, v in rec["fields"]}
    if "confidence" not in keys:
        return html, None
    conf = text_of(keys["confidence"])
    low = conf.lower()
    if low.startswith("high"):
        level = "high"
    elif low.startswith(("medium–high", "medium-high", "med-high", "mid-high")):
        level = "midhigh"
    elif low.startswith("medium") or low.startswith("mid"):
        level = "mid"
    elif low.startswith("low"):
        level = "low"
    else:
        level = "mid"
    wm = re.match(r"\s*(medium[–-]high|medium[–-]low|low[–-]medium|high|medium|low|mid|[A-Za-z]+)", conf, re.I)
    first = wm.group(1) if wm else conf.split(" ")[0]
    rest = conf[len(first):].strip(" ;,()–-")
    rec.update(level=level, conf_word=first, conf_note=rest,
               grassroots="hr-badge" in body)
    return html[:m.start()] + html[m.end():], rec


# ---------------------------------------------------------------- figures
FIG_RE = re.compile(r"<figure(\s[^>]*)?>(.*?)</figure>", re.S)
IMG_RE = re.compile(r"<img\b[^>]*>", re.S)


def thumb_name(fname):
    return "assets/thumbs/" + Path(fname).stem + ".jpg"


def process_figures(html, page, config, info):
    docs = Path(config["docs_dir"])
    base = Path(page.file.src_uri).parent
    first_wide = None
    thumbs_ok = SITE.get("thumbs_enabled", False)
    out = []
    last = 0
    idx = 0
    for m in FIG_RE.finditer(html):
        inner = m.group(2)
        im = IMG_RE.search(inner)
        kind = "std"
        ar = None
        src_rel = None
        if im:
            sm = re.search(r'src="([^"]+)"', im.group(0))
            if sm:
                src = sm.group(1)
                name = Path(src).name
                abs_p = docs / "assets" / "images" / name
                if abs_p.exists():
                    src_rel = "assets/images/" + name
                    dims = img_size(abs_p)
                    if dims:
                        w, h = dims
                        ar = (w, h)
                        ratio = w / h
                        if name.startswith(("patent-", "loc-haer")) or name.endswith(".png"):
                            kind = "plate"
                        elif ratio >= 1.25 and w >= 900:
                            kind = "wide"
                        elif ratio < 0.9:
                            kind = "tall"
                        elif w < 700:
                            kind = "small"
                        else:
                            kind = "std"
        cls = f"hr-fig hr-fig--{kind}"
        open_tag = "<figure" + (m.group(1) or "") + ">"
        if 'class="' in open_tag:
            open_tag = open_tag.replace('class="', f'class="{cls} ', 1)
        else:
            open_tag = f'<figure class="{cls}"' + (m.group(1) or "") + ">"
        if ar:
            open_tag = open_tag.replace("<figure", f'<figure style="--hr-ar:{ar[0]}/{ar[1]}"', 1)
        new_inner = inner
        if im and ar and src_rel:
            tag = im.group(0)
            extra = f' width="{ar[0]}" height="{ar[1]}"'
            tag2 = re.sub(r'\s(width|height)="[^"]*"', "", tag)
            tag2 = tag2[:-1].rstrip("/").rstrip() + extra + " decoding=\"async\">"
            if thumbs_ok and ar[0] > 760:
                s_full = re.search(r'src="([^"]+)"', tag2).group(1)
                s_thumb = re.sub(r"[^/]+$", Path(thumb_name(src_rel)).name, s_full).replace("/images/", "/thumbs/")
                tag2 = tag2.replace(f'src="{s_full}"', f'src="{s_full}" srcset="{s_thumb} 720w, {s_full} {ar[0]}w" sizes="(min-width: 70em) 640px, 92vw"', 1)
            new_inner = inner.replace(tag, tag2, 1)
        piece = open_tag + new_inner + "</figure>"
        out.append(html[last:m.start()])
        out.append(piece)
        last = m.end()
        if src_rel and "thumb" not in info:
            if kind in ("wide", "std", "tall") and not Path(src_rel).name.startswith(("patent-", "loc-haer")):
                info["thumb"] = src_rel
        if idx == 0 and kind == "wide":
            first_wide = (m.start(), m.end(), piece, src_rel)
        idx += 1
    out.append(html[last:])
    html2 = "".join(out)
    if "thumb" not in info:
        mm = re.search(r'assets/images/([^"\)]+\.(?:jpg|png|jpeg|webp))', html)
        if mm:
            info["thumb"] = "assets/images/" + mm.group(1)
    return html2, first_wide


HERO_FIG_RE = re.compile(r'<figure style="[^"]*" class="hr-fig hr-fig--wide">.*?</figure>', re.S)
EMPTY_SEC_RE = re.compile(r'<h2 id="([^"]*)">[^<]*(?:Images?|Photos?|Pictures?|Visuals?)[^<]*(?:<a class="headerlink".*?</a>)?</h2>\s*(?=<h2|<div class="footnote"|\Z)', re.S | re.I)


def lift_hero(html):
    """Lift the first wide photo into the story header (it keeps its caption, credit and lightbox).
    If that leaves an "Images" section empty, drop the empty heading and report its id so the rail can skip it."""
    m = HERO_FIG_RE.search(html)
    if not m:
        return html, None, []
    fig = m.group(0).replace("hr-fig hr-fig--wide", "hr-fig hr-fig--hero", 1)
    html = html[:m.start()] + html[m.end():]
    removed = []
    for em in list(EMPTY_SEC_RE.finditer(html)):
        removed.append(em.group(1))
    html = EMPTY_SEC_RE.sub("", html)
    return html, fig, removed


# ---------------------------------------------------------------- blockquotes / flags / footnotes
BQ_RE = re.compile(r"<blockquote>(.*?)</blockquote>", re.S)


def process_quotes(html, info):
    quotes = []

    def is_attr(p):
        return bool(re.match(r"\s*(—|&mdash;|–)\s*", p))

    def one(ps):
        """Render one quote group (paragraphs, optionally ending with an attribution)."""
        attr = ps[-1] if len(ps) >= 2 and is_attr(ps[-1]) else None
        body = []
        for k, p in enumerate(ps):
            if attr is not None and k == len(ps) - 1:
                body.append('<p class="hr-quote__by">' + p + "</p>")
            else:
                body.append("<p>" + p + "</p>")
        qt = clean_inline(ps[0])
        if 70 <= len(qt) <= 300 and attr:
            sm = re.search(r"<strong>(.*?)</strong>", attr, re.S)
            who = text_of(sm.group(1)) if sm else None
            ctx = clean_inline(re.sub(r"<strong>.*?</strong>", "", attr, count=1, flags=re.S))
            ctx = re.sub(r"^[\s,.:;—–-]+", "", ctx)
            ctx = re.split(r"\.\s", ctx, maxsplit=1)[0].rstrip(".")
            if who:
                quotes.append({"text": qt, "who": who, "ctx": truncate(ctx, 90)})
        return '<blockquote class="hr-quote%s">%s</blockquote>' % (" hr-quote--by" if attr else "", "\n".join(body))

    def sub(m):
        inner = m.group(1)
        if re.search(r"<(?!/?p[ >])(?!/?(?:em|strong|a|sup|span|br|i|b|code)[ >/])", inner):
            return '<blockquote class="hr-quote">%s</blockquote>' % inner
        ps = re.findall(r"<p>(.*?)</p>", inner, re.S)
        if sum(1 for p in ps if is_attr(p)) >= 2:
            groups, cur = [], []
            for p in ps:
                cur.append(p)
                if is_attr(p):
                    groups.append(cur)
                    cur = []
            if cur:
                groups.append(cur)
            return "\n".join(one(g) for g in groups)
        return one(ps) if ps else m.group(0)

    html = BQ_RE.sub(sub, html)
    info["quotes"] = quotes
    return html


BLOCK_TAGS = {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "td", "th", "blockquote", "div", "figcaption", "figure", "ul", "ol", "tr", "br", "section", "dd", "dt"}


def smart_text(t, prev):
    """Typographic quotes for one text node. `prev` is the previous visible character (' ' at block starts)."""
    out = []
    n = len(t)
    for i, ch in enumerate(t):
        nxt = t[i + 1] if i + 1 < n else ""
        if ch == '"':
            ch = "\u201c" if (prev in " \t\n([{\u2014\u2013\u2018\u00a0/" or prev == "") else "\u201d"
        elif ch == "'":
            if prev.isalnum() and (nxt.isalpha() or nxt == "" or nxt in " .,;:!?)\u201d"):
                ch = "\u2019"
            elif nxt.isdigit():
                ch = "\u2019"
            elif prev in " \t\n([{\u2014\u2013\u201c\u00a0" or prev == "":
                ch = "\u2018"
            else:
                ch = "\u2019"
        out.append(ch)
        prev = ch
    return "".join(out), prev


def wrap_flags(html):
    parts = re.split(r"(<[^>]*>)", html)
    skip = 0
    prev = " "
    for i, p in enumerate(parts):
        if p.startswith("<"):
            t = re.match(r"</?\s*([a-zA-Z0-9]+)", p)
            if t:
                name = t.group(1).lower()
                if name in ("code", "pre", "script", "style", "textarea", "svg", "kbd"):
                    skip += -1 if p.startswith("</") else 1
                    skip = max(skip, 0)
                if name in BLOCK_TAGS:
                    prev = " "
            continue
        if skip:
            continue
        if p.strip():
            if not re.match(r"\s*https?://", p):
                p, prev = smart_text(p, prev)
            elif p:
                prev = p[-1]
        if "⚠" in p or "◐" in p:
            p = p.replace("⚠", '<span class="hr-flag hr-flag--conflict" title="Conflict: sources disagree">⚠</span>')
            p = p.replace("◐", '<span class="hr-flag hr-flag--single" title="Single-sourced so far">◐</span>')
        parts[i] = p
    return "".join(parts)


def label_footnotes(html):
    html = html.replace('<div class="footnote">', '<div class="footnote" id="hr-sources" role="doc-endnotes">', 1)
    return html


# ---------------------------------------------------------------- tables
ROW_RE = re.compile(r"<tr>(.*?)</tr>", re.S)
CELL_RE = re.compile(r"<t([dh])[^>]*>(.*?)</t[dh]>", re.S)


def table_rows(table_html):
    rows = []
    for r in ROW_RE.finditer(table_html):
        cells = [c.group(2).strip() for c in CELL_RE.finditer(r.group(1))]
        if cells:
            rows.append(cells)
    return rows


def timeline_html(html):
    m = re.search(r"<table>.*?</table>", html, re.S)
    if not m:
        return html, None
    rows = table_rows(m.group(0))
    if len(rows) < 3 or "year" not in text_of(rows[0][0]).lower():
        return html, None
    entries = []
    for cells in rows[1:]:
        if len(cells) < 2:
            continue
        ym = re.search(r"(1[89]\d\d)", text_of(cells[0]))
        if not ym:
            continue
        entries.append({"year": int(ym.group(1)), "label": cells[0], "event": cells[1],
                        "link": cells[2] if len(cells) > 2 else ""})
    entries.sort(key=lambda e: e["year"])
    decs = []
    for e in entries:
        d = e["year"] // 10 * 10
        if not decs or decs[-1][0] != d:
            decs.append((d, []))
        decs[-1][1].append(e)
    nav = '<nav class="hr-tl-nav" aria-label="Jump to a decade"><ul>' + "".join(
        f'<li><a href="#decade-{d}">{d}s<span>{len(es)}</span></a></li>' for d, es in decs) + "</ul></nav>"
    out = [nav, '<div class="hr-tl">']
    for d, es in decs:
        era = "e30" if d < 1950 else "e50" if d < 1960 else "e60" if d < 1970 else "e70" if d < 1980 else "e80"
        out.append(f'<section class="hr-tl-dec" data-era="{era}" id="decade-{d}"><h2 class="hr-tl-dec__h">{d}s</h2><ol class="hr-tl-list">')
        for e in es:
            flags = "⚠" in e["label"] or "⚠" in e["event"]
            lab = e["label"]
            link = e["link"]
            out.append(f'<li class="hr-tl-item{" hr-tl-item--flag" if flags else ""}"><span class="hr-tl-year">{lab}</span>'
                       f'<div class="hr-tl-card"><p class="hr-tl-event">{e["event"]}</p>'
                       f'<p class="hr-tl-src">{link}</p></div></li>')
        out.append("</ol></section>")
    out.append("</div>")
    return html[:m.start()] + "".join(out) + html[m.end():], {"entries": entries}


def index_html(html):
    m = re.search(r"<table>.*?</table>", html, re.S)
    if not m:
        return html
    rows = table_rows(m.group(0))
    if len(rows) < 12:
        return html
    head = re.search(r"<thead>.*?</thead>", m.group(0), re.S)
    body_rows = [r for r in ROW_RE.finditer(re.search(r"<tbody>.*?</tbody>", m.group(0), re.S).group(0))]
    out, letters, cur = [], [], None
    for r in body_rows:
        first = CELL_RE.search(r.group(1))
        if not first:
            continue
        ch = text_of(first.group(2))[:1].upper()
        ch = ch if ch.isalpha() else "#"
        if ch != cur:
            cur = ch
            letters.append(ch)
            out.append(f'<tr class="hr-letter" id="idx-{ch}"><th colspan="3" scope="colgroup">{ch}</th></tr>')
        out.append(r.group(0))
    jump = '<nav class="hr-az" aria-label="Jump to letter">' + "".join(f'<a href="#idx-{c}">{c}</a>' for c in letters) + "</nav>"
    table = '<table class="hr-index">' + (head.group(0) if head else "") + "<tbody>" + "\n".join(out) + "</tbody></table>"
    return html[:m.start()] + jump + table + html[m.end():]


def _identity_cells(html):
    def tr_sub(m):
        tr = m.group(0)
        cells = list(re.finditer(r"<td>(.*?)</td>", tr, re.S))
        if len(cells) >= 6:
            last = cells[-1]
            t = text_of(last.group(1)).lower()
            cls = "hr-id--ok" if t.startswith("confirmed") else "hr-id--maybe" if t.startswith("name match") else "hr-id--other"
            tr = tr[:last.start()] + f'<td class="hr-id {cls}"><span>{last.group(1)}</span></td>' + tr[last.end():]
        return tr
    return re.sub(r"<tr>.*?</tr>", tr_sub, html, flags=re.S)


# ---------------------------------------------------------------- era heuristic
def guess_era(html):
    body = re.sub(r'<div class="footnote".*', "", html, flags=re.S)
    t = text_of(body)
    ys = [int(y) for y in re.findall(r"\b(19[2-9]\d)\b", t) if 1925 <= int(y) <= 1995]
    if len(ys) < 3:
        return None
    med = statistics.median(ys)
    return "e30" if med < 1950 else "e50" if med < 1960 else "e60" if med < 1970 else "e70" if med < 1980 else "e80"


BAD_BLURB = re.compile(r"copyright|rights-restricted|licen[sc]e|linked rather than|we link to|public domain|creative commons|image credits", re.I)


def pick_blurb(html):
    """First readable sentence-ish of the story: a top-level paragraph, else the first list item, never a credits note."""
    body = re.sub(r'<div class="footnote".*', "", html, flags=re.S)
    body = re.sub(r"<figure.*?</figure>", "", body, flags=re.S)
    body = re.sub(r"<div class=\"admonition.*?</div>", "", body, flags=re.S)
    cands = []
    pm = TopLevelP(body)
    pm.min_len = 60
    # collect every long top-level paragraph, not only the first
    class All(TopLevelP):
        def handle_endtag(self, tag):
            if tag in self.BLOCKS:
                self.depth = max(0, self.depth - 1)
            elif tag == "p" and self.in_p:
                self.in_p = False
                if len(self.p_text.strip()) >= self.min_len:
                    cands.append(self.p_start)

        def handle_starttag(self, tag, attrs):
            if tag in self.BLOCKS:
                self.depth += 1
            elif tag == "p" and self.depth == 0:
                self.in_p, self.p_start, self.p_text = True, self._off(), ""
    a = All(body)
    a.min_len = 60
    try:
        a.feed(body)
    except Exception:
        pass
    for off in cands:
        pe = body.find("</p>", off)
        t = clean_inline(body[off:pe])
        if not BAD_BLURB.search(t):
            return truncate(t, 175)
    for lm in re.finditer(r"<li>(.*?)</li>", body, re.S):
        t = clean_inline(lm.group(1))
        if len(t) >= 60 and not BAD_BLURB.search(t):
            return truncate(t, 175)
    return ""


# ---------------------------------------------------------------- hook entry points
def on_config(config):
    try:
        import PIL  # noqa: F401
        SITE["thumbs_enabled"] = True
    except Exception:
        SITE["thumbs_enabled"] = False
    INFO.clear()
    return config


def page_kind(page):
    u = page.file.src_uri
    if u == "index.md":
        return "home"
    if u.startswith(REF_PAGES):
        return "ref"
    if page.file.name == "index" and u.count("/") == 1 and page.parent is not None:
        return "section"
    return "story"


def on_page_markdown(markdown, page, config, files):
    """Read-only: harvest the newest "Next breadcrumbs" bullets of the Research Trail for the home page."""
    if page.file.src_uri == "research-trail.md":
        m = re.search(r"^## Next breadcrumbs[^\n]*\n(.*?)(?=^## )", markdown, re.S | re.M)
        leads = []
        if m:
            for line in m.group(1).splitlines():
                if not line.startswith("- "):
                    continue
                t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", line[2:])
                t = re.sub(r"[*_`]", "", t)
                lm = re.match(r"([^:]{3,60}):\s*(.+)", t)
                if lm and not lm.group(1).lower().startswith("carry"):
                    leads.append({"label": lm.group(1).strip(), "text": truncate(lm.group(2).strip(), 140)})
        hm = re.search(r"^## Next breadcrumbs \(([^)]*)\)", markdown, re.M)
        SITE["leads"] = leads[:4]
        SITE["leads_round"] = hm.group(1) if hm else ""
    return markdown


def on_page_content(html, page, config, files):
    src = page.file.src_uri
    info = {"src": src, "kind": page_kind(page), "url": page.url}
    INFO[src] = info
    meta = page.meta or {}
    # some plugins (glightbox) hand over a full-document wrapper; peel it so our block-level regexes see clean content
    html = re.sub(r"^\s*<html><head></head><body>", "", html)
    html = re.sub(r"</body></html>\s*$", "", html)

    if info["kind"] == "home":
        # keep slider placeholder; peel intro (before) and afterword (after) for the template
        ph = "<!-- hr:highlights -->"
        if ph in html:
            before, after = html.split(ph, 1)
            info["home_intro"], info["home_after"] = before.strip(), after.strip()
            return ph
        info["home_intro"], info["home_after"] = html, ""
        return ""

    # H1 -> headline
    m = re.match(r"\s*<h1 id=\"[^\"]*\">(.*?)</h1>", html, re.S)
    if m:
        title_html = re.sub(r'<a class="headerlink".*?</a>', "", m.group(1), flags=re.S).strip()
        title_html = wrap_flags(title_html)
        info["title_html"] = title_html
        info["title"] = text_of(title_html)
        html = html[m.end():]
    else:
        info["title"] = page.title
        info["title_html"] = htmlmod.escape(page.title or "")

    html, rec = parse_record(html)
    info["record"] = rec
    html, _ = process_figures(html, page, config, info)
    if info["kind"] in ("story", "ref") and not meta.get("no_hero"):
        html, hero, removed = lift_hero(html)
        info["hero"] = hero
        info["removed_ids"] = removed
    html = process_quotes(html, info)
    html = wrap_flags(html)
    html = mark_lede(html) if info["kind"] in ("story",) else html
    html = label_footnotes(html)

    if src == "reference/timeline.md":
        html, tl = timeline_html(html)
        info["timeline"] = tl
    elif src.startswith("reference/index-"):
        html = index_html(html)
    html = _identity_cells(html) if "<th>Identity</th>" in html else html

    # stats / blurb / era
    body_no_fn = re.sub(r'<div class="footnote".*', "", html, flags=re.S)
    words = len(text_of(body_no_fn).split())
    info["words"] = words
    info["minutes"] = max(1, round(words / 230))
    info["fn"] = len(re.findall(r'<li id="fn:', html))
    info["images"] = len(re.findall(r"<figure", html))
    info["blurb"] = truncate(str(meta["summary"]).strip(), 240) if meta.get("summary") else pick_blurb(html)
    info["margin"] = bool(re.search(r"hr-fig--(plate|tall|small|wide)", html)) or src.startswith("voices/")
    era = FRONT_ERA.get(str(meta.get("era", "")).strip().lower()) if meta.get("era") else None
    yrs = meta.get("years")
    if not era and isinstance(yrs, list) and len(yrs) == 2 and all(isinstance(y, int) for y in yrs):
        mid = (yrs[0] + yrs[1]) // 2
        era = FRONT_ERA.get(f"{max(1930, min(1990, mid // 10 * 10))}s")
    info["era_explicit"] = bool(era)
    info["era"] = era or (guess_era(html) if info["kind"] in ("story",) else None)
    info["deck"] = meta.get("deck")
    info["region"] = meta.get("region")
    cities, states = meta.get("cities") or [], meta.get("states") or []
    info["region_label"] = (cities[0] if len(cities) == 1 else ", ".join(states[:2]) if states else
                            (meta.get("region") if meta.get("region") not in (None, "National") else None))
    info["summary"] = str(meta.get("summary") or "").strip() or None
    info["eras_list"] = [str(e) for e in (meta.get("eras") or [])]
    info["tags"] = [str(t) for t in (meta.get("tags") or [])]
    info["place"] = info["region_label"]
    info["years"] = yrs if isinstance(yrs, list) else None
    html = wrap_end_sections(html, info)
    info["links"] = []
    base = page.url
    for hm in re.finditer(r'<a [^>]*href="([^"#?]+)(?:#[^"]*)?"', html):
        info["links"].append(hm.group(1))
    return html


# ---------------------------------------------------------------- end-of-story sections
OQ_RE = re.compile(r'(<h2 id="open-questions-disputed-details">.*?</h2>)(.*?)(?=<h2 |<div class="footnote"|\Z)', re.S)
SRC_H_RE = re.compile(r'<h2 id="sources">.*?</h2>\s*(?=<div class="footnote")', re.S)


def wrap_end_sections(html, info):
    """Open questions -> a distinct, collapsible end section; sources -> a collapsible ledger (open by default,
    JS folds it on phones). Headings keep their ids so every existing link still lands."""
    m = OQ_RE.search(html)
    info["oq_count"] = 0
    if m:
        n = len(re.findall(r'class="hr-q-anchor"', m.group(2))) or len(re.findall(r"<li", m.group(2)))
        info["oq_count"] = n
        cnt = f'<span class="hr-oq__count">{n} item{"s" if n != 1 else ""}</span>' if n else ""
        block = (f'<details class="hr-oq" data-hr-oq><summary class="hr-oq__sum">{m.group(1)}{cnt}'
                 f'<span class="hr-oq__hint" aria-hidden="true">Show</span></summary><div class="hr-oq__body">{m.group(2)}</div></details>')
        html = html[:m.start()] + block + html[m.end():]
    fm = re.search(r'<div class="footnote" id="hr-sources"', html)
    if fm:
        hm = SRC_H_RE.search(html)
        start = hm.start() if hm and hm.end() == fm.start() else fm.start()
        head = hm.group(0) if hm and hm.end() == fm.start() else ""
        tail = html[start + len(head):]
        n = len(re.findall(r'<li id="fn:', tail))
        title = re.sub(r'<a class="headerlink".*?</a>', "", head, flags=re.S) if head else ""
        ttl = text_of(title) or "Sources & notes"
        hid = 'id="sources"' if head else 'id="hr-sources-h"'
        html = (html[:start] + f'<details class="hr-src" open data-hr-src><summary class="hr-src__sum"><h2 {hid}>{htmlmod.escape(ttl)}</h2>'
                f'<span class="hr-src__count">{n} note{"s" if n != 1 else ""}</span><span class="hr-oq__hint" aria-hidden="true">Show</span></summary>'
                + tail + "</details>")
    return html


# ---------------------------------------------------------------- site-wide assembly
def resolve(href, page_url):
    if re.match(r"^[a-z]+:", href) or href.startswith("/"):
        return None
    parts = [p for p in (page_url or "").split("/") if p]
    for seg in href.split("/"):
        if seg == "..":
            if parts:
                parts.pop()
        elif seg and seg != ".":
            parts.append(seg)
    return "/".join(parts) + "/" if parts else ""


def thumb_for(info):
    t = info.get("thumb")
    if not t:
        return None
    if SITE.get("thumbs_enabled") and t.startswith("assets/images/"):
        return thumb_name(t)
    return t


def card(page, info):
    return {"title": info.get("title") or page.title, "url": page.url, "blurb": info.get("blurb", ""),
            "thumb": thumb_for(info), "level": (info.get("record") or {}).get("level"),
            "conf": (info.get("record") or {}).get("conf_word"), "era": info.get("era"),
            "grass": bool((info.get("record") or {}).get("grassroots")), "minutes": info.get("minutes"),
            "dept": info.get("dept_title"), "kind": info.get("kind"), "summary": info.get("summary"),
            "eras": info.get("eras_list") or [], "place": info.get("place"), "region": info.get("region"),
            "tags": info.get("tags") or [], "years": info.get("years"),
            "plate": Path(info.get("thumb") or "").name.startswith(("patent-", "loc-haer"))}


def nav_pages(nav):
    return [p for p in nav.pages]


def top_items(nav):
    return list(nav.items)


def section_pages(item):
    out = []
    if getattr(item, "is_page", False):
        return [item]
    for ch in item.children:
        out.extend(section_pages(ch))
    return out


def subgroup_of(item):
    """Map each page under a top-level section to its sub-group title (nested nav section), or None."""
    out = {}
    if getattr(item, "is_page", False):
        return out
    for ch in item.children:
        if not getattr(ch, "is_page", False):
            for p in section_pages(ch):
                out[p.file.src_uri] = ch.title
    return out


def build_site(nav, config):
    pages = {p.url: p for p in nav.pages}
    # department assignment
    depts = []
    n = 0
    for item in top_items(nav):
        if getattr(item, "is_page", False):
            ps = [item]
            idx = item
        else:
            ps = section_pages(item)
            idx = next((p for p in ps if p.is_index), ps[0] if ps else None)
        if idx is None:
            continue
        slug = Path(idx.file.src_uri).parts[0] if "/" in idx.file.src_uri else Path(idx.file.src_uri).stem
        if idx.file.src_uri != "index.md":
            n += 1
        icon, blurb = DEPT.get(slug, ("book", ""))
        kids = [p for p in ps if not p.is_index]
        groups = subgroup_of(item)
        for p in ps:
            if p.file.src_uri in INFO:
                INFO[p.file.src_uri]["group"] = groups.get(p.file.src_uri)
        d = {"title": item.title, "url": idx.url, "slug": slug, "icon": icon, "num": n, "blurb": blurb,
             "count": len(kids), "is_section": not getattr(item, "is_page", False), "pages": ps, "idx": idx}
        depts.append(d)
        for p in ps:
            i = INFO.get(p.file.src_uri)
            if i is not None:
                i["dept"] = d
                i["dept_title"] = d["title"]
    # fill blurb fallback from index page
    for d in depts:
        ii = INFO.get(d["idx"].file.src_uri, {})
        if not d["blurb"]:
            d["blurb"] = ii.get("blurb", "")
        d["thumb"] = None
    # section index era = modal era of children; thumbs = first child thumb
    for d in depts:
        ers = [INFO[p.file.src_uri].get("era") for p in d["pages"] if p.file.src_uri in INFO and not p.is_index]
        ers = [e for e in ers if e]
        if ers:
            mode = max(set(ers), key=ers.count)
            INFO[d["idx"].file.src_uri]["era"] = INFO[d["idx"].file.src_uri].get("era") or mode
        for p in ([] if d["slug"] in NO_THUMB else d["pages"]):
            t = thumb_for(INFO.get(p.file.src_uri, {}))
            if t:
                d["thumb"] = t
                break
    SITE["depts"] = depts
    # backlinks
    inbound = {}
    outbound = {}
    by_src_all = {p.file.src_uri: p for p in nav.pages}
    SITE["metas"] = {p.file.src_uri: (p.meta or {}) for p in nav.pages if (p.meta or {}).get("summary")}
    for p in nav.pages:
        i = INFO.get(p.file.src_uri)
        if not i:
            continue
        seen = {}
        for h in i.get("links", []):
            u = resolve(h, p.url)
            if u in pages and u != p.url:
                seen[u] = seen.get(u, 0) + 1
        for t in (p.meta or {}).get("_autolinks") or []:
            tp = by_src_all.get(t)
            if tp is not None and tp.url != p.url:
                seen[tp.url] = seen.get(tp.url, 0) + 1
        outbound[p.url] = seen
        for u, c in seen.items():
            inbound.setdefault(u, {})[p.url] = c
    SITE["inbound"], SITE["outbound"] = inbound, outbound
    SITE["pages"] = pages
    # stats
    tot_fn = sum(i.get("fn", 0) for i in INFO.values())
    tot_img = len({t for i in INFO.values() for t in [i.get("thumb")] if t})
    imgs = len(list((Path(config["docs_dir"]) / "assets" / "images").glob("*")))
    stories = [p for p in nav.pages if INFO.get(p.file.src_uri, {}).get("kind") == "story"
               and not p.is_index]
    SITE["stats"] = {"stories": len(stories), "images": imgs, "sources": tot_fn,
                     "departments": len([d for d in depts if d["is_section"]]),
                     "words": sum(i.get("words", 0) for i in INFO.values())}
    # eras strip
    era_pages = {}
    for p in nav.pages:
        if p.file.src_uri.startswith("eras/") and not p.is_index:
            m = re.match(r"eras/(19\d0)s", p.file.src_uri)
            if m:
                dec = int(m.group(1))
                key = "e30" if dec < 1950 else "e50" if dec < 1960 else "e60" if dec < 1970 else "e70" if dec < 1980 else "e80"
                era_pages.setdefault(key, []).append(p)
    SITE["era_pages"] = era_pages
    # timeline ribbon
    tl = (INFO.get("reference/timeline.md") or {}).get("timeline")
    ribbon = []
    if tl:
        es = tl["entries"]
        want = 11
        step = max(1, len(es) // want)
        picked = es[::step][:want]
        for e in picked:
            ribbon.append({"year": e["label"], "text": truncate(clean_inline(e["event"]), 80),
                           "link": re.search(r'href="([^"]+)"', e["link"]).group(1) if re.search(r'href="([^"]+)"', e["link"]) else None})
    SITE["ribbon"] = ribbon
    # notebook leads (Research Trail "Next breadcrumbs")
    SITE["built"] = datetime.date.today()


def slugify(t):
    return re.sub(r"[^a-z0-9]+", "-", str(t).lower()).strip("-")


TAG_LABEL = lambda t: str(t).replace("-", " ")


def rel_url(target, here):
    import posixpath
    t = posixpath.relpath(target or ".", here.rstrip("/") or ".") if target else "."
    return t + "/" if target and target.endswith("/") and not t.endswith("/") else t


def grassroots_table(pages, here):
    """HTML table of every page whose article record carries the Grassroots badge, grouped by department."""
    rows = []
    for u, p in pages.items():
        i = INFO.get(p.file.src_uri) or {}
        if (i.get("record") or {}).get("grassroots") and not p.is_index:
            d = i.get("dept")
            rows.append(((d or {}).get("num", 99), i.get("title") or p.title, p, d, i))
    rows.sort(key=lambda r: (r[0], r[1].lower()))
    out = ['<table><thead><tr><th>Article</th><th>Department</th><th>What it adds</th></tr></thead><tbody>']
    for _, title, p, d, i in rows:
        blurb = htmlmod.escape(truncate(i.get("blurb") or "", 170))
        dept = f'<a href="{rel_url(d["url"], here)}">{htmlmod.escape(d["title"])}</a>' if d else ""
        out.append(f'<tr><td><a href="{rel_url(p.url, here)}">{htmlmod.escape(title)}</a></td><td>{dept}</td><td>{blurb}</td></tr>')
    out.append("</tbody></table>")
    out.append(f'<p><small>{len(rows)} pages carry the badge. This list is built from the article records, so it is always current.</small></p>')
    return "".join(out)


def on_page_context(context, page, config, nav):
    if "depts" not in SITE or SITE.get("_nav_id") != id(nav):
        SITE.pop("depts", None)
        build_site(nav, config)
        SITE["_nav_id"] = id(nav)
        seed_date(config)
    info = INFO.get(page.file.src_uri, {"kind": "story"})
    kind = info.get("kind", "story")
    hr = dict(info)
    hr["era_label"] = ERA_SHORT.get(info.get("era"))
    hr["thumb_url"] = thumb_for(info)
    d = info.get("dept")
    hr["dept"] = d
    pages, inbound, outbound = SITE["pages"], SITE["inbound"], SITE["outbound"]

    def cardf(url):
        p = pages[url]
        return card(p, INFO.get(p.file.src_uri, {}))

    if kind in ("story", "ref") and page.url in pages:
        # siblings in department
        if d and d["is_section"]:
            sibs = [p for p in d["pages"] if not p.is_index]
            grp = info.get("group")
            if grp:
                gs = [p for p in sibs if INFO.get(p.file.src_uri, {}).get("group") == grp]
                if len(gs) > 1:
                    sibs = gs
            hr["series"] = grp or d["title"]
            ids = [p.url for p in sibs]
            if page.url in ids:
                hr["series_pos"] = (ids.index(page.url) + 1, len(ids))
            if page.url in ids:
                i = ids.index(page.url)
                hr["prev"] = card(sibs[i - 1], INFO.get(sibs[i - 1].file.src_uri, {})) if i > 0 else None
                hr["next"] = card(sibs[i + 1], INFO.get(sibs[i + 1].file.src_uri, {})) if i + 1 < len(sibs) else None
        # related
        score = {}
        for u, c in outbound.get(page.url, {}).items():
            score[u] = score.get(u, 0) + c
        for u, c in inbound.get(page.url, {}).items():
            score[u] = score.get(u, 0) + 1.5 * c
        for u in list(score):
            ii = INFO.get(pages[u].file.src_uri, {})
            if ii.get("kind") not in ("story",) and not (ii.get("kind") == "section"):
                del score[u]
        # front-matter overlap: shared people, companies, clubs, strips, places, tags; explicit `related` counts most
        metas = SITE.get("metas") or {}
        me = metas.get(page.file.src_uri)
        if me:
            by_src = {p.file.src_uri: p for p in pages.values()}
            for rel_src in (me.get("related") or []):
                rp = by_src.get(rel_src)
                if rp is not None:
                    score[rp.url] = score.get(rp.url, 0) + 6
            for rel_src, m in metas.items():
                if rel_src == page.file.src_uri or rel_src not in by_src:
                    continue
                ov, _ = related_lib.overlap(me, m)
                if ov > 1.0:
                    u = by_src[rel_src].url
                    score[u] = score.get(u, 0) + ov
        both = set(outbound.get(page.url, {})) & set(inbound.get(page.url, {}))
        ranked = sorted(score, key=lambda u: (-(u in both), -score[u], u))
        skip = {(hr.get("prev") or {}).get("url"), (hr.get("next") or {}).get("url")}
        rel = [u for u in ranked if u not in skip and not pages[u].is_index][:4]
        hr["related"] = [cardf(u) for u in rel]
        # "Mentioned in": every story that links here (by hand or by a first-mention link)
        bl = []
        for u in sorted(inbound.get(page.url, {}), key=lambda u: (INFO.get(pages[u].file.src_uri, {}).get("title") or "")):
            ii = INFO.get(pages[u].file.src_uri, {})
            if ii.get("kind") == "story" and not pages[u].is_index:
                bl.append({"title": ii.get("title") or pages[u].title, "url": u, "dept": ii.get("dept_title")})
        hr["backlinks"] = bl
        # Quick answers whose full story (first) or related link (after) is this page
        if "qa_by_page" not in SITE:
            main, also = {}, {}
            try:
                qdata = quick_answers_lib.load()
            except Exception:  # pragma: no cover - the quick answers hook reports data errors
                qdata = {}
            for _t, q in quick_answers_lib.questions(qdata):
                main.setdefault(quick_answers_lib.split_link(q["link"])[0], []).append(q)
                for l in q.get("also") or []:
                    also.setdefault(quick_answers_lib.split_link(l)[0], []).append(q)
            SITE["qa_by_page"] = (main, also)
        qmain, qalso = SITE["qa_by_page"]
        src = page.file.src_uri
        qs = list(qmain.get(src, []))
        qs += [q for q in qalso.get(src, []) if q not in qs]
        hr["quick"] = [{"q": q["q"], "id": q["id"]} for q in qs[:4]]
    if kind == "section" and d:
        kids = [p for p in d["pages"] if not p.is_index]
        hr["children"] = [card(p, INFO.get(p.file.src_uri, {})) for p in kids]
        # sub-groups from nested nav sections (e.g. Places: Regional scenes / Cruising & hangouts)
        cg = []
        for p, c in zip(kids, hr["children"]):
            g = INFO.get(p.file.src_uri, {}).get("group")
            if not cg or cg[-1]["title"] != g:
                cg.append({"title": g, "cards": []})
            cg[-1]["cards"].append(c)
        hr["child_groups"] = cg if any(x["title"] for x in cg) else []
    if kind == "home":
        by_src = {p.file.src_uri: p for p in pages.values()}
        want = (page.meta or {}).get("featured") or SITE.get("featured_src")
        fp = by_src.get(want)
        if fp is not None:
            fc = card(fp, INFO.get(fp.file.src_uri, {}))
            fi = INFO.get(fp.file.src_uri, {})
            fc["era_label"] = ERA_SHORT.get(fi.get("era"))
            fc["minutes"] = fi.get("minutes")
            hr["featured"] = fc
        places = []
        for dd in SITE["depts"]:
            if dd["slug"] == "places":
                for p in dd["pages"]:
                    if not p.is_index:
                        places.append(card(p, INFO.get(p.file.src_uri, {})))
        hr["places"] = places
        qs = SITE.get("quotes") or []
        if qs:
            q = qs[(SITE["seed"] * 7) % len(qs)]
            qp = by_src.get(q["src"])
            hr["overheard"] = dict(q, text=smart_text(q["text"], " ")[0], ctx=smart_text(q.get("ctx", ""), " ")[0], url=qp.url if qp else None,
                                   page_title=(INFO.get(q["src"], {}).get("title")))
        hr["intro_html"] = info.get("home_intro", "")
        hr["after_html"] = info.get("home_after", "")
    if page.file.src_uri == "voices/index.md":
        qs = SITE.get("quotes") or []
        by_src = {p.file.src_uri: p for p in pages.values()}
        picks = []
        if qs:
            n = len(qs)
            for k in range(3):
                q = qs[(SITE["seed"] * 5 + k * (n // 3 + 1)) % n]
                qp = by_src.get(q["src"])
                picks.append(dict(q, text=smart_text(q["text"], " ")[0], ctx=smart_text(q.get("ctx", ""), " ")[0], url=qp.url if qp else None,
                                  page_title=INFO.get(q["src"], {}).get("title")))
        hr["picks"] = picks
    if page.file.src_uri == "reference/grassroots-sources.md" and "<!-- hr:grassroots-articles -->" in (page.content or ""):
        page.content = page.content.replace("<!-- hr:grassroots-articles -->", grassroots_table(pages, page.url))
    # breadcrumbs: Home > department > series (sub-group of the department)
    crumbs = []
    if kind != "home":
        crumbs.append({"t": "Home", "u": ""})
        if d and d.get("url") != page.url:
            crumbs.append({"t": d["title"], "u": d["url"]})
            if info.get("group"):
                crumbs.append({"t": info["group"], "u": d["url"] + "#" + slugify(info["group"])})
    hr["crumbs"] = crumbs
    # the summary standfirst is rendered in the story head; the search index has already read it from the content
    if page.content and '<p class="hr-summary"' in page.content:
        page.content = re.sub(r'<p class="hr-summary"[^>]*>.*?</p>\s*', "", page.content, count=1, flags=re.S)
    hr["standfirst"] = (page.meta or {}).get("deck") or info.get("summary")
    toc_n = 0
    if page.toc:
        items = page.toc.items[0].children if page.toc.items and page.toc.items[0].level == 1 else page.toc.items
        skip_ids = set(info.get("removed_ids") or []) | {"open-questions-disputed-details", "sources"}
        toc_n = len([t for t in items if t.id not in skip_ids])
    hr["toc_n"] = toc_n
    hr["long"] = kind == "ref" or (toc_n >= 3 and (info.get("words") or 0) >= 900)
    # hubs: intro paragraph(s) on top, metadata cards with filters, then the editor's listing folded underneath
    if kind == "section" and page.content:
        c = page.content
        mm = re.search(r"<p><strong>|<h2[ >]|<h3[ >]|<ul[ >]|<ol[ >]|<table|<div class=\"admonition", c)
        if mm:
            hr["hub_intro"], hr["hub_listing"] = c[:mm.start()], c[mm.start():]
        else:
            hr["hub_intro"], hr["hub_listing"] = c, ""
        page.content = ""
        facets = {"eras": {}, "regions": {}, "tags": {}}
        for ch in hr.get("children") or []:
            for e in ch.get("eras") or []:
                facets["eras"][e] = facets["eras"].get(e, 0) + 1
            if ch.get("region"):
                facets["regions"][ch["region"]] = facets["regions"].get(ch["region"], 0) + 1
            for t in ch.get("tags") or []:
                facets["tags"][t] = facets["tags"].get(t, 0) + 1
        hr["facets"] = {
            "eras": sorted(facets["eras"].items()),
            "regions": sorted(facets["regions"].items(), key=lambda x: (-x[1], x[0])),
            "tags": sorted([x for x in facets["tags"].items() if x[1] >= 2], key=lambda x: (-x[1], x[0]))[:14],
        }
        for g in hr.get("child_groups") or []:
            g["id"] = slugify(g["title"]) if g.get("title") else None
    context["hr"] = hr
    context["hr_site"] = SITE
    return context


def on_template_context(context, template_name, config):
    if template_name == "404.html":
        context["hr"] = {"kind": "404", "title": "Page not found"}
    return context


def seed_date(config):
    today = datetime.date.today().toordinal()
    SITE["seed"] = today
    # story of the day / overheard
    cands = []
    for src, i in INFO.items():
        if i.get("kind") != "story" or not i.get("thumb") or not i.get("blurb"):
            continue
        lvl = (i.get("record") or {}).get("level")
        if lvl == "low":
            continue
        cands.append(src)
    cands.sort()
    SITE["featured_src"] = cands[today % len(cands)] if cands else None
    qs = []
    for src, i in sorted(INFO.items()):
        if src.startswith("voices/") and not src.endswith("index.md"):
            for q in i.get("quotes", []):
                if q.get("who"):
                    qs.append(dict(q, src=src))
    SITE["quotes"] = qs


def write_cards_json(config):
    import json
    out = {}
    for src, i in INFO.items():
        if i.get("kind") not in ("story", "section", "ref"):
            continue
        u = i.get("url")
        if u is None:
            continue
        out[u] = {"s": i.get("summary") or i.get("blurb") or "", "d": i.get("dept_title") or "",
                  "e": i.get("eras_list") or [], "p": i.get("place") or "", "k": i.get("kind")}
    f = Path(config["site_dir"]) / "assets" / "hr-cards.json"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))


def on_post_build(config):
    write_cards_json(config)
    if not SITE.get("thumbs_enabled"):
        return
    try:
        from PIL import Image, ImageOps
    except Exception:
        return
    src_dir = Path(config["docs_dir"]) / "assets" / "images"
    out_dir = Path(config["site_dir"]) / "assets" / "thumbs"
    cache = Path(config["docs_dir"]).parent / ".cache" / "hr-thumbs"
    out_dir.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)
    n = 0
    for f in sorted(src_dir.iterdir()):
        if f.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
            continue
        dst = out_dir / (f.stem + ".jpg")
        c = cache / (f.stem + ".jpg")
        try:
            if not c.exists() or c.stat().st_mtime < f.stat().st_mtime:
                im = Image.open(f)
                im = ImageOps.exif_transpose(im)
                if im.mode in ("RGBA", "LA", "P"):
                    bg = Image.new("RGB", im.size, (255, 255, 255))
                    im = im.convert("RGBA")
                    bg.paste(im, mask=im.split()[-1])
                    im = bg
                im = im.convert("RGB")
                im.thumbnail((720, 720 * 3), Image.LANCZOS)
                im.save(c, "JPEG", quality=74, optimize=True, progressive=True)
            dst.write_bytes(c.read_bytes())
            n += 1
        except Exception as e:  # pragma: no cover
            log.warning("thumb failed for %s: %s", f.name, e)
    log.info("design: wrote %d thumbnails", n)
