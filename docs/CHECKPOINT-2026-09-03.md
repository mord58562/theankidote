# TheAnkiDote resume checkpoint - 2026-09-03

Written for the next Claude session so Rob can clear chat history and pick up rich-summary generation without re-doing context.

## State at end of session

- **Content channel version:** `03.09.2026` (published, live)
- **Add-on version:** `2.3.2` (unchanged - AnkiWeb-version gate is memory-locked; do not bump without Rob's go-ahead)
- **Total rich summaries:** 686
- **Ratchet:** `OVER_CAP_BUDGET = {"conditions": 79, ...}` in `tests/test_vocab.py` - **no headroom**, any new entry over 900px will fail tests
- **Char cap:** 1200 chars per rich summary (test_overrides_stay_glance_sized) - 0 entries currently over
- **Tests:** all 131 pass on `python3 -m unittest discover tests`
- **git:** all commits pushed to origin/main; tree clean

## What just shipped (this session)

Six audit files were merged from 2026-09-01 (Rob authored, agents applied):

| Audit | Substantives applied | Commit |
|-------|----------------------|--------|
| oncology/screening | 3 | 1b904bf (pre-session) |
| antimicrobial | (pre-session) | e4b7e85 (pre-session) |
| neuro non-acute | 12 | e5c5145 |
| paeds/O&G/psych | 6 (Kawasaki + Wernicke skipped, done elsewhere) | 678b736 |
| GI/hep/renal/endo | 10 | 0ac6955 |
| chronic first-lines | 11 | 56d2d40 |
| rheum/derm/MSK/ENT/ophtho | 21 (Kawasaki here) | 0b2699b |
| emergency dose-critical | 0 substantive (audit finding: all clean) | n/a |

Then commit `3687f3d` trimmed 18 audit-touched entries to keep the 900px ratchet at 79, and fixed 10 unrecognised section labels the audit rewrites had introduced (`First-line:`, `Local invasion:`, `Newer:`, `Major:`, `Minor:`, `Stigmata:`, `Antibody panel:`, `AOM:`, `Otoscopy:`, `Primary techniques:`, `HINTS:`, `Miller Fisher variant:` - all inlined as sentence prose).

Published as content-`03.09.2026` (commit 6394e91).

## What did NOT get done (worth knowing before adding more popups)

- **MINOR issues sections** in every 2026-09-01 audit were deliberately NOT applied (only SUBSTANTIVE errors were fixed). Each audit file has a `### MINOR issues` list - dozens of them across the 8 files. Deferred pool if Rob wants to polish existing entries later; not blocking new-entry work.
- **UNVERIFIED items** flagged in the emergency-dose audit (digoxin, iron, salicylate, lithium, malignant hyperthermia thresholds) need eTG verification when Rob has access.
- **~1030 nearby line changes vs pre-session HEAD** in `content/_rich.py` came from a mixture of the audit-fix cherry-picks and this session's trims; nothing should be surprising, all AU-substantive content verified preserved (script in git log for `3687f3d`).

## AnkiWeb-ready file

- **Path:** `~/theankidote/theankidote-2.3.2.ankiaddon` (1.8 MB)
- **AnkiWeb listing:** https://ankiweb.net/shared/info/720072719
- **Version bump gate:** manifest.json add-on version stays put until Rob says he's pushing to AnkiWeb (memory rule). Content-channel version bumps freely - and just did (`03.09.2026`).
- **Threshold for next add-on bump:** patch (2.3.2 -> 2.3.3) if a visible bugfix ships; minor (2.3 -> 2.4) if a new feature; major (3.0) if schema/UI overhaul. Nothing this session qualifies as visible bugfix beyond what's already in 2.3.2; when the next code/UX change lands, Claude should flag Rob before build_ankiaddon.

## Resuming: "more popups" = more rich-summary entries in RICH_SUMMARIES

### Working strategy
1. **Audit inbox first** (memory rule): `~/theankidote/data/inbox/` - if anything there, merge before generating.
2. **Ratchet has no headroom** (79/79). Every new entry must render `<= 900px` per the estimator in `tests/test_vocab.py:PopupHeightBudget`. If an entry needs >900px, either trim other prose in that entry to stay under, or trim an existing over-cap entry down (bringing ratchet 79 -> 78) so the new one can slot in above cap. Do not raise the ratchet.
3. **Char cap 1200** - target median ~1050.
4. **Section labels** must be from the whitelist in `tests/test_vocab.py:KNOWN_LABELS`. Common ones: `Sx`, `Ix`, `Mx`, `Note`, `Red flags`, `Causes`, `Types`, `Features`, `Clinical features`, `Diagnosis`, `Management`, `Complications`, `Prevention`, `Screening`, `Aetiology`, `Risk factors`, `Prognosis`, etc. When adding a label the whitelist does not know, inline it as sentence prose instead.
5. **Priority gaps** listed in `docs/priority-gaps-2026-08-31.md` if still relevant (verify not already covered by batches 51-57 or the audit fixes just applied).
6. **Anki frequency** drives priority - see `all_rich_summaries_2026-09-01.json` and `categories_2026-09-01.json` in `audit/` if a full-collection scan needs re-running.
7. **Style rules** (Tier 1, all locked in memory):
   - No em-dashes anywhere - use space-hyphen-space.
   - Never "Pabrinal" (Pabrinex).
   - Never "ATSI" - full phrase "Aboriginal and Torres Strait Islander" for general references; only the applicable half for a specific group.
   - Never use the c-word (dead metaphor) - use live/core/primary/main.
   - Australian spellings only (oedema/anaemia/oesophag/tumour/diarrhoea/leukaemia/ischaemia/aetiology/paediatric).
   - Preserve period-vs-semicolon rhythm of surrounding entry; semicolons in Mx blocks can promote clauses to bulleted lines and inflate rendered height.

### Publish-flow when adding new popups
1. Edit `content/_rich.py` - add new keys to `RICH_SUMMARIES`.
2. Run `python3 -m unittest discover tests` - must pass 131/131 before committing.
3. Commit with a batch-descriptive message (`Batch 58: N rich summaries - <name-list>`).
4. Auto-push per memory rule.
5. Publish content channel: `bash tools/publish_content.sh` (rebuilds library.json, creates a GitHub release tag `content-<date>`, commits + pushes updated `data/manifest.json`).
6. Content channel updates are `data`-only and do NOT touch the AnkiWeb version.

### File locations Claude should know
- Rich summaries source: `~/theankidote/content/_rich.py`
- Build script: `~/theankidote/tools/build_library.py`
- Publish script: `~/theankidote/tools/publish_content.sh`
- Add-on build: `~/theankidote/build_ankiaddon.sh`
- Tests: `~/theankidote/tests/test_vocab.py` (all 131 tests) - loads content via `data/library.json`, so **`build_library.py` must run before tests to catch changes to `_rich.py`**.
- Untracked audit artefacts (large): `audit/all_rich_summaries_2026-09-01.json` (all 686 entries dumped), `audit/categories_2026-09-01.json` (frequency + category), `audit/mechanical_sweep_2026-09-01.txt` (mechanical audit clean).

### Worktrees left over
Four locked worktrees under `.claude/worktrees/agent-*` from this session's parallel audit-fix agents. The harness cleans them up automatically; do not touch unless something is stuck.

## One-liner resume trigger

Rob's memory has this trigger: `"continue work on mcqs"` -> A to E MCQ bank. For TheAnkiDote there is no analogous trigger; the natural prompt is `"continue work on the ankidote"` (worked cleanly at session start today). If Claude sees that phrase, read this checkpoint first.
