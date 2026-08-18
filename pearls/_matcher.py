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

`verify_against_regex` exercises exactly those properties against the
original pattern, and the test suite runs it over the real databases.
"""

import re

# Tokens that can open a phrase. `\w` plus the intra-word punctuation
# that appears in drug and condition names, so "beta-blocker" is found
# from its "beta" token and "Crohn's" from "Crohn".
_TOKEN_RE = re.compile(r"\w+", re.UNICODE)

_WORD_RE = re.compile(r"\w", re.UNICODE)


def _is_word(ch: str) -> bool:
    return bool(ch) and _WORD_RE.match(ch) is not None


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
            by_first.setdefault(m.group(0), []).append(low)

        # Longest first within each bucket reproduces the alternation
        # order the regex relied on.
        for k in by_first:
            by_first[k].sort(key=len, reverse=True)

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
        low = text.lower() if self._ci else text
        n = len(low)
        by_first = self._by_first
        pos = 0
        for tok in _TOKEN_RE.finditer(low):
            start = tok.start()
            if start < pos:
                # Inside a phrase already matched; skip without re-testing.
                continue
            bucket = by_first.get(tok.group(0))
            if not bucket:
                continue
            for cand in bucket:
                end = start + len(cand)
                if end > n or low[start:end] != cand:
                    continue
                # Closing `\b`: a boundary exists when the last character
                # of the phrase and the next character of the text differ
                # in word-ness. The opening boundary is free - `start` is
                # a token start, so what precedes it is never a word
                # character.
                nxt = low[end] if end < n else ""
                if _is_word(cand[-1]) == _is_word(nxt) and nxt:
                    continue
                out.append((start, end, cand))
                pos = end
                break

        if self._odd_re is not None:
            for m in self._odd_re.finditer(text):
                out.append((m.start(), m.end(),
                            m.group(0).lower() if self._ci else m.group(0)))
            out.sort()
        return out


def verify_against_regex(matcher: "PhraseMatcher", pattern, texts) -> list:
    """Return a list of disagreements between `matcher` and `pattern`.

    `pattern` must have been built from the same phrase list with the
    same case sensitivity, or the comparison is meaningless.

    Used by the test suite rather than at runtime. An empty list means
    the fast path is returning exactly what the regex returned, which is
    the only claim that makes this a safe substitution.
    """
    problems = []
    for text in texts:
        ci = matcher._ci
        want = [(m.start(), m.end(),
                 m.group(0).lower() if ci else m.group(0))
                for m in pattern.finditer(text)]
        got = sorted(matcher.find(text))
        if want != got:
            problems.append({"text": text[:120], "regex": want, "matcher": got})
    return problems
