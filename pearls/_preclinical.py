# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""Preclinical / basic-medical-science term library.

Standalone, fully free. No UpToDate dependency. Source references are
free-tier educational sites (Deranged Physiology and similar) - all
summaries are reworded in plain language.
"""

# Loaded from data/library.json - see tools/build_library.py. The
# authoring copy of this vocabulary lives in content/, and is
# compiled rather than imported so content can ship without a
# new add-on release.
from . import _library

PRECLINICAL_TERMS: list = _library.get("preclinical")

# Terms absent from the base vocabulary, authored in content/_rich.py as
# NEW_PRECLINICAL and compiled under their own key. Same seam and same
# reasoning as `new_drugs` in `_drugs.py`: kept out of `preclinical`
# because `tools/build_library.py` reads that list back as the base for
# the next build, so an entry appended there could never be removed
# again. Optional, since a library published before 2.2 has no such key.
#
# This is where drug CLASSES live, under the existing `pharmacology`
# category. They are not drugs - `antibiotics` has no DrugBank monograph
# and no generic name - and putting them here gets the right source
# label and the Wikipedia fallback for free.
_NEW: list = _library.get("new_preclinical", [])
PRECLINICAL_TERMS = list(PRECLINICAL_TERMS) + [dict(t) for t in _NEW]


from urllib.parse import quote_plus as _quote_plus

from . import _matcher


_LOOKUP: dict = {}
_NAMES: list = []
for _t in PRECLINICAL_TERMS:
    _n = _t["name"]
    _keys = [_n] + list(_t.get("aliases", []) or [])
    _NAMES.extend(_keys)
    for _k in _keys:
        _LOOKUP[_k.lower()] = _t

# Case-insensitive dedup (matching is case-insensitive at runtime, so two
# entries differing only in case are the same term).
_seen_ci: set = set()
_uniq: list = []
for _name in _NAMES:
    _lk = _name.lower()
    if _lk in _seen_ci:
        continue
    _seen_ci.add(_lk)
    _uniq.append(_name)
_NAMES = sorted(_uniq, key=len, reverse=True)

# Matched by first-word index, not by an alternation over all 501 names.
# This module was left behind when 2.1 moved conditions, drugs, signs,
# descriptive and psych onto PhraseMatcher, so it kept paying
# O(text x alternatives): 9.5ms of every card scan, more than the other
# six vocabularies put together. Semantics are unchanged - PhraseMatcher
# is case-insensitive, longest-wins and non-overlapping, which is
# exactly what the sorted alternation with \b...\b was.
_MATCHER = _matcher.PhraseMatcher(_NAMES) if _NAMES else None


def _wikipedia_url(term: str) -> str:
    return f"https://en.wikipedia.org/wiki/Special:Search?search={_quote_plus(term)}"


def resolve(text: str) -> list:
    if not text or _MATCHER is None:
        return []
    out = []
    seen: set = set()
    for _s, _e, key in _MATCHER.find(text):
        t = _LOOKUP.get(key)
        if t is None:
            continue
        canon = t["name"]
        if canon in seen:
            continue
        seen.add(canon)
        out.append({
            "name":           canon,
            "summary":        t["summary"],
            "url":            _wikipedia_url(canon),
            "source":         "preclinical",
            "category":       t.get("category", ""),
            "case_sensitive": False,
        })
    return out
