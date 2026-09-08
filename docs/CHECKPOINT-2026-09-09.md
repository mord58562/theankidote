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
