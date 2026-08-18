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

# Loaded from data/library.json - see tools/build_library.py. The
# authoring copy of this vocabulary lives in content/, and is
# compiled rather than imported so content can ship without a
# new add-on release.
from . import _library

PSYCH_TERMS: list = _library.get("psych")


# ---------------------------------------------------------------------------
# Index and resolver
# ---------------------------------------------------------------------------

from urllib.parse import quote_plus as _quote_plus

from . import _matcher

_LOOKUP: dict = {}
_NAMES: list = []

for _t in PSYCH_TERMS:
    for _k in [_t["name"]] + list(_t.get("aliases", []) or []):
        _NAMES.append(_k)
        _LOOKUP.setdefault(_k.lower(), _t)

_MATCHER = _matcher.PhraseMatcher(_NAMES) if _NAMES else None


def _wikipedia_url(term: str) -> str:
    return f"https://en.wikipedia.org/wiki/Special:Search?search={_quote_plus(term)}"


def resolve(text: str) -> list:
    """Find psychiatric phenomenology terms in `text`."""
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
            "category":       t.get("category", "psychiatry"),
            "case_sensitive": False,
        })
    return out
