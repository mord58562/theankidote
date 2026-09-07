# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""
TheAnkiDote.pearls._matcher - find many fixed phrases in one pass.

The condition and drug databases were each matched with a single
compiled regex of the form `\\b(?:name1|name2|...|nameN)\\b`, built by
joining several thousand escaped alternatives sorted longest-first.
That is correct and it is what `re` is worst at: the engine has no
alternation index, so at every position in the text it walks the
alternative list until one matches or all fail. Cost is O(text x
alternatives), which measured at 10.4 ms per card for conditions and
6.5 ms for drugs - about 17 ms added to every question and every
answer, on top of everything else a card render does.

This replaces the alternation with a first-word index. Phrases are
grouped by their opening word; the text is tokenised once; each token
is looked up in the index and only that handful of candidates is
checked. Cost becomes O(text + matches), independent of database size,
so the databases can keep growing - which is the point, given 2.0
expands them - without the reviewer getting slower.

Semantics are deliberately identical to the regex being replaced, not
merely similar:

  * matching is case-insensitive;
  * at any position the longest candidate wins, which is why the regex
    sorted alternatives longest-first;
  * matches cannot overlap - scanning resumes after the match, as
    `finditer` does;
  * both ends must fall on a `\\b` boundary, including the awkward case
    of a phrase that starts or ends with a non-word character.

Those properties were verified against the original alternation over
every string in the shipped library before the alternations were
deleted at 2.2. `verify_against_regex` went with them: it existed
only for that comparison, and there is no longer a second
implementation to compare against.
"""

import re
from operator import itemgetter

# Tokens that can open a phrase. `\w` plus the intra-word punctuation
# that appears in drug and condition names, so "beta-blocker" is found
# from its "beta" token and "Crohn's" from "Crohn".
_TOKEN_RE = re.compile(r"\w+", re.UNICODE)

_WORD_RE = re.compile(r"\w", re.UNICODE)


def _is_word(ch: str) -> bool:
    return bool(ch) and _WORD_RE.match(ch) is not None


# One card is scanned by eight matchers in a row - conditions, generics,
# brands, acronyms, preclinical, descriptive, psych, signs - and each was
# lower-casing and re-tokenising the same string. Tokenising dominates
# `find`, so seven eighths of that work was thrown away. This is a
# single-entry cache of the last text scanned, which is exactly the
# access pattern: one card, eight consecutive lookups, then the next
# card evicts it.
#
# Case-sensitive matchers cannot share the case-insensitive token list.
# `str.lower()` is not length-preserving in Unicode - U+0130 lowercases
# to two code points - so offsets taken from the lower-cased text do not
# address the original. The two token lists are kept separately and both
# are built lazily, so a card that only hits case-insensitive matchers
# never tokenises twice.
#
# The cache is one tuple, replaced wholesale rather than field by field.
# Rebinding a module global is atomic under the GIL, so a reader either
# sees the whole previous entry or the whole new one, never a token list
# belonging to a different text.
_scan_cache: tuple = (None, None, None, None)


# Apostrophe folding.
#
# Card authors type with whatever their editor produces, and on macOS
# that is the typographic apostrophe U+2019. Every library term uses the
# ASCII U+0027, so "Addison’s disease" - which is how nine cards in
# the test collection actually write it - matched none of the 107 terms
# in the library that contain an apostrophe. The failure was invisible:
# no error, just a popup that never appeared.
#
# Folded on both sides, at index time and at scan time. Every variant is
# a single character, so offsets into the original text are unchanged
# and the highlighter still spans the right characters.
_APOSTROPHES = {
    "\u2019": "'",   # right single quotation mark
    "\u2018": "'",   # left single quotation mark
    "\u02bc": "'",   # modifier letter apostrophe
    "\u00b4": "'",   # acute accent, used as an apostrophe by some editors
    "\u2032": "'",   # prime
}
_APOSTROPHE_TABLE = str.maketrans(_APOSTROPHES)


def fold_apostrophes(s: str) -> str:
    """Normalise every apostrophe variant to ASCII, preserving length."""
    return s.translate(_APOSTROPHE_TABLE)


def _scan(text: str, ci: bool):
    """Return `(haystack, tokens)` for `text`, reusing the last scan.

    `tokens` is a list of `(start, token)`. `haystack` is the string the
    offsets address: the lower-cased text when `ci`, otherwise `text`.
    """
    global _scan_cache
    key, low, ci_toks, cs_toks = _scan_cache
    if key is not text and key != text:
        key, low, ci_toks, cs_toks = text, None, None, None
    if ci:
        if ci_toks is None:
            low = fold_apostrophes(text.lower())
            ci_toks = [(m.start(), m.group(0))
                       for m in _TOKEN_RE.finditer(low)]
            _scan_cache = (key, low, ci_toks, cs_toks)
        return low, ci_toks
    if cs_toks is None:
        folded = fold_apostrophes(text)
        cs_toks = [(m.start(), m.group(0))
                   for m in _TOKEN_RE.finditer(folded)]
        _scan_cache = (key, low, ci_toks, cs_toks)
        return folded, cs_toks
    return fold_apostrophes(text), cs_toks


_BLOCKED: frozenset = frozenset()


def set_blocklist(phrases) -> None:
    """Install the phrases that must never match, whatever offers them.

    A term that fires on the wrong word - "OR" read as operating theatre
    inside ordinary "or", an alias that turns out to name two different
    things - is the most visible defect this add-on has, and every one
    of them was fixed by editing a set in Python and cutting an AnkiWeb
    release. The list is data, so it travels on the content channel
    instead and `_library` installs it before any vocabulary module
    reaches its `PhraseMatcher(...)` line.

    Suppression is all this can do. A blocklist switches a popup off; it
    cannot add one, retarget one, or alter a word of any summary. So a
    content host that is wrong, or in the wrong hands, costs a user a
    feature and cannot reach past that - which is what makes shipping it
    remotely worth doing at all.
    """
    global _BLOCKED
    _BLOCKED = frozenset(
        fold_apostrophes(str(p).strip().lower())
        for p in (phrases or ()) if str(p).strip())


class PhraseMatcher:
    """Case-insensitive, longest-wins, non-overlapping phrase finder."""

    __slots__ = ("_by_first", "_odd_re", "_max_len", "_ci")

    def __init__(self, phrases, case_sensitive: bool = False):
        """`phrases` is any iterable of strings.

        With `case_sensitive` false (the default) duplicates differing
        only by case are collapsed, matching the de-duplication callers
        already did before building their regex. Brand names are matched
        case-sensitively - they are capitalised, and lower-casing them
        turns ordinary words into false positives - so that mode keeps
        the phrases exactly as given.
        """
        self._ci = not case_sensitive
        by_first: dict = {}
        odd: list = []
        seen: set = set()
        max_len = 0
        for p in phrases:
            if not p:
                continue
            low = fold_apostrophes(p.lower() if self._ci else p)
            if low in seen:
                continue
            # Case-sensitive matchers keep `low` cased, so fold again
            # rather than comparing a brand name against a lower-cased
            # blocklist and missing it.
            if _BLOCKED and low.lower() in _BLOCKED:
                continue
            seen.add(low)
            max_len = max(max_len, len(low))
            m = _TOKEN_RE.match(low)
            if m is None or m.start() != 0:
                # Starts with punctuation, so no token boundary opens it.
                # Rare enough to leave to a regex; keeping them out of the
                # index is what lets the fast path assume a word start.
                odd.append(p)
                continue
            # Length and terminal word-ness are properties of the phrase,
            # not of the text, so they are computed once here rather than
            # per candidate per position in `find`. That is what the
            # closing-boundary test needs, and recomputing it in the loop
            # was most of the loop's cost.
            end_ch = low[-1]
            by_first.setdefault(m.group(0), []).append(
                (low, len(low), end_ch.isalnum() or end_ch == "_"))

        # Longest first within each bucket reproduces the alternation
        # order the regex relied on. `itemgetter` rather than a lambda:
        # the key is called once per element and this runs at import for
        # every vocabulary, so the interpreter round trip is not free.
        _by_len = itemgetter(1)
        for bucket in by_first.values():
            bucket.sort(key=_by_len, reverse=True)

        self._by_first = by_first
        self._max_len = max_len
        self._odd_re = (
            re.compile(r"\b(?:" + "|".join(re.escape(o) for o in odd) + r")\b",
                       re.IGNORECASE if self._ci else 0)
            if odd else None
        )

    def find(self, text: str):
        """Return `(start, end, matched_phrase)` tuples in text order.

        The phrase is lower-cased in case-insensitive mode, so callers
        can use it as a lookup key directly; in case-sensitive mode it
        is the text as matched.

        A list rather than a generator, because the punctuation-initial
        fallback below is a separate scan and its results have to be
        merged back into position order - callers rely on encounter
        order. No current database has such a phrase, so the merge is
        skipped entirely in practice.
        """
        out: list = []
        if not text:
            return out
        low, tokens = _scan(text, self._ci)
        n = len(low)
        by_first_get = self._by_first.get
        append = out.append
        starts_with = low.startswith
        pos = 0
        for start, tok in tokens:
            if start < pos:
                # Inside a phrase already matched; skip without re-testing.
                continue
            bucket = by_first_get(tok)
            if not bucket:
                continue
            for cand, clen, ends_word in bucket:
                end = start + clen
                # `startswith` with an offset compares in place; slicing
                # allocated a throwaway string for every candidate tried,
                # and most candidates are tried only to be rejected.
                if end > n or not starts_with(cand, start):
                    continue
                # Closing `\b`: a boundary exists when the last character
                # of the phrase and the next character of the text differ
                # in word-ness. End of text is always a boundary. The
                # opening boundary is free - `start` is a token start, so
                # what precedes it is never a word character.
                if end < n:
                    nxt = low[end]
                    if ends_word == (nxt.isalnum() or nxt == "_"):
                        continue
                append((start, end, cand))
                pos = end
                break

        if self._odd_re is not None:
            for m in self._odd_re.finditer(text):
                out.append((m.start(), m.end(),
                            m.group(0).lower() if self._ci else m.group(0)))
            out.sort()
        return out
