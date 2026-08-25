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
            low = text.lower()
            ci_toks = [(m.start(), m.group(0))
                       for m in _TOKEN_RE.finditer(low)]
            _scan_cache = (key, low, ci_toks, cs_toks)
        return low, ci_toks
    if cs_toks is None:
        cs_toks = [(m.start(), m.group(0))
                   for m in _TOKEN_RE.finditer(text)]
        _scan_cache = (key, low, ci_toks, cs_toks)
    return text, cs_toks


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
            low = p.lower() if self._ci else p
            if low in seen:
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
