"""MkDocs hook: render the Highlights slider (and archive) from docs/data/highlights.yml.

Placeholders in Markdown pages (HTML comments, so they are invisible if the hook is off):
    <!-- hr:highlights -->          the carousel (home page)
    <!-- hr:highlights-archive -->  the list of rotated-out highlights
Validation errors abort the build (PluginError), so a bad highlight never ships.
"""
import logging
import sys
from pathlib import Path

from mkdocs.exceptions import PluginError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import highlights_lib as hl  # noqa: E402

log = logging.getLogger("mkdocs.hooks.highlights")
_DATA = {}


def on_pre_build(config):
    data = hl.load()
    errors, warns = hl.validate(data)
    for w in warns:
        log.info("highlights: %s", w)
    if errors:
        raise PluginError("Invalid highlights in docs/data/highlights.yml:\n  " + "\n  ".join(errors))
    _DATA["data"] = data


def on_page_content(html, page, config, files):
    data = _DATA.get("data")
    if not data:
        return html
    if "<!-- hr:highlights -->" in html:
        html = html.replace("<!-- hr:highlights -->", hl.render_slider(data, page.url))
    if "<!-- hr:highlights-archive -->" in html:
        html = html.replace("<!-- hr:highlights-archive -->", hl.render_archive(data, page.url))
    return html
