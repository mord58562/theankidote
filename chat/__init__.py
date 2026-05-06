# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""
TheAnkiDote.chat - lazy-loaded AI chat side panel.

Hosts the user's existing chat session in a named QWebEngineProfile.  No
API keys, no programmatic chat scraping - the user manually types in the
embedded provider's web UI exactly as they would in a normal browser tab.
ToS-clean because the user's interaction with the AI is their own
authenticated session through the provider's official web interface.

Bring-your-own-account: free tiers of ChatGPT, Claude, Gemini, Copilot,
Perplexity, and DeepSeek are supported because the user logs in once via
their normal account.  Cookies persist in the named profile across Anki
restarts.  No paid API key required - the addon is just a window onto
the user's existing chat session.

Performance posture:
  * Lazy load - the QWebEngineView, QDockWidget, and provider profile are
    not constructed until the user first clicks the toolbar button.  At
    Anki startup the chat module costs only one toolbar HTML link plus a
    pycmd handler registration.
  * No background activity - no keepalive timer, no auto-search hook, no
    polling.  The dock does nothing unless the user is actively using it.
  * No data scraping - no automated requests, no content extraction.

Convenience features (all manual user actions, no automation):
  * Provider quick-switch buttons in the dock header - one click loads
    that provider's URL in the same webview.  An overflow `▾` menu
    holds the less-frequently-used providers when more than five are
    configured, keeping the header tidy.
  * "Open externally" button - opens the current chat page in the
    user's default system browser, e.g. when an embedded webview
    can't trigger Touch-ID/passkey sign-in or media DRM.  Replaces
    the older "copy card" button (which pulled card text to the
    clipboard) - users who want that flow now use Ctrl+Shift+P
    (`shortcutSendSelectionToChat`).
"""

import os
import time
import base64

from aqt import mw, gui_hooks
from aqt.toolbar import Toolbar

try:
    from PyQt6.QtCore import Qt, QUrl, QTimer, QObject, QEvent, QSize
    from PyQt6.QtGui import QAction, QKeySequence, QGuiApplication, QIcon
    from PyQt6.QtWidgets import (
        QDockWidget, QHBoxLayout, QVBoxLayout, QWidget, QPushButton,
        QApplication, QDialog,
    )
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import (
        QWebEnginePage, QWebEngineProfile, QWebEngineSettings,
    )
except ImportError:
    from aqt.qt import (
        QDockWidget, QHBoxLayout, QVBoxLayout, QWidget, QPushButton,
        QAction, QKeySequence, Qt, QUrl, QTimer, QGuiApplication,
        QObject, QEvent, QApplication, QSize, QIcon, QDialog,
        QWebEngineView, QWebEnginePage, QWebEngineProfile, QWebEngineSettings,
    )

from .. import _config, _theme, _webengine, _log

# ── Constants ─────────────────────────────────────────────────────────────

TOGGLE_CMD   = "theankidote_chat_toggle"
PROFILE_NAME = "theankidote-chat"
CHAT_HOME    = "https://claude.ai/new"

# UA spoofing, sec-ch-ua headers, persistent cookies, and stealth JS
# all live in the shared `_webengine` module - see ChatBrowser.__init__.

# Provider quick-switch buttons rendered in the dock header. Order matters
# - the first entry is the addon's recommended default, second is the
# next in the cycle.  Cookies for all providers persist in the same
# named QWebEngineProfile so the user can be logged into every provider
# simultaneously and switch between them with one click.  No automation:
# clicking a button only fires a normal navigation request.
DEFAULT_PROVIDERS = [
    ("Claude",     "https://claude.ai/new"),
    ("Perplexity", "https://www.perplexity.ai/"),
    ("ChatGPT",    "https://chat.openai.com/"),
    ("Gemini",     "https://gemini.google.com/app"),
    ("Copilot",    "https://copilot.microsoft.com/"),
    ("DeepSeek",   "https://chat.deepseek.com/"),
    ("Grok",       "https://grok.com/"),
    ("Duck",       "https://duck.ai/"),
]

# Per-provider logo PNGs bundled under web/ai_logos/.  These are the
# providers' publicly-published brand marks, used here only as toolbar/
# tab icons that link to the user's authenticated session - the same way
# a normal browser displays a tab's favicon.  No SVG approximations:
# the user requested the actual logos.
#
# Toolbar icon proportions match the UpToDate logo button: rendered at
# height:1.1em with vertical-align:middle, so chat sits centred in line
# with the UTD button on the same baseline.

_ADDON_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LOGOS_DIR    = os.path.join(_ADDON_DIR, "web", "ai_logos")
_FAVICONS_DIR = os.path.join(_ADDON_DIR, "user_files", "favicons")


def _bundled_logo_path(label: str) -> str:
    return os.path.join(_LOGOS_DIR, f"{label}.png")


# In-memory cache of bundled-logo base64 strings.  Bundled PNGs never
# change at runtime, so a single read per provider is safe and avoids
# disk I/O on every toolbar redraw (which fires on every provider
# switch + every dock toggle + various other events).
_BUNDLED_LOGO_CACHE: dict = {}

# Throttle for favicon disk writes - keyed by provider label, value
# is the monotonic timestamp of the last save.
_FAVICON_SAVE_TS: dict = {}


def _bundled_logo_b64(label: str):
    """Read the bundled PNG logo for `label` and return base64-encoded
    bytes, or None if no bundled logo exists for this provider.  Memoised
    on first read - bundled assets don't change at runtime."""
    if label in _BUNDLED_LOGO_CACHE:
        return _BUNDLED_LOGO_CACHE[label]
    p = _bundled_logo_path(label)
    if not os.path.exists(p):
        _BUNDLED_LOGO_CACHE[label] = None
        return None
    try:
        with open(p, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        _BUNDLED_LOGO_CACHE[label] = data
        return data
    except Exception as exc:
        _log.error(f"bundled logo read {label!r}", exc)
        _BUNDLED_LOGO_CACHE[label] = None
        return None


# Generic chat-bubble fallback (only used for the Custom slot or
# completely-unknown providers).  Inline SVG, ~150 bytes.
_CUSTOM_BUBBLE_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#0fcad4">'
    '<path d="M3 5h18a2 2 0 012 2v9a2 2 0 01-2 2H10l-5 4v-4H3a2 2 0 01-2-2V7a2 2 0 012-2z"/>'
    '</svg>'
)


# Favicon cache - QtWebEngine downloads each provider's favicon
# automatically as part of the normal page load.  We listen to the
# QWebEnginePage.iconChanged signal and save the icon to disk on first
# capture, then use the cached PNG as the toolbar icon - higher-fidelity
# than the bundled brand PNG when available.


def _favicon_path(label: str) -> str:
    return os.path.join(_FAVICONS_DIR, f"{label}.png")


def _save_favicon(label: str, qicon) -> bool:
    """Persist the QIcon to the cache dir.  Returns True if saved.

    Throttled - QtWebEngine fires `iconChanged` repeatedly during a
    page load (favicon, then preview-bitmap, then full-resolution),
    each of which would trigger a fresh `pixmap.save()` and a toolbar
    redraw without this guard.  We only save once per label per
    minute since favicons rarely change.
    """
    if qicon is None or qicon.isNull():
        return False
    now = time.monotonic()
    last = _FAVICON_SAVE_TS.get(label, 0.0)
    if now - last < 60.0:
        return False
    try:
        os.makedirs(_FAVICONS_DIR, exist_ok=True)
        pix = qicon.pixmap(64, 64)
        if pix.isNull():
            return False
        ok = bool(pix.save(_favicon_path(label), "PNG"))
        if ok:
            _FAVICON_SAVE_TS[label] = now
        return ok
    except Exception as exc:
        _log.error(f"favicon save {label!r}", exc)
        return False


def _cached_favicon_b64(label: str):
    """Return base64-encoded PNG of the cached favicon, or None."""
    p = _favicon_path(label)
    if not os.path.exists(p):
        return None
    try:
        with open(p, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None


# Theme palette - shared with the StatPearls + UpToDate panels via the
# top-level _theme module.  Aliased to local names so existing references
# elsewhere in this file keep working.
_NAVY        = _theme.NAVY
_TEAL        = _theme.TEAL
_TEAL_DIM    = _theme.TEAL_DIM
_TEAL_BORDER = _theme.TEAL_BORDER
_HEADER_TXT  = _theme.HEADER_TXT
_MUTED       = _theme.MUTED

# CSS-only adblock for chat sites.  Hides the most common upsell/banner
# selectors with `!important`.  Pure CSS, no filter list, no network
# calls; injected once per page load via a QWebEngineScript installed on
# the profile so it runs on every site without per-URL detection.  ~500
# bytes uncompressed - the lightweight footprint asked for.
_CHAT_ADBLOCK_CSS = """
[data-testid*="upgrade"],[data-testid*="upsell"],
[class*="upgrade-cta"],[class*="upsell-cta"],
[class*="-promo-"],[class*="promo-banner"],
[class*="trial-banner"],[class*="paywall-banner"],
[id*="upgrade-banner"],[id*="promo-banner"],
[aria-label*="Upgrade to"],[aria-label*="Try Pro"],
[role="banner"][class*="upgrade"]
{display:none !important;visibility:hidden !important;height:0 !important;}
"""

# JS that injects the CSS on document_start so banners never flash.
_CHAT_ADBLOCK_JS = (
    "(function(){"
    "var s=document.createElement('style');"
    "s.id='theankidote-chat-adblock';"
    "s.textContent=" + repr(_CHAT_ADBLOCK_CSS).replace("'", '"') + ";"
    "document.documentElement.appendChild(s);"
    "})();"
)


# Stealth JS lives in the shared `_webengine` module and is installed
# automatically by `_webengine.apply_to_profile`.


# ── Module-level state - all None until first user activation ─────────────

_dock    = None   # QDockWidget, lazily created
_browser = None   # ChatBrowser widget, lazily created
_dock_visible = False  # tracked flag (Qt async show/hide workaround)
_key_filter = None  # ShortcutOverride event filter, installed once


# ── Key-event filter ──────────────────────────────────────────────────────
#
# When the user is typing into the embedded chat input, pressing Enter
# should submit the prompt.  But Anki registers reviewer shortcuts
# (Enter, Space, 1-9) on the main window with WindowShortcut context
# - they fire even when focus is inside our dock's webview, advancing
# the current card mid-typing.  AnkiTerminator V2 has the same edge-case.
#
# Fix: install a QApplication event filter that intercepts the
# `ShortcutOverride` event for these specific keys ONLY when focus is
# inside our chat dock.  Calling event.accept() at this stage prevents
# QShortcut from firing, while the underlying KeyPress is still
# delivered to the focused webview - so the chat input still receives
# the keystroke and submits the form.

class _ChatKeyFilter(QObject):
    KEYS_TO_BLOCK = frozenset([
        Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space,
        Qt.Key.Key_1, Qt.Key.Key_2, Qt.Key.Key_3, Qt.Key.Key_4,
        Qt.Key.Key_5, Qt.Key.Key_6, Qt.Key.Key_7, Qt.Key.Key_8, Qt.Key.Key_9,
    ])

    def eventFilter(self, obj, event):
        if event.type() != QEvent.Type.ShortcutOverride:
            return False
        if event.key() not in self.KEYS_TO_BLOCK:
            return False
        if _dock is None or not _dock.isVisible():
            return False
        focused = QApplication.focusWidget()
        if focused is None:
            return False
        # Walk parent chain - is the focused widget inside our dock?
        w = focused
        while w is not None:
            if w is _dock:
                # Accept the event so QShortcut doesn't fire.  The
                # underlying KeyPress still propagates to the webview's
                # input field via Qt's normal delivery chain.
                event.accept()
                return True
            w = w.parent()
        return False


def _ensure_key_filter():
    """Install the ShortcutOverride filter on the application once."""
    global _key_filter
    if _key_filter is not None:
        return
    try:
        app = QApplication.instance()
        if app is None:
            return
        _key_filter = _ChatKeyFilter()
        app.installEventFilter(_key_filter)
    except Exception as exc:
        print(f"[TheAnkiDote.chat] key filter install error: {exc}")


# ── Page + popup window ──────────────────────────────────────────────────
#
# OAuth flows (Google, Microsoft, Apple, Anthropic) call window.open() to
# host the auth handshake, then post a token back to the parent via
# postMessage.  If we shunt the popup to the system browser the message
# pipe is severed and sign-in silently fails.
#
# Solution: spawn a transient QDialog that hosts a QWebEngineView on the
# SAME named profile, so cookies and JS contexts are shared.  The popup
# closes itself when the OAuth flow finishes (`window.close()` ->
# `windowCloseRequested`).

class _ChatPopup(QDialog):
    """Transient popup window for OAuth and other window.open() flows.

    Lives on the same named profile as the parent so cookies are shared
    and postMessage between popup and opener works as it would in a
    normal browser.  Self-destructs when the page asks to close (or
    when the user dismisses it manually)."""

    def __init__(self, profile, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sign in")
        self.resize(540, 720)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.view = QWebEngineView(self)
        self.page = _ChatPage(profile, self)
        self.view.setPage(self.page)
        layout.addWidget(self.view)
        try:
            self.page.windowCloseRequested.connect(self.close)
        except Exception:
            pass


class _ChatPage(QWebEnginePage):
    """Page that hosts the chat session.  Spawns popup windows on the
    same profile (NOT the system browser) so OAuth handshakes complete
    correctly."""

    def createWindow(self, _type):
        try:
            owner = self.parent()
            popup = _ChatPopup(self.profile(),
                               owner if isinstance(owner, QWidget) else None)
            popup.show()
            return popup.page
        except Exception as exc:
            print(f"[TheAnkiDote.chat] popup window error: {exc}")
            return None


# ── Browser widget ────────────────────────────────────────────────────────

class ChatBrowser(QWidget):
    """Provider-switching webview. Lazy-built on first dock open."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.profile = QWebEngineProfile(PROFILE_NAME, self)
        # Chrome UA, sec-ch-ua headers, persistent cookies + disk cache,
        # full WebEngineSettings, and DocumentCreation-time stealth JS.
        # Without this stack OAuth providers (Google, Microsoft, Apple,
        # Anthropic) and Cloudflare Turnstile both reject the session.
        _webengine.apply_to_profile(self.profile)

        try:
            from PyQt6.QtWebEngineCore import QWebEngineScript
        except (ImportError, AttributeError):
            from aqt.qt import QWebEngineScript

        if _config.get("chatAdblockEnabled") is not False:
            ad_script = QWebEngineScript()
            ad_script.setName("theankidote-chat-adblock")
            ad_script.setSourceCode(_CHAT_ADBLOCK_JS)
            ad_script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
            ad_script.setRunsOnSubFrames(True)
            ad_script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
            self.profile.scripts().insert(ad_script)

        self.page = _ChatPage(self.profile, self)
        self.view = QWebEngineView(self)
        self.view.setPage(self.page)

        # QtWebEngine downloads the page's favicon as part of normal
        # page load.  Save it to the cache dir on first capture for each
        # provider so the toolbar icon shows the actual brand logo.
        try:
            self.page.iconChanged.connect(self._on_icon_changed)
        except Exception as exc:
            _log.error("chat iconChanged connect", exc)

        # Renderer crash recovery.  The QtWebEngine renderer is a
        # separate OS process which Chromium can kill under memory
        # pressure or GPU crashes.  Without this hook the dock just
        # goes blank until the user restarts Anki.
        try:
            self.page.renderProcessTerminated.connect(self._on_render_crash)
        except Exception as exc:
            _log.error("chat renderProcessTerminated connect", exc)

        # ── header: nav + provider quick-switch + utility buttons ──────
        header = QWidget()
        header.setFixedHeight(40)
        header.setStyleSheet(f"QWidget {{ background: {_NAVY}; }}")
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(6, 0, 6, 0)
        h_lay.setSpacing(3)

        self._btn_back    = self._nav_btn("‹", self.view.back,    "Back",    24)
        self._btn_forward = self._nav_btn("›", self.view.forward, "Forward", 24)
        self._btn_back.setEnabled(False)
        self._btn_forward.setEnabled(False)

        h_lay.addWidget(self._btn_back)
        h_lay.addWidget(self._btn_forward)

        # Provider quick-switch buttons - icon only.  Each shows the
        # provider's brand mark; tooltip identifies it.  Up to the
        # first MAX_INLINE providers render in-line; the remainder
        # collapse into a `▾` overflow menu so a busy header stays
        # compact even when the user has 8+ providers configured.
        providers = list(self._providers())
        MAX_INLINE = 5
        inline = providers[:MAX_INLINE]
        overflow = providers[MAX_INLINE:]
        for label, url in inline:
            btn = QPushButton()
            btn.setFixedSize(28, 28)
            btn.setToolTip(f"Switch to {label}")
            icon = self._provider_icon(label)
            if icon is not None:
                btn.setIcon(icon)
                btn.setIconSize(QSize(20, 20))
            else:
                btn.setText(label[:1])
            btn.clicked.connect(
                lambda _=False, u=url: self.switch_provider(u)
            )
            btn.setStyleSheet(_provider_btn_qss())
            h_lay.addWidget(btn)
        if overflow:
            self._btn_more = QPushButton("▾")
            self._btn_more.setFixedSize(22, 28)
            self._btn_more.setToolTip("More providers")
            self._btn_more.setStyleSheet(_provider_btn_qss())

            def _open_overflow():
                try:
                    from PyQt6.QtWidgets import QMenu
                except (ImportError, AttributeError):
                    from PyQt5.QtWidgets import QMenu
                menu = QMenu(self._btn_more)
                for label, url in overflow:
                    act = menu.addAction(label)
                    act.triggered.connect(
                        lambda _=False, u=url: self.switch_provider(u)
                    )
                menu.exec(
                    self._btn_more.mapToGlobal(self._btn_more.rect().bottomLeft())
                )
            self._btn_more.clicked.connect(_open_overflow)
            h_lay.addWidget(self._btn_more)

        h_lay.addStretch(1)

        # Open the current page in the user's default system browser.
        # Replaces the older 📋 button (which copied the current card
        # to the clipboard) - that flow is now Ctrl+Shift+P, leaving
        # this slot for the more universally-useful "escape hatch" of
        # finishing a task in a real browser when an embedded webview
        # can't (passkey sign-in, video DRM, file downloads, etc.).
        self._btn_external = self._nav_btn(
            "↗", self._open_externally,
            "Open current page in system browser",
            28,
        )
        h_lay.addWidget(self._btn_external)

        # Close
        self._btn_close = self._nav_btn("✕", toggle_dock, "Close", 26)
        h_lay.addWidget(self._btn_close)

        self.view.urlChanged.connect(self._update_nav)
        self.view.loadFinished.connect(self._update_nav)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(header)
        layout.addWidget(self.view)
        self.setMinimumWidth(_config.get("minWidth") or 400)

        # Restore the user's last-selected provider URL across Anki
        # restarts.  Falls back to the configured chatHomeUrl (Claude
        # by default) on a fresh install.
        self.load(_last_or_home_url())

    @staticmethod
    def _providers():
        """Resolve the provider quick-switch list.

        Order:
        1. `chatProviders` in config if the user supplied a full custom list.
        2. Otherwise the built-in DEFAULT_PROVIDERS.
        3. Append a 'Custom' button if `chatCustomProviderUrl` is set
           (e.g. self-hosted OpenWebUI / LibreChat / llama.cpp).
        """
        cfg = _config.get("chatProviders")
        if isinstance(cfg, list) and cfg:
            cleaned = []
            for entry in cfg:
                if isinstance(entry, (list, tuple)) and len(entry) == 2:
                    cleaned.append((str(entry[0]), str(entry[1])))
            providers = cleaned or list(DEFAULT_PROVIDERS)
        else:
            providers = list(DEFAULT_PROVIDERS)
        custom = _config.get("chatCustomProviderUrl")
        if isinstance(custom, str) and custom.strip():
            q = QUrl(custom)
            if q.isValid() and q.scheme() in ("http", "https"):
                providers.append(("Custom", custom))
        return providers

    def load(self, url: str):
        self.view.load(QUrl(url))

    def _on_icon_changed(self, qicon):
        """Cache the favicon for whichever provider the webview is
        currently displaying.  Triggers a toolbar redraw so the new
        cached icon replaces the SVG fallback immediately."""
        try:
            current_url = self.view.url().toString()
        except Exception:
            return
        label = _provider_for_url(current_url)
        if label == "Claude" and "claude.ai" not in current_url.lower():
            return
        if _save_favicon(label, qicon):
            _request_toolbar_redraw()

    def switch_provider(self, url: str):
        """Provider button click: load the URL AND persist it as the
        user's last-selected provider so the choice survives restarts.

        No-ops if the user is already on this provider's URL - clicking
        the same button used to reload and lose chat state.
        """
        try:
            current = self.view.url().toString()
        except Exception:
            current = ""
        if current and _provider_for_url(current) == _provider_for_url(url) \
                and current.split("?")[0].rstrip("/") == url.split("?")[0].rstrip("/"):
            return
        self.load(url)
        try:
            _config.set_value("chatLastUrl", url)
        except Exception as exc:
            _log.error("chatLastUrl persist", exc)
        _request_toolbar_redraw()

    def _open_externally(self):
        """Open the current page in the system browser.  Useful when
        an embedded webview can't trigger Touch-ID / passkey sign-in,
        video DRM, or file dialogs that the host OS would handle."""
        try:
            from aqt.utils import openLink
            url = self.view.url().toString()
            if url and url.startswith(("http://", "https://")):
                openLink(url)
        except Exception as exc:
            _log.error("chat open externally", exc)

    def _on_render_crash(self, status, exit_code):
        """Renderer process died.  Save the URL we were on and reload
        after a brief delay so the dock recovers without an Anki
        restart.  Falls back to the home URL if the prior URL is
        blank / about:blank."""
        _log.warn(f"chat renderer terminated (status={status}, exit={exit_code})")
        try:
            self._crash_url = self.view.url().toString()
        except Exception:
            self._crash_url = None
        QTimer.singleShot(1500, self._recover_after_crash)

    def _recover_after_crash(self):
        url = getattr(self, "_crash_url", None)
        blank = {"about:blank", "", "chrome-error://chromewebdata/"}
        target = url if url and url not in blank else _last_or_home_url()
        try:
            self.view.load(QUrl(target))
        except Exception as exc:
            _log.error("chat post-crash reload", exc)

    def _nav_btn(self, text: str, callback, tip: str, w: int) -> QPushButton:
        btn = QPushButton(text)
        if w:
            btn.setFixedSize(w, 28)
        else:
            btn.setFixedHeight(28)
        btn.setToolTip(tip)
        btn.clicked.connect(callback)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {_HEADER_TXT};
                border: none;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 600;
                padding: 0 6px;
            }}
            QPushButton:hover {{
                background: {_TEAL_DIM};
                color: {_TEAL};
            }}
            QPushButton:disabled {{ color: {_MUTED}; }}
        """)
        return btn

    def _provider_icon(self, label: str):
        """Return a QIcon for the provider button - cached favicon if
        available, falls back to the bundled brand PNG.  Returns None
        if neither exists (caller falls back to a 1-letter label)."""
        try:
            fav = _favicon_path(label)
            if os.path.exists(fav):
                return QIcon(fav)
            bundled = _bundled_logo_path(label)
            if os.path.exists(bundled):
                return QIcon(bundled)
        except Exception:
            pass
        return None

    def _update_nav(self, *_):
        try:
            h = self.page.history()
            self._btn_back.setEnabled(h.canGoBack())
            self._btn_forward.setEnabled(h.canGoForward())
        except Exception:
            pass


# ── Helpers ───────────────────────────────────────────────────────────────

def _validated(url: str, fallback: str) -> str:
    q = QUrl(url) if url else None
    if q and q.isValid() and q.scheme() in ("http", "https"):
        return url
    return fallback


def _home_url() -> str:
    """Configured chat home URL or the built-in default (Claude)."""
    return _validated(_config.get("chatHomeUrl") or "", CHAT_HOME)


def _last_or_home_url() -> str:
    """Last-selected provider URL if persisted, else the home URL.
    Used on dock open so the user lands back on whichever AI they were
    using before Anki was last shut down."""
    last = _config.get("chatLastUrl") or ""
    if last:
        return _validated(last, _home_url())
    return _home_url()


def _dock_area():
    side = _config.get("dockSide") or "right"
    return (Qt.DockWidgetArea.LeftDockWidgetArea if side == "left"
            else Qt.DockWidgetArea.RightDockWidgetArea)


def _request_toolbar_redraw() -> None:
    """Throttled toolbar redraw via the top-level helper, with a
    plain redraw fallback if the helper isn't reachable yet."""
    try:
        from .. import request_toolbar_redraw
        request_toolbar_redraw()
    except Exception:
        try:
            mw.toolbar.redraw()
        except Exception as exc:
            _log.error("toolbar.redraw fallback", exc)


# ── Dock toggle (lazy) ────────────────────────────────────────────────────

def _build_dock_lazily():
    """Create the dock + browser on first open. Heavy Qt objects are NOT
    instantiated at addon startup - only when the user clicks the button."""
    global _dock, _browser
    if _dock is not None:
        return
    _browser = ChatBrowser()
    _dock = QDockWidget()
    _dock.setObjectName("TheAnkiDote_dock_chat")
    _dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
    _dock.setTitleBarWidget(QWidget())
    _dock.setWidget(_browser)
    mw.addDockWidget(_dock_area(), _dock)
    _dock.hide()
    # Install the key filter only after the dock exists - the filter
    # gates on `_dock is not None and isVisible()` so it's a no-op in
    # all other contexts.
    _ensure_key_filter()


def toggle_dock():
    global _dock_visible
    _build_dock_lazily()
    if _dock is None:
        return
    if _dock_visible:
        _dock.hide()
        _dock_visible = False
    else:
        _dock.show()
        _dock_visible = True
        try:
            if mw.dockWidgetArea(_dock) != _dock_area():
                mw.removeDockWidget(_dock)
                mw.addDockWidget(_dock_area(), _dock)
                _dock.show()
        except Exception as exc:
            _log.error("chat dock area enforcement", exc)
    try:
        _config.set_value("dockState_chat", _dock_visible)
    except Exception:
        pass
    _request_toolbar_redraw()


def toggle_dock_show_only():
    """Open the chat dock if it's currently hidden; no-op if already
    visible.  Used by the send-selection-to-chat shortcut so the dock
    is guaranteed to be on-screen but isn't toggled off if the user
    fires the shortcut twice."""
    global _dock_visible
    _build_dock_lazily()
    if _dock is None or _dock_visible:
        return
    _dock.show()
    _dock_visible = True
    try:
        _config.set_value("dockState_chat", True)
    except Exception:
        pass
    _request_toolbar_redraw()


def _close_dock(*_):
    """Hard teardown on profile switch."""
    global _dock, _browser, _dock_visible
    if _dock is not None:
        _dock.close()
        _dock.deleteLater()
        _dock = None
    if _browser is not None:
        _browser.deleteLater()
        _browser = None
    _dock_visible = False


# ── Toolbar button (always cheap to render) ───────────────────────────────

# UTD's toolbar logo renders at 1.1em / vertical-align middle.  We match
# those proportions exactly: a 16x14 SVG sized to 1.1em with the same
# vertical alignment so the chat button sits on the same baseline as the
# UTD button.

def _provider_btn_qss() -> str:
    """Stylesheet for the dock header's icon-only provider buttons.
    Pulls from the shared theme so colours follow Anki's light/dark
    setting."""
    return (
        "QPushButton {"
        f" background: transparent;"
        f" color: {_HEADER_TXT};"
        " border: none;"
        " border-radius: 5px;"
        " padding: 2px;"
        "}"
        "QPushButton:hover {"
        f" background: {_TEAL_DIM};"
        "}"
        "QPushButton:pressed {"
        f" background: {_TEAL_BORDER};"
        "}"
    )


def _provider_for_url(url: str) -> str:
    """Match the URL to a known provider label by host substring."""
    if not url:
        return "Claude"
    u = url.lower()
    for label, host in (
        ("Claude", "claude.ai"),
        ("Perplexity", "perplexity.ai"),
        ("ChatGPT", "openai.com"),
        ("ChatGPT", "chatgpt.com"),
        ("Gemini", "gemini.google.com"),
        ("Copilot", "copilot.microsoft.com"),
        ("DeepSeek", "deepseek.com"),
        ("Grok", "grok.com"),
        ("Duck", "duck.ai"),
        ("Duck", "duckduckgo.com"),
    ):
        if host in u:
            return label
    custom = _config.get("chatCustomProviderUrl")
    if isinstance(custom, str) and url.startswith(custom):
        return "Custom"
    return "Claude"


def _icon_html_for(label: str) -> str:
    """Build the toolbar icon HTML for `label`.

    Preference order:
    1. Cached favicon PNG (downloaded by QtWebEngine on first visit) -
       crispest match for the provider's current branding.
    2. Bundled brand logo PNG from web/ai_logos/<Label>.png - always
       available for the 8 known providers.
    3. Generic chat-bubble SVG fallback - only hit for the Custom slot
       or completely-unknown providers.

    Matches the UTD logo's on-toolbar dimensions (height:1.1em,
    vertical-align:middle) so the chat button sits centred in line with
    the UTD button on the same baseline.
    """
    fav = _cached_favicon_b64(label)
    if fav:
        return (
            f'<img src="data:image/png;base64,{fav}" '
            f'alt="{label}" '
            'style="height:1em;vertical-align:-0.18em;display:inline-block;">'
        )
    bundled = _bundled_logo_b64(label)
    if bundled:
        return (
            f'<img src="data:image/png;base64,{bundled}" '
            f'alt="{label}" '
            'style="height:1em;vertical-align:-0.18em;display:inline-block;">'
        )
    b64 = base64.b64encode(_CUSTOM_BUBBLE_SVG.encode()).decode()
    return (
        f'<img src="data:image/svg+xml;base64,{b64}" '
        f'alt="{label}" '
        'style="height:1em;vertical-align:-0.18em;display:inline-block;">'
    )


def _current_provider_label() -> str:
    """Look up the user's current provider from `chatLastUrl` or
    `chatHomeUrl` so the toolbar icon reflects their selection."""
    return _provider_for_url(_config.get("chatLastUrl") or _home_url())


# Toolbar fallback insert index used only when UTD's link is absent
# (UTD module disabled).  When UTD is present we ignore this entirely
# and position the chat link relative to UTD's actual location in the
# `links` list — see `_add_toolbar_link` below.  This is necessary
# because both chat and UTD use the same base index (6) which is past
# the end of Anki's default 5-item link list, so a plain `insert(6, x)`
# would fall through to `append` and the configured order would never
# take effect.
TOOLBAR_LINK_BASE = 6


def _add_toolbar_link(links: list, toolbar: Toolbar) -> None:
    toolbar.link_handlers[TOGGLE_CMD] = toggle_dock
    shortcut = _config.get("shortcutToggleChat") or "Ctrl+Shift+A"
    label = _current_provider_label()
    tooltip = f"Toggle AI chat sidebar ({shortcut})"
    link = (
        f'<a class=hitem tabindex="-1" aria-label="The AnkiDote - AI chat" '
        f'title="{tooltip}" '
        f'id="theankidote-chat-toolbar-link" '
        f'href=# onclick="return pycmd(\'{TOGGLE_CMD}\')">'
        f'{_icon_html_for(label)}</a>'
    )
    # Position relative to UTD's link if it has already been inserted.
    # Hooks fire in registration order (UTD before chat in our setup),
    # so by the time we run UTD's <a id="theankidote-utd-toolbar-link">
    # is already in `links`.  We use that as our anchor instead of a
    # base index — see TOOLBAR_LINK_BASE comment for the reason.
    order = _config.get("toolbarOrder") or ["chat", "uptodate"]
    chat_first = (
        "chat" in order and "uptodate" in order
        and order.index("chat") < order.index("uptodate")
    )
    utd_idx = next(
        (i for i, l in enumerate(links)
         if "theankidote-utd-toolbar-link" in l),
        None,
    )
    if utd_idx is not None:
        links.insert(utd_idx if chat_first else utd_idx + 1, link)
    elif len(links) >= TOOLBAR_LINK_BASE:
        links.insert(TOOLBAR_LINK_BASE, link)
    else:
        links.append(link)


def _on_js_message(handled, message, context):
    if message == TOGGLE_CMD:
        toggle_dock()
        return (True, None)
    return handled


# ── Hook registration (cheap - no Qt allocation) ──────────────────────────

if not globals().get("_hooks_registered"):
    gui_hooks.top_toolbar_did_init_links.append(_add_toolbar_link)
    gui_hooks.webview_did_receive_js_message.append(_on_js_message)
    try:
        gui_hooks.profile_will_close.append(_close_dock)
    except AttributeError:
        pass
    _hooks_registered = True


# ── Setup (called by top-level theankidote/__init__.py at main_window_did_init) ─

def _setup():
    """Register the keyboard shortcut.  Does NOT create the dock yet -
    that happens lazily on first toggle.  Uses QShortcut directly (no
    Tools-menu entry) - keeps the menu clean while preserving the
    binding."""
    try:
        try:
            from PyQt6.QtGui import QShortcut
        except (ImportError, AttributeError):
            from PyQt5.QtWidgets import QShortcut
        seq = _config.get("shortcutToggleChat") or "Ctrl+Shift+A"
        global _shortcut_holder
        _shortcut_holder = QShortcut(QKeySequence(seq), mw)
        _shortcut_holder.activated.connect(toggle_dock)
    except Exception as exc:
        print(f"[TheAnkiDote.chat] setup error: {exc}")
