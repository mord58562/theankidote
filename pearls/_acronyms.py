# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.

"""Curated medical-acronym dictionary with context-based disambiguation.

Each entry maps an acronym to one or more candidate expansions.  When an
acronym appears in a card, every candidate is scored by how many of its
context keywords also appear in the card text; the highest scorer wins
(ties broken by listing order - most common expansion first).
"""
from . import _library

import re

# (expansion, context_keywords, brief description for tooltip)
# Loaded from data/library.json - see tools/build_library.py. The
# authoring copy of this vocabulary lives in content/, and is
# compiled rather than imported so content can ship without a
# new add-on release.
_ACRONYMS: dict = {k: [tuple(c) for c in v]
                   for k, v in _library.get("acronyms").items()}


# Pre-compile a single master regex for ALL acronym keys (sorted longest-first
# so e.g. "AFib" wins over "AF").  One scan over the card text, instead of 200+
# individual searches.
_KEYS_BY_LEN = sorted(_ACRONYMS, key=len, reverse=True)
_ACRONYM_RE = re.compile(r"\b(?:" + "|".join(re.escape(k) for k in _KEYS_BY_LEN) + r")\b")

# Lower-case each candidate's context list once at import.
_CONTEXTS = {
    k: [(exp, [w.lower() for w in ctx], desc) for (exp, ctx, desc) in cands]
    for k, cands in _ACRONYMS.items()
}


def resolve(card_text: str) -> list:
    """Find acronyms present in card text and pick the best expansion for each.
    Returns list of {acronym, expansion, description}."""
    found = set(_ACRONYM_RE.findall(card_text))
    if not found:
        return []
    text_lower = card_text.lower()
    out = []
    for acronym in found:
        candidates = _CONTEXTS[acronym]
        best = candidates[0]
        best_score = -1
        for cand in candidates:
            _exp, ctx, _desc = cand
            score = 0
            for kw in ctx:
                if kw in text_lower:
                    score += 1
            if score > best_score:
                best_score = score
                best = cand
        expansion, _ctx, description = best
        out.append({
            "acronym": acronym,
            "expansion": expansion,
            "description": description,
        })
    return out
