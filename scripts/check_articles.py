#!/usr/bin/env python3
"""Build gate for article front matter, links and canonical facts.

    python scripts/check_articles.py          # report; exit 1 on any error
    python scripts/check_articles.py --orphans  # also list pages with few inbound links

Run automatically by hooks/articles_hook.py, so a failure here fails `mkdocs build`.
Schema: docs/reference/article-schema.md. Canonical facts: docs/data/canonical.yml."""
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from articles_lib import (DOCS, ROOT, ERAS, REGIONS, TAGS, REQUIRED, LISTS, KNOWN, DEPARTMENTS,  # noqa: E402
                          articles, split_front, plain, body_prose, load_canonical)
import quick_answers_lib  # noqa: E402  (shared open-question flag check)
import move_unknowns  # noqa: E402  (boilerplate open-question items)

try:
    from markdown.extensions.toc import slugify
except Exception:  # pragma: no cover
    def slugify(v, sep):
        v = re.sub(r"[^\w\s-]", "", v).strip().lower()
        return re.sub(r"[%s\s]+" % sep, sep, v)

SNIPPETS = ROOT / "snippets"
ABBR = r"(?:Mr|Mrs|Dr|St|Jr|Sr|Mt|Ft|No|vs|Co|Inc|Ave|Blvd|Rd|U\.S|D\.C|Pa|Mo|Ill|Ind|Mich|Calif|Wash|Okla|Tenn|Tex|Wis|Kan|Neb|Ore|Ark|Ala|Ga|Fla|Ariz|Colo|Minn|N\.Y|N\.J|N\.C|Jan|Feb|Mar|Apr|Aug|Sept|Oct|Nov|Dec|[A-Z])"


def anchors_of(body):
    out, seen = set(), defaultdict(int)
    for m in re.finditer(r"^(#{1,6})\s+(.+?)\s*$", body, re.M):
        h = m.group(2)
        idm = re.search(r"\{[^}]*#([\w-]+)[^}]*\}\s*$", h)
        if idm:
            out.add(idm.group(1))
            continue
        s = slugify(plain(re.sub(r"\{[^}]*\}\s*$", "", h)), "-")
        n = seen[s]
        seen[s] += 1
        out.add(s if n == 0 else f"{s}_{n}")
    out.update(re.findall(r'id="([\w-]+)"', body))
    out.update(re.findall(r"\{[^}]*#([\w-]+)[^}]*\}", body))
    return out


def sentences(t):
    t = re.sub(rf"\b{ABBR}\.", lambda m: m.group(0).replace(".", "·"), t)
    return [s for s in re.split(r"(?<=[.!?])[\"”]?\s+(?=[A-Z\"“])", t.strip()) if s]


def snippet_includes(body):
    return re.findall(r'^-{1,3}8<-{1,3}\s+"([^"]+)"', body, re.M)


def main():
    errors, warns = [], []
    canon = load_canonical()
    arts = articles()
    metas, bodies = {}, {}
    for rel in arts:
        meta, body = split_front((DOCS / rel).read_text())
        metas[rel], bodies[rel] = meta, body
    all_md = {str(p.relative_to(DOCS)) for p in DOCS.rglob("*.md")}
    anchor_cache = {}

    def anchors(rel):
        if rel not in anchor_cache:
            p = DOCS / rel
            anchor_cache[rel] = anchors_of(split_front(p.read_text())[1]) if p.exists() else set()
        return anchor_cache[rel]

    inbound = defaultdict(set)
    for rel in arts:
        meta, body = metas[rel], bodies[rel]
        E = lambda msg: errors.append(f"{rel}: {msg}")  # noqa: E731
        if not meta:
            E("no front matter")
            continue
        for k in REQUIRED:
            if meta.get(k) in (None, "", []) and not (k == "related" and meta.get(k) == []):
                E(f"missing required field '{k}'")
        for k in meta:
            if k not in KNOWN:
                E(f"unknown field '{k}' (see docs/reference/article-schema.md)")
        for k in LISTS:
            if k in meta and not (isinstance(meta[k], list) and all(isinstance(x, (str, int)) for x in meta[k])):
                E(f"'{k}' must be a list of strings")
        h1 = re.search(r"^# (.+)$", body, re.M)
        if not h1:
            E("no H1 headline")
        elif meta.get("title") and plain(meta["title"]) != plain(h1.group(1)):
            E(f"title does not match the H1 ('{plain(h1.group(1))}')")
        dept = rel.split("/")[0]
        if meta.get("department") != dept:
            E(f"department '{meta.get('department')}' should be '{dept}'")
        yrs = meta.get("years")
        if not (isinstance(yrs, list) and len(yrs) == 2 and all(isinstance(y, int) for y in yrs) and 1880 <= yrs[0] <= yrs[1] <= 2030):
            E("years must be [first, last] (integers)")
            yrs = None
        for e in meta.get("eras") or []:
            if e not in ERAS:
                E(f"unknown era '{e}' (use {ERAS[0]}…{ERAS[-1]})")
        if yrs and meta.get("eras"):
            want = {f"{d}s" for d in range(yrs[0] // 10 * 10, yrs[1] // 10 * 10 + 1, 10)}
            if not set(meta["eras"]) <= want:
                E(f"eras {meta['eras']} fall outside years {yrs}")
        if meta.get("region") and meta["region"] not in REGIONS:
            E(f"unknown region '{meta['region']}' (use one of {REGIONS})")
        for t in meta.get("tags") or []:
            if t not in TAGS:
                E(f"unknown tag '{t}' (add it to scripts/articles_lib.py TAGS and the schema page first)")
        for r in meta.get("related") or []:
            if r == rel:
                E("related lists the page itself")
            elif r not in metas:
                E(f"related '{r}' is not an article")
        for c in meta.get("canonical_for") or []:
            if c not in canon:
                E(f"canonical_for '{c}' is not in docs/data/canonical.yml")
            elif canon[c].get("page") != rel:
                E(f"canonical_for '{c}' but canonical.yml names {canon[c].get('page')}")
        # summary: standalone, 1-2 sentences, grounded
        s = str(meta.get("summary") or "")
        if s:
            if len(s) < 40 or len(s) > 330:
                E(f"summary is {len(s)} characters (40–330)")
            if len(sentences(s)) > 2:
                E("summary has more than two sentences")
            if re.search(r"[⚠◐]|\[\^|<sup", s):
                E("summary must not carry flags, footnotes or markers")
            prose = plain(body_prose(body))
            for n in re.findall(r"\d[\d,.–-]*\d|\d", s):
                n = n.rstrip(".,")
                dec = re.fullmatch(r"(1[89]\d|20\d)0", n)
                if n in prose:
                    continue
                if dec and re.search(rf"\b{dec.group(1)}\d", prose) and re.search(rf"{n}s", s):
                    continue
                if "–" in n and all(x in prose for x in n.split("–")):
                    continue
                E(f"summary number '{n}' does not appear in the article")
        # links
        for m in re.finditer(r"\]\(([^)\s]+?)(?:\s+\"[^\"]*\")?\)", body):
            href = m.group(1)
            if re.match(r"^[a-z]+:", href) or href.startswith("#") and not href[1:]:
                continue
            path, _, frag = href.partition("#")
            if not path:
                if frag and frag not in anchors(rel):
                    E(f"link to missing anchor '#{frag}'")
                continue
            if not path.endswith(".md"):
                continue
            tgt = str((DOCS / rel).parent.joinpath(path).resolve().relative_to(DOCS.resolve())) if (DOCS / rel).parent.joinpath(path).resolve().is_relative_to(DOCS.resolve()) else None
            if not tgt or tgt not in all_md:
                E(f"broken link '{href}'")
                continue
            if frag and frag not in anchors(tgt):
                E(f"link '{href}': no anchor '#{frag}' in {tgt}")
            if tgt != rel:
                inbound[tgt].add(rel)
        # open questions: no generated placeholders; each item names its claim and its source
        for x in move_unknowns.boilerplate(body):
            E(f"boilerplate open-question item (rewrite it: the claim, the source, what is missing, the next lead): {x[:80]}")
        # open questions: every inline marker has its item, and every item its marker (resolved items leave both)
        mk = re.findall(r'<sup class="hr-q" id="qr-(\d+)"><a href="#q-(\d+)"', body)
        items = set(re.findall(r'<a id="q-(\d+)" class="hr-q-anchor"', body))
        marks = {m for m, _ in mk}
        for m, t in mk:
            if m != t:
                E(f"open-question marker qr-{m} points to #q-{t}")
        for n in sorted(marks - items, key=int):
            E(f"orphan open-question marker qr-{n}: no item q-{n} in Open questions (resolved? remove the marker too)")
        for n in sorted(items - marks, key=int):
            E(f"orphan open-question item q-{n}: no marker qr-{n} in the story (resolved? remove the item and log it on the Research Trail)")
        for n in sorted(set(re.findall(r'href="#qr-(\d+)"', body)) - marks, key=int):
            E(f"open-question back link to #qr-{n}, but there is no marker qr-{n}")
        if (marks or items) and "## Open questions & disputed details" not in body:
            E("has open-question markers but no 'Open questions & disputed details' section")
        # flag hygiene: a ⚠ names two sources (two footnotes between the item and the marked paragraph, or a link to
        # the other page's Open questions item that carries them); a single-source record shows ◐ in the story
        for n, title in re.findall(r'<sup class="hr-q" id="qr-(\d+)"><a href="#q-\d+" title="([^":]*)', body):
            if title != "Sources disagree":
                continue
            im = re.search(rf'<a id="q-{n}" class="hr-q-anchor"></a>(.*?)(?:<a class="hr-q-back"|<a id="q-|\n## )', body, re.S)
            item = im.group(1) if im else ""
            i = body.find(f'id="qr-{n}"')
            para = body[body.rfind("\n", 0, i):i]
            fns = set(re.findall(r"\[\^([\w-]+)\]", item)) | set(re.findall(r"\[\^([\w-]+)\]", para))
            deleg = re.search(r"\]\((?!#|https?:)[^)#\s]+\.md(?:#[\w-]+)?\)", item)
            if len(fns) < 2 and not deleg:
                E(f"⚠ qr-{n} names fewer than two sources (cite both, link the page that does, or use ◐ / ? instead)")
        rec = re.search(r'!!! abstract "Article record"\n((?:    .*\n?)+)', body)
        if rec:
            cm = re.search(r"\*\*Confidence:\*\* ([^·\n]*?) ?·", rec.group(1))
            if not cm:
                E("the record has no **Confidence:** label")
            elif not re.fullmatch(r"(High|Medium|Low)( \([^()]*\))?", cm.group(1).strip()):
                E(f"confidence '{cm.group(1).strip()}' must be High, Medium or Low (a note may follow in parentheses)")
            if cm and cm.group(1).strip().startswith("High"):
                for fn in re.findall(r"^\[\^([\w-]+)\]:.*search (?:excerpt|summary|snippet)", body, re.M | re.I):
                    E(f"High-confidence page cites [^{fn}] from a search excerpt; read the page itself or lower the confidence")
        story = body.split("## Open questions & disputed details")[0]
        if rec:
            story = story.replace(rec.group(0), "")
            if re.search(r"single[- ]source|\bone source\b|only source", rec.group(1), re.I) and "◐" not in story:
                E("the record says single source, but the story shows no ◐ marker")
        for sn in snippet_includes(body):
            if not (SNIPPETS / sn).exists():
                E(f"snippet '{sn}' not found in snippets/")
    # canonical facts
    for key, f in canon.items():
        page = f.get("page")
        if page not in metas:
            errors.append(f"canonical.yml {key}: page '{page}' is not an article")
            continue
        if f.get("anchor") and f["anchor"] not in anchors(page):
            errors.append(f"canonical.yml {key}: no anchor '#{f['anchor']}' in {page}")
        if f.get("snippet") and not (SNIPPETS / f["snippet"]).exists():
            errors.append(f"canonical.yml {key}: snippet '{f['snippet']}' missing")
        if key not in (metas[page].get("canonical_for") or []):
            errors.append(f"{page}: should list '{key}' in canonical_for")
        # the registry table on the schema page must show the same value
        _sch = (DOCS / "reference" / "article-schema.md").read_text(encoding="utf-8")
        _row = re.search(rf"^\| `{re.escape(key)}` \|.*\| ([^|]*) \|$", _sch, re.M)
        if not _row:
            errors.append(f"reference/article-schema.md: canonical table has no row for '{key}'")
        elif _row.group(1).strip() != str(f.get("value", "")).strip():
            errors.append(f"reference/article-schema.md: canonical table value for '{key}' differs from canonical.yml")
        # flags: the ⚠/◐ in `value` must stand on open items (`oq`) on the canonical page, of the same kind
        oq = f.get("oq") or []
        oq = [oq] if isinstance(oq, str) else oq
        for e in quick_answers_lib.flag_errors(set(re.findall(r"[⚠◐]", str(f.get("value", "")))),
                                               [r if "#" in r and r.split("#")[0] else f"{page}#{r.lstrip('#')}" for r in oq],
                                               f"canonical.yml {key}: value"):
            errors.append(e)
        rx = re.compile(f["detect"]) if f.get("detect") else None
        if not rx:
            continue
        for rel in arts:
            if rel == page:
                continue
            b = bodies[rel].split("## Open questions & disputed details")[0] + "\n".join(
                l for l in bodies[rel].split("## Open questions & disputed details")[1:])
            prose = plain(body_prose(b))
            if rx.search(prose):
                links_canon = re.search(rf"\]\((?:\.\./)?{re.escape(page.split('/')[1]) if page.split('/')[0] == rel.split('/')[0] else re.escape('../' + page)}", bodies[rel]) or re.search(re.escape(page.split("/")[1]) + r"(#[^)]*)?\)", bodies[rel])
                if not links_canon and f.get("snippet") not in snippet_includes(bodies[rel]):
                    errors.append(f"{rel}: tells '{key}' without linking its canonical page {page} (or including snippets/{f.get('snippet')})")
    if "--orphans" in sys.argv:
        print("Inbound article links (excluding front-matter related):")
        for rel in arts:
            n = len(inbound.get(rel, ()))
            if n <= 1:
                print(f"  {n}  {rel}")
    for w in warns:
        print("warning:", w)
    for e in errors:
        print("ERROR:", e)
    print(f"{len(arts)} articles checked, {len(errors)} errors, {len(canon)} canonical facts")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
