# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.

"""Reviewer integration: marking up card text as it is shown.

Two-phase highlighting:
  Phase 1 (synchronous): card_will_show hook injects sp-mark spans + CSS
    directly into the card HTML string if results are already cached.
    This is guaranteed to render - no timing/CSP issues.
  Phase 2 (async fallback): when NCBI results arrive for the first time,
    web.eval() injects the marker code into the live DOM.
"""
import json
import os
import re
import time
from bisect import bisect_right
from html.parser import HTMLParser
from typing import Any

from aqt import mw, gui_hooks

from .. import _config, _log
from . import (_acronyms, _drugs, _conditions, _matcher, _preclinical,
               _descriptive, _psych, _signs)


# ── User-defined custom terms ─────────────────────────────────────────
#
# `customTerms` config key is a string holding a JSON array.  Each entry
# is a {title, summary, url, case_sensitive?} dict.  Parsed lazily on
# first read and cached - if the user updates the config we re-parse
# on the next request.

_custom_terms_cache: list = []
_custom_terms_raw: "str | None" = "<unset>"  # sentinel different from None


def _custom_terms() -> list:
    global _custom_terms_cache, _custom_terms_raw
    raw = _config.get("customTerms")
    if raw == _custom_terms_raw:
        return _custom_terms_cache
    _custom_terms_raw = raw
    _custom_terms_cache = []
    if not raw or not isinstance(raw, str):
        return _custom_terms_cache
    try:
        parsed = json.loads(raw)
    except Exception as exc:
        _log.warn(f"customTerms JSON parse failed: {exc}")
        return _custom_terms_cache
    if not isinstance(parsed, list):
        return _custom_terms_cache
    out = []
    for entry in parsed:
        if not isinstance(entry, dict):
            continue
        title = (entry.get("title") or "").strip()
        url = (entry.get("url") or "").strip()
        if not title or not url:
            continue
        if not (url.startswith("http://") or url.startswith("https://")):
            continue
        out.append({
            "title": title,
            "_article": entry.get("article") or title,
            "url": url,
            "summary": (entry.get("summary") or "").strip(),
            "source": entry.get("source") or "custom",
            "link": "article",
            "label": (entry.get("label") or "").strip(),
            # Explicit, not omitted. `_span` reads this key and falls
            # back to "[]" when it is absent, which is the same value
            # a real empty list gives - so a builder that simply forgot
            # it looked identical to one that meant it. That is how
            # `utd` was lost twice and `link` once. This database has
            # no UpToDate chips; saying so is the point.
            "utd": [],
            # The popup button's destination when this entry has no
            # chapter of its own. Only conditions carry one today; the
            # others say so explicitly rather than by omission, which is
            # the distinction that cost `utd` twice.
            "ref": [],
            "case_sensitive": bool(entry.get("case_sensitive")),
            "user_defined": True,
        })
    _custom_terms_cache = out
    return out

try:
    from aqt.reviewer import Reviewer
except Exception:
    Reviewer = None  # type: ignore[assignment,misc]

_ADDON_PKG  = __name__.split(".")[0]


def _marker_fingerprint() -> str:
    """Short content hash of web/marker.js, used to bust the webview cache.

    marker.js is delivered to the reviewer as `<script src=...>` from
    Anki's media server, and that URL was byte-identical in every
    release. QtWebEngine caches by URL, so an install that had already
    fetched the file kept running its cached copy across upgrades - the
    add-on's Python side updated, the JavaScript side did not. That is
    why bullet rendering, added in preview 9, appeared not to work at
    all: the logic, the data and the CSS were all correct, and the
    reviewer was simply executing an older marker.js.

    Hashing the file rather than the manifest version means the URL also
    changes between builds of the same version, so editing marker.js
    during development takes effect on the next card instead of after a
    profile-wide cache clear.
    """
    try:
        import hashlib
        path = os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), "web", "marker.js")
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()[:12]
    except Exception:
        # Never fatal: a timestamp still busts the cache, it just does so
        # on every restart rather than only when the file changes.
        return str(int(time.time()))


_SCRIPT_URL = f"/_addons/{_ADDON_PKG}/web/marker.js?v={_marker_fingerprint()}"

# ── module-level state ────────────────────────────────────────────────────────

# `_on_answer` and `_current_card` used to live here too, set on every
# question and answer "for Phase 2 use". Three writes each, no reads,
# and Phase 2 never arrived. Same class as `_articles_dismissed`.
_panel_ref    = None
_prev_card_id: "int | None" = None  # for detecting card progression vs flip


def set_panel(panel) -> None:
    global _panel_ref
    _panel_ref = panel


# ── card text extraction ──────────────────────────────────────────────────────



class _Stripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self._buf = []
    def handle_data(self, d):
        self._buf.append(d)
    def result(self):
        return " ".join(self._buf)


_WS_RE      = re.compile(r"\s+")
_TAG_RE     = re.compile(r"<[^>]+>")
# Matches any sp-mark span we previously injected - used for self-healing.
_SP_MARK_RE = re.compile(r'<span class="sp-mark"[^>]*>(.*?)</span>', re.DOTALL)


def _strip_sp_marks(html: str) -> str:
    """Remove any existing sp-mark spans, keeping their text content."""
    return _SP_MARK_RE.sub(r'\1', html)


def _strip_html(html: str) -> str:
    s = _Stripper()
    try:
        s.feed(html)
        return _WS_RE.sub(" ", s.result()).strip()
    except Exception:
        return _TAG_RE.sub("", html).strip()


def _card_text(card) -> str:
    """Plain-text concatenation of all note fields, stripped of HTML.
    Cached on the card object so multiple consumers (query builder, acronym
    resolver) don't repeatedly re-strip.

    A plain string is passed straight through. Every term builder below
    starts by calling this, so accepting a string is what lets the
    reference dock reuse all five of them on page text rather than on a
    card - see `highlight_text`.
    """
    if isinstance(card, str):
        return card
    cached = getattr(card, "_ap_text", None)
    if cached is not None:
        return cached
    try:
        text = " ".join(_strip_html(v) for v in card.note().values() if v.strip())
    except Exception:
        text = ""
    try:
        card._ap_text = text
    except Exception:
        pass
    return text


def _term_search_url(term: str) -> str:
    """In-book StatPearls search URL, via the one in `_conditions`.

    This was a second copy that had drifted: it never applied
    `_us_spelling`, and it is the builder used for acronym-expansion
    searches. So expanding an acronym to an Australian spelling sent
    "oesophageal varices" to a database that only indexes "esophageal",
    which is the exact failure `_us_spelling` was written to prevent -
    fixed at one of the two copies and not the other.
    """
    return _conditions._term_search_url(term)


_AE_E_SWAPS = [
    # American -> British (the primary names in _conditions.py use
    # British spelling, so we normalise expansions toward British).
    ("hematolog",   "haematolog"),
    ("hemoglob",    "haemoglob"),
    ("hemorrh",     "haemorrh"),
    ("hemochrom",   "haemochrom"),
    ("hemophil",    "haemophil"),
    ("hematuria",   "haematuria"),
    ("hematemesis", "haematemesis"),
    ("hematoma",    "haematoma"),
    ("anemia",      "anaemia"),
    ("leukemia",    "leukaemia"),
    ("leukocyte",   "leucocyte"),
    ("edema",       "oedema"),
    ("esophag",     "oesophag"),
    ("pediatric",   "paediatric"),
    ("dyspnea",     "dyspnoea"),
    ("diarrhea",    "diarrhoea"),
    ("tumor",       "tumour"),
    ("color",       "colour"),
    ("fetal",       "foetal"),
    ("fetus",       "foetus"),
]


def _nesting_guard(am: str, br: str):
    """A regex matching `am` except where it is already part of `br`.

    Two of the pairs above nest: "oedema" contains "edema" and
    "oesophag" contains "esophag". A plain `str.replace` therefore
    rewrote text that was already British, and
    `_normalise_for_lookup("Pulmonary oedema")` came back as "pulmonary
    ooedema" - a key that can match nothing. It never showed, because
    the un-normalised form is looked up first and hits, but it is a
    lookup that could only ever miss. The lookbehind is whatever the
    British form puts in front of the American one, so the same
    construction covers any later pair that nests the same way.
    """
    at = br.find(am)
    lead = re.escape(br[:at]) if at > 0 else ""
    return re.compile((f"(?<!{lead})" if lead else "") + re.escape(am))


_AE_E_RE = [(am, br, _nesting_guard(am, br)) for am, br in _AE_E_SWAPS]


def _normalise_for_lookup(s: str) -> str:
    """Lowercase + American->British spelling normalisation so acronym
    expansions like 'Acute Lymphoblastic Leukemia' match the condition
    entry 'Acute lymphoblastic leukaemia'."""
    n = (s or "").strip().lower()
    for am, br, rx in _AE_E_RE:
        # The substring test is the cheap gate; the regex only runs when
        # there is something to rewrite.
        if am in n:
            n = rx.sub(br, n)
    return n


def _acronym_to_condition(expansion: str):
    """If `expansion` matches a known condition's primary name or any
    of its aliases, return that condition entry; otherwise None.

    Used to give acronym popups a richer body: instead of the acronym's
    own short description we render the matched condition's full
    summary (Sx / Ix / Mx / Ddx). The popup title already reads
    'ACRONYM - full name', so the body starts straight into the
    condition rather than restating the expansion a second time.

    Spelling-tolerant: tries direct lookup first, then a normalised
    form swapping American spelling to British (the primary form used
    in _conditions.py) so e.g. ALL ('Acute Lymphoblastic Leukemia')
    matches the British 'Acute lymphoblastic leukaemia' entry.
    """
    if not expansion:
        return None
    lookup = getattr(_conditions, "_LOOKUP", None)
    if lookup is None:
        return None
    direct = lookup.get(expansion.strip().lower())
    if direct is not None:
        return direct
    return lookup.get(_normalise_for_lookup(expansion))


def _acronym_terms(card) -> list:
    """Resolve medical acronyms in card text → highlight terms.
    Acronym matches are case-sensitive to avoid false positives like 'pe' in
    English prose - only the uppercase form gets underlined.

    Smart enrichment: if the acronym's expansion matches a known condition
    (e.g. MI -> 'Myocardial infarction'), the popup shows the CONDITION's
    full summary instead of the acronym's short description. The title
    ('MI - Myocardial infarction') already carries the expansion, so the
    body doesn't restate it. Falls back to the acronym's own description
    when no matching condition exists (lab-value / instrument acronyms
    etc.)."""
    text = _card_text(card)
    if not text:
        return []
    out = []
    for it in _acronyms.resolve(text):
        cond = _acronym_to_condition(it["expansion"])
        if cond is not None:
            out.append({
                "title":      it["acronym"],
                "_article":   f'{it["acronym"]} - {cond["name"]}',
                "_expansion": it["expansion"],
                "url":        _conditions._url_for(cond),
                "summary":    (cond.get("summary", "") or "").strip(),
                # Both of these come from the condition, and both were
                # being invented here instead. `source` was the literal
                # "statpearls" even where `_url_for` had just returned an
                # UpToDate link, and `utd` was absent altogether - so
                # `data-sp-utd` was "[]" and marker.js hid the chip row
                # on all 169 acronym expansions whose condition carries
                # chips. Same dropped-key shape as `link` in
                # `_build_pattern` and `utd` in `_condition_terms`: the
                # data existed, the dict in the middle did not carry it.
                "source":     ("uptodate"
                               if cond.get("source") == "uptodate"
                               and cond.get("utd") else "statpearls"),
                "link":       _conditions._link_kind(cond),
                "utd":        _conditions.utd_chips(cond),
                # The popup button's destination when this entry has no
                # chapter of its own. Only conditions carry one today; the
                # others say so explicitly rather than by omission, which is
                # the distinction that cost `utd` twice.
                "ref": [],
                "case_sensitive": True,
            })
            continue
        out.append({
            "title":      it["acronym"],
            "_article":   f'{it["acronym"]} - {it["expansion"]}',
            "_expansion": it["expansion"],       # used by _upgrade_acronym_urls
            "url":        _term_search_url(it["expansion"]),
            "summary":    it["description"],
            "source":     "statpearls",
            "link":       "search",
            # Explicit, not omitted. `_span` reads this key and falls
            # back to "[]" when it is absent, which is the same value
            # a real empty list gives - so a builder that simply forgot
            # it looked identical to one that meant it. That is how
            # `utd` was lost twice and `link` once. This database has
            # no UpToDate chips; saying so is the point.
            "utd": [],
            # The popup button's destination when this entry has no
            # chapter of its own. Only conditions carry one today; the
            # others say so explicitly rather than by omission, which is
            # the distinction that cost `utd` twice.
            "ref": [],
            "case_sensitive": True,
        })
    return out


def _drug_terms(card) -> list:
    """Resolve drug names in card text → highlight terms.
    Brand names are matched case-sensitively (they're capitalised), generics
    case-insensitively.  Clicking opens the DrugBank page in the sidebar."""
    text = _card_text(card)
    if not text:
        return []
    out = []
    for it in _drugs.resolve(text):
        out.append({
            "title":          it["name"],
            "_article":       it["name"],
            "url":            it.get("url", ""),
            "summary":        it["summary"],
            "source":         "drugbank",
            "link":           it.get("link", "search"),
            # The spellings this card used. `title` is the INN generic
            # and is what the popup is headed with; these are what the
            # pattern underlines, so a card written in `frusemide` gets
            # `frusemide` marked rather than nothing at all.
            "_surfaces":      it.get("surfaces") or [],
            # Explicit, not omitted. `_span` reads this key and falls
            # back to "[]" when it is absent, which is the same value
            # a real empty list gives - so a builder that simply forgot
            # it looked identical to one that meant it. That is how
            # `utd` was lost twice and `link` once. This database has
            # no UpToDate chips; saying so is the point.
            "utd": [],
            # The popup button's destination when this entry has no
            # chapter of its own. Only conditions carry one today; the
            # others say so explicitly rather than by omission, which is
            # the distinction that cost `utd` twice.
            "ref": [],
            "case_sensitive": it.get("case_sensitive", False),
        })
    return out


def _condition_terms(card) -> list:
    """Resolve common medical conditions in card text → highlight terms.
    Each links to a StatPearls article so the user can open the full chapter
    even when the auto-search returned a slightly different article."""
    text = _card_text(card)
    if not text:
        return []
    out = []
    for it in _conditions.resolve(text):
        out.append({
            "title":          it["name"],
            "_article":       it["name"],
            "url":            it["url"],
            "summary":        it["summary"],
            "source":         it.get("source") or "statpearls",
            "link":           it.get("link", "search"),
            # The third key this dict has dropped, after `link` above and
            # for the same reason: `_conditions.resolve` builds the chips,
            # `_build_pattern` JSON-encodes whatever is under this key, and
            # `_span` writes it to `data-sp-utd` - but this dict sits
            # between them and did not carry it. `data-sp-utd` was always
            # "[]", so marker.js hid the UpToDate row on every popup. 824
            # of the 826 conditions in the library carry chips; none of
            # them have ever been drawn.
            "utd":            it.get("utd") or [],
            # The popup button's destination when this entry has no
            # chapter of its own. Only conditions carry one today; the
            # others say so explicitly rather than by omission, which is
            # the distinction that cost `utd` twice.
            "ref": it.get("ref") or [],
            # The alias the card was written in, which is what has to be
            # underlined. `title` stays the primary name so the popup is
            # unchanged - but it is also what the pattern was built from,
            # and 5,457 of the library's 6,044 aliases do not contain
            # their primary name, so "heart attack" resolved Myocardial
            # infarction and then marked nothing.
            "_surfaces":      it.get("surfaces") or [],
            "case_sensitive": False,
        })
    return out


def _preclinical_terms(card) -> list:
    """Resolve preclinical / basic-science terms in card text. Standalone
    library, fully free, no UpToDate dependency. Links to Wikipedia for
    further reading on click."""
    text = _card_text(card)
    if not text:
        return []
    out = []
    seen: set = set()
    # Several databases, one popup source. `_preclinical` holds
    # basic-science concepts, `_descriptive` the vocabulary cards are
    # written in (lesion morphology, symptom words, lab descriptors),
    # and `_psych` the mental state exam. They resolve together because
    # the reader has no reason to care which file a definition came
    # from. Order settles collisions: the first database to claim a name
    # keeps it, and `tests/test_vocab.py` asserts there are none.
    for it in (list(_preclinical.resolve(text))
               + list(_descriptive.resolve(text))
               + list(_psych.resolve(text))
               + list(_signs.resolve(text))):
        if it["name"] in seen:
            continue
        seen.add(it["name"])
        out.append({
            "title":          it["name"],
            "_article":       it["name"],
            "url":            it["url"],
            "summary":        it["summary"],
            "source":         "preclinical",
            "link":           it.get("link", "search"),
            "_surfaces":      it.get("surfaces") or [],
            # Explicit, not omitted. `_span` reads this key and falls
            # back to "[]" when it is absent, which is the same value
            # a real empty list gives - so a builder that simply forgot
            # it looked identical to one that meant it. That is how
            # `utd` was lost twice and `link` once. This database has
            # no UpToDate chips; saying so is the point.
            "utd": [],
            # The popup button's destination when this entry has no
            # chapter of its own. Only conditions carry one today; the
            # others say so explicitly rather than by omission, which is
            # the distinction that cost `utd` twice.
            "ref": [],
            "case_sensitive": False,
        })
    return out


def _custom_term_matches(card) -> list:
    """User-defined popup terms.  Match by case-sensitive substring
    when `case_sensitive` is True, else case-insensitive whole-word."""
    text = _card_text(card)
    if not text:
        return []
    text_lower = text.lower()
    out = []
    for entry in _custom_terms():
        title = entry["title"]
        if entry.get("case_sensitive"):
            present = title in text
        else:
            present = title.lower() in text_lower
        if present:
            out.append(entry)
    return out


# ── Phase 1: synchronous HTML injection via card_will_show ────────────────────

_HIGHLIGHT_CSS_TPL = (
    '<style>.sp-mark{{border-bottom:2px solid {c};cursor:pointer;'
    'border-radius:2px;display:inline;transition:background .1s;}}'
    '.sp-mark:hover{{background:rgba(15,202,212,.18);}}</style>'
)

_pattern_cache: dict = {}
_PATTERN_CACHE_MAX = 16


def _esc_attr(s: str) -> str:
    return (s.replace("&", "&amp;").replace('"', "&quot;")
             .replace("<", "&lt;").replace(">", "&gt;").replace("'", "&#39;"))


def _forms(t: dict) -> list:
    """Every spelling of `t` that should be underlined.

    The title first - it is what the popup is headed with and, on a
    card that uses the primary name, what is written. Then any surface
    form `resolve()` reports having actually matched in this text, which
    is what makes an alias visible: the pattern is built from these
    strings, so before surfaces were carried through, a card that said
    "heart attack" and never "myocardial infarction" resolved the entry
    and then had nothing to mark. All the forms map to one lookup
    record, so the popup title and URL are unaffected by which one hit.

    A surface under four characters is dropped for case-insensitive
    terms, the same rule `_inject_highlights` applies to titles and for
    the same reason: the library carries 387 abbreviation aliases and
    marking them without regard to case would light up "did" wherever
    it appears in prose. Case-sensitive terms are exempt - their casing
    is the discrimination - and so are user-defined ones.
    """
    forms = [t["title"]]
    short_ok = bool(t.get("case_sensitive") or t.get("user_defined"))
    for extra in t.get("_surfaces") or ():
        if not extra or extra in forms:
            continue
        if len(extra) < 4 and not short_ok:
            continue
        forms.append(extra)
    return forms


def _build_pattern(terms: list):
    """Build ONE combined regex that handles both case-sensitive and
    case-insensitive terms in a single pass.  Returns (regex, lookup,
    sensitive_titles_set) - the lookup keys are exact titles for sensitive
    terms and lowercased titles for insensitive terms.

    Using a single pass eliminates the corruption bug from sequential
    passes where pass 2 would match terms inside pass 1's span attributes.
    Results are cached by term fingerprint - re.compile is expensive.
    """
    # Cache key covers only fields that affect the regex/lookup - title,
    # the surface forms found in this text, case-sensitivity, and URL
    # (which can change via _upgrade_*_urls). Summaries and sources are
    # static and excluded so hashing stays fast even as descriptions
    # grow long.
    cache_key = frozenset(
        (t["title"], bool(t.get("case_sensitive")), t.get("url", ""),
         tuple(t.get("_surfaces") or ()))
        for t in terms
    )
    if cache_key in _pattern_cache:
        return _pattern_cache[cache_key]

    def _record(t: dict, title: str) -> dict:
        return {
            "url":     _esc_attr(t["url"]),
            "article": _esc_attr(t.get("_article") or title),
            "summary": _esc_attr(t.get("summary") or ""),
            "source":  _esc_attr(t.get("source") or "statpearls"),
            "badge":   _esc_attr(t.get("label") or ""),
            # Carried through explicitly. Every term builder above sets
            # `link`, and `_span` below reads it, but this dict sat
            # between them and dropped it - so `data-sp-link` was always
            # the "search" default, `isArticle` in web/marker.js was
            # always false, and the 2.5 work that made the popup stop
            # claiming articles it does not have could never take
            # effect. The badge read "The AnkiDote" even on the ~1,000
            # conditions with a real NBK chapter.
            "link":    _esc_attr(t.get("link") or "search"),
            "utd":     _esc_attr(json.dumps(t.get("utd") or [],
                                            separators=(",", ":"))),
            "ref":     _esc_attr(json.dumps(t.get("ref") or [],
                                            separators=(",", ":"))),
        }

    # One flat list of alternatives rather than a case-sensitive block
    # followed by a case-insensitive one.
    #
    # `re` alternation is first-match-wins, so with every sensitive
    # alternative ahead of every insensitive one, a sensitive term beat
    # an insensitive term at the same start position however much
    # shorter it was: "G6PD" won over "G6PD deficiency", "CURB-65" over
    # "CURB-65 score", "FEV1" over "FEV1/FVC ratio". 37 such pairs ship
    # in the library, and the longer entry was resolved, cost a pattern
    # slot and could never win. Sorting the two together by length -
    # which is what longest-match-wins means - is the whole fix; the
    # case-insensitive ones each carry their own scoped `(?i:...)`
    # instead of sharing one group.
    alts: list = []
    lookup: dict = {}
    sens_titles: set = set()
    seen_sens: set = set()
    seen_ins:  set = set()

    for t in terms:
        sensitive = bool(t.get("case_sensitive"))
        title = t["title"]
        rec = _record(t, title)
        for form in _forms(t):
            if sensitive:
                if form in seen_sens:
                    continue
                seen_sens.add(form)
                # First writer wins: `terms` arrives in precedence
                # order, so an earlier database keeps a name a later one
                # also claims. See `_on_card_will_show`.
                lookup.setdefault(form, rec)
                sens_titles.add(form)
            else:
                key = form.lower()
                if key in seen_ins:
                    continue
                seen_ins.add(key)
                lookup.setdefault(key, rec)
            alts.append((form, sensitive))

    if not alts:
        _pattern_cache[cache_key] = (None, None, None)
        return None, None, None

    # Stable, so terms of equal length keep the precedence order above.
    alts.sort(key=lambda a: len(a[0]), reverse=True)

    # `_matcher.alternation` puts the word boundaries where each form
    # needs them rather than wrapping the lot in `\b(?:...)\b`, which
    # asserted a WORD character after a phrase ending in punctuation and
    # so confined the 23 library terms ending in ")" - "Vitamin B12
    # (cobalamin)", "Epidemic polyarthritis (Australian)" - to matching
    # at the very end of the text. Same builder as the matcher's own
    # punctuation fallback, so the two agree on what a boundary is.
    rx = re.compile(_matcher.alternation(
        (form, _matcher.escape_phrase(form) if sensitive
         else "(?i:" + _matcher.escape_phrase(form) + ")")
        for form, sensitive in alts))
    result = rx, lookup, sens_titles
    if len(_pattern_cache) >= _PATTERN_CACHE_MAX:
        _pattern_cache.pop(next(iter(_pattern_cache)))
    _pattern_cache[cache_key] = result
    return result


# What opens a tag: `<` followed by an ASCII letter, `/`, `!` or `?`,
# which is HTML5's own rule. Any other `<` is a literal less-than sign.
# The walker below used to treat every `<` as a tag opener and go
# looking for the matching `>`, so "Sodium < 130 in SIADH" swallowed the
# rest of the node as one enormous tag, and on finding no `>` appended
# the whole remainder unhighlighted and gave up. That is guaranteed on
# the dock path, where `_panel_pearls` hands us decoded text and
# StatPearls and DrugBank prose is full of "sodium <135" and
# "FEV1/FVC <0.70".
#
# A compiled search rather than a per-character test: this runs on every
# text node up to the dock's 4,000-node cap, and skipping to the next
# real tag in C beats stepping over the false ones in Python.
_TAG_OPEN_RE = re.compile(r"<[A-Za-z/!?]")


# What a phrase may run through, and what ends it.
#
# The walker below matches over the characters BETWEEN tags, and for
# most of this add-on's life it matched over each such run on its own.
# So `of an&nbsp;<b>ectopic</b>&nbsp;pregnancy?` - which is how the card
# that prompted this is actually written - offered it "of an&nbsp;",
# "ectopic" and "&nbsp;pregnancy?" one at a time, and "Ectopic
# pregnancy" could not be seen at all. 60% of the library is multi-word
# (2,360 of 3,899 terms) and 4,869 of one user's 6,088 notes carry a
# `<b>` - students bold the key term, which is exactly the term we want
# to mark - so this was most of the vocabulary failing on most of the
# cards, silently, with nothing to notice except an absence.
#
# An inline element does not interrupt the sentence it sits in: a
# reader of `<b>ectopic</b> pregnancy` sees two words of one phrase. So
# text either side of one is joined into a single run before matching.
# A block element does interrupt it, and joining across one would be a
# worse bug than the one being fixed - "Signs of pregnancy</li><li>
# Temperature" would underline a phrase spanning two list items that
# share no sentence, and the popup would explain a term the card never
# used.
#
# Hence an allow-list rather than a deny-list of blocks. A tag not
# named here ends the run, so `<img>`, `<details>`, `<hr>`, an HTML
# comment, a doctype and whatever an editor invents next all fail
# safe: at worst a phrase around one of them stays unmarked, which is
# the status quo, rather than a phrase being invented across it.
_INLINE_TAGS = frozenset((
    "b", "i", "u", "em", "strong", "span", "font", "mark", "small",
    "sub", "sup", "s", "strike", "big", "a",
))


def _tag_end(html: str, i: int) -> int:
    """Index of the `>` closing the tag that starts at `i`, or -1.

    A plain `html.find('>', i)` stops at the first `>` anywhere, quoted
    or not, so `<img alt="a > b">` "ended" inside the alt text and the
    walker then treated `b">` as character data - which is how a span
    came to be injected inside an attribute value, destroying the
    element. An attribute value is the only place a `>` can hide, so
    tracking quotes is the whole of what is needed; this stays a
    scanner, not a parser.

    The character loop only runs on tags that carry a quote at all. A
    tag without one - which is most of them, and all of `<p>`, `<b>`,
    `<br>`, `</div>` - takes the same single `str.find` it always did,
    which matters because this is called for every tag of every text
    node, up to the dock's 4,000-node cap.

    A quote is only a quote where an attribute value can start, ie.
    after `=`. Otherwise `<img alt=Crohn's>` opens a value that never
    closes, and the function returns -1 for a tag that plainly ends -
    the same class of failure as the `>` it was written to fix.
    """
    j = html.find('>', i)
    if j == -1:
        return -1
    if '"' not in html[i:j] and "'" not in html[i:j]:
        return j
    quote = ""
    after_eq = False
    n = len(html)
    j = i + 1
    while j < n:
        ch = html[j]
        if quote:
            if ch == quote:
                quote = ""
        elif ch == '>':
            return j
        elif after_eq and (ch == '"' or ch == "'"):
            quote = ch
        if not ch.isspace():
            after_eq = (ch == '=')
        j += 1
    return -1


def _inject_highlights(html: str, results: list, color: str,
                       with_css: bool = True) -> str:
    """Inject .sp-mark spans + CSS into card HTML string.
    Operates on the raw HTML string - no JS needed, no CSP concerns.
    """
    # Self-heal: strip any sp-mark spans already present (cheap early exit
    # if there are none - avoids running the regex on every card).
    if 'class="sp-mark"' in html:
        html = _strip_sp_marks(html)
    # A term under 4 characters matched case-insensitively is noise -
    # "hi", "is", "an" would light up constantly. Case-sensitive terms
    # are exempt because the casing itself is discriminating (acronyms:
    # "PE" won't match "pe" in prose). User-defined custom terms are
    # exempt too: the user typed this one in deliberately, so silently
    # dropping it because it happens to be short is worse than the
    # noise the filter exists to prevent.
    terms = [r for r in results
             if r.get("title")
             and (len(r["title"]) >= 4 or r.get("case_sensitive")
                  or r.get("user_defined"))]
    if not terms:
        return html

    rx, lookup, sens_titles = _build_pattern(terms)
    if rx is None:
        return html

    def _open_span(word: str):
        """The opening tag for a match, or None if nothing claims it."""
        # The pattern lets a term's spaces match `&nbsp;` and the
        # exotic space characters an editor inserts, so the matched
        # text is not always the form the lookup was keyed on. Key
        # on the same normalised shape the pattern was built from,
        # or every one of those matches finds nothing here and is
        # written back unmarked - which is the bug this whole change
        # is about, moved one step later.
        key = _matcher.normalise_separators(word)
        t = (lookup.get(key) if key in sens_titles
             else lookup.get(key.lower()))
        if not t:
            return None
        return (f'<span class="sp-mark" '
                f'data-sp-url="{t["url"]}" '
                f'data-sp-title="{t["article"]}" '
                f'data-sp-summary="{t["summary"]}" '
                f'data-sp-source="{t.get("source", "statpearls")}" '
                f'data-sp-badge="{t.get("badge", "")}" '
                f'data-sp-link="{t.get("link", "search")}" '
                f'data-sp-utd="{t.get("utd", "[]")}" '
                f'data-sp-ref="{t.get("ref", "")}">')

    def _span(m):
        # ONE pass over the text using the combined regex. No risk of a
        # later pass corrupting an earlier pass's injected HTML.
        word = m.group(0)
        open_tag = _open_span(word)
        return word if open_tag is None else open_tag + word + "</span>"

    # Walk the HTML string, marking the text between tags and skipping
    # `<script>` / `<style>` content.
    #
    # Every text run is appended to `result` verbatim as it is met and
    # rewritten in place later, once the sentence it belongs to has
    # ended. That is what lets a match reach across an inline tag the
    # walker has already emitted: `run_at` remembers where each run was
    # put, `run_tx` what it said, and `_flush` goes back and edits them.
    result: list = []
    run_at: list = []
    run_tx: list = []
    append = result.append

    def _mark_across() -> None:
        """Match over several runs joined, then mark each run's share.

        A match that starts inside an element and ends outside it -
        `<b>ectopic</b> pregnancy` - has no single well-formed span:
        `<span><b>ectopic</b> pregnancy</span>` is fine only because the
        `<b>` closes inside it, and the moment the match starts inside
        the `<b>` instead, one span would have to cross the element's
        boundary and produce `<span>..<b>..</span>..</b>`. So each run
        gets its own span, all of them carrying the same `data-sp-*`
        attributes: the whole term underlines, hovering any part of it
        opens the same popup, and the nesting is valid whatever shape
        the card is written in.
        """
        joined = "".join(run_tx)
        if not joined.strip():
            return
        # Cumulative end offset of each run within `joined`, so a match
        # can be mapped back onto the runs it covers with a bisect
        # rather than a walk - a card is one segment per sentence, but
        # a page of `<span>`-wrapped prose is one segment of hundreds.
        ends: list = []
        p = 0
        for t in run_tx:
            p += len(t)
            ends.append(p)
        # Collected before anything is rewritten, because one run can
        # hold pieces of two different matches and is rebuilt once.
        pieces: dict = {}
        for m in rx.finditer(joined):
            open_tag = _open_span(m.group(0))
            if open_tag is None:
                continue
            ms, me = m.span()
            k = bisect_right(ends, ms)
            base = ends[k - 1] if k else 0
            while k < len(ends) and base < me:
                a = ms - base
                if a < 0:
                    a = 0
                b = me - base
                if b > len(run_tx[k]):
                    b = len(run_tx[k])
                pieces.setdefault(k, []).append((a, b, open_tag))
                base = ends[k]
                k += 1
        for k, plist in pieces.items():
            text = run_tx[k]
            parts: list = []
            prev = 0
            for a, b, open_tag in plist:
                if a > prev:
                    parts.append(text[prev:a])
                parts.append(open_tag)
                parts.append(text[a:b])
                parts.append("</span>")
                prev = b
            parts.append(text[prev:])
            result[run_at[k]] = "".join(parts)

    def _flush() -> None:
        """End the current sentence: mark its runs and start a new one."""
        if run_tx:
            if len(run_tx) == 1:
                # A text node with no inline markup in it, which is most
                # of them, takes the same single `sub` it always did and
                # none of the offset bookkeeping above.
                one = run_tx[0]
                if one.strip():
                    result[run_at[0]] = rx.sub(_span, one)
            else:
                _mark_across()
            del run_at[:]
            del run_tx[:]

    skip = False
    i = 0
    n = len(html)
    search = _TAG_OPEN_RE.search
    while i < n:
        m = search(html, i)
        start = m.start() if m else n
        if start > i:
            chunk = html[i:start]
            if not skip:
                run_at.append(len(result))
                run_tx.append(chunk)
            append(chunk)
        if m is None:
            break
        j = _tag_end(html, start)
        if j == -1:
            _flush()
            append(html[start:])
            break
        tag = html[start:j + 1]
        # Sniff the tag name without splitting twice.
        k = 1
        if tag[k] == '/':
            k += 1
        tag_name_end = k
        while tag_name_end < len(tag) and tag[tag_name_end].isalpha():
            tag_name_end += 1
        tname = tag[k:tag_name_end].lower()
        if tname not in _INLINE_TAGS:
            _flush()
            if tname in ('script', 'style'):
                # Detect closing form; tag[1] == '/' means a closing tag.
                skip = (tag[1] != '/')
        append(tag)
        i = j + 1
    _flush()

    marked = ''.join(result)
    # The card path needs the rule travelling with the HTML,
    # because it is handed to Anki as one string. The dock does
    # not: it installs a single `#tad-hl-style` element after
    # applying the edits, and each edit is inserted with
    # `template.innerHTML`, so a rule carried per node put one
    # `<style>` element into the article body per highlighted
    # node - 105 of them on a 66 KB page, all identical, all
    # redundant against the one the apply script adds.
    return (_HIGHLIGHT_CSS_TPL.format(c=color) + marked) if with_css \
        else marked


def highlight_text(text: str, color: str = "",
                   with_css: bool = True) -> str:
    """Wrap every recognised term in `text` in an sp-mark span.

    The reviewer path highlights a card; this highlights any text, which
    is what the reference dock needs to mark up a StatPearls or DrugBank
    page. It reuses all five term builders and the same injector, so the
    dock cannot drift from the reviewer: one vocabulary, one matcher,
    one set of data attributes, and `web/marker.js` renders the popup in
    both places.

    Returns `text` unchanged when nothing matches, so a caller can test
    identity to skip a DOM write.
    """
    if not text or not text.strip():
        return text
    try:
        results = (_custom_term_matches(text) + _acronym_terms(text)
                   + _condition_terms(text) + _drug_terms(text)
                   + _preclinical_terms(text))
    except Exception as exc:
        _log.error("highlight_text resolve", exc)
        return text
    if not results:
        return text
    col = _config.safe_css_colour(color or _config.get("highlightColor"))
    try:
        return _inject_highlights(text, results, col, with_css=with_css)
    except Exception as exc:
        _log.error("highlight_text inject", exc)
        return text



def _on_card_will_show(html: str, card, kind: str) -> str:
    """Phase 1: inject highlights synchronously before card renders.
    Sourced from the bundled term databases (acronyms, drugs, conditions)
    plus user-defined custom terms - all instant, no network call."""
    if kind not in ("reviewQuestion", "reviewAnswer"):
        return html
    if not _config.get("enableHighlights"):
        return html
    if kind == "reviewQuestion" and not _config.get("enableHighlightsOnQuestions"):
        return html
    if _panel_ref is None:
        return html
    try:
        # Concatenated in precedence order, because `_build_pattern`
        # keys its lookup by lowercased title and the first database to
        # claim a name keeps it. Six names are held by both a condition
        # and a preclinical entry - splenomegaly, dysphagia,
        # lymphadenopathy, ptosis, aphasia, heart murmur - and seven by
        # both a drug and a preclinical entry, glucagon and vitamin K
        # among them. Preclinical links to a Wikipedia search and the
        # other two to a StatPearls chapter or a DrugBank monograph, so
        # preclinical goes last and all thirteen keep the better
        # destination; it used to be written last, and won every one of
        # them. Custom terms go first: the user typed those in
        # deliberately, which outranks anything shipped. Conditions and
        # drugs share no name at all, so their order settles nothing and
        # is only here to be stated rather than discovered again.
        custom      = _custom_term_matches(card)
        acronyms    = _acronym_terms(card)
        conditions  = _condition_terms(card)
        drugs       = _drug_terms(card)
        preclinical = _preclinical_terms(card)
        all_terms   = custom + acronyms + conditions + drugs + preclinical
        if not all_terms:
            return html
        color = _config.safe_css_colour(_config.get("highlightColor"))
        return _inject_highlights(html, all_terms, color)
    except Exception as exc:
        _log.error("card_will_show", exc)
        return html


# ── Phase 2: async fallback via web.eval() ────────────────────────────────────

def _on_webview_will_set_content(web_content: Any, context: Any) -> None:
    """Belt-and-suspenders: also load marker.js via <script src> for tooltip events."""
    if Reviewer is None or not isinstance(context, Reviewer):
        return
    web_content.body += f'<script src="{_SCRIPT_URL}"></script>\n'




def _clear_in_reviewer() -> None:
    try:
        reviewer = mw.reviewer
        if reviewer and reviewer.web:
            reviewer.web.eval(
                'var _s=document.querySelectorAll(".sp-mark");'
                'for(var _i=0;_i<_s.length;_i++){'
                '  var _m=_s[_i];'
                '  if(_m.parentNode)_m.parentNode.replaceChild('
                '    document.createTextNode(_m.textContent),_m);'
                '}'
                'if(document.body)document.body.normalize();'
            )
    except Exception:
        pass


# ── reviewer hooks ────────────────────────────────────────────────────────────

def _first_field_text(card) -> str:
    """The card's opening field, lowercased.

    On essentially every note type this is the subject line - the thing
    the card is *about* - so a term appearing there is categorically
    more relevant than one mentioned in passing further down."""
    try:
        vals = [v for v in card.note().values() if v.strip()]
        return _strip_html(vals[0]).lower() if vals else ""
    except Exception:
        return ""


def _rank_results(card, items: list) -> list:
    """Order the sidebar's article list by how central each term is.

    The list used to be every match on the card in the order the
    resolvers happened to find them, conditions first and drugs after.
    On a card about calcium pyrophosphate deposition disease that put
    "gout" - mentioned once, as a contrast - above the disease the card
    is actually about, and buried the drug the card is teaching under
    every condition named anywhere in the text.

    Four signals, in rough order of how much they matter:
      * the term appears in the first field (the card's subject);
      * how many times it appears at all;
      * how early the first mention is;
      * how specific the term is, since a long name is a narrower claim
        about the card's content than a short one.
    """
    text = (_card_text(card) or "").lower()
    head = _first_field_text(card)
    if not text:
        return items
    for it in items:
        name = (it.get("_term") or it.get("title") or "").lower()
        if not name:
            it["_score"] = 0.0
            continue
        count = text.count(name)
        pos = text.find(name)
        score = 0.0
        if name in head:
            score += 100.0
        score += min(count, 6) * 8.0
        if pos >= 0:
            score += max(0.0, 20.0 - pos / 40.0)
        score += min(len(name), 40) / 4.0
        it["_score"] = score
    items.sort(key=lambda r: -r.get("_score", 0.0))
    return items


def _local_results_for_card(card) -> list:
    """Build the sidebar's article list from the local databases.

    Ranked by `_rank_results` and capped at `maxResults`, because an
    unbounded list scrolls and a scrolling list of guesses is worse than
    a short one: the reader stops reading it either way, and the short
    one at least stays out of the way."""
    results = []
    seen: set = set()
    # `_on_card_will_show` used to stash its condition and drug lists on
    # the card here for this function to reuse. It was never read once:
    # Anki fires `card_will_show` first, and the loop above - which runs
    # before this call, in the same function - deleted both names as
    # part of dropping the stale text cache. So every call took the
    # recompute branch, at a measured 0.03 ms per card. Deleted rather
    # than repaired: keeping the stash alive across the cache drop would
    # mean serving a condition list derived from text the same function
    # has just declared stale, and 0.03 ms is not worth a staleness
    # window.
    conds = _condition_terms(card)
    for t in conds:
        key = t["url"]
        if key and key not in seen:
            seen.add(key)
            results.append({
                "id":      f"local_cond_{t['title']}",
                "title":   t["title"],
                "_term":   t["title"],
                "url":     t["url"],
                "summary": t.get("summary", ""),
            })
    drugs = _drug_terms(card)
    for t in drugs:
        key = t["url"]
        if key and key not in seen:
            seen.add(key)
            results.append({
                "id":      f"local_drug_{t['title']}",
                # Kept separate from `_term` so the " - drug" label does
                # not end up in the text we score against the card.
                "title":   t["title"] + " - drug",
                "_term":   t["title"],
                "url":     t["url"],
                "summary": t.get("summary", ""),
            })
    _rank_results(card, results)
    try:
        cap = int(_config.get("maxResults") or 8)
    except Exception:
        cap = 8
    if cap > 0:
        results = results[:cap]
    return results


def _dismiss_popup() -> None:
    """Close any popup still on screen.

    The card's HTML is re-rendered on a flip and on a new card, so the
    span the popup was anchored to is detached and the popup is left
    hovering over content it no longer describes.
    """
    try:
        if mw.reviewer and mw.reviewer.web:
            mw.reviewer.web.eval(
                "if(window.spAddon&&spAddon.dismissTip)spAddon.dismissTip();")
    except Exception:
        pass


def _on_show_question(card) -> None:
    global _prev_card_id

    card_id = getattr(card, "id", None)
    card_changed = (card_id != _prev_card_id)
    _prev_card_id = card_id

    # Dismiss any open popup immediately when progressing to a new card.
    if card_changed:
        _dismiss_popup()

    # Drop any prior text cache on this card so re-shown cards re-strip lazily.
    try:
        if hasattr(card, "_ap_text"):
            delattr(card, "_ap_text")
    except Exception:
        pass

    if not _config.get("enableHighlights"):
        _clear_in_reviewer()
        return

    if _panel_ref is None:
        return

    # Feed instant local-database matches to the sidebar's article list.
    # Empty list hides the list section entirely (no "searching..." stub).
    if card_changed:
        _panel_ref.apply_local_results(_local_results_for_card(card))


def _on_show_answer(card) -> None:
    """Flipping to the answer re-renders the card, so a popup opened on
    the question is now anchored to a span that no longer exists. This
    only fired on a card change before, which left the popup up across
    every flip and, on a card shown twice in a session, never cleared
    it at all."""
    _dismiss_popup()


# ── register hooks ────────────────────────────────────────────────────────────

def register_hooks() -> None:
    gui_hooks.webview_will_set_content.append(_on_webview_will_set_content)
    gui_hooks.reviewer_did_show_question.append(_on_show_question)
    gui_hooks.reviewer_did_show_answer.append(_on_show_answer)
    try:
        gui_hooks.card_will_show.append(_on_card_will_show)
        _log.debug("card_will_show hook registered")
    except AttributeError:
        _log.warn("card_will_show hook not available (older Anki)")
