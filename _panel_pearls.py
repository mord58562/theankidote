# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.

"""Side panel: AMBOSS-style UI - nav header + article webview."""

try:
    from PyQt6.QtCore import Qt, QUrl, QSize, pyqtSignal
    from PyQt6.QtWidgets import (
        QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
        QMenu, QProgressBar, QPushButton, QVBoxLayout, QWidget,
    )
    from PyQt6.QtGui import QAction
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
        QMenu, QProgressBar, QPushButton, QVBoxLayout, QWidget,
    )
    from PyQt5.QtWebEngineWidgets import (
        QWebEngineView, QWebEnginePage, QWebEngineProfile, QWebEngineSettings,
    )
    _USER_ROLE  = Qt.UserRole
    _NO_HSCROLL = Qt.ScrollBarAlwaysOff

import json
import re

from . import _webengine, _log, _config, _theme

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

    `_theme` went un-imported until 1.4.1, so every line below raised
    NameError and the whole restyle aborted on the first statement -
    which is why switching Anki's theme left the panel untouched.
    """
    g = globals()
    g["_DARK"] = _theme.DARK
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
            "border-radius:4px;}"
        "QPushButton:hover{"
            f"background:{_TEAL_DIM};color:{_TEAL};}}"
        "QPushButton:disabled{"
            f"color:{_MUTED};}}"
    )
    g["_CLOSE_BTN_QSS"] = (
        "QPushButton{"
            f"background:transparent;color:{_HEADER_TXT};"
            "border:none;border-radius:4px;}"
        "QPushButton:hover{"
            "background:rgba(220,50,50,.18);color:#ff7070;}"
        "QPushButton:pressed{"
            "background:rgba(220,50,50,.32);}"
    )


_rebuild_qss()


# Optical sizes for the header glyphs.  These come from different
# Unicode blocks with different design metrics, so a single font-size
# renders them at visibly different weights - the guillemets came out
# tiny next to the arrows, and the house sat heavier than both.  Sizing
# each glyph individually is the only way to get them to read as one
# set; the QSS below deliberately omits font-size so these win.
_GLYPH_PX = {
    "\u2190": 15,  # back
    "\u2192": 15,  # forward
    "\u21bb": 16,  # reload
    "\u2302": 15,  # home
    "\u2197": 14,  # open externally
    "\u2715": 12,  # close
}


def _nav_btn(parent: QWidget, text: str, tip: str, w: int = 26) -> QPushButton:
    b = QPushButton(text, parent)
    b.setFixedSize(w, 28)
    b.setToolTip(tip)
    b.setStyleSheet(_NAV_BTN_QSS)
    _size_glyph(b, text)
    return b


def _size_glyph(btn: QPushButton, text: str) -> None:
    """Apply the per-glyph optical size from `_GLYPH_PX`."""
    px = _GLYPH_PX.get(text)
    if not px:
        return
    try:
        f = btn.font()
        f.setPixelSize(px)
        f.setBold(True)
        btn.setFont(f)
    except Exception:
        pass


# ──────────────────────────────────────────────────────────────────────────
# Results section
# ──────────────────────────────────────────────────────────────────────────

class _ResultsSection(QWidget):
    article_selected = pyqtSignal(str)
    dismissed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._results: list = []

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Header row: title on the left, dismiss on the right.  The list
        # is a guess at what is relevant on the current card and it is
        # not always a good one, so it needs a way out that isn't
        # closing the whole sidebar.  It comes back on the next card, or
        # immediately via the toolbar button.
        self._hdr_row = QWidget(self)
        hdr_lay = QHBoxLayout(self._hdr_row)
        hdr_lay.setContentsMargins(0, 0, 0, 0)
        hdr_lay.setSpacing(0)

        self._hdr = QLabel("RELEVANT ARTICLES")
        hdr_lay.addWidget(self._hdr, 1)

        self._btn_dismiss = QPushButton("\u2715", self._hdr_row)
        self._btn_dismiss.setFixedSize(22, 22)
        self._btn_dismiss.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_dismiss.setToolTip("Hide this list for now")
        self._btn_dismiss.clicked.connect(self._on_dismiss)
        _size_glyph(self._btn_dismiss, "\u2715")
        hdr_lay.addWidget(self._btn_dismiss)

        self._style_header()
        lay.addWidget(self._hdr_row)

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
        rebuild.

        Item colours come from the list-level stylesheet, so restyling
        is enough - but the header text and row heights are rebuilt from
        the retained results anyway, since the section may be hidden and
        must not be shown by a restyle.
        """
        try:
            self._style_header()
            self._style_list()
            if self._results and self.isVisible():
                self.show_results(list(self._results))
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

    def _on_dismiss(self) -> None:
        self.hide()
        self.dismissed.emit()

    def _style_header(self) -> None:
        self._hdr_row.setStyleSheet(f"""
            QWidget {{
                background: {_NAVY_LIGHT};
                border-top: 1px solid {_TEAL_BORDER};
                border-bottom: 1px solid {_TEAL_BORDER};
            }}
        """)
        self._btn_dismiss.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {_MUTED};
                border: none;
                margin-right: 6px;
            }}
            QPushButton:hover {{ color: {_TEAL}; }}
        """)
        self._hdr.setStyleSheet(f"""
            QLabel {{
                background: transparent;
                color: {_TEAL};
                font-size: 9px;
                font-weight: bold;
                letter-spacing: .08em;
                padding: 5px 10px;
                border: none;
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
        # Set when the user dismisses the article list.  Scoped to the
        # current card so the next card gets a fresh list, and cleared
        # by the toolbar button so re-opening the panel brings it back.
        self._articles_dismissed = False

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

        self._btn_back     = _nav_btn(header, "←", "Back")
        self._btn_forward  = _nav_btn(header, "→", "Forward")
        self._btn_reload   = _nav_btn(header, "↻", "Reload")
        self._btn_home     = _nav_btn(header, "⌂", "Home")
        self._btn_home.clicked.connect(self._go_home)

        # Segmented site switch.  Which site you are on is the single
        # most important piece of state in this panel and it used to be
        # invisible - buried in a dropdown hanging off the home button,
        # so switching to DrugBank to run a search was undiscoverable.
        # Now it is two pills that show where you are and move you.
        self._seg = QWidget(header)
        seg_lay = QHBoxLayout(self._seg)
        seg_lay.setContentsMargins(0, 0, 0, 0)
        seg_lay.setSpacing(0)
        self._btn_sp = QPushButton("StatPearls", self._seg)
        self._btn_db = QPushButton("DrugBank", self._seg)
        for b in (self._btn_sp, self._btn_db):
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setFixedHeight(22)
            b.setCheckable(True)
        self._btn_sp.setToolTip("Search StatPearls")
        self._btn_db.setToolTip("Search DrugBank")
        self._btn_sp.clicked.connect(lambda: self._set_site("statpearls"))
        self._btn_db.clicked.connect(lambda: self._set_site("drugbank"))
        seg_lay.addWidget(self._btn_sp)
        seg_lay.addWidget(self._btn_db)
        self._style_segment()
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
        h_lay.addSpacing(8)
        h_lay.addWidget(self._seg)
        h_lay.addStretch(1)
        h_lay.addWidget(self._btn_external)
        h_lay.addWidget(self._btn_close)
        outer.addWidget(header)

        # ── loading bar (flush under the header) ──────────────────────────
        # Switching to DrugBank goes through Cloudflare's challenge and
        # can take seconds. Nothing on screen changed while that ran, so
        # the switch read as broken and got clicked again - which starts
        # the whole navigation over. A progress bar doesn't make it
        # faster but it does make it legibly in-progress.
        self._progress = QProgressBar(self)
        self._progress.setFixedHeight(2)
        self._progress.setTextVisible(False)
        self._progress.setRange(0, 100)
        self._progress.hide()
        self._style_progress()
        outer.addWidget(self._progress)

        # ── webview ───────────────────────────────────────────────────────
        self._profile = QWebEngineProfile(_PROFILE_NAME, self)
        # Cloudflare bypass (Chrome UA, sec-ch-ua headers, stealth JS, etc.).
        # DrugBank pages sit behind Cloudflare's bot challenge; without this
        # the verification page gets stuck and never redirects to the article.
        _webengine.apply_to_profile(self._profile)
        self._page = QWebEnginePage(self._profile, self)
        self._view = QWebEngineView(self)
        self._view.setPage(self._page)
        # Render StatPearls and DrugBank dark when Anki is dark, using
        # Chromium's own auto-dark pass - see _webengine.set_dark_mode.
        _webengine.set_dark_mode(self._page, _DARK)

        # Renderer crash recovery - same pattern as the UTD dock.
        try:
            self._page.renderProcessTerminated.connect(self._on_render_crash)
        except Exception as exc:
            _log.error("pearls renderProcessTerminated connect", exc)

        # Navigation tracing.  The blank-panel reports so far have had no
        # message of any kind, which rules out both the load-failure and
        # renderer-crash paths - so the page is "loading fine" and still
        # showing nothing.  Record the whole sequence to a file the user
        # can send back, including what the DOM actually contains.
        try:
            self._view.loadStarted.connect(
                lambda: _log.diag(f"loadStarted url={self._view.url().toString()[:120]!r}")
            )
        except Exception:
            pass

        # ── results section ───────────────────────────────────────────────
        self._results = _ResultsSection(self)
        self._results.article_selected.connect(self.load_url)
        self._results.dismissed.connect(self._on_results_dismissed)

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
        self._view.loadStarted.connect(
            lambda: (self._progress.setValue(0), self._progress.show()))
        self._view.loadProgress.connect(self._progress.setValue)
        self._view.loadFinished.connect(lambda _ok: self._progress.hide())

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
        self._articles_dismissed = False
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
        # A new card's results arrive here, so this is where a dismissal
        # scoped to the previous card expires.
        self._articles_dismissed = False
        if self._show_articles:
            if results:
                self._results.show_results(results)
            else:
                self._results.hide()

    def reset_for_new_card(self) -> None:
        """Called when toolbar button is pressed on a different card.
        Navigates the webview to the StatPearls homepage and shows the list."""
        self._show_articles = True
        self._articles_dismissed = False
        self._auto_loaded = False
        self._view.load(QUrl(self._current_home_url()))
        if self._last_results:
            self._results.show_results(self._last_results)

    def hide_article_list(self) -> None:
        """Called when user opens the panel via popup click - list stays out
        of the way so the article body fills the pane."""
        self._show_articles = False
        self._results.hide()

    def _on_results_dismissed(self) -> None:
        """User hid the article list from its own header.

        Kept separate from `hide_article_list` (which is the popup-click
        path) so the two intents stay distinguishable: this one is a
        judgement about the list's usefulness on this card, and it
        should not survive to the next one."""
        self._articles_dismissed = True
        self._show_articles = False

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
                site = "db" if "drugbank" in url.lower() else "sp"
                hit = _ncbi.cached_url(f"{site}:{term}")
                if not hit and site == "sp":
                    acc = _ncbi.cached(term)
                    hit = _ncbi.article_url(acc) if acc else None
                if hit:
                    url = hit
                    self._pending_url = hit
                elif "ncbi.nlm.nih.gov" in url.lower():
                    # Nothing cached: resolve the chapter before
                    # navigating.  Landing on the in-book search results
                    # page is not an acceptable fallback - NCBI only
                    # redirects to the chapter when a search has exactly
                    # one hit, and the multi-hit results page does not
                    # render in this webview at all.
                    #
                    # Strictly gated on the target being NCBI: the
                    # resolver searches StatPearls, so running it for a
                    # DrugBank link sends drug popups to a StatPearls
                    # chapter instead of the drug page.
                    self._resolve_then_load(term, url, section)
                    return
            except Exception as exc:
                _log.diag(f"cache lookup failed for {term!r}: {exc}")
        try:
            self._view.stop()
        except Exception:
            pass
        self._load_queued = True
        QTimer.singleShot(0, lambda: self._do_load(url))

    def _resolve_then_load(self, term: str, fallback: str, section: str) -> None:
        """Look the term up on NCBI, then load the chapter it resolves to.

        Runs off the UI thread, so the panel shows a short placeholder
        rather than freezing or flashing a page we know renders blank.
        Any failure falls back to the original search URL, which is no
        worse than the previous behaviour."""
        self._pending_section = section
        self._show_resolving(term)
        _log.diag(f"resolving {term!r}")

        from .pearls import _ncbi as _ncbi_mod

        def done(acc):
            try:
                if acc:
                    target = _ncbi_mod.article_url(acc)
                    _log.diag(f"resolved {term!r} -> {acc}")
                else:
                    target = fallback
                    _log.diag(f"unresolved {term!r}; falling back to search")
                self._pending_url = target
                self._load_retries = 0
                self._do_load(target)
            except Exception as exc:
                _log.error("resolve_then_load", exc)

        try:
            _ncbi_mod.resolve_async(term, done)
        except Exception as exc:
            _log.diag(f"resolve_async unavailable: {exc}")
            done(None)

    def _show_resolving(self, term: str) -> None:
        safe = (term or "").replace("&", "&amp;").replace("<", "&lt;")
        self._page.setHtml(
            "<html><body style=\"margin:0;background:#162d45;color:#eaf3f8;"
            "font:14px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;"
            "padding:34px 30px;line-height:1.6;\">"
            f"<div style=\"opacity:.75;\">Finding the StatPearls chapter for "
            f"<b>{safe}</b>\u2026</div></body></html>"
        )

    def _do_load(self, url: str) -> None:
        self._load_queued = False
        try:
            _log.diag(f"_do_load {url[:120]!r}")
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

    def _style_progress(self) -> None:
        self._progress.setStyleSheet(
            "QProgressBar { border: none; background: transparent; }"
            f"QProgressBar::chunk {{ background: {_TEAL}; }}"
        )

    def _style_segment(self) -> None:
        """Pill pair sharing one outline, active half filled."""
        base = (
            "QPushButton{border:1px solid %s;background:transparent;"
            "color:%s;font-size:11px;font-weight:600;padding:0 11px;}"
            "QPushButton:hover{background:%s;}"
            "QPushButton:checked{background:%s;color:%s;}"
        ) % (_TEAL_BORDER, _MUTED, _TEAL_DIM, _TEAL_DIM, _TEAL)
        self._btn_sp.setStyleSheet(
            base + "QPushButton{border-top-left-radius:11px;"
                   "border-bottom-left-radius:11px;border-right:none;}")
        self._btn_db.setStyleSheet(
            base + "QPushButton{border-top-right-radius:11px;"
                   "border-bottom-right-radius:11px;}")

    def _refresh_home_ui(self) -> None:
        choice = self._current_home_choice()
        self._btn_sp.setChecked(choice == "statpearls")
        self._btn_db.setChecked(choice == "drugbank")
        self._btn_home.setToolTip(f"Home ({self._current_home_label()})")

    def _set_site(self, choice: str) -> None:
        """Switch site: navigate there now and make it the default.

        Doing both is the point - previously the dropdown only changed
        which page the home button would load *next* time, which is not
        what anyone clicking "DrugBank" means."""
        try:
            _config.set_value("pearlsHomePage", choice)
        except Exception as exc:
            _log.error("pearls set site", exc)
        self._refresh_home_ui()
        # Already browsing that site? Record the preference and stay put.
        # Reloading DrugBank's home over a DrugBank monograph costs a
        # Cloudflare round trip and throws away the page you were
        # reading, which is not what clicking the pill you are already
        # on should do.
        try:
            cur = self._view.url().toString().lower()
        except Exception:
            cur = ""
        on_db = "drugbank.com" in cur
        if cur and ((choice == "drugbank") == on_db):
            self._clear_pending()
            return
        self._go_home()

    def _clear_pending(self) -> None:
        """Drop the popup-click intent.

        Set by `load_url` and consumed by the resolve / autojump / scroll
        handlers.  Any navigation the user drives themselves - home, a
        site switch, a search on the site - is a different intent, and
        leaving the old one in place makes those handlers act on it."""
        self._pending_url = ""
        self._pending_term = ""
        self._pending_section = ""

    def _go_home(self):
        self._auto_loaded = False
        self._clear_pending()
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
        """The renderer process died.  Qt leaves the view painted blank,
        which is indistinguishable from an empty page - the panel just
        goes grey with no explanation.  Report it, and bound the retries
        so a page that reliably kills the renderer shows a message
        instead of flashing content at the reader forever."""
        try:
            self._crash_url = self._view.url().toString()
        except Exception:
            self._crash_url = None
        n = getattr(self, "_crash_count", 0) + 1
        self._crash_count = n
        _log.diag(f"RENDERER TERMINATED status={status} exit={exit_code} attempt={n}")
        if n > 2:
            # Only the give-up case reaches stderr, since Anki surfaces
            # that as a modal error report and a crash we recover from
            # silently is not worth interrupting a review for.
            _log.warn(
                f"renderer terminated {n}x (status={status}, exit={exit_code}, "
                f"url={(self._crash_url or '')[:120]!r})"
            )
            self._show_crash_error(status, exit_code)
            return
        QTimer.singleShot(1500, self._recover_after_crash)

    def _recover_after_crash(self):
        url = getattr(self, "_crash_url", None)
        blank = {"about:blank", "", "chrome-error://chromewebdata/"}
        target = url if url and url not in blank else self._current_home_url()
        try:
            self._view.load(QUrl(target))
        except Exception as exc:
            _log.error("pearls post-crash reload", exc)

    def _show_crash_error(self, status, exit_code) -> None:
        url = (getattr(self, "_crash_url", "") or "").replace("&", "&amp;")
        url = url.replace("<", "&lt;").replace('"', "&quot;")
        self._page.setHtml(
            "<html><body style=\"margin:0;background:#162d45;color:#eaf3f8;"
            "font:14px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;"
            "padding:34px 30px;line-height:1.6;\">"
            "<div style=\"font-size:15px;font-weight:600;margin-bottom:10px;\">"
            "This page kept crashing the browser engine</div>"
            "<div style=\"opacity:.85;\">The embedded renderer stopped three "
            "times in a row on this page, so reloading has been given up on. "
            "Opening it in your normal browser will work.</div>"
            f"<div style=\"margin-top:18px;\"><a href=\"{url}\" "
            "style=\"color:#5dd5df;\">Open in browser</a></div>"
            f"<div style=\"margin-top:22px;font-size:12px;opacity:.55;\">"
            f"Renderer exit status {status}, code {exit_code}. Please include "
            f"this line if you report the problem.</div>"
            f"<div style=\"margin-top:10px;font-size:12px;opacity:.45;"
            f"word-break:break-all;\">{url}</div>"
            "</body></html>",
            QUrl(getattr(self, "_crash_url", "") or "about:blank"),
        )

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
        # The pending term belongs to whichever site the popup pointed
        # at.  A DrugBank search page also matches the search patterns
        # below, so without this a leftover StatPearls term would drive
        # a jump inside DrugBank's results.
        want_db = "drugbank" in (getattr(self, "_pending_url", "") or "").lower()
        if want_db != ("drugbank.com" in low):
            return
        # NCBI redirects the in-book search URL to the book's own
        # accession with the query preserved
        # (/books/n/statpearls/?term=X -> /books/NBK430685/?term=X), so
        # matching only the pre-redirect form missed every real case.
        is_search = (
            "unearth/q?" in low
            or "/books/n/statpearls/?term=" in low
            or ("/books/nbk" in low and "term=" in low)
        )
        if not is_search:
            return
        try:
            _log.diag(f"autojump attempt term={term!r}")
            self._page.runJavaScript(self._AUTOJUMP_JS % json.dumps(term))
        except Exception as exc:
            _log.diag(f"autojump failed: {exc}")

    def _cache_resolved(self, url: str) -> None:
        """Remember a canonical article/drug URL reached from a search."""
        term = getattr(self, "_pending_term", "") or ""
        if not term:
            return
        # A search-results URL carries a query string and resolves to the
        # book root, not the chapter - caching it would pin the term to
        # the StatPearls landing page forever.
        if "?" in url:
            return
        m = re.search(r"/books/(NBK\d+)", url) or re.search(r"/drugs/(DB\d+)", url)
        if not m:
            return
        site = "db" if "drugbank" in url.lower() else "sp"
        try:
            from .pearls import _ncbi
            _ncbi.remember_url(f"{site}:{term}", url)
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
                (getattr(self, "_btn_home", None), _NAV_BTN_QSS),
                (getattr(self, "_btn_external", None), _NAV_BTN_QSS),
                (getattr(self, "_btn_close", None), _CLOSE_BTN_QSS),
            ):
                if btn is not None:
                    btn.setStyleSheet(qss)
                    _size_glyph(btn, btn.text())
            if getattr(self, "_btn_sp", None) is not None:
                self._style_segment()
            if getattr(self, "_progress", None) is not None:
                self._style_progress()
            if getattr(self, "_results", None) is not None:
                self._results.apply_theme()
            # Follow Anki into dark mode without a reload: the attribute
            # applies to the live page, and Blink repaints on the next
            # frame.
            if getattr(self, "_page", None) is not None:
                _webengine.set_dark_mode(self._page, _DARK)
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
            # A load queued by `load_url` is about to run; starting a
            # second one here would cancel it, and the cancellation
            # surfaces as a failed navigation.  This is exactly the
            # "Open article" path, which shows the dock and then loads.
            if getattr(self, "_load_queued", False):
                return
            cur = self._view.url().toString()
            if cur in ("", "about:blank") or cur.startswith("chrome-error"):
                target = getattr(self, "_pending_url", "") or self._current_home_url()
                self._load_retries = 0
                QTimer.singleShot(0, lambda: self._do_load(target))
        except Exception:
            pass

    def _on_url_changed(self, url: QUrl):
        try:
            _log.diag(f"urlChanged {url.toString()[:120]!r}")
        except Exception:
            pass
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

    def _force_repaint(self) -> None:
        """Work around the view staying blank after a completed load.

        The page is fully loaded and laid out (the DOM probe reports a
        populated body and the correct title) but nothing is composited,
        so the panel shows an empty rectangle.  Qt has no "repaint now"
        that reliably reaches the web content, but a zoom round-trip
        forces a relayout plus a fresh composite, and is invisible to
        the reader at these magnitudes.
        """
        try:
            z = self._view.zoomFactor()
            self._view.setZoomFactor(z * 1.0001)
            QTimer.singleShot(0, lambda: self._restore_zoom(z))
        except Exception as exc:
            _log.diag(f"repaint nudge failed: {exc}")

    def _restore_zoom(self, z: float) -> None:
        try:
            self._view.setZoomFactor(z)
            self._view.update()
        except Exception:
            pass

    def _probe_dom(self, tag: str) -> None:
        """Report what the page actually rendered.  A successful load
        that leaves an empty body is the case none of the existing error
        paths cover, and it is indistinguishable from a crash on screen."""
        try:
            self._page.runJavaScript(
                "(function(){try{return JSON.stringify({"
                "url:location.href,"
                "title:document.title||'',"
                "bodyLen:(document.body?document.body.innerHTML.length:-1),"
                "text:(document.body?document.body.innerText.slice(0,120):'')"
                "});}catch(e){return 'probe error: '+e;}})()",
                lambda r, t=tag: _log.diag(f"{t} dom={r}"),
            )
        except Exception as exc:
            _log.diag(f"{tag} probe failed: {exc}")

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
            # Retry what actually failed.  `_pending_url` is only set by
            # `load_url` (the popup "Open article" path) and survives
            # until the next one, so using it here meant a failed
            # in-page navigation - a DrugBank search, most visibly -
            # retried whatever StatPearls chapter had last been opened
            # and dumped the reader back on it.  `requestedUrl` is the
            # URL Chromium was asked for, and is still correct on the
            # chrome-error page.
            requested = ""
            try:
                requested = self._page.requestedUrl().toString()
            except Exception:
                pass
            if requested.startswith("chrome-error") or requested == "about:blank":
                requested = ""
            target = requested or getattr(self, "_pending_url", "") \
                or self._current_home_url()
            # A navigation that was superseded - the home page still
            # loading when the user clicks a link, which is the common
            # case - reports ok=False for the abandoned one.  That is
            # normal, not a failure: something newer is already on its
            # way, and retrying would fight it.
            if getattr(self, "_load_queued", False):
                _log.diag(f"load superseded (url={cur[:100]!r})")
                return
            if getattr(self, "_load_retries", 0) < 1:
                self._load_retries = getattr(self, "_load_retries", 0) + 1
                # Recorded to the diagnostic file rather than stderr:
                # Anki turns anything on stderr into a modal error report,
                # and a retry that then succeeds is not something to
                # interrupt the user for.
                _log.diag(f"load failed (ok={_ok}, url={cur[:100]!r}); retrying")
                QTimer.singleShot(900, lambda: self._do_load(target))
            else:
                _log.warn(f"load failed twice: {target[:100]!r}")
                self._show_load_error(target)
            return
        self._crash_count = 0
        # The intent that `load_url` recorded has now been satisfied.
        # Leaving it set turns it into a stale fallback for every later
        # navigation the user makes themselves.
        if cur and not cur.startswith("chrome-error"):
            self._pending_url = ""
        _log.diag(f"loadFinished ok={_ok} url={cur[:120]!r}")
        try:
            vs = self._view.size()
            cs = self._page.contentsSize()
            _log.diag(
                f"geometry view={vs.width()}x{vs.height()} "
                f"visible={self._view.isVisible()} "
                f"contents={int(cs.width())}x{int(cs.height())} "
                f"zoom={self._view.zoomFactor():.2f}"
            )
        except Exception as exc:
            _log.diag(f"geometry probe failed: {exc}")
        self._probe_dom("afterLoad")
        self._force_repaint()
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

