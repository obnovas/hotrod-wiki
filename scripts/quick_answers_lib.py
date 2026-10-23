"""Quick Answers: data, validation and rendering for docs/reference/quick-answers.md.

Data: docs/data/quick_answers.yml (themes -> questions). Used by hooks/quick_answers_hook.py (renders the page and
fails the build on any error), hooks/design_hook.py (the "Quick answers" links in an article's Keep reading area)
and scripts/check_quick_answers.py (the same check from the command line).

Checks, per question:
  * id is a unique, stable anchor; q, a and link are present; a has 1-3 sentences
  * link and every `also` page exist, with their #anchors
  * every number in the answer appears in the linked article (same rule as the Highlights)
  * an answer carrying ⚠ or ◐ names a `flag`: an Open questions item (page.md#q-N, whose inline marker still
    exists and is of the same kind) or a ⚠/◐ heading inside that page's Open questions section. When the article
    resolves the item and removes it, the build fails until the answer drops its flag. A `flag` on an answer with
    no ⚠/◐ is also an error.
"""
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from articles_lib import DOCS, split_front  # noqa: E402
import highlights_lib as hl  # noqa: E402

DATA = DOCS / "data" / "quick_answers.yml"
PAGE = "reference/quick-answers.md"
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
OQ_H = "## Open questions & disputed details"
KIND = {"⚠": ("Sources disagree", "Open question"), "◐": ("Single source so far", "Open question")}


def load(path=DATA):
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def questions(data):
    for t in data.get("themes") or []:
        for q in t.get("questions") or []:
            yield t, q


def anchors(md):
    """Heading slugs, explicit { #id } attributes and id="..." anchors."""
    out = set(hl.headings(md))
    for m in re.finditer(r"^#{1,6}\s+(.*?)\s*$", md, re.M):
        h = re.sub(r"\s*\{[^}]*\}\s*$", "", m.group(1))
        out.add(hl.slugify(re.sub(r"[*_`]", "", h)))
    out.update(re.findall(r"\{[^}]*#([\w-]+)[^}]*\}", md))
    out.update(re.findall(r'id="([\w-]+)"', md))
    return out


def split_link(link):
    path, _, frag = str(link).partition("#")
    return path, frag


def page_title(rel):
    p = DOCS / rel
    meta, body = split_front(p.read_text(encoding="utf-8"))
    if meta.get("title"):
        return str(meta["title"])
    m = re.search(r"^# (.+)$", body, re.M)
    return re.sub(r"[*_`]", "", m.group(1)).strip() if m else rel


def link_label(link, main):
    """A related link's text: the page title, or the section heading when it points into the full-story page."""
    path, frag = split_link(link)
    if frag and path == split_link(main)[0]:
        md = (DOCS / path).read_text(encoding="utf-8")
        for m in re.finditer(r"^#{2,6}\s+(.*?)\s*$", md, re.M):
            if frag in anchors(m.group(0)):
                return re.sub(r"\s*\{[^}]*\}\s*$", "", re.sub(r"[*_`]", "", m.group(1))).strip()
    return page_title(path)


def sentences(t):
    t = re.sub(r"\b(?:Mr|Mrs|Dr|St|Jr|Sr|U\.S|Mo|Ill|Pa|Oct|Aug|Jan|Feb|Mar|Apr|Sept|Nov|Dec|vs|in|No|[A-Z])\.", "·", t)
    return [s for s in re.split(r"(?<=[.!?])[\"”)]?\s+(?=[A-Z\"“*])", t.strip()) if s]


def _check_flag(qid, a, flag, E):
    if flag == "legend":
        return
    marks = set(re.findall(r"[⚠◐]", a))
    if not marks and flag:
        E(f"has a flag ({flag}) but no ⚠ or ◐ in the answer; drop the flag or restore the mark")
        return
    if marks and not flag:
        E("carries ⚠/◐ but names no `flag` (the Open questions item it points to)")
        return
    if not marks:
        return
    if "see Open questions" not in a:
        E("a flagged answer must say 'see Open questions' after its ⚠/◐")
    path, frag = split_link(flag)
    p = DOCS / path
    if not p.exists() or not frag:
        E(f"flag '{flag}' must be page.md#q-N or page.md#heading in an existing page")
        return
    md = p.read_text(encoding="utf-8")
    if OQ_H not in md:
        E(f"flag '{flag}': {path} has no Open questions section any more; the doubt was resolved, so drop the ⚠/◐")
        return
    oq = md.split(OQ_H, 1)[1]
    oq = re.split(r"^## (?!#)", oq, flags=re.M)[0] if re.search(r"^## ", oq, re.M) else oq
    m = re.match(r"q-(\d+)$", frag)
    if m:
        n = m.group(1)
        if f'id="q-{n}"' not in md:
            E(f"flag '{flag}': item q-{n} is gone from {path} (resolved?). Drop the ⚠/◐ here and update the answer")
            return
        mk = re.search(rf'<sup class="hr-q" id="qr-{n}"><a href="#q-{n}" title="([^"]*)">([⚠◐?]?)', md)
        if not mk:
            E(f"flag '{flag}': the inline marker qr-{n} is gone from {path} (resolved?). Drop the ⚠/◐ here")
            return
        for k in marks:
            if not mk.group(1).startswith(KIND[k]):
                E(f"flag '{flag}': the answer says {k} but the article marks it '{mk.group(1).split(':')[0]}'")
    else:
        hit = None
        for hm in re.finditer(r"^#{3,6}\s+(.*?)\s*$", oq, re.M):
            h = hm.group(1)
            if frag in anchors(hm.group(0)):
                hit = h
        if hit is None:
            E(f"flag '{flag}': no heading '#{frag}' inside the Open questions section of {path} (resolved?). Drop the ⚠/◐")
        elif not re.search(r"[⚠◐]|[Dd]isput|[Dd]iscrepanc|[Cc]onflict", hit):
            E(f"flag '{flag}': the heading '{hit}' no longer marks a dispute; drop the ⚠/◐")


def validate(data):
    errors = []
    seen = set()
    tids = set()
    for t in data.get("themes") or []:
        if not ID_RE.match(str(t.get("id", ""))) or not t.get("title"):
            errors.append(f"theme {t.get('id')!r}: needs a lowercase id and a title")
        if t.get("id") in tids:
            errors.append(f"theme {t.get('id')}: duplicate id")
        tids.add(t.get("id"))
    for t, q in questions(data):
        qid = q.get("id", "?")
        E = lambda m: errors.append(f"[{qid}] {m}")  # noqa: E731
        for k in ("id", "q", "a", "link"):
            if not q.get(k):
                E(f"missing '{k}'")
        if not q.get("id") or not q.get("a") or not q.get("link"):
            continue
        if not ID_RE.match(qid):
            E("id must be lowercase letters, digits and hyphens")
        if qid in seen or qid in tids:
            E("duplicate id")
        seen.add(qid)
        a = " ".join(str(q["a"]).split())
        n = len(sentences(a))
        if n > 3:
            E(f"answer has {n} sentences (limit 3)")
        links = [q["link"]] + list(q.get("also") or [])
        if len(q.get("also") or []) > 2:
            E("at most two `also` links")
        body = None
        for i, l in enumerate(links):
            path, frag = split_link(l)
            p = DOCS / path
            if not path.endswith(".md") or not p.exists():
                E(f"link target not found: docs/{path}")
                continue
            md = p.read_text(encoding="utf-8")
            if frag and frag not in anchors(md):
                E(f"anchor '#{frag}' not found in {path}")
            if i == 0:
                body = hl.norm(split_front(md)[1])
        if body is not None:
            for num in re.findall(r"\d[\d,.]*\d|\d", a):
                v = num.rstrip(".,")
                if v not in body and v.replace(",", "") not in body.replace(",", ""):
                    E(f"number '{v}' does not appear in {split_link(q['link'])[0]}")
        _check_flag(qid, a, q.get("flag"), E)
    return errors


def rel_href(target, here=PAGE):
    """Markdown link from `here` to `target` (both docs-relative .md paths, target may carry #frag)."""
    path, frag = split_link(target)
    up = "../" * here.count("/")
    return up + path + (f"#{frag}" if frag else "")


def render(data, here=PAGE):
    """The page body: a jump index, then one section per theme and one H3 per question (each its own search entry)."""
    out = []
    themes = data.get("themes") or []
    total = sum(len(t.get("questions") or []) for t in themes)
    out.append(f'<p class="hr-qa-count">{total} questions in {len(themes)} themes. Each answer links to its full story.</p>\n')
    out.append('<nav class="hr-qa-index" aria-label="Questions by theme" markdown>\n')
    for t in themes:
        qs = t.get("questions") or []
        out.append(f'<details class="hr-qa-theme" markdown>\n<summary><span>{t["title"]}</span> <span class="hr-qa-n">{len(qs)}</span></summary>\n')
        out.append("\n".join(f"- [{q['q']}](#{q['id']})" for q in qs) + f"\n- [All of {t['title'].lower()} →](#{t['id']})\n")
        out.append("</details>\n")
    out.append("</nav>\n")
    for t in themes:
        out.append(f"\n## {t['title']} {{ #{t['id']} }}\n")
        for q in t.get("questions") or []:
            a = " ".join(str(q["a"]).split())
            if q.get("flag"):
                a = a.replace("see Open questions", f"see [Open questions]({rel_href(q['flag'], here)})", 1)
            out.append(f"\n### {q['q']} {{ #{q['id']} .hr-qa-q }}\n\n{a}\n")
            more = f"[Full story: {page_title(split_link(q['link'])[0])} →]({rel_href(q['link'], here)})"
            also = [f"[{link_label(l, q['link'])}]({rel_href(l, here)})" for l in (q.get("also") or [])]
            line = more + (" · Related: " + ", ".join(also) if also else "")
            out.append(f'<p class="hr-qa-more" markdown>{line}</p>\n')
    return "\n".join(out)


def by_page(data):
    """docs-relative page -> [(question, url fragment)] for every answer whose full story is that page."""
    out = {}
    for t, q in questions(data):
        path, _ = split_link(q["link"])
        out.setdefault(path, []).append(q)
    return out


if __name__ == "__main__":
    errs = validate(load())
    for e in errs:
        print("ERROR:", e)
    print(f"{sum(1 for _ in questions(load()))} quick answers checked, {len(errs)} errors")
    sys.exit(1 if errs else 0)
