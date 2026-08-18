#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Integrity tests for the term databases.

The reviewer resolves several databases into one popup and the first to
claim a name wins, so a name appearing in two of them means one entry is
silently unreachable. That is invisible at runtime - the popup still
opens, it just shows the wrong definition - which makes it exactly the
kind of thing a test should catch. Three collisions had already
accumulated by the time this was written.

Run: python3 tests/test_vocab.py
"""

import importlib.util
import os
import re
import pathlib
import sys
import types
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)

sys.modules.setdefault("aqt", types.ModuleType("aqt"))
sys.modules["aqt"].mw = None
_pkg = types.ModuleType("pearls")
_pkg.__path__ = [os.path.join(_ROOT, "pearls")]
sys.modules["pearls"] = _pkg


def _load(name, relpath):
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(_ROOT, relpath))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_matcher = _load("pearls._matcher", "pearls/_matcher.py")
sys.modules["pearls._matcher"] = _matcher
_pkg._matcher = _matcher

# Every vocabulary module now reads `data/library.json` through this,
# so it has to be in place before any of them are loaded.
_library = _load("pearls._library", "pearls/_library.py")
sys.modules["pearls._library"] = _library
_pkg._library = _library

_conditions = _load("pearls._conditions", "pearls/_conditions.py")
_drugs = _load("pearls._drugs", "pearls/_drugs.py")
_preclinical = _load("pearls._preclinical", "pearls/_preclinical.py")
_descriptive = _load("pearls._descriptive", "pearls/_descriptive.py")
_psych = _load("pearls._psych", "pearls/_psych.py")
_signs = _load("pearls._signs", "pearls/_signs.py")
_acronyms = _load("pearls._acronyms", "pearls/_acronyms.py")
# The authoring copy of the rich summaries lives in content/ and is not
# shipped; what the add-on actually reads is the compiled copy in the
# library. Test the compiled copy - a test that passes against a file no
# user receives is worse than no test.
_rich = types.SimpleNamespace(
    RICH_SUMMARIES=_library.get("rich_summaries"),
    NEW_CONDITIONS=_library.get("new_conditions"))
# `_ncbi` imports the add-on package root (for `_log`), which would drag
# aqt into this harness. Only SECTION_MAP is needed, and reading it
# statically keeps the test dependency-free.
def _section_map():
    import ast
    with open(os.path.join(_ROOT, "pearls", "_ncbi.py"), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                getattr(t, "id", "") == "SECTION_MAP" for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError("SECTION_MAP not found in pearls/_ncbi.py")


SECTION_MAP = _section_map()
sys.modules["pearls._rich"] = _rich
_pkg._rich = _rich

# Resolution order in `_reviewer._preclinical_terms`, which is what
# decides who wins a collision.
VOCAB = [
    ("preclinical", {n.lower() for n in _preclinical._NAMES}),
    ("descriptive", {n.lower() for n in _descriptive._NAMES}),
    ("psych", {n.lower() for n in _psych._NAMES}),
    ("signs", {n.lower() for n in _signs._NAMES}),
]
OTHER = [
    ("conditions", {n.lower() for n in _conditions._NAMES}),
    ("drugs", {k.lower() for k in _drugs._GENERIC_LOOKUP}),
]


class NoCollisions(unittest.TestCase):
    def test_vocabulary_databases_are_disjoint(self):
        for i, (a_name, a) in enumerate(VOCAB):
            for b_name, b in VOCAB[i + 1:]:
                overlap = sorted(a & b)
                self.assertEqual(
                    overlap, [],
                    f"{a_name} and {b_name} both claim: {overlap}. "
                    f"One entry is unreachable - rename or drop the alias.")

    # Substances that are both a physiological concept and a drug, and
    # so legitimately appear in `_preclinical` and in `_drugs`. The
    # collision is resolved by order rather than by deletion: in
    # `_on_card_will_show` the drug list precedes the preclinical one,
    # so a card mentioning thiamine gets the DrugBank monograph, which
    # is the right answer clinically. Recorded here so these stay
    # accepted while any *new* overlap fails.
    ACCEPTED_SHADOWS = {
        ("preclinical", "drugs"): {
            "calcitriol", "folic acid", "glucagon", "pyridoxine",
            "thiamine", "vasopressin", "vitamin k",
        },
    }

    def test_vocabulary_does_not_shadow_conditions_or_drugs(self):
        for v_name, v in VOCAB:
            for o_name, o in OTHER:
                allowed = self.ACCEPTED_SHADOWS.get((v_name, o_name), set())
                overlap = sorted((v & o) - allowed)
                self.assertEqual(
                    overlap, [],
                    f"{v_name} shadows {o_name}: {overlap}. A condition or "
                    f"drug entry is usually the more useful answer - drop the "
                    f"alias, or add it to ACCEPTED_SHADOWS with a reason.")


class EntriesAreWellFormed(unittest.TestCase):
    DATASETS = (
        ("descriptive", _descriptive.DESCRIPTIVE_TERMS),
        ("psych", _psych.PSYCH_TERMS),
        ("signs", _signs.SIGN_TERMS),
    )

    def test_required_fields(self):
        for label, terms in self.DATASETS:
            for t in terms:
                self.assertTrue(t.get("name"), f"{label}: entry with no name")
                self.assertTrue(
                    t.get("summary"), f"{label}: {t.get('name')} has no summary")
                self.assertIsInstance(t.get("aliases", []), list)

    def test_names_are_unique_within_a_database(self):
        for label, terms in self.DATASETS:
            seen = set()
            for t in terms:
                for k in [t["name"]] + list(t.get("aliases") or []):
                    low = k.lower()
                    self.assertNotIn(
                        low, seen, f"{label}: '{k}' appears twice")
                    seen.add(low)

    def test_summaries_use_australian_spelling(self):
        """US spellings slip in from imported sources; the add-on is
        explicitly Australian-first, so catch them here."""
        # A plain substring test flags the correct spelling too, because
        # "oedematous" contains "edema" and "haemorrhage" contains
        # "hemorrhage". The lookbehind excludes the vowel that makes the
        # word Australian, so only the genuinely US form matches.
        banned = [
            (r"(?<![oa])edema", "oedema"),
            (r"(?<![oa])emorrhag", "haemorrhage"),
            (r"(?<![oa])emoglobin", "haemoglobin"),
            (r"(?<![oa])ematolog", "haematolog"),
            (r"\banemi", "anaemia"),
            (r"diarrhea", "diarrhoea"),
            (r"(?<![oa])esophag", "oesophag"),
            (r"(?<![oa])ediatric", "paediatric"),
            (r"\btumors?\b", "tumour"),
            (r"leukemi", "leukaemia"),
            (r"(?<![oa])ischemi", "ischaemi"),
            (r"orthopnea", "orthopnoea"),
            (r"(?<![oa])dyspnea", "dyspnoea"),
            (r"\bestrogen", "oestrogen"),
            (r"\betiolog", "aetiolog"),
            (r"(?<![oa])ynecolog", "gynaecolog"),
            (r"\bfetal\b", "foetal or fetal - be consistent"),
        ]
        for label, terms in self.DATASETS:
            for t in terms:
                low = t["summary"].lower()
                for pat, good in banned:
                    self.assertIsNone(
                        re.search(pat, low),
                        f"{label}: {t['name']} matches /{pat}/ - use '{good}'")

    def test_section_labels_are_recognised_by_the_renderer(self):
        """A `Label:` the popup renderer doesn't know renders as body
        text, which is a silent formatting failure. Keep this list in
        step with `_SECTION_LABELS` in web/marker.js.

        This is deliberately stricter than the renderer: it also flags
        ordinary prose that *looks* like a label ("Symmetry matters
        too:"). That prose renders correctly today, but only because no
        label happens to share its first word - adding one later would
        silently turn a sentence into a section header. Cheaper to
        forbid the shape than to debug that.
        """
        known = {
            "sx", "mx", "tx", "rx", "dx", "ix", "hx", "px", "ddx", "se", "ci",
            "moa", "pk", "pd", "definition", "epidemiology", "aetiology",
            "etiology", "causes", "mechanism", "mechanisms", "risk factors", "risk", "pathophysiology",
            "pathology", "classification", "types", "subtypes", "variants",
            "staging", "stages", "phases", "clinical features", "features",
            "presentation", "signs", "symptoms", "examination", "triggers",
            "associations", "genetics", "investigations", "workup",
            "diagnosis", "criteria", "screening", "differential",
            "management", "treatment", "monitoring", "follow-up",
            "complications", "prognosis", "secondary prevention", "prevention",
            "red flags",
            "extra-articular", "extrahepatic", "extraintestinal", "class",
            "indications", "contraindications", "cautions", "dose", "dosing",
            "route", "adverse effects", "interactions", "pregnancy",
            "breastfeeding", "renal", "hepatic", "paediatric", "elderly",
            "onset", "duration", "half-life", "metabolism", "excretion",
            "targets", "uses", "pbs", "australian notes", "note", "notes",
            "pearls", "mnemonic", "key point", "exam tip",
        }
        pat = re.compile(r"(?:^|[;.]\s+)([A-Z][A-Za-z /-]{1,24}):\s")
        for label, terms in self.DATASETS:
            for t in terms:
                for found in pat.findall(t["summary"]):
                    self.assertIn(
                        found.lower(), known,
                        f"{label}: {t['name']} uses section label "
                        f"'{found}:' which the popup renderer will not "
                        f"recognise")


class NoNearDuplicateConditions(unittest.TestCase):
    """One condition must not be entered twice under two spellings.

    The cross-database collision tests above do not see this, because
    both entries live in `_conditions`. It is the same silent failure
    though, and worse in one respect: which entry a reader gets depends
    on how their card happens to be worded. `Bell palsy` and `Bell's
    palsy` were both present through preview 11 with different
    summaries (277 vs 784 characters) and different accessions -
    NBK482290 is the Bell Palsy article, NBK549815 is Facial Nerve
    Palsy - so a card saying "Bell palsy" got a stub and the wrong
    chapter. `Raynaud phenomenon` and `Raynaud's phenomenon` were the
    same story.

    Possessive and non-possessive forms of an eponym are the case that
    actually occurs, so they are normalised together here. House
    convention is the non-possessive canonical name (Horner syndrome,
    Parkinson disease, Addison disease) with the possessive as an alias.
    """

    def _normalise(self, name):
        low = name.lower().replace("'s ", " ")
        if low.endswith("'s"):
            low = low[:-2]
        low = re.sub(r"[^a-z0-9 ]", " ", low)
        return re.sub(r"\s+", " ", low).strip()

    def test_no_two_entries_normalise_to_the_same_name(self):
        seen = {}
        for entry in _conditions._CONDITIONS:
            key = self._normalise(entry["name"])
            self.assertNotIn(
                key, seen,
                f"{entry['name']!r} and {seen.get(key)!r} are the same "
                f"condition entered twice; merge them and keep the other "
                f"spelling as an alias")
            seen[key] = entry["name"]

    def test_no_canonical_name_is_also_an_alias_elsewhere(self):
        owner = {}
        for entry in _conditions._CONDITIONS:
            for alias in entry.get("aliases", []):
                owner.setdefault(alias.lower(), []).append(entry["name"])
        for entry in _conditions._CONDITIONS:
            others = [n for n in owner.get(entry["name"].lower(), [])
                      if n != entry["name"]]
            self.assertFalse(
                others,
                f"{entry['name']!r} is a canonical name and also an alias "
                f"of {others} - one of them is unreachable")

    def test_no_accession_serves_two_conditions(self):
        owner = {}
        for entry in _conditions._CONDITIONS:
            nbk = entry.get("nbk")
            if not nbk:
                continue
            self.assertNotIn(
                nbk, owner,
                f"{nbk} is used by both {owner.get(nbk)!r} and "
                f"{entry['name']!r}; at most one can be correct")
            owner[nbk] = entry["name"]


class SectionLabelsAreLinkable(unittest.TestCase):
    """`_SECTION_LINKABLE` in web/marker.js must mirror `SECTION_MAP`.

    A section label is rendered as a click target that jumps to the
    matching heading in the StatPearls article. The jump is resolved
    through `_ncbi.SECTION_MAP`, so a label the renderer marks clickable
    but the map does not know opens the article at the top instead -
    a control that looks live and does nothing. Through preview 11
    every label was clickable and 47% of them resolved to nothing,
    "Clinical features", "Note" and "Red flags" alone accounting for
    124 of 138 dead clicks.

    The two lists live in different languages and cannot import each
    other, so this test is the only thing keeping them in step.
    """

    def setUp(self):
        with open(os.path.join(_ROOT, "web", "marker.js"),
                  encoding="utf-8") as fh:
            self.js = fh.read()

    def _linkable(self):
        block = re.search(r"var _SECTION_LINKABLE = \{\};(.*?)\}\)\(\);",
                          self.js, re.S)
        self.assertIsNotNone(block, "_SECTION_LINKABLE not found in marker.js")
        return set(re.findall(r'"([^"]+)"', block.group(1)))

    def test_linkable_matches_section_map(self):
        self.assertEqual(
            self._linkable(), set(SECTION_MAP),
            "web/marker.js `_SECTION_LINKABLE` and pearls/_ncbi.py "
            "`SECTION_MAP` have drifted apart")

    def test_every_linkable_label_resolves_to_headings(self):
        for label in self._linkable():
            self.assertTrue(
                SECTION_MAP.get(label.strip().rstrip(":").lower(), []),
                f"{label!r} is rendered as a click target but resolves to "
                f"no heading, so the click opens the article at the top")

    def test_editorial_labels_are_not_clickable(self):
        """Labels that are this add-on's own synthesis have no honest
        target. Pointing them at a plausible-looking heading is the
        heading-level version of inventing an NBK accession."""
        for label in ("note", "notes", "red flags", "mnemonic",
                      "key point", "exam tip", "pbs", "australian notes"):
            self.assertNotIn(
                label, SECTION_MAP,
                f"{label!r} has no corresponding StatPearls heading and "
                f"must not be made clickable")


class AcronymSummaries(unittest.TestCase):
    """`_acronyms` had no structural coverage at all until now.

    Its summaries go through the same popup renderer as conditions, so
    the same rules bind, but nothing was enforcing them: 20 entries
    carried labels the renderer does not know ("First-line:",
    "Laboratory:", "Admission criteria:"), each rendering as body text
    rather than a section header, silently.
    """

    ENTRIES = [(acr, exp, summary)
               for acr, cands in _acronyms._ACRONYMS.items()
               for exp, _kw, summary in cands]

    LABEL_RE = re.compile(r"(?:^|[;.]\s+)([A-Z][A-Za-z /-]{1,24}):\s")

    def _registered(self):
        with open(os.path.join(_ROOT, "web", "marker.js"),
                  encoding="utf-8") as fh:
            js = fh.read()
        # The array closes with `].sort(...)`, not `];` - stopping at the
        # first `];` runs on into unrelated code and silently produces a
        # permissive label set that would let a bad label pass.
        block = re.search(r"var _SECTION_LABELS = \[(.*?)\n  \]\.sort\(",
                          js, re.S)
        self.assertIsNotNone(block, "_SECTION_LABELS not found in marker.js")
        labels = {s.lower() for s in re.findall(r'"([^"]+)"', block.group(1))}
        for lab in labels:
            self.assertRegex(
                lab, r"^[a-z][a-z /-]*$",
                f"extraction picked up {lab!r}, which is not a section label")
        return labels

    def test_section_labels_are_registered(self):
        known = self._registered()
        for acr, exp, summary in self.ENTRIES:
            for found in self.LABEL_RE.findall(summary):
                self.assertIn(
                    found.lower(), known,
                    f"{acr} ({exp}) uses section label '{found}:' which the "
                    f"popup renderer does not know, so it renders as body "
                    f"text")

    def test_summaries_stay_glance_sized(self):
        for acr, exp, summary in self.ENTRIES:
            self.assertLessEqual(
                len(summary), 1200,
                f"{acr} ({exp}) summary is {len(summary)} characters; the "
                f"popup orients and hands off to the article")

    def test_summaries_use_australian_spelling(self):
        banned = [
            (r"\banemia\b", "anaemia"), (r"\bedema\b", "oedema"),
            (r"\bdiarrhea\b", "diarrhoea"), (r"\bhemorrhage\b", "haemorrhage"),
            (r"\bischemi", "ischaemi"), (r"\besophag", "oesophag"),
            (r"\bpediatric", "paediatric"), (r"\bceliac\b", "coeliac"),
            (r"\btumor\b", "tumour"),
            (r"\bacetaminophen\b", "paracetamol"),
            (r"\balbuterol\b", "salbutamol"),
            (r"\bepinephrine\b", "adrenaline"),
        ]
        for acr, exp, summary in self.ENTRIES:
            low = summary.lower()
            for pat, good in banned:
                self.assertIsNone(
                    re.search(pat, low),
                    f"{acr} ({exp}) matches /{pat}/ - use '{good}'")

    def test_no_empty_summaries(self):
        for acr, exp, summary in self.ENTRIES:
            self.assertTrue(summary.strip(),
                            f"{acr} ({exp}) has an empty summary")


class PopupHeightBudget(unittest.TestCase):
    """The popup must not grow, whatever the content does.

    Bullet rendering makes a section taller than the paragraph it
    replaced - each point starts its own line instead of flowing - by a
    mean of about 85px across the structured summaries and over 300px
    for the worst of them. Before this the box had `overflow-y:auto`
    but no height limit except the viewport, so on a tall window it
    simply grew. The popup orients and hands off to the article
    underneath; one that fills the screen competes with it.

    Two guarantees, because either alone is insufficient: `_MAX_H` in
    web/marker.js caps what can be rendered no matter what, and the
    estimate below stops content being authored so far past the cap
    that the popup becomes a scrolling document.
    """

    # 480px box less 22px padding each side, 14px system font.
    CHARS_PER_LINE = 62
    BULLET_CHARS_PER_LINE = 58
    LINE_PX = 21.7
    BULLET_LINE_PX = 19.6      # .pts sets line-height:1.4
    HEADER_PX = 21
    PADDING_PX = 36
    CEILING_PX = 1000

    def _marker(self):
        with open(os.path.join(_ROOT, "web", "marker.js"),
                  encoding="utf-8") as fh:
            return fh.read()

    def test_popup_has_a_hard_height_cap(self):
        js = self._marker()
        m = re.search(r"var _MAX_H = (\d+);", js)
        self.assertIsNotNone(
            m, "web/marker.js no longer defines _MAX_H; the popup would "
               "grow to fit its content on a tall window")
        self.assertLessEqual(
            int(m.group(1)), 640,
            "_MAX_H has been raised; the popup is allowed to get taller")

    def test_cap_is_applied_unconditionally(self):
        js = self._marker()
        block = re.search(r"function _position\(el\) \{(.*?)\n  \}", js, re.S)
        self.assertIsNotNone(block, "_position not found in marker.js")
        body = block.group(1)
        self.assertIn(
            "_MAX_H", body,
            "_position does not reference the cap, so it only limits height "
            "when the viewport happens to force it")

    CONNECTIVE = re.compile(
        r"^(and|or|but|which|who|whereas|while|though|although|then|so|"
        r"because|since|with|without|as|if|when|whereby|thereby|hence|"
        r"thus)\b", re.I)

    def _split_top(self, body, sep):
        parts, depth, cur = [], 0, ""
        for ch in body:
            if ch in "([":
                depth += 1
            elif ch in ")]":
                depth = max(0, depth - 1)
            if ch == sep and depth == 0:
                parts.append(cur)
                cur = ""
                continue
            cur += ch
        parts.append(cur)
        return [p.strip(" ,;.") for p in parts if p.strip(" ,;.")]

    # Mirrors `_MIN_POINTS` / `_MIN_LONGEST` in web/marker.js. Changing
    # either here without changing it there makes this whole class stop
    # predicting anything.
    MIN_POINTS = 4
    MIN_LONGEST = 40

    def _points(self, body):
        """Mirror of `_splitPoints` in web/marker.js."""
        semi = self._split_top(body, ";")
        if len(semi) > 1:
            return semi
        comma = self._split_top(body, ",")
        if len(comma) >= self.MIN_POINTS and all(
                len(p) >= 3 and not self.CONNECTIVE.match(p) for p in comma):
            return comma
        return semi

    def _worth_bulleting(self, points):
        """Mirror of `_worthBulleting` in web/marker.js."""
        return (len(points) >= self.MIN_POINTS
                and any(len(p) >= self.MIN_LONGEST for p in points))

    def _estimate_px(self, summary):
        """Rendered height of a summary, structured the way the popup
        renders it. Deliberately mirrors `_formatSummary` rather than
        measuring characters, because character count stopped predicting
        height once sections became bulleted."""
        import math
        # The loose character class can swallow the space before a
        # qualifier, so "Sx (tetrad):" captures as "Sx " - strip it or
        # the section is not recognised and the block is costed as lede.
        labels = {l.strip().lower() for l in re.findall(
            r"(?:^|[;.]\s+)([A-Z][A-Za-z /-]{1,24})(?:\s*\([^()]{1,24}\))?:\s",
            summary)}
        parts = re.split(
            r"(?:^|[;.]\s+)(?=[A-Z][A-Za-z /-]{1,24}(?:\s*\([^()]{1,24}\))?:\s)",
            summary)
        height = self.PADDING_PX
        for part in parts:
            if not part.strip():
                continue
            head, sep, body = part.partition(": ")
            base = re.sub(r"\s*\([^()]*\)\s*$", "", head)
            is_section = bool(sep) and base.lower() in labels
            if not is_section:
                body = part
            else:
                height += self.HEADER_PX
            points = self._points(body)
            if is_section and self._worth_bulleting(points):
                for pt in points:
                    height += math.ceil(
                        len(pt) / self.BULLET_CHARS_PER_LINE
                    ) * self.BULLET_LINE_PX + 1
            else:
                height += math.ceil(
                    len(body) / self.CHARS_PER_LINE) * self.LINE_PX + 1
        return height

    def _every_summary(self):
        """Every summary the popup can render, base entries included.

        This used to walk `RICH_SUMMARIES`, the acronyms and the drugs,
        which is to say the three vocabularies that were least likely to
        be the problem. The 774 conditions carrying their original
        unstructured summary - where the length actually lives - were
        not looked at, so Lung cancer shipped through preview 14
        rendering at roughly 1,200px against a ceiling this test claims
        to enforce at 1,000px.
        """
        seen = set()
        for entry in _conditions._LOOKUP.values():
            name = entry["name"]
            if name in seen:
                continue
            seen.add(name)
            yield name, entry["summary"]
        for acronym, cands in _acronyms._ACRONYMS.items():
            for expansion, _kw, summary in cands:
                yield f"{acronym} ({expansion})", summary
        for drug in _drugs._DRUGS:
            yield drug["generic"], drug["summary"]

    # Entries still rendering past the 620px cap, by vocabulary. These
    # are debt, not a target: the popup scrolls for every one of them.
    # The numbers only ever go down. Raising one to make a change pass
    # is the failure mode this exists to catch - the point is that a
    # summary added tomorrow cannot quietly join them.
    OVER_CAP_BUDGET = {"conditions": 184, "drugs": 192, "acronyms": 0}

    def test_over_cap_backlog_only_shrinks(self):
        over = {"conditions": 0, "drugs": 0, "acronyms": 0}
        seen = set()
        for entry in _conditions._LOOKUP.values():
            if entry["name"] in seen:
                continue
            seen.add(entry["name"])
            if self._estimate_px(entry["summary"]) > 620:
                over["conditions"] += 1
        for cands in _acronyms._ACRONYMS.values():
            for _e, _kw, summary in cands:
                if self._estimate_px(summary) > 620:
                    over["acronyms"] += 1
        for drug in _drugs._DRUGS:
            if self._estimate_px(drug["summary"]) > 620:
                over["drugs"] += 1
        for vocab, budget in self.OVER_CAP_BUDGET.items():
            self.assertLessEqual(
                over[vocab], budget,
                f"{over[vocab]} {vocab} summaries now render past the "
                f"620px cap, up from {budget}; either shorten the new "
                f"entry or explain in the commit why the backlog grew")
        for vocab, budget in self.OVER_CAP_BUDGET.items():
            if over[vocab] < budget:
                self.fail(
                    f"{vocab} backlog is down to {over[vocab]} from "
                    f"{budget} - good, now lower OVER_CAP_BUDGET to "
                    f"{over[vocab]} so it cannot drift back up")

    def test_no_summary_is_grossly_over_the_cap(self):
        entries = list(self._every_summary())
        for name, summary in entries:
            px = self._estimate_px(summary)
            self.assertLessEqual(
                round(px), self.CEILING_PX,
                f"{name} renders to roughly {round(px)}px, past the "
                f"{self.CEILING_PX}px ceiling; the popup caps at "
                f"{620}px so this would be mostly scrollbar")


class BulletSplitting(unittest.TestCase):
    """Guards on the comma fallback in `_splitPoints`.

    Semicolons are the deliberate list separator, but almost nothing
    outside the structured condition summaries uses them - every drug
    entry enumerates with commas, so before the fallback existed no
    drug popup ever bulleted. Commas are also ordinary punctuation
    though, so splitting on them blindly turns a sentence into
    nonsense: "caution with macrolides, azoles" becomes a bullet
    reading "azoles".

    This mirrors the JavaScript so the guards can be reasoned about
    here; `PopupHeightBudget._points` is the same logic and both must
    match `_splitPoints` in web/marker.js.
    """

    def _points(self, body):
        return PopupHeightBudget()._points(body)

    def test_semicolon_lists_split(self):
        self.assertEqual(len(self._points("alpha; beta; gamma")), 3)

    def test_comma_list_of_four_splits(self):
        self.assertEqual(
            self._points("myalgia, raised LFTs, dark urine, "
                         "rhabdomyolysis (rare)"),
            ["myalgia", "raised LFTs", "dark urine",
             "rhabdomyolysis (rare)"])

    def test_comma_list_of_three_stays_prose(self):
        self.assertEqual(
            len(self._points("myalgia, raised LFTs, rhabdomyolysis")), 1,
            "three comma items are cheaper to read - and 40px cheaper to "
            "render - as one line of prose than as three bullets")

    def test_two_comma_items_stay_prose(self):
        self.assertEqual(
            len(self._points("caution with macrolides, azoles")), 1,
            "a two-item comma phrase must not bullet - the second half "
            "reads as a fragment on its own")

    def test_connective_blocks_the_split(self):
        for body in (
            "started within 72 hr, shortens the course, and improves recovery",
            "give fluids, cool actively, then reassess",
            "raised CK, raised LFTs, which confirms the diagnosis",
        ):
            self.assertEqual(
                len(self._points(body)), 1,
                f"{body!r} is a sentence with commas, not a list")

    def test_commas_inside_brackets_are_protected(self):
        pts = self._points(
            "hyperthermia (>38, often >40), rigidity (lead pipe), "
            "clonus (inducible or ocular), coma")
        self.assertEqual(len(pts), 4)
        self.assertIn("hyperthermia (>38, often >40)", pts)


class BulletWorthiness(unittest.TestCase):
    """Splitting a body into points is not the same as bulleting it.

    A bullet occupies a whole line whatever it contains, so four
    two-word items cost about 80px where the same words set as prose
    cost 22px. Across the shipped library this is the single strongest
    predictor of overflow: summaries that fit the popup carry a median
    of 4 bullets and those that scroll carry 10, at an identical median
    length. Character budgets do not discriminate between the two at
    all, which is why the old `_rich.py` house rule - cap at 1,200
    characters, aim for 1,050 - produced entries that scrolled anyway.

    So a list has to earn the space: four or more points, at least one
    of them long enough to be worth scanning for.
    """

    def _worth(self, body):
        b = PopupHeightBudget()
        return b._worth_bulleting(b._points(body))

    def test_four_substantial_points_bullet(self):
        self.assertTrue(self._worth(
            "renal loss through diuretics or hyperaldosteronism; "
            "gastrointestinal loss through vomiting or diarrhoea; "
            "shift into cells with insulin or beta-2 agonists; "
            "poor intake in the malnourished"))

    def test_four_short_points_stay_prose(self):
        self.assertFalse(
            self._worth("fever; rash; arthralgia; malaise"),
            "four one-word bullets spend four lines saying what fits on "
            "one")

    def test_three_substantial_points_stay_prose(self):
        self.assertFalse(self._worth(
            "hypertension is the dominant risk factor by a wide margin; "
            "bicuspid aortic valve in the younger patient; "
            "Marfan and Ehlers-Danlos syndromes"))

    def test_the_estimator_and_the_renderer_agree(self):
        """`_MIN_POINTS` and `_MIN_LONGEST` are duplicated in marker.js.

        Nothing imports one from the other, so the only thing keeping
        the height estimate honest is this assertion.
        """
        js = (pathlib.Path(__file__).resolve().parent.parent
              / "web" / "marker.js").read_text(encoding="utf-8")
        for const, value in (("_MIN_POINTS", PopupHeightBudget.MIN_POINTS),
                             ("_MIN_LONGEST", PopupHeightBudget.MIN_LONGEST)):
            m = re.search(r"var\s+" + const + r"\s*=\s*(\d+)", js)
            self.assertIsNotNone(m, f"{const} not found in web/marker.js")
            self.assertEqual(
                int(m.group(1)), value,
                f"{const} is {m.group(1)} in marker.js but {value} in "
                f"PopupHeightBudget; the height estimate is now fiction")


class NoteRendersLast(unittest.TestCase):
    """`Note:` is an aside and belongs after the clinical sections.

    In the shipped library it usually is not: 29 conditions and 21 drug
    entries write it immediately before `Red flags:`, which buries the
    safety-critical section underneath an aside. Rather than rewrite
    fifty summaries and rely on the convention holding, `_formatSummary`
    moves it to the end at render time - which also covers downloaded
    content, written by whoever published it.

    Reordering does not change any section's height, so
    `PopupHeightBudget` needs no matching logic; that is why this lives
    in its own class rather than in the estimator.
    """

    TRAILING = ("note", "notes")

    def _reorder(self, labels):
        """Mirror of the partition in `_formatSummary`."""
        bare = [re.sub(r"\s*\([^()]*\)\s*$", "", l).lower() for l in labels]
        keep = [l for l, b in zip(labels, bare) if b not in self.TRAILING]
        tail = [l for l, b in zip(labels, bare) if b in self.TRAILING]
        return keep + tail

    def test_the_renderer_partitions_trailing_labels(self):
        js = (pathlib.Path(__file__).resolve().parent.parent
              / "web" / "marker.js").read_text(encoding="utf-8")
        self.assertIn("_TRAILING", js,
                      "marker.js no longer moves Note to the end")
        self.assertLess(
            js.index("_TRAILING"), js.index('var html = ""'),
            "the reorder must happen before the render loop, or it has "
            "no effect on the output")

    def test_note_moves_behind_red_flags(self):
        self.assertEqual(
            self._reorder(["Sx", "Note", "Red flags"]),
            ["Sx", "Red flags", "Note"])

    def test_a_qualified_note_still_moves(self):
        self.assertEqual(
            self._reorder(["Note (caveat)", "Complications"]),
            ["Complications", "Note (caveat)"])

    def test_sections_that_are_not_notes_keep_their_order(self):
        original = ["Causes", "Sx", "Ix", "Mx", "Red flags"]
        self.assertEqual(self._reorder(original), original)

    def test_every_shipped_summary_ends_on_its_note(self):
        """Applied to the real library, not to invented examples."""
        pattern = re.compile(
            r"(?:^|[;.]\s+)([A-Z][A-Za-z /-]{1,24})"
            r"(?:\s*\([^()]{1,24}\))?:\s")
        checked = 0
        seen = set()
        entries = []
        for entry in _conditions._LOOKUP.values():
            if entry["name"] in seen:
                continue
            seen.add(entry["name"])
            entries.append((entry["name"], entry["summary"]))
        entries += [(d["generic"], d["summary"]) for d in _drugs._DRUGS]
        for name, summary in entries:
            labels = [l.strip() for l in pattern.findall(summary)]
            if not any(l.lower() in self.TRAILING for l in labels):
                continue
            checked += 1
            after = self._reorder(labels)
            self.assertIn(
                after[-1].lower().split(" (")[0], self.TRAILING,
                f"{name}: reordering left {after[-1]!r} after the note")
        self.assertGreater(checked, 40,
                           "expected many summaries to carry a Note")


class QualifiedSectionLabels(unittest.TestCase):
    """`Sx (tetrad):` must be recognised as the section `Sx`.

    The label pattern allowed no punctuation, so a label carrying a
    parenthetical qualifier was not matched at all and its whole block
    collapsed silently back into the lede - which is what put the
    neuroleptic malignant syndrome tetrad and lab panel into the
    opening paragraph.
    """

    LABEL_RE = re.compile(
        r"(?:^|[;.]\s+)([A-Z][A-Za-z /-]{1,24})(?:\s*\([^()]{1,24}\))?:\s")

    def test_pattern_matches_a_qualified_label(self):
        found = [f.strip() for f in
                 self.LABEL_RE.findall("Foo. Sx (tetrad): fever, rigidity, coma")]
        self.assertIn("Sx", found)

    def test_marker_js_strips_the_qualifier_for_the_jump(self):
        with open(os.path.join(_ROOT, "web", "marker.js"),
                  encoding="utf-8") as fh:
            js = fh.read()
        self.assertTrue(
            'data-sec="\' + _esc(secKey)' in js,
            "data-sec must carry the bare label; SECTION_MAP is keyed on "
            "'Sx', not 'Sx (tetrad)'")
        self.assertRegex(
            js, r"var secKey = p\.label\.replace\(",
            "secKey must be derived by stripping the qualifier")


class RichSummaries(unittest.TestCase):
    """`_rich.RICH_SUMMARIES` is applied by canonical name, so a typo or
    a renamed condition silently does nothing - the popup keeps its old
    summary and no error is raised anywhere."""

    KNOWN_LABELS = {
        "definition", "epidemiology", "aetiology", "etiology", "causes",
        "mechanism", "mechanisms", "risk factors", "risk", "pathophysiology",
        "pathology", "classification", "types", "subtypes", "variants",
        "staging", "stages", "phases", "clinical features", "features", "presentation",
        "signs", "symptoms", "examination", "triggers", "associations",
        "genetics", "investigations", "workup", "diagnosis", "criteria",
        "screening", "differential", "management", "treatment", "monitoring",
        "follow-up", "complications", "prognosis", "secondary prevention",
        "prevention", "red flags",
        "extra-articular", "extrahepatic", "extraintestinal", "class", "indications", "contraindications", "cautions", "dose",
        "dosing", "route", "adverse effects", "interactions", "pregnancy",
        "breastfeeding", "renal", "hepatic", "paediatric", "elderly", "onset",
        "duration", "half-life", "metabolism", "excretion", "targets", "uses",
        "pbs", "australian notes", "note", "notes", "pearls", "mnemonic",
        "key point", "exam tip", "sx", "mx", "tx", "rx", "dx", "ix", "hx",
        "px", "ddx", "se", "ci", "moa", "pk", "pd",
    }

    def test_every_override_targets_a_real_condition(self):
        missed = sorted(set(_rich.RICH_SUMMARIES) - _conditions._RICH_APPLIED)
        self.assertEqual(
            missed, [],
            f"these overrides matched no condition and are dead: {missed}")

    def test_overrides_are_keyed_on_the_canonical_name(self):
        """An alias key applies, but titles the popup something else.

        `_LOOKUP` is keyed on every alias, so an override written under
        an alias does get merged and `test_every_override_targets_a_real
        _condition` passes. What it does not do is change the title:
        `resolve()` returns `c["name"]`, so a summary written about
        community-acquired pneumonia rendered under the key
        "Community-acquired pneumonia" appears beneath the heading
        "Pneumonia", and one written about acute coronary syndrome
        appears beneath "Myocardial infarction". The content is then
        narrower than the heading claims, silently. Eight overrides
        shipped this way through preview 14.
        """
        for name in _rich.RICH_SUMMARIES:
            entry = _conditions._LOOKUP.get(name.lower())
            if entry is None:
                continue
            self.assertEqual(
                entry["name"], name,
                f"override keyed {name!r} but the popup titles it "
                f"{entry['name']!r}; key it on the canonical name, or "
                f"the summary and the heading disagree")

    def test_overrides_actually_replaced_the_summary(self):
        for canon, text in _rich.RICH_SUMMARIES.items():
            entry = _conditions._LOOKUP.get(canon.lower())
            self.assertIsNotNone(entry, f"{canon} not in conditions")
            self.assertEqual(entry["summary"], text, f"{canon} not applied")

    def test_section_labels_are_recognised(self):
        pat = re.compile(r"(?:^|[;.]\s+)([A-Z][A-Za-z /-]{1,24}):\s")
        for canon, text in _rich.RICH_SUMMARIES.items():
            for found in pat.findall(text):
                self.assertIn(
                    found.lower(), self.KNOWN_LABELS,
                    f"{canon}: section label '{found}:' is not one the "
                    f"popup renderer knows - it will render as body text")

    MAX_CHARS = 1200

    def test_overrides_stay_glance_sized(self):
        """The popup orients you and hands off to the full StatPearls
        article; it does not replace it. A summary long enough to scroll
        has stopped being a summary. The first draft of this layer ran
        to 2,337 characters, which is the mistake this guards against -
        structure makes the length findable, it is not a licence to keep
        adding."""
        oversize = {k: len(v) for k, v in _rich.RICH_SUMMARIES.items()
                    if len(v) > self.MAX_CHARS}
        self.assertEqual(
            oversize, {},
            f"over {self.MAX_CHARS} chars: {oversize}. Target median is ~1050; "
            f"cut content rather than raising the ceiling.")

    def test_each_override_is_structured(self):
        """An override with no sections is just a long paragraph, which
        is the problem this layer exists to fix."""
        pat = re.compile(r"(?:^|[;.]\s+)([A-Z][A-Za-z /-]{1,24}):\s")
        for canon, text in _rich.RICH_SUMMARIES.items():
            self.assertGreaterEqual(
                len(pat.findall(text)), 3,
                f"{canon} has fewer than 3 sections - not worth an override")

    def test_australian_spelling(self):
        banned = [(r"(?<![oa])edema", "oedema"), (r"\banemi", "anaemia"),
                  (r"(?<![oa])esophag", "oesophag"), (r"\btumors?\b", "tumour"),
                  (r"diarrhea", "diarrhoea"), (r"leukemi", "leukaemia"),
                  (r"(?<![oa])ischemi", "ischaemi"), (r"\betiolog", "aetiolog"),
                  (r"(?<![oa])ediatric", "paediatric")]
        for canon, text in _rich.RICH_SUMMARIES.items():
            low = text.lower()
            for pat, good in banned:
                self.assertIsNone(re.search(pat, low),
                                  f"{canon} matches /{pat}/ - use '{good}'")


class AustralianFirst(unittest.TestCase):
    """The add-on is Australian-first, which is a claim about framing as
    well as spelling.

    A definition reading "UK/AU term for CBC" makes the US name the real
    thing and the Australian one a regional variant of it. Seven acronym
    entries were written that way. The reverse - a US acronym entry
    pointing at the Australian term - is correct and stays.
    """

    SUBORDINATING = [
        r"UK/AU term for",
        r"\bUK term for",
        r"Australian term for",
        r"British term for",
        r"Commonwealth term for",
    ]

    def test_no_definition_subordinates_australian_usage(self):
        src = open(os.path.join(_ROOT, "pearls", "_acronyms.py")).read()
        for pat in self.SUBORDINATING:
            hits = [m.group(0) for m in re.finditer(pat, src)]
            self.assertEqual(
                hits, [],
                f"/{pat}/ frames the Australian term as a variant of the US "
                f"one - define it directly and note the US name as an aside.")


class StatPearlsLinks(unittest.TestCase):
    """StatPearls is a US publication, so a search built from an
    Australian spelling finds nothing - and 189 conditions carry no
    direct NBK accession and fall back to search."""

    def test_search_queries_use_us_spelling(self):
        cases = [
            ("Iron deficiency anaemia", "Iron deficiency anemia"),
            ("Autoimmune haemolytic anaemia", "Autoimmune hemolytic anemia"),
            ("Coeliac disease", "Celiac disease"),
            ("Oesophageal varices", "Esophageal varices"),
            ("Pulmonary oedema", "Pulmonary edema"),
            ("Hypercalcaemia", "Hypercalcemia"),
            ("Asthma", "Asthma"),
        ]
        for au, us in cases:
            self.assertEqual(_conditions._us_spelling(au), us)

    def test_new_conditions_carry_no_unverified_accession(self):
        """An NBK id that belongs to a different article opens the wrong
        page confidently, which is worse than falling back to search.
        Three invented ids shipped in preview 8 before this was caught."""
        for entry in _rich.NEW_CONDITIONS:
            self.assertFalse(
                entry.get("nbk"),
                f"{entry['name']} carries an nbk - verify it against the "
                f"real article before adding it, or leave it out.")


class ResolversWork(unittest.TestCase):
    def test_dermatology_card(self):
        text = ("Photodistributed poikiloderma - hyperpigmentations + "
                "hypopigmentation + telangiectasias + epidermal atrophy")
        names = {r["name"] for r in _descriptive.resolve(text)}
        for expected in ("Poikiloderma", "Telangiectasia", "Epidermal atrophy"):
            self.assertIn(expected, names)

    def test_mental_state_card(self):
        text = ("Speech pressured with flight of ideas. Affect labile. "
                "Derailment and thought blocking. Grandiose delusions.")
        names = {r["name"] for r in _psych.resolve(text)}
        for expected in ("Flight of ideas", "Derailment", "Thought blocking",
                         "Grandiose delusion"):
            self.assertIn(expected, names)

    def test_no_match_returns_empty(self):
        for mod in (_descriptive, _psych):
            self.assertEqual(mod.resolve(""), [])
            self.assertEqual(mod.resolve("qqqq zzzz"), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
