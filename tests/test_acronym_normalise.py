# SPDX-License-Identifier: GPL-3.0-or-later
"""Spelling-normalisation tests for the acronym → condition resolver.

Loads just `_normalise_for_lookup` and `_AE_E_SWAPS` from the source
file - importing the whole module would require aqt, anki, etc.
"""

import ast
import os
import unittest


def _load_normaliser():
    src = os.path.join(
        os.path.dirname(__file__), "..", "pearls", "_reviewer.py"
    )
    with open(src, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    wanted = {"_AE_E_SWAPS", "_normalise_for_lookup"}
    body = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(getattr(t, "id", None) in wanted for t in node.targets):
                body.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name in wanted:
            body.append(node)
    mod = ast.Module(body=body, type_ignores=[])
    ns: dict = {}
    exec(compile(mod, src, "exec"), ns)
    return ns["_normalise_for_lookup"]


class NormaliseTest(unittest.TestCase):
    def setUp(self):
        self.fn = _load_normaliser()

    def test_lowercase(self):
        self.assertEqual(self.fn("Heart Failure"), "heart failure")

    def test_leukemia_to_leukaemia(self):
        self.assertEqual(
            self.fn("Acute Lymphoblastic Leukemia"),
            "acute lymphoblastic leukaemia",
        )

    def test_anemia_to_anaemia(self):
        self.assertEqual(self.fn("Iron-deficiency Anemia"),
                         "iron-deficiency anaemia")

    def test_oedema(self):
        self.assertEqual(self.fn("Pulmonary Edema"), "pulmonary oedema")

    def test_already_british(self):
        self.assertEqual(
            self.fn("Acute lymphoblastic leukaemia"),
            "acute lymphoblastic leukaemia",
        )

    def test_empty(self):
        self.assertEqual(self.fn(""), "")
        self.assertEqual(self.fn(None), "")


if __name__ == "__main__":
    unittest.main()
