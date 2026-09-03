# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.

"""Curated medical-acronym dictionary with context-based disambiguation.

Each entry maps an acronym to one or more candidate expansions.  When an
acronym appears in a card, every candidate is scored by how many of its
context keywords also appear in the card text; the highest scorer wins
(ties broken by listing order - most common expansion first).
"""
import re

from . import _library
from . import _matcher


# Acronyms that overlap with Roman numerals. On their own, "IV" means
# intravenous - but "Rome IV", "DSM-IV", "grade IV", "cranial nerve IV"
# and dozens of similar patterns are Roman numerals, not the drug route.
# Suppress the acronym when the immediately-preceding token is a known
# classifier so the popup doesn't misfire in those contexts.
_ROMAN_ACRONYMS = frozenset({
    "II", "III", "IV", "VI", "VII", "VIII", "IX", "XI", "XII",
})
_ROMAN_CLASSIFIERS = frozenset({
    "rome", "dsm", "icd", "type", "class", "grade", "stage", "phase",
    "chapter", "factor", "figure", "level", "generation", "gen",
    "cranial", "nerve", "cn", "world", "war", "period", "line",
    "nyha", "mrc", "killip", "asa", "figo", "raiu",
    "los", "angeles", "salter", "salter-harris",
    "haemophilia", "hemophilia",
})


def _prev_token_lower(text: str, start: int) -> str:
    """The word immediately before `start`, lowercased.

    Skips trailing whitespace and hyphens so both 'Rome IV' and 'DSM-IV'
    resolve to 'rome' / 'dsm'. Returns '' when at start of string.
    """
    left = text[max(0, start - 40):start]
    # Strip trailing separator characters (whitespace, hyphens, en/em dashes).
    left = re.sub(r"[-\s‐-―]+$", "", left)
    if not left:
        return ""
    m = re.search(r"[A-Za-z][A-Za-z-]*$", left)
    return m.group(0).lower() if m else ""


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
    matches = _MATCHER.find(card_text)
    if not matches:
        return []
    # Suppress Roman-numeral false positives: if every occurrence of a
    # numeral acronym sits after a classifier (Rome, DSM, type, grade,
    # cranial nerve, etc.), it isn't the drug route - drop the whole
    # acronym from the results.
    found: set = set()
    for start, _end, k in matches:
        if k in _ROMAN_ACRONYMS:
            if _prev_token_lower(card_text, start) in _ROMAN_CLASSIFIERS:
                continue
        found.add(k)
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
