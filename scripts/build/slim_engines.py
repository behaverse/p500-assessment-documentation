#!/usr/bin/env python3
"""
Slim engines.json
=================

Removes timeline content from content/engines.json that the webapp never reads
at runtime, shrinking the file the browser downloads on first load.

Background
----------
Each engine's `categories.timelines` block carries:
  - subItems       : fully-rendered HTML for every individual timeline
  - defaultContent  : a duplicate of `content`
  - content         : the timelines landing page

The webapp loads individual timeline pages from webapp/pages/timelines/*.html
and builds the timeline list from content/timeline_configs/*.json, so it never
reads `subItems`. `defaultContent` is read by nothing. The global search only
reads `categories[<cat>].content.body`, so `content` is kept.

Removing `subItems` + `defaultContent` drops the file ~9.0 MB -> ~0.8 MB with no
change to display or search behaviour. The script is idempotent and safe to
re-run; the original remains recoverable via git.

Usage
-----
Run from the repository root:
    python3 scripts/build/slim_engines.py
"""

import json
from pathlib import Path

ENGINES_JSON = Path("content/engines.json")
# Keys removed from each engine's `categories.timelines` block.
DROP_TIMELINE_KEYS = ("subItems", "defaultContent")


def slim(data: dict) -> tuple[dict, int]:
    """Strip unused timeline keys in place. Returns (data, removed_key_count)."""
    removed = 0
    for engine_id, engine in data.items():
        categories = engine.get("categories")
        if not isinstance(categories, dict):
            continue
        timelines = categories.get("timelines")
        if not isinstance(timelines, dict):
            continue
        for key in DROP_TIMELINE_KEYS:
            if key in timelines:
                del timelines[key]
                removed += 1
    return data, removed


def main() -> int:
    if not ENGINES_JSON.exists():
        print(f"Error: {ENGINES_JSON} not found. Run from the repository root.")
        return 1

    before = ENGINES_JSON.stat().st_size
    with ENGINES_JSON.open(encoding="utf-8") as f:
        data = json.load(f)

    data, removed = slim(data)

    # Match the existing formatting (indent=2, non-ASCII preserved).
    with ENGINES_JSON.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    after = ENGINES_JSON.stat().st_size
    print(f"Removed {removed} timeline key(s) across {len(data)} engines.")
    print(f"engines.json: {before/1e6:.2f} MB -> {after/1e6:.2f} MB "
          f"({100 * (before - after) / before:.0f}% smaller)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
