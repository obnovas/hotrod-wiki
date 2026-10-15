#!/usr/bin/env python3
"""Maintain docs/data/highlights.yml (the home-page Highlights slider).

Commands
  check            validate every highlight (the same checks the build runs) and the nightly standard
  list             show featured and archived highlights in display order
  stats            counts by source type, flag and grassroots share
  add              append a new highlight (validated before it is written); see --help
  scaffold         print a YAML template to paste by hand

Examples
  python scripts/update_highlights.py check
  python scripts/update_highlights.py add --id pomona-join-them --headline "..." --teaser "..." \\
      --link grassroots/pomona-choppers-fontana.md --evidence "phrase from the article" \\
      --source-type "Local news" --confidence Medium --grassroots --eras 1950s --regions "Pomona, Calif."

Nothing here talks to the network. Run from anywhere; paths are relative to the repo root.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import highlights_lib as hl  # noqa: E402
import yaml  # noqa: E402


def cmd_check(args) -> int:
    data = hl.load()
    errors, warns = hl.validate(data, strict_style=args.strict)
    for w in warns:
        print("warn :", w)
    for e in errors:
        print("ERROR:", e)
    for m in hl.batch_report(data, args.day):
        print("round:", m)
    feat, arch = hl.ordered(data)
    print(f"{len(data['highlights'])} highlights: {len(feat)} featured, {len(arch)} archived; "
          f"{sum(h['grassroots'] for h in data['highlights'])} grassroots")
    print("FAILED" if errors else "OK")
    return 1 if errors else 0


def cmd_list(_args) -> int:
    data = hl.load()
    feat, arch = hl.ordered(data)
    for title, items in (("FEATURED", feat), ("ARCHIVED", arch)):
        print(f"== {title} ({len(items)})")
        for i, h in enumerate(items, 1):
            t = h["source_type"] if isinstance(h["source_type"], list) else [h["source_type"]]
            print(f"{i:>2}. {h['added']} {'G' if h['grassroots'] else '-'} {h['flag']:<13} "
                  f"{h['id']:<28} [{', '.join(t)}]")
    return 0


def cmd_stats(_args) -> int:
    data = hl.load()
    hs = data["highlights"]
    c = collections.Counter()
    for h in hs:
        for t in (h["source_type"] if isinstance(h["source_type"], list) else [h["source_type"]]):
            c[t] += 1
    print("by source type:", dict(c.most_common()))
    print("by flag:", dict(collections.Counter(h["flag"] for h in hs)))
    g = sum(h["grassroots"] for h in hs)
    print(f"grassroots: {g}/{len(hs)} ({100 * g // max(len(hs), 1)}%)")
    by_day = collections.Counter(h["added"] for h in hs)
    print("added per round:", dict(sorted(by_day.items())))
    return 0


def cmd_scaffold(_args) -> int:
    print("""  - id: short-kebab-id
    headline: "Specific and surprising, under 110 characters"
    teaser: "One or two sentences. Only facts the article states, with the same hedges."
    link: folder/article.md#optional-heading-slug
    evidence: ["verbatim phrase 1 from the article", "verbatim phrase 2"]
    source_type: ["Local news"]   # see SOURCE_TYPES in scripts/highlights_lib.py
    confidence: Medium            # High | Medium-High | Medium | Low-Medium | Low
    flag: none                    # none | conflict | single-source
    grassroots: true
    added: %s
    eras: ["1950s"]
    regions: ["Town, State"]
    image: commons-example.jpg     # optional; must have a row in docs/reference/image-credits.md
    image_alt: "What the photo shows"
    image_note: "Context the photo does NOT show, if relevant"
""" % dt.date.today().isoformat())
    return 0


def cmd_add(a) -> int:
    data = hl.load()
    h = {
        "id": a.id, "headline": a.headline, "teaser": a.teaser, "link": a.link,
        "evidence": a.evidence if len(a.evidence) > 1 else a.evidence[0],
        "source_type": a.source_type if len(a.source_type) > 1 else a.source_type[0],
        "confidence": a.confidence, "flag": a.flag, "grassroots": bool(a.grassroots),
        "added": a.added or dt.date.today().isoformat(),
    }
    if a.eras: h["eras"] = a.eras
    if a.regions: h["regions"] = a.regions
    if a.image:
        h["image"] = a.image
        h["image_alt"] = a.image_alt or ""
        if a.image_note: h["image_note"] = a.image_note
    trial = {"settings": data["settings"], "highlights": [*data["highlights"], h]}
    errors, warns = hl.validate(trial, strict_style=True)
    mine = [e for e in errors if e.startswith(f"[{a.id}]")] + [e for e in errors if not e.startswith("[")]
    for w in warns:
        if w.startswith(f"[{a.id}]"): print("warn :", w)
    if mine:
        for e in mine: print("ERROR:", e)
        print("not written")
        return 1
    block = yaml.safe_dump([h], sort_keys=False, allow_unicode=True, width=100, default_flow_style=None)
    # keep human-friendly: append to the file, preserving existing comments
    path = hl.DATA
    text = path.read_text(encoding="utf-8").rstrip("\n") + "\n\n" + "\n".join("  " + l if l else l for l in block.splitlines()) + "\n"
    if a.dry_run:
        print(text[-len(block) - 200:])
        return 0
    path.write_text(text, encoding="utf-8")
    print(f"added {a.id}. Run: python scripts/update_highlights.py check")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check"); c.add_argument("--strict", action="store_true", help="treat style warnings as errors")
    c.add_argument("--day", help="round date (YYYY-MM-DD) to test against the nightly standard; default newest"); c.set_defaults(f=cmd_check)
    sub.add_parser("list").set_defaults(f=cmd_list)
    sub.add_parser("stats").set_defaults(f=cmd_stats)
    sub.add_parser("scaffold").set_defaults(f=cmd_scaffold)
    ad = sub.add_parser("add", help="validate and append a highlight")
    ad.add_argument("--id", required=True); ad.add_argument("--headline", required=True); ad.add_argument("--teaser", required=True)
    ad.add_argument("--link", required=True, help="docs-relative .md path, optional #anchor")
    ad.add_argument("--evidence", required=True, action="append", help="verbatim phrase from the article (repeatable)")
    ad.add_argument("--source-type", required=True, action="append", choices=hl.SOURCE_TYPES, help="repeatable")
    ad.add_argument("--confidence", required=True, choices=hl.CONFIDENCE)
    ad.add_argument("--flag", default="none", choices=list(hl.FLAGS))
    ad.add_argument("--grassroots", action="store_true")
    ad.add_argument("--added"); ad.add_argument("--eras", nargs="*"); ad.add_argument("--regions", nargs="*")
    ad.add_argument("--image"); ad.add_argument("--image-alt"); ad.add_argument("--image-note")
    ad.add_argument("--dry-run", action="store_true")
    ad.set_defaults(f=cmd_add)
    a = p.parse_args()
    return a.f(a)


if __name__ == "__main__":
    sys.exit(main())
