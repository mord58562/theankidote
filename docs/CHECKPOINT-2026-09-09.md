# Checkpoint - 2026-09-09

Rob: "continue work on the ankidote from where you got cut off last
night, note the multiple errors from the cloud agent overnight."

## Starting state, verified

- `main` clean and level with `origin/main` at `8c2cb00`.
- 203 tests green across the five suites, run as plain scripts.
- Add-on 2.6.2, released on GitHub as `v2.6.2` with the package
  attached. Content channel at `08.09.2026.12`.
- Library: 826 conditions, 1,161 drugs, 436 acronyms, 55 descriptive;
  1,945 `NEW_CONDITIONS`, 2,769 `RICH_SUMMARIES`.

## The overnight cloud failures - diagnosed and fixed

Six consecutive fires from 03:23 UTC on 2026-09-08 produced nothing.

- **Five aborted at the Section 0 integrity check.** 70c0e01 (11:42 on
  2026-09-08) legitimately edited `.remote-agent-context.md` to fix the
  f-string corruption bug in its own insertion recipe, and the sha256
  pinned in the routine config was never refreshed. The check did
  exactly its job. Two of the aborted runs diagnosed it correctly and
  pushed a notification.
- **One died on a five-hour rate limit** (06:25 UTC), contending with
  the local session. Not a defect.

Read the diff of 70c0e01 before trusting it: two coherent changes, the
`json.dumps` fix and a version line. No injected instructions.

### Fixed

- [x] A pre-commit hook (`tools/git-hooks/`, installed via
      `install.sh`) prints the new digest and refuses a commit that
      stages `.remote-agent-context.md`, until the author confirms the
      routine was refreshed with `ANKIDOTE_CONTEXT_OK=1`. The failure
      is otherwise silent for hours and costs a day of content.
- [x] Context file staleness: it claimed the add-on was 2.5.0 (it is
      2.6.2) and carried the routine-setup snapshot from 2026-09-03
      (892 primaries, ~975 summaries, AnkiWeb 2.3.3) against a library
      three times that size.
- [x] Routine config updated: new digest
      `b8d827de7f60ca99517c1b8e061f707c9ace899ee6d2eaf880f5278fb5bac75f`,
      model still `opus`, MCP connector preserved.
- [x] The routine prompt still carried the **old buggy `fmt()`** - the
      exact f-string interpolation fixed everywhere else. Steps 3-5 now
      point at `tools/verify_batch.py` and `tools/merge_batch.py`,
      which already enforce budgets, banned characters, labels,
      duplicate names/aliases and the matcher-based coverage check.
      Step 6 also now runs the suites as scripts, since
      `unittest discover` and `pytest` both fail to collect.

## Gap re-measurement, 2026-09-09

`triage_gaps.py` against content `08.09.2026.12`:

| module | raw | genuinely missing | covered under another name |
|---|---|---|---|
| Medicine-1 | 163 | 59 | 104 |
| O&G | 125 | **99** | 26 |
| Paediatrics | 87 | 41 | 46 |
| Psychiatry | 85 | 29 | 56 |

Psychiatry fell 45 to 29 on the 2026-09-08 psychotherapy, law and
rating-scale batch. **O&G is untouched at 99 and is the whole priority.**

## Phases

- [x] 1. Diagnose the overnight failures; fix the cause.
- [ ] 2. O&G content batch, parallel drafting agents.
- [ ] 3. verify_batch, merge_batch, build, suites green.
- [ ] 4. Publish the content channel; re-measure; refresh the routine
      snapshot if the numbers moved.

## What the session actually found

Phase 2 started as a content batch and turned up two live defects
first, both from Rob's own diagnostic log rather than from the code.

### The content channel has been dead for every install

GitHub moved release-asset downloads to
`release-assets.githubusercontent.com`. The updater pins the hosts it
will follow a redirect to; that name was not among them; every client
refused every download. Rob's copy is stranded at `08.09.2026.2` while
the channel is now at `09.09.2026` - eleven publishes that reached
nobody.

Failing closed is right and the pin stays. The defect is that nothing
noticed, and the reason is sharp: `publish_content.sh` verified the
asset with `curl -sSL`, which follows a redirect anywhere, so it
reported a healthy 200 throughout. The check and the client disagreed
about what "reachable" means. Publishing now fetches through
`_updater._fetch`, and a test follows the live redirect and asserts
where it lands. Both were proven against the old code.

**This is add-on code. It reaches users only through AnkiWeb, so until
that upload the channel stays dead for everyone, Rob included.**

### The dock diagnostic was reporting itself

`visibilityChanged` arrives synchronously from inside Qt's show() and
hide(), and both toggle paths set the mirror flag after the call - so
every ordinary toggle looked like an outside change and logged a stack
trace naming the function that had just called it. Four such pairs in
eleven minutes last night. Fixed at three call sites; the test reads
the real `__init__.py`, since a replica of an ordering constraint
tests the replica.

### The spelling rule for "fetal" was backwards

`verify_batch` listed "fetal" as a US spelling wanting "foetal". It is
RANZCOG's spelling and the library's own, 213 uses to none. The gate
rejected every correctly-spelled obstetric batch, and three drafting
agents resolved it three different ways in one afternoon.

The deeper finding: `test_vocab`'s matching rule never fired, because
`DATASETS` covers three small tables and does not reach
`RICH_SUMMARIES` at all. The 2,800 entries that are the actual popup
text had no spelling check, which is how a contradiction sat in two
files with a green suite. The ban now runs against that table too, and
it is clean under the full ruleset.

## Content

31 O&G entries merged and published as `09.09.2026`. Four agents
drafted in parallel; all 31 verified clean together with the
AnkiConnect alias check live.

About half of roughly sixty candidates were dropped as already covered
under another name. That is the matcher earning its place, and it is
now written into both the brief and the routine as the expected rate.

| module | before | after |
|---|---|---|
| O&G | 99 | **73** |
| Medicine-1 | 59 | 59 |
| Paediatrics | 41 | 41 |
| Psychiatry | 29 | 29 |

Paediatrics is the obvious next target: untouched recently, and now
above psychiatry.

## Cloud routine

Digest refreshed twice, both times in the same turn as the edit -
`b8d827de` this morning, `c4acce71` after the batch. `origin/main`
matches. The prompt now carries the current gap ranking, the
fetal/foetal ruling, the alias gaps this batch found, an explanation
of the two manifest tests that fail between a source push and a
publish, and an instruction never to touch the context file - a
drafting agent edited it today despite being told not to, with a
change that would not have run (`os.path.expanduser`, no `import os`)
and that would have silently re-broken every fire.

Per Rob, 2026-09-09: **when the Y4 work is done and the RANZCP pivot
happens, this routine gets updated with it.** Recorded in memory
against the pivot criteria, including the two things that need
deciding then - the fellowship cartridge is private, so the routine
cannot push it the way it pushes Y4 content, and whether Y4 batches
continue in parallel, which would mean two routines.

## Open for Rob

- **2.6.2 is built and unreleased.** Rob is running 2.6.1. The
  content-channel fix is not in either, so it needs a new build.
- The dock-toggle and content-channel fixes are user-visible bugfixes
  and earn a patch bump to **2.6.3**, on Rob's say-so.

## 2.6.3 shipped

Released as `v2.6.3` on GitHub with the package attached, and **Rob
pushed it to AnkiWeb on 2026-09-09**. The released asset is
byte-identical to the local build (`500ae53f`), 69 files, bundling
content `09.09.2026`.

Both fixes were verified in the shipped bytes rather than only in the
tree: the allowlist carries `release-assets.githubusercontent.com`,
and the mirror flag is set before `hide()` in the packaged
`__init__.py`.

**The content channel is unblocked for users from this release.** An
install picks the library up in the background on one launch and
applies it on the next, so Settings should read `09.09.2026` after two.

Routine digest refreshed to `439bc418` in the same turn as the version
bump, since the bump made the context file's version line stale.
Verified against `origin/main`.

## Handover from the parallel session

A second session was doing a GitHub-wide tidy-up and pushed six
commits here (README, manifest description, config.md, content/README,
changelog wording, marker.js comments). All landed before mine and
broke nothing. It has stopped writing to this tree.

It also committed my in-flight working-tree edits as `eeba07a` under
its own message. Nothing was lost, the merged state is coherent and
not duplicated, and history was left alone rather than rewritten - a
slightly wrong author line is the better trade. Both sessions have
written the lesson into memory: stage by explicit path in any repo Rob
may have two sessions on, and account for every modified file in
`git status` before committing.

Two findings it handed over were checked and **neither is a defect** -
see the config-key commit. The real gap was that nothing was checking,
which is now a scanning test.

## Next

O&G is still the worst module at 73. Paediatrics at 41 is the second
target and has not been worked recently. The alias gaps the batch
turned up are cheap value and are named in the routine prompt:
"cervical screening", "intrauterine device", "sterilisation",
"abnormal uterine bleeding", "failure to progress", "perineal repair",
"ventouse" all resolve to nothing though the concept is covered.

---

# Second session, 2026-09-09 afternoon

Rob: continue content generation, then a list of popup, dock and
matching defects from live use with screenshots.

## Content

27 entries across O&G and Paediatrics, published as `09.09.2026.1`.
Six drafting agents ran the curriculum gap list; three drafts were
deleted as duplicates the agents could not see, and "Hypertension in
pregnancy" was rebuilt because its first draft restated Pre-eclampsia's
investigation panel. Gestational and chronic hypertension in pregnancy
had been falling through to the generic Hypertension entry, which is
non-pregnant Australian cardiovascular risk guidance.

Then `Anorexia` and 60 acronyms, published as `09.09.2026.2`.

Anorexia had no popup at all. Aliasing it to Anorexia nervosa would have
been wrong: of 20 bare uses in Rob's collection, most are the symptom,
sitting in lists beside malaise and weight loss. It has its own entry
naming both senses.

The acronyms came from a scan of the live collection - 6,088 notes,
2.38 MB of text, 517 capitalised tokens no vocabulary resolved. The
largest group is the Australian bodies the cards cite, which are
frequent precisely because they are the sources.

## The defect class

Four of Rob's reports were one shape: the pipeline resolves a surface
form, keeps the entry and throws the form away, so the popup can say
"here is an entry" but never "here is why this text resolved to it".
Brand and generic collapsed because the popup could not say which form
it matched; the schizophrenia run mislabelled because the span could not
say the form it covered was not the entry's. Both now carry the form.

`brands_au` is authored, not inferred, and is empty today. The corpus
mixes Australian trade names with American ones authored directly and
only two entries ever came through `DRUG_US_MERGES`, so there is no
provenance to recover. Absent means the neutral wording, so the list can
grow over the content channel a few drugs at a time. **This is the
obvious next content job**: 1,672 brand strings, of which the Australian
ones are the ones Rob sees on a drug chart.

## Measured, not guessed

- 63 relational aliases contain another entry's primary name, but only
  5 are harmful. The rest are single concepts - "dementia with Lewy
  bodies" should win its whole phrase. The build gate is narrow for
  that reason.
- Fixing `.cat` to a block released 8.75px a section, so the popup
  spacing went up while the over-cap backlog went DOWN: 29 conditions to
  17, 80 drugs to 72, with no content touched.
- 1,161 drugs, none with a rich override, median summary 571 chars
  against 1,048 for conditions. 223 thin entries under 400 chars appear
  in the collection and they are the common ones - prednisolone 215
  chars at 108 mentions, ceftriaxone 253, aspirin 279.

## Open for Rob

- **These are add-on code changes and are not in any released build.**
  Popup button, section links, typography, StatPearls chrome, DrugBank
  banner and self-suppression, the loading-bar watchdog, the golden and
  diamond sweeps and chips, the brand relation line, the UpToDate proxy
  fix. They earn a **minor bump to 2.7.0** on Rob's say-so. 2.6.3 is
  what is on AnkiWeb.
- Several conclusions need a running Anki: that `.scroll` scrolls and
  the button stays pinned in the Qt webview, that the tiled sweep has no
  seam, that `header nav.banner-bar` matches the live DrugBank banner,
  and that the UpToDate chip now lands signed in through the HCN proxy.

## Not done

- Extending the thin high-frequency drug entries. The recommendation is
  frequency-weighted: about 100 that are both thin and common, to
  roughly 600-750 chars, leaving the long tail. A blanket rewrite would
  worsen the below-the-fold problem that was just fixed.
- `brands_au` authoring, above.
- Medicine-1 is now the worst module at 163 raw.

---

# Third session, 2026-09-09 evening

Rob: complete anything in progress or outstanding, no new major work or
content generation.

## State found

- `main` clean and level with `origin/main` at 184cb58, the 2.7.0 bump.
- 207 tests green across the five suites, run as scripts.
- `theankidote-2.7.0.ankiaddon` built at 15:37 and unreleased.
- Content channel at `09.09.2026.2`; `data/manifest.json` matches the
  bundled library.
- Routine digest `9d5e8d8c` matches `.remote-agent-context.md` on disk
  and the value pinned in the routine prompt.

## Finished

- **The CHANGELOG had no 2.7.0 entry.** The version was bumped, the
  notes written and the package built without one. Written from the two
  code commits and the config-key commit, in the file's own style.
- **The package was rebuilt** after that commit, since `CHANGELOG.md`
  ships inside the `.ankiaddon`. Verified file by file against the
  working tree: 64 files, no difference.

## The overnight routine is being starved, not broken

Every fire today failed within eight seconds: 00:23, 03:23, 06:26 and
09:23 UTC, all `rate_limit: rejected (five_hour)`. The integrity check
never ran, because the process never got a turn. Two of the four cite a
reset at 09:40 UTC, one at 04:20.

This is contention with the local sessions, not a defect, and it is the
same cause as the single 2026-09-08 failure - the other five that day
were the stale digest, which is fixed. No content has come from the
cloud since 2026-09-08. Nothing to repair; the fires resume when the
local window is not consuming the budget.

## Open for Rob

- **v2.7.0 is not on GitHub.** The package is built and verified and the
  release notes are ready, but creating the release was refused by the
  permission classifier in this session. It needs Rob's go-ahead, and
  then the AnkiWeb upload, which is his call in any case. 2.6.3 is what
  is on AnkiWeb, so every 2.7.0 fix is still unreleased.
- The Qt-surface checks from the afternoon session are unchanged and
  still want a running Anki: that `.scroll` scrolls with the button
  pinned, that the tiled sweep has no seam, that the DrugBank banner
  selector matches, and that an UpToDate chip lands signed in through
  the HCN proxy.

## Not done, deliberately

No content this session. The next content jobs are unchanged:
`brands_au` authoring, the roughly 100 thin high-frequency drug entries,
and Medicine-1, which is the worst module at 163 raw and has not been
worked in this cycle.
