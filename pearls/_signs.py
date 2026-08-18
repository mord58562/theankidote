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

# Loaded from data/library.json - see tools/build_library.py. The
# authoring copy of this vocabulary lives in content/, and is
# compiled rather than imported so content can ship without a
# new add-on release.
from . import _library

SIGN_TERMS: list = _library.get("signs")


# ---------------------------------------------------------------------------
# Index and resolver
# ---------------------------------------------------------------------------

from urllib.parse import quote_plus as _quote_plus

from . import _matcher

_LOOKUP: dict = {}
_NAMES: list = []

for _t in SIGN_TERMS:
    for _k in [_t["name"]] + list(_t.get("aliases", []) or []):
        _NAMES.append(_k)
        _LOOKUP.setdefault(_k.lower(), _t)

_MATCHER = _matcher.PhraseMatcher(_NAMES) if _NAMES else None


def _wikipedia_url(term: str) -> str:
    return f"https://en.wikipedia.org/wiki/Special:Search?search={_quote_plus(term)}"


def resolve(text: str) -> list:
    """Find clinical sign and symptom terms in `text`."""
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
            "category":       t.get("category", "signs"),
            "case_sensitive": False,
        })
    return out
