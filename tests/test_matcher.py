#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Equivalence tests for pearls/_matcher.py.

`PhraseMatcher` replaced the giant regex alternations in the condition
and drug databases for speed. The only thing that makes that a safe
substitution is that it returns exactly what the regex returned, so
these tests diff the two directly - over the real databases, not a
sample - rather than asserting the matcher does what it says.

Run: python3 tests/test_matcher.py
"""

import importlib.util
import os
import random
import re
import sys
import types
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)

# The databases import cleanly without Anki; the package __init__ does not.
sys.modules.setdefault("aqt", types.ModuleType("aqt"))
sys.modules["aqt"].mw = None


def _load(name, relpath):
    path = os.path.join(_ROOT, relpath)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_matcher = _load("_tad_matcher", "pearls/_matcher.py")
# `_conditions` and `_drugs` do `from . import _matcher`, so give them a
# package to find it in.
_pkg = types.ModuleType("pearls")
_pkg.__path__ = [os.path.join(_ROOT, "pearls")]
_pkg._matcher = _matcher
sys.modules["pearls"] = _pkg
sys.modules["pearls._matcher"] = _matcher
_conditions = _load("pearls._conditions", "pearls/_conditions.py")
_drugs = _load("pearls._drugs", "pearls/_drugs.py")


def _corpus():
    """Card-shaped text, plus adversarial cases, plus fuzz.

    The hand-written entries cover the things a first-word index could
    plausibly get wrong: a phrase that is a prefix of a longer one,
    repeated terms, terms against punctuation and hyphens, and terms at
    the very start and very end of the string.
    """
    texts = [
        "",
        "gout",
        "gout.",
        "(gout)",
        "gout-like presentation, pseudo-gout, non-gout arthritis",
        "goutish goutier ungout",
        "gout gout gout gout",
        "Acne vulgaris: topical benzoyl peroxide, adapalene or tretinoin; "
        "oral doxycycline; isotretinoin (Roaccutane) needs dermatology.",
        "Calcium pyrophosphate deposition disease versus acute gout - knee "
        "and wrist, longer duration of attacks, possible systemic symptoms.",
        "Dermatomyositis: Gottron papules, heliotrope eruption, Raynaud "
        "phenomenon, interstitial lung disease, increased risk of malignancy "
        "(more significant in dermatomyositis than polymyositis).",
        "Polymyalgia rheumatica and giant cell arteritis. Prednisolone, "
        "methotrexate, tocilizumab.",
        "Erythema nodosum: sarcoidosis, tuberculosis, Behcet disease, "
        "inflammatory bowel disease, oral contraceptive pill, pregnancy.",
        "COPD - salbutamol, ipratropium, tiotropium, budesonide/formoterol.",
        "Nothing clinical in this sentence whatsoever, just plain words.",
        "\u00e9\u00e0\u00fc unicode padding around gout and aspirin",
    ]
    random.seed(20260814)
    vocab = ("acne gout aspirin heart failure asthma copd diabetes lupus the a "
             "of and with in for calcium disease acute chronic pain").split()
    for _ in range(400):
        n = random.randint(1, 70)
        texts.append(" ".join(random.choice(vocab) for _ in range(n)))
    return texts


CORPUS = _corpus()


class MatchesRegexExactly(unittest.TestCase):
    """The substitution is only safe if the output is identical."""

    def _check(self, label, matcher, pattern):
        problems = _matcher.verify_against_regex(matcher, pattern, CORPUS)
        self.assertEqual(
            problems, [],
            f"{label}: {len(problems)} of {len(CORPUS)} texts disagree; "
            f"first: {problems[0] if problems else None}")

    def test_conditions(self):
        self._check("conditions",
                    _conditions._CONDITION_MATCHER, _conditions._CONDITION_RE)

    def test_drug_generics(self):
        self._check("generics", _drugs._GENERIC_MATCHER, _drugs._GENERIC_RE)

    def test_drug_brands_are_case_sensitive(self):
        self._check("brands", _drugs._BRAND_MATCHER, _drugs._BRAND_RE)


class MatcherSemantics(unittest.TestCase):
    """The properties the resolvers depend on, stated directly."""

    def test_longest_phrase_wins(self):
        m = _matcher.PhraseMatcher(["heart", "heart failure"])
        self.assertEqual([t[2] for t in m.find("heart failure")],
                         ["heart failure"])

    def test_matches_do_not_overlap(self):
        m = _matcher.PhraseMatcher(["ab cd", "cd ef"])
        self.assertEqual([t[2] for t in m.find("ab cd ef")], ["ab cd"])

    def test_word_boundaries_required(self):
        m = _matcher.PhraseMatcher(["gout"])
        self.assertEqual(m.find("gouty"), [])
        self.assertEqual(m.find("ungout"), [])
        self.assertEqual([t[2] for t in m.find("gout.")], ["gout"])
        self.assertEqual([t[2] for t in m.find("(gout)")], ["gout"])

    def test_case_insensitive_by_default(self):
        m = _matcher.PhraseMatcher(["Aspirin"])
        self.assertEqual([t[2] for t in m.find("ASPIRIN aspirin")],
                         ["aspirin", "aspirin"])

    def test_case_sensitive_mode(self):
        m = _matcher.PhraseMatcher(["Panadol"], case_sensitive=True)
        self.assertEqual([t[2] for t in m.find("Panadol")], ["Panadol"])
        self.assertEqual(m.find("panadol"), [])

    def test_hyphenated_phrase_found_from_its_first_token(self):
        m = _matcher.PhraseMatcher(["beta-blocker"])
        self.assertEqual([t[2] for t in m.find("a beta-blocker here")],
                         ["beta-blocker"])

    def test_positions_are_correct(self):
        m = _matcher.PhraseMatcher(["gout"])
        self.assertEqual(m.find("xx gout yy"), [(3, 7, "gout")])

    def test_empty_and_missing(self):
        m = _matcher.PhraseMatcher(["gout"])
        self.assertEqual(m.find(""), [])
        self.assertEqual(m.find("nothing here"), [])
        self.assertEqual(_matcher.PhraseMatcher([]).find("gout"), [])

    def test_results_are_in_text_order(self):
        m = _matcher.PhraseMatcher(["alpha", "beta", "gamma"])
        got = [t[2] for t in m.find("gamma beta alpha")]
        self.assertEqual(got, ["gamma", "beta", "alpha"])


class ResolversStillWork(unittest.TestCase):
    """End-to-end: the resolvers' own output, not just the matcher's."""

    def test_condition_resolve(self):
        got = {c["name"].lower() for c in _conditions.resolve(
            "Polymyalgia rheumatica and giant cell arteritis")}
        self.assertTrue(got, "expected at least one condition")

    def test_drug_resolve(self):
        got = {d["name"].lower() for d in _drugs.resolve(
            "topical benzoyl peroxide, adapalene, doxycycline")}
        self.assertTrue(got, "expected at least one drug")

    def test_resolve_is_stable_across_calls(self):
        text = "Acne vulgaris treated with doxycycline and isotretinoin"
        first = _drugs.resolve(text)
        self.assertEqual(first, _drugs.resolve(text))


if __name__ == "__main__":
    unittest.main(verbosity=2)
