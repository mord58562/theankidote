# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.

"""Common medical condition detection - curated list of diseases, syndromes,
and named clinical entities linked to specific StatPearls articles.

Each entry has:
  • name      - canonical name; matches case-insensitively as a whole word
  • aliases   - alternate forms (plurals, alt-spellings) that should also match
  • nbk       - optional NBK accession (e.g., "NBK513321") for a direct article
                URL.  When omitted, a StatPearls book-title search URL is used.
  • utd       - optional list of (label, query) tuples linking to UpToDate
                subtopic pages.  Each tuple becomes a chip in the popup;
                `query` is fed to UpToDate's search.  If `nbk` is missing
                but `utd` is present, the first UTD entry is used as the
                primary URL (and the chip is omitted to avoid duplication).
  • summary   - concise clinical summary (definition, presentation, key
                management) - pharmacology kept to a minimum.

The list focuses on common, specific entities that students/clinicians look
up.  Generic symptoms ("fever", "pain") and ambiguous terms ("shock") are
deliberately excluded to avoid false positives.  Acronyms (e.g., MI, CHF)
are covered by `_acronyms.py` and drugs by `_drugs.py`.
"""

from . import _library

import re
from urllib.parse import quote_plus

from . import _matcher

# Loaded from data/library.json - see tools/build_library.py. The
# authoring copy of this vocabulary lives in content/, and is
# compiled rather than imported so content can ship without a
# new add-on release.
# Copied, not referenced. The rich overrides below are applied by
# mutating `entry["summary"]` in place, and these dicts belong to the
# loaded library - so without the copy the merge would rewrite the base
# text inside `_library.LIBRARY` itself. Nothing in the running add-on
# would notice, but `tools/build_library.py` reads the base text back
# out of the library to rebuild it, and would then bake each override
# permanently into the base, making the next edit to content/_rich.py a
# silent no-op.
_CONDITIONS: list = [dict(c) for c in _library.get("conditions")]


# ── Build lookup tables and master regex ──────────────────────────────────────

# Australian to US spelling, applied only when building a StatPearls
# search query. Ordered longest-first so "haemorrhage" is rewritten
# whole rather than being caught mid-word by the "haem" rule.
_US_SPELLING = (
    ("haemorrhag", "hemorrhag"), ("haematolog", "hematolog"),
    ("haemoglobin", "hemoglobin"), ("haemolytic", "hemolytic"),
    ("haemophilia", "hemophilia"), ("haemat", "hemat"), ("haem", "hem"),
    ("anaemia", "anemia"), ("anaemic", "anemic"),
    ("oedema", "edema"), ("oesophag", "esophag"), ("oestrogen", "estrogen"),
    ("paediatric", "pediatric"), ("gynaecolog", "gynecolog"),
    ("diarrhoea", "diarrhea"), ("dyspnoea", "dyspnea"),
    ("orthopnoea", "orthopnea"), ("apnoea", "apnea"),
    ("ischaemi", "ischemi"), ("leukaemi", "leukemi"),
    ("aetiolog", "etiolog"), ("coeliac", "celiac"),
    ("tumour", "tumor"), ("oedematous", "edematous"),
    ("caesarean", "cesarean"), ("orthopaedic", "orthopedic"),
    ("hypercalcaemia", "hypercalcemia"), ("hyperkalaemia", "hyperkalemia"),
    ("hypokalaemia", "hypokalemia"), ("hyponatraemia", "hyponatremia"),
    ("hypernatraemia", "hypernatremia"), ("bacteraemia", "bacteremia"),
    ("septicaemia", "septicemia"), ("uraemi", "uremi"),
    ("glycaemi", "glycemi"), ("lipaemi", "lipemi"),
    ("aemia", "emia"),
)


def _us_spelling(term: str) -> str:
    """Rewrite a term into US spelling for searching.

    StatPearls is a US publication, so an in-book search for "Iron
    deficiency anaemia" returns nothing while "anemia" finds the
    article. This bit us on the 189 conditions that carry no direct
    NBK accession and therefore fall back to search - the popup opened
    a search page that could never match, which reads as the link being
    broken.

    Only the outgoing query is changed. Everything the reader sees
    stays in Australian spelling.
    """
    out = term
    low = out.lower()
    for au, us in _US_SPELLING:
        if au in low:
            # Rebuild case-insensitively while preserving the rest of
            # the string; terms are short so the cost is irrelevant.
            idx = low.find(au)
            while idx != -1:
                out = out[:idx] + us + out[idx + len(au):]
                low = out.lower()
                idx = low.find(au)
    # A replacement at position 0 inserts the lowercase US form, so
    # "Coeliac disease" would come back as "celiac disease". NCBI search
    # is case-insensitive, but the URL is visible in the panel.
    if term[:1].isupper() and out[:1].islower():
        out = out[:1].upper() + out[1:]
    return out


def _term_search_url(term: str) -> str:
    """In-book StatPearls search URL - targets the per-book search interface
    (`/books/n/statpearls/`) so the term populates the 'Search this book'
    input rather than the broader Bookshelf-wide search bar."""
    return ("https://www.ncbi.nlm.nih.gov/books/n/statpearls/?term="
            f"{quote_plus(_us_spelling(term))}")


def _utd_url(query: str) -> str:
    """UpToDate URL builder.

    Two input forms are recognised:
      * `slug:<topic-slug>` → direct article link
        (e.g. `slug:treatment-of-acute-pancreatitis`).
      * anything else → search URL with the input as the search term.

    The slug form is produced by `tools/utd_slug_finder.py apply` after
    a ToS-clean Brave/Google search-API discovery pass.  Direct slugs
    save the user one click; if a slug ever 404s, UTD's own search page
    is the natural fallback (the chip user can re-run the same query).

    No content is ever scraped - slugs are public URL metadata returned
    by search engines that have explicit robots.txt permission to crawl
    UpToDate.  See tools/utd_slug_finder.py for the discovery flow.
    """
    if query.startswith("slug:"):
        return f"https://www.uptodate.com/contents/{query[5:]}"
    return ("https://www.uptodate.com/contents/search?search="
            f"{quote_plus(query)}&source=USER_INPUT&searchType=PLAIN_TEXT")


def _url_for(entry: dict) -> str:
    """Primary URL for the condition.  Resolution order:
      1. `source == "uptodate"` and UTD entries → first UTD entry
      2. `nbk` set → direct NCBI bookshelf link
      3. fallback → StatPearls in-book search

    Note: `utd` alone does NOT make a condition UTD-primary - UTD chips are
    supplementary by default.  Set `"source": "uptodate"` explicitly to
    promote UTD to primary (used for entries StatPearls doesn't cover)."""
    if entry.get("source") == "uptodate":
        utd = entry.get("utd")
        if utd:
            return _utd_url(utd[0][1])
    nbk = entry.get("nbk")
    if nbk:
        return f"https://www.ncbi.nlm.nih.gov/books/{nbk}/"
    return _term_search_url(entry["name"])


# Lookup keyed by lowercase form of name + each alias.
_LOOKUP: dict = {}
_NAMES:  list = []

# Conditions contributed by the structured-summary layer. Some entries
# there describe things the base database never listed - the oncological
# emergencies especially - and a summary for a term that cannot be
# matched is dead weight. Merged before the index is built so the new
# names are matchable like any other.
_NEW: list = _library.get("new_conditions")
_CONDITIONS = list(_CONDITIONS) + list(_NEW)

for _c in _CONDITIONS:
    n = _c["name"]
    keys = [n] + list(_c.get("aliases", []) or [])
    _NAMES.extend(keys)
    for k in keys:
        # First-occurrence wins so the lookup is deterministic when an alias
        # is shared across UK/US spelling pairs or otherwise duplicated.
        # Aliases were pruned in a separate audit so no two entries should
        # share an alias at present; `setdefault` is defence-in-depth.
        _LOOKUP.setdefault(k.lower(), _c)

# Case-insensitive dedup of display names (keep first-seen form). Matching is
# case-insensitive at runtime, so "Foo" and "foo" are the same term; carrying
# both bloats the regex and would surface as duplicate "synonyms" anywhere we
# enumerate _NAMES.
_seen_ci: set = set()
_uniq: list = []
for _n in _NAMES:
    _lk = _n.lower()
    if _lk in _seen_ci:
        continue
    _seen_ci.add(_lk)
    _uniq.append(_n)
# Sort longest first so the regex prefers fuller matches over substrings.
_NAMES = sorted(_uniq, key=len, reverse=True)
# Matched by first-word index rather than a several-thousand-alternative
# regex; see pearls/_matcher.py for why and for the equivalence proof.
# The pattern is kept because the test suite diffs the two.
_CONDITION_RE = (
    re.compile(r"\b(?:" + "|".join(re.escape(n) for n in _NAMES) + r")\b",
               re.IGNORECASE)
    if _NAMES else None
)
_CONDITION_MATCHER = _matcher.PhraseMatcher(_NAMES) if _NAMES else None


# Structured rewrites, merged over the entries above. Authored in
# content/_rich.py and compiled into the library, so a corrected summary
# can ship without a new add-on release. Applied by canonical name, so
# aliases inherit it automatically - and only by canonical name, because
# `resolve()` titles the popup from `c["name"]`: an override keyed on an
# alias still merges but renders under a heading it was not written for.
_RICH: dict = _library.get("rich_summaries")

_RICH_APPLIED: set = set()
for _canon, _text in _RICH.items():
    _entry = _LOOKUP.get(_canon.lower())
    if _entry is not None and _text:
        _entry["summary"] = _text
        _RICH_APPLIED.add(_canon)


def resolve(text: str) -> list:
    """Find condition mentions in `text`. Returns a list of dicts:
        {name, summary, url, source, utd, case_sensitive=False}
    `name` is the canonical name (regardless of which form was matched in the
    text), so the popup title is consistent.
    `utd` is a list of {label, url} chip dicts for the popup footer.  When
    a condition has no NBK but has UTD entries, the first UTD slot powers
    the primary URL and is dropped from the chip list to avoid duplication."""
    if not text or _CONDITION_MATCHER is None:
        return []
    out  = []
    seen: set = set()
    for _s, _e, key in _CONDITION_MATCHER.find(text):
        c = _LOOKUP.get(key)
        if c is None:
            continue
        canon = c["name"]
        if canon in seen:
            continue
        seen.add(canon)
        utd_entries  = c.get("utd") or []
        utd_primary  = c.get("source") == "uptodate" and bool(utd_entries)
        # When UTD is primary, the first chip's URL is reused for "Open
        # UpToDate →" - drop it from the chip list to avoid duplication.
        chip_source  = utd_entries[1:] if utd_primary else utd_entries
        utd_chips    = [{"label": lbl, "url": _utd_url(q)}
                        for lbl, q in chip_source]
        out.append({
            "name":           canon,
            "summary":        c["summary"],
            "url":            _url_for(c),
            "source":         "uptodate" if utd_primary else "statpearls",
            "utd":            utd_chips,
            "case_sensitive": False,
        })
    return out
