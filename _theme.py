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


DARK = night_mode()

if DARK:
    NAVY        = "#0d2137"
    NAVY_LIGHT  = "#1a3a5c"
    TEAL        = "#0fcad4"
    TEAL_DIM    = "rgba(15,202,212,.12)"
    TEAL_BORDER = "rgba(15,202,212,.35)"
    HEADER_TXT  = "#e8f4f8"
    BODY_TXT    = "#eaf3f8"
    MUTED       = "rgba(232,244,248,.45)"
    BG_BOX      = "#162d45"
else:
    NAVY        = "#e8f2f8"
    NAVY_LIGHT  = "#cfe0ec"
    TEAL        = "#0a9ba3"
    TEAL_DIM    = "rgba(10,155,163,.1)"
    TEAL_BORDER = "rgba(10,155,163,.3)"
    HEADER_TXT  = "#1a2c3e"
    BODY_TXT    = "#1a2c3e"
    MUTED       = "rgba(26,44,62,.5)"
    BG_BOX      = "#ffffff"
