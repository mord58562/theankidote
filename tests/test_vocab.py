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
    DRUG_SUMMARIES=_library.get("drug_summaries", {}),
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

    # ── Box model, read off the CSS in web/marker.js ─────────────────
    #
    # Rewritten at 2.2. The previous version modelled the summary text
    # and a 36px padding and nothing else, so it omitted every other
    # child of `.box`: the source label, the title, the UpToDate chip
    # row and the footer button. Measured against all 2,429 entries it
    # was never closer than 114px, median 153px, worst 278px. That is
    # why teriparatide estimated 488px against a 620px cap and still
    # rendered a scrollbar, and why `OVER_CAP_BUDGET` read 158/192 when
    # the true figures were 483/400.
    #
    # The CSS this mirrors, verbatim:
    #
    #   .box{padding:18px 22px;font-size:14px;line-height:1.55;
    #        max-width:480px;box-sizing:border-box}
    #     .label {font-size:12px; margin:0 0 7px}
    #     .title {font-size:17px; margin:0 0 9px}
    #     .summary{font-size:14px; line-height:1.6}
    #       .lede {margin:0 0 2px}
    #       .sec  {margin-top:7px}
    #         span.cat{display:inline-block;font-size:10.5px;
    #                  margin-bottom:1px}
    #         .secbody{margin-top:1px}
    #         ul.pts{margin-top:1px;padding-left:15px;line-height:1.4}
    #           li{margin-bottom:1px}  li:last-child{margin-bottom:0}
    #     .utd{margin-top:12px;padding-top:10px;border-top:1px}
    #       .utd-label{font-size:10px;margin:0 0 6px}
    #       .utd-chips{display:flex;flex-wrap:wrap;gap:5px}
    #         .utd-chip{padding:3px 10px;border:1px;font-size:12px}
    #     .open{display:block;margin-top:13px;padding:7px 12px;
    #           border:1px;font-size:13px}

    CONTENT_W = 480 - 22 - 22          # 436px of usable width

    # 436px at 14px system font; bullets lose 15px to .pts padding.
    CHARS_PER_LINE = 62
    BULLET_CHARS_PER_LINE = 58
    TITLE_CHARS_PER_LINE = 52          # 17px semibold is a wider glyph

    PADDING_PX = 18 + 18
    LABEL_PX = 12 * 1.55 + 7           # 25.60, lh inherited from .box
    TITLE_LINE_PX = 17 * 1.55          # 26.35
    TITLE_MARGIN_PX = 9
    OPEN_PX = 13 + 1 + 7 + (13 * 1.55) + 7 + 1        # 49.15

    UTD_HEAD_PX = 12 + 10 + 1 + (10 * 1.55) + 6       # 44.50
    UTD_ROW_PX = 3 + 3 + 1 + 1 + (12 * 1.55)          # 26.60
    UTD_GAP_PX = 5

    SECTION_MARGIN_PX = 7              # .sec{margin-top:7px}
    BODY_MARGIN_PX = 1                 # .secbody / .pts margin-top
    LEDE_MARGIN_PX = 2                 # .lede{margin-bottom:2px}
    # .cat is a 10.5px inline-block sitting on a line whose strut comes
    # from .summary's own 14px at line-height 1.6, so the strut decides.
    HEADER_PX = 14 * 1.6               # 22.40, not the 21 assumed before

    LINE_PX = 14 * 1.6                 # 22.40; .summary overrides .box
    BULLET_LINE_PX = 14 * 1.4          # 19.60; .pts sets line-height:1.4

    MAX_H = 900                        # must match _MAX_H in marker.js
    CEILING_PX = 1260

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
        self.assertEqual(
            int(m.group(1)), self.MAX_H,
            f"_MAX_H is {m.group(1)} in marker.js but {self.MAX_H} in "
            f"PopupHeightBudget. These are the renderer's cap and the "
            f"estimator's idea of it; if they drift, the backlog ratchet "
            f"below is counting against a cap that does not exist.")

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

    def _utd_rows(self, entry):
        """How many rows the UpToDate chips wrap onto.

        `.utd-chips` is a 436px flex row with a 5px gap; each chip is
        20px of padding and border plus its label. Chips are only
        rendered when `data-sp-utd` carries entries, so an entry without
        them pays nothing for the block at all.
        """
        utd = (entry or {}).get("utd") or []
        widths = []
        for pair in utd:
            if not pair:
                continue
            try:
                label = str(pair[0])
            except (TypeError, IndexError):
                continue
            widths.append(20 + 6.6 * len(label) + 2)
        if not widths:
            return 0
        rows, cur = 1, 0.0
        for w in widths:
            add = w if cur == 0 else w + self.UTD_GAP_PX
            if cur + add > self.CONTENT_W:
                rows, cur = rows + 1, w
            else:
                cur += add
        return rows

    def _estimate_px(self, summary, title="", entry=None):
        """Rendered height of a whole popup, structured the way it
        renders. Mirrors `_formatSummary` for the summary text and the
        CSS above for everything around it.

        `title` and `entry` are optional so the splitting tests can call
        this with a bare summary, but every caller that is deciding
        whether something fits the cap must pass both: the title wraps
        and the UpToDate chips are a real 71px when present.
        """
        import math
        height = self.PADDING_PX + self.LABEL_PX
        height += math.ceil(
            max(1, len(title)) / self.TITLE_CHARS_PER_LINE
        ) * self.TITLE_LINE_PX + self.TITLE_MARGIN_PX

        # The loose character class can swallow the space before a
        # qualifier, so "Sx (tetrad):" captures as "Sx " - strip it or
        # the section is not recognised and the block is costed as lede.
        labels = {l.strip().lower() for l in re.findall(
            r"(?:^|[;.]\s+)([A-Z][A-Za-z /-]{1,24})(?:\s*\([^()]{1,24}\))?:\s",
            summary)}
        parts = re.split(
            r"(?:^|[;.]\s+)(?=[A-Z][A-Za-z /-]{1,24}(?:\s*\([^()]{1,24}\))?:\s)",
            summary)
        for part in parts:
            if not part.strip():
                continue
            head, sep, body = part.partition(": ")
            base = re.sub(r"\s*\([^()]*\)\s*$", "", head)
            is_section = bool(sep) and base.lower() in labels
            if not is_section:
                body = part
                height += self.LEDE_MARGIN_PX
            else:
                height += self.SECTION_MARGIN_PX + self.HEADER_PX
            height += self.BODY_MARGIN_PX
            points = self._points(body)
            if is_section and self._worth_bulleting(points):
                for i, pt in enumerate(points):
                    height += math.ceil(
                        len(pt) / self.BULLET_CHARS_PER_LINE
                    ) * self.BULLET_LINE_PX
                    if i < len(points) - 1:
                        height += 1        # li margin, not on :last-child
            else:
                height += math.ceil(
                    len(body) / self.CHARS_PER_LINE) * self.LINE_PX

        rows = self._utd_rows(entry)
        if rows:
            height += (self.UTD_HEAD_PX + rows * self.UTD_ROW_PX
                       + (rows - 1) * self.UTD_GAP_PX)
        # `.open` is hidden only when there is no data-sp-url, which no
        # shipped entry is, so it is unconditional here.
        height += self.OPEN_PX
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
            yield name, entry["summary"], entry
        for acronym, cands in _acronyms._ACRONYMS.items():
            for expansion, _kw, summary in cands:
                yield f"{acronym} ({expansion})", summary, None
        for drug in _drugs._DRUGS:
            yield drug["generic"], drug["summary"], drug

    # Entries still rendering past the cap, by vocabulary. These are
    # debt, not a target: the popup scrolls for every one of them. The
    # numbers only ever go down. Raising one to make a change pass is
    # the failure mode this exists to catch - the point is that a
    # summary added tomorrow cannot quietly join them.
    #
    # Reset at 2.2, in the same commit that corrected the estimator
    # and raised the cap, because both numbers moved at once and neither
    # movement means anything on its own. Under the old text-only
    # estimate against a 620px cap these read 158 and 192. Under the
    # corrected model against 900px they are what you see here. The
    # backlog did not grow; it was always this size and was being
    # measured with a ruler that omitted 150px of chrome.
    # `preclinical` joins the ratchet at 2.2, at zero. Drug classes were
    # added to that vocabulary and they are long entries, so the budget is
    # worth holding at the point where it is still clean - a backlog is
    # much easier to prevent than to pay down, which is what the 122 and
    # 80 above are.
    OVER_CAP_BUDGET = {"conditions": 100, "drugs": 80, "acronyms": 0,
                       "preclinical": 0}

    def test_over_cap_backlog_only_shrinks(self):
        over = {"conditions": 0, "drugs": 0, "acronyms": 0,
                "preclinical": 0}
        seen = set()
        for entry in _conditions._LOOKUP.values():
            if entry["name"] in seen:
                continue
            seen.add(entry["name"])
            if self._estimate_px(entry["summary"], entry["name"],
                                 entry) > self.MAX_H:
                over["conditions"] += 1
        for acronym, cands in _acronyms._ACRONYMS.items():
            for expansion, _kw, summary in cands:
                if self._estimate_px(
                        summary, f"{acronym} ({expansion})") > self.MAX_H:
                    over["acronyms"] += 1
        pre_seen = set()
        for term in _preclinical.PRECLINICAL_TERMS:
            if term["name"] in pre_seen:
                continue
            pre_seen.add(term["name"])
            if self._estimate_px(term["summary"], term["name"],
                                 term) > self.MAX_H:
                over["preclinical"] += 1
        for drug in _drugs._DRUGS:
            if self._estimate_px(drug["summary"], drug["generic"],
                                 drug) > self.MAX_H:
                over["drugs"] += 1
        for vocab, budget in self.OVER_CAP_BUDGET.items():
            self.assertLessEqual(
                over[vocab], budget,
                f"{over[vocab]} {vocab} summaries now render past the "
                f"{self.MAX_H}px cap, up from {budget}; either shorten "
                f"the new entry or explain in the commit why the backlog "
                f"grew")
        for vocab, budget in self.OVER_CAP_BUDGET.items():
            if over[vocab] < budget:
                self.fail(
                    f"{vocab} backlog is down to {over[vocab]} from "
                    f"{budget} - good, now lower OVER_CAP_BUDGET to "
                    f"{over[vocab]} so it cannot drift back up")

    def test_no_summary_is_grossly_over_the_cap(self):
        for name, summary, entry in self._every_summary():
            px = self._estimate_px(summary, name, entry)
            self.assertLessEqual(
                round(px), self.CEILING_PX,
                f"{name} renders to roughly {round(px)}px, past the "
                f"{self.CEILING_PX}px ceiling; the popup caps at "
                f"{self.MAX_H}px so this would be mostly scrollbar")


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

    def test_drug_section_labels_are_recognised(self):
        """Same silent failure as the conditions above, on a table that
        did not exist before 2.2 and so was never covered."""
        pat = re.compile(r"(?:^|[;.]\s+)([A-Z][A-Za-z /-]{1,24}):\s")
        for canon, text in _rich.DRUG_SUMMARIES.items():
            for found in pat.findall(text):
                self.assertIn(
                    found.lower(), self.KNOWN_LABELS,
                    f"{canon}: section label '{found}:' is not one the "
                    f"popup renderer knows - it will render as body text")

    def test_each_drug_override_is_structured(self):
        pat = re.compile(r"(?:^|[;.]\s+)([A-Z][A-Za-z /-]{1,24}):\s")
        for canon, text in _rich.DRUG_SUMMARIES.items():
            self.assertGreaterEqual(
                len(pat.findall(text)), 3,
                f"{canon}: fewer than 3 sections, so it renders as one "
                f"long paragraph")

    def test_every_drug_override_reached_a_popup(self):
        """A key written against a name that was renamed out from under
        it never renders and says nothing. `build_library.py` refuses it,
        but a content edit does not run the build first."""
        for canon, text in _rich.DRUG_SUMMARIES.items():
            entry = _drugs._GENERIC_LOOKUP.get(canon.lower())
            self.assertIsNotNone(entry, f"{canon} is not a drug generic")
            self.assertEqual(entry["summary"], text, f"{canon} not applied")

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
