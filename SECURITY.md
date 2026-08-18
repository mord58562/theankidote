# Security policy

## Reporting a vulnerability

If you discover a security issue in The AnkiDote, please report it
privately rather than opening a public GitHub issue.

**Preferred channel:** open a GitHub Security Advisory at
<https://github.com/mord58562/theankidote/security/advisories/new>. This
gives us a private workspace to discuss and patch before public
disclosure.

**Fallback:** email the maintainer via the address shown on the GitHub
profile <https://github.com/mord58562>.

Please include:

- A clear description of the issue.
- Steps to reproduce, ideally with a minimal config snippet.
- The Anki version (`Help → About`) and the operating system you tested
  on.
- Any relevant addon-debug-console output (enable `debug: true` in the
  addon config first to get full tracebacks).

## Scope

The AnkiDote is an Anki desktop addon. Threats we treat as in-scope:

- Code execution via crafted card content (e.g. malicious `data-sp-url`
  attributes, JavaScript injection via popup HTML).
- Privilege escalation through the embedded webview profile.
- Cookie / session token leakage between the three webview profiles
  or to disk locations the user wouldn't expect.
- Bypass of the http/https URL whitelist on the `tad_open:` pycmd
  handler.
- Bugs that allow a malicious deck to navigate the user's authenticated
  Claude / UpToDate / DrugBank session to attacker-controlled URLs
  without their knowledge.
- Anything reachable through the term-library content channel added in
  2.0: the manifest fetch, the library download, the validation that
  gates it, and the file write that stores it. Treat the content host
  as untrusted when reasoning about this - the whole point of the
  review in 2.1 was that a compromised or spoofed host should not be
  able to run code, read files, write outside `user_files/`, or leave
  the add-on permanently unable to start.

Out of scope:

- Vulnerabilities in Anki itself, in QtWebEngine / Chromium, or in
  PyQt - please report those upstream.
- Vulnerabilities in third-party services whose web UIs the addon
  embeds (Claude.ai, OpenAI, etc) - report those to the relevant
  vendor.
- Issues that require physical access to the user's machine (cookies
  stored at rest are documented as plaintext, in line with every
  desktop browser).

## Disclosure timeline

Maintainer will acknowledge receipt within 7 days, propose a fix
window, and credit the reporter (with their consent) in the release
notes once the patch ships on AnkiWeb.

## Hardening posture

The addon's defensive posture, for context:

- All deck-content URL navigations go through `_is_safe_url`
  (http/https only). Cross-origin navigations to unrecognised hosts
  are logged at debug level for audit.
- The three webview profiles use named QWebEngineProfiles so cookies
  are scoped to the addon and never leak into Anki's main webview or
  any other addon's webviews.
- No remote config and no telemetry. There is one network fetch beyond
  Anki's own addon-update path: the term-library content channel, added
  in 2.0 and on by default since 2.0.1. It sends nothing about the
  collection, fetches JSON only, and can be turned off in
  Settings > General > Reference database, which stops all content
  network activity.
- Downloaded content is data, never code. It is parsed with
  `json.loads` and is never imported, `exec`'d or unpickled; a test
  parses `pearls/_updater.py` and fails the build if `pickle`, `exec`,
  `eval`, `marshal`, `importlib` or `subprocess` appear in it.
- Both content URLs - the manifest address from config and the library
  address the manifest names - must be `https`, checked before the
  request and again after any redirect. `urllib` will otherwise fetch
  `file://`, `ftp://` and `data:` as readily as a web address.
- Downloaded content is checked against a published sha256 and byte
  count *before* it is parsed, then validated entry by entry across
  every vocabulary before it is written. A file that fails is renamed
  to `.rejected` rather than retried at every launch. Entry URLs must
  be `http`/`https` to validate, so a non-web link cannot be stored,
  let alone clicked.
- The download is written through a temp file opened with
  `O_CREAT | O_EXCL | O_NOFOLLOW`, so a planted symlink cannot redirect
  the write, and moved into place with `os.replace`.
- No API keys, no credential storage. Authentication is via the user's
  own embedded browser session in each provider's web UI.
- Addon settings live in Anki's standard addon-config JSON (handled
  by `mw.addonManager`).
- Cookies + cache live in QtWebEngine's per-profile directory under
  `~/Library/Application Support/Anki2/QtWebEngine/<profile>/` (macOS),
  `%APPDATA%\Anki2\QtWebEngine\<profile>\` (Windows), or
  `$XDG_DATA_HOME/Anki2/QtWebEngine/<profile>/` (Linux). These are NOT
  encrypted at rest - same as every desktop browser. If you share the
  machine with someone you don't trust, set up a separate OS account.
