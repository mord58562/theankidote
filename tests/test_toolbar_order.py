# SPDX-License-Identifier: GPL-3.0-or-later
"""Toolbar order computation regression tests.

Replicates the position computation used by both chat and uptodate
modules so we can confirm the configured order actually decides the
final on-screen order.

The contract: given hook-fire order [uptodate, chat] (registration
order), the final `links` list should have utd and chat in the order
specified by `toolbarOrder`, anchored relative to each other rather
than at fixed indices.
"""

import unittest


BASE = 6
ANKI_BUILTIN_LINKS = ["decks", "add", "browse", "stats", "sync"]  # 5 items
UTD_ID  = "theankidote-utd-toolbar-link"
CHAT_ID = "theankidote-chat-toolbar-link"


def utd_link():
    return f'<a id="{UTD_ID}">UTD</a>'


def chat_link():
    return f'<a id="{CHAT_ID}">CHAT</a>'


def add_utd(links: list, order: list) -> None:
    """Mirror of uptodate._add_toolbar_link's positioning logic."""
    utd_first = (
        "uptodate" in order and "chat" in order
        and order.index("uptodate") < order.index("chat")
    )
    chat_idx = next(
        (i for i, l in enumerate(links) if CHAT_ID in l), None
    )
    if chat_idx is not None:
        links.insert(chat_idx if utd_first else chat_idx + 1, utd_link())
    elif len(links) >= BASE:
        links.insert(BASE, utd_link())
    else:
        links.append(utd_link())


def add_chat(links: list, order: list) -> None:
    """Mirror of chat._add_toolbar_link's positioning logic."""
    chat_first = (
        "chat" in order and "uptodate" in order
        and order.index("chat") < order.index("uptodate")
    )
    utd_idx = next(
        (i for i, l in enumerate(links) if UTD_ID in l), None
    )
    if utd_idx is not None:
        links.insert(utd_idx if chat_first else utd_idx + 1, chat_link())
    elif len(links) >= BASE:
        links.insert(BASE, chat_link())
    else:
        links.append(chat_link())


def simulate(order: list) -> list:
    """Hook-fire order is [uptodate, chat] (their import order in the
    top-level package)."""
    links = list(ANKI_BUILTIN_LINKS)
    add_utd(links, order)
    add_chat(links, order)
    return links


def positions(links: list) -> tuple:
    chat_pos = next(i for i, l in enumerate(links) if CHAT_ID in l)
    utd_pos  = next(i for i, l in enumerate(links) if UTD_ID in l)
    return chat_pos, utd_pos


class ToolbarOrderTest(unittest.TestCase):
    def test_chat_first_keeps_chat_left_of_utd(self):
        links = simulate(["chat", "uptodate"])
        chat_pos, utd_pos = positions(links)
        self.assertLess(chat_pos, utd_pos)

    def test_utd_first_keeps_utd_left_of_chat(self):
        links = simulate(["uptodate", "chat"])
        chat_pos, utd_pos = positions(links)
        self.assertLess(utd_pos, chat_pos)

    def test_default_order_chat_left(self):
        # Fresh-install default in _config.py is ["chat", "uptodate"].
        links = simulate(["chat", "uptodate"])
        chat_pos, utd_pos = positions(links)
        self.assertLess(chat_pos, utd_pos)

    def test_only_one_link_appended_per_module(self):
        links = simulate(["uptodate", "chat"])
        utd_count  = sum(1 for l in links if UTD_ID in l)
        chat_count = sum(1 for l in links if CHAT_ID in l)
        self.assertEqual(utd_count, 1)
        self.assertEqual(chat_count, 1)


if __name__ == "__main__":
    unittest.main()
