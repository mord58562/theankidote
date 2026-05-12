# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""
TheAnkiDote.uptodate - UpToDate dock with persistent institutional SSO.

Default home URL is the public UpToDate search page
(https://www.uptodate.com/contents/search).  This works directly for
personal subscribers and for OpenAthens / Shibboleth users whose
institution recognises the user from existing session cookies.

NSW Health and Vic Health users (HCN proxy) and any institution with a
custom SP-initiated entry URL MUST set `uptodateHomeUrl` to their own
URL - see config.md for examples.  Loading the public UTD page when
your live cookies are scoped to a proxy domain (e.g. .hcn.com.au) will
look "signed out" because the cookies don't follow.

Design:

  * Named QWebEngineProfile - cookies and cache auto-persist to disk under
    ~/Library/Application Support/Anki2/QtWebEngine/theankidote-uptodate/.
    Log in once, stay logged in indefinitely across Anki restarts.

  * Activity-gated session keepalive - a hidden QWebEnginePage on the same
    profile refreshes the UpToDate session cookie ONLY while the user has
    been active in Anki within the last 2 x interval minutes.  If the
    server redirects to an SSO/login page the session has expired and the
    dock is shown automatically for re-authentication.

  * NSW/Vic Health (HCN proxy) - set `uptodateHomeUrl` to
    https://www.uptodate.com.acs.hcn.com.au/contents/search.  Do NOT use
    bookmarked SSO URLs - stale jsessionids cause 405 errors; always
    enter via the HCN proxy host.

  * Every other institution - change `uptodateHomeUrl` in the add-on config
    to your institution's SP-initiated UpToDate URL (see config.md for
    OpenAthens / Shibboleth / direct examples).

  * Auto-search from card - when the dock is open and a new card question is
    shown, UpToDate automatically searches for the card's front-field text.

  * Selected-text search - highlight any text on a card and press the
    configured shortcut (default Ctrl+Shift+L) to search it in the dock.

  * Popup shunt - window.open() calls are forwarded to the system browser so
    institutional auth popups are handled by the user's normal browser.
"""

import os
import re
import time
from urllib.parse import quote as _url_quote

from aqt import mw, gui_hooks
from aqt.toolbar import Toolbar

try:
    from PyQt6.QtWidgets import (
        QDockWidget, QHBoxLayout, QVBoxLayout, QWidget, QPushButton,
        QFileDialog, QProgressBar,
    )
    from PyQt6.QtCore import Qt, QUrl, QTimer
    from PyQt6.QtGui import QAction, QKeySequence, QDesktopServices
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import (
        QWebEnginePage, QWebEngineProfile, QWebEngineSettings,
    )
except ImportError:
    from aqt.qt import (
        QDockWidget, QHBoxLayout, QVBoxLayout, QWidget, QPushButton,
        QFileDialog, QAction, QKeySequence, Qt, QUrl, QTimer, QDesktopServices,
        QWebEngineView, QWebEnginePage, QWebEngineProfile, QWebEngineSettings,
        QProgressBar,
    )

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

UPTODATE_HOME      = "https://www.uptodate.com/contents/search"
TOGGLE_CMD         = "theankidote_uptodate_toggle"
TOOLBAR_LINK_BASE  = 6                # sit next to AnkiTerminator (index 5)
PROFILE_NAME       = "theankidote-uptodate"  # named profile → persistent cookies
                                              # (renamed from "uptoanki" so the
                                              # legacy session is decoupled)

# URL fragments that indicate an SSO/login redirect (session expiry).
# Covers NSW Health Oracle AM, OpenAthens, Shibboleth, and generic patterns.
_SSO_PATTERNS = (
    "spzsso.cit.health.nsw.gov.au",  # NSW Health Oracle AM
    "oaam_server",                    # Oracle Access Manager (generic)
    "openathens.net",                 # OpenAthens
    "/Shibboleth.sso/",              # Shibboleth SP
    "idp.federations",                # Federation identity providers
    "wayf.",                          # WAYF / federation discovery
    "login.do",                       # Generic Java login endpoint
)


def _is_sso_url(url_str: str) -> bool:
    """Return True if the URL matches any known SSO / login-redirect pattern."""
    return any(p in url_str for p in _SSO_PATTERNS)


# Domains for which we accept institutional / self-signed certificates.
# The configured home_url domain is added dynamically in _on_cert_error.
_TRUSTED_CERT_DOMAINS = (".uptodate.com", ".hcn.com.au")

# ---------------------------------------------------------------------------
# Module-level state
# ---------------------------------------------------------------------------

_dock                      = None   # QDockWidget
_browser                   = None   # UpToDateBrowser
_keepalive_page            = None   # hidden QWebEnginePage for background session refresh
_keepalive_timer           = None   # QTimer driving the keepalive
_lifecycle_hooks_registered = False  # guard: addons_dialog + profile_will_close hooks

# Last time the user interacted with Anki (reviewer card shown, dock toggled,
# selection search). Used to gate the keepalive: we only refresh the UpToDate
# session when the user is actively using Anki, NOT in the background while
# Anki sits idle. This keeps the addon ToS-friendly - no programmatic UTD
# access happens without recent user activity.
_last_user_activity = 0.0          # monotonic seconds; 0 = never seen


# ---------------------------------------------------------------------------
# Config / theme helpers
# ---------------------------------------------------------------------------

from .. import _config, _theme, _webengine, _log


def _home_url() -> str:
    """Configured home URL, validated; falls back to the HCN default."""
    url = _config.get("uptodateHomeUrl") or UPTODATE_HOME
    q = QUrl(url)
    if not q.isValid() or q.scheme() not in ("http", "https"):
        print("[TheAnkiDote.uptodate] Invalid uptodateHomeUrl - using default")
        return UPTODATE_HOME
    return url


def _dock_area() -> "Qt.DockWidgetArea":
    """Dock area determined by config (default: right)."""
    side = _config.get("dockSide") or "right"
    return (Qt.DockWidgetArea.LeftDockWidgetArea if side == "left"
            else Qt.DockWidgetArea.RightDockWidgetArea)


_HTML_TAG_RE   = re.compile(r"<[^>]+>")
_HTML_ENTITIES = {
    "&amp;": "&", "&lt;": "<", "&gt;": ">",
    "&nbsp;": " ", "&#39;": "'", "&quot;": '"',
}

def _strip_html(text: str) -> str:
    text = _HTML_TAG_RE.sub(" ", text)
    for entity, char in _HTML_ENTITIES.items():
        text = text.replace(entity, char)
    return " ".join(text.split())


# ---------------------------------------------------------------------------
# Shared colour palette - sourced from _theme so the dock matches the
# rest of the addon's light/dark theming behaviour.
# ---------------------------------------------------------------------------

_NAVY         = _theme.NAVY
_TEAL         = _theme.TEAL
_TEAL_DIM     = _theme.TEAL_DIM
_TEAL_BORDER  = _theme.TEAL_BORDER
_HEADER_TXT   = _theme.HEADER_TXT
_MUTED        = _theme.MUTED

# ---------------------------------------------------------------------------
# Web page classes
# ---------------------------------------------------------------------------

class _PopupShunt(QWebEnginePage):
    """Throwaway page: captures the first URL of a popup, opens it in the
    system browser, then self-destructs."""
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        self.urlChanged.connect(self._open_externally)

    def _open_externally(self, url: QUrl):
        try:
            QDesktopServices.openUrl(url)
        finally:
            self.deleteLater()


class UpToDatePage(QWebEnginePage):
    """Main page.  Accepts all navigation; passes popups to the system browser;
    accepts certificates for trusted UpToDate / HCN domains only."""

    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        try:
            self.certificateError.connect(self._on_cert_error)
        except Exception:
            pass

    def _on_cert_error(self, error):
        """Accept certificate errors for known UTD domains and the user's
        configured home URL domain (covers institutional proxies)."""
        try:
            host = error.url().host()
            trusted = list(_TRUSTED_CERT_DOMAINS)
            # Also trust whatever domain the user has configured as home
            home_host = QUrl(_home_url()).host()
            if home_host:
                trusted.append(home_host)
            if any(host == d.lstrip(".") or host.endswith(d) for d in trusted):
                error.acceptCertificate()
        except Exception:
            pass

    def createWindow(self, _type):
        return _PopupShunt(self.profile(), parent=self)


# ---------------------------------------------------------------------------
# Browser widget
# ---------------------------------------------------------------------------

class UpToDateBrowser(QWidget):
    """Nav toolbar + progress bar + persistent-session UpToDate web view."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Named profile → QtWebEngine auto-persists cookies & cache to disk.
        self.profile = QWebEngineProfile(PROFILE_NAME, self)
        # Apply the shared Cloudflare-bypass / browser-hardening stack:
        # Chrome UA, sec-ch-ua client hints, persistent cookies, disk
        # cache, full WebEngineSettings, and stealth JS.  Institutional
        # SSO providers (Oracle AM, Shibboleth, OpenAthens) reject the
        # default QtWebEngine UA as an "unsupported browser".
        _webengine.apply_to_profile(self.profile)

        try:
            self.profile.downloadRequested.connect(self._on_download_requested)
        except Exception:
            pass

        self.page = UpToDatePage(self.profile, self)
        self.view = QWebEngineView(self)
        self.view.setPage(self.page)

        # Renderer crash recovery - the WebEngine renderer is a separate OS
        # process that can be killed by memory pressure, GPU issues, etc.
        # Without this, a crash leaves the view blank until Anki restarts.
        try:
            self.page.renderProcessTerminated.connect(self._on_render_crash)
        except Exception:
            pass

        # ── flat navy nav header ──────────────
        header = QWidget()
        header.setFixedHeight(44)
        header.setStyleSheet(f"QWidget {{ background: {_NAVY}; }}")
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(6, 0, 6, 0)
        h_lay.setSpacing(4)

        self._btn_back     = self._nav_btn("‹", self.view.back,    "Back")
        self._btn_forward  = self._nav_btn("›", self.view.forward,  "Forward")
        self._btn_reload   = self._nav_btn("↺", self.view.reload,   "Reload")
        self._btn_home     = self._nav_btn("⌂",
                                lambda: self.view.load(QUrl(_home_url())), "Home")
        self._btn_clear    = self._nav_btn("⎚", self._clear_session,
                                "Clear UTD session and reload "
                                "(use if stuck on a login / SSO error)")
        self._btn_external = self._nav_btn("↗", self._open_externally,
                                "Open current page in system browser")
        self._btn_close    = self._nav_btn("✕", toggle_dock,        "Close sidebar")
        self._btn_back.setEnabled(False)
        self._btn_forward.setEnabled(False)

        self.view.urlChanged.connect(self._update_nav_state)
        self.view.loadFinished.connect(self._update_nav_state)

        h_lay.addWidget(self._btn_back)
        h_lay.addWidget(self._btn_forward)
        h_lay.addWidget(self._btn_reload)
        h_lay.addWidget(self._btn_home)
        h_lay.addStretch(1)
        h_lay.addWidget(self._btn_clear)
        h_lay.addWidget(self._btn_external)
        h_lay.addWidget(self._btn_close)

        # ── teal loading bar (sits flush below header) ────────────────────
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(2)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.hide()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{ border: none; background: transparent; }}
            QProgressBar::chunk {{ background: {_TEAL}; }}
        """)
        self.view.loadStarted.connect(
            lambda: (self.progress_bar.setValue(0), self.progress_bar.show()))
        self.view.loadProgress.connect(self.progress_bar.setValue)
        self.view.loadFinished.connect(lambda _ok: self.progress_bar.hide())

        # ── layout ───────────────────────────────────────────────────────
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(header)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.view)
        self.setMinimumWidth(_config.get("minWidth") or 400)

        self.view.load(QUrl(_home_url()))

    # ------------------------------------------------------------------
    # Downloads
    # ------------------------------------------------------------------

    def _on_download_requested(self, download):
        try:
            filename = download.downloadFileName()
        except Exception:
            filename = "download"
        save_path, _ = QFileDialog.getSaveFileName(self, "Save File", filename)
        if save_path:
            directory, name = os.path.split(save_path)
            try:
                download.setDownloadDirectory(directory)
                download.setDownloadFileName(name)
                download.accept()
            except Exception:
                pass
        else:
            try:
                download.cancel()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Navigation helpers
    # ------------------------------------------------------------------

    def _nav_btn(self, text: str, callback, tip: str) -> QPushButton:
        """Create a flat ghost button matching the navy header style."""
        btn = QPushButton(text)
        btn.setFixedSize(26, 30)
        btn.setToolTip(tip)
        btn.clicked.connect(callback)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {_HEADER_TXT};
                border: none;
                border-radius: 4px;
                font-size: 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {_TEAL_DIM};
                color: {_TEAL};
            }}
            QPushButton:disabled {{
                color: {_MUTED};
            }}
        """)
        return btn

    def _update_nav_state(self, *_):
        """Enable/disable back and forward buttons based on page history."""
        try:
            hist = self.page.history()
            self._btn_back.setEnabled(hist.canGoBack())
            self._btn_forward.setEnabled(hist.canGoForward())
        except Exception as exc:
            _log.error("UTD nav state", exc)

    def _open_externally(self):
        """Open the current UTD page in the system browser.  Cookies
        won't follow (different browser profile) so the user may need
        to authenticate again externally - same as opening any
        institutional URL from outside the dock."""
        try:
            from aqt.utils import openLink
            url = self.view.url().toString()
            if url and url.startswith(("http://", "https://")):
                openLink(url)
        except Exception as exc:
            _log.error("UTD open externally", exc)

    # ------------------------------------------------------------------
    # Session reset
    # ------------------------------------------------------------------

    def _clear_session(self):
        """Wipe cookies, HTTP cache, and web storage on the UTD profile,
        then reload the home URL.  Recovery path for wedged SSO/login
        states (e.g. Oracle Access Manager 'System error', stale
        OpenAthens/Shibboleth jsessionids, expired HCN proxy tokens)
        where the existing session cookie is invalid but the server
        won't return a clean redirect.

        Confirms first because it forces a re-login.  Local state only
        - does not log the user out at the institutional IdP."""
        try:
            from aqt.utils import askUser
            if not askUser(
                "Clear the UpToDate session and reload?\n\n"
                "This deletes the dock's saved cookies and cache for "
                "UpToDate / your institutional proxy, then loads the "
                "home URL fresh. You will need to log in again.\n\n"
                "Use this if you're stuck on a login or SSO error page.",
                defaultno=True,
                title="Clear UTD session",
            ):
                return
        except Exception:
            pass

        try:
            self.profile.cookieStore().deleteAllCookies()
        except Exception as exc:
            _log.error("UTD clear cookies", exc)
        try:
            self.profile.clearHttpCache()
        except Exception as exc:
            _log.error("UTD clear cache", exc)
        # localStorage / sessionStorage are scoped per-origin and Qt has
        # no public API to wipe them across all origins; the JS below
        # clears whatever the current page has, which is enough to break
        # an Oracle AM "System error" stuck on a stale token.
        try:
            self.page.runJavaScript(
                "try { localStorage.clear(); sessionStorage.clear(); } "
                "catch (e) {}"
            )
        except Exception:
            pass
        try:
            self.view.load(QUrl(_home_url()))
        except Exception as exc:
            _log.error("UTD reload after clear", exc)

    # ------------------------------------------------------------------
    # Renderer crash recovery
    # ------------------------------------------------------------------

    def _on_render_crash(self, status, exit_code):
        """The WebEngine renderer process has died.  Save the URL we were on
        and schedule a reload so the dock recovers without an Anki restart."""
        print(f"[TheAnkiDote] renderer terminated (status={status}) - recovering in 2 s")
        try:
            self._crash_url = self.view.url().toString()
        except Exception:
            self._crash_url = None
        QTimer.singleShot(2000, self._recover)

    def _recover(self):
        """Reload after a renderer crash.  Restore the previous URL when safe;
        fall back to the home URL otherwise (e.g. crash happened on SSO page)."""
        url = getattr(self, "_crash_url", None)
        blank = {"about:blank", "", "chrome-error://chromewebdata/"}
        reload_url = (
            url if url and url not in blank and not _is_sso_url(url)
            else _home_url()
        )
        try:
            self.view.load(QUrl(reload_url))
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Dock management
# ---------------------------------------------------------------------------

def _health_check_browser():
    """If the view is in a blank or error state (e.g. after renderer crash that
    the auto-recovery timer hasn't fired for yet), kick off a reload now."""
    if _browser is None:
        return
    try:
        url = _browser.view.url().toString()
        if url in ("about:blank", "", "chrome-error://chromewebdata/"):
            _browser.view.load(QUrl(_home_url()))
    except Exception:
        pass


def toggle_dock():
    _mark_user_active()
    if _dock is None:
        return
    if _dock.isVisible():
        _dock.hide()
        try:
            mw.web.setFocus()
        except Exception:
            pass
        try:
            _config.set_value("dockState_uptodate", False)
        except Exception:
            pass
    else:
        _dock.show()
        _enforce_dock_area()
        _arrange_with_siblings()
        _health_check_browser()
        try:
            _config.set_value("dockState_uptodate", True)
        except Exception:
            pass


def _enforce_dock_area():
    if _dock is None:
        return
    if mw.dockWidgetArea(_dock) != _dock_area():
        mw.removeDockWidget(_dock)
        mw.addDockWidget(_dock_area(), _dock)
        _dock.show()


def _arrange_with_siblings():
    """Split side-by-side with any other visible dock in the same area,
    instead of letting Qt tab them together."""
    if _dock is None:
        return
    try:
        area = _dock_area()
        for child in mw.findChildren(QDockWidget):
            if child is _dock or not child.isVisible():
                continue
            if mw.dockWidgetArea(child) != area:
                continue
            mw.splitDockWidget(child, _dock, Qt.Orientation.Horizontal)
            _dock.show()
            return
    except Exception as e:
        print(f"[TheAnkiDote] dock arrange error: {e}")


def _show_dock() -> None:
    """Make the dock visible, enforce its configured area, and tile siblings."""
    if _dock is None:
        return
    _dock.show()
    _enforce_dock_area()
    _arrange_with_siblings()


def _close_dock(*_args):
    """Fully tear down dock, browser, and keepalive.  Used on profile close."""
    global _dock, _browser, _keepalive_page, _keepalive_timer
    try:
        if _keepalive_timer is not None:
            _keepalive_timer.stop()
            _keepalive_timer.deleteLater()
            _keepalive_timer = None
    except Exception:
        pass
    try:
        if _keepalive_page is not None:
            _keepalive_page.deleteLater()
            _keepalive_page = None
    except Exception:
        pass
    if _dock is not None:
        _dock.close()
        _dock.deleteLater()
        _dock = None
    if _browser is not None:
        _browser.deleteLater()
        _browser = None


def _hide_dock(*_args):
    """Hide the dock while the add-ons dialog is open, without destroying it.
    Previously _close_dock was used here, which permanently destroyed the dock
    for the rest of the session - a common cause of 'stopped working' reports."""
    if _dock is not None:
        _dock.hide()


# ---------------------------------------------------------------------------
# Session keepalive
#
# A hidden QWebEnginePage on the same named profile pings the UpToDate home
# URL every N minutes.  Because it shares the same cookie store as the visible
# browser, the server sees a normal authenticated request and refreshes the
# session cookie - so long as the user runs Anki at least every few hours
# they will never need to log in again.
#
# If the ping is redirected to the NSW Health SSO page, the session has
# expired.  The dock is shown automatically and the visible browser is
# navigated to the login entry point so the user can re-authenticate
# immediately.
# ---------------------------------------------------------------------------

def _make_keepalive_page() -> QWebEnginePage:
    """Create a hidden page on _browser's profile wired up for keepalive."""
    page = QWebEnginePage(_browser.profile, _browser)
    page.urlChanged.connect(_on_keepalive_url_changed)
    try:
        page.renderProcessTerminated.connect(_on_keepalive_crash)
    except Exception:
        pass
    return page


def _start_keepalive():
    global _keepalive_page, _keepalive_timer
    if _browser is None:
        return
    interval_mins = max(5, (_config.get("uptodateKeepaliveIntervalMinutes") or 20))

    # Hidden page on the same profile = same cookie jar as _browser
    _keepalive_page = _make_keepalive_page()

    _keepalive_timer = QTimer()
    _keepalive_timer.setInterval(interval_mins * 60 * 1000)
    _keepalive_timer.timeout.connect(_do_keepalive)
    _keepalive_timer.start()


def _mark_user_active() -> None:
    """Record that the user has just interacted with Anki.  Called from the
    reviewer hook, dock toggle, and selection-search shortcut - anywhere
    the user demonstrably is at the keyboard."""
    global _last_user_activity
    _last_user_activity = time.monotonic()


def _do_keepalive():
    """Silently refresh the UpToDate session cookie - but ONLY when the
    user has been active recently.

    Without this gate the timer would fire every 20 min for as long as Anki
    is open, including overnight when Anki is left running.  An automated
    request with no associated user activity is ToS-questionable.  Gating
    on recent activity keeps the keepalive within the spirit of "session
    follows user" and well clear of automated-access patterns.

    Window: 2 × interval (default 40 min).  If the user hasn't touched
    Anki in the last 40 minutes, skip the ping.  Their session may expire
    sooner - that's fine, they'll re-auth on next use, which is the
    correct UX anyway when away from the keyboard."""
    if _keepalive_page is None:
        return
    interval_mins = max(5, (_config.get("uptodateKeepaliveIntervalMinutes") or 20))
    activity_window_s = interval_mins * 60 * 2
    if _last_user_activity == 0.0:
        return  # user has not interacted since Anki opened
    if time.monotonic() - _last_user_activity > activity_window_s:
        return  # idle too long
    _keepalive_page.load(QUrl(_home_url()))


def _on_keepalive_crash(*_):
    """Recreate the keepalive page when its renderer process dies.
    Without this the background session refresh stops silently, and the
    session eventually expires without any user-visible warning."""
    global _keepalive_page
    if _browser is None:
        return
    print("[TheAnkiDote] keepalive renderer crashed - recreating")
    try:
        if _keepalive_page is not None:
            _keepalive_page.deleteLater()
    except Exception:
        pass
    _keepalive_page = _make_keepalive_page()


def _on_keepalive_url_changed(url: QUrl):
    """Called when the background keepalive page navigates.
    If it lands on the SSO login URL the session has expired - surface the
    dock and redirect the visible browser to the login entry point."""
    url_str = url.toString()
    if not _is_sso_url(url_str):
        return

    # Show the dock so the user sees the login page
    if _dock is not None and not _dock.isVisible():
        _show_dock()

    # Only redirect the visible browser if it's currently on a UTD/HCN page
    # (don't hijack if the user has navigated elsewhere)
    if _browser is not None:
        current = _browser.view.url().toString()
        if any(d in current for d in ("uptodate.com", "hcn.com.au")):
            _browser.view.load(QUrl(_home_url()))


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

_QUESTION_PREFIX_RE = re.compile(
    r"^(what\s+(?:is|are|was|were)|define|describe|explain"
    r"|how\s+(?:does|do|is|are)|why|when|which)\s+",
    re.IGNORECASE,
)


def _utd_search_base() -> str:
    """Return the bare UpToDate search path to append ?search= to.

    For NSW Health (HCN proxy) and direct UTD URLs the home_url IS the
    search endpoint, so we use it (stripping any pre-existing query string).
    For redirect-style home URLs (OpenAthens, Shibboleth, etc.) cookies are
    already set on www.uptodate.com after first login, so we search there
    directly - the session follows the cookies, not the original redirect URL.
    """
    home = _home_url()
    host = QUrl(home).host()
    if "uptodate.com" in host or "hcn.com.au" in host:
        return home.split("?")[0]   # strip any trailing query string
    return "https://www.uptodate.com/contents/search"


def _do_search(term: str):
    """Load a UpToDate search for *term*, showing the dock if it is hidden."""
    term = term.strip()
    if not term or _browser is None:
        return
    url = "{}?search={}".format(_utd_search_base(), _url_quote(term[:200]))
    _browser.view.load(QUrl(url))
    if _dock is not None and not _dock.isVisible():
        _show_dock()


def _auto_search_card(card) -> None:
    """When the dock is open and a new card question is shown, automatically
    search UpToDate for the card's front-field text."""
    _mark_user_active()
    if not _config.get("uptodateAutoSearchCard") is not False:
        return
    if _browser is None or _dock is None or not _dock.isVisible():
        return
    try:
        front = _strip_html(card.note().fields[0])
        front = _QUESTION_PREFIX_RE.sub("", front).strip()[:150]
        if front:
            _do_search(front)
    except Exception:
        pass


def _search_selection() -> None:
    """Search the text currently selected in the reviewer or main webview."""
    _mark_user_active()
    def _handle(text: str):
        if text and text.strip():
            _do_search(text.strip())

    # Prefer the reviewer webview (most likely location of selected medical text)
    try:
        if mw.state == "review" and mw.reviewer and mw.reviewer.web:
            mw.reviewer.web.page().runJavaScript(
                "window.getSelection().toString()", _handle)
            return
    except Exception:
        pass
    # Fall back to main webview
    try:
        mw.web.page().runJavaScript("window.getSelection().toString()", _handle)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Toolbar link
# Registered at MODULE LEVEL so it fires during the initial toolbar draw
# (which happens before main_window_did_init).
# ---------------------------------------------------------------------------

def _toolbar_label() -> str:
    """Return the toolbar button HTML.  Uses the logo at
    `theankidote/web/logo.png` (shared web-assets dir).  The web/
    directory is exported by the top-level `__init__.py` already, so
    Anki's media server serves it at `/_addons/theankidote/web/...`."""
    # __file__ is theankidote/uptodate/__init__.py - parent of dirname
    # is the top-level addon dir.
    addon_dir = os.path.dirname(os.path.dirname(__file__))
    logo = os.path.join(addon_dir, "web", "logo.png")
    if os.path.exists(logo):
        # Top-level package name (e.g. "theankidote"), not the
        # subpackage (e.g. "theankidote.uptodate").
        pkg = __name__.split(".")[0]
        return (
            f'<img src="/_addons/{pkg}/web/logo.png" '
            f'alt="UpToDate" '
            f'style="height:1em;vertical-align:-0.18em;display:inline-block;">'
        )
    return "UTD"


def _add_toolbar_link(links: list, toolbar: Toolbar) -> None:
    toolbar.link_handlers[TOGGLE_CMD] = lambda: toggle_dock()
    shortcut = _config.get("shortcutToggleUptodate") or "Ctrl+Shift+U"
    tooltip = f"Toggle UpToDate sidebar ({shortcut})"
    link = (
        f'<a class=hitem tabindex="-1" aria-label="The AnkiDote - UpToDate" '
        f'title="{tooltip}" '
        f'id="theankidote-utd-toolbar-link" '
        f'href=# onclick="return pycmd(\'{TOGGLE_CMD}\')">'
        f'{_toolbar_label()}</a>'
    )
    # Position relative to chat's link if already inserted (defensive  - 
    # UTD's hook normally fires first so chat won't be present yet, but
    # if hook order ever changes this still does the right thing).
    order = _config.get("toolbarOrder") or ["chat", "uptodate"]
    utd_first = (
        "uptodate" in order and "chat" in order
        and order.index("uptodate") < order.index("chat")
    )
    chat_idx = next(
        (i for i, l in enumerate(links)
         if "theankidote-chat-toolbar-link" in l),
        None,
    )
    if chat_idx is not None:
        links.insert(chat_idx if utd_first else chat_idx + 1, link)
    elif len(links) >= TOOLBAR_LINK_BASE:
        links.insert(TOOLBAR_LINK_BASE, link)
    else:
        links.append(link)


def _on_js_message(handled, message, context):
    if message == TOGGLE_CMD:
        toggle_dock()
        return (True, None)
    return handled


# Register hooks once at module load.
# A flag guards against double-registration if Anki ever hot-reloads the module.
if not globals().get("_hooks_registered"):
    gui_hooks.top_toolbar_did_init_links.append(_add_toolbar_link)
    gui_hooks.webview_did_receive_js_message.append(_on_js_message)
    gui_hooks.reviewer_did_show_question.append(_auto_search_card)
    _hooks_registered = True


# ---------------------------------------------------------------------------
# Public API
#
# Called from the top-level theankidote/__init__.py pycmd handler when an
# UpToDate URL is clicked from a popup chip - so the click lands in the
# authenticated UTD session rather than the StatPearls profile.
# Returns True on successful dock load, False if not yet initialised.
# ---------------------------------------------------------------------------

def open_url_in_dock(url: str) -> bool:
    """Load `url` in the UpToDate dock and show it.  Returns False if the
    dock has not yet been initialised (e.g. profile still loading)."""
    _mark_user_active()
    if _browser is None or _dock is None:
        return False
    try:
        _browser.view.load(QUrl(url))
        if not _dock.isVisible():
            _show_dock()
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Setup - runs after the main window is ready
# ---------------------------------------------------------------------------

def _setup():
    global _dock, _browser, _lifecycle_hooks_registered

    # Guard against double-initialisation (e.g. multiple main_window_did_init
    # fires, or add-on hot-reload).  _close_dock sets _dock back to None so
    # post-profile-switch re-entry is allowed.
    if _dock is not None:
        return

    _browser = UpToDateBrowser()
    _dock = QDockWidget()
    _dock.setObjectName("TheAnkiDote_dock_uptodate")
    _dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
    _dock.setTitleBarWidget(QWidget())
    _dock.setWidget(_browser)
    mw.addDockWidget(_dock_area(), _dock)
    _dock.hide()

    # Toggle shortcut - QShortcut bound to mw so the binding works
    # without cluttering the Tools menu.  Functionality is identical
    # to a QAction; only the menu entry is removed.
    try:
        from PyQt6.QtGui import QShortcut
    except (ImportError, AttributeError):
        from PyQt5.QtWidgets import QShortcut
    toggle_seq = _config.get("shortcutToggleUptodate") or "Ctrl+Shift+U"
    _toggle_sc = QShortcut(QKeySequence(toggle_seq), mw)
    _toggle_sc.activated.connect(toggle_dock)

    # Selected-text search shortcut - same QShortcut treatment.
    search_seq = _config.get("shortcutSearchSelection") or "Ctrl+Shift+L"
    _search_sc = QShortcut(QKeySequence(search_seq), mw)
    _search_sc.activated.connect(_search_selection)

    # Background session keepalive
    _start_keepalive()

    # Register lifecycle hooks exactly once across all profile switches.
    # addons_dialog_will_show and profile_will_close accumulate on each
    # _setup() call otherwise (one per profile open → duplicates after
    # the user switches profiles).
    if not _lifecycle_hooks_registered:
        # Hide (not destroy) the dock when the add-ons dialog opens.
        # Using _close_dock here permanently destroyed the dock for the rest of
        # the session because _setup() never re-runs after main_window_did_init.
        gui_hooks.addons_dialog_will_show.append(_hide_dock)
        # Full teardown only on profile close - _setup() will re-run for the
        # new profile via main_window_did_init.
        try:
            gui_hooks.profile_will_close.append(_close_dock)
        except AttributeError:
            pass
        _lifecycle_hooks_registered = True

    mw.toolbar.redraw()


# NOTE: top-level theankidote/__init__.py invokes `_setup()` directly
# from its own main_window_did_init handler so that subpackage
# initialisation is gated on `enableUpToDate` config and ordered
# alongside the pearls subpackage.  Self-registering here would cause
# the dock to appear even in UpToDateless mode.
