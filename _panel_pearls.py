# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.

"""Side panel: AMBOSS-style UI - nav header + article webview."""

try:
    from PyQt6.QtCore import Qt, QUrl, QSize, pyqtSignal
    from PyQt6.QtWidgets import (
        QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
        QPushButton, QVBoxLayout, QWidget,
    )
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import (
        QWebEnginePage, QWebEngineProfile, QWebEngineSettings,
    )
    _USER_ROLE  = Qt.ItemDataRole.UserRole
    _NO_HSCROLL = Qt.ScrollBarPolicy.ScrollBarAlwaysOff
except (ImportError, AttributeError):
    from PyQt5.QtCore import Qt, QUrl, QSize, pyqtSignal
    from PyQt5.QtWidgets import (
        QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
        QPushButton, QVBoxLayout, QWidget,
    )
    from PyQt5.QtWebEngineWidgets import (
        QWebEngineView, QWebEnginePage, QWebEngineProfile, QWebEngineSettings,
    )
    _USER_ROLE  = Qt.UserRole
    _NO_HSCROLL = Qt.ScrollBarAlwaysOff

from . import _webengine, _log

# New profile name (was "ankipearls" in the old standalone addon) so
# cookies and cache don't leak between versions.
_PROFILE_NAME = "theankidote-pearls"
_AP_HOME      = "https://www.ncbi.nlm.nih.gov/books/NBK430685/"

# JavaScript injected into every DrugBank page after load.
#
# Hides the "create a free account" upsell banner using known selectors
# only.  Earlier versions did a `querySelectorAll('*')` text-content
# sweep on every load AND on every MutationObserver fire - measurable
# CPU spike on long DrugBank monograph pages.  The selector-only
# approach is sufficient in practice and stays within DrugBank's
# free-access ToS for personal study (we only hide CSS-visible
# elements; we don't bypass paywalls or scrape any non-displayed
# content).
#
# The MutationObserver watches body subtree but throttles to one
# hideBanners() call per 250 ms so a busy SPA route change doesn't
# thrash the page.
# Focuses the "Search this book" input on NCBI Bookshelf pages so the
# user can start typing immediately when the side panel is opened via
# the toolbar button.  No-op on any page that doesn't expose that
# button (DrugBank monographs, individual chapter pages, etc.).
#
# Strategy: find a button or submit-input whose visible text/value is
# exactly "Search this book", then focus the closest text input in the
# same form (preferred) or the nearest preceding text-input sibling.
_FOCUS_SEARCH_JS = r"""
(function() {
    function findInput() {
        var nodes = document.querySelectorAll(
            'button, input[type="submit"], input[type="button"]'
        );
        for (var i = 0; i < nodes.length; i++) {
            var b = nodes[i];
            var label = (b.value || b.textContent || '').trim().toLowerCase();
            if (label !== 'search this book') continue;
            var form = b.form || (b.closest && b.closest('form'));
            if (form) {
                var input = form.querySelector(
                    'input[type="text"], input[type="search"], input:not([type])'
                );
                if (input) return input;
            }
            var sib = b.previousElementSibling;
            while (sib) {
                if (sib.tagName === 'INPUT' &&
                    (sib.type === 'text' || sib.type === 'search' || !sib.type)) {
                    return sib;
                }
                sib = sib.previousElementSibling;
            }
            return null;
        }
        return null;
    }
    try {
        var inp = findInput();
        if (inp) {
            inp.focus();
            try { inp.select(); } catch(e) {}
        }
    } catch(e) {}
})();
"""

_DRUGBANK_BANNER_JS = r"""
(function() {
    var SELECTORS = [
        '.db-banner', '.signup-banner', '.registration-banner',
        '.upsell-banner', '.account-banner', '.free-account-banner',
        '[id*="signup-banner"]', '[id*="register-banner"]',
        '[id*="upsell-banner"]', '[id*="account-banner"]'
    ];
    function hideBanners() {
        try {
            SELECTORS.forEach(function(sel) {
                document.querySelectorAll(sel).forEach(function(el) {
                    el.style.setProperty('display', 'none', 'important');
                });
            });
        } catch(e) {}
    }

    hideBanners();

    var pending = false;
    var observer = new MutationObserver(function(mutations) {
        if (pending) return;
        var relevant = mutations.some(function(m) {
            return m.addedNodes.length > 0;
        });
        if (!relevant) return;
        pending = true;
        setTimeout(function() {
            pending = false;
            hideBanners();
        }, 250);
    });
    try {
        observer.observe(document.body || document.documentElement, {
            childList: true, subtree: true
        });
    } catch(e) {}
})();
"""


def _night_mode() -> bool:
    try:
        from aqt.theme import theme_manager
        return bool(theme_manager.night_mode)
    except Exception:
        return True


_DARK = _night_mode()

# ── Colour palette - dark (AMBOSS-inspired) or light (Anki light theme) ───
if _DARK:
    _NAVY        = "#0d2137"
    _NAVY_LIGHT  = "#1a3a5c"
    _TEAL        = "#0fcad4"
    _TEAL_DIM    = "rgba(15,202,212,.12)"
    _TEAL_BORDER = "rgba(15,202,212,.35)"
    _HEADER_TXT  = "#e8f4f8"
    _MUTED       = "rgba(232,244,248,.55)"
else:
    _NAVY        = "#e8f2f8"
    _NAVY_LIGHT  = "#cfe0ec"
    _TEAL        = "#0a9ba3"
    _TEAL_DIM    = "rgba(10,155,163,.1)"
    _TEAL_BORDER = "rgba(10,155,163,.3)"
    _HEADER_TXT  = "#1a2c3e"
    _MUTED       = "rgba(26,44,62,.5)"

_RESULT_BG   = "#f0f8fb"
_RESULT_BDR  = "#c5e3ed"
_ITEM_TXT    = "#1a3a5c"   # always dark - results list always has a light bg


# ──────────────────────────────────────────────────────────────────────────
# Compact flat nav button - stylesheet built once and reused.
# ──────────────────────────────────────────────────────────────────────────

_NAV_BTN_QSS = (
    "QPushButton{"
        f"background:transparent;color:{_HEADER_TXT};border:none;"
        "border-radius:4px;font-size:14px;font-weight:bold;}"
    "QPushButton:hover{"
        f"background:{_TEAL_DIM};color:{_TEAL};}}"
    "QPushButton:disabled{"
        f"color:{_MUTED};}}"
)

_HOME_BTN_QSS = (
    "QPushButton{"
        f"background:transparent;color:{_TEAL};"
        "border:none;border-radius:4px;font-size:17px;font-weight:bold;}"
    "QPushButton:hover{"
        f"background:{_TEAL_DIM};color:{_TEAL};}}"
)

_CLOSE_BTN_QSS = (
    "QPushButton{"
        f"background:transparent;color:{_HEADER_TXT};"
        "border:none;border-radius:4px;font-size:13px;font-weight:900;}"
    "QPushButton:hover{"
        "background:rgba(220,50,50,.18);color:#ff7070;}"
    "QPushButton:pressed{"
        "background:rgba(220,50,50,.32);}"
)


def _nav_btn(parent: QWidget, text: str, tip: str, w: int = 26) -> QPushButton:
    b = QPushButton(text, parent)
    b.setFixedSize(w, 28)
    b.setToolTip(tip)
    b.setStyleSheet(_NAV_BTN_QSS)
    return b


# ──────────────────────────────────────────────────────────────────────────
# Results section
# ──────────────────────────────────────────────────────────────────────────

class _ResultsSection(QWidget):
    article_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._results: list = []

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self._hdr = QLabel("RELEVANT ARTICLES")
        self._hdr.setStyleSheet(f"""
            QLabel {{
                background: {_NAVY_LIGHT};
                color: {_TEAL};
                font-size: 9px;
                font-weight: bold;
                letter-spacing: .08em;
                padding: 5px 10px;
                border-top: 1px solid {_TEAL_BORDER};
                border-bottom: 1px solid {_TEAL_BORDER};
            }}
        """)
        lay.addWidget(self._hdr)

        self._list = QListWidget()
        self._list.setHorizontalScrollBarPolicy(_NO_HSCROLL)
        self._list.setStyleSheet(f"""
            QListWidget {{
                background: {_RESULT_BG};
                border: none;
                outline: none;
                font-size: 12px;
            }}
            QListWidget::item {{
                padding: 7px 12px;
                color: {_ITEM_TXT};
                border-bottom: 1px solid {_RESULT_BDR};
            }}
            QListWidget::item:hover {{
                background: #daeef5;
                color: #0d2137;
            }}
            QListWidget::item:selected {{
                background: #b8dce8;
                color: #0d2137;
            }}
        """)
        self._list.setMaximumHeight(185)
        # itemClicked covers mouse; itemActivated also catches keyboard
        # Enter / double-click, so the list is fully keyboard-navigable
        # (↑/↓ to move, Enter to load) once focused.
        self._list.itemClicked.connect(self._on_click)
        self._list.itemActivated.connect(self._on_click)
        lay.addWidget(self._list)

        self.hide()

    def show_results(self, results: list):
        self._results = results
        self._list.clear()
        if not results:
            self.hide()
            return
        n = len(results)
        self._hdr.setText(f"RELEVANT ARTICLES  ({n})")
        for r in results:
            item = QListWidgetItem("  " + r["title"])
            item.setData(_USER_ROLE, r["url"])
            item.setToolTip(r["url"])
            self._list.addItem(item)
        row_h  = self._list.sizeHintForRow(0) if self._list.count() > 0 else 26
        height = min(n * row_h + 4, 185)
        self._list.setFixedHeight(height)
        self.show()

    def _on_click(self, item: QListWidgetItem):
        url = item.data(_USER_ROLE)
        if url:
            self.article_selected.emit(url)


# ──────────────────────────────────────────────────────────────────────────
# Main panel
# ──────────────────────────────────────────────────────────────────────────

class StatPearlsPanel(QWidget):
    """AMBOSS-inspired side panel: nav header + results + webview."""

    closed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._last_results: list = []
        self._auto_loaded  = False
        self._show_articles = False  # only true when opened via toolbar button

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── nav header ────────────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(40)
        header.setStyleSheet(f"background: {_NAVY};")
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(8, 0, 8, 0)
        h_lay.setSpacing(2)

        self._btn_back     = _nav_btn(header, "‹", "Back")
        self._btn_forward  = _nav_btn(header, "›", "Forward")
        self._btn_reload   = _nav_btn(header, "↺", "Reload")
        self._btn_home     = _nav_btn(header, "⌂", "StatPearls home", 28)
        self._btn_external = _nav_btn(header, "↗",
            "Open current page in system browser", 28)
        self._btn_back.setEnabled(False)
        self._btn_forward.setEnabled(False)
        self._btn_home.setStyleSheet(_HOME_BTN_QSS)

        self._btn_close = _nav_btn(header, "✕", "Close sidebar")
        self._btn_close.setStyleSheet(_CLOSE_BTN_QSS)

        h_lay.addWidget(self._btn_back)
        h_lay.addWidget(self._btn_forward)
        h_lay.addWidget(self._btn_reload)
        h_lay.addWidget(self._btn_home)
        h_lay.addStretch(1)
        h_lay.addWidget(self._btn_external)
        h_lay.addWidget(self._btn_close)
        outer.addWidget(header)

        # ── webview ───────────────────────────────────────────────────────
        self._profile = QWebEngineProfile(_PROFILE_NAME, self)
        # Cloudflare bypass (Chrome UA, sec-ch-ua headers, stealth JS, etc.).
        # DrugBank pages sit behind Cloudflare's bot challenge; without this
        # the verification page gets stuck and never redirects to the article.
        _webengine.apply_to_profile(self._profile)
        self._page = QWebEnginePage(self._profile, self)
        self._view = QWebEngineView(self)
        self._view.setPage(self._page)

        # Renderer crash recovery - same pattern as the UTD dock.
        try:
            self._page.renderProcessTerminated.connect(self._on_render_crash)
        except Exception as exc:
            _log.error("pearls renderProcessTerminated connect", exc)

        # ── results section ───────────────────────────────────────────────
        self._results = _ResultsSection(self)
        self._results.article_selected.connect(self.load_url)

        outer.addWidget(self._results)
        outer.addWidget(self._view, 1)

        # NCBI bookshelf article pages need ~520 px of usable content width to
        # render without a horizontal scrollbar.  Set this as the minimum AND
        # advertise it through sizeHint so the dock opens at this width.
        self.setMinimumWidth(520)

        # ── wire nav ──────────────────────────────────────────────────────
        self._btn_back.clicked.connect(self._view.back)
        self._btn_forward.clicked.connect(self._view.forward)
        self._btn_reload.clicked.connect(self._view.reload)
        self._btn_home.clicked.connect(self._go_home)
        self._btn_external.clicked.connect(self._open_externally)
        self._view.urlChanged.connect(self._on_url_changed)
        self._view.loadFinished.connect(self._on_load_finished)

        self._view.load(QUrl(_AP_HOME))

    def sizeHint(self):  # type: ignore[override]
        # Default dock width chosen so NCBI book pages fit without horizontal
        # scrolling.  Anki uses sizeHint when first docking the widget.
        return QSize(560, 600)

    # ── public API ────────────────────────────────────────────────────────

    def show_article_list(self) -> None:
        """Called when user opens the panel via the toolbar button (same card).
        Shows the article-list; leaves the webview on whatever page is loaded."""
        self._show_articles = True
        if self._last_results:
            self._results.show_results(self._last_results)
        # Page is already loaded (no loadFinished event coming); fire the
        # focus JS synchronously.  No-op if the current page isn't a NCBI
        # bookshelf landing with a "Search this book" button.
        try:
            self._page.runJavaScript(_FOCUS_SEARCH_JS)
        except Exception:
            pass

    def apply_local_results(self, results: list) -> None:
        """Sidebar's article list is fed by instant local-database matches
        (StatPearls + DrugBank entries detected on the current card).  No
        network search is performed - the popups already cover term lookup,
        and the webview loads articles directly when a popup is clicked."""
        self._last_results = results
        if self._show_articles:
            if results:
                self._results.show_results(results)
            else:
                self._results.hide()

    def reset_for_new_card(self) -> None:
        """Called when toolbar button is pressed on a different card.
        Navigates the webview to the StatPearls homepage and shows the list."""
        self._show_articles = True
        self._auto_loaded = False
        self._view.load(QUrl(_AP_HOME))
        if self._last_results:
            self._results.show_results(self._last_results)

    def hide_article_list(self) -> None:
        """Called when user opens the panel via popup click - list stays out
        of the way so the article body fills the pane."""
        self._show_articles = False
        self._results.hide()

    def load_url(self, url: str) -> None:
        self._auto_loaded = True
        self._view.load(QUrl(url))

    def get_last_results(self) -> list:
        return self._last_results

    # ── private ───────────────────────────────────────────────────────────

    def _go_home(self):
        self._auto_loaded = False
        self._view.load(QUrl(_AP_HOME))

    def _open_externally(self):
        try:
            from aqt.utils import openLink
            url = self._view.url().toString()
            if url and url.startswith(("http://", "https://")):
                openLink(url)
        except Exception as exc:
            _log.error("pearls open externally", exc)

    def _on_render_crash(self, status, exit_code):
        _log.warn(f"pearls renderer terminated (status={status}, exit={exit_code})")
        try:
            self._crash_url = self._view.url().toString()
        except Exception:
            self._crash_url = None
        try:
            from PyQt6.QtCore import QTimer
        except (ImportError, AttributeError):
            from PyQt5.QtCore import QTimer
        QTimer.singleShot(1500, self._recover_after_crash)

    def _recover_after_crash(self):
        url = getattr(self, "_crash_url", None)
        blank = {"about:blank", "", "chrome-error://chromewebdata/"}
        target = url if url and url not in blank else _AP_HOME
        try:
            self._view.load(QUrl(target))
        except Exception as exc:
            _log.error("pearls post-crash reload", exc)

    def _on_url_changed(self, url: QUrl):
        try:
            history = self._page.history()
            self._btn_back.setEnabled(history.canGoBack())
            self._btn_forward.setEnabled(history.canGoForward())
        except Exception:
            pass

    def _on_load_finished(self, _ok: bool):
        try:
            history = self._page.history()
            self._btn_back.setEnabled(history.canGoBack())
            self._btn_forward.setEnabled(history.canGoForward())
        except Exception:
            pass
        try:
            host = self._view.url().host()
            if "drugbank.com" in host:
                self._page.runJavaScript(_DRUGBANK_BANNER_JS)
            if "ncbi.nlm.nih.gov" in host:
                # Auto-focus the "Search this book" input on the StatPearls
                # home page so the user can start typing immediately.  No-op
                # on chapter / non-book pages where the button isn't present.
                self._page.runJavaScript(_FOCUS_SEARCH_JS)
        except Exception:
            pass

