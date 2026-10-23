#!/usr/bin/env python3
"""Validate docs/data/quick_answers.yml (the same check the build runs in hooks/quick_answers_hook.py).

    python scripts/check_quick_answers.py          # exit 1 on any error
    python scripts/check_quick_answers.py --list   # also print every question with its full-story page
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import quick_answers_lib as qa  # noqa: E402

data = qa.load()
errs = qa.validate(data)
if "--list" in sys.argv:
    for t, q in qa.questions(data):
        print(f"{t['id']:28} #{q['id']:40} {q['link']}{'  ' + q['flag'] if q.get('flag') else ''}")
for e in errs:
    print("ERROR:", e)
print(f"{sum(1 for _ in qa.questions(data))} quick answers in {len(data.get('themes') or [])} themes, {len(errs)} errors")
sys.exit(1 if errs else 0)
