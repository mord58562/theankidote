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
