# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.

"""Side panel: AMBOSS-style UI - nav header + article webview."""

try:
    from PyQt6.QtCore import Qt, QUrl, QSize, pyqtSignal
    from PyQt6.QtWidgets import (
        QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
        QMenu, QPushButton, QToolButton, QVBoxLayout, QWidget,
    )
    from PyQt6.QtGui import QAction
    _TB_POPUP = QToolButton.ToolButtonPopupMode.MenuButtonPopup
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import (
        QWebEnginePage, QWebEngineProfile, QWebEngineSettings,
    )
    _USER_ROLE  = Qt.ItemDataRole.UserRole
    _NO_HSCROLL = Qt.ScrollBarPolicy.ScrollBarAlwaysOff
except (ImportError, AttributeError):
    from PyQt5.QtCore import Qt, QUrl, QSize, pyqtSignal
    from PyQt5.QtWidgets import (
        QAction, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
        QMenu, QPushButton, QToolButton, QVBoxLayout, QWidget,
    )
    _TB_POPUP = QToolButton.MenuButtonPopup
    from PyQt5.QtWebEngineWidgets import (
        QWebEngineView, QWebEnginePage, QWebEngineProfile, QWebEngineSettings,
    )
    _USER_ROLE  = Qt.UserRole
    _NO_HSCROLL = Qt.ScrollBarAlwaysOff

import json
import re

from . import _webengine, _log, _config

try:
    from PyQt6.QtCore import QTimer
except (ImportError, AttributeError):
    from PyQt5.QtCore import QTimer

# New profile name (was "ankipearls" in the old standalone addon) so
# cookies and cache don't leak between versions.
_PROFILE_NAME  = "theankidote-pearls"
_AP_HOME       = "https://www.ncbi.nlm.nih.gov/books/NBK430685/"
_DRUGBANK_HOME = "https://go.drugbank.com/"

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


_HIDE_BOOKSHELF_BAR_JS = r"""
(function() {
    function hideTopBar() {
        try {
            // Common NCBI Bookshelf top-search selectors.
            var candidates = [
                '.bookshelf_search',
                '#shared-page > .nav-bar',
                '.search-bar',
                '#search-bar',
                '#bsf_search',
                'form[name="ePathobj_search"]',
                'form[name="EntrezForm"]',
                '.bk_search',
                '.bk-srch',
                '#nlm-ncbi',
                '#universal_header_search',
                '.universal_header_search'
            ];
            candidates.forEach(function(sel) {
                document.querySelectorAll(sel).forEach(function(el) {
                    el.style.setProperty('display', 'none', 'important');
                });
            });
            // Fallback: look for a leading container whose text starts with
            // "Bookshelf" and contains a select element for "Books".
            var labels = document.querySelectorAll('label, span, div');
            for (var i = 0; i < labels.length && i < 400; i++) {
                var el = labels[i];
                var txt = (el.textContent || '').trim();
                if (txt === 'Bookshelf' || /^Bookshelf\b/.test(txt)) {
                    // Walk up to the smallest container that includes a select
                    // (Books dropdown) AND a text input.
                    var p = el;
                    for (var depth = 0; depth < 6 && p; depth++) {
                        if (p.querySelector && p.querySelector('select') &&
                            p.querySelector('input[type="text"], input[type="search"]')) {
                            p.style.setProperty('display', 'none', 'important');
                            break;
                        }
                        p = p.parentElement;
                    }
                }
            }
        } catch (e) {}
    }
    hideTopBar();
    var pending = false;
    var observer = new MutationObserver(function() {
        if (pending) return;
        pending = true;
        setTimeout(function() {
            pending = false;
            hideTopBar();
        }, 300);
    });
    try {
        observer.observe(document.body || document.documentElement, {
            childList: true, subtree: true
        });
    } catch (e) {}
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

def _rebind_theme() -> None:
    """Re-read the palette after Anki switches light/dark mid-session.

    The module captures `_theme.*` into local constants at import for
    cheap f-string interpolation, and the QSS strings below bake those
    values in.  Both have to be rebuilt, and every live widget restyled
    (see `PearlsPanel.apply_theme`), or the panel keeps the palette it
    was born with.
    """
    g = globals()
    g["_NAVY"] = _theme.NAVY
    g["_NAVY_LIGHT"] = _theme.NAVY_LIGHT
    g["_TEAL"] = _theme.TEAL
    g["_TEAL_DIM"] = _theme.TEAL_DIM
    g["_TEAL_BORDER"] = _theme.TEAL_BORDER
    g["_HEADER_TXT"] = _theme.HEADER_TXT
    g["_BODY_TXT"] = _theme.BODY_TXT
    g["_MUTED"] = _theme.MUTED
    g["_BG_BOX"] = _theme.BG_BOX
    _rebuild_qss()


def _rebuild_qss() -> None:
    """(Re)build the button stylesheets from the current palette."""
    g = globals()
    g["_NAV_BTN_QSS"] = (
        "QPushButton{"
            f"background:transparent;color:{_HEADER_TXT};border:none;"
            "border-radius:4px;font-size:14px;font-weight:bold;}"
        "QPushButton:hover{"
            f"background:{_TEAL_DIM};color:{_TEAL};}}"
        "QPushButton:disabled{"
            f"color:{_MUTED};}}"
    )
    g["_HOME_BTN_QSS"] = (
        "QToolButton{"
            f"background:transparent;color:{_TEAL};"
            "border:none;border-radius:4px;font-size:17px;font-weight:bold;"
            "padding-right:14px;}"
        "QToolButton:hover{"
            f"background:{_TEAL_DIM};color:{_TEAL};}}"
        "QToolButton::menu-button{"
            "background:transparent;border:none;width:12px;}"
        "QToolButton::menu-arrow{"
            f"image:none;}}"
    )
    g["_CLOSE_BTN_QSS"] = (
        "QPushButton{"
            f"background:transparent;color:{_HEADER_TXT};"
            "border:none;border-radius:4px;font-size:13px;font-weight:900;}"
        "QPushButton:hover{"
            "background:rgba(220,50,50,.18);color:#ff7070;}"
        "QPushButton:pressed{"
            "background:rgba(220,50,50,.32);}"
    )


_rebuild_qss()


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
        self._style_header()
        lay.addWidget(self._hdr)

        self._list = QListWidget()
        self._list.setHorizontalScrollBarPolicy(_NO_HSCROLL)
        self._style_list()

        self._list.setMaximumHeight(185)
        # itemClicked covers mouse; itemActivated also catches keyboard
        # Enter / double-click, so the list is fully keyboard-navigable
        # (↑/↓ to move, Enter to load) once focused.
        self._list.itemClicked.connect(self._on_click)
        self._list.itemActivated.connect(self._on_click)
        lay.addWidget(self._list)

        self.hide()

    def apply_theme(self) -> None:
        """Re-apply every stylesheet this widget owns after a palette
        rebuild.  Row widgets carry inline colours, so they are rebuilt
        from the retained result list rather than restyled in place."""
        try:
            self._style_header()
            self._style_list()
            if getattr(self, "_results", None):
                self.set_results(list(self._results))
        except Exception as exc:
            _log.error("results apply_theme", exc)

    def _style_list(self) -> None:
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

    def _style_header(self) -> None:
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
        self._header = header
        header.setStyleSheet(f"background: {_NAVY};")
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(8, 0, 8, 0)
        h_lay.setSpacing(2)

        self._btn_back     = _nav_btn(header, "‹", "Back")
        self._btn_forward  = _nav_btn(header, "›", "Forward")
        self._btn_reload   = _nav_btn(header, "↺", "Reload")
        self._btn_home     = QToolButton(header)
        self._btn_home.setText("⌂")
        self._btn_home.setFixedSize(40, 28)
        self._btn_home.setPopupMode(_TB_POPUP)
        self._btn_home.setStyleSheet(_HOME_BTN_QSS)
        self._home_menu = QMenu(self._btn_home)
        self._act_home_statpearls = QAction("StatPearls home", self._btn_home)
        self._act_home_drugbank   = QAction("DrugBank home",   self._btn_home)
        self._act_home_statpearls.setCheckable(True)
        self._act_home_drugbank.setCheckable(True)
        self._act_home_statpearls.triggered.connect(
            lambda: self._set_home_choice("statpearls"))
        self._act_home_drugbank.triggered.connect(
            lambda: self._set_home_choice("drugbank"))
        self._home_menu.addAction(self._act_home_statpearls)
        self._home_menu.addAction(self._act_home_drugbank)
        self._btn_home.setMenu(self._home_menu)
        self._refresh_home_ui()
        self._btn_external = _nav_btn(header, "↗",
            "Open current page in system browser", 28)
        self._btn_back.setEnabled(False)
        self._btn_forward.setEnabled(False)

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

        self._view.load(QUrl(self._current_home_url()))

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
            self._page.runJavaScript(_HIDE_BOOKSHELF_BAR_JS)
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
        self._view.load(QUrl(self._current_home_url()))
        if self._last_results:
            self._results.show_results(self._last_results)

    def hide_article_list(self) -> None:
        """Called when user opens the panel via popup click - list stays out
        of the way so the article body fills the pane."""
        self._show_articles = False
        self._results.hide()

    def load_url(self, url: str, term: str = "", section: str = "") -> None:
        """Navigate the panel webview.

        Two failure modes made this blank out in practice, both fixed here:

        1. A load already in flight (the home page fired from __init__, or a
           previous article) is cancelled by the new one.  The cancelled
           navigation emits loadFinished(ok=False) and QtWebEngine parks the
           view on chrome-error://chromewebdata/, which paints as an empty
           grey rectangle.  Stopping first makes the handover explicit.
        2. Loading into a dock that is still hidden gives the renderer a 0x0
           viewport; the page can finish loading with nothing composited and
           stay blank after the dock appears.  Deferring by one event-loop
           tick lets the show + layout land first.
        """
        self._auto_loaded = True
        self._pending_url = url
        self._pending_section = section
        self._load_retries = 0
        # A term we have resolved before goes straight to the article or
        # drug page; nothing else in this method needs to know how the
        # URL was obtained.
        if term:
            self._pending_term = term
            try:
                from .pearls import _ncbi
                hit = _ncbi.cached_url(term)
                if not hit:
                    acc = _ncbi.cached(term)
                    hit = _ncbi.article_url(acc) if acc else None
                if hit:
                    url = hit
                    self._pending_url = hit
            except Exception as exc:
                _log.debug(f"cache lookup failed for {term!r}: {exc}")
        try:
            self._view.stop()
        except Exception:
            pass
        QTimer.singleShot(0, lambda: self._do_load(url))

    def _do_load(self, url: str) -> None:
        try:
            self._view.load(QUrl(url))
        except Exception as exc:
            _log.error(f"pearls load {url[:60]!r}", exc)

    def get_last_results(self) -> list:
        return self._last_results

    # ── private ───────────────────────────────────────────────────────────

    def _current_home_choice(self) -> str:
        try:
            v = _config.get("pearlsHomePage")
        except Exception:
            v = None
        return "drugbank" if v == "drugbank" else "statpearls"

    def _current_home_url(self) -> str:
        return _DRUGBANK_HOME if self._current_home_choice() == "drugbank" else _AP_HOME

    def _current_home_label(self) -> str:
        return "DrugBank" if self._current_home_choice() == "drugbank" else "StatPearls"

    def _refresh_home_ui(self) -> None:
        choice = self._current_home_choice()
        self._act_home_statpearls.setChecked(choice == "statpearls")
        self._act_home_drugbank.setChecked(choice == "drugbank")
        self._btn_home.setToolTip(f"Home ({self._current_home_label()})")

    def _set_home_choice(self, choice: str) -> None:
        try:
            _config.set_value("pearlsHomePage", choice)
        except Exception as exc:
            _log.error("pearls set home choice", exc)
        self._refresh_home_ui()
        self._go_home()

    def _go_home(self):
        self._auto_loaded = False
        self._view.load(QUrl(self._current_home_url()))

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
        QTimer.singleShot(1500, self._recover_after_crash)

    def _recover_after_crash(self):
        url = getattr(self, "_crash_url", None)
        blank = {"about:blank", "", "chrome-error://chromewebdata/"}
        target = url if url and url not in blank else self._current_home_url()
        try:
            self._view.load(QUrl(target))
        except Exception as exc:
            _log.error("pearls post-crash reload", exc)

    # ── search-page auto-resolve ─────────────────────────────────────
    # 47% of drugs and 100% of conditions have no direct article/drug ID,
    # so "Open article" lands on a search results page and the reader has
    # to click again.  Rather than shipping thousands of hand-collected
    # IDs that rot, let each site resolve its own term: when a search
    # page finishes loading, look for a single unambiguous exact match
    # and follow it.  The resulting canonical URL is cached by
    # `_on_url_changed`, so it only ever happens once per term.
    _AUTOJUMP_JS = r"""
    (function () {
      try {
        var q = %s;
        if (!q) return;
        var norm = function (t) {
          return String(t || "").toLowerCase()
            .replace(/\s+/g, " ").replace(/[^a-z0-9 +/-]/g, "").trim();
        };
        var want = norm(q);
        var links = document.querySelectorAll(
          'a[href*="/drugs/DB"], a[href*="/books/NBK"]');
        var exact = [], prefix = [];
        for (var i = 0; i < links.length; i++) {
          var a = links[i];
          var t = norm(a.textContent);
          if (!t) continue;
          if (t === want) exact.push(a.href);
          else if (t.indexOf(want + " ") === 0) prefix.push(a.href);
        }
        // Strict matches are considered first.  Treating a prefix match
        // as equal turns a clean hit into an ambiguous one - searching
        // "apixaban" also returns "Apixaban and rivaroxaban comparison",
        // and lumping them together means neither wins.
        var uniq = function (arr) {
          return arr.filter(function (h, i) { return arr.indexOf(h) === i; });
        };
        var e = uniq(exact);
        if (e.length === 1) { window.location.href = e[0]; return; }
        // Several equally-exact hits means the search page really is the
        // right answer; leave the reader on it.
        if (e.length === 0) {
          var p = uniq(prefix);
          if (p.length === 1) window.location.href = p[0];
        }
      } catch (e) {}
    })();
    """

    def _maybe_autojump(self, url: str) -> None:
        term = getattr(self, "_pending_term", "") or ""
        if not term:
            return
        low = url.lower()
        is_search = ("unearth/q?" in low) or ("/books/n/statpearls/?term=" in low)
        if not is_search:
            return
        try:
            self._page.runJavaScript(self._AUTOJUMP_JS % json.dumps(term))
        except Exception as exc:
            _log.debug(f"autojump failed: {exc}")

    def _cache_resolved(self, url: str) -> None:
        """Remember a canonical article/drug URL reached from a search."""
        term = getattr(self, "_pending_term", "") or ""
        if not term:
            return
        m = re.search(r"/books/(NBK\d+)", url) or re.search(r"/drugs/(DB\d+)", url)
        if not m:
            return
        try:
            from .pearls import _ncbi
            _ncbi.remember_url(term, url)
            self._pending_term = ""
        except Exception as exc:
            _log.debug(f"cache resolved url failed: {exc}")

    # StatPearls chapters run to several screens, so landing at the top
    # when the reader clicked "Mx" still leaves them hunting.  Anchor IDs
    # are per-chapter and not derivable, so match on heading text
    # instead - the chapter headings are a fixed vocabulary.
    _SCROLL_JS = r"""
    (function () {
      try {
        var wants = %s;
        if (!wants || !wants.length) return;
        var norm = function (t) {
          return String(t || "").toLowerCase().replace(/\s+/g, " ").trim();
        };
        var heads = document.querySelectorAll("h1,h2,h3,h4");
        for (var w = 0; w < wants.length; w++) {
          var want = norm(wants[w]);
          for (var i = 0; i < heads.length; i++) {
            var t = norm(heads[i].textContent);
            if (t === want || t.indexOf(want) === 0) {
              heads[i].scrollIntoView({block: "start"});
              // Nudge up so the heading is not flush against the top of
              // the viewport, which reads as a cut-off page.
              window.scrollBy(0, -12);
              return;
            }
          }
        }
      } catch (e) {}
    })();
    """

    def _maybe_scroll_to_section(self, url: str) -> None:
        section = getattr(self, "_pending_section", "") or ""
        if not section:
            return
        low = url.lower()
        if "/books/nbk" not in low and "go.drugbank.com/drugs/" not in low:
            return          # still on a search page; wait for the real one
        try:
            from .pearls import _ncbi
            wants = _ncbi.headings_for(section)
        except Exception:
            wants = []
        if not wants:
            self._pending_section = ""
            return
        try:
            self._page.runJavaScript(self._SCROLL_JS % json.dumps(wants))
        except Exception as exc:
            _log.debug(f"section scroll failed: {exc}")
        self._pending_section = ""

    def _show_load_error(self, url: str) -> None:
        """Replace the blank grey rectangle with something actionable."""
        safe = (url or "").replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")
        self._page.setHtml(
            "<html><body style=\"margin:0;background:#162d45;color:#eaf3f8;"
            "font:14px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;"
            "padding:34px 30px;line-height:1.6;\">"
            "<div style=\"font-size:15px;font-weight:600;margin-bottom:10px;\">"
            "Couldn\u2019t load this page</div>"
            "<div style=\"opacity:.85;\">The request failed twice. NCBI rate-limits "
            "rapid requests, so waiting a moment and retrying usually works.</div>"
            f"<div style=\"margin-top:18px;\"><a href=\"{safe}\" style=\"color:#5dd5df;\">"
            "Try again</a></div>"
            f"<div style=\"margin-top:22px;font-size:12px;opacity:.55;"
            f"word-break:break-all;\">{safe}</div>"
            "</body></html>",
            QUrl(url or "about:blank"),
        )

    def apply_theme(self) -> None:
        """Restyle the whole panel after Anki switches light/dark.

        Anki emits `theme_did_change` on a manual toggle and on an OS
        appearance change when following the system setting; without
        this the panel keeps whichever palette it was constructed with
        until Anki restarts.
        """
        try:
            _rebind_theme()
            if getattr(self, "_header", None) is not None:
                self._header.setStyleSheet(f"background: {_NAVY};")
            for btn, qss in (
                (getattr(self, "_btn_back", None), _NAV_BTN_QSS),
                (getattr(self, "_btn_forward", None), _NAV_BTN_QSS),
                (getattr(self, "_btn_reload", None), _NAV_BTN_QSS),
                (getattr(self, "_btn_home", None), _HOME_BTN_QSS),
                (getattr(self, "_btn_close", None), _CLOSE_BTN_QSS),
            ):
                if btn is not None:
                    btn.setStyleSheet(qss)
            if getattr(self, "_results", None) is not None:
                self._results.apply_theme()
        except Exception as exc:
            _log.error("pearls apply_theme", exc)

    def showEvent(self, ev):  # type: ignore[override]
        """A page that finished loading while the dock was hidden can come
        back composited-empty.  Reload if we surfaced onto a blank page."""
        try:
            super().showEvent(ev)
        except Exception:
            pass
        try:
            cur = self._view.url().toString()
            if cur in ("", "about:blank") or cur.startswith("chrome-error"):
                target = getattr(self, "_pending_url", "") or self._current_home_url()
                self._load_retries = 0
                QTimer.singleShot(0, lambda: self._do_load(target))
        except Exception:
            pass

    def _on_url_changed(self, url: QUrl):
        try:
            self._cache_resolved(url.toString())
        except Exception:
            pass
        try:
            history = self._page.history()
            self._btn_back.setEnabled(history.canGoBack())
            self._btn_forward.setEnabled(history.canGoForward())
        except Exception:
            pass

    def _on_load_finished(self, _ok: bool):
        # A failed navigation leaves the view on chrome-error://chromewebdata/,
        # which renders as a blank grey panel with no indication of what went
        # wrong.  Retry once (NCBI throttles bursts of requests, and the retry
        # almost always succeeds), then fall back to a readable message.
        try:
            cur = self._view.url().toString()
        except Exception:
            cur = ""
        if not _ok or cur.startswith("chrome-error"):
            target = getattr(self, "_pending_url", "") or self._current_home_url()
            if getattr(self, "_load_retries", 0) < 1:
                self._load_retries = getattr(self, "_load_retries", 0) + 1
                _log.debug(f"pearls load failed, retrying: {target[:80]!r}")
                QTimer.singleShot(900, lambda: self._do_load(target))
            else:
                self._show_load_error(target)
            return
        try:
            self._maybe_autojump(cur)
        except Exception:
            pass
        try:
            self._maybe_scroll_to_section(cur)
        except Exception:
            pass
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
                self._page.runJavaScript(_HIDE_BOOKSHELF_BAR_JS)
        except Exception:
            pass

