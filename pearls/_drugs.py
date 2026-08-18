# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.

"""Drug name detection - generic + brand names with concise clinical summaries.

Each entry has a primary generic name (matched case-insensitively), optional
brand names (matched case-sensitively because branded medications are written
with a capital first letter), and a clinically-focused summary covering:
  • Class + mechanism of action (brief)
  • Key indication(s)
  • Important adverse effects (SE)
  • Critical contraindications/cautions (CI)

Brand names that are also common English words are deliberately excluded to
avoid false positives.
"""

from . import _library

import re

from . import _matcher
from urllib.parse import quote_plus

# Loaded from data/library.json - see tools/build_library.py. The
# authoring copy of this vocabulary lives in content/, and is
# compiled rather than imported so content can ship without a
# new add-on release.
_DRUGS: list = _library.get("drugs")


# ── DrugBank direct URLs ──────────────────────────────────────────────────────
# Accession IDs for well-established drugs.  When present, clicking the popup
# button opens the specific DrugBank page; otherwise a search URL is used.
# Loaded from data/library.json - see tools/build_library.py. The
# authoring copy of this vocabulary lives in content/, and is
# compiled rather than imported so content can ship without a
# new add-on release.
_DRUGBANK_IDS: dict = _library.get("drugbank_ids")


DRUGBANK_FREE_ACCOUNT_URL = "https://go.drugbank.com/public_users/sign_up"


def _drugbank_url(entry: dict) -> str:
    # DrugBank monograph pages are viewable without an account; the unearth
    # search endpoint is sometimes gated - users can sign up for a free
    # DrugBank account in their own browser session if they hit a wall.
    db_id = _DRUGBANK_IDS.get((entry.get("generic") or "").lower())
    if db_id:
        return f"https://go.drugbank.com/drugs/{db_id}"
    name = entry.get("generic") or ""
    return f"https://go.drugbank.com/unearth/q?searcher=drugs&query={quote_plus(name)}"


# ── Build lookup tables and master regexes ────────────────────────────────────

_GENERIC_LOOKUP: dict = {}   # lowercase generic name → entry
_BRAND_LOOKUP:   dict = {}   # exact brand name → entry

for _d in _DRUGS:
    _g = _d.get("generic")
    if _g:
        _GENERIC_LOOKUP[_g.lower()] = _d
    # A brand that case-insensitively matches the generic isn't a real brand -
    # skip it so the same word doesn't surface twice through the brand path.
    _g_lower = (_g or "").lower()
    for _b in _d.get("brands", []) or []:
        if _b.lower() == _g_lower:
            continue
        _BRAND_LOOKUP[_b] = _d


def _compile_alternation(words):
    """Build a regex that matches any of `words` as whole words.  Sort
    longest-first so multi-word names take precedence over their components."""
    if not words:
        return None
    sorted_words = sorted(words, key=len, reverse=True)
    return re.compile(r"\b(?:" + "|".join(re.escape(w) for w in sorted_words) + r")\b")


# Generic names: case-insensitive
_GENERIC_RE = re.compile(
    r"\b(?:" + "|".join(re.escape(g) for g in
                        sorted(_GENERIC_LOOKUP, key=len, reverse=True)) + r")\b",
    re.IGNORECASE,
) if _GENERIC_LOOKUP else None

# Brand names: case-sensitive (brand names are capitalised; lower-case noise
# words could otherwise false-positive)
_BRAND_RE = _compile_alternation(list(_BRAND_LOOKUP)) if _BRAND_LOOKUP else None

# First-word-indexed equivalents of the two patterns above. See
# pearls/_matcher.py: the alternations are O(text x alternatives) and
# these are O(text), which is what lets the database keep growing. The
# regexes stay for the equivalence test in tests/test_matcher.py.
_GENERIC_MATCHER = (_matcher.PhraseMatcher(list(_GENERIC_LOOKUP))
                    if _GENERIC_LOOKUP else None)
_BRAND_MATCHER = (_matcher.PhraseMatcher(list(_BRAND_LOOKUP), case_sensitive=True)
                  if _BRAND_LOOKUP else None)


def resolve(text: str) -> list:
    """Find drug mentions in `text`. Returns a list of dicts:
        {name, summary, url, case_sensitive}
    name preserves the case as it appeared in the text for brand matches and
    uses the canonical generic spelling for generic matches.
    """
    if not text:
        return []
    out = []
    seen: set = set()

    if _GENERIC_MATCHER:
        for _s, _e, key in _GENERIC_MATCHER.find(text):
            if key in seen:
                continue
            d = _GENERIC_LOOKUP.get(key)
            if not d:
                continue
            seen.add(key)
            out.append({
                "name":           d["generic"],
                "summary":        d["summary"],
                "url":            _drugbank_url(d),
                "case_sensitive": False,
            })

    if _BRAND_MATCHER:
        for _s, _e, brand in _BRAND_MATCHER.find(text):
            if brand in seen:
                continue
            d = _BRAND_LOOKUP.get(brand)
            if not d:
                continue
            seen.add(brand)
            out.append({
                "name":           brand,
                "summary":        d["summary"],
                "url":            _drugbank_url(d),
                "case_sensitive": True,
            })

    return out
