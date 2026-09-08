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
import json
import os
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

    def test_a_non_breaking_space_does_not_stop_a_match(self):
        """Anki's editor writes `&nbsp;`, and it broke every two-word term.

        From a card the user sent: `of an&nbsp;<b>ectopic</b>&nbsp;
        pregnancy` underlined nothing, though Ectopic pregnancy is in
        the library. 60% of library terms are multi-word, and 3,277 of
        that user's 6,088 notes contain `&nbsp;`, so this was most of
        the vocabulary failing on most of the cards - silently, with
        nothing to notice except an absence.

        Two halves, and both are checked here: resolution runs on the
        stripped text, where the entity has decoded to U+00A0, and
        highlighting runs on the raw HTML, where it is still an entity.
        """
        html = "of an&nbsp;ectopic&nbsp;pregnancy?"
        results = self.rv._condition_terms(self.rv._strip_html(html))
        self.assertTrue(results, "the term did not even resolve")
        out = self.rv._inject_highlights(html, results, "#0fcad4",
                                         with_css=False)
        marks = re.findall(r'<span class="sp-mark"[^>]*>(.*?)</span>', out)
        self.assertEqual(marks, ["ectopic&nbsp;pregnancy"],
                         "the entity form was not marked")
        # The span must wrap what the card actually says, entity and
        # all - normalising is only ever for the lookup key.
        self.assertIn("&nbsp;", out)

    def test_a_unicode_space_does_not_stop_a_match(self):
        """The dock passes decoded text, so it meets the character."""
        for sep in ("\u00a0", "\u202f", "\u2009"):
            with self.subTest(sep=repr(sep)):
                marked = self.rv.highlight_text(f"an ectopic{sep}pregnancy",
                                                with_css=False)
                self.assertIn("sp-mark", marked)

    def test_a_missing_space_is_still_not_a_match(self):
        """The separator is flexible, not optional."""
        self.assertNotIn(
            "sp-mark",
            self.rv.highlight_text("ectopicpregnancy", with_css=False))

    def test_every_builder_carries_every_key_the_span_writes(self):
        """The structural guard for a bug this tree has shipped three times.

        `_span` reads a fixed set of keys. Five builders produce the
        dicts it reads them from, and each time one of them was written
        or edited, a key got left out - `link` first, so every popup
        claimed an article it did not have; then `utd` in
        `_condition_terms`, so 824 conditions never drew their UpToDate
        row; then `utd` again in `_acronym_terms`, one branch away from
        the fix. Each was invisible, because a missing key falls back to
        a default that reads like a real answer.

        Reading the source rather than the output, because the failure
        is a builder that CAN produce a dict without the key, not a
        particular card that happens to. A builder legitimately without
        a key - the drug tables carry no `utd` - must say so with an
        explicit default rather than by omission, which is exactly the
        distinction that was missing.
        """
        import ast
        src = (ROOT / "pearls" / "_reviewer.py").read_text(encoding="utf-8")
        tree = ast.parse(src)

        # The keys `_span` interpolates, read off the source so this
        # cannot drift from the writer it is guarding.
        span_keys = set(re.findall(r't\.get\("(\w+)"|t\["(\w+)"\]',
                                  src))
        keys = {a or b for a, b in span_keys}
        keys.discard("badge")           # optional by design, blank is fine
        self.assertIn("link", keys, "the span writer no longer reads link")
        self.assertIn("utd", keys, "the span writer no longer reads utd")

        builders = ["_custom_terms", "_acronym_terms", "_drug_terms",
                    "_condition_terms", "_preclinical_terms"]
        for name in builders:
            fn = next((n for n in ast.walk(tree)
                       if isinstance(n, ast.FunctionDef) and n.name == name),
                      None)
            self.assertIsNotNone(fn, f"{name} is gone; update this test")
            # Every dict literal this builder appends is a term dict.
            for node in ast.walk(fn):
                if not isinstance(node, ast.Dict):
                    continue
                literal = {k.value for k in node.keys
                           if isinstance(k, ast.Constant)
                           and isinstance(k.value, str)}
                if "title" not in literal:
                    continue        # not a term dict
                missing = {k for k in ("url", "summary", "source", "link",
                                       "utd")} - literal
                self.assertFalse(
                    missing,
                    f"{name} builds a term dict without {sorted(missing)}; "
                    f"`_span` reads those and falls back to a default that "
                    f"looks like an answer. Set them explicitly, even to "
                    f"an empty value.")

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


# ── A corpus to hold the walker to ────────────────────────────────────
#
# The invariant below - strip the spans and get the input back - is only
# worth anything over markup that actually varies. Three hand-written
# cases prove nothing about a walker; the shapes that break one are the
# ones nobody thought to write down.
#
# So the corpus is generated, from a fixed seed, out of the tag and
# attribute inventory of a real 6,088-note collection: `b` 36,331
# occurrences, `div` 26,486, `br` 22,600, `li` 16,764, `u` 11,908, `i`
# 10,515, then `ul`, `img`, `span`, `td`, `a`, `font`, `ol`, `tr`,
# `summary`, `p`, `strong`, `table`, `sup`, `sub`, `blockquote`, `em`,
# `th`, `mark`; `&nbsp;` 10,761 times, `&gt;` 1,902, `&lt;` 774, and
# seven fields carrying a bare `<` that is not a tag at all. The
# attribute strings are the ones that collection actually uses.
#
# Generated rather than a dump of the collection because those cards are
# a student's own notes and a good deal of licensed deck material, and
# this repository is public. The structure is what this test is about,
# and the structure is not anybody's copy. The real cards were run
# through the same assertion while the fix was written - all 13,206
# non-empty fields, zero mismatches - and `TAD_CARD_CORPUS` below lets
# anyone repeat that against their own collection without the corpus
# ever entering the tree.

_CORPUS_INLINE = ("b", "i", "u", "em", "strong", "span", "font", "mark",
                  "small", "sub", "sup", "s", "big", "a")
_CORPUS_BLOCK = ("div", "p", "li", "ul", "ol", "td", "th", "tr", "table",
                 "blockquote", "h3", "summary", "pre")
_CORPUS_VOID = ("<br>", "<br />", "<hr>", '<img src="paste-1.jpg">',
                '<img src="x.png" alt="a > b asthma here">',
                "<img alt=Crohn's>", "<!-- a note -->")
_CORPUS_ATTRS = ("", ' style=""', ' class="toggle"', ' data-au-notes="v2"',
                 ' style="background-color: rgb(255, 229, 243);"',
                 ' color="#ff0000"',
                 ' style="width:50%;  padding: 2px; border: 1px solid;"')
# Half library terms, half the words that sit between them. The terms
# are multi-word on purpose: a single word never needed a run joined.
_CORPUS_WORDS = (
    "ectopic pregnancy", "deep vein thrombosis", "myocardial infarction",
    "urinary tract infection", "chronic kidney disease",
    "placental abruption", "postpartum haemorrhage", "asthma", "sepsis",
    "Addison's disease", "warfarin", "metformin",
    "the", "is", "of", "a", "Define:", "risk factor", "management",
    "in children", "{{c1::two}}", "Sodium < 130", "loss &gt;500ml",
    "salt &amp; water", "an&nbsp;", " ", "&nbsp;", "&lt;135",
)


# Terms a card can put a tag through the middle of. Written as the
# library writes them, so a split of one is recognisable by its title.
_CORPUS_SPLITTABLE = (
    "ectopic pregnancy", "deep vein thrombosis", "myocardial infarction",
    "chronic kidney disease", "placental abruption",
    "postpartum haemorrhage",
)


def _corpus(count=600):
    """`count` card-shaped documents, deterministic for a given count."""
    import random
    rnd = random.Random(20260908)
    docs = []

    def text():
        return " ".join(rnd.choice(_CORPUS_WORDS)
                        for _ in range(rnd.randint(1, 6)))

    def split_term(depth):
        """A term with a tag through the middle of it, which is how a
        student who bolds the key word writes one."""
        term = rnd.choice(_CORPUS_SPLITTABLE)
        words = term.split()
        cut = rnd.randint(1, len(words) - 1)
        head, tail = " ".join(words[:cut]), " ".join(words[cut:])
        sep = rnd.choice((" ", "&nbsp;", "\u00a0", " "))
        wrap = rnd.choice(_CORPUS_INLINE)
        attr = rnd.choice(_CORPUS_ATTRS)
        if rnd.random() < 0.5:
            return "<%s%s>%s</%s>%s%s" % (wrap, attr, head, wrap, sep, tail)
        if rnd.random() < 0.5 or depth > 2:
            return "%s%s<%s%s>%s</%s>" % (head, sep, wrap, attr, tail, wrap)
        inner = rnd.choice(_CORPUS_INLINE)
        return ("<%s%s><%s>%s</%s></%s>%s<%s>%s</%s>"
                % (wrap, attr, inner, head, inner, wrap, sep,
                   inner, tail, inner))

    def frag(depth):
        out = []
        for _ in range(rnd.randint(1, 4)):
            roll = rnd.random()
            if roll < 0.25 or depth > 3:
                out.append(text())
            elif roll < 0.36:
                out.append(split_term(depth))
            elif roll < 0.40:
                # The same terms broken by a block tag instead, which
                # must never come back joined.
                term = rnd.choice(_CORPUS_SPLITTABLE).split()
                cut = rnd.randint(1, len(term) - 1)
                t = rnd.choice(("li", "div", "p", "td"))
                out.append("<%s>%s</%s>%s<%s>%s</%s>"
                           % (t, " ".join(term[:cut]), t,
                              rnd.choice(("", "<br>", "\n")),
                              t, " ".join(term[cut:]), t))
            elif roll < 0.55:
                out.append(rnd.choice(_CORPUS_VOID))
            elif roll < 0.80:
                t = rnd.choice(_CORPUS_INLINE)
                out.append("<%s%s>%s</%s>"
                           % (t, rnd.choice(_CORPUS_ATTRS), frag(depth + 1), t))
            else:
                t = rnd.choice(_CORPUS_BLOCK)
                out.append("<%s%s>%s</%s>"
                           % (t, rnd.choice(_CORPUS_ATTRS), frag(depth + 1), t))
        return "".join(out)

    for _ in range(count):
        docs.append(frag(0))
    return docs


# Named here rather than read off `_reviewer._INLINE_TAGS`, so that
# quietly moving one of these onto the inline list fails this test
# instead of passing it.
_BLOCK_TAGS = frozenset((
    "div", "p", "li", "ol", "ul", "br", "td", "tr", "th", "table",
    "blockquote", "pre", "hr", "section", "article", "figure",
    "details", "summary", "img", "h1", "h2", "h3", "h4", "h5", "h6",
))


_SP_SPAN_RE = re.compile(r'<span class="sp-mark"[^>]*?>(.*?)</span>', re.S)
_ANY_TAG_RE = re.compile(r"<[A-Za-z/!?][^>]*>")


def _unmark(html):
    """The output with every sp-mark span unwrapped, text kept.

    An sp-mark span holds one run of character data and never a tag, so
    the `</span>` that closes it is always the next one in the string -
    which is what makes this a safe inverse rather than a guess.
    """
    return _SP_SPAN_RE.sub(r"\1", html)


class MatchesAcrossInlineMarkup(unittest.TestCase):
    """A term the card puts in bold is still one term.

    `_inject_highlights` matched within each run of characters between
    two tags, so `<b>ectopic</b>&nbsp;pregnancy` was offered to the
    pattern as "ectopic" and "&nbsp;pregnancy" separately and "Ectopic
    pregnancy" could not be seen. 60% of the library is multi-word and
    4,869 of one collection's 6,088 notes carry a `<b>`, almost always
    around the key term.
    """

    @classmethod
    def setUpClass(cls):
        cls.rv = _load_reviewer()

    def _inject(self, html):
        """The card path: resolve from the stripped text, inject into
        the raw HTML. The two see different strings, which is half of
        why this class of bug survives so long."""
        rv = self.rv
        text = rv._strip_html(html)
        results = (rv._acronym_terms(text) + rv._condition_terms(text)
                   + rv._drug_terms(text) + rv._preclinical_terms(text))
        return rv._inject_highlights(html, results, "#0fcad4",
                                     with_css=False)

    def _marks(self, html):
        return _SP_SPAN_RE.findall(self._inject(html))

    def _titles(self, html):
        return re.findall(r'<span class="sp-mark"[^>]*data-sp-title='
                          r'"([^"]*)"', self._inject(html))

    def test_the_card_that_prompted_this_underlines_its_term(self):
        """Verbatim from the card the user sent."""
        html = "of an&nbsp;<b>ectopic</b>&nbsp;pregnancy?"
        marks = self._marks(html)
        self.assertTrue(marks, "nothing was underlined at all")
        self.assertEqual(
            "".join(marks).replace("&nbsp;", " "), "ectopic pregnancy",
            "the mark does not cover the term the card wrote")
        self.assertEqual(set(self._titles(html)), {"Ectopic pregnancy"})

    def test_a_term_split_by_a_bold_tag_matches(self):
        self.assertEqual(
            "".join(self._marks("an <b>ectopic</b> pregnancy today")),
            "ectopic pregnancy")

    def test_a_term_split_by_a_styled_span_matches(self):
        html = ('an <span style="background-color: rgb(255, 229, 243);">'
                'ectopic</span> pregnancy today')
        self.assertEqual("".join(self._marks(html)), "ectopic pregnancy")

    def test_a_term_split_by_nested_inline_tags_matches(self):
        html = "an <b><i>ectopic</i></b> <u>pregnancy</u> today"
        self.assertEqual("".join(self._marks(html)), "ectopic pregnancy")

    def test_every_piece_of_a_split_term_opens_the_same_popup(self):
        """One span per text run, all carrying the same attributes, so
        hovering either half opens one popup. A single span cannot be
        written here: a match that starts inside the `<b>` and ends
        outside it would have to close across the element boundary."""
        out = self._inject("an <b>ectopic</b> pregnancy today")
        spans = re.findall(r'<span class="sp-mark"[^>]*>', out)
        self.assertEqual(len(spans), 2, "expected one span per text run")
        self.assertEqual(spans[0], spans[1],
                         "the two halves would open different popups")

    def test_a_term_does_not_match_across_a_block_boundary(self):
        """The failure mode worth more than the bug being fixed.

        Joining every run would let "Signs of pregnancy</li><li>
        Temperature" underline a phrase spanning two list items that
        share no sentence, and the popup would explain a term the card
        never used. Anything not on the inline list ends the run,
        including tags nobody has thought about yet.
        """
        for html in ("<li>ectopic</li><li>pregnancy</li>",
                     "<ul><li>ectopic</li>\n<li>pregnancy</li></ul>",
                     "ectopic<br>pregnancy",
                     "ectopic<br />pregnancy",
                     "<div>ectopic</div><div>pregnancy</div>",
                     "<p>ectopic</p><p>pregnancy</p>",
                     "<td>ectopic</td><td>pregnancy</td>",
                     "ectopic<hr>pregnancy",
                     '<h3>ectopic</h3>pregnancy',
                     'ectopic<img src="x.png">pregnancy',
                     "<blockquote>ectopic</blockquote>pregnancy"):
            with self.subTest(html=html):
                self.assertEqual(self._marks(html), [],
                                 "a phrase was invented across a break")

    def test_script_and_style_content_is_still_skipped(self):
        for tag in ("script", "style"):
            with self.subTest(tag=tag):
                html = ("<%s>var s = 'ectopic pregnancy';</%s>"
                        "an <b>ectopic</b> pregnancy" % (tag, tag))
                out = self._inject(html)
                self.assertIn("var s = 'ectopic pregnancy';", out,
                              "the %s body was rewritten" % tag)
                self.assertEqual(
                    "".join(_SP_SPAN_RE.findall(out)), "ectopic pregnancy")

    def test_an_existing_mark_is_not_marked_again(self):
        """The self-heal strips a previous run's spans before the walk,
        so a re-render cannot nest a span inside a span."""
        once = self._inject("an <b>ectopic</b> pregnancy today")
        twice = self._inject(once)
        self.assertEqual(twice, once)
        self.assertNotIn('<span class="sp-mark" data-sp-url="'
                         'https://www.ncbi.nlm.nih.gov/books/NBK539860/" '
                         'data-sp-title="Ectopic pregnancy"'
                         ' data-sp-summary', twice.replace(once, ""))

    def test_a_tag_is_never_written_into(self):
        """A `>` inside an attribute value once ended the tag early and
        a span was injected into an `alt`, destroying the element."""
        html = '<img src="x.png" alt="a > b ectopic pregnancy here">an ' \
               '<b>ectopic</b> pregnancy'
        out = self._inject(html)
        self.assertIn('<img src="x.png" alt="a > b ectopic pregnancy here">',
                      out, "the img tag was rewritten")
        for tag in _ANY_TAG_RE.findall(_unmark(out)):
            self.assertNotIn("sp-mark", tag,
                             "a mark was written inside a tag")


class StrippingTheMarksGivesBackTheCard(unittest.TestCase):
    """One assertion that catches text loss, duplication, reordering and
    a mangled tag at once.

    The walker now edits runs it emitted several tags ago, which is
    exactly the kind of change that drops or repeats a character
    somewhere nobody is looking. Removing every `<span class="sp-mark"
    ...>` and its matching `</span>` has to give the input back byte
    for byte - no weaker check would notice a swapped pair of runs.
    """

    @classmethod
    def setUpClass(cls):
        cls.rv = _load_reviewer()
        cls.docs = _corpus()

    def _mark(self, html):
        return self.rv.highlight_text(html, with_css=False)

    def test_the_corpus_is_actually_exercising_the_walker(self):
        """A vacuous corpus would pass the invariant perfectly."""
        norm = self.rv._matcher.normalise_separators
        span_re = re.compile(r'<span class="sp-mark"[^>]*data-sp-title='
                             r'"([^"]*)"[^>]*>(.*?)</span>', re.S)
        marked = split = 0
        for doc in self.docs:
            out = self._mark(doc)
            if "sp-mark" not in out:
                continue
            marked += 1
            spans = [(m.start(), m.end(), m.group(1), m.group(2))
                     for m in span_re.finditer(out)]
            for (_s1, e1, t1, w1), (s2, _e2, t2, w2) in zip(spans, spans[1:]):
                # One term, one span per run. Three things have to hold
                # for a pair of spans to be that rather than two
                # separate hits on the same term: the same title; a gap
                # holding markup and nothing else, not even a space,
                # because a space between two words of the term belongs
                # to a run and lands inside the second span; and the two
                # pieces spelling the term when put together.
                if t1 != t2 or _ANY_TAG_RE.sub("", out[e1:s2]) != "":
                    continue
                if norm(w1 + w2).lower() != norm(t1).lower():
                    continue
                # The gap is the markup the term was written through,
                # and only an inline element may appear in it. A block
                # tag here would mean a phrase invented across two list
                # items or two table cells, which is a worse defect
                # than the one this walker was changed to fix.
                for gap_tag in re.findall(r"</?([A-Za-z][A-Za-z0-9]*)",
                                          out[e1:s2]):
                    self.assertNotIn(
                        gap_tag.lower(), _BLOCK_TAGS,
                        "a term was joined across <%s> in:\n  %s"
                        % (gap_tag, doc))
                split += 1
                break
        self.assertGreater(marked, len(self.docs) // 4,
                           "the corpus barely marks anything")
        self.assertGreater(split, 20,
                           "no document in the corpus has a term split "
                           "across inline markup, so the invariant is "
                           "not testing the new path")

    def test_the_generated_corpus_survives_a_round_trip(self):
        for i, doc in enumerate(self.docs):
            out = self._mark(doc)
            if _unmark(out) != doc:
                self.fail("document %d lost, gained or moved text\n"
                          "  in : %r\n  out: %r" % (i, doc, _unmark(out)))

    def test_a_real_collection_survives_a_round_trip(self):
        """Opt-in, because a real collection cannot live in this tree.

        Point `TAD_CARD_CORPUS` at a JSON array of field HTML strings -
        an `ankiconnect notesInfo` dump will do - and the same assertion
        runs against the cards as written.
        """
        path = os.environ.get("TAD_CARD_CORPUS")
        if not path:
            self.skipTest("TAD_CARD_CORPUS is not set")
        docs = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
        for i, doc in enumerate(docs):
            if not isinstance(doc, str) or not doc.strip():
                continue
            out = self._mark(doc)
            if _unmark(out) != doc:
                self.fail("field %d lost, gained or moved text\n"
                          "  in : %r\n  out: %r" % (i, doc, _unmark(out)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
