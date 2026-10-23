"""Parse Open-questions items so checks can test each one.

An item starts at `<a id="q-N" class="hr-q-anchor"></a>` and runs to the end of its
paragraph. When the anchor stands alone before a heading, the item is the section that
heading opens (up to the next anchor or a heading of the same or higher level).
"""
import re

ANCHOR = re.compile(r'<a id="(q-\d+)" class="hr-q-anchor"></a>')
COLON_LABEL = re.compile(r'^\s*\*\*(?:Single source so far|Disputed|Open question|Sources disagree|Label)[^*]*:\*\*')
CITE = re.compile(r'\[\^[^\]]+\]|\]\([^)]*\.md(?:#[^)]*)?\)|\]\(<?https?://')
FORMAT = re.compile(r'^\*\*(?:Disputed|Single source so far|Open question)\.\*\* \*\*(?:[^*]|\*[^*]+\*)+?\?\*\*')
SECTION_HEAD = re.compile(r'^#{2,6} (.*?)\s*(?:\{[^}]*\})?\s*$', re.M)
LEADS = re.compile(r'^#{2,6} (?:Next leads|More from the notebook)\b', re.M)
URL = re.compile(r'https?://')


def items(text):
    out = []
    ms = list(ANCHOR.finditer(text))
    for i, m in enumerate(ms):
        end_next = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        rest = text[m.end():end_next]
        para = rest.split("\n\n")[0]
        body = para
        if not re.sub(r'<a class="hr-q-back".*?</a>', "", para).strip():
            h = re.match(r'\s*\n(#{2,6}) ', rest)
            if h:
                lvl = len(h.group(1))
                stop = re.search(r'\n#{2,%d} ' % lvl, rest[h.end():])
                body = rest[: h.end() + stop.start()] if stop else rest
                stop2 = re.search(r'\n\[\^[^\]]+\]: ', body)
                if stop2:
                    body = body[: stop2.start()]
        out.append((m.group(1), body.strip()))
    return out


def problems(text, voices=False):
    bad = []
    for q, body in items(text):
        if LEADS.match(body):
            continue  # a section-style item that lists research leads, not a claim
        if COLON_LABEL.match(body):
            bad.append(f"{q}: label ends with a colon; write '**Label.** **Question?**'")
        elif body.startswith("#"):
            head = SECTION_HEAD.match(body).group(1).replace("⚠", "").replace("◐", "").strip()
            if not head.endswith("?"):
                bad.append(f"{q}: a section-style item's heading must be the question (keep the old anchor with {{ #old-slug }})")
        elif not FORMAT.match(body):
            bad.append(f"{q}: start with '**Disputed.**', '**Single source so far.**' or '**Open question.**', then the question in bold, e.g. '**When did it open?**'")
        if not (CITE.search(body) or (voices and URL.search(body))):
            bad.append(f"{q}: no citation (footnote, wiki-page link{', or URL' if voices else ''})")
    return bad
