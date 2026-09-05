# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""General clinical signs and symptoms - the vocabulary of examination.

Companion to `_descriptive` (morphology and laboratory words) and
`_psych` (mental state). This file covers the cardiorespiratory,
gastrointestinal, neurological and renal terms that examination and
history cards are written in.

The editorial line is the same as elsewhere: define the term, then give
the one discriminating fact that makes it useful at the bedside rather
than a gloss you could have guessed. Orthopnoea is only interesting
because of *why* lying flat matters; a murmur only becomes information
once you know which features separate innocent from pathological.
Entries stop there - a full differential belongs in the condition entry
the sign points to, not in a hover popup.

Australian spelling; US variants carried as aliases so imported decks
still resolve.
"""

from ._vocab import build_vocab

SIGN_TERMS, _NAMES, resolve = build_vocab("signs", default_category="signs")
