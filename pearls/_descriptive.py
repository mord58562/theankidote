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

# Loaded from data/library.json - see tools/build_library.py. The
# authoring copy of this vocabulary lives in content/, and is
# compiled rather than imported so content can ship without a
# new add-on release.
from . import _library

DESCRIPTIVE_TERMS: list = _library.get("descriptive")


# ---------------------------------------------------------------------------
# Index and resolver
# ---------------------------------------------------------------------------
#
# Same shape as the other databases so `_reviewer` treats it identically,
# and built on `PhraseMatcher` rather than a regex alternation - see
# pearls/_matcher.py. This list will keep growing, and the whole point of
# the matcher is that growth costs nothing at review time.

from urllib.parse import quote_plus as _quote_plus

from . import _matcher

_LOOKUP: dict = {}
_NAMES: list = []

for _t in DESCRIPTIVE_TERMS:
    for _k in [_t["name"]] + list(_t.get("aliases", []) or []):
        _NAMES.append(_k)
        _LOOKUP.setdefault(_k.lower(), _t)

_MATCHER = _matcher.PhraseMatcher(_NAMES) if _NAMES else None


def _wikipedia_url(term: str) -> str:
    return f"https://en.wikipedia.org/wiki/Special:Search?search={_quote_plus(term)}"


def resolve(text: str) -> list:
    """Find descriptive-vocabulary terms in `text`.

    Returns the same dict shape as the condition, drug and preclinical
    resolvers, tagged `source="preclinical"` so it inherits the existing
    popup styling - these are reference definitions, not clinical
    monographs, and giving them their own colour would imply a
    distinction the reader does not need to make.
    """
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
