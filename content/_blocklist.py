# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""Phrases that must never produce a popup, shipped as content.

A term firing on the wrong word is the defect users actually see, and
it has always been the one class of bug that needed an AnkiWeb release
to fix: the suppression lists lived in Python, so a single bad alias
cost a version bump and a wait for everyone to update. This list is
compiled into `library.json` and reaches installed clients on the next
content check instead.

Scope, deliberately narrow: an entry here stops a phrase being indexed
by every vocabulary at once. That suits a phrase which is wrong in all
contexts - an alias that turns out to name two unrelated things, a word
the base corpus should never have carried. It does not suit a term that
is right in one setting and wrong in another; `_acronyms._CONTEXTS` and
`_ENGLISH_WORD_ACRONYMS` weigh the surrounding card text and stay in
code, because a blanket block would lose the cases they get right.

Blocking is the only power this has. Nothing here can add a popup,
point one somewhere else, or change a word of any summary, so the worst
a mistaken or tampered entry can do is switch a term off.

Matching is case-insensitive and apostrophe-insensitive, so one spelling
covers the variants.
"""

BLOCKLIST: list = [
]
