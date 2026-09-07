# Checkpoint - 2026-09-07, evening session

Picks up from `HANDOVER-2026-09-07.md`. That document's open thread 1
(Medicine and Psychiatry framework gapfills never finished) is what this
session is closing.

## Starting state, verified

- `git status` clean, `main` level with `origin/main` at `310e12a`.
- `theankidote-2.5.0.ankiaddon` at the repo root, 83 files, carrying
  `data/library.json` at content `07.09.2026.9`. Manifest inside the
  package matches the manifest on disk. Still awaiting Rob's AnkiWeb
  push, so everything below folds into 2.5.0.

## The scratchpad survived

The temp directory the handover warned would not survive did survive.
Its contents are now in a durable location outside the repo:

    ~/Downloads/frameworks/_extracted/

Deliberately NOT in the repo: `fw_*.json` are extracted Y4 curriculum
item lists, and the repo auto-pushes to a public remote.

`framework_coverage.py` was re-pointed at that directory and re-run
against the current library:

| module | items | covered | gap | % |
|---|---|---|---|---|
| Medicine-1 | 597 | 360 | 237 | 60% |
| O&G | 253 | 125 | 128 | 49% |
| Paediatrics | 238 | 147 | 91 | 61% |
| Psychiatry | 192 | 76 | 116 | 39% |
| TOTAL | 1280 | 708 | 572 | 55% |

That is the RAW scorer, which over-reports: it counts an item as a gap
whenever the framework's wording fails to match, including when the
entry exists under another name. The triage lists resolve that.

## What the work actually is

Cross-referencing the current gaps against the triage verdicts, with
nothing left untriaged in either module:

| module | alias needed | genuinely missing | not an entry |
|---|---|---|---|
| Medicine-1 | 121 | 75 | 41 |
| Psychiatry | 46 | 49 | 21 |

## Phases

- [ ] 1. `CONDITION_ALIASES` overlay in `content/_rich.py`. Conditions
      pass through `build_library.collect()` untouched from
      `library.json`, so there is no authoring route for an alias on an
      existing condition - the same gap acronyms had until
      `content/_new_acronyms.py` was added earlier today. Same fix,
      same validation shape as `DRUG_ALIASES`.
- [ ] 2. Apply the 167 alias additions through it.
- [ ] 3. Merge the 124 new entries (10 parallel authoring agents, one
      per framework topic, drafts to `_extracted/drafts/*.json`).
- [ ] 4. `verify_batch.py`, then `merge_batch.py`, then
      `build_library.py`, then `tests/test_vocab.py`.
- [ ] 5. Publish content, rebuild the `.ankiaddon`, commit and push.

## Traps carried forward from the handover

- Fetch before publishing; the cloud routine pushes to this branch.
  Resolve `_rich.py` conflicts with `merge_batch.py`, never by hand.
- Do not loosen `pearls/_ncbi._score`.
- `OVER_CAP_BUDGET["conditions"]` is a ratchet at 29. Every new entry
  must estimate under 900px or the suite fails.
- Library is 6.18 MB against the 8 MB ceiling that every pre-2.5.0
  client carries. 124 entries will move that. Watch the publish
  script's warning.
