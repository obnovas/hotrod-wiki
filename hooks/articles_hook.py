"""Article structure hook.

  * on_pre_build    : runs scripts/check_articles.py; any error fails the build (schema, links, canonical facts).
  * on_page_markdown: front-matter `summary` becomes the page's meta description (search results and social cards),
                      and articles get a search boost.
  * on_page_content : puts the summary at the top of the story as a standfirst (so the search index carries it
                      under the title), and links the first mention of any name that has its own article
                      (docs/data/entities.yml).
Related stories and "Mentioned in" backlinks are assembled in design_hook.on_page_context from the same front matter.
"""
import html as htmlmod
import importlib.util
import re
import sys
from pathlib import Path

from mkdocs.exceptions import PluginError

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import articles_lib  # noqa: E402
import yaml  # noqa: E402

ENT = {}        # target rel -> [names]
AUTOLINKS = {}  # src rel -> [target rel] (for reporting / backlinks)


def on_config(config):
    ENT.clear()
    f = ROOT / "docs" / "data" / "entities.yml"
    if f.exists():
        for rel, v in (yaml.safe_load(f.read_text()) or {}).items():
            ENT[rel] = list((v or {}).get("names") or [])
    return config


def on_pre_build(config):
    spec = importlib.util.spec_from_file_location("check_articles", ROOT / "scripts" / "check_articles.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = mod.main()
    if rc:
        errs = [l for l in buf.getvalue().splitlines() if l.startswith("ERROR")]
        raise PluginError("Article check failed (scripts/check_articles.py):\n  " + "\n  ".join(errs[:40]))
    for rel in ENT:
        if not (ROOT / "docs" / rel).exists():
            raise PluginError(f"docs/data/entities.yml: {rel} does not exist")


def on_page_markdown(markdown, page, config, files):
    meta = page.meta
    if articles_lib.is_article(page.file.src_uri):
        if meta.get("summary") and not meta.get("description"):
            meta["description"] = str(meta["summary"]).strip()
        meta.setdefault("search", {"boost": 2})
    return markdown


SKIP_TAGS = {"a", "h1", "h2", "h3", "h4", "h5", "h6", "code", "pre", "sup", "script", "style", "figcaption", "summary", "dt", "th", "button", "svg"}


def _rel_href(target, here):
    up = here.count("/")
    return "../" * up + target[:-3] + "/" if not target.endswith("index.md") else "../" * up + target[:-8]


def autolink(html, src, page_url):
    if not ENT:
        return html, []
    stop = html.find('id="open-questions-disputed-details"')
    head, tail = (html[:stop], html[stop:]) if stop > 0 else (html, "")
    tokens = re.split(r"(<[^>]+>)", head)
    names = []
    for tgt, ns in ENT.items():
        if tgt == src:
            continue
        for n in ns:
            names.append((n, tgt))
    names.sort(key=lambda x: -len(x[0]))
    # positions of existing links to each target
    done, linked = set(), []
    stack = []
    in_admon = 0
    out = []
    for tok in tokens:
        if tok.startswith("<"):
            m = re.match(r"<(/?)([a-zA-Z0-9]+)", tok)
            if m:
                closing, tag = m.group(1) == "/", m.group(2).lower()
                if tag in SKIP_TAGS:
                    if closing:
                        if tag in stack:
                            while stack and stack.pop() != tag:
                                pass
                    elif not tok.endswith("/>"):
                        stack.append(tag)
                if tag == "div" and not closing and re.search(r'class="[^"]*admonition[^"]*abstract', tok):
                    in_admon = 1
                if tag == "a" and not closing:
                    hm = re.search(r'href="([^"#]*)', tok)
                    if hm:
                        h = hm.group(1)
                        for t in ENT:
                            stem = t[:-3].split("/")[-1]
                            if h.rstrip("/").endswith(stem) or h.endswith(stem + ".md"):
                                done.add(t)
            out.append(tok)
            continue
        if stack or in_admon or not tok.strip():
            if in_admon and "Article record" not in tok and tok.strip():
                pass
            out.append(tok)
            continue
        text = tok
        for n, tgt in names:
            if tgt in done:
                continue
            esc = htmlmod.escape(n, quote=False).replace('"', "&quot;")
            for cand in {n, esc, n.replace('"', "&quot;"), n.replace('"', "“").replace("“", "“", 1)}:
                m = re.search(r"(?<![\w-])" + re.escape(cand) + r"(?![\w-])", text)
                if m:
                    href = _rel_href(tgt, page_url)
                    text = text[:m.start()] + f'<a class="hr-autolink" href="{href}">{m.group(0)}</a>' + text[m.end():]
                    done.add(tgt)
                    linked.append(tgt)
                    break
        out.append(text)
        # leave the record box once its block closes (record box is a single div with one or two paragraphs)
        if in_admon and "</div>" in "".join(out[-3:]):
            in_admon = 0
    return "".join(out) + tail, linked


def on_page_content(html, page, config, files):
    src = page.file.src_uri
    if not articles_lib.is_article(src):
        return html
    meta = page.meta or {}
    s = str(meta.get("summary") or "").strip()
    if s:
        html = f'<p class="hr-summary" data-search-boost="summary">{htmlmod.escape(s)}</p>\n' + html
    html, linked = autolink(html, src, page.url)
    AUTOLINKS[src] = linked
    page.meta["_autolinks"] = linked
    return html
