"""Reading paths (docs/data/paths.yml): load, index and check.

A path is an ordered route through story pages. Each step is {page, why, planned?}. `page` is a path under docs/,
in the same form as front-matter `related`. A page may sit on several paths; its primary path is the first one
in the file that lists it (plan paths A-K come before the extra paths).

Used by scripts/check_articles.py (the build gate) and hooks/design_hook.py (the path bar and the path index)."""
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
PATHS = DOCS / "data" / "paths.yml"
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def load(path=PATHS):
    if not Path(path).exists():
        return []
    return (yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}).get("paths") or []


def live_steps(p):
    """Steps that exist (planned steps are never linked)."""
    return [s for s in p.get("steps") or [] if not s.get("planned")]


def by_page(paths):
    """page -> [(path, index in live steps)], primary first."""
    out = {}
    for p in paths:
        for i, s in enumerate(live_steps(p)):
            out.setdefault(s["page"], []).append((p, i))
    return out


def check(paths, articles):
    """-> (errors, warnings). `articles` is the list of story pages (docs-relative .md paths)."""
    errors, warns = [], []
    arts = set(articles)
    seen = set()
    for n, p in enumerate(paths):
        pid = p.get("id")
        where = f"paths.yml {pid or f'#{n + 1}'}"
        if not pid or not ID_RE.match(str(pid)):
            errors.append(f"{where}: id must be a lower-case slug")
        elif pid in seen:
            errors.append(f"{where}: duplicate id")
        seen.add(pid)
        if not p.get("title"):
            errors.append(f"{where}: no title")
        if not p.get("purpose"):
            errors.append(f"{where}: no purpose")
        steps = p.get("steps") or []
        if len(live_steps(p)) < 2:
            errors.append(f"{where}: needs at least two existing steps")
        on = set()
        for s in steps:
            pg = s.get("page")
            if not pg:
                errors.append(f"{where}: a step has no page")
                continue
            if pg in on:
                errors.append(f"{where}: '{pg}' is listed twice")
            on.add(pg)
            exists = (DOCS / pg).exists()
            if s.get("planned"):
                if exists:
                    errors.append(f"{where}: '{pg}' is marked planned but now exists (drop `planned: true`)")
            elif not exists:
                errors.append(f"{where}: step '{pg}' does not exist (mark it `planned: true` or fix the path)")
            elif pg not in arts:
                errors.append(f"{where}: step '{pg}' is not a story page")
            if not s.get("why"):
                warns.append(f"{where}: step '{pg}' has no `why`")
    covered = {s["page"] for p in paths for s in live_steps(p) if s.get("page")}
    for a in sorted(arts - covered):
        warns.append(f"{a}: on no reading path (docs/data/paths.yml)")
    return errors, warns
