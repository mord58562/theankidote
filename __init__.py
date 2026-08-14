# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""
The AnkiDote - unified medical-reference sidebar for Anki
==========================================================

Top-level orchestration. Wires up the three subpackages (`pearls` for
StatPearls + DrugBank highlighting and popups; `uptodate` for the
authenticated UpToDate browser dock; `chat` for the AI chat sidebar)
into a single Anki add-on with three toolbar buttons and one shared
config.

Author : mord58562  (github.com/mord58562)
Licence: GNU General Public License v3.0 or later (see LICENSE)

Cost & access
-------------
The AnkiDote add-on itself is free and open source.  It charges for
nothing and never will.  The only paid component is UpToDate, a
third-party clinical reference that requires its own subscription
(personal or institutional).  Without UTD access, "UpToDateless mode"
hides every UTD control - StatPearls + DrugBank remain fully functional.

See README.md for an end-user overview, config.md for every
configuration key, SECURITY.md for the security disclosure process,
and CHANGELOG.md for the per-version release notes.
"""

# QtWebEngine Chromium flags note:
#
# Earlier versions of this addon set QTWEBENGINE_CHROMIUM_FLAGS in
# os.environ at module load time hoping to push
# `--disable-blink-features=AutomationControlled` into the Chromium
# command line.  That env var is read by Qt at QApplication
# construction, which has already happened by the time an Anki addon
# loads, so the assignment was a no-op.  Removed in 1.0 - we now use
# the AT V2-style minimal profile (see _webengine.py) which clears
# Cloudflare without any flag tweaks.

import base64 as _b64
import sys as _sys
from urllib.parse import unquote, urlparse

from aqt import gui_hooks, mw
from aqt.toolbar import Toolbar
from aqt.utils import openLink

try:
    from PyQt6.QtWidgets import QDockWidget, QWidget
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QAction, QKeySequence
    _NO_DOCK    = QDockWidget.DockWidgetFeature.NoDockWidgetFeatures
    _RIGHT_AREA = Qt.DockWidgetArea.RightDockWidgetArea
except (ImportError, AttributeError):
    from PyQt5.QtWidgets import QDockWidget, QWidget
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QAction, QKeySequence
    _NO_DOCK    = QDockWidget.NoDockWidgetFeatures
    _RIGHT_AREA = Qt.RightDockWidgetArea

from . import _config, _theme, _dock_layout, _log, _extras
from .pearls import _reviewer

# One-shot legacy config-key migration.  AnkiPearls + AnkiDate users
# upgrading from those standalone addons may carry their old config
# names; we copy values forward where defaults differ and drop the
# legacy keys.  Idempotent.
_LEGACY_KEY_MAP = {
    "ankipearls_enableHighlights": "enableHighlights",
    "ankipearls_highlightColor":   "highlightColor",
    "ankidate_uptodateHomeUrl":    "uptodateHomeUrl",
    "ankidate_keepaliveMins":      "uptodateKeepaliveIntervalMinutes",
}


def _migrate_legacy_keys() -> None:
    """Copy legacy ankipearls_/ankidate_ keys forward to the unified
    names.  Runs once per launch; cheap if no legacy keys are present."""
    try:
        cfg = mw.addonManager.getConfig(__name__) or {}
    except Exception as exc:
        _log.error("legacy migration: getConfig", exc)
        return
    changed = False
    for old, new in _LEGACY_KEY_MAP.items():
        if old in cfg and new not in cfg:
            cfg[new] = cfg.pop(old)
            changed = True
        elif old in cfg:
            del cfg[old]
            changed = True
    if changed:
        try:
            mw.addonManager.writeConfig(__name__, cfg)
            _log.debug("migrated legacy config keys")
        except Exception as exc:
            _log.error("legacy migration: writeConfig", exc)


_migrate_legacy_keys()

# Allow Anki's media server to serve our web/ directory.  Audit when
# adding to web/: anything in there is reachable via /_addons/<pkg>/web/
# in any reviewer or webview.  Bundled assets only - never write user
# input there.
mw.addonManager.setWebExports(__name__, r"web(\\|/).*")

if _config.get("enableUpToDate") is not False:
    from . import uptodate as _utd_mod  # noqa: F401  side-effect import
else:
    _utd_mod = None  # type: ignore[assignment]

# Chat subpackage - cheap to import (the heavy QWebEngineView is built
# only on first user click).  Hidden when explicitly disabled.
if _config.get("enableChat") is not False:
    from . import chat as _chat_mod  # noqa: F401  side-effect import
else:
    _chat_mod = None  # type: ignore[assignment]


# ── pycmd command names ───────────────────────────────────────────────────
# Namespaced with `tad_` ("the ankidote") to avoid collision with any
# legacy installs that might briefly coexist during user migration.

_PEARLS_TOGGLE_CMD = "theankidote_pearls_toggle"
_OPEN_CMD          = "tad_open"
_OPEN_CMD_PREFIX   = _OPEN_CMD + ":"


# ── toolbar icons ─────────────────────────────────────────────────────────

_CROWN_B64 = _b64.b64encode(
    b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 20">'
    b'<path d="M2,16 L2,10 L7,13 L12,3 L17,13 L22,10 L22,16 Z" fill="#0a7d85"/>'
    b'<rect x="2" y="16" width="20" height="3" rx="1.5" fill="#0a7d85"/>'
    b'</svg>'
).decode()
_CROWN_ICON = (
    f'<img src="data:image/svg+xml;base64,{_CROWN_B64}"'
    ' width="16" height="14" style="vertical-align:middle;display:block;">'
)


# ── module-level dock state ───────────────────────────────────────────────

_pearls_dock: "QDockWidget | None" = None
_pearls_panel = None
# Ctrl+Shift+P is Anki's own Switch Profile binding, so it is no longer
# the default here; Ctrl+Shift+K/J are free of documented Anki defaults.
_DEFAULT_SEND_SEL = "Ctrl+Shift+K"
_DEFAULT_SEND_CARD = "Ctrl+Shift+J"
_LEGACY_SEND_SEL = "Ctrl+Shift+P"
# Read from manifest.json so there is one place to bump.  Used only to
# decide whether an install has already seen a given release's one-time
# notices - see `_maybe_show_upgrade_notice`.
_ADDON_VERSION = "1.4.1"
# QShortcut objects are owned by Python; without a reference they are
# collected and the binding silently stops working.
_shortcut_refs: list = []
_diag_shortcut = None  # fixed chord, never rebound
_last_opened_card_id: "int | None" = None
# Explicit visibility flag - Qt's show()/hide() are async, so QDockWidget.
# isVisible() reports stale state for ~one event-loop tick after a toggle.
_pearls_dock_visible: bool = False


# ── Throttled toolbar redraw ──────────────────────────────────────────────
#
# `mw.toolbar.redraw()` rebuilds the entire toolbar HTML (including
# base64-encoded provider icons - several KB each) and is called from
# many code paths (every dock toggle, every provider switch, every
# favicon save).  Without throttling we end up re-rendering 5+ times
# per user click.
#
# Coalesce calls to a single redraw on the next event-loop tick.

_redraw_pending: bool = False


def request_toolbar_redraw() -> None:
    """Queue a single toolbar.redraw() for the next tick.  Multiple
    calls in the same tick collapse to one.  Public entry point used
    by the chat / uptodate subpackages too."""
    global _redraw_pending
    if _redraw_pending:
        return
    _redraw_pending = True
    try:
        try:
            from PyQt6.QtCore import QTimer
        except (ImportError, AttributeError):
            from PyQt5.QtCore import QTimer
        QTimer.singleShot(0, _do_toolbar_redraw)
    except Exception:
        # Fallback: just redraw synchronously.
        _do_toolbar_redraw()


def _do_toolbar_redraw() -> None:
    global _redraw_pending
    _redraw_pending = False
    try:
        mw.toolbar.redraw()
    except Exception as exc:
        _log.error("toolbar.redraw", exc)


# ── Pearls dock helpers ───────────────────────────────────────────────────

def _current_card_id() -> "int | None":
    try:
        if mw.reviewer and mw.reviewer.card:
            return mw.reviewer.card.id
    except Exception as exc:
        _log.error("current_card_id", exc)
    return None


def toggle_pearls_dock() -> None:
    """Toolbar-button entry point for the StatPearls/DrugBank dock.

    Side-effect: redraws the top toolbar so the crown button hides
    while the dock is visible (and reappears when it's closed).  The
    UpToDate button is unaffected and stays visible whatever happens
    to the StatPearls dock."""
    global _last_opened_card_id, _pearls_dock_visible
    if _pearls_dock is None:
        return
    if _pearls_dock_visible:
        _pearls_dock.hide()
        _pearls_dock_visible = False
        try:
            mw.web.setFocus()
        except Exception:
            pass
    else:
        card_id = _current_card_id()
        if _pearls_panel is not None:
            if card_id != _last_opened_card_id:
                _pearls_panel.reset_for_new_card()
            else:
                _pearls_panel.show_article_list()
        _last_opened_card_id = card_id
        _pearls_dock.show()
        _pearls_dock_visible = True
        _fix_pearls_dock()
    _persist_dock_state()
    request_toolbar_redraw()


def _term_for_url(url: str) -> str:
    """Recover the search term from a fallback search URL.

    Both fallbacks encode the term as a query parameter, so there is no
    need to thread the term separately through the JS bridge.  Returns
    "" for URLs that are already canonical - nothing to resolve."""
    try:
        # Only the names not already imported at module scope are pulled
        # in here - importing `urlparse` again would shadow the global
        # for this whole function.
        from urllib.parse import parse_qs, unquote_plus
        q = parse_qs(urlparse(url).query)
        for key in ("term", "query"):
            if q.get(key):
                return unquote_plus(q[key][0])
    except Exception:
        pass
    return ""


def show_pearls_dock() -> None:
    global _pearls_dock_visible
    if _pearls_dock and not _pearls_dock_visible:
        _pearls_dock.show()
        _pearls_dock_visible = True
        _fix_pearls_dock()
        _persist_dock_state()
        request_toolbar_redraw()


def _fix_pearls_dock() -> None:
    if _pearls_dock is None:
        return
    try:
        if mw.dockWidgetArea(_pearls_dock) != _RIGHT_AREA:
            mw.removeDockWidget(_pearls_dock)
            mw.addDockWidget(_RIGHT_AREA, _pearls_dock)
            _pearls_dock.show()
    except Exception as exc:
        _log.error("pearls dock area enforcement", exc)
    _dock_layout.arrange(_pearls_dock, _dock_layout.ORDER_PEARLS)


# ── Dock state persistence (open/closed across Anki restarts) ─────────────
#
# Saves which docks were open when the user last quit, so reopening
# Anki restores the same workspace.  Uses one config key per dock.

def _persist_dock_state() -> None:
    if not _config.get("rememberDockState"):
        return
    try:
        _config.set_value("dockState_pearls", bool(_pearls_dock_visible))
    except Exception as exc:
        _log.error("persist pearls dock state", exc)


def _restore_dock_state() -> None:
    """Reopen any dock that was visible at last exit.  Called from
    `_setup` after all docks are constructed."""
    if not _config.get("rememberDockState"):
        return
    try:
        if _config.get("dockState_pearls"):
            show_pearls_dock()
        if _config.get("enableUpToDate") is not False \
                and _config.get("dockState_uptodate"):
            from . import uptodate as _utd_mod
            try:
                _utd_mod.toggle_dock()
            except Exception as exc:
                _log.error("restore UTD dock", exc)
        if _config.get("enableChat") is not False \
                and _config.get("dockState_chat"):
            from . import chat as _chat_mod
            try:
                _chat_mod.toggle_dock()
            except Exception as exc:
                _log.error("restore chat dock", exc)
    except Exception as exc:
        _log.error("restore dock state", exc)


# ── Toolbar - pearls (crown) button ───────────────────────────────────────

_amboss_present_cache: "bool | None" = None


def _amboss_installed() -> bool:
    global _amboss_present_cache
    if _amboss_present_cache is None:
        try:
            _amboss_present_cache = any(
                "amboss" in str(a).lower()
                for a in mw.addonManager.allAddons()
            )
        except Exception as exc:
            _log.error("amboss detection", exc)
            _amboss_present_cache = False
    return _amboss_present_cache


def _add_pearls_toolbar_link(links: list, toolbar: Toolbar) -> None:
    # Always register the handler so the keyboard shortcut still works
    # when the dock is visible (closing the dock with the same shortcut).
    toolbar.link_handlers[_PEARLS_TOGGLE_CMD] = toggle_pearls_dock
    if _pearls_dock_visible:
        return
    shortcut = _config.get("shortcutTogglePearls") or "Ctrl+Shift+S"
    top = "28px" if _amboss_installed() else "4px"
    indicator_css = (
        f"position:absolute;right:0.3em;top:{top};"
        "height:22px;width:26px;"
        "display:flex;align-items:center;justify-content:center;"
        "border-radius:4px;cursor:pointer;"
        "background:rgba(255,255,255,0.07);"
        "border:1px solid rgba(10,125,133,0.45);"
        "transition:background .15s,border-color .15s;"
    )
    over_bg  = "rgba(15,202,212,.18)"
    over_bdr = "rgba(15,202,212,.7)"
    out_bg   = "rgba(255,255,255,.07)"
    out_bdr  = "rgba(10,125,133,.45)"
    link = (
        f'<a tabindex="-1" aria-label="The AnkiDote - StatPearls" '
        f'title="Toggle StatPearls / DrugBank sidebar ({shortcut})" '
        f'href="#" onclick="return pycmd(\'{_PEARLS_TOGGLE_CMD}\')" '
        f'onmouseenter="this.style.background=\'{over_bg}\';this.style.borderColor=\'{over_bdr}\';" '
        f'onmouseleave="this.style.background=\'{out_bg}\';this.style.borderColor=\'{out_bdr}\';" '
        f'style="{indicator_css}">'
        f'{_CROWN_ICON}</a>'
    )
    links.append(link)


# ── pycmd handler ─────────────────────────────────────────────────────────

# Domains we recognise as "ours" or otherwise safe to load in the
# authenticated profile.  Used as a soft check for cross-origin
# navigations triggered by deck card content - if a card embeds a
# data-sp-url attribute pointing somewhere unexpected we still allow
# http/https but log it for the user's debug audit.
_KNOWN_HOSTS = (
    "ncbi.nlm.nih.gov", "drugbank.com", "go.drugbank.com",
    "uptodate.com", "uptodate.com.acs.hcn.com.au",
)


def _is_safe_url(url: str) -> bool:
    """Whitelist URL schemes accepted by the open-in-dock pycmd handler.
    Defensive against a malicious card embedding e.g. javascript: or
    file: URLs in a span's data-sp-url attribute - those would otherwise
    be loaded into the QWebEngineView with the addon's profile."""
    s = (url or "").strip().lower()
    return s.startswith("http://") or s.startswith("https://")


def _log_unknown_host(url: str) -> None:
    """Debug-audit hook: announce when a card link goes outside the
    set of hosts we deliberately integrate with.  Only logs at the
    `debug` config level so this is silent for normal users."""
    try:
        host = urlparse(url).hostname or ""
    except Exception:
        host = ""
    if host and not any(host.endswith(h) for h in _KNOWN_HOSTS):
        _log.debug(f"opening unrecognised host '{host}' from card content")


def _on_js_message(handled, message: str, context):
    if message == _PEARLS_TOGGLE_CMD:
        toggle_pearls_dock()
        return (True, None)

    if message.startswith(_OPEN_CMD_PREFIX):
        url = unquote(message[len(_OPEN_CMD_PREFIX):])
        if not _is_safe_url(url):
            _log.debug(f"dropped unsafe URL: {url[:80]!r}")
            return (True, None)
        _log_unknown_host(url)
        # UpToDate URLs go to the UTD subpackage's authenticated dock.
        if "uptodate.com" in url:
            try:
                from . import uptodate as _utd_mod
                if _config.get("enableUpToDate") is not False \
                        and _utd_mod.open_url_in_dock(url):
                    return (True, None)
            except Exception as exc:
                _log.error("uptodate open_url_in_dock", exc)
        if _pearls_panel is not None and _config.get("enableArticleViewer"):
            # Show first, then load.  Loading into a hidden dock hands the
            # renderer a 0x0 viewport, and the page can finish loading with
            # nothing composited - the panel then appears blank until it is
            # manually reloaded.
            show_pearls_dock()
            # Strip our own fragment before navigating: it is an
            # instruction to this add-on, not part of the target URL.
            section = ""
            if "#tad-sec=" in url:
                # `unquote` is imported at module scope; re-importing it
                # here would rebind it as a function local and make the
                # earlier call on this path an unbound-local error.
                url, _, raw = url.partition("#tad-sec=")
                section = unquote(raw)
            # Pass the term so the panel can use (and populate) the
            # resolved-URL cache instead of leaving the reader on a
            # search results page.
            _pearls_panel.load_url(url, term=_term_for_url(url), section=section)
        else:
            try:
                openLink(url)
            except Exception as exc:
                _log.error(f"openLink {url[:60]!r}", exc)
        return (True, None)

    return handled


# ── Send selection to chat ────────────────────────────────────────────────
#
# Convenience shortcut that grabs the current selection from the
# reviewer (or main webview), opens the chat dock if needed, and
# copies the selection to the clipboard so the user can paste it
# straight into the AI input.  Pure clipboard write - no programmatic
# message submission, in keeping with the addon's no-API-call policy.

def _push_to_chat(text: str, what: str) -> None:
    """Copy `text`, open the chat dock, focus the message box, paste.

    The clipboard write happens first and unconditionally, because it is
    the one step that cannot fail: everything after it - finding the
    composer on whichever of the eight providers is loaded, waiting for
    a cold webview to finish loading, getting the paste to land in a
    rich-text editor - is best-effort. When any of it doesn't work the
    user is left exactly where they were before 1.4.1, with the text on
    the clipboard and a tooltip saying so.

    Nothing is submitted. The text lands in the box; the user reads it,
    edits it, and presses Enter.
    """
    text = (text or "").strip()
    if not text:
        try:
            from aqt.utils import tooltip
            tooltip("Nothing to send.", period=1500)
        except Exception:
            pass
        return
    try:
        from PyQt6.QtGui import QGuiApplication
    except (ImportError, AttributeError):
        from PyQt5.QtGui import QGuiApplication
    try:
        QGuiApplication.clipboard().setText(text)
    except Exception as exc:
        _log.error("clipboard write", exc)

    n = len(text)
    size = f"{n} chars" if n < 1000 else f"{n // 1000}k chars"

    def _report(pasted: bool) -> None:
        try:
            from aqt.utils import tooltip
            if pasted:
                tooltip(f"{what} pasted into the chat ({size}).", period=1600)
            else:
                tooltip(f"{what} copied ({size}). Paste into the chat.",
                        period=1800)
        except Exception:
            pass

    try:
        from . import chat as _chat_mod
        _chat_mod.deliver_to_composer(text, _report)
    except Exception as exc:
        _log.error("send-to-chat: open dock", exc)
        _report(False)


def _send_selection_to_chat() -> None:
    if _config.get("enableChat") is False:
        return
    handle = lambda t: _push_to_chat(t, "Selection")
    try:
        if mw.state == "review" and mw.reviewer and mw.reviewer.web:
            mw.reviewer.web.page().runJavaScript(
                "window.getSelection().toString()", handle
            )
            return
    except Exception as exc:
        _log.error("send-to-chat: reviewer JS", exc)
    try:
        mw.web.page().runJavaScript("window.getSelection().toString()", handle)
    except Exception as exc:
        _log.error("send-to-chat: main JS", exc)


# Read the card as displayed rather than from the note fields: what is
# on screen is what the question is, cloze deletions resolved, hidden
# fields excluded, and the answer only present once revealed.  Popup
# and dock chrome injected by this add-on is stripped so the model does
# not see the reference text as part of the card.
_CARD_TEXT_JS = r"""
(function () {
  try {
    var host = document.querySelector("#qa") || document.body;
    if (!host) return "";
    var clone = host.cloneNode(true);
    var junk = clone.querySelectorAll(
      "#tad-tip, .tad-tip, script, style, .replaybutton, #_tad_root");
    for (var i = 0; i < junk.length; i++) { junk[i].remove(); }
    var t = clone.innerText || clone.textContent || "";
    return t.replace(/\u00a0/g, " ")
            .replace(/[ \t]+\n/g, "\n")
            .replace(/\n{3,}/g, "\n\n")
            .trim();
  } catch (e) { return ""; }
})();
"""


def _send_card_to_chat() -> None:
    """Copy everything currently visible on the card and open the chat."""
    if _config.get("enableChat") is False:
        return
    if mw.state != "review" or not mw.reviewer or not mw.reviewer.web:
        try:
            from aqt.utils import tooltip
            tooltip("No card is being shown.", period=1500)
        except Exception:
            pass
        return
    try:
        mw.reviewer.web.page().runJavaScript(
            _CARD_TEXT_JS, lambda t: _push_to_chat(t, "Card")
        )
    except Exception as exc:
        _log.error("send-card-to-chat", exc)


# ── First-run module-selection dialog ────────────────────────────────────

def _open_uptodate_login() -> None:
    """Open the UTD sidebar and force-load the home URL so institutional
    SSO login is triggered immediately."""
    try:
        from . import uptodate as _utd_mod
        if _utd_mod._dock is None and hasattr(_utd_mod, "_setup"):
            _utd_mod._setup()
        if _utd_mod._dock is not None and not _utd_mod._dock.isVisible():
            _utd_mod._show_dock()
        if _utd_mod._browser is not None:
            try:
                from PyQt6.QtCore import QUrl
            except (ImportError, AttributeError):
                from PyQt5.QtCore import QUrl
            _utd_mod._browser.view.load(QUrl(_utd_mod._home_url()))
        request_toolbar_redraw()
    except Exception as exc:
        _log.error("auto-open UTD", exc)


def _maybe_first_run() -> None:
    """One-time module-selection dialog on the first launch after install."""
    try:
        from PyQt6.QtCore import QTimer
    except (ImportError, AttributeError):
        from PyQt5.QtCore import QTimer

    if _config.get("firstRunDone"):
        return

    def _ask():
        if _config.get("firstRunDone"):
            return
        accepted = _open_settings_dialog(first_run=True)
        _config.set_value("firstRunDone", True)
        if accepted and _config.get("enableUpToDate") is not False:
            QTimer.singleShot(50, _open_uptodate_login)

    QTimer.singleShot(800, _ask)


def _force_first_run() -> None:
    """Re-trigger the welcome / module-selection dialog from the
    Tools menu.  Used by the 'Run setup again…' entry."""
    _config.set_value("firstRunDone", False)
    _maybe_first_run()


# ── Hook registration ─────────────────────────────────────────────────────

gui_hooks.top_toolbar_did_init_links.append(_add_pearls_toolbar_link)
gui_hooks.webview_did_receive_js_message.append(_on_js_message)


# ── Shortcut (re)binding ──────────────────────────────────────────────────

def _rebind_shortcuts() -> None:
    """Build every user-editable binding from the current config.

    Called at setup and again whenever Settings closes.  Before 1.4.1
    the bindings were created once at launch, so changing one in
    Settings did nothing until the next restart - which reads as the
    setting not working rather than as a deferred one, since the whole
    point of changing a shortcut is usually that the old one clashes
    with something right now.

    An empty string disables a binding.  `_config.get` falls back to the
    packaged default when a key is missing entirely, so the `is None`
    checks below distinguish "not set" from "deliberately cleared".
    """
    try:
        from PyQt6.QtGui import QShortcut
    except (ImportError, AttributeError):
        from PyQt5.QtWidgets import QShortcut

    for sc in _shortcut_refs:
        try:
            sc.setEnabled(False)
            sc.setParent(None)
            sc.deleteLater()
        except Exception:
            pass
    _shortcut_refs.clear()

    bindings = (
        ("shortcutTogglePearls",        "Ctrl+Shift+S",     toggle_pearls_dock),
        ("shortcutSendSelectionToChat", _DEFAULT_SEND_SEL,  _send_selection_to_chat),
        ("shortcutSendCardToChat",      _DEFAULT_SEND_CARD, _send_card_to_chat),
    )
    for key, default, slot in bindings:
        seq = _config.get(key)
        if seq is None:
            seq = default
        if not seq:
            continue
        try:
            sc = QShortcut(QKeySequence(seq), mw)
            sc.activated.connect(slot)
            _shortcut_refs.append(sc)
        except Exception as exc:
            _log.error(f"bind {key}", exc)

    # The UpToDate and chat bindings live in their subpackages so they
    # aren't created for a user who has those modules switched off.
    # Reach them only if the module has actually been loaded.
    for name, fn in (("uptodate", "rebind_shortcuts"), ("chat", "rebind_shortcut")):
        mod = _sys.modules.get(f"{__name__}.{name}")
        if mod is None:
            continue
        try:
            getattr(mod, fn)()
        except Exception as exc:
            _log.error(f"{name} rebind", exc)


# ── Setup (after main window ready) ───────────────────────────────────────

def _setup() -> None:
    """Initialise pearls dock + reviewer hooks; lazily import UTD/chat
    subpackages if enabled.  Called once when Anki's main window is ready."""
    global _pearls_dock, _pearls_panel

    from ._panel_pearls import StatPearlsPanel

    _pearls_panel = StatPearlsPanel()
    _reviewer.set_panel(_pearls_panel)
    _pearls_panel._btn_close.clicked.connect(toggle_pearls_dock)

    _pearls_dock = QDockWidget()
    _pearls_dock.setObjectName("TheAnkiDote_dock_pearls")
    _pearls_dock.setFeatures(_NO_DOCK)
    _pearls_dock.setTitleBarWidget(QWidget())
    _pearls_dock.setWidget(_pearls_panel)
    mw.addDockWidget(_RIGHT_AREA, _pearls_dock)
    _pearls_dock.hide()

    # Keyboard shortcuts.  Anchored to mw so they fire whenever the
    # main window has focus, and built through `_rebind_shortcuts` so
    # Settings can re-apply them without a restart.
    _rebind_shortcuts()

    try:
        from PyQt6.QtGui import QShortcut
    except (ImportError, AttributeError):
        from PyQt5.QtWidgets import QShortcut

    # Undocumented diagnostics toggle.  Deliberately an awkward chord so
    # it cannot be hit by accident and does not collide with anything.
    # Not user-editable, so it sits outside the rebind cycle.
    global _diag_shortcut
    _diag_shortcut = QShortcut(QKeySequence("Ctrl+Alt+Shift+D"), mw)
    _diag_shortcut.activated.connect(_unlock_diagnostics)

    # Tools menu submenu.
    try:
        from PyQt6.QtWidgets import QMenu
    except (ImportError, AttributeError):
        from PyQt5.QtWidgets import QMenu

    submenu = QMenu("The AnkiDote", mw)
    mw.form.menuTools.addMenu(submenu)

    def _make_toggle(label, key, default_true=True):
        act = QAction(label, mw)
        act.setCheckable(True)
        current = _config.get(key)
        act.setChecked(current is not False if default_true else current is True)

        def _on_toggle(checked):
            _config.set_value(key, bool(checked))
        act.toggled.connect(_on_toggle)
        return act

    submenu.addAction(_make_toggle(
        "StatPearls + DrugBank", "enableHighlights", default_true=True))
    submenu.addAction(_make_toggle(
        "UpToDate sidebar", "enableUpToDate", default_true=True))
    submenu.addAction(_make_toggle(
        "AI chat sidebar", "enableChat", default_true=True))
    submenu.addSeparator()

    settings_action = QAction("Settings...", mw)
    settings_action.triggered.connect(_open_settings_dialog)
    submenu.addAction(settings_action)

    rerun_action = QAction("Run setup again...", mw)
    rerun_action.triggered.connect(_force_first_run)
    submenu.addAction(rerun_action)

    # Diagnostics live behind _unlock_diagnostics; the entry is added to
    # this submenu only once unlocked.
    global _tad_submenu
    _tad_submenu = submenu
    if _config.get("diagnosticsUnlocked"):
        _add_diagnostics_action()

    _reviewer.register_hooks()
    _extras.register()

    # Deferred so it lands after the first-run dialog rather than
    # stacking two modal windows on a fresh install.
    try:
        from aqt.qt import QTimer as _QTimer
        _QTimer.singleShot(1200, _maybe_show_upgrade_notice)
    except Exception as exc:
        _log.error("schedule upgrade notice", exc)

    if _config.get("enableUpToDate") is not False:
        try:
            from . import uptodate as _utd_mod
            if hasattr(_utd_mod, "_setup"):
                _utd_mod._setup()
        except Exception as exc:
            _log.error("uptodate setup", exc)

    if _config.get("enableChat") is not False:
        try:
            from . import chat as _chat_mod
            if hasattr(_chat_mod, "_setup"):
                _chat_mod._setup()
        except Exception as exc:
            _log.error("chat setup", exc)

    request_toolbar_redraw()
    _maybe_first_run()
    # Restore docks AFTER first-run so a fresh-install user isn't
    # presented with three open docks before they've chosen any.
    try:
        from PyQt6.QtCore import QTimer
    except (ImportError, AttributeError):
        from PyQt5.QtCore import QTimer
    QTimer.singleShot(900, _restore_dock_state)


# ── Settings dialog ───────────────────────────────────────────────────────
#
# Split into builder helpers so the top-level function stays scannable.
# Each `_build_*_group` returns the QGroupBox plus any control widgets
# the saver needs to read after the dialog is accepted.

def _is_addon_installed(addon_id: str) -> bool:
    try:
        return addon_id in {str(a) for a in mw.addonManager.allAddons()}
    except Exception:
        try:
            import os
            base = mw.addonManager.addonsFolder()
            return os.path.isdir(os.path.join(base, addon_id))
        except Exception:
            return False


def _qt_imports():
    try:
        from PyQt6.QtCore import Qt as _Qt
        from PyQt6.QtWidgets import (
            QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QDialogButtonBox,
            QLabel, QFrame, QLineEdit, QGroupBox, QPushButton, QPlainTextEdit,
            QListWidget, QListWidgetItem, QAbstractItemView,
            QScrollArea, QWidget, QGridLayout, QKeySequenceEdit, QTabWidget,
            QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView,
        )
        from PyQt6.QtGui import QKeySequence
    except (ImportError, AttributeError):
        from PyQt5.QtCore import Qt as _Qt
        from PyQt5.QtWidgets import (
            QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QDialogButtonBox,
            QLabel, QFrame, QLineEdit, QGroupBox, QPushButton, QPlainTextEdit,
            QListWidget, QListWidgetItem, QAbstractItemView,
            QScrollArea, QWidget, QGridLayout, QKeySequenceEdit, QTabWidget,
            QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView,
        )
        from PyQt5.QtGui import QKeySequence
    return locals()


def _caption(_w, text: str):
    """Small secondary-colour note.

    Uses the palette's disabled text role rather than a hard-coded
    colour so it follows the system theme, light or dark, without the
    add-on having an opinion about it.
    """
    lab = _w["QLabel"](text)
    lab.setWordWrap(True)
    try:
        from aqt.qt import QPalette
        pal = lab.palette()
        pal.setColor(QPalette.ColorRole.WindowText,
                     pal.color(QPalette.ColorGroup.Disabled,
                               QPalette.ColorRole.WindowText))
        lab.setPalette(pal)
    except Exception:
        pass
    f = lab.font()
    f.setPointSizeF(max(9.0, f.pointSizeF() - 1.5))
    lab.setFont(f)
    return lab


def _build_modules_group(_w, first_run: bool):
    """Module on/off switches.

    Deliberately three plain checkboxes.  They previously sat in
    bordered cards with monospace shortcut pills and a paragraph of
    description each, which made three booleans occupy most of the
    dialog and looked nothing like anything else in Anki.
    """
    pearls_default = True if first_run else (_config.get("enableHighlights") is not False)
    utd_default    = True if first_run else (_config.get("enableUpToDate") is not False)
    chat_default   = True if first_run else (_config.get("enableChat") is not False)

    box = _w["QGroupBox"]("Modules")
    lay = _w["QVBoxLayout"](box)
    lay.setSpacing(6)

    def _row(title, desc, checked):
        cb = _w["QCheckBox"](title)
        cb.setChecked(checked)
        lay.addWidget(cb)
        note = _caption(_w, desc)
        note.setContentsMargins(20, 0, 0, 4)
        lay.addWidget(note)
        return cb

    pearls_cb = _row(
        "Reference popups and sidebar",
        "Highlights conditions and drugs on your cards, with StatPearls "
        "and DrugBank in a side panel.", pearls_default)
    utd_cb = _row(
        "UpToDate sidebar",
        "Requires your own subscription.", utd_default)
    chat_cb = _row(
        "AI chat sidebar",
        "Uses your existing chat session. No API key needed.", chat_default)
    return box, pearls_cb, utd_cb, chat_cb


def _install_addon(addon_id: str, btn=None) -> None:
    """Open the add-on's AnkiWeb page.

    Deliberately not an in-place download: installing another author's
    add-on silently on someone's behalf is not ours to do, and the
    AnkiWeb page is where the code, reviews and permissions are.
    """
    try:
        # openLink is imported at module scope; re-importing here would
        # rebind it as a function local.
        openLink(f"https://ankiweb.net/shared/info/{addon_id}")
        if btn is not None:
            btn.setEnabled(False)
            btn.setText("Opened in your browser")
    except Exception as exc:
        _log.error("open addon page", exc)


def _build_recommendations_group(_w, first_run: bool):
    """One optional companion add-on, shown only if it isn't installed.

    A plain group box with a button: it used to be an outlined card with
    an uppercase letter-spaced header and a pill-shaped install button,
    none of which resembles anything else in Anki.
    """
    if _is_addon_installed("1374772155"):
        return None

    box = _w["QGroupBox"]("Suggested add-on")
    lay = _w["QVBoxLayout"](box)
    lay.setSpacing(6)
    lay.addWidget(_caption(
        _w, "Image Occlusion Enhanced - hide parts of a diagram to make "
            "image cards. Pairs well with the reference popups."))
    btn = _w["QPushButton"]("Install Image Occlusion Enhanced")
    btn.clicked.connect(lambda: _install_addon("1374772155", btn))
    lay.addWidget(btn)
    return box


def _parse_custom_terms(raw) -> list:
    """Config string -> list of dicts, tolerating anything malformed.

    Hand-edited JSON in a text box is guaranteed to be broken sooner or
    later, and the reviewer already ignores entries it can't use.  The
    editor takes the same view: unparseable input yields an empty table
    rather than an error, and the original string is left untouched
    unless the user actually saves.
    """
    if not raw or not isinstance(raw, str):
        return []
    try:
        import json as _json
        parsed = _json.loads(raw)
    except Exception:
        return []
    if not isinstance(parsed, list):
        return []
    return [e for e in parsed if isinstance(e, dict)]


def _custom_terms_dialog(parent, raw) -> "str | None":
    """Add/remove editor for `customTerms`.  Returns the new JSON string,
    or None if the user cancelled.

    This was a raw JSON textarea until 1.4.1 - a developer control
    wearing a preferences UI, where a missing comma silently disabled
    every custom term with no feedback anywhere.  A table can't produce
    invalid JSON, and the fields it can't represent (`article`,
    `source`) are carried through per row rather than dropped, so
    anyone who hand-wrote a richer config doesn't lose it by opening
    this window once.
    """
    _w = _qt_imports()
    Qt_ = _w["_Qt"]
    dlg = _w["QDialog"](parent)
    dlg.setWindowTitle("Custom Terms")
    dlg.resize(560, 340)
    lay = _w["QVBoxLayout"](dlg)

    lay.addWidget(_caption(
        _w, "Words to highlight on your cards in addition to the built-in "
            "databases. Clicking one opens the link you give it."))

    table = _w["QTableWidget"](0, 4)
    table.setHorizontalHeaderLabels(["Term", "Summary", "Link", "Match case"])
    table.verticalHeader().setVisible(False)
    table.setSelectionBehavior(_w["QAbstractItemView"].SelectionBehavior.SelectRows)
    try:
        hdr = table.horizontalHeader()
        RM = _w["QHeaderView"].ResizeMode
        hdr.setSectionResizeMode(0, RM.ResizeToContents)
        hdr.setSectionResizeMode(1, RM.Stretch)
        hdr.setSectionResizeMode(2, RM.Stretch)
        hdr.setSectionResizeMode(3, RM.ResizeToContents)
    except Exception:
        pass
    lay.addWidget(table, 1)

    def _add_row(entry: dict) -> None:
        r = table.rowCount()
        table.insertRow(r)
        for col, key in enumerate(("title", "summary", "url")):
            it = _w["QTableWidgetItem"](str(entry.get(key) or ""))
            if col == 0:
                # Stash the whole original entry so fields this table
                # doesn't show survive a round trip.
                it.setData(Qt_.ItemDataRole.UserRole, entry)
            table.setItem(r, col, it)
        chk = _w["QTableWidgetItem"]()
        chk.setFlags(Qt_.ItemFlag.ItemIsUserCheckable | Qt_.ItemFlag.ItemIsEnabled
                     | Qt_.ItemFlag.ItemIsSelectable)
        chk.setCheckState(Qt_.CheckState.Checked if entry.get("case_sensitive")
                          else Qt_.CheckState.Unchecked)
        table.setItem(r, 3, chk)

    for entry in _parse_custom_terms(raw):
        _add_row(entry)

    row_btns = _w["QHBoxLayout"]()
    add_btn = _w["QPushButton"]("Add")
    del_btn = _w["QPushButton"]("Remove")
    add_btn.clicked.connect(lambda: (_add_row({}),
                                     table.setCurrentCell(table.rowCount() - 1, 0),
                                     table.editItem(table.item(table.rowCount() - 1, 0))))

    def _remove():
        rows = sorted({i.row() for i in table.selectedIndexes()}, reverse=True)
        if not rows and table.currentRow() >= 0:
            rows = [table.currentRow()]
        for r in rows:
            table.removeRow(r)
    del_btn.clicked.connect(_remove)
    row_btns.addWidget(add_btn)
    row_btns.addWidget(del_btn)
    row_btns.addStretch(1)
    lay.addLayout(row_btns)

    lay.addWidget(_caption(
        _w, "Links must start with http:// or https://. Rows missing a term "
            "or a link are discarded when you save."))

    btns = _w["QDialogButtonBox"](
        _w["QDialogButtonBox"].StandardButton.Ok
        | _w["QDialogButtonBox"].StandardButton.Cancel)
    btns.accepted.connect(dlg.accept)
    btns.rejected.connect(dlg.reject)
    lay.addWidget(btns)

    if not dlg.exec():
        return None

    out = []
    for r in range(table.rowCount()):
        base = {}
        first = table.item(r, 0)
        if first is not None:
            stashed = first.data(Qt_.ItemDataRole.UserRole)
            if isinstance(stashed, dict):
                base = dict(stashed)
        def _cell(c):
            it = table.item(r, c)
            return (it.text() if it is not None else "").strip()
        title, summary, url = _cell(0), _cell(1), _cell(2)
        if not title or not url:
            continue
        if not (url.startswith("http://") or url.startswith("https://")):
            continue
        base.update({"title": title, "summary": summary, "url": url})
        chk = table.item(r, 3)
        base["case_sensitive"] = bool(
            chk is not None and chk.checkState() == Qt_.CheckState.Checked)
        if not base["case_sensitive"]:
            base.pop("case_sensitive", None)
        out.append(base)

    if not out:
        return ""
    import json as _json
    return _json.dumps(out, ensure_ascii=False, indent=2)


def _build_pearls_group(_w):
    """Reference-popup settings.

    Lives on the General tab as of 1.4.1.  It had a tab to itself, which
    held two checkboxes and a JSON box - not enough to justify a tab,
    and it read as a peer of Services and Shortcuts when it is really
    part of the same "how does the add-on behave" bucket as the module
    switches sitting directly above it.
    """
    box = _w["QGroupBox"]("Reference popups")
    lay = _w["QVBoxLayout"](box)
    pearls_qcb = _w["QCheckBox"]("Highlight terms on the question side too")
    pearls_qcb.setChecked(_config.get("enableHighlightsOnQuestions") is not False)
    lay.addWidget(pearls_qcb)
    articleview_cb = _w["QCheckBox"](
        "Open clicked popups in the side panel (uncheck to use external browser)"
    )
    articleview_cb.setChecked(_config.get("enableArticleViewer") is not False)
    lay.addWidget(articleview_cb)

    # Held in a mutable box so the button can update it without the
    # caller needing a widget handle to read back on close.
    state = {"raw": _config.get("customTerms") or ""}
    row = _w["QHBoxLayout"]()
    btn = _w["QPushButton"]("Custom terms...")
    count_lab = _caption(_w, "")

    def _refresh_count():
        n = len(_parse_custom_terms(state["raw"]))
        count_lab.setText("None set" if not n else
                          ("1 term" if n == 1 else f"{n} terms"))

    def _edit():
        new = _custom_terms_dialog(btn.window(), state["raw"])
        if new is not None:
            state["raw"] = new
            _refresh_count()

    btn.clicked.connect(_edit)
    _refresh_count()
    row.addWidget(btn)
    row.addWidget(count_lab)
    row.addStretch(1)
    lay.addLayout(row)
    return box, pearls_qcb, articleview_cb, state


def _build_utd_group(_w):
    box = _w["QGroupBox"]("UpToDate")
    lay = _w["QVBoxLayout"](box)
    explainer = _w["QLabel"](
        "Institution home URL.  Defaults to the public UpToDate search "
        "page; subscribers will be redirected to their institution's SSO "
        "automatically.  NSW Health / Vic Health users (HCN proxy) and "
        "OpenAthens / Shibboleth users may want to set their direct entry "
        "URL here - see config.md for examples."
    )
    explainer.setWordWrap(True)
    lay.addWidget(explainer)
    utd_url_edit = _w["QLineEdit"](_config.get("uptodateHomeUrl") or "")
    utd_url_edit.setPlaceholderText("https://www.uptodate.com/contents/search")
    lay.addWidget(utd_url_edit)
    return box, utd_url_edit


def _build_chat_group(_w):
    box = _w["QGroupBox"]("AI chat")
    lay = _w["QVBoxLayout"](box)
    adblock_cb = _w["QCheckBox"]("Hide ad/upsell banners on chat sites (CSS-only)")
    adblock_cb.setChecked(_config.get("chatAdblockEnabled") is not False)
    lay.addWidget(adblock_cb)
    autopaste_cb = _w["QCheckBox"](
        "Paste straight into the chat box when you send a selection or card")
    autopaste_cb.setChecked(_config.get("chatAutoPaste") is not False)
    lay.addWidget(autopaste_cb)
    lay.addWidget(_caption(
        _w, "Uncheck to copy to the clipboard only. Nothing is ever sent - "
            "you still press Enter yourself."))
    cu_label = _w["QLabel"](
        "Optional custom provider URL (self-hosted OpenWebUI / "
        "LibreChat / llama.cpp).  Adds a 'Custom' button to the dock."
    )
    cu_label.setWordWrap(True)
    lay.addWidget(cu_label)
    chat_url_edit = _w["QLineEdit"](_config.get("chatCustomProviderUrl") or "")
    chat_url_edit.setPlaceholderText("https://my-self-hosted-llm.example.com/")
    lay.addWidget(chat_url_edit)
    passkey_note = _w["QLabel"](
        "Note: passkey / Touch ID sign-in won't trigger inside an "
        "embedded webview (a macOS limitation that affects every Anki "
        "sidebar addon).  Use password + 2FA - cookies persist, so you "
        "only need to sign in once per provider."
    )
    passkey_note.setWordWrap(True)
    lay.addWidget(passkey_note)
    return box, adblock_cb, chat_url_edit, autopaste_cb


def _build_order_group(_w):
    Qt_ = _w["_Qt"]
    box = _w["QGroupBox"]("Toolbar button order")
    lay = _w["QVBoxLayout"](box)
    lay.setContentsMargins(8, 4, 8, 6)
    lay.setSpacing(4)
    hint = _w["QLabel"]("Drag to reorder the chat and UpToDate toolbar buttons.")
    hint.setWordWrap(True)
    lay.addWidget(hint)
    lst = _w["QListWidget"]()
    lst.setDragDropMode(_w["QAbstractItemView"].DragDropMode.InternalMove)
    lst.setSelectionMode(_w["QAbstractItemView"].SelectionMode.SingleSelection)
    lst.setFixedHeight(56)

    labels = {"chat": "AI chat", "uptodate": "UpToDate"}
    cur_order = _config.get("toolbarOrder") or ["chat", "uptodate"]
    seen: set = set()
    for key in cur_order:
        if key in labels and key not in seen:
            it = _w["QListWidgetItem"](labels[key])
            it.setData(Qt_.ItemDataRole.UserRole, key)
            lst.addItem(it)
            seen.add(key)
    for key in ("chat", "uptodate"):
        if key not in seen:
            it = _w["QListWidgetItem"](labels[key])
            it.setData(Qt_.ItemDataRole.UserRole, key)
            lst.addItem(it)
    lay.addWidget(lst)
    return box, lst


_SHORTCUT_FIELDS = [
    ("shortcutTogglePearls",       "Ctrl+Shift+S", "Toggle StatPearls / DrugBank"),
    ("shortcutToggleUptodate",     "Ctrl+Shift+U", "Toggle UpToDate"),
    ("shortcutToggleChat",         "Ctrl+Shift+A", "Toggle AI chat"),
    ("shortcutSearchSelection",    "Ctrl+Shift+L", "Search selection in UpToDate"),
    ("shortcutSendSelectionToChat", _DEFAULT_SEND_SEL,  "Send selection to AI chat"),
    ("shortcutSendCardToChat",      _DEFAULT_SEND_CARD, "Send whole card to AI chat"),
]


def _build_shortcuts_group(_w):
    """Editable key bindings in a plain form layout."""
    box = _w["QGroupBox"]("Shortcuts")
    form = _w["QFormLayout"](box)
    try:
        form.setLabelAlignment(_w["_Qt"].AlignmentFlag.AlignRight
                               | _w["_Qt"].AlignmentFlag.AlignVCenter)
        form.setRowWrapPolicy(_w["QFormLayout"].RowWrapPolicy.DontWrapRows)
    except Exception:
        pass
    edits = {}
    for key, default, label in _SHORTCUT_FIELDS:
        seq = _w["QKeySequenceEdit"]()
        try:
            seq.setKeySequence(_w["QKeySequence"](_config.get(key) or default))
        except Exception:
            pass
        form.addRow(label, seq)
        edits[key] = seq
    form.addRow("", _caption(_w, "Click a field and press the keys you want. "
                                 "Leave one empty to turn it off."))
    return box, edits


def _build_misc_group(_w):
    box = _w["QGroupBox"]("Other")
    lay = _w["QVBoxLayout"](box)
    remember_cb = _w["QCheckBox"](
        "Reopen the same docks at next Anki launch"
    )
    remember_cb.setChecked(bool(_config.get("rememberDockState")))
    lay.addWidget(remember_cb)
    # Diagnostics are deliberately not surfaced here; see _unlock_diagnostics.
    return box, remember_cb, None


def _open_settings_dialog(first_run: bool = False) -> bool:
    """Settings.

    Two very different jobs, so two shapes.  First run is a single
    short pane - pick your modules and go.  Afterwards it is a tabbed
    preferences window laid out the way Anki's own Preferences is:
    native widgets, no custom colours, grouped boxes, and changes that
    are written when you close rather than gated behind a Save button.
    """
    _w = _qt_imports()
    QDialog = _w["QDialog"]
    Qt_ = _w["_Qt"]

    if first_run:
        return _first_run_dialog(_w)

    dlg = QDialog(mw)
    dlg.setWindowTitle("The AnkiDote")
    dlg.resize(560, 460)
    outer = _w["QVBoxLayout"](dlg)

    tabs = _w["QTabWidget"]()
    outer.addWidget(tabs, 1)

    def _tab(*boxes):
        page = _w["QWidget"]()
        lay = _w["QVBoxLayout"](page)
        for b in boxes:
            lay.addWidget(b)
        lay.addStretch(1)
        return page

    modules_box, pearls_cb, utd_cb, chat_cb = _build_modules_group(_w, False)
    pearls_box, pearls_qcb, articleview_cb, terms_state = _build_pearls_group(_w)
    order_box, toolbar_order_list = _build_order_group(_w)
    misc_box, remember_cb, _ = _build_misc_group(_w)
    tabs.addTab(_tab(modules_box, pearls_box, order_box, misc_box), "General")

    utd_box, utd_url_edit = _build_utd_group(_w)
    chat_box, adblock_cb, chat_url_edit, autopaste_cb = _build_chat_group(_w)
    tabs.addTab(_tab(utd_box, chat_box), "Services")

    shortcuts_box, shortcut_edits = _build_shortcuts_group(_w)
    tabs.addTab(_tab(shortcuts_box), "Shortcuts")

    # Anki states this once, quietly, and lets people restart when it
    # suits them - rather than a modal asking permission to quit their
    # app the moment they change a checkbox.
    footer = _caption(_w, "Some settings take effect after you restart Anki.")
    try:
        footer.setAlignment(Qt_.AlignmentFlag.AlignCenter)
    except Exception:
        pass
    outer.addWidget(footer)

    btns = _w["QDialogButtonBox"](_w["QDialogButtonBox"].StandardButton.Close)
    btns.rejected.connect(dlg.reject)
    btns.accepted.connect(dlg.accept)
    outer.addWidget(btns)

    dlg.exec()

    # Written on close.  There is no Cancel: a preferences window that
    # can be abandoned needs a Save button, and a Save button on a
    # window of checkboxes is the thing that made this confusing.
    _config.set_value("enableHighlights", pearls_cb.isChecked())
    _config.set_value("enableUpToDate",   utd_cb.isChecked())
    _config.set_value("enableChat",       chat_cb.isChecked())
    _config.set_value("enableHighlightsOnQuestions", pearls_qcb.isChecked())
    _config.set_value("enableArticleViewer", articleview_cb.isChecked())
    _config.set_value("uptodateHomeUrl", utd_url_edit.text().strip() or None)
    _config.set_value("chatCustomProviderUrl", chat_url_edit.text().strip() or None)
    _config.set_value("chatAdblockEnabled", adblock_cb.isChecked())
    _config.set_value("chatAutoPaste", autopaste_cb.isChecked())
    _config.set_value("customTerms", terms_state["raw"].strip() or None)
    _config.set_value("rememberDockState", remember_cb.isChecked())

    order = []
    for i in range(toolbar_order_list.count()):
        key = toolbar_order_list.item(i).data(Qt_.ItemDataRole.UserRole)
        if key:
            order.append(key)
    if order:
        _config.set_value("toolbarOrder", order)

    for key, seq in shortcut_edits.items():
        try:
            _config.set_value(key, seq.keySequence().toString() or "")
        except Exception as exc:
            _log.error(f"save shortcut {key}", exc)

    # Apply the bindings now.  Until 1.4.1 they were only read at
    # launch, so a shortcut changed here appeared not to work at all
    # until the next restart - and the usual reason to change one is a
    # clash you want gone immediately.
    try:
        _rebind_shortcuts()
    except Exception as exc:
        _log.error("rebind shortcuts after settings", exc)

    try:
        request_toolbar_redraw()
    except Exception:
        pass
    return True


def _first_run_dialog(_w) -> bool:
    """Welcome pane: which modules, and the UpToDate entry point."""
    QDialog = _w["QDialog"]
    dlg = QDialog(mw)
    dlg.setWindowTitle("The AnkiDote")
    dlg.resize(520, 460)
    outer = _w["QVBoxLayout"](dlg)

    intro = _w["QLabel"]("Three reference modules. Untick anything you "
                         "don't want - you can change this later.")
    intro.setWordWrap(True)
    outer.addWidget(intro)

    modules_box, pearls_cb, utd_cb, chat_cb = _build_modules_group(_w, True)
    outer.addWidget(modules_box)

    recs_box = _build_recommendations_group(_w, True)
    if recs_box is not None:
        outer.addWidget(recs_box)

    utd_box, utd_url_edit = _build_utd_group(_w)
    outer.addWidget(utd_box)
    outer.addStretch(1)

    btns = _w["QDialogButtonBox"](_w["QDialogButtonBox"].StandardButton.Ok)
    btns.button(_w["QDialogButtonBox"].StandardButton.Ok).setText("Continue")
    btns.accepted.connect(dlg.accept)
    outer.addWidget(btns)

    if dlg.exec() != QDialog.DialogCode.Accepted:
        return False
    _config.set_value("enableHighlights", pearls_cb.isChecked())
    _config.set_value("enableUpToDate",   utd_cb.isChecked())
    _config.set_value("enableChat",       chat_cb.isChecked())
    _config.set_value("uptodateHomeUrl", utd_url_edit.text().strip() or None)
    return True


def _relaunch_anki() -> None:
    """Spawn a fresh Anki instance and trigger Anki's own clean
    shutdown for the current one.

    `mw.app.exit(0)` bypasses `unloadProfile`, which is the path that
    saves the collection, flushes pending addon-config writes, and
    runs `profile_will_close`.  Calling exit() mid-event-loop after a
    modal dialog dismiss is also a known crash trigger.

    Instead: spawn the relaunch first so the new process is on its
    way, then call `mw.unloadProfileAndExit()` (Anki's official close
    path) on the next event-loop tick.

    On macOS we relaunch via `open -n <Anki.app>` so launchd spawns a
    fresh instance even though the old one is winding down.  On
    Windows / Linux we re-exec detached so the child survives the
    parent's exit.

    `sys.executable` may be the bundled python on Linux or the Anki
    binary on macOS / Windows; falling back to `sys.argv[0]` covers
    the case where Anki is launched via a wrapper script.
    """
    import subprocess as _subprocess
    try:
        from PyQt6.QtCore import QTimer as _QTimer
    except (ImportError, AttributeError):
        from PyQt5.QtCore import QTimer as _QTimer

    exe = _sys.executable
    if not exe and _sys.argv:
        exe = _sys.argv[0]
    relaunched = False
    try:
        if _sys.platform == "darwin" and exe and "/Contents/MacOS/" in exe:
            app_path = exe.split("/Contents/MacOS/")[0]
            _subprocess.Popen(
                ["/usr/bin/open", "-n", app_path],
                stdin=_subprocess.DEVNULL,
                stdout=_subprocess.DEVNULL,
                stderr=_subprocess.DEVNULL,
            )
            relaunched = True
        elif _sys.platform == "win32" and exe:
            DETACHED_PROCESS = 0x00000008
            _subprocess.Popen(
                [exe], creationflags=DETACHED_PROCESS, close_fds=True
            )
            relaunched = True
        elif exe:
            _subprocess.Popen([exe], start_new_session=True, close_fds=True)
            relaunched = True
    except Exception as exc:
        _log.error("relaunch spawn", exc)

    def _clean_exit():
        try:
            mw.unloadProfileAndExit()
            return
        except Exception as exc:
            _log.error("unloadProfileAndExit", exc)
        try:
            mw.close()
            return
        except Exception as exc:
            _log.error("mw.close", exc)
        try:
            mw.app.quit()
        except Exception as exc:
            _log.error("mw.app.quit", exc)

    _QTimer.singleShot(0, _clean_exit)

    if not relaunched:
        try:
            from aqt.utils import showInfo
            showInfo("Settings saved.  Please restart Anki manually.")
        except Exception:
            pass


_tad_submenu = None
_diag_action = None


def _add_diagnostics_action() -> None:
    """Put the diagnostics entry in the Tools submenu."""
    global _diag_action
    try:
        if _tad_submenu is None or _diag_action is not None:
            return
        from aqt.qt import QAction as _QAction
        _diag_action = _QAction("Show diagnostic log...", mw)
        _diag_action.triggered.connect(_reveal_diagnostic_log)
        _tad_submenu.addSeparator()
        _tad_submenu.addAction(_diag_action)
    except Exception as exc:
        _log.error("add diagnostics action", exc)


def _unlock_diagnostics() -> None:
    """Toggle the hidden diagnostics entry.

    Not documented and not discoverable: the log is a developer tool and
    an extra menu item nobody uses is clutter for everyone else.
    """
    try:
        on = not bool(_config.get("diagnosticsUnlocked"))
        _config.set_value("diagnosticsUnlocked", on)
        _config.set_value("debug", on)
        from aqt.utils import tooltip
        if on:
            _add_diagnostics_action()
            tooltip("Diagnostics on - Tools > The AnkiDote.", period=2500)
        else:
            if _diag_action is not None:
                try:
                    _tad_submenu.removeAction(_diag_action)
                except Exception:
                    pass
            tooltip("Diagnostics off.", period=1800)
    except Exception as exc:
        _log.error("unlock diagnostics", exc)


def _reveal_diagnostic_log() -> None:
    """Open the diagnostic log in Finder.  Asking a user to hunt for a
    file inside an addon folder is a good way to get no bug report."""
    try:
        # `mw` and `os` are module-level imports; re-importing them here
        # would rebind them as function locals for this whole body.
        from aqt.utils import showInfo, tooltip
        import os as _os
        import subprocess as _sp
        path = _log.diag_path()
        if not _os.path.exists(path):
            with open(path, "a", encoding="utf-8"):
                pass
        try:
            if _sys.platform == "darwin":
                _sp.Popen(["open", "-R", path])
            elif _sys.platform.startswith("win"):
                _sp.Popen(["explorer", "/select,", path])
            else:
                _sp.Popen(["xdg-open", _os.path.dirname(path)])
            tooltip("Revealed diagnostic.log")
        except Exception:
            showInfo(f"Diagnostic log:\n\n{path}")
    except Exception as exc:
        _log.error("reveal diagnostic log", exc)


def _version_tuple(v) -> tuple:
    """Loose "1.4.1" -> (1, 4, 1) for ordering. Anything unparseable
    sorts as (0,), i.e. older than every real release."""
    if not isinstance(v, str):
        return (0,)
    parts = []
    for chunk in v.strip().split("."):
        digits = "".join(c for c in chunk if c.isdigit())
        if not digits:
            break
        parts.append(int(digits))
    return tuple(parts) or (0,)


def _maybe_show_upgrade_notice() -> None:
    """One-time notice for anyone arriving from a version below 1.4.

    1.4 changed a shortcut people had in their fingers: send-to-chat
    moved off Ctrl+Shift+P, which is Anki's own Switch Profile binding
    and could bounce you to the profile picker mid-review. It also
    added a second shortcut and made all of them editable.

    The 1.4.0 implementation keyed the prompt purely off whether the
    user was still sitting on Ctrl+Shift+P, and silently marked itself
    done for everyone else - so anyone who had already rebound that key
    by hand never heard about either change. Version tracking replaces
    that: `lastSeenVersion` says which release this install has
    actually run, so upgrade notices can be aimed at a version range
    instead of inferred from one config value.

    Three states have to be told apart, and none of them should see a
    dialog except the third:
      * fresh install - `firstRunDone` is still False, and the welcome
        pane is enough on its own;
      * already ran 1.4.0 - `lastSeenVersion` is absent (1.4.0 predates
        the key) but `sendShortcutMigrated` is True, because 1.4.0 set
        that flag on every path including the silent one;
      * upgrading from below 1.4 - neither is true.
    """
    try:
        seen = _config.get("lastSeenVersion")

        def _stamp() -> None:
            _config.set_value("lastSeenVersion", _ADDON_VERSION)
            _config.set_value("sendShortcutMigrated", True)

        if not _config.get("firstRunDone"):
            _stamp()
            return
        if seen is not None and _version_tuple(seen) >= (1, 4):
            _config.set_value("lastSeenVersion", _ADDON_VERSION)
            return
        if seen is None and _config.get("sendShortcutMigrated"):
            _stamp()
            return

        current = (_config.get("shortcutSendSelectionToChat") or "")
        on_legacy = (current.replace(" ", "").lower()
                     == _LEGACY_SEND_SEL.replace(" ", "").lower())

        from aqt.qt import QMessageBox
        box = QMessageBox(mw)
        box.setWindowTitle("The AnkiDote")
        box.setIcon(QMessageBox.Icon.Question if on_legacy
                    else QMessageBox.Icon.Information)

        if on_legacy:
            box.setText("Change the send-to-chat shortcut?")
            box.setInformativeText(
                f"Your shortcut for sending a selection to the AI chat is "
                f"{_LEGACY_SEND_SEL}, which is also Anki's own Switch "
                f"Profile shortcut. The new default is {_DEFAULT_SEND_SEL}."
                f"\n\n{_DEFAULT_SEND_CARD} sends the whole visible card, and "
                f"both now land straight in the chat box rather than only on "
                f"the clipboard."
                f"\n\nEvery shortcut is editable under Tools > The AnkiDote > "
                f"Settings > Shortcuts."
            )
            keep = box.addButton(f"Keep {_LEGACY_SEND_SEL}",
                                 QMessageBox.ButtonRole.RejectRole)
            change = box.addButton(f"Use {_DEFAULT_SEND_SEL}",
                                   QMessageBox.ButtonRole.AcceptRole)
            box.setDefaultButton(change)
            box.exec()
            if box.clickedButton() is change:
                _config.set_value("shortcutSendSelectionToChat", _DEFAULT_SEND_SEL)
                _rebind_shortcuts()
                try:
                    from aqt.utils import tooltip
                    tooltip(f"Send-to-chat is now {_DEFAULT_SEND_SEL}.",
                            period=3000)
                except Exception:
                    pass
        else:
            box.setText("What's new in The AnkiDote")
            box.setInformativeText(
                f"Send a selection ({_DEFAULT_SEND_SEL}) or the whole visible "
                f"card ({_DEFAULT_SEND_CARD}) to the AI chat - the text now "
                f"goes straight into the message box instead of stopping at "
                f"the clipboard. Nothing is sent until you press Enter."
                f"\n\nThe sidebar header has a StatPearls / DrugBank switch, "
                f"and Settings has been rebuilt around Anki's own Preferences "
                f"with every shortcut editable."
                f"\n\nYour existing shortcuts have been left exactly as they "
                f"are."
            )
            opener = box.addButton("Open settings",
                                   QMessageBox.ButtonRole.AcceptRole)
            box.addButton(QMessageBox.StandardButton.Ok)
            box.setDefaultButton(QMessageBox.StandardButton.Ok)
            box.exec()
            if box.clickedButton() is opener:
                _open_settings_dialog()

        _stamp()
    except Exception as exc:
        _log.error("upgrade notice", exc)
        try:
            _config.set_value("lastSeenVersion", _ADDON_VERSION)
            _config.set_value("sendShortcutMigrated", True)
        except Exception:
            pass


def _on_theme_change() -> None:
    """Follow Anki's light/dark switch mid-session.

    The palette is computed once at import, so without this the docks
    keep the theme they were built with until Anki restarts.  The
    reviewer popup already re-checks `body.nightMode` each time it
    opens, so only the Qt side needs rebuilding.
    """
    try:
        if not _theme.refresh():
            return
    except Exception as exc:
        _log.error("theme refresh", exc)
        return
    panels = [_pearls_panel]
    # The UpToDate and chat docks own their own module-level browser
    # objects; reach them through their modules rather than duplicating
    # the state here.
    for name in ("uptodate", "chat"):
        try:
            import importlib
            mod = importlib.import_module(f"{__name__}.{name}")
            panels.append(getattr(mod, "_browser", None))
        except Exception:
            pass
    for panel in panels:
        try:
            if panel is not None and hasattr(panel, "apply_theme"):
                panel.apply_theme()
        except Exception as exc:
            _log.error("panel apply_theme", exc)
    try:
        request_toolbar_redraw()
    except Exception:
        pass


try:
    gui_hooks.theme_did_change.append(_on_theme_change)
except Exception as exc:  # older Anki without the hook
    _log.debug(f"theme_did_change hook unavailable: {exc}")


gui_hooks.main_window_did_init.append(_setup)
