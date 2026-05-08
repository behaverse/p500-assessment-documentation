# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository purpose

Documentation platform for 16 cognitive-assessment "engines" (BCS, DS, NB, WO, UFOV, TH, SRM, SOS, SMC, RE, BM, BSAC, MOT, OC, OOO, PC). The deliverable is a static webapp under [webapp/](webapp/) that displays generated content sourced from an Excel master spec and per-engine JSON timeline configs.

## Common commands

All Python scripts use **relative paths anchored at the project root**, so always run them from the repo root (or use the `generate_timelines.py` wrapper, which `chdir`s for you).

```bash
# Setup (first time)
pip install -r requirements.txt          # or: source venv/bin/activate

# Serve the webapp (no build step — pure static HTML/CSS/JS)
cd webapp && python3 -m http.server 8000  # → http://localhost:8000

# Regenerate timeline HTML pages from content/timeline_configs/*.json
python3 scripts/generation/generate_timelines.py
# (wrapper that chdirs to project root, then calls generate_enhanced_timeline_pages.main)

# Regenerate engine description + parameters from content/Task spec.xlsx
python3 scripts/build/excel_extractor.py
```

There is no test suite, linter, or formatter wired up. `node -c webapp/js/script.js` is the only quick syntax check the README mentions.

## Architecture

### Two data pipelines feed one webapp

The webapp is a thin client over **two independently-generated data products**, both rooted in [content/](content/):

1. **Engine descriptions + parameters** (`content/Task spec.xlsx` → `content/engines.json`)
   - [scripts/build/excel_extractor.py](scripts/build/excel_extractor.py) parses the `scenes` and `parameters` sheets.
   - Output `engines.json` is the **runtime data source** the webapp fetches at load.

2. **Timeline pages** (`content/timeline_configs/*.json` + `content/en.yaml` + `content/timeline_names.xlsx` → `webapp/pages/timelines/<engine>/<timeline>.html`)
   - [scripts/generation/generate_enhanced_timeline_pages.py](scripts/generation/generate_enhanced_timeline_pages.py) is the resolver/generator.
   - Output is **pre-rendered HTML files** loaded on demand, not data merged into `engines.json`.

When changing engine-level content (description, parameter tables), regenerate `engines.json`. When changing timeline structure, regenerate the timeline HTML pages. They do not share output paths.

### Webapp runtime (no framework)

[webapp/index.html](webapp/index.html) hardcodes the 16-engine nav list. [webapp/js/script.js](webapp/js/script.js) `fetch`es `content/engines.json` and drives the 3-tier nav (engine → category → sub-item). [webapp/js/timeline.js](webapp/js/timeline.js) handles the `timelines` category — it loads the pre-rendered HTML files from `pages/timelines/<engine>/`. The HOME page content is hardcoded inside `script.js`, not in `engines.json`.

### The `webapp/content` symlink is load-bearing

[webapp/content](webapp/content) is a symlink to `../content`. Without it, `fetch('content/engines.json')` from the served webapp 404s. Don't replace it with a copy or delete it during cleanup.

### Timeline JSON is non-standard

Files in [content/timeline_configs/](content/timeline_configs/) contain **C-style comments and trailing commas** — they are not valid JSON. The generator strips them via regex in `EnhancedTimelineResolver._clean_json_comments` before parsing. If you write a new tool that consumes these files, replicate that cleaning step or use the resolver class.

### Engine ID conventions

Engine IDs are uppercase in [content/engines.json](content/engines.json), nav data attributes, and timeline config filenames (e.g. `BCS.json`), but **lowercase** in webapp output paths (`webapp/pages/timelines/bcs/`, `webapp/pages/parameters/BCS_parameters.html` is the exception — parameter pages keep uppercase). Match existing casing per directory rather than guessing.

## Repo hygiene notes

- [likely_obselete/](likely_obselete/) and [scripts/legacy/](scripts/legacy/) hold archived/deprecated files pending cleanup — don't import from them.
- [content/engines.json.backup](content/engines.json.backup) is tracked. Treat `engines.json` as a build artifact that's nonetheless committed.
- [TODO.md](TODO.md) lists open work (parameter enum display, timeline justifications, demo videos, deployment).
