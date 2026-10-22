#!/usr/bin/env python3
"""Move every 'unknown' (⚠ conflict notes, ◐ single-source notes, 'From the detective's notebook' asides,
'what we could not find', open questions, next leads) out of the running prose into ONE section at the bottom
of each article, '## Open questions & disputed details', leaving a small superscript marker at the claim.

  python scripts/move_unknowns.py docs/places/modesto.md [...]      # rewrite in place
  python scripts/move_unknowns.py --all                              # every article page
  python scripts/move_unknowns.py --check [--all|files]              # exit 1 if a page still has a mid-prose unknown

Rules (see docs/style-guide.md, "Keep the detective's notebook at the back"):
  * The Article record box and pull-quote admonitions are left alone.
  * A flag symbol stays in the body as the marker (<sup class="hr-q">), linked to its item; the item text never
    repeats the symbol, so ⚠/◐ counts are unchanged.
  * Whole notebook paragraphs, flagged bullets and sections whose heading is an unknown (⚠, 'detective's
    notebook', 'what to doubt', 'still missing', 'next leads', ...) move as a block; moved section headings
    become H3 (same text, so existing #anchors keep working).
  * Footnote references travel with the words they support.
"""
import re, sys
from pathlib import Path

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None

ROOT = Path(__file__).resolve().parent.parent
SECTION = "## Open questions & disputed details"
SKIP_PREFIX = ("reference/", "bibliography.md", "research-trail.md", "highlights-archive.md", "taxonomy.md",
               "contribute.md", "style-guide.md", "index.md", "about/")
UNKNOWN_HEAD = re.compile(r"⚠|◐|detective.s notebook|what to doubt|could not|couldn.t|still missing|caveat|"
                          r"discrepanc|conflicts? with the record|open question|what the sources (?:do not|don.t)|"
                          r"next leads?|unresolved|disputed|what we (?:do not|don.t) know|unknowns", re.I)
NOTEBOOK_START = re.compile(r"^(?:[⚠◐]\s*)?(?:\*\*|\*)?\s*(?:[⚠◐]\s*)?(?:From the detective.s notebook|What we could not find|"
                            r"We could not find|Still missing|Open question)", re.I)
TRAILING_HEAD = re.compile(r"^## +(Images|Visual references|Sources?\b|Sources and notes|Notes on sources|Image)", re.I)
FN_DEF = re.compile(r"^\[\^[^\]]+\]:")
FLAG = re.compile(r"[⚠◐]")
LABEL = {"⚠": "Disputed.", "◐": "Single source so far.", None: "Open question."}
TITLE = {"⚠": "Sources disagree", "◐": "Single source so far", None: "Open question"}


OVR = {"keep": [], "split": [], "move": []}
CUR = {"rel": ""}


def load_overrides():
    f = ROOT / "scripts/unknowns_overrides.yml"
    if yaml and f.exists():
        d = yaml.safe_load(f.read_text()) or {}
        for k in OVR:
            OVR[k] = d.get(k) or []


def ovr(kind_, text):
    for page, phrase in OVR[kind_]:
        if page == CUR["rel"] and phrase in text:
            return phrase
    return None


def is_article(rel):
    return rel.endswith(".md") and not rel.startswith(SKIP_PREFIX) and not rel.endswith("/index.md")


# ----------------------------------------------------------------------------- block splitter
def split_front(text):
    m = re.match(r"^---\n.*?\n---\n", text, re.S)
    return (text[:m.end()], text[m.end():]) if m else ("", text)


def blocks_of(body):
    """List of blocks; each block is a list of lines. Blank lines separate blocks except inside indented
    continuations (admonitions, list items), <figure>/<div> html and tables."""
    lines = body.split("\n")
    out, cur, in_html = [], [], 0
    i = 0
    while i < len(lines):
        l = lines[i]
        if in_html:
            cur.append(l)
            if re.search(r"</(figure|div|details)>\s*$", l):
                in_html -= 1
            i += 1
            continue
        if re.match(r"^<(figure|div|details)\b", l) and not re.search(r"</(figure|div|details)>\s*$", l):
            if cur:
                out.append(cur); cur = []
            cur = [l]; in_html = 1; i += 1
            continue
        if l.strip() == "":
            # keep indented continuations of admonitions / list items in the same block
            j = i
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if cur and j < len(lines) and lines[j].startswith(("    ", "\t")) and (
                    cur[0].startswith(("!!!", "???", "- ", "* ")) or re.match(r"^\d+\. ", cur[0])):
                cur.extend(lines[i:j]); i = j
                continue
            if cur:
                out.append(cur); cur = []
            i += 1
            continue
        if l.startswith("#") and cur:
            out.append(cur); cur = []
        cur.append(l)
        if l.startswith("#"):
            out.append(cur); cur = []
        i += 1
    if cur:
        out.append(cur)
    return out


def kind(b):
    f = b[0]
    if f.startswith("#"):
        return "head"
    if f.startswith("!!!") or f.startswith("???"):
        return "adm"
    if f.startswith("<"):
        return "html"
    if f.startswith("|"):
        return "table"
    if f.startswith(">"):
        return "quote"
    if FN_DEF.match(f):
        return "fn"
    if re.match(r"^\s*([-*]|\d+\.) ", f):
        return "list"
    return "para"


def strip_md(t):
    t = re.sub(r"\[\^[^\]]+\]", "", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    return re.sub(r"[*_`]", "", t).strip()


# ----------------------------------------------------------------------------- transformer
class Mover:
    def __init__(self):
        self.items = []   # (n, symbol, title, [lines]) ; title only for moved sections

    def new(self, sym, lines, label=None, heading=None):
        n = len(self.items) + 1
        self.items.append({"n": n, "sym": sym, "lines": lines, "heading": heading, "label": label})
        return n

    @staticmethod
    def marker(n, sym):
        shown = sym or "?"
        tip = {"⚠": "Sources disagree: see Open questions", "◐": "Single source so far: see Open questions"}.get(
            sym, "Open question: see the bottom of the page")
        return f'<sup class="hr-q" id="qr-{n}"><a href="#q-{n}" title="{tip}">{shown}</a></sup>'


def leading_flag(text):
    m = re.match(r"^(\s*(?:[-*] |\d+\. )?)(\*\*|\*)?\s*([⚠◐])\s*", text)
    return m


def light(t):
    t = re.sub(r'<sup class="hr-q".*?</sup>', "", t)
    t = re.sub(r"\[\^[^\]]+\]", "", t)
    return re.sub(r"\s+", " ", t)


def _claim(before, after):
    """The sentence the flag sits in (plain text, no quotes), for a 'marked in place' item."""
    b = FLAG.sub("", light(before))
    a = FLAG.sub("", light(after))
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(*])", b)
    head = parts[-1] if parts else b
    if len(head) < 25 and len(parts) > 1:
        head = parts[-2] + " " + head
    a = a.lstrip()
    tail = re.split(r"(?<=[.!?])\s", a, maxsplit=1)[0] if a and not re.match(r"^[A-Z\"“*]", a) else ""
    c = (head + (" " + tail if tail else "")).strip()
    c = re.sub(r"^\s*(?:>\s*)?(?:[-*]|\d+\.)?\s+", "", c)
    c = re.sub(r"\(\s*[,;]?\s*\)", "", c)
    c = re.sub(r"\s+", " ", c).strip(" ,;:(")
    nq = len(re.findall(r'["“”]', c))
    if nq % 2 or c.count("**") % 2 or len(re.findall(r"(?<!\*)\*(?!\*)", c)) % 2 or c.count("[") != c.count("]") or len(c) > 220 or len(c) < 30 or c.count("(") != c.count(")"):
        return None
    return c


def _in_place(sym, before, after, mv):
    c = _claim(before, after)
    lab = "Disputed:" if sym == "⚠" else "Single source so far:"
    where = f" in *{CUR['sec']}*" if CUR.get("sec") else " near the top of the story"
    if not c:
        what = "sources disagree on the point" if sym == "⚠" else "the point rests on one source so far:"
        txt = (f"the marked point{where}. The sources disagree; the details are in the text and its notes."
               if sym == "⚠" else f"the marked point{where} rests on one source so far.")
        n = mv.new(sym, [txt[0].upper() + txt[1:]], lab)
    else:
        n = mv.new(sym, [c if re.search(r"[.!?][\"”*)]*$", c) else c + "."], lab)
    return n


def process_inline(line, mv, table=False):
    """Handle flags inside a paragraph/bullet/attribution line. Returns new line."""
    line = re.sub(r"\*\*([⚠◐])\*\*", r"\1", line)
    line = re.sub(r"\*\*([⚠◐])\s+(?=\S)", r"\1 **", line)
    out = ""
    pos = 0
    while True:
        m = FLAG.search(line, pos)
        if not m:
            out += line[pos:]
            return out
        sym = m.group(0)
        before = line[pos:m.start()]
        rest = line[m.end():]
        if before.count("[") > before.count("]") or re.search(r'<sup class="hr-q"[^>]*><a[^>]*>$', line[:m.start()]):
            out += before + sym; pos = m.end(); continue
        if table:
            cell_start = line.rfind("|", 0, m.start()) + 1
            cell_end = line.find("|", m.end())
            cell_end = len(line) if cell_end < 0 else cell_end
            first = strip_md(line.strip("|").split("|")[0])
            cell = light((line[cell_start:m.start()] + line[m.end():cell_end]).strip())
            cell = re.sub(r"\s+", " ", cell)
            n = mv.new(sym, [f"In the table, row *{first}*: {cell}" if cell else f"In the table, row *{first}*."], "Disputed:" if sym == "⚠" else "Single source so far:")
            out += before + mv.marker(n, sym); pos = m.end(); continue
        whole_before = out + before
        t = rest.lstrip()
        if before.endswith("(") and rest.startswith(")"):      # legend symbol "(⚠)": leave it
            out += before + sym; pos = m.end(); continue
        # (⚠ explanation) -> move the parenthetical
        pm = re.match(r"\s*([^()]*)\)", rest)
        if before.rstrip().endswith("(") and pm and len(pm.group(1).split()) >= 3:
            inner = pm.group(1).strip()
            b2 = before.rstrip()[:-1].rstrip()
            n = mv.new(sym, [inner[:1].upper() + inner[1:]])
            out += b2 + mv.marker(n, sym)
            pos = m.end() + pm.end()
            continue
        open_paren = whole_before.count("(") > whole_before.count(")")
        sentence_start = (before.strip() == "" or re.search(r"[.!?\])”\"]\s*$|\*\*\s*$|:\s*$", before.rstrip()) is not None)
        if (open_paren or t == "" or t.startswith("[^") or re.fullmatch(r"[\s*_.,;:)\]]*", t)
                or not sentence_start or not re.match(r"(\*\*|\*|[A-Z\"“(\[])", t)):
            n = _in_place(sym, whole_before, rest, mv)
            out += before.rstrip() + mv.marker(n, sym) + ("" if re.match(r"[\s.,;:)\]\[]", rest[:1] or " ") else " ")
            pos = m.end()
            continue
        # italic note right after the flag: move just the italic span (+ footnotes)
        im = re.match(r"\s*(\*(?!\*)[^*]+\*(?:\[\^[^\]]+\])*[.,;]?)", rest)
        if im and len(im.group(1).split()) >= 4:
            n = mv.new(sym, [im.group(1).strip()])
            out += before.rstrip() + mv.marker(n, sym)
            pos = m.end() + im.end()
            continue
        # explanation follows the flag: move flag..end of block (or up to an override phrase where the story resumes)
        sp = ovr("split", rest)
        if sp:
            k = rest.index(sp)
            n = mv.new(sym, [rest[:k].strip()])
            out += before.rstrip() + mv.marker(n, sym) + " "
            line = rest[k:]; pos = 0
            continue
        # move only the explanatory sentences; narrative that resumes stays in the story
        sents = split_sents(rest)
        k = 0
        label = False
        for si, (a, b_) in enumerate(sents):
            raw = rest[a:b_].strip()
            st = strip_md(raw).strip()
            if si == 0 and re.fullmatch(r"\*\*[^*]{1,80}\*\*", re.sub(r"\[\^[^\]]+\]", "", raw)):
                label = True; k = b_; continue
            if ((si == 0 or (si == 1 and label)) and expl_first(st)) or (si > 0 and expl_next(st)):
                k = b_
            else:
                break
        if label and k == sents[0][1] and len(sents) > 1:
            k = sents[1][1]           # a label always takes its first sentence with it
        if k == 0:
            n = _in_place(sym, whole_before, rest, mv)
            out += before.rstrip() + mv.marker(n, sym) + " "
            line = rest.lstrip(); pos = 0
            continue
        mt = _strip_notebook(rest[:k].strip())
        n = mv.new(sym, [mt[:1].upper() + mt[1:]])
        out += before.rstrip() + mv.marker(n, sym)
        if rest[k:].strip():
            out += " "
            line = rest[k:].lstrip(); pos = 0
            continue
        return out


OPEN_EXPL = re.compile(r"^(this|that|these|those|we|our|it is|it's|its own|single|one source|only|unverified|not |no |none|unsourced|self|claim|other|others|some |sources|the sources|neither|both|a claim|needs?|treat|see |compare|possibl|probabl|likely|unclear|unknown|conflict|disputed|but |either|an interested|interested|the figures?|the date|the year|the spelling|spelling|a later|later accounts|earlier|until |whether|if |which|why|how |who |what |where |when )", re.I)
BROAD_EXPL = re.compile(r"\b(says?|said|gives?|calls?|puts?|per|according|claims?|sources?|spell(?:s|ed|ing)?|misprint|typo|verif\w*|confirm\w*|unclear|unknown|disagree\w*|differ\w*|conflict\w*|we|our|not|no|never|probably|perhaps|only|interested party|figures are|own account|recollection|memory|detective|notebook|vs|versus|as reported|as printed|as given|reportedly|hearsay|forum|summary|snippet)\b", re.I)


def expl_first(s):
    return bool(OPEN_EXPL.search(s) or BROAD_EXPL.search(s))


def expl_next(s):
    return bool(OPEN_EXPL.search(s))


def split_sents(t):
    """[(start, end)] spans of sentences in t, footnote refs kept with their sentence."""
    spans = []
    a = 0
    for m in re.finditer(r'[.!?]["”)]?\*{0,2}(?:\[\^[^\]]+\])*(?=\s+["“*(\[]?[A-Z])', t):
        if re.search(r"\b(?:[A-Z]|Mr|Mrs|Dr|St|Jr|Sr|Maj|Lt|Gen|Sgt|Capt|Col|No|vs|Co|Inc|Mt|Ft|Ave|So|Cal|U\.S|Pa|Mo|Ill|Ind|Mich|Calif|Wash|Okla|Tenn|Jan|Feb|Mar|Apr|Aug|Sept|Oct|Nov|Dec)\.$", t[:m.start() + 1]):
            continue
        spans.append((a, m.end()))
        a = m.end()
        while a < len(t) and t[a].isspace():
            a += 1
    if a < len(t):
        spans.append((a, len(t)))
    return spans


def transform(text):
    front, body = split_front(text)
    if SECTION in body:
        return text, 0
    bl = blocks_of(body)
    mv = Mover()
    PENDING.clear()
    CUR["sec"] = ""

    class Keep(list):
        def append(self, b):
            super().append(_flush_pending(b))
    keep = Keep()      # list of blocks (lists of lines) for body
    i = 0
    seen_h1 = False
    while i < len(bl):
        b = bl[i]; k = kind(b)
        first = b[0]
        if k == "head":
            CUR["sec"] = strip_md(FLAG.sub("", first.lstrip("#"))).strip() if not first.startswith("# ") else ""
        # ---------- whole section whose heading is an unknown
        hl = len(re.match(r"^#*", first).group(0))
        if k == "head" and hl >= 2 and UNKNOWN_HEAD.search(first) and not TRAILING_HEAD.match(first):
            j = i + 1
            while j < len(bl) and not (kind(bl[j]) == "head" and len(re.match(r"^#*", bl[j][0]).group(0)) <= hl) and kind(bl[j]) != "fn":
                j += 1
            heading = first[hl:].strip()
            sym = None
            hm = FLAG.search(heading)
            content = []
            for bb in bl[i + 1:j]:
                if kind(bb) == "head":
                    bb = ["####" + bb[0].lstrip("#")]   # sub-heads become H4 inside the moved section
                elif kind(bb) in ("para", "list") and re.search(r"detective.s notebook", "\n".join(bb), re.I):
                    bb = _strip_notebook("\n".join(bb)).split("\n")
                content.append(bb)
            heading = re.sub(r"^From the detective.s notebook\s*[:.]?\s*", "", heading, flags=re.I)
            heading = heading.strip() or "More from the notebook"
            heading = heading[:1].upper() + heading[1:]
            n = mv.new(None, content, heading="### " + heading)
            _attach_marker(keep, mv.marker(n, None))
            i = j
            continue
        # ---------- notebook paragraph / paragraph or bullet that starts with a flag
        if k in ("para", "list") and k != "head":
            new_lines = []
            moved_any = False
            jt = "\n".join(b)
            narrative_nb = (re.match(r"^\W*From the detective.s notebook", first, re.I) and not FLAG.search(jt)
                            and not re.search(r"could not|couldn.t|not found|have not found|haven.t found|unknown|no source|unclear|not (?:yet )?(?:seen|read|identified)|we do not know|we don.t know", jt, re.I)
                            and not ovr("move", jt))
            if k == "para" and (narrative_nb or ((NOTEBOOK_START.match(first) or _starts_flag_shortlabel(first)) and ovr("keep", jt))):
                txt = _strip_notebook("\n".join(b))
                lf = leading_flag(txt)
                if lf and lf.group(3):          # kept paragraph that opened with a flag: marker after its first sentence
                    sym = lf.group(3)
                    txt = txt[:lf.start(3)] + txt[lf.end():]
                    k1 = split_sents(txt)[0][1]
                    n = _in_place(sym, txt[:k1], "", mv)
                    txt = txt[:k1] + mv.marker(n, sym) + txt[k1:]
                keep.append([process_inline(x, mv) for x in txt.split("\n")])
                i += 1
                continue
            if k == "para" and (NOTEBOOK_START.match(first) or _starts_flag_shortlabel(first)):
                sym = None
                txt = _strip_notebook("\n".join(b))
                lf = leading_flag(txt)
                if lf and lf.group(3):
                    sym = lf.group(3)
                    txt = txt[:lf.start(3)] + txt[lf.end():]
                elif _starts_flag_shortlabel(txt):
                    fm = FLAG.search(txt)
                    sym = fm.group(0)
                    txt = txt[:fm.start()].rstrip() + " " + txt[fm.end():].lstrip()
                n = mv.new(sym, txt.split("\n"))
                _attach_marker(keep, mv.marker(n, sym))
                i += 1
                continue
            if k == "list":
                # split into items; move items that start with a flag/notebook phrase
                items = _list_items(b)
                kept_items = []
                for it in items:
                    head_txt = re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", it[0])
                    if it[0].startswith((" ", "\t")):
                        kept_items.append(it); continue
                    if NOTEBOOK_START.match(head_txt) or _starts_flag_shortlabel(head_txt):
                        lf = leading_flag(head_txt)
                        sym = lf.group(3) if lf else None
                        txt = "\n".join([head_txt] + [x.strip() for x in it[1:]])
                        if lf:
                            txt = txt[:lf.start(3)] + txt[lf.end():]
                        txt = _strip_notebook(txt)
                        n = mv.new(sym, txt.split("\n"))
                        if kept_items:
                            kept_items[-1][-1] = kept_items[-1][-1] + mv.marker(n, sym)
                        else:
                            _attach_marker(keep, mv.marker(n, sym))
                        continue
                    kept_items.append([process_inline(x, mv) for x in it])
                if kept_items:
                    keep.append([x for it in kept_items for x in it])
                i += 1
                continue
            keep.append([process_inline(x, mv) for x in b])
            i += 1
            continue
        if k == "quote":
            keep.append([process_inline(x, mv) if x.lstrip("> ").startswith(("—", "-- ", "– ")) or FLAG.search(x) else x for x in b])
            i += 1; continue
        if k == "table":
            keep.append([process_inline(x, mv, table=True) if FLAG.search(x) else x for x in b])
            i += 1; continue
        keep.append(b)
        i += 1
    if PENDING:
        # nothing followed: put it on the last paragraph we kept
        for b in reversed(keep):
            if kind(b) in ("para", "list"):
                b[-1] = b[-1].rstrip() + "".join(PENDING); break
        PENDING.clear()
    if not mv.items:
        return text, 0
    # where to insert: before the first trailing section (Images, Visual references, Sources) or footnotes
    ins = len(keep)
    for idx, b in enumerate(keep):
        if kind(b) == "fn" or (kind(b) == "head" and TRAILING_HEAD.match(b[0])):
            ins = idx
            break
    sec = [[SECTION], ["*From the detective's notebook: where the sources disagree, where we have only one, and what we are still looking for. Each item links back to its place in the story.*"]]
    for it in mv.items:
        n, sym = it["n"], it["sym"]
        back = f' <a class="hr-q-back" href="#qr-{n}" title="Back to the story">↩</a>'
        anchor = f'<a id="q-{n}" class="hr-q-anchor"></a>'
        if it["heading"]:
            sec.append([anchor])
            sec.append([it["heading"]])
            blocks = it["lines"]
            if blocks:
                last = blocks[-1]
                blocks = blocks[:-1] + [last[:-1] + [last[-1] + back]] if kind(last) in ("para", "list") else blocks + [[back.strip()]]
            sec.extend(blocks)
        else:
            lines = [l for l in it["lines"]]
            lab = it.get("label") or LABEL[sym]
            lines[0] = f'{anchor}**{lab}** ' + lines[0].lstrip()
            lines[-1] = lines[-1] + back
            sec.append(lines)
    keep = list(keep[:ins]) + sec + list(keep[ins:])
    new_body = "\n\n".join("\n".join(b) for b in keep) + "\n"
    return front + new_body, len(mv.items)


def _starts_flag_shortlabel(t):
    """'⚠ **...**', '**⚠ ...', '**Names:** ⚠ ...' (short label then flag)."""
    s = re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", t)
    if re.match(r"^(\*\*|\*)?\s*[⚠◐]", s):
        return True
    m = FLAG.search(s)
    return bool(m and m.start() < 40 and len(strip_md(s[:m.start()])) < 30 and s.startswith("**"))


def _strip_notebook(t):
    t = re.sub(r"From the detective.s notebook\s*[:.]?\s*", "", t, count=1, flags=re.I)
    t = t.strip()
    t = re.sub(r"^\*\*\*\*\s*", "", t)          # '**From...:** text' -> '**** text'
    t = re.sub(r"^\*\*\s+(?=\S)", "", t) if not re.match(r"^\*\*\s+\S.*?\*\*", t) else t   # '*From...:* text' -> '** text'
    t = re.sub(r"^\*\*\s*([⚠◐])\s*\*\*\s*", r"\1 ", t)    # '**⚠** text'
    t = re.sub(r"^\*\s+", "", t)
    t = t.strip()
    m = re.match(r"^((?:\*\*|\*)?\s*(?:[⚠◐]\s*)?(?:\*\*|\*)?\s*)([a-z])", t)
    if m:
        t = m.group(1) + m.group(2).upper() + t[m.end():]
    return t


def _list_items(b):
    items = []
    for l in b:
        if re.match(r"^(?:[-*]|\d+\.) ", l) or not items:
            items.append([l])
        else:
            items[-1].append(l)
    return items


PENDING = []


def _attach_marker(keep, mk):
    """Append a marker to the last prose line of the nearest preceding paragraph/list in the body; if the
    unknown sat right under a subhead, attach it to the next paragraph instead (never to a heading)."""
    for b in reversed(keep):
        k = kind(b)
        if k in ("para", "list"):
            b[-1] = b[-1].rstrip() + mk
            return
        if k == "head":
            break
    PENDING.append(mk)


def _flush_pending(b):
    if PENDING and kind(b) in ("para", "list"):
        b[-1] = b[-1].rstrip() + "".join(PENDING)
        PENDING.clear()
    return b


def check(text):
    front, body = split_front(text)
    body = body.split(SECTION)[0]
    bad = []
    for b in blocks_of(body):
        k = kind(b)
        if k in ("adm", "fn", "html"):
            continue
        for l in b:
            clean = re.sub(r'<sup class="hr-q".*?</sup>', "", l).replace("(⚠)", "").replace("(◐)", "")
            if FLAG.search(clean):
                bad.append(l[:120])
            elif re.search(r"detective.s notebook", clean, re.I) and k != "head":
                bad.append(l[:120])
    return bad


def main():
    load_overrides()
    args = sys.argv[1:]
    chk = "--check" in args
    args = [a for a in args if a != "--check"]
    if "--all" in args or not args:
        files = [p for p in sorted((ROOT / "docs").rglob("*.md")) if is_article(str(p.relative_to(ROOT / "docs")))]
    else:
        files = [Path(a).resolve() for a in args]
    rc = 0
    for f in files:
        t = f.read_text()
        if chk:
            bad = check(t)
            if bad:
                rc = 1
                print(f"{f.relative_to(ROOT)}: {len(bad)} unknown(s) still in the prose")
                for x in bad[:5]:
                    print("    ", x)
            continue
        CUR["rel"] = str(f.relative_to(ROOT / "docs"))
        nt, n = transform(t)
        if n:
            f.write_text(nt)
            print(f"{f.relative_to(ROOT)}: moved {n}")
    sys.exit(rc)


if __name__ == "__main__":
    main()
