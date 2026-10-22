#!/usr/bin/env python3
"""Orphan / under-linked report from the built site (run after `mkdocs build`).

Counts, for every article, how many other articles link to it from their body text (hand links and
first-mention links; the related-story cards and backlinks are not counted)."""
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from articles_lib import ROOT, articles  # noqa: E402

SITE = ROOT / "site"


def main():
    arts = articles()
    url = {a: a[:-3] + "/" for a in arts}
    back = {v: k for k, v in url.items()}
    inbound = defaultdict(set)
    for a in arts:
        f = SITE / url[a] / "index.html"
        if not f.exists():
            continue
        h = f.read_text()
        m = re.search(r'<div class="hr-body md-typeset">(.*?)<footer class="hr-more"', h, re.S) or re.search(r'<div class="hr-body md-typeset">(.*)', h, re.S)
        body = m.group(1) if m else ""
        for href in re.findall(r'href="([^"#]+)', body):
            if re.match(r"^[a-z]+:", href):
                continue
            parts = [p for p in url[a].split("/") if p]
            for seg in href.split("/"):
                if seg == "..":
                    parts and parts.pop()
                elif seg and seg != ".":
                    parts.append(seg)
            t = "/".join(parts) + "/"
            if t in back and back[t] != a:
                inbound[back[t]].add(a)
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    rows = sorted(arts, key=lambda a: (len(inbound[a]), a))
    print(f"Articles with <= {limit} inbound article links:")
    n = 0
    for a in rows:
        if len(inbound[a]) <= limit:
            print(f"  {len(inbound[a])}  {a}")
            n += 1
    print(f"{n} of {len(arts)}")


if __name__ == "__main__":
    main()
