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


## The audit, finished

Seven passes ran in parallel: AI tells, future-proofing, usability,
simplicity, speed, security, and a blind from-scratch design (Phase 4,
which is what makes this a full audit rather than a light one). Every
finding below was verified against the code before it was acted on.

**The headline: 2.5.0's flagship fix did not work.** The release notes
say popups stopped claiming StatPearls articles they do not have. Two
independent faults meant they never stopped. `_reviewer.py` dropped the
`link` key between the builder that computes it and the span that reads
it, so `isArticle` was always false; and `marker.js` set the button
label correctly and then overwrote it unconditionally from a block four
releases older. The badge said "The AnkiDote" on articles that exist,
the button said "Open article" on articles that do not. Exactly
inverted.

Nine more real defects fixed, listed in the CHANGELOG under 2.5.0.

**Three findings were rejected on inspection**, and the reasoning is
now in the files so the next audit does not re-raise them:

1. The Settings window writing on close is deliberate, and says so in a
   comment directly above the writes.
2. The rich merge writing into `new_conditions` in place is safe. The
   build re-sources them from `content/_rich.py`, where the stubs are
   filled from `RICH_SUMMARIES` at import, so an edited override still
   takes effect. Two separate audits flagged this one.
3. The `!=` schema gate is correct. A bump means an existing key
   changed meaning, so a newer client genuinely cannot read an older
   library; refusing both directions is the contract, not an oversight.

### Deliberately not done

**The dock's per-node highlighting.** Measured: `highlight_text` is
called once per text node, 105 times on a 66 KB article, 16.9 ms
against 5.8 ms for a single pass, and up to 620 ms of blocked main
thread at the 4000-node cap. The fix is to resolve once over the joined
text and run only the substitution per node. It is the largest
remaining win and it is a rewrite of the hot path, which cannot be
runtime-tested from here - the add-on is never installed locally and
Anki is never restarted. Shipping an untested restructure of the
highlighting path into a release about to be published is worse than
carrying the cost one more release. The number is recorded; the
handover's old "2.5 ms, no concern" line is corrected in place, since
it measured a function nothing calls.

**The popup's vertical rhythm.** Fourteen spacing values in one box.
Snapping them to a scale is the ordinary fix and it costs content: the
cap is 900px, 29 summaries are already over it, `PopupHeightBudget`
mirrors this CSS line for line, and the ratchet only allows the count
to fall. The colour, weight, radius and register fixes were all free
and were made; the spacing was not.

**Signing the content manifest.** Two reviews arrived at this
independently. The hash validates the manifest's own payload, so it
proves the download was not truncated and nothing about who wrote it.
The host is pinned now, which closes the config-repointing hole; a
signature against a key in the package is the real answer and is a
larger change than belongs here.

### From the blind design, worth carrying

The from-scratch design (`$CLAUDE_JOB_DIR/tmp/from-scratch-design.md`,
653 lines, written without reading this tree) converged on the current
architecture more often than not: the engine/library split, the
case-sensitive index for acronyms, refusing to match ordinary words.
Two divergences are worth recording.

1. **`core/` may not import `aqt`.** Today `pearls/_reviewer.py`
   imports `aqt` at module scope, so none of the matching logic can be
   exercised without Anki. This is not theoretical: verifying one of
   this session's own fixes failed with `ModuleNotFoundError: aqt` and
   had to be checked through `_conditions` instead.
2. **A signed feed and a payload carrying no HTML.** The second half
   matters less here - every path from library text to the DOM is
   escaped, and that was traced end to end this session - but the
   first is the item above.


## Second pass, same evening

The remaining verified findings were applied: the popup-click path
collapsing rather than hiding the article list, the chosen article
being remembered on both paths and forgotten when deliberately left,
the popup surviving a question-to-answer flip, the popup running off
the bottom of the window, and the updater telling nobody when a check
failed. `_make_shortcut` was consolidated from three copies into
`_dock_layout.make_shortcut`.

**That consolidation introduced a NameError and the suite passed
anyway** - the moved function referenced `_log` and its new home did
not import it. Almost nothing in this tree can be imported under test,
because it needs Anki, so a missing name is invisible to 155 passing
tests and arrives the first time a shortcut fails to bind. The suite
now runs pyflakes' undefined-name check over the package. The names
`_rebind_theme` and `_theme.refresh` write into `globals()` are
allowlisted one by one rather than the files being skipped, so a
genuine undefined name in those files still fails. Proven against the
bug that prompted it.

That is the general lesson from this audit worth carrying: the test
suite covers content and pure logic well and covers the Qt surface not
at all, so anything touching a widget, a hook or a signal is verified
by reading and by static analysis only. It is also why the dock
highlighting rewrite stayed deferred.

## What is left

- **Rob's, and only Rob's**: the Qt runtime behaviour. The sidebar
  collapse and restore, the remembered article, the shortcut binding
  after the `_dock_layout` move, and the popup positioning all want
  exercising from the built package before it goes up.
- The three deferred items above: dock per-node highlighting, the
  popup's vertical rhythm, and signing the content manifest.
## Third pass

The smaller findings are done: the config drift (with a test holding
`config.json`, `_config._DEFAULTS` and `config.md` together, and
distinguishing settings from managed state rather than demanding they
match exactly), all eight updater failure messages, the load-failure
page that asserted NCBI rate-limiting as the cause, the duplicated
"Reference popups" label, and the Tools-menu module toggles, which
wrote a value and said nothing while the Settings window redrew the
toolbar and named the module needing a restart.

Two more findings rejected on inspection, bringing the total to five
across the audit. The first run opening UpToDate to trigger SSO is not
an unprompted login wall - it fires only if the user accepted the setup
dialog and left the module enabled seconds earlier. And `config.md` is
correct that `debug` logs to the debug console; the always-on
diagnostic file is a separate mechanism, and that was the omission.

Rejecting one finding in five is worth noting for the next audit: the
reports were strong, and the ones that did not survive were all cases
where the reasoning was sound but a comment, a guard or a caller
elsewhere already settled it. Read the surrounding code before acting
on any of them.

## What is left

- **Rob's, and only Rob's**: the Qt runtime behaviour.

  **Confirmed by Rob, 2026-09-07:** the Relevant articles section's
  collapse and restore behaves well. That is the header-toggle path,
  which shipped in the first 2.5.0, so it validates the pattern rather
  than this session's change - the popup-click path was still calling
  `hide()` and only collapses in the rebuilt package. Good evidence for
  the change; not a test of it.

  Still unexercised: the popup-click path collapsing rather than
  hiding, the remembered article surviving a restart and being cleared
  by Home, keyboard shortcuts still binding after the `_dock_layout`
  move, popup positioning near the bottom of the window, and the two
  new tooltip paths (a failed content update, and a module toggled from
  the Tools menu).
- The three deferred items: dock per-node highlighting, the popup's
  vertical rhythm, and signing the content manifest.
- Four findings deliberately left, all of them Qt behaviour that cannot
  be verified without running Anki: no `loadFinished(ok=False)`
  handling in the UpToDate and chat docks, a silent failure when the
  chat OAuth popup cannot open, no empty state on a card with no
  recognised terms, and the "Open in side panel" switch whose off-state
  lives only in a tooltip.
