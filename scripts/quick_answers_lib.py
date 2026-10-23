"""Quick Answers: data, validation and rendering for docs/reference/quick-answers.md.

Data: docs/data/quick_answers.yml (themes -> questions). Used by hooks/quick_answers_hook.py (renders the page and
fails the build on any error), hooks/design_hook.py (the "Quick answers" links in an article's Keep reading area)
and scripts/check_quick_answers.py (the same check from the command line).

Checks, per question:
  * id is a unique, stable anchor; q, a and link are present; a has 1-3 sentences
  * link and every `also` page exist, with their #anchors
  * link is not a hub (index pages, `hub: true`): the Full story must state the facts
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


def oq_ref_kinds(ref):
    """Check one Open questions reference (page.md#q-N, or page.md#heading inside its Open questions section).
    Returns (kinds, errors): kinds is the set of marks the item stands for ({'⚠'}, {'◐'} or both for an open question)."""
    path, frag = split_link(ref)
    p = DOCS / path
    if not p.exists() or not frag:
        return set(), [f"'{ref}' must be page.md#q-N or page.md#heading in an existing page"]
    md = p.read_text(encoding="utf-8")
    if OQ_H not in md:
        return set(), [f"'{ref}': {path} has no Open questions section any more (resolved?)"]
    oq = md.split(OQ_H, 1)[1]
    oq = re.split(r"^## (?!#)", oq, flags=re.M)[0] if re.search(r"^## ", oq, re.M) else oq
    m = re.match(r"q-(\d+)$", frag)
    if m:
        n = m.group(1)
        if f'id="q-{n}"' not in md:
            return set(), [f"'{ref}': item q-{n} is gone from {path} (resolved?)"]
        mk = re.search(rf'<sup class="hr-q" id="qr-{n}"><a href="#q-{n}" title="([^"]*)"', md)
        if not mk:
            return set(), [f"'{ref}': the inline marker qr-{n} is gone from {path} (resolved?)"]
        t = mk.group(1)
        kinds = {k for k, starts in KIND.items() if t.startswith(starts[0])} or ({"⚠", "◐"} if t.startswith("Open question") else set())
        return kinds, []
    for hm in re.finditer(r"^#{3,6}\s+(.*?)\s*$", oq, re.M):
        if frag in anchors(hm.group(0)):
            h = hm.group(1)
            kinds = set(re.findall(r"[⚠◐]", h))
            if re.search(r"[Dd]isput|[Dd]iscrepanc|[Cc]onflict", h):
                kinds.add("⚠")
            if re.search(r"[Ss]ingle.source", h):
                kinds.add("◐")
            if not kinds:
                return set(), [f"'{ref}': the heading '{h}' no longer marks a dispute or a single source"]
            return kinds, []
    return set(), [f"'{ref}': no heading '#{frag}' inside the Open questions section of {path} (resolved?)"]


def flag_errors(marks, refs, what):
    """Marks (⚠/◐) claimed by `what` must be backed by open items of the same kind, and vice versa."""
    errs = []
    refs = [refs] if isinstance(refs, str) else list(refs or [])
    if not marks and refs:
        return [f"{what} names open-question items ({', '.join(refs)}) but carries no ⚠ or ◐; drop them or restore the mark"]
    if marks and not refs:
        return [f"{what} carries {''.join(sorted(marks))} but names no open-question item it stands on"]
    covered = set()
    for r in refs:
        kinds, e = oq_ref_kinds(r)
        if e:
            errs += [f"{what}: {x}. If the question was resolved, drop the ⚠/◐ here and update the text" for x in e]
            continue
        if not kinds & marks:
            errs.append(f"{what}: '{r}' is a {''.join(sorted(kinds))} item, but the text carries {''.join(sorted(marks))}")
        covered |= kinds
    if not errs:
        for k in marks - covered:
            errs.append(f"{what} carries {k} but none of its items ({', '.join(refs)}) is that kind")
    return errs


def _check_flag(qid, a, flag, E):
    if flag == "legend":
        return
    marks = set(re.findall(r"[⚠◐]", a))
    refs = [flag] if isinstance(flag, str) else list(flag or [])
    if marks and a.count("see Open questions") < max(1, len(refs)):
        E("each flagged ⚠/◐ must say 'see Open questions' (one per flag)")
    for e in flag_errors(marks, refs, "the answer"):
        E(e)


def is_hub(path, md=None):
    """A page that only points the way: the home page, a department or section index, or one whose front
    matter says `hub: true` (cruising-overview, regional-scenes). A Full story link must not land on one."""
    if path == "index.md" or path.endswith("/index.md"):
        return True
    if md is None:
        p = DOCS / path
        md = p.read_text(encoding="utf-8") if p.exists() else ""
    fm = split_front(md)[0]
    return bool(isinstance(fm, dict) and fm.get("hub"))


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
                if is_hub(path, md):
                    E(f"Full story link goes to a hub ({path}), which states no facts of its own; link the page that tells the story")
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
            fl = q.get("flag")
            for ref in ([fl] if isinstance(fl, str) else list(fl or [])):
                if ref != "legend":
                    a = a.replace("see Open questions", f"see [Open questions]({rel_href(ref, here)})\u200b", 1)
            a = a.replace("\u200b", "")
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
