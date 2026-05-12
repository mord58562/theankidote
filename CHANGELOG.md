# Changelog

All notable changes to The AnkiDote.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-05-12

### Added

- Preclinical / basic-science term library (344 entries) covering
  physiology, biochemistry, microbiology, immunology, pathology,
  pharmacology, anatomy, histology, embryology, genetics, and
  biostatistics. Popups link to Wikipedia for further reading.
  Fully free, no UpToDate dependency.
- First-run welcome dialog: recommends two companion AnkiWeb addons
  (FSRS Helper 759844606, Image Occlusion 1374772155) with detection
  of whether they are already installed.
- Eponym and abbreviation aliases for 226 existing conditions (Wegener /
  GPA, Hashimoto / chronic lymphocytic thyroiditis, Reiter / reactive
  arthritis, STEMI / NSTEMI / MI, HFrEF / heart failure, COPD, etc.)
  so the underliner catches both the classic eponym and the modern
  name.
- StatPearls dock: home button is now a split toggle (StatPearls
  home or DrugBank home), persists the choice across restarts.
- Chat dock: subtle Dr House quote in the header, surfaced every
  10 to 20 dock-opens.

### Changed

- Welcome dialog redesigned: three "module cards" with descriptions
  and shortcut chips, tighter layout, no more empty vertical band.
- AI chat dock: only the currently-selected provider renders inline;
  all other providers live in a single dropdown menu next to it.
- Top toolbar AI icon now reflects the currently-active provider in
  real time.
- StatPearls pages: the NCBI Bookshelf top-of-page search strip is
  hidden, removing the visual ambiguity with the per-book "Search
  this book" form (which is auto-focused on open).
- DrugBank handling strengthened: unmapped drugs now resolve to a
  DrugBank "unearth" search instead of falling back off-site.

### Removed

- DailyMed fallback URL (DrugBank-only now).
- Back / Forward navigation arrows in the AI chat dock header
  (rarely useful; provider switching already triggers a fresh load).

## [1.0.4] - 2026-05-10

### Added

- "Clear session" button (⎚) in the UpToDate dock nav header. Wipes
  the dock's cookies, HTTP cache, and current-page web storage on the
  UTD profile, then reloads the home URL. Recovery path for users
  stuck on a wedged SSO/login error (e.g. Oracle Access Manager
  "System error", stale OpenAthens/Shibboleth jsessionids, expired
  HCN proxy tokens) where the existing cookie is invalid but the
  server won't issue a clean redirect. Confirms before clearing;
  local state only - does not log the user out at their IdP.

## [1.0.3] - 2026-05-09

### Fixed

- First-run / "Run setup again…" dialog now exposes the institution
  URL field so HCN-proxy (NSW Health, Vic Health) and other custom-
  entry users can set `uptodateHomeUrl` from the welcome flow. Previous
  behaviour: re-running setup just reloaded the configured URL, which
  for non-default institutions was the public UTD page - leaving the
  user apparently signed out with no in-app way to point the dock at
  their proxy entry.
- `uptodate/__init__.py` module docstring corrected: it claimed the
  default home URL was the HCN proxy, but the actual default is the
  public UpToDate search page. Updated to match `_DEFAULTS` and
  `config.md`.

## [1.0.2] - 2026-05-06

### Changed

- StatPearls side panel auto-focuses the "Search this book" input on
  NCBI Bookshelf landing pages whenever it loads or is reopened via
  the toolbar button. Means you can hit the toolbar shortcut and
  immediately start typing a query without first clicking into the
  text field. No-op on chapter pages or non-bookshelf URLs.

## [1.0.1] - 2026-05-06

Pre-publication content + UX cleanup.

### Removed

- **Per-card NCBI auto-search.** The previous flow made three
  sequential PubMed E-utilities round trips (esearch + esummary +
  efetch) every time a card was shown, taking 1–4 seconds and showing
  a "SEARCHING STATPEARLS…" stub the whole time. The article-list
  section in the side panel is now fed exclusively by instant
  local-database matches (StatPearls and DrugBank entries already
  detected on the card). When there are no local matches, the list
  section is hidden entirely. Popup highlighting and click-to-open-
  article in the webview are unaffected and remain instant. Removes
  the `autoSearch` and `maxResults` config keys.

### Fixed

- `Settings…` dialog no longer crashes on open (`_Qt` undefined-name
  bug introduced when the Qt import was scoped into `_qt_imports()`).

### Changed

- Deduplicated the bundled term databases: 9 silently-overwritten
  acronym entries and 9 silently-overwritten drug entries removed,
  keeping the longer/more curated definition in each pair.
- `manifest.json` `min_point_version` bumped from 49 → 50 (Qt6 was
  Anki's default from 2.1.50, matching the addon's `tested_on_qt5:
  false`). Legacy AnkiPearls / UpToAnki / AnkiDate side-loaded
  installs are now declared in `conflicts` so Anki disables them.

## [1.0.0] - 2026-05-05

First public AnkiWeb release. Unifies the previous AnkiPearls and
AnkiDate addons into a single package and adds a third AI-chat module.

### Added

- AI chat side dock (Claude / ChatGPT / Gemini / Copilot / Perplexity /
  DeepSeek / Grok / Duck.ai) with one-click provider switching and an
  overflow `▾` menu when more than five providers are configured.
- "Open externally" `↗` button in every dock header - opens the
  current page in the user's system browser, the escape hatch for
  passkey sign-in, video DRM, and other features that embedded
  webviews can't trigger.
- Send-selection-to-chat keyboard shortcut (`Ctrl+Shift+P`).
- Custom popup terms (`customTerms` config key) - user-defined JSON
  array of `{title, summary, url}` merged into the reviewer's
  highlight set alongside the bundled term databases.
- "Run setup again…" Tools menu entry to retrigger the welcome dialog.
- "Help / FAQ (open online)" Tools menu entry pointing at the README.
- Toolbar button order Settings drag-list (chat ↔ UpToDate).
- Save-without-restart checkbox in Settings.
- Optional dock-state persistence (`rememberDockState`) - reopen the
  same docks at the next Anki launch.
- Verbose debug logging gated by the `debug` config flag.
- Renderer-crash auto-recovery for the chat and StatPearls docks
  (UpToDate dock already had this).
- Legacy AnkiPearls / AnkiDate config-key migration on first launch
  after upgrade.
- Cross-source acronym → condition unification (e.g. "MI" expands to
  "Myocardial infarction" with the full condition summary).
- British / American spelling normalisation in the acronym → condition
  resolver so "Acute lymphoblastic Leukemia" matches the British
  "Leukaemia" canonical entry.

### Changed

- **Cloudflare bypass**: replaced the previous heavy stealth JS stack
  (navigator.webdriver delete, sec-ch-ua headers, fake PluginArray,
  Function.prototype.toString proxy, etc.) with a minimal AT V2-style
  profile setup - `ForcePersistentCookies` + standard QtWebEngine
  attributes. The stealth tricks were tripping Cloudflare's tamper
  detection; the minimal profile clears Turnstile cleanly.
- Default UpToDate home URL changed from the NSW/Vic Health HCN proxy
  to the public `https://www.uptodate.com/contents/search` so non-AU
  users get a working default. NSW/Vic Health and other institutions
  with a custom SP-initiated URL set theirs in Settings.
- Settings dialog split into per-module group boxes for readability;
  added "Other" group with `rememberDockState` and `debug` toggles.
- Toolbar redraws coalesce to one per event-loop tick instead of one
  per call site.
- Favicon disk writes throttled to one save per provider per minute.
- Config cache switched from a 2 s TTL to invalidate-on-write - O(1)
  reads after first load.
- DrugBank banner-hider tightened to a fixed selector list with a
  250 ms-debounced MutationObserver. The previous full-DOM
  `querySelectorAll('*')` sweep is gone.

### Removed

- **Per-card NCBI auto-search.** The previous version made three
  sequential PubMed E-utilities round trips (esearch + esummary +
  efetch) every time a card was shown, taking 1–4 seconds and showing
  a "SEARCHING STATPEARLS…" stub the whole time. The article-list
  section in the side panel is now fed exclusively by instant
  local-database matches (StatPearls and DrugBank entries already
  detected on the card). When there are no local matches, the
  list section is hidden - no empty stub, no spinner. Popup
  highlighting and click-to-open-article in the webview are
  unaffected and remain instant. Removes the `autoSearch` and
  `maxResults` config keys.
- "Copy current card" 📋 button in the chat dock (the same flow is
  now `Ctrl+Shift+P`, freeing the slot for "Open externally").
- Dead `QTWEBENGINE_CHROMIUM_FLAGS` env-var assignment at module load
  (no-op because Anki's QApplication has already been constructed by
  the time addons load).
- Stealth JS injection module - see "Changed → Cloudflare bypass".

### Fixed

- Toolbar button order now actually reorders chat ↔ UpToDate. Prior
  versions read `toolbarOrder` from config but both modules used the
  same fallback `links.append()` path so the configured order was
  ignored.
- "Save & restart Anki" no longer crashes Anki or loses pending
  changes - switched from `mw.app.exit(0)` (which bypasses
  `unloadProfile`) to `mw.unloadProfileAndExit()`.
- Settings button label now actually relaunches Anki rather than just
  quitting.

### Security

- Replaced ad-hoc `try / except: pass` blocks with a centralised
  logging shim that writes to stderr at WARN/ERROR level. Users can
  enable `debug: true` for full tracebacks when filing bug reports.
- pycmd `tad_open:` URL handler now logs cross-origin navigations to
  unrecognised hosts at debug level (still allowed, http/https only,
  but auditable).

### Known limitations

- Passkey / Touch ID sign-in does not trigger inside QtWebEngine on
  macOS (platform-authenticator entitlement restriction). Workaround
  documented in Settings and README.
