# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""Preclinical / basic-medical-science term library.

Standalone, fully free. No UpToDate dependency. Source references are
free-tier educational sites (Deranged Physiology and similar) - all
summaries are reworded in plain language.

The `new_preclinical` overlay is where drug CLASSES live, under the
existing `pharmacology` category. They are not drugs - "antibiotics"
has no DrugBank monograph and no generic name - and putting them here
gets the right source label and the Wikipedia fallback for free.
"""

from ._vocab import build_vocab

# `new_preclinical` is authored in content/_rich.py and compiled under
# its own key, mirroring `new_drugs` in `_drugs.py`. Kept out of
# `preclinical` because `tools/build_library.py` reads that list back
# as the base for the next build, so an entry appended there could
# never be removed again.
PRECLINICAL_TERMS, _NAMES, resolve = build_vocab(
    "preclinical", new_key="new_preclinical",
)
