# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""Shared factory for the small vocabulary databases.

`_signs`, `_descriptive`, `_psych` and `_preclinical` all resolve
identically: build a name/alias index over a list of dicts from
`library.json`, hand it to `PhraseMatcher`, and return matches with the
same shape the sidebar consumes. Keeping four copies of that in step
was the main friction when a schema field was renamed - four files, one
easy miss. This helper is what each of them now delegates to.
"""

from urllib.parse import quote_plus

from . import _library, _matcher


def _wikipedia_url(term: str) -> str:
    return f"https://en.wikipedia.org/wiki/Special:Search?search={quote_plus(term)}"


def build_vocab(base_key: str, default_category: str = "",
                new_key: str | None = None) -> tuple:
    """Build the term list, name index and `resolve()` function for a
    vocabulary database.

    * `base_key` selects the base list from `library.json`.
    * `new_key`, when set, appends the equivalent overlay list; missing
      keys are tolerated so a library published before the overlay
      shipped still loads.
    * `default_category` supplies the `category` field when an entry
      omits it (kept per-module so `_signs` can default to "signs"
      while `_descriptive` stays "").

    Returns `(terms, names, resolve)`. Callers re-export `terms` under
    their own name (`SIGN_TERMS` etc.) because the build tool and the
    tests read those constants directly, and `names` under `_NAMES` so
    the vocab-coverage tests can inspect the built index.
    """
    terms: list = list(_library.get(base_key))
    if new_key:
        terms += [dict(t) for t in (_library.get(new_key, []) or [])]

    lookup: dict = {}
    names: list = []
    for entry in terms:
        for key in [entry["name"]] + list(entry.get("aliases") or []):
            names.append(key)
            lookup.setdefault(key.lower(), entry)

    # Case-insensitive dedupe: matching is case-insensitive, so two
    # entries differing only in case would double-scan the same text.
    seen_ci: set = set()
    uniq: list = []
    for name in names:
        lk = name.lower()
        if lk in seen_ci:
            continue
        seen_ci.add(lk)
        uniq.append(name)
    names = sorted(uniq, key=len, reverse=True)

    matcher = _matcher.PhraseMatcher(names) if names else None

    def resolve(text: str) -> list:
        if not text or matcher is None:
            return []
        out: list = []
        seen: set = set()
        for _s, _e, key in matcher.find(text):
            t = lookup.get(key)
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
                "category":       t.get("category", default_category),
                "case_sensitive": False,
            })
        return out

    return terms, names, resolve
