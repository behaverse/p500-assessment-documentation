# Content gaps / TODO

A scan of the generated webapp content for placeholder ("lorem ipsum") and missing
text, to organize future content authoring. This tracks *content* gaps, not code or
UI work. Last scanned: 2026-06-15.

## 1. Timeline "About" descriptions — placeholder on every page (highest volume)

Every generated timeline page has a `<div class="timeline-about">` whose body is
**lorem ipsum**. This is the per-timeline narrative description shown under the demo
video on each timeline page. The placeholder is emitted by
`scripts/generation/generate_enhanced_timeline_pages.py`; real descriptions need to be
written (likely sourced from the timeline configs or authored per timeline).

**76 timeline pages affected** — 68 across the 16 navigable engines, plus 8 on
orphan engines (see §3).

Per navigable engine (number of timelines needing an About description):

| Engine | Pages | Engine | Pages | Engine | Pages | Engine | Pages |
|--------|-------|--------|-------|--------|-------|--------|-------|
| BCS    | 5     | NB     | 6     | RE     | 3     | SRM    | 5     |
| BM     | 5     | OC     | 2     | SMC    | 7     | TH     | 4     |
| BSAC   | 9     | OOO    | 1     | SOS    | 2     | UFOV   | 5     |
| DS     | 4     | MOT    | 5     | PC     | 2     | WO     | 3     |

Note: the rest of each timeline page (Config, Instructions, Parameters, Sample Data
section heading) is generated from real data — only the About paragraph is placeholder.

## 2. Engine descriptions — missing or stub (engines.json / Task spec.xlsx)

The `description` category text per engine (the prose on the engine landing page) is
authored in `content/Task spec.xlsx` and extracted into `engines.json`. Current state:

| Engine | Description | Action |
|--------|-------------|--------|
| MOT    | **empty (0 chars)** | Write a description |
| OC     | stub (~88 chars)    | Expand |
| PC     | stub (~137 chars)   | Expand |
| SMC    | thin (~188 chars)   | Expand |
| (others) | adequate (450–2000 chars) | — |

The companion site (https://behaverse.org/projects/cognitive-tests.html) has short,
well-written descriptions for all engines — now mirrored in the landing-page demo
modal (`ENGINE_BLURB` in `webapp/js/script.js`). These can seed the fuller engine
descriptions.

## 3. Orphan engines — timeline content exists but not navigable

These have timeline configs/pages (with lorem About sections) but are **not in the
16-engine nav**, so they are unreachable in the webapp. Decide per engine: author
content + add to nav (needs a thumbnail + demo video in `webapp/assets/engines/<CODE>/`,
which they currently lack), or remove to stop generating dead pages. See HANDOFF.md
known issue #3.

| Engine | Timeline pages | Has thumbnail/video? |
|--------|----------------|----------------------|
| ML     | 3              | no |
| SS     | 2              | no |
| SART   | 1              | no |
| SRT    | 1              | no |
| TOVA   | 1              | no |
| RSAC   | 0 (config only)| no |

## 4. To verify (not confirmed missing)

- **Sample Data links:** every timeline page has a "Sample Data" section reading
  "You can download a sample dataset here" — confirm whether a real dataset is linked
  or the link is a placeholder.
- **Parameter pages:** spot-checks look populated from `Task spec.xlsx`. Note the word
  "placeholder" appears legitimately in the Target Hit (TH) engine as a domain term
  ("stimulus placeholders", `MaxPlaceholderCount`) — not a content gap.

## Suggested order of work

1. MOT engine description (only fully-empty one).
2. Timeline About descriptions for the navigable engines, starting with the
   highest-traffic / most-timelines engines (BSAC 9, SMC 7, NB 6).
3. Expand the OC / PC / SMC engine descriptions.
4. Resolve orphan engines (author + assets, or remove).
5. Confirm Sample Data download links.
