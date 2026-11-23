#!/usr/bin/env python3
"""Parse built JSON-LD and check apex canonicals, meta descriptions, sitemap, and robots.

    python scripts/check_launch_seo.py [site-dir]

Exit 1 if any page's JSON-LD does not parse, or a launch check fails.
Redirect stubs (noindex) and 404.html are not required to carry JSON-LD.
"""
import html
import json
import re
import sys
from pathlib import Path

APEX = "https://hotroddinghistory.com/"
LD_RE = re.compile(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', re.S)
CANON_RE = re.compile(r'<link rel="canonical" href="([^"]+)"')
OG_RE = re.compile(r'<meta property="og:url" content="([^"]*)"')
DESC_RE = re.compile(r'<meta name="description" content="([^"]*)"')


def _types(node, found):
    if isinstance(node, dict):
        t = node.get("@type")
        if isinstance(t, str):
            found.add(t)
        elif isinstance(t, list):
            found.update(x for x in t if isinstance(x, str))
        for v in node.values():
            _types(v, found)
    elif isinstance(node, list):
        for v in node:
            _types(v, found)


def check(site_dir):
    site = Path(site_dir)
    errors = []
    pages = 0
    articles = 0
    saw_org = False
    for path in sorted(site.rglob("*.html")):
        rel = path.relative_to(site).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        if rel == "404.html" or 'name="robots" content="noindex"' in text:
            continue
        blocks = LD_RE.findall(text)
        if len(blocks) != 1:
            errors.append(f"{rel}: expected 1 JSON-LD block, found {len(blocks)}")
            continue
        try:
            data = json.loads(blocks[0])
        except json.JSONDecodeError as exc:
            errors.append(f"{rel}: JSON-LD does not parse ({exc})")
            continue
        pages += 1
        blob = blocks[0]
        if "www.hotroddinghistory.com" in blob or "Adventure Equity" in blob:
            errors.append(f"{rel}: JSON-LD uses www or names the publisher company")
        types = set()
        _types(data, types)
        if "Organization" not in types or "WebSite" not in types:
            errors.append(f"{rel}: JSON-LD missing Organization or WebSite")
        if rel == "index.html":
            graph = data.get("@graph") or []
            org = next((n for n in graph if n.get("@type") == "Organization"), {})
            site_node = next((n for n in graph if n.get("@type") == "WebSite"), {})
            action = site_node.get("potentialAction") or {}
            target = (action.get("target") or {}).get("urlTemplate") or ""
            if org.get("name") != "Hot Rodding History":
                errors.append("index.html: Organization name is not Hot Rodding History")
            if APEX + "?q={search_term_string}" not in target:
                errors.append(f"index.html: SearchAction target is {target!r}")
            saw_org = True
        if "Article" in types:
            articles += 1
            if "BreadcrumbList" not in types:
                errors.append(f"{rel}: Article page has no BreadcrumbList")
        for label, rx in (("canonical", CANON_RE), ("og:url", OG_RE)):
            m = rx.search(text)
            if not m:
                errors.append(f"{rel}: missing {label}")
                continue
            href = html.unescape(m.group(1))
            if not href.startswith(APEX) or href.startswith("https://www."):
                errors.append(f"{rel}: {label} is {href}")
        dm = DESC_RE.search(text)
        if dm:
            desc = html.unescape(dm.group(1))
            if len(desc) > 158:
                errors.append(f"{rel}: meta description is {len(desc)} characters")
    if not saw_org:
        errors.append("homepage JSON-LD was not checked")
    if articles < 1:
        errors.append("no Article JSON-LD found")
    if pages < 10:
        errors.append(f"only {pages} pages carried JSON-LD")
    robots = site / "robots.txt"
    if not robots.exists() or f"Sitemap: {APEX}sitemap.xml" not in robots.read_text(encoding="utf-8"):
        errors.append("robots.txt missing or sitemap is not the apex URL")
    sm = site / "sitemap.xml"
    if not sm.exists():
        errors.append("sitemap.xml was not built")
    else:
        xml = sm.read_text(encoding="utf-8")
        locs = re.findall(r"<loc>([^<]+)</loc>", xml)
        if not locs:
            errors.append("sitemap.xml has no URLs")
        bad = [u for u in locs if not html.unescape(u).startswith(APEX)]
        if bad:
            errors.append(f"sitemap has {len(bad)} URLs off the apex, first {bad[0]}")
        if any("/cruising/woodward/" in html.unescape(u) for u in locs):
            errors.append("sitemap includes a redirect stub (/cruising/woodward/)")
    return errors


def main():
    site = Path(sys.argv[1] if len(sys.argv) > 1 else "site")
    errors = check(site)
    if errors:
        print(f"{len(errors)} error(s)")
        for e in errors:
            print("ERROR", e)
        return 1
    print("launch SEO check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
