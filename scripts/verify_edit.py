#!/usr/bin/env python3
"""Compare every docs/*.md against its pre-edit baseline and report anything that disappeared or appeared:
footnote ids and text, source URLs, reference counts, quotes, flags (conflict, single-source, grassroots badge),
numbers, figure/caption markup, the Article record box, Visual references, and internal anchor links.

  python scripts/verify_edit.py --base pre-edit [--base pre-edit2] [--only docs/people/x.md] [--quiet]

A file is compared against the first --base ref that contains it. Files in no base are listed as NEW and skipped.
Exit status 1 if any difference is found.
"""
import argparse, collections, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FN_DEF = re.compile(r"^\[\^([^\]]+)\]:[ \t]*(.*(?:\n(?:[ \t]+.*|))*)", re.M)
NUM = re.compile(r"(?<![\w/#-])(?<!\d\.)\$?\d[\d,]*(?:\.\d+)?(?![\w-]*\.(?:png|jpg|jpeg|svg|md))")
QUOTE = re.compile(r"[“\"]([^“”\"\n]+?)[”\"]")


def git_show(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def moved_from():
    """new docs path -> [possible old docs paths], from hooks/redirects.yml (pages that moved keep a redirect)"""
    import yaml
    f = ROOT / "hooks/redirects.yml"
    out = {}
    if not f.exists():
        return out
    for old, new in (yaml.safe_load(f.read_text()) or {}).get("redirects", {}).items():
        new_md = "docs/" + (new.strip("/") + "/index.md" if new.endswith("/") and "." not in new else new)
        cand_new = ["docs/" + new.strip("/") + ".md", "docs/" + new.strip("/") + "/index.md"]
        cand_old = ["docs/" + old.strip("/") + ".md", "docs/" + old.strip("/") + "/index.md"]
        for n in cand_new:
            out.setdefault(n, []).extend(cand_old)
    return out


MOVED = None


def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", s).strip()


def split(text):
    # front matter is dropped, except the record-box note fields (location, peak, status, later, revival,
    # principal_source), which carry story text, footnote refs and markers: they are compared as part of the body
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    notes = ""
    if fm:
        import yaml
        sys.path.insert(0, str(ROOT / "scripts"))
        from articles_lib import record_notes_text
        try:
            notes = record_notes_text(yaml.safe_load(fm.group(1)) or {})
        except Exception:
            notes = ""
    text = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.S)
    if notes:
        text = notes + "\n\n" + text
    defs = {m.group(1): norm(m.group(2)) for m in FN_DEF.finditer(text)}
    body = FN_DEF.sub("", text)
    return body, defs


def block(text, start_pat, end_pat=None):
    m = re.search(start_pat, text, re.S | re.M)
    return norm(m.group(0)) if m else ""


def analyse(text):
    body, defs = split(text)
    a = {}
    a["fn_defs"] = defs
    a["fn_refs"] = collections.Counter(re.findall(r"\[\^([^\]]+)\]", body))
    a["urls"] = set(re.findall(r"https?://[^\s)>\]\"']+", text))
    quotes = set()
    for line in body.splitlines():
        if line.startswith(">") and not line.startswith(">>>"):
            pass
    bq = re.findall(r"^>\s?(.*)$", body, re.M)
    for b in bq:
        if len(b.split()) >= 3:
            quotes.add(norm(b))
    for m in QUOTE.finditer(re.sub(r"<[^>]+>", " ", body)):
        if len(m.group(1).split()) >= 2:
            quotes.add(norm(m.group(1)).strip(" ,.;:"))
    a["quotes"] = quotes
    a["flags"] = collections.Counter({"⚠": body.count("⚠"), "◐": body.count("◐"), "badge": body.count("hr-badge")})
    plain = re.sub(r"^\s*\d+\.\s", "", body, flags=re.M)
    plain = re.sub(r"\]\([^)]*\)", "]", plain)           # drop link targets
    plain = re.sub(r"<(?:figure|img|a|span|div|p)[^>]*>", " ", plain)
    plain = re.sub(r"!\[[^\]]*\]", " ", plain)
    figs = re.findall(r"<figure.*?</figure>", body, re.S)
    for f in figs:
        plain = plain.replace(f, " ")
    a["numbers"] = collections.Counter(n.strip("$").rstrip(".,") for n in NUM.findall(plain))
    a["figures"] = [norm(f) for f in figs]
    a["record"] = block(body, r'^!!! abstract "Article record".*?(?=\n\S)')
    a["visual"] = block(body, r"^#+ [^\n]*Visual references.*?(?=\n#+ |\Z)")
    a["anchors"] = set(re.findall(r"\]\(([^)#\s]+\.md#[^)\s]+)\)", body))
    return a


def diff_sets(label, old, new, out):
    for x in sorted(old - new):
        out.append(f"  - {label} REMOVED: {x[:160]}")
    for x in sorted(new - old):
        out.append(f"  + {label} ADDED:   {x[:160]}")


def compare(path, old_t, new_t):
    o, n = analyse(old_t), analyse(new_t)
    out = []
    for k in sorted(set(o["fn_defs"]) | set(n["fn_defs"])):
        if k not in n["fn_defs"]: out.append(f"  - footnote [^{k}] REMOVED")
        elif k not in o["fn_defs"]: out.append(f"  + footnote [^{k}] ADDED")
        elif o["fn_defs"][k] != n["fn_defs"][k]: out.append(f"  ~ footnote [^{k}] TEXT CHANGED")
    for k in sorted(set(o["fn_refs"]) | set(n["fn_refs"])):
        if (o["fn_refs"][k] == 0) != (n["fn_refs"][k] == 0):
            out.append(f"  ~ footnote [^{k}] cited {o['fn_refs'][k]}x -> {n['fn_refs'][k]}x")
    diff_sets("URL", o["urls"], n["urls"], out)
    diff_sets("quote", o["quotes"], n["quotes"], out)
    for k in o["flags"]:
        if o["flags"][k] != n["flags"][k]:
            out.append(f"  ~ flag {k}: {o['flags'][k]} -> {n['flags'][k]}")
    for k in sorted(set(o["numbers"]) | set(n["numbers"])):
        if o["numbers"][k] == 0: out.append(f"  + number NEW: {k}")
        elif n["numbers"][k] == 0: out.append(f"  - number GONE: {k}")
    if o["figures"] != n["figures"]: out.append("  ~ figure markup/caption CHANGED")
    if o["record"] != n["record"]: out.append("  ~ Article record box CHANGED")
    if o["visual"] != n["visual"]: out.append("  ~ Visual references section CHANGED")
    return out


def anchor_check():
    """every [..](x.md#anchor) link (in docs and in highlights.yml) must resolve to a heading or explicit id"""
    import yaml
    from markdown.extensions.toc import slugify
    def ids(path):
        t = path.read_text(); out = set()
        for m in re.finditer(r"^#+\s+(.*?)\s*$", t, re.M):
            h = m.group(1)
            mm = re.search(r"\{[^}]*#([\w-]+)[^}]*\}\s*$", h)
            if mm: out.add(mm.group(1)); h = re.sub(r"\{[^}]*\}\s*$", "", h)
            out.add(slugify(re.sub(r"[`*_]|<[^>]+>|\[([^\]]*)\]\([^)]*\)", r"\1", h), "-"))
        return out
    probs = []
    refs = []
    for f in sorted(ROOT.glob("docs/**/*.md")):
        for m in re.finditer(r"\]\(([^)#\s]+\.md)#([^)\s]+)\)", f.read_text()):
            refs.append((f, (f.parent / m.group(1)).resolve(), m.group(2)))
    hy = ROOT / "docs/data/highlights.yml"
    if hy.exists():
        for h in yaml.safe_load(hy.read_text())["highlights"]:
            if "#" in h["link"]:
                pth, anc = h["link"].split("#", 1)
                refs.append((hy, (ROOT / "docs" / pth).resolve(), anc))
    for f, tgt, anc in refs:
        if not tgt.exists() or anc not in ids(tgt):
            probs.append(f"  broken anchor: {f.relative_to(ROOT)} -> {tgt.name}#{anc}")
    return probs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", action="append", default=[])
    ap.add_argument("--only", action="append", default=[])
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    bases = a.base or ["pre-edit"]
    files = [Path(p) for p in a.only] or sorted(ROOT.glob("docs/**/*.md"))
    bad = 0; new = []; same = 0
    for f in files:
        rel = str(f.resolve().relative_to(ROOT))
        old = next((t for t in (git_show(b, rel) for b in bases) if t is not None), None)
        if old is None:
            global MOVED
            MOVED = MOVED if MOVED is not None else moved_from()
            for cand in sorted(MOVED.get(rel, []), key=len, reverse=True):
                old = next((t for t in (git_show(b, cand) for b in bases) if t is not None), None)
                if old is not None:
                    break
        if old is None:
            new.append(rel); continue
        diffs = compare(rel, old, (ROOT / rel).read_text())
        if diffs:
            bad += 1
            print(rel); print("\n".join(diffs))
        else:
            same += 1
    ap_ = anchor_check()
    if ap_:
        bad += 1; print("\n".join(ap_))
    print(f"\n{same} files identical on every checked dimension; {bad} with differences; {len(new)} new files not in baseline")
    if new and not a.quiet: print("NEW:", ", ".join(new))
    sys.exit(1 if bad else 0)

main()
