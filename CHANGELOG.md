# Changelog

All notable changes to The AnkiDote.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.2] - 2026-08-14

### Added

- **StatPearls and DrugBank follow Anki into dark mode.** Uses
  Chromium's own auto-dark rendering pass rather than an injected
  stylesheet, so figures and structure diagrams survive intact. Needs
  Qt 6.7 or newer; on older builds the pages render light as before.
- **The article list can be dismissed.** A small close button on the
  RELEVANT ARTICLES header hides it for the current card. It is a guess
  at what is relevant and not always a good one, and closing the whole
  sidebar was previously the only way out of its way. The next card
  brings it back, as does the toolbar button.
- **A web inspector for the sidebars**, alongside the diagnostic log
  under Tools > The AnkiDote once diagnostics are unlocked. Qt reads
  `QTWEBENGINE_REMOTE_DEBUGGING` when Anki starts, so it cannot be
  switched on for the session you are already in - the entry offers to
  relaunch Anki with it set, and warns first: the port drives every
  webview in the process, signed-in UpToDate and chat sessions
  included. Nothing is persisted, so the next normal restart turns it
  back off.
- **Restore defaults, on the Shortcuts tab.** A blank field is
  ambiguous - deliberately disabled, or lost to a bad write? - and
  there was no route back to a working binding. Two actions sharing a
  binding is now flagged too.

### Changed

- **The article list is ranked and capped.** It was every match on the
  card in whatever order the resolvers found them, conditions first and
  drugs after - so on a card about calcium pyrophosphate deposition
  disease, "gout" (mentioned once, as a contrast) sat above the disease
  the card is actually about. Entries are now scored on whether the term
  appears in the card's first field, how often it appears, how early,
  and how specific it is, then trimmed to `maxResults` (default 8).
- **Clicking the site you are already on no longer reloads.** Switching
  to DrugBank from a DrugBank monograph cost a Cloudflare round trip
  and discarded the page you were reading.
- **A loading bar sits under the sidebar header.** Reaching DrugBank
  goes through Cloudflare's challenge and can take several seconds,
  during which nothing on screen changed - so the switch read as broken
  and got clicked again, restarting the navigation.
- **Header icons are optically matched.** The glyphs come from
  different Unicode blocks and were all set at one font size, so the
  guillemet arrows rendered tiny beside the reload and home icons.
  Back and forward are now proper arrows, sized per glyph.

### Fixed

- **Shortcuts now fire wherever focus is.** Every binding was created
  with Qt's default `WindowShortcut` context, which only fires when the
  active window is the one the shortcut is parented to - so a binding
  was dead whenever focus sat in the reviewer's webview or a genuine
  top-level window like Browse was in front. That is the whole reason
  the diagnostics chord appeared to do nothing. All bindings are now
  `ApplicationShortcut`, which is what a global shortcut is supposed to
  mean and what they were all documented as doing.
- **The diagnostics chord is configurable** via `shortcutDiagnostics`,
  so another add-on claiming `Ctrl+Alt+Shift+D` no longer leaves it
  unreachable. Setting `diagnosticsUnlocked` to `true` by hand is
  documented as the fallback.
- **DrugBank search no longer throws you back into StatPearls.** A
  failed navigation retried `_pending_url` - the target of the last
  popup "Open article" click, which persists until the next one. So any
  in-page navigation that failed, a DrugBank search most visibly,
  retried whatever StatPearls chapter had last been opened and landed
  the reader on it. Failed loads now retry the URL Chromium was
  actually asked for, and the popup intent is cleared once satisfied or
  when you navigate yourself. The same stale state could also send the
  search-page auto-jump hunting for a StatPearls term inside DrugBank's
  results; it is now scoped to the site the popup pointed at.
- **Switching theme no longer reports an error.** `_ResultsSection`
  called `set_results`, which does not exist - the method is
  `show_results`. The restyle aborted at that point every time.
- **The welcome dialog sizes to its contents.** It was fixed at
  520x460, leaving a third of the pane empty with the Continue button
  marooned at the bottom - which reads as content that failed to load.
- **Settings text no longer clips.** Indented descriptions used
  contents margins, which narrow a label's text without changing the
  height it reports to the layout, so the second line was painted under
  the widget below. Descriptions are short single lines now, and the
  long explanatory paragraphs have moved to tooltips.

## [1.4.1] - 2026-08-14

### Added

- **Sent text now lands in the chat box.** `Ctrl+Shift+K` and
  `Ctrl+Shift+J` previously stopped at the clipboard and asked you to
  paste. They now open the dock, focus the provider's message box and
  paste for you. Nothing is submitted - the text sits in the box for
  you to read, edit and send. Turn it off under Settings > Services >
  AI chat if you would rather only the clipboard were touched.
- **Custom popup terms have a proper editor.** Settings > General >
  Custom terms opens a table with Add and Remove, replacing the raw
  JSON textarea where one missing comma silently disabled every custom
  term with no feedback anywhere.

### Changed

- **Shortcut changes apply immediately.** Bindings were only read at
  launch, so changing one in Settings appeared to do nothing until the
  next restart - unhelpful, given the usual reason to change a shortcut
  is a clash you want gone now.
- **The Reference tab has been folded into General.** Two checkboxes
  and a button did not justify a tab, and it read as a peer of Services
  and Shortcuts when it belongs with the module switches above it.
- **The 1.4 upgrade notice now reaches everyone upgrading from below
  1.4.** It was shown only to users still sitting on `Ctrl+Shift+P`, so
  anyone who had already rebound that key by hand never heard that
  shortcuts had become editable or that a whole-card shortcut existed.
  Installs now record which version they last ran.

### Fixed

- **Switching Anki's theme restyles all three sidebars.** The
  StatPearls panel raised `NameError: name '_theme' is not defined` on
  the first line of its restyle, so nothing after it ran; the UpToDate
  and AI chat docks had no restyle path at all and kept whichever theme
  they were built with until Anki restarted.

## [1.4] - 2026-08-14

### Added

- **A StatPearls / DrugBank switch in the sidebar header.** Which site
  you were on was the panel's most important state and the only way to
  change it was a dropdown hidden on the home button, so searching
  DrugBank was effectively undiscoverable. It is now two pills showing
  where you are, and clicking one takes you there.
- **Send the whole card to the AI chat** with `Ctrl+Shift+J`. Copies
  everything currently visible - cloze deletions resolved, the answer
  included once revealed, popup and dock chrome excluded - and opens the
  chat dock ready to paste.
- **Shortcuts are editable in Settings.** A clash with another add-on is
  the most likely reason to change a binding, and the only way to do it
  was hand-editing JSON. Clear a field to disable that shortcut.

### Changed

- **Settings has been rebuilt to look and behave like Anki's own
  Preferences.** Tabbed rather than one long scroll, native controls
  throughout instead of custom-coloured cards and pills, and changes
  written when you close the window rather than gated behind a Save
  button. Shortcuts are edited by clicking the field and pressing the
  keys.
- **The send-to-chat shortcut is now `Ctrl+Shift+K`**, because
  `Ctrl+Shift+P` is Anki's own Switch Profile binding and could bounce
  you to the profile picker mid-review. Existing users are asked once
  whether to move to the new default or keep what they have.
- **Settings no longer restarts Anki.** The Save button was labelled
  "Save & restart Anki", with a checkbox you had to tick to avoid
  quitting mid-session. Anki's own convention is followed instead: a
  quiet note that some settings need a restart, and you restart when it
  suits you.

### Fixed

- Clicking a link while the sidebar's home page was still loading could
  raise an Anki error report, even though the page then loaded fine. The
  abandoned load is now recognised as superseded rather than failed, and
  routine retries are recorded to the diagnostic log instead of being
  raised as errors.
- The home button kept the styling of the dropdown it used to be,
  leaving a mismatched hover area next to the other navigation buttons.

## [1.3.2] - 2026-08-12

### Added

- 92 more conditions link directly to their article, covering entries
  filed under a synonym rather than the name used here - acoustic
  neuroma under vestibular schwannoma, chilblains under pernio,
  age-related hearing loss under presbycusis. 639 of 828 conditions now
  open their article in one step.

### Changed

- Where a matching article covers a different entity, a broader class or
  a narrower subtype than the term as taught, no link is used and the
  search is shown instead. Reading the wrong chapter unaware is worse
  than an extra click, and nothing on the page would signal the swap.

## [1.3.1] - 2026-08-12

### Added

- 46 further conditions now link directly to their StatPearls chapter.
  These are entries whose article is filed under the American spelling -
  hyponatraemia, coeliac disease, subarachnoid haemorrhage, transient
  ischaemic attack and similar - which previously found nothing. 547 of
  828 conditions now open their article in one step.

## [1.3] - 2026-08-12

### Added

- 501 conditions now carry a direct StatPearls link, so "Open article"
  opens the chapter immediately with no lookup and no network delay.

### Fixed

- Chapter links are only used where the article genuinely is the
  condition. Terms that matched a narrower article - "Stroke" matching
  "Heat Stroke", "Sepsis" matching "Neonatal Sepsis", "Hypertension"
  matching "Portal Hypertension" - now fall back to a search instead,
  since the opened page gives no sign that it is the wrong one.
- Links remembered by earlier versions are discarded on upgrade. Those
  could point at an unrelated article, and there is no way to tell which
  ones, so they are all rebuilt.

## [1.2.7] - 2026-08-12

### Fixed

- Chapter lookup could open an unrelated article. NCBI indexes
  StatPearls by section rather than by chapter, so a search returned
  headings like "Morphology" and the add-on followed them to whichever
  chapter they belonged to. Lookups now match on chapter titles, and a
  term whose chapter cannot be identified confidently falls back to a
  search rather than opening something that only looks plausible.

## [1.2.6] - 2026-08-12

### Fixed

- **Drug popups opened StatPearls pages instead of DrugBank.** The
  chapter lookup added in 1.2.5 was being applied to every popup rather
  than only StatPearls ones, so clicking through from a drug searched
  StatPearls for the drug name and opened whatever it found. Drug links
  behave as they did before 1.2.5 again.
- Remembered links are now kept separately for drugs and conditions, so
  a drug and a condition sharing a name cannot overwrite each other.

## [1.2.5] - 2026-08-12

### Fixed

- **"Open article" now goes to the article.** It was landing on
  StatPearls' in-book search results, which only redirects onward when a
  search happens to have exactly one hit - so common terms with several
  matching chapters stopped there, and that results page does not
  display in the panel at all. The term is now looked up on NCBI first
  and the chapter opened directly.
- Lookups prefer the current chapter over retired ones, which NCBI keeps
  in its index and which carry an out-of-date warning.

## [1.2.4] - 2026-08-12

### Fixed

- The article panel could finish loading a page and still show nothing.
  The page itself was fine - correct address, correct title, full
  content - but was never drawn, leaving an empty rectangle. The panel
  now forces the view to redraw once a page has loaded.
- NCBI redirects its in-book search address to the book's own page with
  the search preserved, which the add-on did not recognise. As a result
  a search never resolved to the chapter, and the search results page
  itself risked being remembered as though it were the article.

## [1.2.3] - 2026-08-12

### Added

- A diagnostic log at `user_files/diagnostic.log`, reachable from
  Tools > The AnkiDote > Show diagnostic log. It records every
  navigation the article panel makes and what the loaded page actually
  contained, which is the information needed to work out why a panel
  came up empty.

## [1.2.2] - 2026-08-12

### Fixed

- The article panel could go blank with no explanation. When the
  embedded browser engine's renderer process stops, Qt leaves the view
  painted empty, which looks identical to a page that simply loaded
  nothing. The panel now reports what happened, stops reloading after
  three consecutive failures instead of retrying indefinitely, and
  offers to open the page in your normal browser.
- Showing the dock and loading a page in the same action could start two
  navigations, with the second cancelling the first and the cancellation
  being reported as a load failure. This affected the "Open article"
  path specifically.

## [1.2.1] - 2026-08-12

### Fixed

- **"Open article" crashed instead of opening anything.** A redundant
  local import shadowed the module-level `unquote`, which made the name
  local to the whole function and turned the earlier call on that path
  into an `UnboundLocalError`. Every article click failed with a
  traceback, so nothing added in 1.2 - the article resolver, the section
  jump, the DrugBank auto-jump - could run at all. A check for this class
  of shadowing has been added to the test suite.

## [1.2] - 2026-08-11

### Fixed

- **The StatPearls panel no longer opens blank.** Two separate causes,
  both most visible when using "Open article" from a popup. Clicking it
  started the page load before showing the dock, so the renderer was
  handed a zero-size viewport and could finish loading with nothing
  drawn; and a failed or superseded navigation left the view parked on
  Chromium's internal error page, which paints as an empty grey
  rectangle with no message. Loads now begin only once the dock is
  visible, an in-flight load is stopped before a new one starts, a
  failed load retries once, and a second failure shows a readable
  message with a retry link instead of nothing at all. Surfacing the
  panel onto a blank page also triggers a reload.
- **Roughly 10% of the condition library was unreachable.** 111
  condition names appeared more than once, and because lookups resolve
  to the first match, the earliest and almost always briefest version
  was the one shown while the fuller rewrite sat unused. Duplicates are
  now merged, keeping the richest summary and the combined aliases of
  every copy. Breast cancer, infective endocarditis, lung cancer,
  syphilis and ankylosing spondylitis were among the worst affected.
- **Australian spellings now match.** Terms such as `haemophilia`,
  `hyponatraemia`, `coeliac disease`, `transient ischaemic attack` and
  `ischaemic colitis` are recognised in cards, and popup titles display
  the Australian form rather than the American one. American spellings
  are retained as aliases, so cards written either way still match.
- `CoA` no longer highlights as coarctation of the aorta on
  biochemistry cards, where it means coenzyme A.
- Epidural/extradural haematoma and the two gastro-oesophageal reflux
  entries were duplicate records of the same entity under different
  names, and are now single entries.

- **"Open article" now opens the article.** Every condition and 47% of
  drugs had no direct link, so the button loaded a search results page
  and left you to click again — which is most of why the sidebar was
  worth skipping. The panel now resolves the term to the real chapter or
  drug page, via NCBI's E-utilities for StatPearls and by following an
  unambiguous exact match for DrugBank, and caches the result so it only
  ever happens once per term. Ambiguous searches still show the results
  page, since that genuinely is the right answer there.
- **Section labels in a popup are now clickable.** Clicking `Mx`, `Ix`,
  `Sx` and the rest opens the article scrolled to the matching StatPearls
  section (Treatment / Management, Evaluation, History and Physical…),
  so the popup covers the summary and one click reaches the detail.
- Part of the popup stylesheet was silently discarded. A missing string
  concatenation left JavaScript's automatic semicolon insertion to split
  the declaration, dropping every rule after it — the UpToDate chips,
  section labels and rarity styling were unstyled as a result.
- **The add-on follows Anki's theme when it changes mid-session.**
  Previously the palette was fixed when Anki started, so switching
  light/dark left the docks on the old colours until restart.

### Changed

- Drug and condition text follows Australian conventions: INN and
  Australian generic names (adrenaline, salbutamol, ciclosporin,
  rifampicin, indometacin, pethidine, mesalazine and others), SI units
  in place of `mEq/L`, and "boxed warning" in place of the US-specific
  phrasing. Claims of US regulatory approval are now labelled as US
  rather than presented as though they applied locally.
- 15 drugs listed twice under both their American and Australian names
  are now single entries carrying both, so brand names and summaries no
  longer split across two records.

## [1.1.7] - 2026-08-11

### Fixed

- Term popups no longer run off the bottom of the screen. A popup now
  measures itself against the available space and opens above the term
  when there isn't room below; if neither side fits, it clamps to the
  roomier side and scrolls internally. Horizontal clamping now uses the
  popup's real width instead of a hard-coded one.
- Popup styling stays stable while you read: hovering away and back, or
  flipping to the answer side, no longer re-rolls a popup's appearance.
  It's now settled once per card and resets on the next card.

### Changed

- Minor visual polish.

## [1.1.6] - 2026-05-22

### Changed

- Minor visual polish.

## [1.1.5] - 2026-05-19

### Changed

- Picking a provider from the inline button or `▾` overflow menu now
  also persists it as `chatHomeUrl` (the default home URL), not just
  `chatLastUrl` (the last-session URL). Net effect: the LLM you
  selected stays the default going forward even if `chatLastUrl` is
  ever cleared.

## [1.1.4] - 2026-05-19

### Fixed

- AI chat dock no longer slows down provider loads. Previously the
  `urlChanged` handler treated every intermediate URL (about:blank,
  CSP redirects, internal SPA routes) as a fake provider crossing -
  because `_provider_for_url` defaulted to "Claude" for any
  unrecognised URL - and fired a meta.json fsync + full toolbar HTML
  rebuild + JS injection on every flap. We now use an `_explicit_`
  provider matcher that returns `None` for opaque schemes and
  unknown hosts, and gate all side effects on an explicit match.

### Changed

- Addon no longer has a baked-in Claude preference. The default home
  URL and the fallback provider label are now derived from the first
  entry in the user's in-app provider order (`chatProviders` config
  if set, else `DEFAULT_PROVIDERS`). The bundled order still has
  Claude first; reorder `DEFAULT_PROVIDERS` and the default follows.
  `chatHomeUrl` default is now `null` (meaning "use the first provider
  in order"); existing users with `https://claude.ai/new` saved
  explicitly are unaffected.

## [1.1.3] - 2026-05-19

### Fixed

- Top-toolbar AI chat icon now repaints reliably on every provider
  switch. The 1.1.2 fix relied on `mw.toolbar.redraw()` re-firing the
  `top_toolbar_did_init_links` hook with the fresh `chatLastUrl`; on
  the Anki release Rob is running, the redraw path doesn't actually
  repaint inline base64 `<img>` data URIs, so the old provider's logo
  stuck. We now also patch the link element's `innerHTML` directly
  by id from JS, which is invariant to whatever the surrounding
  redraw mechanism is doing.

## [1.1.2] - 2026-05-19

### Fixed

- Top-toolbar AI chat button now repaints its provider logo
  synchronously when the user picks a different LLM from the inline
  or overflow provider switcher. Previously the icon could lag a tick
  behind the click while the new page started loading. The toolbar
  also re-syncs when an in-page navigation crosses a provider
  boundary (e.g. an OAuth bounce back to the host site).

## [1.1.1] - 2026-05-12

### Changed

- Welcome dialog now recommends only Image Occlusion. The FSRS Helper
  recommendation has been removed; the rest of the dialog is unchanged.

### Fixed

- Capitalisation variants of the same term no longer appear as separate
  synonyms. Aliases that differ from the canonical name only in case
  have been pruned (10 conditions, 6 drugs), and the lookup builders now
  case-insensitively dedup names at load time so future entries can't
  reintroduce the issue.

## [1.1.0] - 2026-05-12

### Added

- Preclinical / basic-science term library (344 entries) covering
  physiology, biochemistry, microbiology, immunology, pathology,
  pharmacology, anatomy, histology, embryology, genetics, and
  biostatistics. Popups link to Wikipedia for further reading.
  Fully free, no UpToDate dependency.
- First-run welcome dialog: recommends one companion AnkiWeb addon
  (Image Occlusion 1374772155) with detection of whether it is
  already installed.
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
