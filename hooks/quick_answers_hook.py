"""MkDocs hook: the Quick Answers page, generated from docs/data/quick_answers.yml.

  * on_pre_build     : validates every answer (numbers in the linked article, links and anchors, flags still open);
                       any error fails the build (PluginError).
  * on_page_markdown : replaces <!-- hr:quick-answers --> on docs/reference/quick-answers.md with the jump index and
                       one H3 per question, so each question has a stable anchor and its own search entry.
The design hook reads the same data for the "Quick answers" links in an article's Keep reading area.
"""
import sys
from pathlib import Path

from mkdocs.exceptions import PluginError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import quick_answers_lib as qa  # noqa: E402

_DATA = {}


def on_pre_build(config):
    data = qa.load()
    errors = qa.validate(data)
    if errors:
        raise PluginError("Invalid quick answers in docs/data/quick_answers.yml:\n  " + "\n  ".join(errors))
    _DATA["data"] = data


def on_page_markdown(markdown, page, config, files):
    if page.file.src_uri == qa.PAGE and "<!-- hr:quick-answers -->" in markdown:
        markdown = markdown.replace("<!-- hr:quick-answers -->", qa.render(_DATA.get("data") or qa.load(), qa.PAGE))
    return markdown
