#!/usr/bin/env python3
"""External link report for the articles and the bibliography. Not part of the build: it needs the
network, it is slow, and a dead outside site must not block a research push.

For every distinct http(s) URL in docs/**/*.md it:
  1. tries the https:// form first (an http:// link that works over https is reported as "upgrade");
  2. falls back to the original URL;
  3. if both fail with a 404/410/5xx or a connection error, asks the Wayback Machine for the closest
     snapshot and reports it as the suggested replacement ("dead, use <snapshot>").
401/402/403/429 answers are reported as "blocked" (402 is a paywall): many sites refuse scripts, which says nothing about
whether the page exists. Only a 404 or 410 counts as "dead". A 5xx or a connection error (DNS, TLS, timeout) is reported as "unreachable", since
it can be the checker's own network; confirm it from a browser before replacing the link. Wayback links themselves are only checked with --check-archive.

It also lists footnote definitions that cite a URL without an "(accessed YYYY-MM-DD)" date.

Usage:
  python scripts/check_external_links.py                 # whole site, summary + problems
  python scripts/check_external_links.py docs/places     # one folder or file
  python scripts/check_external_links.py --no-network    # access-date report only
  python scripts/check_external_links.py --json out.json # machine-readable results too
Exit status is always 0 unless --strict is given (then 1 when a link is dead).
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
UA = "Mozilla/5.0 (compatible; hotrod-history-linkcheck/1.0)"
# a URL may contain balanced parentheses (Wikimedia and Wikipedia titles do); trailing punctuation is not part of it
URL_RE = re.compile(r"https?://(?:[^\s<>()\"'\]]|\([^\s<>()\"']*\))+(?<![.,;:!?*_])")
FOOTDEF_RE = re.compile(r"^\[\^[\w-]+\]:.*$", re.M)
ACCESSED_RE = re.compile(r"accessed \d{4}-\d{2}-\d{2}", re.I)
WAYBACK = "web.archive.org"


def collect(paths):
    """{url: [(file, line)]} and [(file, line, footnote text)] lacking an access date."""
    where = defaultdict(list)
    undated = []
    files = []
    for p in paths:
        p = Path(p)
        files += sorted(p.rglob("*.md")) if p.is_dir() else [p]
    for f in files:
        text = f.read_text(encoding="utf-8")
        rel = f.relative_to(ROOT) if f.is_relative_to(ROOT) else f
        for n, line in enumerate(text.splitlines(), 1):
            urls = URL_RE.findall(line)
            archived = [u.split("://", 2)[-1] for u in urls if WAYBACK in u]
            for u in urls:
                # an original URL kept next to its Wayback copy is history, not a link to check
                if WAYBACK not in u and any(a.endswith(u.split("://", 1)[1].removeprefix("www.")) for a in archived):
                    continue
                where[u].append((str(rel), n))
        for m in FOOTDEF_RE.finditer(text):
            if URL_RE.search(m.group(0)) and not ACCESSED_RE.search(m.group(0)):
                n = text.count("\n", 0, m.start()) + 1
                undated.append((str(rel), n, m.group(0)[:110]))
    return where, undated


def fetch(url, timeout):
    """HTTP status (int) or an error string. HEAD first, GET when HEAD is refused."""
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (400, 403, 405, 406, 429, 500, 501, 503):
                continue
            return e.code
        except Exception as e:  # DNS, TLS, timeout, refused
            if method == "HEAD":
                continue
            return type(e).__name__
    return "error"


def wayback(url, timeout):
    api = "https://archive.org/wayback/available?url=" + urllib.parse.quote(url, safe="")
    try:
        with urllib.request.urlopen(urllib.request.Request(api, headers={"User-Agent": UA}), timeout=timeout) as r:
            snap = json.load(r).get("archived_snapshots", {}).get("closest") or {}
        if snap.get("available") and str(snap.get("status")) == "200":
            return snap["url"].replace("http://web.archive.org", "https://web.archive.org")
    except Exception:
        pass
    return None


def ok(status):
    return isinstance(status, int) and status < 400


def check(url, timeout, check_archive):
    host = urllib.parse.urlsplit(url).netloc
    if WAYBACK in host and not check_archive:
        return {"url": url, "result": "archive", "status": None}
    if url.startswith("http://"):
        https = "https://" + url[len("http://"):]
        s = fetch(https, timeout)
        if ok(s):
            return {"url": url, "result": "upgrade", "status": s, "suggest": https}
    s = fetch(url, timeout)
    if ok(s):
        return {"url": url, "result": "ok", "status": s}
    if s in (401, 402, 403, 429):  # 402: paywall
        return {"url": url, "result": "blocked", "status": s}
    snap = wayback(url, timeout)
    # a connection error may be the checker's network, not the site: report it apart from a 404
    # only 404/410 mean the page is gone; a 5xx or a connection error may be temporary or the checker's network
    kind = "dead" if s in (404, 410) else "unreachable"
    return {"url": url, "result": kind, "status": s, "suggest": snap}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", default=[str(DOCS)])
    ap.add_argument("--no-network", action="store_true", help="only report missing access dates")
    ap.add_argument("--check-archive", action="store_true", help="also fetch web.archive.org links")
    ap.add_argument("--timeout", type=float, default=15)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--json", metavar="FILE")
    ap.add_argument("--strict", action="store_true", help="exit 1 when a link is dead")
    a = ap.parse_args()

    where, undated = collect(a.paths)
    results = []
    if not a.no_network:
        with ThreadPoolExecutor(a.workers) as ex:
            results = list(ex.map(lambda u: check(u, a.timeout, a.check_archive), sorted(where)))

    by = defaultdict(list)
    for r in results:
        by[r["result"]].append(r)

    def loc(u):
        w = where[u]
        return ", ".join(f"{f}:{n}" for f, n in w[:3]) + (f" (+{len(w) - 3} more)" if len(w) > 3 else "")

    print(f"{len(where)} distinct external URLs in {len({f for v in where.values() for f, _ in v})} files")
    if results:
        print("  " + ", ".join(f"{k}: {len(v)}" for k, v in sorted(by.items())))
    for r in by["dead"] + by["unreachable"]:
        fix = f"use {r['suggest']}" if r.get("suggest") else "no Wayback snapshot; find another source or demote"
        label = "DEAD   " if r["result"] == "dead" else "NO CONN"
        print(f"{label} [{r['status']}] {r['url']}\n        in {loc(r['url'])}\n        {fix}")
    for r in by["upgrade"]:
        print(f"UPGRADE {r['url']} -> {r['suggest']}\n        in {loc(r['url'])}")
    for r in by["blocked"]:
        print(f"BLOCKED [{r['status']}] {r['url']} (site refuses scripts; check by hand)\n        in {loc(r['url'])}")
    print(f"\n{len(undated)} footnotes cite a URL without an access date (\"(accessed YYYY-MM-DD)\")")
    per = defaultdict(int)
    for f, _, _ in undated:
        per[f] += 1
    for f, c in sorted(per.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {c:3d}  {f}")
    if a.json:
        Path(a.json).write_text(json.dumps({"links": results, "where": where, "undated": undated}, indent=1))
    return 1 if a.strict and by["dead"] else 0


if __name__ == "__main__":
    sys.exit(main())
