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

Semantics were deliberately identical to the regex being replaced, not
merely similar:

  * matching is case-insensitive;
  * at any position the longest candidate wins, which is why the regex
    sorted alternatives longest-first;
  * matches cannot overlap - scanning resumes after the match, as
    `finditer` does;
  * a phrase edge that is a word character must fall on a `\\b`
    boundary.

The last of those is where this deliberately stopped being identical.
`\\b(?:...)\\b` also asserts a boundary at an edge made of
punctuation, and a boundary there means a WORD character on the far
side - so "Vitamin B12 (cobalamin)" and the 22 other library terms
ending in ")" matched only at the very end of a text, and a phrase
opening with punctuation could not match at all. The assertion is now
made at word-character edges only, which is what `\\b` was standing in
for.

The remaining properties were verified against the original alternation
over every string in the shipped library before the alternations were
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
# Every space a card can put between two words of a phrase. Anki's
# editor emits `&nbsp;` on almost every space you type after another
# space, and `_strip_html` decodes that to U+00A0 before resolution sees
# it - so "ectopic pregnancy" was indexed with an ASCII space, the card
# read `ectopic\u00a0pregnancy`, and `startswith` failed. The term
# resolved on no card written that way, which is most of them.
#
# These all fold to a plain space, and every one is a single character,
# so the haystack keeps its length and `find`'s offsets keep addressing
# the original text. That is the whole reason this is a translate table
# and not a `replace` of the `&nbsp;` entity.
_MATCH_SPACES = {
    0x00A0: " ",   # no-break space, what &nbsp; decodes to
    0x2007: " ",   # figure space
    0x202F: " ",   # narrow no-break space
    0x2009: " ",   # thin space
    0x2002: " ",   # en space
    0x2003: " ",   # em space
    0x200B: " ",   # zero-width space, seen in pasted text
    0xFEFF: " ",   # zero-width no-break space (BOM), likewise
}

_FOLD_TABLE = str.maketrans({**_APOSTROPHES, **_MATCH_SPACES})


def fold_for_match(s: str) -> str:
    """Normalise apostrophes and exotic spaces, preserving length.

    Length matters: `find` returns offsets into the folded haystack and
    `surface_form` slices the ORIGINAL text with them, so a fold that
    changed length would hand back a mis-aligned span.
    """
    return s.translate(_FOLD_TABLE)


# The old name, kept because it is the one the comments elsewhere use.
fold_apostrophes = fold_for_match


def surface_form(text: str, start: int, end: int, phrase: str,
                 ci: bool = True):
    """The characters `find` matched, exactly as the reader wrote them.

    `find` returns offsets into a haystack that, in case-insensitive
    mode, is `text` lower-cased and apostrophe-folded. Folding preserves
    length; `str.lower()` does not for every code point - U+0130
    lower-cases to two - so on a text carrying one of those the offsets
    address the haystack and not the original, and the slice would be a
    character or two out. Returns None in that case rather than hand
    back a mis-aligned span, so a caller can fall back to the name it
    would have shown before.

    Callers want this because the highlighter has to mark the words on
    the card, not the primary name of whatever those words resolve to:
    a card that says "heart attack" and never says "myocardial
    infarction" has nothing for the primary name to match.
    """
    got = text[start:end]
    if not ci:
        return got
    return got if fold_for_match(got.lower()) == phrase else None


# A space in a library term has to match whatever the card actually
# puts between those two words. Anki's editor inserts `&nbsp;` on almost
# every keystroke that follows a space, so the card path (raw HTML) sees
# the entity and the dock path (decoded text) sees U+00A0 - and a plain
# escaped space matched neither. "ectopic pregnancy" is in the library
# and did not underline on a card reading `an ectopic&nbsp;pregnancy`.
#
# Written as a class rather than by normalising the text, because the
# highlighter substitutes back into the ORIGINAL string: rewriting the
# text to match would move every offset after it.
_SEP = r"(?:\s|&nbsp;|&#160;|&#xa0;|\u00a0)+"
_SEP_RE = re.compile(_SEP)


def normalise_separators(text: str) -> str:
    """Collapse whatever separated two words back to a single space.

    The inverse of `escape_phrase`: that lets a term's space match an
    `&nbsp;` entity or a Unicode space in the card, and this turns such
    a match back into the form the lookup tables are keyed on. Length is
    NOT preserved, so this is only for building a dictionary key, never
    for anything that carries an offset.
    """
    return " ".join(_SEP_RE.split(fold_for_match(text)))


def escape_phrase(phrase: str) -> str:
    """`re.escape`, but a run of spaces matches any real-world separator.

    Splitting on whitespace and rejoining also means a term written with
    two spaces, or with a newline where the card wrapped, still matches.
    """
    parts = [re.escape(p) for p in phrase.split()]
    if not parts:
        return re.escape(phrase)
    return _SEP.join(parts)


def alternation(alts) -> str:
    """A pattern matching any of `alts`, each at the boundaries it needs.

    `alts` is a sequence of `(phrase, escaped)` pairs in the order the
    engine should try them. `escaped` is the regex source for that
    phrase, which lets a caller wrap one alternative in `(?i:...)`
    without making the whole pattern case-insensitive.

    Boundaries first. `\\b(?:...)\\b` asserts a boundary at both ends
    of whichever alternative matched, and a boundary beside punctuation
    means a WORD character on the far side - so "Vitamin B12
    (cobalamin)" and the 22 other library terms ending in ")" matched
    only at the very end of a text, and a phrase opening with
    punctuation could not match at all. The assertion belongs at
    word-character edges only, which is what `\\b` was standing in for.

    Then speed, because this is compiled per text node and run over
    every one of them. The trailing assertion has to be
    per-alternative: whether a form needs one is a property of that
    form, which is the whole point. The leading one does not, and
    hoisting it is worth real time - `re` derives a first-character set
    for a plain alternation and uses it to skip positions the pattern
    cannot start at, and a lookbehind at the head of every branch is
    what defeats that. Measured on a 1 KB node of clinical prose: 16 us
    hoisted against 69 us repeated. Hoisting is only sound while every
    alternative opens on a word character, which every term in the
    library does; a user-defined term that opens on punctuation drops
    the pattern back to per-alternative boundaries.
    """
    alts = list(alts)
    if not alts:
        return ""
    tails = [esc + (r"(?!\w)" if _is_word(phrase[-1:]) else "")
             for phrase, esc in alts]
    if all(_is_word(phrase[:1]) for phrase, _esc in alts):
        return r"(?<!\w)(?:" + "|".join(tails) + ")"
    return "|".join(
        (r"(?<!\w)" if _is_word(phrase[:1]) else "") + tail
        for (phrase, _esc), tail in zip(alts, tails))


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
            low = fold_for_match(text.lower())
            ci_toks = [(m.start(), m.group(0))
                       for m in _TOKEN_RE.finditer(low)]
            _scan_cache = (key, low, ci_toks, cs_toks)
        return low, ci_toks
    if cs_toks is None:
        folded = fold_for_match(text)
        cs_toks = [(m.start(), m.group(0))
                   for m in _TOKEN_RE.finditer(folded)]
        _scan_cache = (key, low, ci_toks, cs_toks)
        return folded, cs_toks
    return fold_for_match(text), cs_toks


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
        fold_for_match(str(p).strip().lower())
        for p in (phrases or ()) if str(p).strip())


class PhraseMatcher:
    """Case-insensitive, longest-wins, non-overlapping phrase finder."""

    __slots__ = ("_by_first", "_odd_re", "_ci")

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
        for p in phrases:
            if not p:
                continue
            low = fold_for_match(p.lower() if self._ci else p)
            if low in seen:
                continue
            # Case-sensitive matchers keep `low` cased, so fold again
            # rather than comparing a brand name against a lower-cased
            # blocklist and missing it.
            if _BLOCKED and low.lower() in _BLOCKED:
                continue
            seen.add(low)
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
        # Per-alternative boundaries rather than one `\b(?:...)\b`
        # around the lot. Every phrase that lands here opens with
        # punctuation - that is what disqualified it from the index -
        # so a leading `\b` would have required a word character in
        # front of it, and the fallback could never have fired at all.
        # `alternation` asserts a boundary only at the edges where the
        # phrase's own characters do not already provide one.
        self._odd_re = (
            re.compile(alternation((o, escape_phrase(o)) for o in odd),
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
                # Closing `\b`, but only where a phrase ending in a word
                # character needs one: the next character of the text
                # must then be a non-word character, or the text must
                # end. A phrase whose own last character is punctuation
                # separates itself from whatever follows, and demanding
                # a `\b` there demanded the opposite - a word character
                # straight after the punctuation. That is what confined
                # the 23 library terms ending in ")" to matching at the
                # very end of a card: "Vitamin B12 (cobalamin) is low"
                # matched nothing, "his Vitamin B12 (cobalamin)" did.
                # The opening boundary is free - `start` is a token
                # start, so what precedes it is never a word character.
                if ends_word and end < n:
                    nxt = low[end]
                    if nxt.isalnum() or nxt == "_":
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
