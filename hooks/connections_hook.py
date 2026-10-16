"""MkDocs hook: render the Web of influence from docs/data/connections.yml.

Placeholders in Markdown pages (HTML comments, so they are invisible if the hook is off):
    <!-- hr:connections-graph -->   controls + the SVG diagram
    <!-- hr:connections-table -->   the full text table (accessible fallback)
    <!-- hr:connections-stats -->   one-line counts
Validation errors abort the build (PluginError): every edge needs a supporting wiki page and a verbatim
evidence phrase from it, and every profile in docs/companies/ needs a node.
"""
import logging
import sys
from pathlib import Path

from mkdocs.exceptions import PluginError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import connections_lib as cl  # noqa: E402

log = logging.getLogger("mkdocs.hooks.connections")
_DATA = {}


def on_pre_build(config):
    data = cl.load()
    errors, warns = cl.validate(data)
    for w in warns:
        log.warning("connections: %s", w)
    if errors:
        raise PluginError("Invalid connections in docs/data/connections.yml:\n  " + "\n  ".join(errors))
    _DATA["data"] = data


def on_page_content(html, page, config, files):
    data = _DATA.get("data")
    if not data:
        return html
    if "<!-- hr:connections-graph -->" in html:
        graph = ('<div class="hr-web" data-hr-web>' + cl.render_legend(data)
                 + '<div class="hr-web__stage">' + cl.render_graph(data, page.url) + "</div></div>")
        html = html.replace("<!-- hr:connections-graph -->", graph)
    if "<!-- hr:connections-table -->" in html:
        html = html.replace("<!-- hr:connections-table -->", cl.render_table(data, page.url))
    if "<!-- hr:connections-stats -->" in html:
        html = html.replace("<!-- hr:connections-stats -->", cl.render_stats(data))
    return html
