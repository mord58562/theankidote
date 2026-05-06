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

from . import _config, _theme, _dock_layout, _log, _easter_eggs
from .pearls import _reviewer

# One-shot legacy config-key migration.  AnkiPearls + AnkiDate users
# upgrading from those standalone addons may carry their old config
# names; we copy values forward where defaults differ and drop the
# legacy keys.  Idempotent.
_LEGACY_KEY_MAP = {
    "ankipearls_enableHighlights": "enableHighlights",
    "ankipearls_highlightColor":   "highlightColor",
    "ankipearls_autoSearch":       "autoSearch",
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
            _pearls_panel.load_url(url)
            show_pearls_dock()
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

def _send_selection_to_chat() -> None:
    if _config.get("enableChat") is False:
        return
    try:
        from . import chat as _chat_mod
    except Exception as exc:
        _log.error("send-to-chat: chat import", exc)
        return

    def _handle(text: str) -> None:
        text = (text or "").strip()
        if not text:
            return
        try:
            try:
                from PyQt6.QtGui import QGuiApplication
            except (ImportError, AttributeError):
                from PyQt5.QtGui import QGuiApplication
            QGuiApplication.clipboard().setText(text)
        except Exception as exc:
            _log.error("clipboard write", exc)
        try:
            _chat_mod.toggle_dock_show_only()
        except Exception as exc:
            _log.error("send-to-chat: toggle_dock_show_only", exc)
        try:
            from aqt.utils import tooltip
            tooltip("Selection copied. Paste into the chat.", period=1500)
        except Exception:
            pass

    try:
        if mw.state == "review" and mw.reviewer and mw.reviewer.web:
            mw.reviewer.web.page().runJavaScript(
                "window.getSelection().toString()", _handle
            )
            return
    except Exception as exc:
        _log.error("send-to-chat: reviewer JS", exc)
    try:
        mw.web.page().runJavaScript("window.getSelection().toString()", _handle)
    except Exception as exc:
        _log.error("send-to-chat: main JS", exc)


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

    # Pearls keyboard shortcut.  Anchored to mw so it fires whenever
    # the main window has focus.
    shortcut = _config.get("shortcutTogglePearls") or "Ctrl+Shift+S"
    try:
        from PyQt6.QtGui import QShortcut
    except (ImportError, AttributeError):
        from PyQt5.QtWidgets import QShortcut
    _pearls_shortcut = QShortcut(QKeySequence(shortcut), mw)
    _pearls_shortcut.activated.connect(toggle_pearls_dock)

    # Send-selection-to-chat shortcut.  Default Ctrl+Shift+P.
    send_seq = _config.get("shortcutSendSelectionToChat") or "Ctrl+Shift+P"
    if send_seq:
        _send_chat_shortcut = QShortcut(QKeySequence(send_seq), mw)
        _send_chat_shortcut.activated.connect(_send_selection_to_chat)

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

    _reviewer.register_hooks()
    _easter_eggs.register()

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

def _qt_imports():
    try:
        from PyQt6.QtCore import Qt as _Qt
        from PyQt6.QtWidgets import (
            QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QDialogButtonBox,
            QLabel, QFrame, QLineEdit, QGroupBox, QPushButton, QPlainTextEdit,
            QListWidget, QListWidgetItem, QAbstractItemView,
            QScrollArea, QWidget,
        )
    except (ImportError, AttributeError):
        from PyQt5.QtCore import Qt as _Qt
        from PyQt5.QtWidgets import (
            QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QDialogButtonBox,
            QLabel, QFrame, QLineEdit, QGroupBox, QPushButton, QPlainTextEdit,
            QListWidget, QListWidgetItem, QAbstractItemView,
            QScrollArea, QWidget,
        )
    return locals()


def _build_modules_group(_w, first_run: bool):
    pearls_default = True if first_run else (_config.get("enableHighlights") is not False)
    utd_default    = True if first_run else (_config.get("enableUpToDate") is not False)
    chat_default   = True if first_run else (_config.get("enableChat") is not False)

    pearls_sc = _config.get("shortcutTogglePearls") or "Ctrl+Shift+S"
    utd_sc    = _config.get("shortcutToggleUptodate") or "Ctrl+Shift+U"
    chat_sc   = _config.get("shortcutToggleChat") or "Ctrl+Shift+A"

    box = _w["QGroupBox"]("Modules")
    lay = _w["QVBoxLayout"](box)
    pearls_cb = _w["QCheckBox"](f"StatPearls + DrugBank popups ({pearls_sc})")
    pearls_cb.setChecked(pearls_default)
    utd_cb = _w["QCheckBox"](f"UpToDate sidebar ({utd_sc})")
    utd_cb.setChecked(utd_default)
    chat_cb = _w["QCheckBox"](f"AI chat sidebar ({chat_sc})")
    chat_cb.setChecked(chat_default)
    lay.addWidget(pearls_cb)
    lay.addWidget(utd_cb)
    lay.addWidget(chat_cb)
    return box, pearls_cb, utd_cb, chat_cb


def _build_pearls_group(_w):
    box = _w["QGroupBox"]("StatPearls + DrugBank")
    lay = _w["QVBoxLayout"](box)
    pearls_qcb = _w["QCheckBox"]("Highlight terms on the question side too")
    pearls_qcb.setChecked(_config.get("enableHighlightsOnQuestions") is not False)
    lay.addWidget(pearls_qcb)
    articleview_cb = _w["QCheckBox"](
        "Open clicked popups in the side panel (uncheck to use external browser)"
    )
    articleview_cb.setChecked(_config.get("enableArticleViewer") is not False)
    lay.addWidget(articleview_cb)
    # Custom popup terms - free-form JSON the user can edit.  Stored
    # under `customTerms` and merged into reviewer term resolution.
    hint = _w["QLabel"](
        "Custom popup terms (JSON): list of {\"title\": \"...\", "
        "\"summary\": \"...\", \"url\": \"https://...\"}.  Leave blank for none."
    )
    hint.setWordWrap(True)
    hint.setStyleSheet(f"color:{_theme.MUTED};font-size:11px;")
    lay.addWidget(hint)
    custom_terms_edit = _w["QPlainTextEdit"]()
    custom_terms_edit.setPlainText(_config.get("customTerms") or "")
    custom_terms_edit.setFixedHeight(100)
    custom_terms_edit.setStyleSheet(
        "QPlainTextEdit{font-family:monospace;font-size:11px;"
        f"border:1px solid {_theme.TEAL_BORDER};border-radius:3px;}}"
    )
    lay.addWidget(custom_terms_edit)
    return box, pearls_qcb, articleview_cb, custom_terms_edit


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
    explainer.setStyleSheet(f"color:{_theme.MUTED};font-size:11px;")
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
    cu_label = _w["QLabel"](
        "Optional custom provider URL (self-hosted OpenWebUI / "
        "LibreChat / llama.cpp).  Adds a 'Custom' button to the dock."
    )
    cu_label.setWordWrap(True)
    cu_label.setStyleSheet(f"color:{_theme.MUTED};font-size:11px;")
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
    passkey_note.setStyleSheet(
        f"color:{_theme.MUTED};font-size:10px;font-style:italic;"
        "padding-top:4px;"
    )
    lay.addWidget(passkey_note)
    return box, adblock_cb, chat_url_edit


def _build_order_group(_w):
    Qt_ = _w["_Qt"]
    box = _w["QGroupBox"]("Toolbar button order")
    lay = _w["QVBoxLayout"](box)
    lay.setContentsMargins(8, 4, 8, 6)
    lay.setSpacing(4)
    hint = _w["QLabel"]("Drag to reorder the chat and UpToDate toolbar buttons.")
    hint.setStyleSheet(f"color:{_theme.MUTED};font-size:11px;")
    hint.setWordWrap(True)
    lay.addWidget(hint)
    lst = _w["QListWidget"]()
    lst.setDragDropMode(_w["QAbstractItemView"].DragDropMode.InternalMove)
    lst.setSelectionMode(_w["QAbstractItemView"].SelectionMode.SingleSelection)
    lst.setFixedHeight(56)
    lst.setStyleSheet(
        "QListWidget{border:1px solid " + _theme.TEAL_BORDER
        + ";border-radius:4px;font-size:12px;}"
        "QListWidget::item{padding:4px 8px;}"
    )
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


def _build_misc_group(_w):
    box = _w["QGroupBox"]("Other")
    lay = _w["QVBoxLayout"](box)
    remember_cb = _w["QCheckBox"](
        "Reopen the same docks at next Anki launch"
    )
    remember_cb.setChecked(bool(_config.get("rememberDockState")))
    lay.addWidget(remember_cb)
    debug_cb = _w["QCheckBox"](
        "Verbose debug logging (for bug reports)"
    )
    debug_cb.setChecked(bool(_config.get("debug")))
    lay.addWidget(debug_cb)
    return box, remember_cb, debug_cb


def _open_settings_dialog(first_run: bool = False) -> bool:
    """Unified settings dialog.

    First-run mode shows just the module checkboxes for a fast first
    decision.  Post-install mode adds the deeper per-module options
    plus the toolbar-order drag list and the new misc group.

    Returns True on Save, False on Cancel."""
    _w = _qt_imports()
    QDialog = _w["QDialog"]
    Qt_ = _w["_Qt"]

    dlg = QDialog(mw)
    dlg.setWindowTitle("The AnkiDote - welcome" if first_run
                       else "The AnkiDote - settings")
    dlg.setMinimumWidth(620)
    dlg.setMinimumHeight(560)
    dlg.resize(640, 720)

    # Outer layout: header text, scroll area (containing all the
    # group boxes), then a fixed footer with the buttons.  The scroll
    # area lets every group box breathe at full size while the dialog
    # itself stays at a comfortable on-screen height.
    outer = _w["QVBoxLayout"](dlg)
    outer.setContentsMargins(20, 18, 20, 14)
    outer.setSpacing(10)

    intro_text = (
        "Welcome.  Three reference modules - untick any you don't want."
        if first_run else
        "Quick module toggles are also available directly under "
        "Tools > The AnkiDote.  Use this dialog for the deeper options "
        "(institution URL, custom chat provider, custom popup terms, "
        "highlight/popup behaviour, button order)."
    )
    intro = _w["QLabel"](intro_text)
    intro.setWordWrap(True)
    intro.setStyleSheet(f"color:{_theme.MUTED};font-size:12px;")
    outer.addWidget(intro)

    scroll = _w["QScrollArea"]()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(_w["QFrame"].Shape.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt_.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll_body = _w["QWidget"]()
    lay = _w["QVBoxLayout"](scroll_body)
    lay.setContentsMargins(0, 0, 8, 0)
    lay.setSpacing(14)
    scroll.setWidget(scroll_body)
    outer.addWidget(scroll, 1)

    modules_box, pearls_cb, utd_cb, chat_cb = _build_modules_group(_w, first_run)
    lay.addWidget(modules_box)

    pearls_qcb = articleview_cb = utd_url_edit = chat_url_edit = None
    adblock_cb = toolbar_order_list = remember_cb = debug_cb = None
    custom_terms_edit = None
    save_without_restart = False

    if first_run:
        outro = _w["QLabel"](
            "Manage these and per-module options anytime via "
            "Tools > The AnkiDote."
        )
        outro.setWordWrap(True)
        outro.setStyleSheet(f"color:{_theme.MUTED};font-size:11px;")
        lay.addWidget(outro)
    else:
        pearls_box, pearls_qcb, articleview_cb, custom_terms_edit = _build_pearls_group(_w)
        lay.addWidget(pearls_box)
        utd_box, utd_url_edit = _build_utd_group(_w)
        lay.addWidget(utd_box)
        chat_box, adblock_cb, chat_url_edit = _build_chat_group(_w)
        lay.addWidget(chat_box)
        order_box, toolbar_order_list = _build_order_group(_w)
        lay.addWidget(order_box)
        misc_box, remember_cb, debug_cb = _build_misc_group(_w)
        lay.addWidget(misc_box)

        lay.addStretch(1)

    # Fixed footer outside the scroll area: the save-without-restart
    # checkbox and the OK/Cancel buttons stay on-screen no matter how
    # far down the user has scrolled.
    skip_restart_cb = None
    if not first_run:
        sep = _w["QFrame"]()
        sep.setFrameShape(_w["QFrame"].Shape.HLine)
        sep.setStyleSheet(f"color:{_theme.TEAL_BORDER};")
        outer.addWidget(sep)

        skip_restart_cb = _w["QCheckBox"](
            "Save without restarting now (apply some changes on next launch)"
        )
        skip_restart_cb.setChecked(False)
        outer.addWidget(skip_restart_cb)

    btns = _w["QDialogButtonBox"](
        _w["QDialogButtonBox"].StandardButton.Save
        | _w["QDialogButtonBox"].StandardButton.Cancel
    )
    save_btn = btns.button(_w["QDialogButtonBox"].StandardButton.Save)
    save_btn.setText("Continue" if first_run else "Save && restart Anki")
    btns.accepted.connect(dlg.accept)
    btns.rejected.connect(dlg.reject)
    outer.addWidget(btns)

    if dlg.exec() != QDialog.DialogCode.Accepted:
        return False

    _config.set_value("enableHighlights", pearls_cb.isChecked())
    _config.set_value("enableUpToDate",   utd_cb.isChecked())
    _config.set_value("enableChat",       chat_cb.isChecked())

    if not first_run:
        if pearls_qcb is not None:
            _config.set_value("enableHighlightsOnQuestions", pearls_qcb.isChecked())
        if articleview_cb is not None:
            _config.set_value("enableArticleViewer", articleview_cb.isChecked())
        if utd_url_edit is not None:
            text = utd_url_edit.text().strip() or None
            _config.set_value("uptodateHomeUrl", text)
        if chat_url_edit is not None:
            text = chat_url_edit.text().strip() or None
            _config.set_value("chatCustomProviderUrl", text)
        if adblock_cb is not None:
            _config.set_value("chatAdblockEnabled", adblock_cb.isChecked())
        if custom_terms_edit is not None:
            _config.set_value("customTerms",
                              custom_terms_edit.toPlainText().strip() or None)
        if toolbar_order_list is not None:
            new_order = []
            for i in range(toolbar_order_list.count()):
                key = toolbar_order_list.item(i).data(Qt_.ItemDataRole.UserRole)
                if key:
                    new_order.append(key)
            if new_order:
                _config.set_value("toolbarOrder", new_order)
        if remember_cb is not None:
            _config.set_value("rememberDockState", remember_cb.isChecked())
        if debug_cb is not None:
            _config.set_value("debug", debug_cb.isChecked())

        save_without_restart = bool(skip_restart_cb.isChecked())

    if not first_run and not save_without_restart:
        _relaunch_anki()
    elif not first_run and save_without_restart:
        try:
            from aqt.utils import tooltip
            tooltip(
                "Settings saved.  Some changes apply on next Anki launch.",
                period=2500,
            )
        except Exception:
            pass
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


gui_hooks.main_window_did_init.append(_setup)
