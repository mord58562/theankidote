# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""Shared QtWebEngine profile setup.

Empirical finding: every form of "anti-detection stealth" we tried
(navigator.webdriver overrides, sec-ch-ua header injection, custom
Chrome User-Agent, Function.prototype.toString proxy, fake PluginArray,
chrome.runtime mock, WebGL parameter spoofing, etc.) made Cloudflare
*more* likely to fail us, not less.  Cloudflare's tamper-detection
specifically watches for those exact patches.  AnkiTerminator V2,
which clears Cloudflare reliably, does **none** of them - it just
runs a named QWebEngineProfile with persistent cookies and standard
settings, and Cloudflare passes.

So this module deliberately keeps things minimal.  Mirroring AT V2:

  * Named profile -> auto-persists to disk under
    ~/Library/Application Support/Anki2/QtWebEngine/<profile>/
  * ForcePersistentCookies (not just Allow) so session cookies
    survive Anki restarts - Cloudflare's `cf_clearance` is a
    session cookie and persisting it cuts repeat challenges.
  * Disk HTTP cache so a fresh-as-snow profile doesn't look like a
    bot on every load.
  * Standard JS / clipboard / localContent / autoplay settings  - 
    same set AT V2 enables.
  * No User-Agent override.  Qt 6 QtWebEngine's default UA is
    Chrome-flavoured ("Mozilla/5.0 ... Chrome/X.Y ... Safari/537.36
    QtWebEngine/<ver>").  Cloudflare accepts it; trying to fake a
    different one only creates UA/JS-API mismatches.
  * No request interceptor, no DocumentCreation script, no
    JS-side property patching.

`apply_to_profile(profile)` is the single entry point used by the
chat / UpToDate / StatPearls profiles.  Idempotent.
"""

try:
    from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
except (ImportError, AttributeError):
    from aqt.qt import QWebEngineProfile, QWebEngineSettings


def apply_to_profile(profile: "QWebEngineProfile") -> None:
    """Apply the standard browser-like settings to `profile`.

    Idempotent.  Mirrors the AT V2 webview profile setup that has
    been observed to clear Cloudflare's bot challenge on Claude.ai,
    Perplexity, and similar Cloudflare-fronted endpoints.
    """
    # ── Cookie + cache persistence ───────────────────────────────────
    # ForcePersistentCookies (NOT just AllowPersistentCookies)  - 
    # forces even session-only cookies to persist to disk.  This is
    # what AT V2 uses; the docs note it is "for testing purposes".
    # In practice it makes Cloudflare's session cookies (cf_clearance,
    # __cf_bm) survive Anki restarts so the user doesn't get re-
    # challenged on every relaunch.
    try:
        profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
        )
    except Exception:
        pass
    try:
        profile.setHttpCacheType(
            QWebEngineProfile.HttpCacheType.DiskHttpCache
        )
    except Exception:
        pass

    # ── Standard browser-like settings ───────────────────────────────
    # The AT V2 set, verbatim.  Keep this list in sync with theirs:
    # extra/missing attributes can both push Cloudflare to flag the
    # session, so don't add new ones speculatively.
    try:
        s = profile.settings()
        s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
    except Exception:
        pass

    # No UA override.  No request interceptor.  No injected scripts.
    # Trust QtWebEngine's defaults - they're what AT V2 trusts and
    # Cloudflare lets through.


def inject_stealth(profile: "QWebEngineProfile") -> None:  # pragma: no cover
    """Kept as a no-op for backwards compatibility with callers that
    still expect this symbol.  Stealth JS is no longer used - see
    module docstring."""
    return
