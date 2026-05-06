# SPDX-License-Identifier: GPL-3.0-or-later
"""URL whitelist regression tests.  Imports just the function under
test - we intentionally do NOT import the whole addon (that would
require Anki/PyQt) - by reading the source and exec'ing the helper
in isolation.  Keeps tests dependency-free."""

import ast
import os
import unittest


def _load_is_safe_url():
    src_path = os.path.join(os.path.dirname(__file__), "..", "__init__.py")
    with open(src_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_is_safe_url":
            mod = ast.Module(body=[node], type_ignores=[])
            ns: dict = {}
            exec(compile(mod, src_path, "exec"), ns)
            return ns["_is_safe_url"]
    raise RuntimeError("_is_safe_url not found")


class SafeUrlTest(unittest.TestCase):
    def setUp(self):
        self.fn = _load_is_safe_url()

    def test_https_allowed(self):
        self.assertTrue(self.fn("https://www.uptodate.com/contents/search"))

    def test_http_allowed(self):
        self.assertTrue(self.fn("http://example.org"))

    def test_javascript_blocked(self):
        self.assertFalse(self.fn("javascript:alert(1)"))

    def test_file_blocked(self):
        self.assertFalse(self.fn("file:///etc/passwd"))

    def test_data_blocked(self):
        self.assertFalse(self.fn("data:text/html,<script>x</script>"))

    def test_empty(self):
        self.assertFalse(self.fn(""))
        self.assertFalse(self.fn(None))

    def test_whitespace_stripped(self):
        self.assertTrue(self.fn("  https://example.com  "))

    def test_case_insensitive_scheme(self):
        self.assertTrue(self.fn("HTTPS://example.com"))


if __name__ == "__main__":
    unittest.main()
