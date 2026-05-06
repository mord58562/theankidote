# The AnkiDote — configuration reference

The AnkiDote is free and open source. UpToDate is a paid third-party
service; the addon links into your own UTD subscription if you have
one. Without UTD access, untick "UpToDate sidebar" in the first-run
dialog or in Settings — every UTD control disappears.

This file documents every config key. The recommended way to edit
these is **Tools → The AnkiDote → Settings…** rather than the raw
JSON, but both are supported.

## Highlighting / popups (StatPearls + DrugBank)

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| `enableHighlights` | bool | `true` | Master toggle for term highlighting in the reviewer. |
| `enableHighlightsOnQuestions` | bool | `true` | Highlight on the question side, not just the answer. |
| `enableArticleViewer` | bool | `true` | If true, popup clicks open the side panel; if false, they open the user's external browser. |
| `highlightColor` | hex string | `"#0fcad4"` | Underline colour for highlighted terms. |
| `autoSearch` | bool | `true` | Automatically run a StatPearls search when each card is shown. |
| `maxResults` | int | `8` | Maximum article results returned per card. |
| `customTerms` | string (JSON) / null | `null` | User-defined popup terms — see "Custom popup terms" below. |

### Custom popup terms

`customTerms` is a string holding a JSON array. Each entry is an object
with these fields:

| Field | Required | Description |
| --- | --- | --- |
| `title` | yes | The exact word/phrase to highlight in card text. |
| `summary` | yes | The tooltip body shown in the popup. |
| `url` | yes | Article URL opened when the popup is clicked (must be http/https). |
| `article` | no | Display title for the popup header — defaults to `title`. |
| `case_sensitive` | no | If `true`, only exact-case matches highlight. |
| `source` | no | Free-form source label shown in the popup; defaults to `"custom"`. |

Example (paste this into the **Settings → StatPearls + DrugBank →
Custom popup terms** field, or directly into config JSON):

```json
[
    {"title": "TICOSPA",
     "summary": "Treat-to-target trial in axial spondyloarthritis (2021).",
     "url":     "https://pubmed.ncbi.nlm.nih.gov/34903489/"},
    {"title": "GOLD",
     "summary": "Global Initiative for Chronic Obstructive Lung Disease classification.",
     "url":     "https://goldcopd.org/"}
]
```

Custom terms are merged into the reviewer's highlight set alongside
the bundled StatPearls, DrugBank, acronym, and condition databases.
Stored as a string (not a parsed list) so the config blob doesn't
need revalidation on every load — the reviewer parses lazily and
caches.

## UpToDate sidebar

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| `enableUpToDate` | bool | `true` | Master toggle. False hides the toolbar button and skips the keepalive timer. |
| `uptodateHomeUrl` | string | `"https://www.uptodate.com/contents/search"` | Your institution's SP-initiated UpToDate entry point. The default works for direct subscribers and OpenAthens / Shibboleth users — they're redirected to their institution's SSO automatically on first visit. NSW/Vic Health users behind the HCN proxy and any institution with a non-default entry URL should change this; see examples below. |
| `uptodateAutoSearchCard` | bool | `true` | When the UTD dock is open and a new card question is shown, automatically search UpToDate for the card's front field. |
| `uptodateKeepaliveIntervalMinutes` | int (≥5) | `20` | How often to refresh the UTD session cookie *while the user is actively using Anki*. The keepalive only fires if the reviewer or dock has been touched within `2 × interval` minutes — when Anki sits idle no programmatic UTD requests are made. |

### `uptodateHomeUrl` examples

**Direct UpToDate / personal subscription / OpenAthens / Shibboleth
(the default):**

```json
{"uptodateHomeUrl": "https://www.uptodate.com/contents/search"}
```

Most institutional logins recognise the user from their existing
session cookies and skip straight past SSO on subsequent loads.

**NSW Health and Vic Health (HCN proxy):**

```json
{"uptodateHomeUrl": "https://www.uptodate.com.acs.hcn.com.au/contents/search"}
```

**OpenAthens redirector (some NHS UK and university institutions):**

```json
{"uptodateHomeUrl": "https://go.openathens.net/redirector/YOUR-ORG-ID?url=https%3A%2F%2Fwww.uptodate.com%2Fcontents%2Fsearch"}
```

To find your OpenAthens redirector ID, log in once at
`https://go.openathens.net` in a normal browser and copy the
redirector URL pattern from the address bar before the final
UpToDate redirect.

### Resetting the welcome dialog

Tools → The AnkiDote → "Run setup again…" — or set `firstRunDone`
to `false` in config and restart.

### General method for finding your entry URL

1. Open a private/incognito browser window so you start with no cached
   credentials.
2. Navigate to `https://www.uptodate.com/contents/search`.
3. Click "Institutional login" and complete your institution's SSO.
4. Watch the address bar during the login flow. The first URL that
   initiates the SSO redirect is the value for `uptodateHomeUrl`.
5. If you end up directly on `https://www.uptodate.com/contents/search`
   after login (no redirect chain), the default value will work — UTD
   detects your institution from cookies on subsequent visits.

## AI chat sidebar

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| `enableChat` | bool | `true` | Master toggle. False hides the toolbar button and shortcut. |
| `chatHomeUrl` | string | `"https://claude.ai/new"` | URL the chat dock loads on a fresh install. After the user clicks any provider button, `chatLastUrl` (below) overrides this. |
| `chatLastUrl` | string / null | `null` | Internal: the user's last-selected provider URL. Persisted across restarts so the dock reopens to the same provider. |
| `chatProviders` | list of `[label, url]` / null | `null` | Override the built-in provider list. `null` uses the bundled set (Claude, Perplexity, ChatGPT, Gemini, Copilot, DeepSeek, Grok, Duck). When more than five providers are configured the surplus collapses into a `▾` overflow menu. |
| `chatAdblockEnabled` | bool | `true` | Inject a small CSS-only rule that hides upgrade-banner / paywall selectors on chat sites. Pure CSS, no filter list, no network calls. |
| `chatCustomProviderUrl` | string / null | `null` | Optional 9th provider button pointing at a self-hosted endpoint (OpenWebUI, LibreChat, llama.cpp web UI, etc.). |

The chat dock is a webview only — it hosts your existing logged-in
chat session in a named `theankidote-chat` profile (cookies persist
across restarts). No API keys, no programmatic chat — the user types
into the embedded provider's web UI exactly as they would in a normal
browser tab.

The "Open externally" `↗` button in each dock header opens the current
page in the system browser. Useful for passkey / Touch ID sign-in,
video DRM, or any other feature an embedded webview can't trigger.

The "send selection to chat" shortcut (`Ctrl+Shift+P`) writes the
reviewer's current text selection to the system clipboard and opens
the chat dock. Paste manually into the chat input. The addon never
submits messages programmatically.

### Passkey limitation

macOS restricts the Touch ID / Secure Enclave platform authenticator
to Apple-entitled apps (Safari, Chrome.app). Embedded QtWebEngine
webviews can't trigger it — same restriction in every Anki sidebar
addon (AnkiTerminator V2 included). Use password + 2FA; the named-
profile cookie store keeps you signed in across restarts.

## UI

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| `shortcutTogglePearls` | string | `"Ctrl+Shift+S"` | Toggle the StatPearls dock. |
| `shortcutToggleUptodate` | string | `"Ctrl+Shift+U"` | Toggle the UTD dock. |
| `shortcutToggleChat` | string | `"Ctrl+Shift+A"` | Toggle the AI chat dock. |
| `shortcutSearchSelection` | string | `"Ctrl+Shift+L"` | Search the current selection in UpToDate. |
| `shortcutSendSelectionToChat` | string | `"Ctrl+Shift+P"` | Copy the current selection and open the chat dock. |
| `dockSide` | `"right"` / `"left"` | `"right"` | Which side all docks appear on. |
| `minWidth` | int | `400` | Minimum dock width (pixels). |
| `toolbarOrder` | list | `["chat", "uptodate"]` | Left-to-right display order of the chat and UpToDate toolbar buttons. Edited in Settings via a drag-list. The pearls crown sits separately at the toolbar's right edge. |
| `rememberDockState` | bool | `false` | Reopen the same docks at the next Anki launch. |
| `debug` | bool | `false` | Verbose logging to stderr. Enable when filing bug reports — full tracebacks land in Anki's debug console (`Help → Debug Console`). |

On macOS, Anki maps `Ctrl` to `⌘` automatically — the bindings show
as `⌘⇧S` etc. The macOS `Ctrl` modifier is reachable as `Meta` if
you really want a macOS-specific binding distinct from `⌘`.

## Internal / managed flags

These are flipped automatically by the addon. You can set them
manually if you want to, but you usually don't need to.

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| `firstRunDone` | bool | `false` | Set to `true` after the welcome dialog has been completed. Toggle it back to `false` (or use Tools → The AnkiDote → "Run setup again…") to re-trigger the dialog. |
| `tourSeen` | bool | `false` | Legacy flag from when the welcome dialog and the post-install tour were separate. Retained for forward-compatibility but no longer used. |
| `dockState_pearls` / `dockState_uptodate` / `dockState_chat` | bool | `false` | Last-seen visibility of each dock. Only consulted when `rememberDockState` is `true`. |
