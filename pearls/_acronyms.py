# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.

"""Curated medical-acronym dictionary with context-based disambiguation.

Each entry maps an acronym to one or more candidate expansions.  When an
acronym appears in a card, every candidate is scored by how many of its
context keywords also appear in the card text; the highest scorer wins
(ties broken by listing order - most common expansion first).
"""
import re

from . import _library
from . import _matcher


# Acronyms that overlap with Roman numerals. On their own, "IV" means
# intravenous - but "Rome IV", "DSM-IV", "grade IV", "cranial nerve IV"
# and dozens of similar patterns are Roman numerals, not the drug route.
# Suppress the acronym when the immediately-preceding token is a known
# classifier so the popup doesn't misfire in those contexts.
_ROMAN_ACRONYMS = frozenset({
    "II", "III", "IV", "VI", "VII", "VIII", "IX", "XI", "XII",
})
# Acronyms that are also ordinary English words.
#
# Case-sensitive matching is what keeps most acronyms honest, but card
# authors capitalise for emphasis and for structure - "1st line: X OR Y"
# was expanding OR to Operating Room, and "ALL patients" to Acute
# Lymphoblastic Leukaemia. Both had exactly one candidate expansion, and
# a single-candidate acronym skips context scoring entirely, so nothing
# stood between the word and the popup.
#
# These expand only when at least one of the expansion's own context
# keywords is somewhere on the card. "Taken to OR under general
# anaesthesia" still resolves; "nifedipine OR indomethacin" no longer
# does.
_ENGLISH_WORD_ACRONYMS = frozenset({
    "OR", "ALL", "PET", "CAP", "AS", "TEN", "MEN", "ARM", "BED", "MAP",
    "LAST", "IF", "DID", "TI",
})

_ROMAN_CLASSIFIERS = frozenset({
    "rome", "dsm", "icd", "type", "class", "grade", "stage", "phase",
    "chapter", "factor", "figure", "level", "generation", "gen",
    "cranial", "nerve", "cn", "world", "war", "period", "line",
    "nyha", "mrc", "killip", "asa", "figo", "raiu",
    "los", "angeles", "salter", "salter-harris",
    "haemophilia", "hemophilia",
})


def _prev_token_lower(text: str, start: int) -> str:
    """The word immediately before `start`, lowercased.

    Skips trailing whitespace and hyphens so both 'Rome IV' and 'DSM-IV'
    resolve to 'rome' / 'dsm'. Returns '' when at start of string.
    """
    left = text[max(0, start - 40):start]
    # Strip trailing separator characters (whitespace, hyphens, en/em dashes).
    left = re.sub(r"[-\s‐-―]+$", "", left)
    if not left:
        return ""
    m = re.search(r"[A-Za-z][A-Za-z-]*$", left)
    return m.group(0).lower() if m else ""


# (expansion, context_keywords, brief description for tooltip)
# Loaded from data/library.json - see tools/build_library.py. The
# authoring copy of this vocabulary lives in content/, and is
# compiled rather than imported so content can ship without a
# new add-on release.
_ACRONYMS: dict = {k: [tuple(c) for c in v]
                   for k, v in _library.get("acronyms").items()}


# Matched by first-word index, not by an alternation over all 420 keys.
# Acronyms are matched case-sensitively - lower-casing them turns "ALL"
# into the English word - so the matcher is built in that mode, which
# also keeps the keys exactly as given. Longest-first still holds, so
# "AFib" wins over "AF"; that ordering is PhraseMatcher's contract too.
#
# Like _preclinical, this module was left behind when 2.1 moved the
# other vocabularies over, and kept paying O(text x alternatives):
# 2.6ms of every card scan.
_KEYS_BY_LEN = sorted(_ACRONYMS, key=len, reverse=True)
_MATCHER = _matcher.PhraseMatcher(_KEYS_BY_LEN, case_sensitive=True)

# A card that spells an acronym out got nothing. 272 of the 485
# expansions in this dictionary never fired, because the matcher above
# is built from the keys alone - so "CRP" opened a popup and
# "C-reactive protein" did not, on the same card, with the same content
# sitting behind it. Same shape as the other never-executed features
# found in this tree: the data was there, nothing looked at it.
#
# Expansions are matched case-insensitively, unlike the acronyms. The
# dictionary stores them in Title Case ("C-Reactive Protein") and cards
# write sentence case, so case-sensitive matching would close the gap
# on paper and leave it open in practice.
#
# Phrases that carry no information the reader lacks, or that appear in
# ordinary clinical prose often enough that underlining them is noise
# rather than help. "Emergency Department" is on every second card;
# "Carcinoembryonic Antigen" is on the ones that want explaining. The
# test is not whether the phrase is medical - it is whether a popup on
# it would ever be opened on purpose.
_EXPANSION_BLOCKLIST = frozenset(x.lower() for x in (
    # Places, units and routes
    "Emergency Department", "Intensive Care Unit",
    "Neonatal Intensive Care Unit", "Paediatric Intensive Care Unit",
    "Operating Room", "New South Wales", "Northern Territory",
    "International Units", "Nil Per Os", "Per Os", "Per Rectum",
    "Per Vaginam", "Pro Re Nata", "Four Times Daily", "Three Times Daily",
    "Twice Daily", "Once Daily",
    # Observations and anatomy a reader is not looking up
    "Heart Rate", "Respiratory Rate", "Blood Pressure",
    "Systolic Blood Pressure", "Fetal Heart Rate", "Cranial Nerve",
    "Left Atrium", "Right Atrium", "Left Ventricle", "Right Ventricle",
    "Cardiovascular System", "Range of Motion", "Direct Current",
    "Red Blood Cell", "White Blood Cell", "Blood Sugar Level",
    "Blood Glucose Level",
    # Statistics and process words that are not the entity
    "Odds Ratio", "Risk Ratio", "Clinical Practice Guideline",
    "Multidisciplinary Team", "Do Not Resuscitate", "PR Interval",
))


def _expansion_forms():
    """Expansion -> acronym, for the expansions worth underlining.

    Skips anything carrying a parenthetical or a slash: those are
    editorial notes to the reader of this file ("EGD in US terminology",
    "Toxoplasmosis/Rubella/CMV/Herpes/Other"), not phrases a card
    contains. Single words are skipped too - they are either the acronym
    again or an ordinary word.

    Where two acronyms claim one expansion - TOE and TEE are the same
    echocardiogram either side of the Pacific - the first listed wins,
    which is the same tie-break `resolve` already uses for candidates.
    """
    forms = {}
    for acronym, cands in _ACRONYMS.items():
        for expansion, _ctx, _desc in cands:
            if not expansion or "(" in expansion or "/" in expansion:
                continue
            if len(expansion.split()) < 2 or len(expansion) < 8:
                continue
            key = expansion.lower()
            if key in _EXPANSION_BLOCKLIST or key == acronym.lower():
                continue
            forms.setdefault(key, (acronym, expansion))
    return forms


_EXPANSIONS = _expansion_forms()
_EXP_MATCHER = _matcher.PhraseMatcher(
    sorted(_EXPANSIONS, key=len, reverse=True), case_sensitive=False)

# Lower-case each candidate's context list once at import.
_CONTEXTS = {
    k: [(exp, [w.lower() for w in ctx], desc) for (exp, ctx, desc) in cands]
    for k, cands in _ACRONYMS.items()
}


def resolve(card_text: str) -> list:
    """Find acronyms present in card text and pick the best expansion for each.
    Returns list of {acronym, expansion, description}.

    Context scoring exists to disambiguate, and 401 of the 420 acronyms
    have exactly one candidate, so for 95% of hits the loop below
    substring-searched the whole card for every context keyword in order
    to pick the only option available. Scoring now runs only where there
    is an actual choice, and `card_text.lower()` is deferred until then
    rather than computed for every card whether or not it is used.
    """
    matches = _MATCHER.find(card_text)
    # Expansions spelled out in full. Kept separate from `matches`
    # because they identify their own candidate - "Free Thyroxine" is
    # FT4 and nothing else - so they skip the context scoring the
    # ambiguous acronym keys need.
    spelled = {}
    for start, end, key in _EXP_MATCHER.find(card_text):
        acronym, expansion = _EXPANSIONS[key]
        spelled.setdefault(acronym, set()).add(card_text[start:end])
    if not matches and not spelled:
        return []
    # Suppress Roman-numeral false positives: if every occurrence of a
    # numeral acronym sits after a classifier (Rome, DSM, type, grade,
    # cranial nerve, etc.), it isn't the drug route - drop the whole
    # acronym from the results.
    found: set = set()
    for start, _end, k in matches:
        if k in _ROMAN_ACRONYMS:
            if _prev_token_lower(card_text, start) in _ROMAN_CLASSIFIERS:
                continue
        found.add(k)
    if not found and not spelled:
        return []
    text_lower = None
    out = []
    for acronym in found | set(spelled):
        candidates = _CONTEXTS[acronym]
        named = None
        if acronym in spelled:
            want = {s_.lower() for s_ in spelled[acronym]}
            for cand in candidates:
                if cand[0].lower() in want:
                    named = cand
                    break
        if named is not None:
            best = named
        elif len(candidates) == 1:
            best = candidates[0]
        else:
            if text_lower is None:
                text_lower = card_text.lower()
            best = candidates[0]
            best_score = -1
            for cand in candidates:
                _exp, ctx, _desc = cand
                score = 0
                for kw in ctx:
                    if kw in text_lower:
                        score += 1
                if score > best_score:
                    best_score = score
                    best = cand
        # An acronym that is also an English word has to earn its popup.
        if acronym in _ENGLISH_WORD_ACRONYMS and acronym not in spelled:
            if text_lower is None:
                text_lower = card_text.lower()
            if not any(kw.lower() in text_lower for kw in best[1]):
                continue
        expansion, _ctx, description = best
        out.append({
            "acronym": acronym,
            "expansion": expansion,
            "description": description,
            # The spelled-out forms actually present in this card, so
            # the reviewer can underline them. Empty when only the
            # acronym itself appeared.
            "surfaces": sorted(spelled.get(acronym, ())),
            # False when the card never wrote the acronym itself, which
            # is what stops `_acronym_terms` marking a three-letter key
            # that is not on the card.
            "acronym_present": acronym in found,
        })
    return out
