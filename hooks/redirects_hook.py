"""Write redirect stubs for pages that moved, so published links keep working.

Reads hooks/redirects.yml (old url -> new url). After the build it writes, for each old URL, an
index.html with a meta refresh, a canonical link and a tiny script that keeps any #fragment, and a
Netlify `_redirects` file with permanent (301) rules. Old URLs that still exist as real pages are skipped.
No third-party plugin is needed.
"""
import html
import logging
from pathlib import Path

import yaml

log = logging.getLogger("mkdocs.hooks.redirects")

STUB = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Moved: {title}</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="{target}">
<meta http-equiv="refresh" content="0; url={target}">
<script>location.replace({target_js} + location.hash);</script></head>
<body><p>This page moved to <a href="{target}">{target_text}</a>.</p></body></html>
"""


def _load(config):
    path = Path(config["config_file_path"]).parent / "hooks" / "redirects.yml"
    if not path.exists():
        return {}
    return (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("redirects", {}) or {}


def on_post_build(config):
    redirects = _load(config)
    site = Path(config["site_dir"])
    base = (config.get("site_url") or "").rstrip("/")
    prefix = "/" + base.split("://", 1)[-1].split("/", 1)[1].strip("/") + "/" if base.count("/") > 2 else "/"
    prefix = prefix.replace("//", "/")
    rules = []
    made = 0
    for old, new in redirects.items():
        old_dir = site / old.strip("/")
        if not (site / new.strip("/") / "index.html").exists():
            log.warning("redirect target missing for %s -> %s", old, new)
            continue
        if (old_dir / "index.html").exists():
            log.warning("redirect source %s still exists as a page; skipped", old)
            continue
        target = prefix + new.lstrip("/")
        old_dir.mkdir(parents=True, exist_ok=True)
        (old_dir / "index.html").write_text(
            STUB.format(title=html.escape(new), target=html.escape(target), target_js='"' + target + '"',
                        target_text=html.escape(target)), encoding="utf-8")
        rules.append(f"{prefix}{old.lstrip('/')}  {target}  301!")
        rules.append(f"{prefix}{old.strip('/')}  {target}  301!")
        made += 1
    if rules:
        (site / "_redirects").write_text("\n".join(rules) + "\n", encoding="utf-8")
    log.info("redirects: wrote %d stubs", made)
