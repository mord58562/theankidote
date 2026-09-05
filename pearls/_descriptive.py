# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""Descriptive clinical vocabulary - the words cards are *written in*.

The condition and drug databases cover the things a card is *about*.
This one covers the vocabulary those cards are described with, which
turned out to be the larger gap: on a dermatomyositis card, the disease
resolved and every word describing it - poikiloderma, telangiectasia,
myalgia, pathognomonic - did not. That is backwards. A student who
already knows a term reads past it either way, and one who doesn't is
stuck precisely on the descriptive word, because it is the only part of
the sentence carrying the actual finding.

Entries follow the section convention the popup renderer parses (see
`_formatSummary` in web/marker.js): a lede defining the term, then
optional `Label:` sections. Most entries here want only a lede - these
are definitions, not monographs, and a two-line answer read at a glance
is the entire point. Sections are used where a term has a genuinely
listable dimension: the causes of purpura, the grades of a pressure
injury.

Australian spelling throughout, with US variants carried as aliases so
imported decks still resolve.
"""

from ._vocab import build_vocab

DESCRIPTIVE_TERMS, _NAMES, resolve = build_vocab("descriptive")
