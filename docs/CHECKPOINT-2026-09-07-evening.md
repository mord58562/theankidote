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

- [x] 1. `CONDITION_ALIASES` overlay in `content/_rich.py`. Conditions
      pass through `build_library.collect()` untouched from
      `library.json`, so there is no authoring route for an alias on an
      existing condition - the same gap acronyms had until
      `content/_new_acronyms.py` was added earlier today. Same fix,
      same validation shape as `DRUG_ALIASES`.
- [x] 2. Alias additions applied - 43 over 27 entries, not 167. Of the
      167 triaged rows, 92 already resolved (the matcher handles a
      qualified framework phrase against its entity unaided), most of
      the rest was curriculum phrasing no card carries, and several
      were wrong targets. Committed as `f4fb4b7`.
- [x] 3. 116 entries merged. 10 agents, one per framework topic.
- [x] 4. Verified, merged, built, suite green (150 tests).
- [x] 5. Published `07.09.2026.11`, then `07.09.2026.13` for a
      restored alias. 2.5.1 built, committed and pushed.

## Traps carried forward from the handover

- Fetch before publishing; the cloud routine pushes to this branch.
  Resolve `_rich.py` conflicts with `merge_batch.py`, never by hand.
- Do not loosen `pearls/_ncbi._score`.
- `OVER_CAP_BUDGET["conditions"]` is a ratchet at 29. Every new entry
  must estimate under 900px or the suite fails.
- Library is 6.18 MB against the 8 MB ceiling that every pre-2.5.0
  client carries. 124 entries will move that. Watch the publish
  script's warning.


## Outcome

Framework coverage on the raw scorer:

| module | before | after |
|---|---|---|
| Medicine-1 | 60% | 72% |
| Psychiatry | 39% | 55% |
| TOTAL (four modules) | 55% | 63% |

Read that as a floor, not a measurement. The scorer requires the matched
entity to share the framework item's head noun, so it counts an item as
a gap whenever the curriculum's phrasing differs from the entry's title
even though `resolve()` finds it. Of the 249 items still scored as gaps
across the two modules, 21 resolve to nothing at all, and all but a
handful of those are covered under another name - 'Organic illness
presenting as psychiatric illness' by `Organic causes of psychiatric
symptoms', 'Interpretation of coagulation tests' by `Coagulation test
interpretation'. The residual real gap is small.

Deliberate non-entries, so they are not re-proposed next time:
'Cough' (would highlight everywhere; `Chronic cough in adults' exists),
'Inflammatory versus non-inflammatory joint pathology' (the `Arthritis'
entry already carries the discriminator, and fires on the commoner
word), and 'Lived experience of mental illness' (the entry written is
`Lived experience workforce', which is a narrower thing - an alias would
mislead).

## Opened during the session

**2.5.0 is rebuilt and awaiting a re-upload.** Rob confirmed 2.5.0
reached AnkiWeb mid-session, and then corrected course: republish 2.5.0
rather than open 2.5.1. The 2.5.1 that had been built was rolled back -
manifest returned to 2.5.0, its changelog section folded into 2.5.0's
`### Fixed`, and `WHATS-NEW-2.5.1.md` folded into `WHATS-NEW-2.5.md`.
`theankidote-2.5.0.ankiaddon`, 66 files, bundling content
`07.09.2026.13`.

Re-uploading the same version number reaches users: Anki decides an
add-on has an update from AnkiWeb's modification time on the listing,
not from the version string in `manifest.json`.

Three things worth carrying forward:

1. **`docs/` and `audit/` are no longer packaged.** This file included.
   If a future session wants a note to reach users, it goes in
   `WHATS-NEW-*.md`, which is still shipped.
2. **Do not hand `build_library.py` an explicit `--version`** unless
   publishing. The preflight in `publish_content.sh` compares against
   the local manifest, which the build rewrites, so a hand-build at
   version N makes the real publish of N refuse itself as stale. The
   dry-run case is fixed; this one is workflow, not code.
3. **`_extracted/` outside the repo** holds the framework item lists,
   the triage, the drafts and the coverage script. It is deliberately
   not in the tree - the extracted curriculum lists are institutional
   material and this remote is public.
