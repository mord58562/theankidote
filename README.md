# The AnkiDote

A unified medical-reference sidebar for Anki. Free and open source under
GPL-3.0. Three independently-toggleable side docks plus inline term
highlighting in the reviewer.

## What's new in 1.3

**Opening articles actually works.** "Open article" used to land on
StatPearls' in-book search results, which only forwards you to the
chapter when a search happens to have exactly one hit. Common terms with
several matching chapters stopped there, and that results page doesn't
render in the panel at all. 639 of 828 conditions now carry a direct
link and open in one step; the rest fall back to a search. Links are
only used where the article genuinely is the condition, so a term that
matches a different entity, a broader class, or a narrower subtype gets
no link - reading the wrong chapter unaware is worse than an extra
click.

**The article panel no longer opens blank.** Loads start only once the
panel is visible, an in-flight load is stopped before a new one begins,
a failed load retries once, and a second failure shows a readable
message rather than an empty rectangle. A page that loads but isn't
drawn is now redrawn, and if the browser engine's renderer stops the
panel says so and offers to open the page in your normal browser.

**Australian conventions throughout.** `haemophilia`, `hyponatraemia`,
`coeliac disease` and `transient ischaemic attack` are now recognised in
cards and displayed in Australian form, with American spellings still
matching as synonyms. Drug text uses INN and Australian generic names
(adrenaline, salbutamol, ciclosporin, rifampicin, indometacin,
pethidine, mesalazine), SI units, and labels US regulatory claims as US.

**The condition library was around 10% unreachable.** 111 names appeared
more than once and lookups resolved to the first match, so the briefest
version showed while the fuller rewrite sat unused - breast cancer,
infective endocarditis, lung cancer, syphilis and ankylosing spondylitis
among the worst affected. Duplicates are merged, keeping the richest
summary and the combined aliases.

**Popups.** They no longer run off the bottom of the screen: a popup
measures the space available and opens above the term when there's no
room below. Section labels (`Sx`, `Ix`, `Mx`) are clickable and open the
article at the matching section. A popup's appearance is settled once
per card and survives hovering away and back, and the flip to the answer
side.

**The add-on follows Anki's light/dark switch mid-session** instead of
keeping whatever theme it started with.

See `CHANGELOG.md` for the full history.

Three independently-toggleable side docks plus inline term
highlighting in the reviewer.

## What's new in 1.1.2

- **Snappier toolbar provider icon.** The top-toolbar AI chat button
  now repaints its logo the instant you switch LLM in the dock, instead
  of waiting for the new page to start loading. The icon also catches
  up automatically when an in-page navigation crosses provider
  boundaries (e.g. an OAuth bounce back to the host site).

## What's new in 1.1.1

- Welcome dialog tidy-up and case-insensitive synonym dedup. See
  CHANGELOG for full notes.

## What's new in 1.1.0

- **Preclinical / basic-science popups (~340 entries).** Hover-popups
  now cover the foundational vocabulary clinical cards quietly assume
  you remember: cardiac, respiratory, renal, GI, endocrine, neuro, and
  haematology physiology; biochemistry pathways (glycolysis, TCA, ETC,
  urea cycle, fatty-acid oxidation, ketogenesis); microbiology (key
  pathogens, resistance mechanisms); immunology (T-cell subsets,
  hypersensitivity types, complement); pathology (cell injury,
  necrosis types, neoplasia basics); pharmacology (PK, receptor
  families); plus anatomy landmarks, embryology, genetics, histology,
  and biostatistics (sens/spec, LR+/LR-, NNT, RR, OR, etc.). Each
  popup is a 1-3 sentence plain-English summary that links to
  Wikipedia for further reading. Standalone, fully free, no UpToDate
  required.
- **Eponym + abbreviation aliases** for 200+ existing conditions so the
  highlighter catches both forms (Wegener / GPA, Hashimoto / chronic
  lymphocytic thyroiditis, Reiter / reactive arthritis, STEMI /
  NSTEMI, HFrEF, COPD, etc.).
- **Welcome dialog redesign** with per-module descriptions and a
  Recommended companion addon section (Image Occlusion) that auto-hides
  the card if you already have it installed.
- **StatPearls dock:** confusing NCBI Bookshelf top search strip hidden;
  per-book "Search this book" field auto-focused; home button now
  toggles between StatPearls and DrugBank as the default.
- **AI chat dock:** only the active provider renders inline; everything
  else lives in a single dropdown next to it. Subtle Dr House quote
  occasionally appears in the dock header.
- **Removed:** back/forward arrows in the chat dock (rarely useful);
  DailyMed fallback (DrugBank-only now).

Three independently-toggleable side docks plus inline term highlighting
in the reviewer:

- **StatPearls + DrugBank popups and side panel** - hover-to-reveal
  tooltips on medical terms in the reviewer, click to open the full
  article in a docked side panel. Bundled local term databases cover
  ~830 clinical conditions (with eponym and abbreviation aliases for
  the renamed ones), ~1170 drugs, ~420 multi-meaning clinical
  abbreviations, and ~340 preclinical / basic-science concepts
  (physiology, biochemistry, microbiology, immunology, pathology,
  pharmacology, anatomy, biostatistics). Popups link out to
  StatPearls, DrugBank, or Wikipedia depending on the source; the
  side panel can be set to either StatPearls or DrugBank as the home
  page. All popup content is local and instant - no network call to
  show a popup.
- **UpToDate authenticated browser dock** - separate side panel with a
  persistent named profile, so you log in to your institution's UpToDate
  subscription once and stay logged in across Anki restarts. Activity-
  gated session keepalive only refreshes the cookie while you're using
  Anki, never in the background.
- **AI chat dock** - bring-your-own-account embedded webview pointed at
  your existing Claude / ChatGPT / Gemini / Copilot / Perplexity /
  DeepSeek / Grok / Duck.ai session. No API keys, no programmatic chat
  scraping. One-click provider switching with cookies persisted per
  provider so you can stay logged into all of them. Ctrl+Shift+K sends
  the reviewer's current text selection and Ctrl+Shift+J sends the
  whole visible card: the dock opens, the provider's message box is
  focused, and the text is pasted into it. Nothing is submitted - you
  read it, edit it and press Enter yourself.

## Cost & access

The add-on is free. UpToDate is a paid third-party service that requires
your own subscription (personal or institutional). The add-on never
includes UpToDate content, only opens links in your existing UTD session.

If you don't have UpToDate access, untick "UpToDate sidebar" on the
first-run dialog - every UTD control disappears so you never see a button
you can't use. StatPearls, DrugBank, and the AI chat dock all work fully
without any paid service.

## Install

**AnkiWeb (recommended):** Tools → Add-ons → Get Add-ons → paste
`720072719` → restart Anki. Listing:
<https://ankiweb.net/shared/info/720072719>.

**From source:**

```
cd "$HOME/Library/Application Support/Anki2/addons21"   # macOS
# or %APPDATA%\Anki2\addons21\                           # Windows
# or $XDG_DATA_HOME/Anki2/addons21/                      # Linux
git clone https://github.com/mord58562/theankidote.git theankidote
```

Then restart Anki.

## First run

A welcome dialog asks which of the three modules you want enabled and
checks for one recommended companion addon (Image Occlusion) - the
install pill appears only if you don't already have it. You can
re-trigger the dialog any time via
**Tools → The AnkiDote → Run setup again…**.

If you keep UpToDate enabled, the dock will open automatically pointed
at the UpToDate sign-in page so you can complete institutional SSO
straight away. The session cookie persists thereafter.

## Configuration

**Tools → The AnkiDote → Settings…** opens the full settings dialog.
**Tools → The AnkiDote** also exposes quick module on/off toggles. See
`config.md` for every config key, including the JSON format for custom
popup terms.

Highlights:

- `enableUpToDate`, `enableHighlights`, `enableChat` - module master
  toggles. Restart Anki for full effect.
- `uptodateHomeUrl` - defaults to the public UpToDate search page.
  Subscribers will be redirected to their institution's SSO automatically
  on first visit. NSW/Vic Health users behind the HCN proxy and any
  institution with a custom SP-initiated URL should set their direct
  entry point in Settings; see `config.md` for examples.
- `chatCustomProviderUrl` - adds a 9th "Custom" button pointing at a
  self-hosted endpoint (OpenWebUI / LibreChat / llama.cpp etc).
- `customTerms` - a JSON array of `{title, summary, url, case_sensitive?}`
  user-defined popup terms merged into reviewer highlighting alongside
  the bundled StatPearls / DrugBank / acronyms / conditions sets.
- `toolbarOrder` - drag the chat ↔ UpToDate buttons in Settings to
  swap their order in the top toolbar.
- `pearlsHomePage` - `"statpearls"` (default) or `"drugbank"`; sets
  which page the side panel's Home button loads. Toggleable inline
  from the home button's dropdown.
- `rememberDockState` - reopen the same docks at next launch.
- `debug` - extra logging for bug-report diagnosis. The article
  panel's diagnostic log is always written; see Reporting bugs.

### Default keyboard shortcuts

| Action                       | Shortcut       |
| ---                          | ---            |
| Toggle StatPearls/DrugBank   | `Ctrl+Shift+S` |
| Toggle UpToDate              | `Ctrl+Shift+U` |
| Toggle AI chat               | `Ctrl+Shift+A` |
| Search selection in UpToDate | `Ctrl+Shift+L` |
| Send selection to AI chat    | `Ctrl+Shift+K` |
| Send whole card to AI chat   | `Ctrl+Shift+J` |

On macOS, Anki maps `Ctrl` to `⌘` automatically - the bindings show as
`⌘⇧S` etc. Every shortcut is editable in Tools > The AnkiDote >
Settings > Shortcuts: click a field, press the keys you want, and the
new binding takes effect as soon as you close the window. Clear a field
to disable that shortcut entirely.

If any of these clash with another addon you use or with an Anki default
that matters to you (e.g. some Anki builds reserve `Ctrl+Shift+A` for the
Add Cards dialog), set `shortcutTogglePearls`, `shortcutToggleUptodate`,
`shortcutToggleChat`, `shortcutSearchSelection`, or
`shortcutSendSelectionToChat`, or `shortcutSendCardToChat` to your
preferred binding in `config.md`.
Set any one to an empty string to disable it.

## Privacy & Terms-of-Service posture

Per-source statements:

- **StatPearls / NCBI Bookshelf** - public NIH database, accessed via
  NCBI's documented public E-utilities API (esearch / esummary / efetch).
  The add-on identifies itself in the User-Agent and stays well within
  NCBI's rate-limit guidance (one debounced search per card view).
- **DrugBank** - pages load in the addon's webview using your personal
  free-tier session. No content scraping, no API keys, no automation
  beyond a small CSS rule that hides their login-upsell banner. If you
  prefer not to hide that banner, click any DrugBank link from a popup
  to open it in your system browser.
- **UpToDate** - webview-only access through your own institutional or
  personal subscription. No programmatic content extraction, no
  credential storage by the addon itself. The activity-gated keepalive
  only fires when you've used Anki within the last 2× the configured
  interval (default 40 minutes), so leaving Anki open overnight does
  NOT make background UTD requests.
- **AI chat (Claude / ChatGPT / Gemini / Copilot / Perplexity / DeepSeek /
  Grok / Duck.ai)** - embedded webview hosting your own logged-in chat
  session. No API keys, no programmatic message submission, no chat
  scraping. The send-to-chat shortcuts copy to your system clipboard,
  then focus the provider's message box and paste - the same two steps
  you would do by hand, and nothing more. The message is never sent;
  that is always your keystroke. Set `chatAutoPaste` to `false` for
  clipboard-only behaviour.
- **No telemetry. No remote config. No cloud sync.** Settings live in
  Anki's normal addon-config JSON. Cookies and cache live in QtWebEngine's
  per-profile directory under `~/Library/Application Support/Anki2/
  QtWebEngine/`. Nothing leaves your machine that you didn't initiate.

## Sidebar behaviour

The StatPearls / DrugBank pills show which site you are on and switch to
the other one; clicking the site you are already browsing does nothing
rather than reloading it. When Anki is in dark mode both sites render
dark, using Chromium's own auto-dark pass (Qt 6.7+).

The RELEVANT ARTICLES list is generated from terms detected on the
current card. It can be wrong, so it has a close button - dismissing it
hides it for that card only.

## Debugging

**Settings > Advanced** holds the developer controls: a verbose-logging
switch, **Show log** (reveals the log file in your file manager), and
**Web inspector**. The inspector needs Anki to restart, because Qt reads the
remote-debugging setting once at startup; the entry handles that and
warns you first, since the port can drive every webview in the process.
It is never persisted - a normal restart leaves it off.

## Known limitations

- **Passkey / Touch ID sign-in won't trigger inside an embedded
  webview.** macOS restricts the platform authenticator to entitled
  apps (Safari, Chrome.app); QtWebEngine isn't entitled. Sign in with
  password + 2FA - the named-profile cookie store keeps you signed in
  across restarts.
- **WebUSB / WebAuthn hardware keys** likewise generally don't work in
  embedded webviews. Use the "Open externally" `↗` button in any dock
  header to finish the task in your real browser.
- **Renderer crashes** are auto-recovered by reloading the last URL,
  up to three consecutive times. Past that the panel shows a message
  with a link to open the page in your normal browser, rather than
  reloading a page that reliably kills the renderer.

## Reporting bugs

Please open an issue at
<https://github.com/mord58562/theankidote/issues>. The add-on keeps a
diagnostic log of what the article panel is doing - open it via
**Tools → The AnkiDote → Show diagnostic log** and attach the relevant
lines. For full tracebacks as well, set `debug: true` in the addon
config before reproducing.

Redact any patient data before sharing screenshots or card exports.
See `SECURITY.md` for the security disclosure process.

## Disclaimer

Educational / study tool only. The popup summaries are condensed
mnemonics and **do not substitute for clinical judgement, current local
guidelines, drug-information references, or the user's own scholarship**.
No part of this software constitutes medical advice. Verify every
clinical decision against authoritative primary sources and your
institution's guidelines. Use at your own risk; the author and
contributors accept no liability for clinical outcomes derived from
the use of this add-on.

## License

GPL-3.0-or-later. See `LICENSE`.
