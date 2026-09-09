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
from . import _matcher
from urllib.parse import quote_plus

# Loaded from data/library.json - see tools/build_library.py. The
# authoring copy of this vocabulary lives in content/, and is
# compiled rather than imported so content can ship without a
# new add-on release.
#
# Copied entry by entry, and the copy is not optional. `_DRUG_SUMMARIES`
# below rewrites `summary` in place, and `tools/build_library.py` reads
# the drug list back out of the library to recompile it. Without the
# copy those are the same dict objects, so the first rebuild after an
# override is written bakes the override in as the base text - and from
# then on, deleting the override from `content/_rich.py` changes
# nothing, because the text it was replacing is gone. This is the
# identical trap `_conditions.py` documents at `[dict(c) for c in ...]`;
# it was found there and it applies here for the same reason.
_DRUGS: list = [dict(d) for d in _library.get("drugs")]


# ── DrugBank direct URLs ──────────────────────────────────────────────────────
# Accession IDs for well-established drugs.  When present, clicking the popup
# button opens the specific DrugBank page; otherwise a search URL is used.
# Loaded from data/library.json - see tools/build_library.py. The
# authoring copy of this vocabulary lives in content/, and is
# compiled rather than imported so content can ship without a
# new add-on release.
_DRUGBANK_IDS: dict = _library.get("drugbank_ids")


DRUGBANK_FREE_ACCOUNT_URL = "https://go.drugbank.com/public_users/sign_up"


def _drug_link_kind(entry: dict) -> str:
    """A DrugBank id gives a real monograph; without one the URL is an
    `unearth` search, so the popup must not offer to open an article."""
    return ("article"
            if _DRUGBANK_IDS.get((entry.get("generic") or "").lower())
            else "search")


def _drugbank_url(entry: dict) -> str:
    # DrugBank monograph pages are viewable without an account; the unearth
    # search endpoint is sometimes gated - users can sign up for a free
    # DrugBank account in their own browser session if they hit a wall.
    db_id = _DRUGBANK_IDS.get((entry.get("generic") or "").lower())
    if db_id:
        return f"https://go.drugbank.com/drugs/{db_id}"
    name = entry.get("generic") or ""
    return f"https://go.drugbank.com/unearth/q?searcher=drugs&query={quote_plus(name)}"


# Drugs absent from the base vocabulary entirely, authored in
# content/_rich.py as NEW_DRUGS and compiled into the library under its
# own key. Mirrors `new_conditions` and exists for the same reason: the
# base vocabulary is a fixed corpus and there has to be a way to add to
# it over the content channel rather than only over an AnkiWeb release.
#
# Kept out of `drugs` deliberately. `tools/build_library.py` reads
# `drugs` back out of the library as the base for the next build, so an
# entry appended there becomes permanent - removing it from NEW_DRUGS
# afterwards would do nothing. A separate key means the list stays
# authoritative in both directions.
#
# Merged before the index is built, so a new name is matchable like any
# other. Optional, because a library published before 2.2 does not carry
# it.
_NEW_DRUGS: list = _library.get("new_drugs", [])
_DRUGS = _DRUGS + [dict(d) for d in _NEW_DRUGS]


# ── Structured rewrites, merged over the entries above ───────────────────────
#
# The drug vocabulary had no authoring copy at all before 2.2. Condition
# text has lived in `content/_rich.py` since the 2.0 split and reaches
# installs over the content channel; drug text lived only in
# `data/library.json`, which is a build artefact nobody hand-edits, so
# "rewrite this drug summary" had no procedure. That is why the drug
# backlog never moved while the condition backlog did.
#
# This is the same seam as `rich_summaries`, deliberately: authored in
# `content/_rich.py`, compiled into the library, applied at runtime
# rather than baked in at build time, keyed on the primary generic.
#
# Keyed on the generic only, never an alias. `resolve()` titles the
# popup from `d["generic"]`, so an override keyed on an alias would
# merge and then render under a heading it was not written for - the
# same rule `_conditions.py` records for primary names.
#
# Optional key: a library published before 2.2 does not carry it, and a
# published library is preferred over the bundled one, so its absence is
# a normal state.
_DRUG_SUMMARIES: dict = _library.get("drug_summaries", {})

_BY_GENERIC: dict = {}
for _d in _DRUGS:
    _g0 = _d.get("generic")
    if _g0:
        _BY_GENERIC.setdefault(_g0.lower(), _d)
for _canon, _text in _DRUG_SUMMARIES.items():
    _entry = _BY_GENERIC.get(_canon.lower())
    if _entry is not None and _text:
        _entry["summary"] = _text


# ── Build lookup tables and master regexes ────────────────────────────────────

_GENERIC_LOOKUP: dict = {}   # lowercase generic name → entry
_BRAND_LOOKUP:   dict = {}   # exact brand name → entry

for _d in _DRUGS:
    _g = _d.get("generic")
    if _g:
        _GENERIC_LOOKUP[_g.lower()] = _d
    # Spelling variants go through the GENERIC path, not the brand path.
    #
    # They are not brands: `frusemide` is what NSW Health, the PBS and
    # most Australian cards call furosemide, and `cephalexin` and
    # `thyroxine` are the same story. Routing them through
    # `_BRAND_LOOKUP` would match them case-sensitively, which is right
    # for a capitalised trade name and wrong for a lower-case generic -
    # `frusemide` mid-sentence would match and `Frusemide` at the start
    # of one would not.
    #
    # `resolve` reports `d["generic"]`, so an aliased match still shows
    # the INN spelling in the popup heading. The alias decides what the
    # matcher recognises and which word gets underlined on the card -
    # `frusemide` written on a card is `frusemide` underlined - but
    # never what the popup calls it.
    for _a in _d.get("aliases", []) or []:
        if isinstance(_a, str) and _a.strip():
            _GENERIC_LOOKUP.setdefault(_a.lower(), _d)
    # A brand that case-insensitively matches the generic isn't a real brand -
    # skip it so the same word doesn't surface twice through the brand path.
    _g_lower = (_g or "").lower()
    for _b in _d.get("brands", []) or []:
        if _b.lower() == _g_lower:
            continue
        # `setdefault`, not assignment. 21 brand strings are claimed by
        # more than one generic, and a plain assignment let the last
        # entry in list order win in silence: Buscopan resolved to
        # whichever of `hyoscine` and `hyoscine butylbromide` happened to
        # sit later. Most of the 21 are combination products where each
        # component entry lists the same trade name - Entresto against
        # both `sacubitril` and `sacubitril/valsartan`, Malarone against
        # `atovaquone` and `proguanil` - so first-wins is not obviously
        # right either, but it is at least stable across a rebuild, and
        # `_COMBINATION_BRANDS` below names the ones where the combined
        # entry is the one the reader wants.
        _BRAND_LOOKUP.setdefault(_b, _d)


# Brands whose popup must resolve to the combined-product entry rather
# than to whichever single component was listed first. Each of these is
# sold only as the combination, so a popup headed with one component
# describes something the patient is not taking.
_COMBINATION_BRANDS = {
    "Entresto": "sacubitril/valsartan",
    "Buscopan": "hyoscine butylbromide",
}
for _b, _want in _COMBINATION_BRANDS.items():
    _pref = _GENERIC_LOOKUP.get(_want.lower())
    if _pref is not None and _b in _BRAND_LOOKUP:
        _BRAND_LOOKUP[_b] = _pref


# Matched by first-word index rather than by a single alternation over
# every name. See pearls/_matcher.py: an alternation is
# O(text x alternatives) and this is O(text), which is what lets the
# database keep growing.
#
# The alternations themselves were kept until 2.2 purely so a test
# could diff the two matchers against each other. Compiling them cost
# 27ms of every Anki launch (1,161 generics and 1,651 brands) to build
# two objects nothing ever read.
_GENERIC_MATCHER = (_matcher.PhraseMatcher(list(_GENERIC_LOOKUP))
                    if _GENERIC_LOOKUP else None)
_BRAND_MATCHER = (_matcher.PhraseMatcher(list(_BRAND_LOOKUP), case_sensitive=True)
                  if _BRAND_LOOKUP else None)


def _brand_relation(brand: str, entry: dict) -> str:
    """One sentence saying how a trade name relates to its generic.

    Australian wording where the entry says the brand is sold here, and
    neutral wording otherwise. The distinction is not guessed: only an
    explicit `brands_au` list earns "an Australian brand of", because
    the corpus carries American trade names authored directly alongside
    Australian ones and nothing distinguishes Lipitor from Clopine by
    inspection. Guessing wrong here would put a false claim about
    Australian availability in front of a student who is going to act on
    it, which is worse than the weaker sentence.
    """
    generic = entry.get("generic") or ""
    if not generic:
        return ""
    if brand in (entry.get("brands_au") or []):
        return f"{brand} is an Australian brand of {generic}."
    return f"{brand} is a brand name for {generic}."


def _spelling_relation(surface: str, entry: dict) -> str:
    """The same sentence for a generic reached through a spelling alias.

    Frusemide and furosemide are the same INN spelled two ways, and the
    popup heading shows the entry's own spelling, so a reader who typed
    the Australian form saw a heading that silently disagreed with the
    card. Naming the relationship is the same fix as for brands, and the
    two are the same defect: the matched form was resolved and then
    thrown away.
    """
    generic = entry.get("generic") or ""
    if not generic or surface.lower() == generic.lower():
        return ""
    return f"{surface} is another spelling of {generic}."


def resolve(text: str) -> list:
    """Find drug mentions in `text`. Returns a list of dicts:
        {name, surfaces, summary, url, case_sensitive}
    name preserves the case as it appeared in the text for brand matches and
    uses the primary generic spelling for generic matches.
    `surfaces` is every distinct spelling the entry was matched on here -
    the alias the card actually used. 38 of the 42 spelling aliases do not
    contain their generic as a substring, so the highlighter had nothing
    to mark: a card written in `frusemide` resolved furosemide and then
    underlined nothing. The mark follows the card, the heading stays INN.
    """
    if not text:
        return []
    out = []
    seen: dict = {}

    if _GENERIC_MATCHER:
        for _s, _e, key in _GENERIC_MATCHER.find(text):
            d = _GENERIC_LOOKUP.get(key)
            if not d:
                continue
            surface = _matcher.surface_form(text, _s, _e, key)
            prev = seen.get(key)
            if prev is not None:
                if surface and surface not in prev["surfaces"]:
                    prev["surfaces"].append(surface)
                continue
            item = {
                "name":           d["generic"],
                "surfaces":       [surface] if surface else [],
                "summary":        d["summary"],
                "relation":       _spelling_relation(surface, d),
                "form_kind":      ("spelling" if surface
                                   and surface.lower() != d["generic"].lower()
                                   else "primary"),
                "url":            _drugbank_url(d),
                "link":           _drug_link_kind(d),
                "case_sensitive": False,
            }
            seen[key] = item
            out.append(item)

    if _BRAND_MATCHER:
        for _s, _e, brand in _BRAND_MATCHER.find(text):
            if brand in seen:
                continue
            d = _BRAND_LOOKUP.get(brand)
            if not d:
                continue
            # A case-sensitive matcher reports the phrase as written, so
            # the brand is already its own surface form.
            #
            # `relation` is the whole point of this branch. Until it
            # existed the brand popup was the generic's popup with a
            # different heading: hovering Clopine showed clozapine's
            # text under the word Clopine and never said the two were
            # the same drug. The reader who has just seen Clopine on a
            # ward drug chart is exactly the reader who does not yet
            # know that. It is derived from the lookup that resolved the
            # brand rather than authored per brand, so it cannot drift
            # from the entry it describes, and it costs nothing for the
            # 1,672 brand strings that would otherwise each need a line
            # written by hand.
            #
            # `url` and `link` still key on `d["generic"]`, because
            # DrugBank indexes generics and a chip pointing at a trade
            # name lands nowhere.
            item = {
                "name":           brand,
                "surfaces":       [brand],
                "summary":        d["summary"],
                "relation":       _brand_relation(brand, d),
                "form_kind":      "brand",
                "url":            _drugbank_url(d),
                "link":           _drug_link_kind(d),
                "case_sensitive": True,
            }
            seen[brand] = item
            out.append(item)

    return out
