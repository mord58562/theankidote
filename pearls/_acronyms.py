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
from . import _matcher


# (expansion, context_keywords, brief description for tooltip)
# Loaded from data/library.json - see tools/build_library.py. The
# authoring copy of this vocabulary lives in content/, and is
# compiled rather than imported so content can ship without a
# new add-on release.
_ACRONYMS: dict = {k: [tuple(c) for c in v]
                   for k, v in _library.get("acronyms").items()}


# Matched by first-word index, not by an alternation over all 420 keys.
# Acronyms are matched case-sensitively - lower-casing them turns "ALL"
# into the English word - so the matcher is built in that mode, which
# also keeps the keys exactly as given. Longest-first still holds, so
# "AFib" wins over "AF"; that ordering is PhraseMatcher's contract too.
#
# Like _preclinical, this module was left behind when 2.1 moved the
# other vocabularies over, and kept paying O(text x alternatives):
# 2.6ms of every card scan.
_KEYS_BY_LEN = sorted(_ACRONYMS, key=len, reverse=True)
_MATCHER = _matcher.PhraseMatcher(_KEYS_BY_LEN, case_sensitive=True)

# Lower-case each candidate's context list once at import.
_CONTEXTS = {
    k: [(exp, [w.lower() for w in ctx], desc) for (exp, ctx, desc) in cands]
    for k, cands in _ACRONYMS.items()
}


def resolve(card_text: str) -> list:
    """Find acronyms present in card text and pick the best expansion for each.
    Returns list of {acronym, expansion, description}.

    Context scoring exists to disambiguate, and 401 of the 420 acronyms
    have exactly one candidate, so for 95% of hits the loop below
    substring-searched the whole card for every context keyword in order
    to pick the only option available. Scoring now runs only where there
    is an actual choice, and `card_text.lower()` is deferred until then
    rather than computed for every card whether or not it is used.
    """
    found = {k for _s, _e, k in _MATCHER.find(card_text)}
    if not found:
        return []
    text_lower = None
    out = []
    for acronym in found:
        candidates = _CONTEXTS[acronym]
        if len(candidates) == 1:
            best = candidates[0]
        else:
            if text_lower is None:
                text_lower = card_text.lower()
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
