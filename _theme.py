# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""Shared theme palette - one source of truth for colours used by every
side panel and any chrome the addon adds to the main window.  Detects
light/dark from Anki's theme_manager so all of the addon's UI follows
the same theming as the rest of the app.

Each module that imports this:
    from .. import _theme       (from a subpackage)
    from . import _theme        (from theankidote/__init__.py)

then uses `_theme.DARK`, `_theme.NAVY`, `_theme.TEAL`, etc.
"""


def night_mode() -> bool:
    try:
        from aqt.theme import theme_manager
        return bool(theme_manager.night_mode)
    except Exception:
        # Default to dark when theme_manager isn't available - matches the
        # legacy behaviour of the original AnkiPearls + AnkiDate addons.
        return True


def _build(dark: bool) -> dict:
    """Palette for one mode.  Kept as a function so the theme can be
    rebuilt when Anki switches mode mid-session; module constants are
    then rebound in place, so callers that captured `_theme.NAVY` at
    import time still read the current value."""
    if dark:
        return dict(
            NAVY="#0d2137", NAVY_LIGHT="#1a3a5c", TEAL="#0fcad4",
            TEAL_DIM="rgba(15,202,212,.12)", TEAL_BORDER="rgba(15,202,212,.35)",
            HEADER_TXT="#e8f4f8", BODY_TXT="#eaf3f8",
            MUTED="rgba(232,244,248,.45)", BG_BOX="#162d45",
            # Deliberately close to the AA floor rather than as far
            # above it as possible: this is an easter egg, and at
            # 10.4:1 in a pill it read as a UI element announcing
            # itself. 4.8:1 is legible when you look at it and recedes
            # when you don't.
            QUOTE_TXT="#5f92a4",
        )
    return dict(
        NAVY="#e8f2f8", NAVY_LIGHT="#cfe0ec", TEAL="#0b7f89",
        TEAL_DIM="rgba(11,127,137,.10)", TEAL_BORDER="rgba(11,127,137,.30)",
        HEADER_TXT="#123047", BODY_TXT="#1a2c3e",
        MUTED="rgba(26,44,62,.5)", BG_BOX="#ffffff",
        QUOTE_TXT="#4a7186",  # 4.6:1 on the light header
    )


def refresh() -> bool:
    """Recompute the palette from Anki's current theme.  Returns True if
    the mode actually changed, so callers can skip needless restyling."""
    global DARK
    dark = night_mode()
    changed = dark != DARK
    DARK = dark
    for k, v in _build(dark).items():
        globals()[k] = v
    return changed


# ──────────────────────────────────────────────────────────────────────────
# Dock chrome
# ──────────────────────────────────────────────────────────────────────────
# Three docks - reference, UpToDate, chat - put the same band of chrome
# above a webview, and each had built it separately. That produced two
# arrow families, three systems for sizing the glyphs, header heights of
# 40, 40 and 44, and a close button that turned red in one dock and teal
# in the other two. None of it was decided; it accumulated. Anything a
# user can see across two docks is decided here instead.
#
# This is deliberately a different register from the Settings window,
# which is native Qt on Anki's own palette. A preferences sheet should
# look like the host application. A strip of browser chrome sitting on
# top of a webview should not, or it reads as a native toolbar glued
# above foreign content.

HEADER_H       = 40
NAV_W          = 26          # arrows, reload, close
NAV_W_WIDE     = 28          # home, external, clear - wider glyphs
NAV_H          = 28
HEADER_MARGINS = (6, 0, 6, 0)
HEADER_SPACING = 3
RADIUS_CONTROL = 4

# One arrow family across the docks. The reference panel reached these
# by trying the guillemets first: beside the reload glyph they render
# small and light, and the set stops reading as one set. UpToDate still
# had the guillemets and an anticlockwise reload.
GLYPH_BACK     = "\u2190"
GLYPH_FORWARD  = "\u2192"
GLYPH_RELOAD   = "\u21bb"
GLYPH_HOME     = "\u2302"
GLYPH_EXTERNAL = "\u2197"
GLYPH_CLEAR    = "\u239a"
GLYPH_CLOSE    = "\u2715"

# These glyphs come from different Unicode blocks with different design
# metrics, so one font-size renders them at visibly different weights.
# Sizing each individually is the only way to make them read as a set,
# which is why the QSS below omits font-size and lets these win.
GLYPH_PX = {
    GLYPH_BACK: 15,
    GLYPH_FORWARD: 15,
    GLYPH_RELOAD: 16,
    # Drawn small within its em box in most system fonts, so it needs a
    # couple more pixels than the arrows to belong to the same set.
    GLYPH_HOME: 18,
    GLYPH_EXTERNAL: 14,
    GLYPH_CLEAR: 15,
    GLYPH_CLOSE: 12,
}


def nav_qss() -> str:
    """Flat ghost button for a dock header.

    Built on demand rather than baked in at widget creation so a theme
    switch can regenerate it. Close buttons use this too: a red hover
    was saying "destructive" about closing a sidebar, which is neither
    destructive nor how the other two docks close.
    """
    return (
        "QPushButton{"
        f"background:transparent;color:{HEADER_TXT};border:none;"
        f"border-radius:{RADIUS_CONTROL}px;}}"
        f"QPushButton:hover{{background:{TEAL_DIM};color:{TEAL};}}"
        f"QPushButton:disabled{{color:{MUTED};}}"
    )


def size_glyph(btn) -> None:
    """Apply the optical size for whatever glyph the button carries."""
    px = GLYPH_PX.get(btn.text())
    if not px:
        return
    try:
        f = btn.font()
        f.setPixelSize(px)
        f.setBold(True)
        btn.setFont(f)
    except Exception:
        pass


DARK = night_mode()
refresh()
