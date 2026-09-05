# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""Psychiatric phenomenology - the vocabulary of the mental state exam.

Descriptive psychopathology is unusually unforgiving: the words are
technical, they are not interchangeable with their everyday senses, and
the distinctions between them are exactly what gets examined. A card
saying "circumstantial speech with intact insight" is doing precise work
that is invisible to a reader who has the ordinary meaning of
"circumstantial" in mind.

This file therefore leans harder on contrast than the others. Most
entries name the term they are most often confused with, because in
phenomenology that pairing *is* the definition - tangentiality only
means something against circumstantiality, an illusion only against a
hallucination.

Terminology follows RANZCP and Australian practice; where DSM-5-TR and
ICD-11 differ materially the entry says so rather than picking one.
"""

from ._vocab import build_vocab

PSYCH_TERMS, _NAMES, resolve = build_vocab("psych", default_category="psychiatry")
