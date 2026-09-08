# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""Tests for the span the reviewer writes into a card.

`pearls/_reviewer.py` imports `aqt` at module scope, so for most of this
project's life it could not be imported under test at all and nothing
here was covered. That is how `data-sp-link` came to be dropped from the
lookup dict: five term builders set it, the span writer read it, and the
dict between them did not carry it, so `isArticle` in `web/marker.js`
was always false. Every popup then claimed an article whether or not one
existed, and the badge credited the add-on for summaries StatPearls did
write. It shipped, and the release notes described the fix as done.

Two stubs are enough to reach the matcher: a fake `aqt`, and a synthetic
parent package so `_reviewer`'s `from .. import _config, _log` resolves.
Nothing on this path needs a running Anki.
"""
import re
import sys
import types
import unittest
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent


class _Hook:
    def append(self, *a, **k):
        pass

    def remove(self, *a, **k):
        pass


class _Hooks:
    def __getattr__(self, _name):
        return _Hook()


def _load_reviewer():
    # Fill in what is missing rather than installing a stub only when
    # `aqt` is absent entirely. `test_vocab` registers its own bare
    # `aqt` carrying just `mw` at import time, and unittest imports
    # every test module before running any of them - so "is aqt
    # registered" was always true here by the time this ran, and the
    # stub that would have supplied `gui_hooks` was skipped.
    aqt = sys.modules.get("aqt") or types.ModuleType("aqt")
    if not hasattr(aqt, "gui_hooks"):
        aqt.gui_hooks = _Hooks()
    if not hasattr(aqt, "mw"):
        aqt.mw = None
    sys.modules["aqt"] = aqt
    if "theankidote" not in sys.modules:
        pkg = types.ModuleType("theankidote")
        pkg.__path__ = [str(ROOT)]
        sys.modules["theankidote"] = pkg
    from theankidote.pearls import _reviewer     # noqa: E402
    return _reviewer


class SpanAttributes(unittest.TestCase):
    """What the popup reads is what the span carries."""

    @classmethod
    def setUpClass(cls):
        cls.rv = _load_reviewer()
        from theankidote.pearls import _conditions
        cls.conditions = _conditions

    def _span_for(self, text, word):
        out = self.rv.highlight_text(text)
        m = re.search(r'<span class="sp-mark"[^>]*>' + re.escape(word)
                      + r"</span>", out)
        self.assertIsNotNone(m, f"{word!r} was not highlighted at all")
        return m.group(0)

    def _attr(self, span, name):
        m = re.search(name + r'="([^"]*)"', span)
        return m.group(1) if m else None

    def test_a_condition_with_a_chapter_is_marked_as_an_article(self):
        """PID carries a verified NBK accession, so the popup may
        honestly offer to open it."""
        entry = self.conditions._LOOKUP.get("pelvic inflammatory disease")
        self.assertIsNotNone(entry, "the fixture condition is gone")
        self.assertTrue(entry.get("nbk"), "fixture no longer has an nbk id")
        span = self._span_for(
            "Mild and subclinical PID causes tubal infertility.", "PID")
        self.assertEqual(self._attr(span, "data-sp-link"), "article")

    def test_a_condition_without_one_is_marked_as_a_search(self):
        entry = self.conditions._LOOKUP.get("terminal agitation")
        self.assertIsNotNone(entry, "the fixture condition is gone")
        self.assertFalse(entry.get("nbk"), "fixture unexpectedly has an nbk id")
        span = self._span_for(
            "Terminal agitation is common at the end of life.",
            "Terminal agitation")
        self.assertEqual(self._attr(span, "data-sp-link"), "search")

    def test_every_span_carries_the_keys_the_popup_reads(self):
        """A missing attribute is not a rendering fault, it is a silently
        wrong popup: `getAttribute` returns null and marker.js falls back
        to a default that reads as a real answer."""
        span = self._span_for("Chest pain and PID and warfarin.", "PID")
        for attr in ("data-sp-url", "data-sp-title", "data-sp-summary",
                     "data-sp-source", "data-sp-link", "data-sp-utd"):
            self.assertIsNotNone(
                self._attr(span, attr),
                f"{attr} is absent from the span; marker.js reads it")

    def test_a_condition_with_chips_actually_carries_them(self):
        """Presence is not enough - this attribute shipped present and
        empty.

        `data-sp-utd` was `"[]"` on every span ever written. The chips
        are built by `_conditions.resolve`, JSON-encoded by
        `_build_pattern` and read by `web/marker.js`, but the dict
        `_condition_terms` builds between them did not carry the key -
        the same omission that had already cost `data-sp-link`. The
        test above asserted the attribute was present, which it was, so
        nothing failed while 824 of the 826 conditions in the library
        rendered no UpToDate row at all.
        """
        import html as _html
        import json as _json
        entry = None
        for name in ("hypertension", "heart failure", "asthma"):
            cand = self.conditions._LOOKUP.get(name)
            if cand and cand.get("utd"):
                entry = (name, cand)
                break
        self.assertIsNotNone(entry, "no fixture condition carries utd chips")
        name, _cand = entry
        span = self._span_for(name.capitalize() + " is common.",
                              name.capitalize())
        raw = self._attr(span, "data-sp-utd")
        self.assertIsNotNone(raw, "data-sp-utd is absent")
        chips = _json.loads(_html.unescape(raw))
        self.assertTrue(
            chips,
            f"{name!r} carries utd chips in the library but the span "
            f"emitted an empty list")
        for chip in chips:
            # marker.js skips any entry missing either key, so a chip
            # that lacks one is a chip that never draws.
            self.assertIn("label", chip)
            self.assertIn("url", chip)
            self.assertTrue(chip["label"] and chip["url"])

    def test_the_dock_path_carries_no_stylesheet(self):
        """The card path is handed to Anki as one string and needs the
        rule travelling with it. The dock inserts each edit with
        `template.innerHTML` and installs one `#tad-hl-style` element
        itself, so a rule carried per node put one `<style>` into the
        article body per highlighted node.
        """
        text = "Mild and subclinical PID causes tubal infertility."
        card = self.rv.highlight_text(text)
        dock = self.rv.highlight_text(text, with_css=False)
        self.assertIn("<style>", card, "the card path lost its rule")
        self.assertNotIn("<style>", dock)
        self.assertEqual(
            re.sub(r"^<style>.*?</style>", "", card, flags=re.S), dock,
            "the two paths disagree about the markup, not just the rule")

    def test_search_urls_use_us_spelling(self):
        """The reviewer had its own copy of this builder that skipped the
        rewrite, so acronym expansions searched a US-only database with
        Australian spelling."""
        url = self.rv._term_search_url("Oesophageal varices")
        self.assertIn("esophageal", url.lower())
        self.assertNotIn("oesophageal", url.lower())


class WhatGetsUnderlined(unittest.TestCase):
    """The mark has to land on the words the reader actually wrote."""

    @classmethod
    def setUpClass(cls):
        cls.rv = _load_reviewer()
        from theankidote.pearls import _conditions, _drugs
        cls.conditions = _conditions
        cls.drugs = _drugs

    def _marks(self, text):
        out = self.rv.highlight_text(text, with_css=False)
        return re.findall(r'<span class="sp-mark"[^>]*>(.*?)</span>', out)

    def _span_for(self, text, word):
        out = self.rv.highlight_text(text, with_css=False)
        m = re.search(r'<span class="sp-mark"[^>]*>' + re.escape(word)
                      + r"</span>", out)
        self.assertIsNotNone(m, f"{word!r} was not highlighted at all")
        return m.group(0)

    def test_a_condition_written_as_an_alias_is_underlined(self):
        """`resolve` reports the primary name so the popup title is
        stable, and the pattern was built from that name - so a card
        that says "heart attack" and never "myocardial infarction"
        resolved the entry and then marked nothing. 5,457 of the
        library's 6,044 condition aliases do not contain their primary
        name, so this was most of them."""
        entry = self.conditions._LOOKUP.get("heart attack")
        self.assertIsNotNone(entry, "the fixture alias is gone")
        self.assertNotIn("heart attack", entry["name"].lower(),
                         "fixture alias now contains its primary name")
        self.assertIn("heart attack",
                      self._marks("Patient reports a heart attack in 2019."))

    def test_the_popup_still_names_the_primary_entry(self):
        """Only the underline follows the reader's wording. The title
        and the URL stay those of the entry, or the alias would open an
        article under a heading nobody wrote."""
        span = self._span_for("Patient reports a heart attack in 2019.",
                              "heart attack")
        entry = self.conditions._LOOKUP.get("heart attack")
        m = re.search(r'data-sp-title="([^"]*)"', span)
        self.assertEqual(m.group(1), entry["name"])
        self.assertIn("data-sp-url=\"" + self.conditions._url_for(entry),
                      span)

    def test_a_drug_written_as_a_spelling_variant_is_underlined(self):
        """`frusemide` is what NSW Health, the PBS and most Australian
        cards call furosemide. 38 of the 42 drug aliases do not contain
        their generic."""
        self.assertIn("frusemide", self._marks("Give frusemide 40 mg IV."))
        self.assertIn("furosemide", self._marks("Give furosemide 40 mg IV."))

    def test_two_spellings_of_one_entry_both_light_up(self):
        """`resolve` reports an entry once however many ways the card
        spells it, so the surfaces have to accumulate rather than the
        first one winning."""
        marks = self._marks("A heart attack: the myocardial infarction "
                            "was anterior.")
        self.assertIn("heart attack", marks)
        self.assertIn("myocardial infarction", marks)

    def test_a_bare_less_than_does_not_stop_highlighting(self):
        """The HTML walker treated every `<` as a tag opener, looked for
        the matching `>`, and on not finding one appended the whole
        remainder unhighlighted. StatPearls and DrugBank prose is full
        of "sodium <135", and the dock hands this decoded text."""
        marks = self._marks("Sodium < 130 in SIADH suggests hyponatraemia.")
        self.assertIn("SIADH", marks)
        self.assertIn("hyponatraemia", marks)

    def test_a_bare_less_than_mid_sentence_loses_nothing_after_it(self):
        marks = self._marks(
            "FEV1/FVC < 0.70 confirms asthma on spirometry.")
        self.assertIn("asthma", marks)
        self.assertIn("spirometry", marks)

    def test_a_greater_than_inside_an_attribute_does_not_break_the_tag(self):
        """A `>` in an attribute value ended the "tag" early, so the
        rest of the attribute was treated as character data and a span
        was injected inside it - which destroys the element."""
        html = '<img src="x.png" alt="a > b asthma here">Asthma is common.'
        out = self.rv.highlight_text(html, with_css=False)
        self.assertIn('<img src="x.png" alt="a > b asthma here">', out,
                      "the img tag was rewritten")
        self.assertRegex(out, r'<span class="sp-mark"[^>]*>Asthma</span>')

    def test_an_unquoted_apostrophe_in_a_tag_is_not_a_quote(self):
        """Tracking quotes without asking where an attribute value can
        start turns `<img alt=Crohn's>` into a value that never closes,
        so the tag never ends and the whole rest of the node goes
        unhighlighted - the same failure the quote tracking exists to
        fix, one step along."""
        out = self.rv.highlight_text("<img alt=Crohn's>Asthma is common.",
                                     with_css=False)
        self.assertIn("<img alt=Crohn's>", out, "the img tag was rewritten")
        self.assertRegex(out, r'<span class="sp-mark"[^>]*>Asthma</span>')

    def test_the_longer_term_wins_across_the_case_boundary(self):
        """Every case-sensitive alternative used to sit ahead of every
        case-insensitive one, and `re` alternation is first-match-wins -
        so the acronym G6PD beat the condition "G6PD deficiency"
        whatever their lengths. 37 such pairs ship in the library."""
        self.assertIn("G6PD deficiency",
                      self._marks("G6PD deficiency causes haemolysis."))
        self.assertIn("CURB-65 score",
                      self._marks("The CURB-65 score guides admission."))

    def test_a_term_ending_in_punctuation_matches_mid_sentence(self):
        """`\\b` after a phrase ending in ")" asserts a WORD character
        next, so the 23 library terms that end that way only ever
        matched at the very end of a text."""
        marks = self._marks(
            "Vitamin B12 (cobalamin) deficiency causes macrocytosis.")
        self.assertIn("Vitamin B12 (cobalamin)", marks)

    def test_an_acronym_expansion_carries_the_conditions_chips(self):
        """The branch that enriches an acronym from a matching condition
        copies url, summary and link across and used to drop `utd`, so
        `data-sp-utd` was "[]" and marker.js hid the chip row on all 169
        acronym expansions whose condition carries chips."""
        import html as _html
        import json as _json
        term = None
        for t in self.rv._acronym_terms(
                "Mild and subclinical PID causes tubal infertility."):
            if t["title"] == "PID":
                term = t
        self.assertIsNotNone(term, "the fixture acronym no longer resolves")
        self.assertTrue(term.get("utd"),
                        "the acronym term dict carries no chips")
        span = self._span_for(
            "Mild and subclinical PID causes tubal infertility.", "PID")
        raw = re.search(r'data-sp-utd="([^"]*)"', span).group(1)
        chips = _json.loads(_html.unescape(raw))
        self.assertTrue(chips, "the span emitted an empty chip list")
        for chip in chips:
            self.assertTrue(chip.get("label") and chip.get("url"))

    def test_a_shared_name_keeps_its_better_destination(self):
        """`splenomegaly` is both a condition and a preclinical term,
        `glucagon` both a drug and a preclinical term, and the lookup is
        keyed on the lowercased title - so whichever database was
        written last took the name. Preclinical links to a Wikipedia
        search; it used to be written last and won all thirteen."""
        span = self._span_for("The patient has splenomegaly today.",
                              "splenomegaly")
        self.assertIn("ncbi.nlm.nih.gov", span,
                      "splenomegaly lost its StatPearls entry")
        span = self._span_for("Glucagon was given for the hypoglycaemia.",
                              "Glucagon")
        self.assertIn("drugbank.com", span,
                      "glucagon lost its DrugBank entry")

    def test_british_spelling_survives_normalisation(self):
        """"oedema" contains "edema" and "oesophag" contains "esophag",
        so the American-to-British swap rewrote text that was already
        British and produced a key that can never match."""
        self.assertEqual(
            self.rv._normalise_for_lookup("Pulmonary oedema"),
            "pulmonary oedema")
        self.assertEqual(
            self.rv._normalise_for_lookup("Pulmonary edema"),
            "pulmonary oedema")
        self.assertEqual(
            self.rv._normalise_for_lookup("Oesophageal varices"),
            "oesophageal varices")


class MarkerJsReadsThoseAttributes(unittest.TestCase):
    """The other half of the same contract, checked against the file
    rather than against a memory of it."""

    def _marker(self):
        return (ROOT / "web" / "marker.js").read_text(encoding="utf-8")

    def test_link_attribute_is_what_decides_isarticle(self):
        js = self._marker()
        self.assertRegex(
            js,
            r'var isArticle = \(el\.getAttribute\("data-sp-link"\)'
            r' \|\| "search"\) === "article";',
            "marker.js no longer derives isArticle from data-sp-link, so "
            "the span attribute this module tests may reach nothing")

    def test_the_button_label_is_not_reassigned_after_it_is_set(self):
        """The label was set from `isArticle` and then overwritten
        unconditionally sixty lines later, which is what defeated the
        fix the 2.5 notes describe. One assignment, or none of this
        matters."""
        js = self._marker()
        self.assertEqual(
            js.count("_tipOpenBtn.textContent"), 1,
            "_tipOpenBtn.textContent is assigned more than once; a later "
            "assignment silently undoes the isArticle branch")


if __name__ == "__main__":
    unittest.main(verbosity=2)
