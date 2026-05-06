# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.

"""Unified config helpers - single source of truth for both subpackages.

Both `pearls` and `uptodate` import from here so config keys are unified
and the on-disk JSON file is shared.  Keys keep their semantic prefix
(`uptodate*` for UTD-specific, `chat*` for chat-specific) for readability
in config.md.

Cache: invalidate-on-write.  Earlier versions used a 2-second TTL which
rebuilt the cache on every read past the window even when nothing had
changed.  We now load lazily once, then update the cache directly on
every `set_value` call - reads are O(1) with no syscall after first
load.
"""

from aqt import mw

# Anki maps add-on configs by package name.  Resolve to the top-level
# folder name so getConfig/writeConfig work regardless of whether this
# module is imported as `theankidote._config` or any sub-import path.
_PKG = __name__.split(".")[0]

_DEFAULTS = {
    # ── Highlighting (StatPearls + DrugBank) ─────────────────────────
    "enableHighlights": True,
    "enableHighlightsOnQuestions": True,
    "enableArticleViewer": True,
    "highlightColor": "#0fcad4",
    "autoSearch": True,
    "maxResults": 8,

    # User-defined popup terms.  String containing a JSON array of
    # objects {title, summary, url, case_sensitive?}.  Merged into
    # the reviewer's term list at render time.  Stored as a string
    # rather than a parsed list so we don't have to revalidate the
    # whole config blob on every load - the reviewer parses lazily
    # and caches.
    "customTerms": None,

    # ── UpToDate sidebar ────────────────────────────────────────────
    "enableUpToDate": True,
    # Default home URL is the public UpToDate search page; subscribers
    # are redirected to their institution's SSO automatically on first
    # visit, then cookies persist.  NSW/Vic Health users behind the
    # HCN proxy or any institution with a custom SP-initiated entry
    # URL should set their direct entry point in Settings.
    "uptodateHomeUrl": "https://www.uptodate.com/contents/search",
    "uptodateAutoSearchCard": True,
    "uptodateKeepaliveIntervalMinutes": 20,

    # ── AI chat sidebar ─────────────────────────────────────────────
    "enableChat": True,
    "chatHomeUrl": "https://claude.ai/new",
    "chatLastUrl": None,
    "chatProviders": None,
    "chatAdblockEnabled": True,
    "chatCustomProviderUrl": None,

    # ── UI ──────────────────────────────────────────────────────────
    "shortcutTogglePearls":        "Ctrl+Shift+S",
    "shortcutToggleUptodate":      "Ctrl+Shift+U",
    "shortcutSearchSelection":     "Ctrl+Shift+L",
    "shortcutToggleChat":          "Ctrl+Shift+A",
    "shortcutSendSelectionToChat": "Ctrl+Shift+P",
    "dockSide": "right",
    "minWidth": 400,

    # Toolbar button order.  List of {"chat","uptodate"} in left-to-
    # right display order.  Edited from Settings via a drag-list.
    "toolbarOrder": ["chat", "uptodate"],

    # Persist which docks were open at exit and reopen them next launch.
    "rememberDockState": False,
    "dockState_pearls":   False,
    "dockState_uptodate": False,
    "dockState_chat":     False,

    # Verbose logging.  Off by default; users flip this to True when
    # filing bug reports so we get full tracebacks.
    "debug": False,

    # Internal first-run flags.
    "firstRunDone": False,
    "tourSeen": False,
}


_cache_val: "dict | None" = None


def _load() -> dict:
    global _cache_val
    if _cache_val is None:
        try:
            _cache_val = mw.addonManager.getConfig(_PKG) or {}
        except Exception:
            _cache_val = {}
    return _cache_val


def get(key: str):
    cache = _load()
    return cache.get(key, _DEFAULTS.get(key))


def set_value(key: str, value) -> None:
    """Persist a config value and refresh the cache immediately."""
    global _cache_val
    try:
        cfg = mw.addonManager.getConfig(_PKG) or {}
        cfg[key] = value
        mw.addonManager.writeConfig(_PKG, cfg)
        _cache_val = cfg
    except Exception:
        # Don't crash the caller if config write fails; just log and
        # update the in-memory cache so the runtime sees the new value
        # even if it isn't on disk.  Logging via _log would be circular
        # (it imports _config), so a plain print is fine here.
        print(f"[TheAnkiDote] config write failed for {key!r}")
        if _cache_val is None:
            _cache_val = {}
        _cache_val[key] = value


def invalidate() -> None:
    """Drop the cache; used by tests + on profile switch."""
    global _cache_val
    _cache_val = None
