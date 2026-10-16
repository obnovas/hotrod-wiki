#!/usr/bin/env python3
"""Validate docs/data/connections.yml (the Web of influence).

Fails (exit 1) if any edge lacks a supporting page or a verbatim evidence phrase in that page, if an endpoint
is unknown, if a company profile has no node, or if a node is an orphan. The MkDocs build runs the same checks.

  python scripts/check_connections.py          # validate
  python scripts/check_connections.py --list   # print every edge with its evidence page
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import connections_lib as cl  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    data = cl.load()
    errors, warns = cl.validate(data)
    nodes = {n["id"]: n for n in data["nodes"]}
    if args.list:
        for e in data["edges"]:
            print(f'{nodes[e["from"]]["label"]:28} --{e["type"]}--> {nodes[e["to"]]["label"]:28} [{e["page"]}] {e.get("flag", "")}')
    for w in warns:
        print("warn :", w)
    for e in errors:
        print("ERROR:", e)
    print(f"{len(data['nodes'])} nodes, {len(data['edges'])} edges, {len(errors)} errors, {len(warns)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
