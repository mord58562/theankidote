# Checkpoint - 2026-09-08

Session task, in Rob's words: find where we were, take stock, fix
everything that comes to mind since the last AnkiWeb push, run a minor
audit focussed on bugs, fix those, then return to content generation.

## Starting state, verified

- `main` clean and level with `origin/main` at `7182bbc`.
- 164 tests green across the five suites (they run as plain scripts,
  not under pytest - `pytest tests/` fails to collect because
  `__init__.py` imports `aqt` at module scope).
- `theankidote-2.5.0.ankiaddon` at the repo root, 65 files, bundling
  content `08.09.2026`. Current against the tree; only
  `docs/CHECKPOINT-2026-09-07-evening.md` is newer, and `docs/` is no
  longer packaged.
- **2.5.0 is still awaiting Rob's AnkiWeb re-upload.**

## Carried in from 2026-09-07

Four defects were left open, all of them Qt surface that cannot be
verified without running Anki:

- [ ] A. no `loadFinished(ok=False)` handling in the UpToDate and chat docks
- [ ] B. silent failure when the chat OAuth popup cannot open
- [ ] C. no empty state on a card with no recognised terms
- [ ] D. the "Open in side panel" switch whose off-state lives only in a tooltip

Three deferrals, with reasons recorded:

- dock per-node highlighting - measured and DECLINED, closed for good
- the popup's vertical rhythm - costs content against the 900px cap
- signing the content manifest - larger than the session it arose in

Five findings rejected on inspection; do not re-raise. See the
2026-09-07 evening checkpoint for each.

## Phases

- [ ] 1. Fix A-D.
- [ ] 2. Minor audit, bug-focused, parallel dimensions. Includes the
      AI-tells pass, which is not optional.
- [ ] 3. Fix every verified finding; rebuild; suite green.
- [ ] 4. Back to content generation.
