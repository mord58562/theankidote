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

## Audit findings, 2026-09-08

Seven dimensions ran in parallel: the StatPearls dock, the two browser
docks, the pearls engine, the add-on lifecycle, marker.js, the build
and publish pipeline, and the AI-tells pass. Six have reported.

### Fixed and pushed

- [x] `data-sp-utd` was `"[]"` on every span ever written.
      `_condition_terms` did not carry the key. 824 of 826 conditions
      have chips; none had ever drawn. Third key this dict has dropped.
      Regression test added, and proven to fail against the old code.
- [x] The chat adblock JS was a syntax error from the day it was
      written. `repr().replace()` instead of `json.dumps`. Proven with
      `node --check`.
- [x] The DrugBank auto-jump could never fire: `_finish_good_load`
      cleared `_pending_url` before `_maybe_autojump` read it.
- [x] The retry budget was per session, not per navigation.
- [x] Home was connected to `_go_home` twice.
- [x] The article list did not follow the card, and a popup click wrote
      a transient collapse into a stored preference.
- [x] "Open in side panel" is two radios; its off-state was a tooltip.

### Verified, still to fix

Chat / UpToDate: a selection of 8 characters or fewer is pasted twice
into the composer (proven arithmetically - this is most medical terms);
the `QWebEngineProfile` is created before the pages that use it and so
is destroyed first; provider matching is a raw substring test against
the whole URL; the chat dock has no working reload behind a button
tooltipped "Reload"; the chat dock never calls `_dock_layout.arrange`;
UpToDate has its own older copy of that logic; `_PopupShunt` hands an
unvalidated URL to the system browser.

StatPearls dock: `_cache_resolved` attributes an unrelated URL to a
stale `_pending_term` and persists it; `_on_article_chosen` bypasses
both term resolution and the URL safety check, and can load UpToDate
into the pearls profile; `_judge_failed_load` skips highlighting; the
`_set_site` no-op branch wipes the remembered article; a double-click
in the list fires twice.

Lifecycle: `_extras.py` rewrites Anki's `meta.json` on every answered
card; `_on_theme_change` and `_on_js_message` import modules the user
disabled, resurrecting a dead toolbar button; the UpToDate dock is
never rebuilt after a profile switch; the restart-needed tooltip is
dead in the direction that matters; the Tools-menu checkmarks never
refresh; the config cache is never invalidated.

marker.js: light mode overrides the per-source accent; `_aimUntil`
leaks past `_hideTip`; a double-click on a term opens the article.

Tests: the undefined-name guard reads only pyflakes' `out` stream, so a
file that fails to PARSE passes it - in a tree where most files cannot
be imported under test.

AI-tells: 181 em-dashes in `audit/` (public repo, not packaged); a raw
exception string reaches a user-facing toast; the panel docstring names
a paid competitor; one switch has two different names.


## Progress, end of the fixing phase

Committed and pushed so far, each verified before it was acted on and
most of them proven with a repro:

- The content channel was dead between publishes. A bare
  `build_library.py` stripped the url from `data/manifest.json`, which
  is the live pointer every client polls; 19 of the last 40 commits
  touching that file carried none. The build no longer writes the
  manifest unless it is publishing, and the test that guarded it - whose
  assertion sat inside `if "url" in man:` - now fails when the key is
  absent.
- Three features that had never once run: the UpToDate chip row on every
  condition popup (824 of 826 entries), the chat adblock (a JavaScript
  syntax error since it was written), and the DrugBank auto-jump.
- `_extras` rewrote Anki's `meta.json` on every answered card.
- Two paths imported modules the user had disabled, leaving a toolbar
  button that does nothing for the rest of the session.
- The docks: an 8-character-or-shorter selection was pasted twice; a
  substring test decided which provider a URL belonged to; the reload
  button could not reload; the profile was destroyed before its pages.
- The authoring pipeline could write a `_rich.py` that does not parse,
  and could turn a bare `"PID"` into three one-character aliases.
- A failed publish left `data/` poisoned so the retry refused itself.
- The undefined-name guard passed any file that failed to PARSE, in a
  tree where most files cannot be imported under test at all.
- 181 em-dashes, the residue of an earlier pass, one paid competitor
  named in a docstring, four names for one surface, and a toast that
  showed the reader a urlopen traceback.

Still in flight when this was written: the matching engine (aliases
never highlight; a literal `<` in text kills highlighting from that
point on) and the remaining StatPearls panel findings.
