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


import re as _re
from urllib.parse import quote_plus as _quote_plus


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
_PRECLINICAL_RE = (
    _re.compile(r"\b(?:" + "|".join(_re.escape(n) for n in _NAMES) + r")\b",
                _re.IGNORECASE)
    if _NAMES else None
)


def _wikipedia_url(term: str) -> str:
    return f"https://en.wikipedia.org/wiki/Special:Search?search={_quote_plus(term)}"


def resolve(text: str) -> list:
    if not text or _PRECLINICAL_RE is None:
        return []
    out = []
    seen: set = set()
    for m in _PRECLINICAL_RE.finditer(text):
        key = m.group(0).lower()
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
