# Behaverse Assessment Documentation (P500)

Documentation platform for the cognitive-assessment "engines" used in the **P500** study. The deliverable is a static webapp under [webapp/](webapp/) that displays content generated from an Excel master spec and per-engine timeline configs. No framework, no build step at runtime — pure HTML/CSS/JS over generated data.

**Live site:** https://behaverse.org/p500-assessment-documentation/ (deployed from `main` via GitHub Pages).

## Quick start

```bash
# Install Python build dependencies (only needed to regenerate content)
pip install -r requirements.txt

# Serve the webapp at http://localhost:8000
make serve
# equivalently: cd webapp && python3 -m http.server 8000
```

The webapp itself is static and needs no build to run. Python is only required when you regenerate the generated data (see Development workflow).

## Repository structure

```
behaverse_assessment_documentation/
├── Makefile                  # build / serve / dist / clean targets
├── requirements.txt          # Python build-time dependencies
├── content/                  # Source data + generated runtime data
│   ├── Task spec.xlsx        # Master spreadsheet (build-time input)
│   ├── timeline_names.xlsx   # Timeline naming reference (build-time input)
│   ├── timeline_configs/     # Per-engine timeline JSON (build-time input, non-standard JSON)
│   ├── en.yaml               # Localization strings (runtime)
│   ├── engines.json          # Generated engine config (runtime data source)
│   ├── images/               # Engine images
│   └── OrderedClicks/        # OrderedClicks level data
├── scripts/                  # Python automation
│   ├── build/excel_extractor.py              # Task spec.xlsx -> engines.json
│   ├── build/slim_engines.py                 # strip unused timeline HTML from engines.json
│   ├── generation/generate_enhanced_timeline_pages.py  # configs -> timeline HTML
│   ├── generation/generate_timelines.py      # wrapper that chdirs to repo root
│   ├── debug/                # One-off debugging scripts (not part of the build)
│   └── utils/                # Helper scripts
├── webapp/                   # Static web application (the deliverable)
│   ├── index.html            # Shell + hardcoded engine nav
│   ├── content -> ../content # Symlink so fetch('content/...') resolves
│   ├── js/script.js          # Nav + content rendering
│   ├── js/timeline.js        # Timeline category loader
│   ├── css/                  # styles.css, parameters.css
│   ├── pages/                # Generated HTML (parameters/, timelines/)
│   └── assets/               # Engine videos and thumbnails
└── .github/workflows/deploy.yml  # CI: build + deploy to GitHub Pages
```

## Development workflow

All Python scripts use **relative paths anchored at the repo root** — run them from the
repo root (or use `make`, which does the right thing).

### Regenerate content

```bash
make build      # runs both generators below

# or individually:
python3 scripts/build/excel_extractor.py            # -> content/engines.json
python3 scripts/generation/generate_timelines.py    # -> webapp/pages/timelines/<engine>/*.html
```

- Changed an **engine description or parameter table**? The source is `content/Task spec.xlsx`; regenerate `engines.json`, then run `python3 scripts/build/slim_engines.py` to drop unused timeline HTML.
- Changed a **timeline structure**? The source is `content/timeline_configs/*.json`; regenerate the timeline HTML pages.

These two pipelines are independent and do not share output paths.

> **Asset paths in generated timeline pages must be root-relative** (`assets/...`, `content/images/...`) — never `../`-prefixed. The webapp fetches each timeline page and injects it into the root `index.html`, so relative URLs resolve against the site root, not the file. Under the GitHub Pages project subpath, `../` paths escape the subpath and 404. The generator already does this; preserve it.

### Serve and sanity-check

```bash
make serve
node -c webapp/js/script.js webapp/js/timeline.js     # JS syntax check
```

Always click through the nav (engine -> category -> sub-item, including a timeline page) after changing generated content or JS before considering a change done.

### Add a new engine

1. Add engine data to `content/Task spec.xlsx`.
2. Add a timeline config in `content/timeline_configs/<ID>.json`.
3. Run `make build`.
4. Add the engine ID to the nav list in `webapp/index.html` (the nav is hardcoded).

## Deploy

The site is built and published to GitHub Pages by [.github/workflows/deploy.yml](.github/workflows/deploy.yml) on every push to `main`. The workflow runs `make dist`, which copies `webapp/` into `dist/` and replaces the `webapp/content` symlink with a real copy of the runtime content (excluding the Excel build inputs).

Build a deployable bundle locally to inspect it:

```bash
make dist     # produces ./dist
make clean    # removes ./dist
```

## Status

- **16 engines** documented: BCS, DS, NB, WO, UFOV, TH, SRM, SOS, SMC, RE, BM, BSAC, MOT, OC, OOO, PC.
- Three-tier navigation (engine -> category -> sub-item) with deep-linkable URLs and keyboard accessibility.
- Parameter tables with per-page search and filtering; global search across descriptions, parameters, and timelines.
- Generated timeline pages under `webapp/pages/timelines/`.

`content/timeline_configs/` contains a few extra task configs (e.g. ML, RSAC, SART, SRT, SS, TOVA) that are not in the 16-engine nav. They are not currently surfaced in the webapp.

## Troubleshooting

**Webapp stuck on "Loading...":**
```bash
node -c webapp/js/script.js                       # check JS syntax
curl http://localhost:8000/content/engines.json | head -c 200   # verify data is reachable
```

**`webapp/content` symlink missing** (a fresh checkout or a clean operation can drop it):
```bash
ln -s ../content webapp/content
```

**Script import or path errors:** run scripts from the repo root, or use `make build`.
