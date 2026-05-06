# The AnkiDote - migration plan

Status snapshot of the consolidation of AnkiPearls + AnkiDate into one
add-on. Maintained as the source of truth while the migration progresses;
delete once consolidation is complete.

## End state

```
theankidote/
├── manifest.json             # done
├── config.json               # done - unified keys with prefix `uptodate*`
├── config.md                 # done
├── MIGRATION.md              # this file
├── __init__.py               # top-level entry: registers BOTH toolbar
│                             # buttons + hooks; calls pearls.setup()
│                             # and uptodate.setup()
├── _config.py                # unified config helper (one source of truth
│                             # for both pearls and uptodate)
├── _panel_pearls.py          # ex-AnkiPearls _panel.py (StatPearls/DB)
├── _panel_uptodate.py        # ex-AnkiDate dock (UTD authenticated)
│
├── pearls/
│   ├── __init__.py           # exposes setup(); no module-level hooks
│   ├── _acronyms.py          # verbatim copy from ankipearls/
│   ├── _conditions.py        # verbatim copy from ankipearls/
│   ├── _drugs.py             # verbatim copy from ankipearls/
│   ├── _reviewer.py          # adapted: imports rewritten
│   └── _searcher.py          # verbatim copy from ankipearls/
│
├── uptodate/
│   ├── __init__.py           # exposes setup(); body adapted from
│   │                         # uptoanki/__init__.py
│   └── (sub-modules to be split later)
│
└── web/
    ├── marker.js             # verbatim copy from ankipearls/web/
    └── logo.png              # copy from uptoanki/logo.png
```

## Behavioural goals (preserve from current pair)

- ✅ **Two toolbar buttons**: crown (StatPearls/DrugBank) and UTD logo.
  Each toggles its own dock independently.
- ✅ **Two web profiles**: `theankidote-pearls` (StatPearls webview) and
  `theankidote-uptodate` (institutional-SSO authenticated browser).
  Profile names changed from the old addons so cookies don't leak; users
  with the old `uptoanki` profile re-authenticate once on first launch
  of the new addon.
- ✅ **Cross-source chip routing**: in the popup tooltip, clicking a
  StatPearls/DrugBank URL opens the pearls panel; clicking a UTD chip
  opens the UTD panel (so the institutional session is used).
- ✅ **UpToDateless mode (`enableUpToDate=false`)**:
  - UTD toolbar button hidden
  - UTD shortcut not registered
  - UTD chips stripped from popups
  - UTD-only condition entries skipped
  - StatPearls + DrugBank fully unaffected
- ✅ **One-time prompt** when `enableUpToDate` is null (first run after
  install/upgrade).
- ✅ **Activity-gated UTD keepalive** (already implemented in uptoanki;
  carried over).
- ✅ **Renderer crash recovery**, popup shunt, certificate handling for
  the UTD profile (carried over from uptoanki).

## Files to migrate (next session)

Order matters - bottom-up dependency.

| Source | Destination | Edits required |
|---|---|---|
| `ankipearls/_searcher.py` | `theankidote/pearls/_searcher.py` | None (or adjust internal import paths). |
| `ankipearls/_acronyms.py` | `theankidote/pearls/_acronyms.py` | None. |
| `ankipearls/_drugs.py` | `theankidote/pearls/_drugs.py` | None. |
| `ankipearls/_conditions.py` | `theankidote/pearls/_conditions.py` | None. |
| `ankipearls/_config.py` | `theankidote/_config.py` | Merge UTD-specific keys; adjust `_PKG` resolution. |
| `ankipearls/_reviewer.py` | `theankidote/pearls/_reviewer.py` | Imports change `from . import` → `from .. import`. |
| `ankipearls/_panel.py` | `theankidote/_panel_pearls.py` | Profile name → `theankidote-pearls`. |
| `ankipearls/web/marker.js` | `theankidote/web/marker.js` | None. |
| `uptoanki/__init__.py` | `theankidote/_panel_uptodate.py` (browser) + `theankidote/uptodate/__init__.py` (setup) | Split into panel widget + setup(); profile name → `theankidote-uptodate`; toolbar registration moved to top-level `__init__.py`. |
| `uptoanki/logo.png` | `theankidote/web/logo.png` | None. |
| `ankipearls/__init__.py` | `theankidote/__init__.py` | Merge with `uptoanki/__init__.py`'s setup logic. Two toolbar buttons. UTD button gated on `enableUpToDate`. Cross-source URL routing absorbs the current `_open_in_uptoanki` shim. |

## Shim removal (after migration verified)

Once The AnkiDote is installed and verified:

1. Remove the cross-addon delegation shim in
   `ankipearls/__init__.py::_open_in_uptoanki()` (no longer needed -
   the new addon handles routing internally).
2. Mark the two old add-ons as deprecated in their manifests.
3. The user uninstalls AnkiPearls and AnkiDate; The AnkiDote remains.

## Portfolio update (after consolidation complete)

Once The AnkiDote is shipping:

- Replace the two separate listings (project 03 AnkiDate + project 04
  AnkiPearls) in `~/portfolio/index.html` with a single
  "The AnkiDote" entry.
- Update `~/portfolio/update.sh`: replace the AnkiDate + AnkiPearls
  zip-rebuild blocks with one for `~/Downloads/theankidote/`. Update
  the project-list comment that prevents Claude from re-adding the
  old entries.
- Commit + push to live.

## ToS posture (unchanged)

- StatPearls = NCBI Bookshelf, public domain. ✅
- DrugBank = free tier, links only. ✅
- UpToDate = paywalled. The AnkiDote never scrapes. The unified
  approach is identical to what AnkiDate already does: an authenticated
  browser the user logs into themselves; an activity-gated keepalive;
  no programmatic content extraction. Linking out (via UTD chips) is
  fine - same as a bookmark.

## Status

### Code complete (this session)

- [x] Skeleton directory created
- [x] `manifest.json` - `license: GPL-3.0-or-later`, `homepage`, author=mord58562
- [x] `config.json` - unified keys with `uptodate*` prefix
- [x] `config.md` - cost/access callout (add-on free, UTD is paid third-party)
- [x] `MIGRATION.md` (this file)
- [x] `LICENSE` (GPL-3.0)
- [x] SPDX headers on all 10 .py files; `Copyright (C) 2025 mord58562`
- [x] Verbatim file copies: pearls/_acronyms.py, _conditions.py, _drugs.py,
      _searcher.py, web/marker.js, web/logo.png
- [x] `_config.py` - unified config helper with `set_value()` for one-time prompt
- [x] `pearls/_reviewer.py` - imports adapted (`from .. import _config`)
- [x] `_panel_pearls.py` - profile renamed to `theankidote-pearls`, imports adapted,
      `_reviewer` access via `from .pearls import _reviewer`
- [x] `uptodate/__init__.py` - profile renamed to `theankidote-uptodate`, all
      `_cfg().get(...)` reads migrated to unified `_config.get(...)` with
      prefixed keys; toolbar title rebranded to "The AnkiDote - UpToDate";
      auto-registration via `gui_hooks.main_window_did_init` removed (top-level
      controls invocation so it can be gated)
- [x] Top-level `__init__.py` - credits + medical disclaimer + cost/access notes;
      pearls toolbar (crown) + UpToDate toolbar (logo) both registered;
      pycmd handler with `tad_open` / `theankidote_pearls_toggle` namespace;
      first-run UpToDate prompt; UTD subpackage gated on `enableUpToDate != False`
- [x] `web/marker.js` - `pycmd("ap_open:...")` → `pycmd("tad_open:...")` so the
      new namespace doesn't collide if a legacy install lingers
- [x] No cross-package imports of `ankipearls` or `uptoanki` anywhere - addon
      is fully self-contained
- [x] Syntax check: all 10 .py files parse, marker.js parses

### Remaining (user action)

- [ ] Test The AnkiDote in Anki - uninstall both legacy add-ons first to avoid
      hook double-fire. Verify both toolbar buttons appear, popups work,
      UpToDate dock authenticates against your institutional SSO.
- [ ] Once verified, **delete the legacy directories** so they cease to exist:
      `rm -rf ~/Downloads/ankipearls ~/Downloads/uptoanki`. The user previously
      asked that the unified add-on not depend on either; this finalises that.
- [ ] Code review pass (optimisation, security/ToS, new features) - pending,
      will run once the user signals install verification.
- [ ] Replace AnkiDate + AnkiPearls portfolio entries with one
      "The AnkiDote" entry; update `update.sh` zip rebuilds and project list.
- [ ] Push portfolio commit to live.
