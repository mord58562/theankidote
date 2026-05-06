# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""Shared dock-layout helper.

The three side panels (AI chat, UpToDate, StatPearls) all live in the
same dock area.  Without intervention Qt tabs them together when more
than one is visible, so opening a second dock hides the first.

This helper places each dock side-by-side in the canonical left-to-right
order (AI -> UTD -> Pearls) when it becomes visible, regardless of the
order the user opens them in.

Usage from each module after `mw.addDockWidget(area, dock)`:

    from .. import _dock_layout
    _dock_layout.arrange(dock, _dock_layout.ORDER_CHAT)

Order constants are integers - lower numbers sit further left.
"""

from aqt import mw

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QDockWidget
except (ImportError, AttributeError):
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QDockWidget


# Position order, lowest = leftmost.  Mirrors the user-requested layout:
# AI on the left, UpToDate in the middle, StatPearls/DrugBank on the right.
ORDER_CHAT     = 1
ORDER_UPTODATE = 2
ORDER_PEARLS   = 3


# Object-name tags identifying each of our docks.  Used to recognise our
# own siblings without picking up unrelated dock widgets from other
# add-ons.
_OUR_DOCK_NAMES = {
    "TheAnkiDote_dock_chat":     ORDER_CHAT,
    "TheAnkiDote_dock_uptodate": ORDER_UPTODATE,
    "TheAnkiDote_dock_pearls":   ORDER_PEARLS,
}


def _our_visible_siblings(self_dock: QDockWidget):
    """Return [(order, dock), ...] for our other visible docks in the
    same area as `self_dock`."""
    out = []
    try:
        area = mw.dockWidgetArea(self_dock)
    except Exception:
        return out
    for d in mw.findChildren(QDockWidget):
        if d is self_dock:
            continue
        if d.objectName() not in _OUR_DOCK_NAMES:
            continue
        try:
            if not d.isVisible():
                continue
            if mw.dockWidgetArea(d) != area:
                continue
        except Exception:
            continue
        out.append((_OUR_DOCK_NAMES[d.objectName()], d))
    return out


def arrange(self_dock: QDockWidget, self_order: int) -> None:
    """Position `self_dock` in the canonical left-to-right row.

    Called every time the dock is shown.  Idempotent - if no rearrangement
    is needed the call is a no-op.  Safe when no siblings are visible
    (just leaves the dock where Qt put it).
    """
    if self_dock is None:
        return
    try:
        siblings = _our_visible_siblings(self_dock)
        if not siblings:
            return  # alone in this area, nothing to split with

        # Build a sorted list (order, dock) including self.
        all_docks = sorted(siblings + [(self_order, self_dock)],
                           key=lambda x: x[0])
        my_idx = next(i for i, (o, d) in enumerate(all_docks) if d is self_dock)

        # Anchor on the dock immediately to my left (if any), splitting
        # so I land on its right side.  If I'm leftmost, anchor on the
        # dock immediately to my right and split so it lands on my right.
        if my_idx > 0:
            left_dock = all_docks[my_idx - 1][1]
            mw.splitDockWidget(left_dock, self_dock, Qt.Orientation.Horizontal)
        else:
            right_dock = all_docks[my_idx + 1][1]
            mw.splitDockWidget(self_dock, right_dock, Qt.Orientation.Horizontal)

        self_dock.show()
        self_dock.raise_()
    except Exception as exc:
        print(f"[TheAnkiDote] dock arrange error: {exc}")
