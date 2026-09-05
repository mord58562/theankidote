# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""Regression tests for the 2.0.2 security review.

Every test here corresponds to a defect that was present in 2.0.1 and
was demonstrated rather than argued for. They are grouped by the surface
the handover named, in the order an attacker would reach for them.

The recurring theme is that 2.0 made the term library *downloadable*,
which moved summary text, entry URLs and library structure out of the
author's hands and into the hands of whoever controls the content host.
Several checks that were adequate for a file shipped inside the
.ankiaddon are not adequate for one fetched at startup.
"""
import ast
import copy
import json
import os
import pathlib
import re
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "content"))

from pearls import _library, _updater  # noqa: E402


def _valid():
    return copy.deepcopy(_library.LIBRARY)


class ValidationIsDeep(unittest.TestCase):
    """`_validate` used to check `conditions[0]` and accept the rest.

    That was not a theoretical gap. A library whose eighth condition is
    a bare string passed validation, was written to `user_files/`, was
    preferred over the bundled copy at every subsequent launch, and then
    raised `ValueError` inside `_conditions.py` at import - which kills
    the add-on permanently, because the Settings dialog that could turn
    updates off lives inside the add-on that no longer imports. The only
    recovery was deleting a file by hand.

    So the gate has to be the whole file, not a sample. Fall-back-never-
    fail is only true if nothing malformed can get past validation in
    the first place.
    """

    def test_the_shipped_library_still_validates(self):
        self.assertEqual("", _library._validate(_valid()))

    def test_a_bad_entry_late_in_the_list_is_caught(self):
        """The specific shape that bricked the add-on."""
        lib = _valid()
        lib["conditions"][7] = "just a string"
        self.assertIn("conditions[7]", _library._validate(lib))

    def test_the_last_entry_is_checked(self):
        """A sampling validator would wave this through."""
        lib = _valid()
        last = len(lib["conditions"]) - 1
        lib["conditions"][last] = {"name": None, "summary": "s"}
        self.assertIn(f"conditions[{last}]", _library._validate(lib))

    def test_missing_required_field_is_caught(self):
        lib = _valid()
        lib["conditions"][500] = {"name": "X"}
        self.assertIn("summary", _library._validate(lib))

    def test_empty_summary_is_caught(self):
        lib = _valid()
        lib["conditions"][4]["summary"] = "   "
        self.assertIn("empty", _library._validate(lib))

    def test_a_string_where_a_list_belongs_is_caught(self):
        """The worst shape of the lot, because it does not raise.

        `_conditions` iterates `aliases`. A string iterates character by
        character instead of failing, so a single bad entry injects one
        one-character phrase per letter into the matcher and every card
        in the collection lights up.
        """
        for field in ("aliases", "utd"):
            lib = _valid()
            lib["conditions"][3][field] = "abc"
            self.assertIn(field, _library._validate(lib), field)
        lib = _valid()
        lib["drugs"][2]["brands"] = "Panadol"
        self.assertIn("brands", _library._validate(lib))

    def test_drug_entries_are_checked_too(self):
        lib = _valid()
        lib["drugs"][1000]["generic"] = 1
        self.assertIn("drugs[1000]", _library._validate(lib))

    def test_every_vocabulary_is_checked(self):
        """Not just conditions and drugs - all seven lists."""
        for key in ("conditions", "new_conditions", "drugs", "signs",
                    "descriptive", "preclinical", "psych"):
            lib = _valid()
            lib[key][0] = ["not an object"]
            self.assertIn(key, _library._validate(lib), key)

    def test_mapping_vocabularies_are_checked(self):
        for key, bad in (("acronyms", {"a": 1}),
                         ("drugbank_ids", None),
                         ("rich_summaries", ["a"])):
            lib = _valid()
            lib[key]["ZZZ"] = bad
            self.assertIn(key, _library._validate(lib), key)

    def test_a_non_http_entry_url_is_refused(self):
        """Entry URLs are navigated to in the panel's authenticated profile.

        `_is_safe_url` in `__init__.py` is the second gate and blocks
        these at click time. This is the first, and it is the one that
        stops the value being stored at all - which matters because the
        stored copy outlives the session that downloaded it.
        """
        for bad in ("javascript:alert(1)", "file:///etc/passwd",
                    "data:text/html,<script>x</script>"):
            lib = _valid()
            lib["conditions"][3]["url"] = bad
            self.assertIn("url", _library._validate(lib), bad)

    def test_an_https_entry_url_is_allowed(self):
        lib = _valid()
        lib["conditions"][3]["url"] = "https://www.ncbi.nlm.nih.gov/books/NBK1/"
        self.assertEqual("", _library._validate(lib))

    def test_validation_is_fast_enough_to_run_at_every_launch(self):
        """Checking the whole file is only defensible if it is cheap.

        Measured at ~1 ms for the shipped library. The bound is loose
        because CI machines vary; it exists to catch someone making this
        accidentally quadratic, not to police milliseconds.
        """
        import time
        lib = _valid()
        t = time.time()
        _library._validate(lib)
        self.assertLess(time.time() - t, 1.0)


class RejectedDownloadsAreQuarantined(unittest.TestCase):
    """Falling back covers the launch. It does not cover the next one.

    Without quarantine the bad file stays the preferred copy and is
    re-read, re-parsed and re-rejected forever, so a single bad publish
    is a permanent state the user cannot see or clear.
    """

    def test_quarantine_renames_rather_than_deletes(self):
        d = tempfile.mkdtemp()
        path = os.path.join(d, "library.json")
        with open(path, "w") as fh:
            fh.write("{}")
        _library._quarantine(path, "test")
        self.assertFalse(os.path.exists(path))
        self.assertTrue(os.path.exists(path + ".rejected"),
                        "evidence must survive for a bug report")

    def test_only_the_downloaded_copy_is_quarantined(self):
        """A bundled copy that fails means the install is damaged.

        Renaming it would turn a reinstallable problem into an
        unrecoverable one, so `_load` must only quarantine USER_COPY.
        """
        src = (ROOT / "pearls" / "_library.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_load":
                calls = [n for n in ast.walk(node)
                         if isinstance(n, ast.Call)
                         and getattr(n.func, "id", "") == "_quarantine"]
                self.assertTrue(calls, "_load should quarantine bad downloads")
                for call in calls:
                    guard = ast.dump(node)
                    self.assertIn("downloaded", guard)
                return
        self.fail("_load not found")


class UpdaterTransport(unittest.TestCase):
    """`urllib.request.urlopen` is not an HTTP client.

    Its default opener also carries FileHandler, FTPHandler and
    DataHandler. Two attacker-influenced strings reached it in 2.0.1:
    the manifest URL (from config, a plain JSON file any other add-on
    can write) and the library URL (from the manifest body, so from
    whoever controls the content host).
    """

    def test_non_https_schemes_are_refused(self):
        for bad in ("file:///etc/passwd", "ftp://host/x",
                    "data:text/plain,x", "http://host/x",
                    "http://localhost:8765/", None, 42, ""):
            with self.assertRaises(ValueError, msg=repr(bad)):
                _updater._require_https(bad, "test")

    def test_https_is_allowed_case_insensitively(self):
        _updater._require_https("https://example.org/x", "test")
        _updater._require_https("HTTPS://example.org/x", "test")

    def test_both_fetches_are_scheme_checked(self):
        """Not just the manifest.

        2.0.1 asserted the manifest URL was https in a test and left the
        library URL - the one that comes from the manifest body, and so
        the one an attacker actually controls - unchecked.
        """
        src = (ROOT / "pearls" / "_updater.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        fetch = next(n for n in ast.walk(tree)
                     if isinstance(n, ast.FunctionDef) and n.name == "_fetch")
        names = [getattr(n.func, "id", "") for n in ast.walk(fetch)
                 if isinstance(n, ast.Call)]
        self.assertGreaterEqual(
            names.count("_require_https"), 2,
            "_fetch must check the URL it was given and the URL it "
            "landed on; every caller goes through _fetch")

    def test_the_default_manifest_url_is_https(self):
        self.assertTrue(
            _updater.DEFAULT_MANIFEST_URL.startswith("https://"))

    def test_the_configured_manifest_url_is_https(self):
        src = (ROOT / "_config.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and any(
                    getattr(t, "id", "") == "_DEFAULTS" for t in node.targets):
                defaults = ast.literal_eval(node.value)
                self.assertTrue(
                    defaults["libraryManifestUrl"].startswith("https://"))
                return
        self.fail("_DEFAULTS not found")

    def test_redirect_downgrade_is_rechecked(self):
        """GitHub release downloads redirect, so redirects must be followed.

        CPython's `HTTPRedirectHandler.http_error_302` already refuses to
        follow anything but http, https and ftp, so a redirect cannot
        reach `file:`. It can still land on plain http, which is why
        `_fetch` checks the final URL as well as the requested one.
        """
        src = (ROOT / "pearls" / "_updater.py").read_text(encoding="utf-8")
        self.assertIn("after redirect", src)


class AtomicWriteDoesNotFollowSymlinks(unittest.TestCase):
    """`open(tmp, "wb")` follows symlinks.

    A pre-planted `library.json.part` pointing at any file the Anki
    process can write turned the atomic write into a truncate-and-
    overwrite of that target. Verified against the 2.0.1 implementation
    before the fix: the victim file ended up holding the payload.
    """

    def test_a_planted_symlink_does_not_get_written_through(self):
        d = tempfile.mkdtemp()
        victim = os.path.join(d, "VICTIM")
        with open(victim, "w") as fh:
            fh.write("original")
        target = os.path.join(d, "sub", "library.json")
        os.makedirs(os.path.dirname(target))
        os.symlink(victim, target + ".part")

        _updater._write_atomically(target, b'{"ok":1}')

        with open(victim) as fh:
            self.assertEqual("original", fh.read(),
                             "the symlink target must not be written")
        with open(target) as fh:
            self.assertEqual('{"ok":1}', fh.read())

    def test_the_write_still_works_normally(self):
        d = tempfile.mkdtemp()
        target = os.path.join(d, "sub", "library.json")
        _updater._write_atomically(target, b"first")
        _updater._write_atomically(target, b"second")
        with open(target) as fh:
            self.assertEqual("second", fh.read())
        self.assertFalse(os.path.exists(target + ".part"),
                         "no partial file may survive a successful write")

    def test_no_partial_file_survives_a_failed_write(self):
        d = tempfile.mkdtemp()
        target = os.path.join(d, "library.json")

        class Boom(bytes):
            def __len__(self):
                raise RuntimeError("boom")

        try:
            _updater._write_atomically(target, Boom(b"x"))
        except Exception:
            pass
        self.assertFalse(os.path.exists(target + ".part"))


class MarkerJsEscaping(unittest.TestCase):
    """Library text reaches the DOM, and is no longer author-controlled."""

    def _marker(self):
        return (ROOT / "web" / "marker.js").read_text(encoding="utf-8")

    def test_esc_covers_every_html_metacharacter(self):
        """Including the apostrophe.

        Not exploitable while every attribute in the file is double-
        quoted, which they are. It is covered because the failure mode is
        invisible: a single-quoted attribute added later would be
        injectable and nothing around it would look wrong.
        """
        src = self._marker()
        start = src.index("function _esc(")
        body = src[start:src.index("\n  }", start)]
        for ch in ("&", "<", ">", '"', "'"):
            self.assertIn(f"/{ch}/g", body, f"_esc must escape {ch!r}")

    def test_trivia_goes_through_esc(self):
        """The pool is author-written today, but it shares the render path."""
        self.assertIn("_esc(egg.t)", self._marker())

    def test_no_raw_library_text_reaches_innerhtml(self):
        """Every innerHTML write must be built from _esc'd parts.

        This is a coarse check by design: it asserts the file contains no
        `innerHTML =` whose right-hand side names a bare summary/title
        variable. A precise check would need a JS parser; this catches
        the careless case, which is the one that happens.
        """
        src = self._marker()
        for line in src.split("\n"):
            if "innerHTML" not in line or "=" not in line:
                continue
            rhs = line.split("=", 1)[1]
            for bare in ("summary", "title", "raw", "body"):
                self.assertNotIn(
                    f" {bare};", rhs,
                    f"raw {bare} assigned to innerHTML: {line.strip()}")


class ConfigWriteBackPattern(unittest.TestCase):
    """`set_value` writes the whole config dict back to meta.json.

    This is what froze `libraryAutoUpdate: false` into per-install state
    for 2.0.0 users before anyone could choose it, and required a
    migration to undo. The pattern is unchanged - it is how Anki's
    addonManager works - so this test does not forbid it. It pins the
    fact that every key touched by an automatic first-run write is
    frozen at whatever the default was on that launch, so that changing
    any of those defaults later is known to reach nobody.
    """

    def _defaults(self):
        tree = ast.parse((ROOT / "_config.py").read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and any(
                    getattr(t, "id", "") == "_DEFAULTS" for t in node.targets):
                return ast.literal_eval(node.value)
        self.fail("_DEFAULTS not found")

    def test_keys_written_automatically_are_documented_as_frozen(self):
        """`set_value` reads the whole config and writes the whole config.

        That is how Anki's addonManager works, so this does not forbid
        the pattern. It pins the consequence: `_extras._on_answer` calls
        `set_value` on every answered card, so the first answered card on
        a fresh install writes the entire default set into meta.json.
        Every default becomes a stored value before the user has opened
        Settings, which is exactly how `libraryAutoUpdate: false` froze
        for 2.0.0 users and needed a migration to undo.

        The test that matters is therefore: does anything write config
        automatically, and does `set_value` still write the whole dict?
        If both stay true, changing any shipped default reaches only
        fresh installs, and any new default needs a migration.
        """
        tree = ast.parse((ROOT / "_config.py").read_text(encoding="utf-8"))
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "set_value")
        dumped = ast.dump(fn)
        self.assertIn("getConfig", dumped)
        self.assertIn("writeConfig", dumped,
                      "set_value writes the whole config dict back")
        self.assertIn("set_value", (ROOT / "_extras.py").read_text("utf-8"),
                      "an automatic writer is what freezes the defaults")

    def test_the_migration_is_idempotent(self):
        """It must key on a stamp, not on the value it changes."""
        src = (ROOT / "__init__.py").read_text(encoding="utf-8")
        self.assertIn("libraryAutoUpdateMigrated", src)




class ContentVersionFormat(unittest.TestCase):
    """The bundled version must never sort below the published one.

    Content versions are compared as strings (or, in the current
    client, parsed as a date tuple with a same-day counter).

    Historically both defaults were `%Y.%m.%d`. From 2026-08-28 both
    default to `%d.%m.%Y` (Australian) with a per-day counter that
    resets at local midnight; the sort-order guard parses either shape
    into a tuple so mid-history transition is safe.
    """

    def _manifest(self):
        return json.loads(
            (ROOT / "data" / "manifest.json").read_text(encoding="utf-8"))

    def test_the_two_defaults_use_the_same_format(self):
        py = (ROOT / "tools" / "build_library.py").read_text(encoding="utf-8")
        sh = (ROOT / "tools" / "publish_content.sh").read_text(encoding="utf-8")
        self.assertIn("%d.%m.%Y", py,
                      "build_library.py must default to the d.m.y format")
        self.assertNotIn("date.today().isoformat()", py)
        self.assertIn("%d.%m.%Y", sh)

    def test_the_bundled_version_is_dotted_and_padded(self):
        import re
        v = self._manifest()["content_version"]
        self.assertRegex(
            v,
            r"^(?:\d{4}\.\d{2}\.\d{2}|\d{2}\.\d{2}\.\d{4})(\.\d+)?$",
            "zero-padded dotted date in either y.m.d or d.m.y; "
            "1.9.2026 sorts above 15.09.2026 as strings")

    def test_the_bundled_version_sorts_at_or_above_every_shipped_release(self):
        """Guards against shipping an add-on that downgrades itself.

        The channel was seeded at 2026.08.18 (y.m.d). Any bundled version
        that sorts below a version already on the channel means a fresh
        install replaces its own content with older content.

        Naive string compare works within a single format but fails
        across the y.m.d -> d.m.y transition (2026-08-28) - "01.09.2026"
        would sort below "2026.08.18" as strings. Parse both to a
        (y, m, d, counter) tuple, matching the publish script's guard.
        """
        def parse(v):
            parts = v.split(".")
            counter = 0
            if len(parts) == 4:
                counter = int(parts[3]); parts = parts[:3]
            if len(parts) != 3:
                return None
            a, b, c = parts
            if len(a) == 4:
                y, m, d = int(a), int(b), int(c)
            elif len(c) == 4:
                d, m, y = int(a), int(b), int(c)
            else:
                return None
            return (y, m, d, counter)
        self.assertGreater(
            parse(self._manifest()["content_version"]), parse("2026.08.18"))

    def test_the_manifest_is_never_behind_the_library(self):
        """Equal in a build; the manifest may be ahead in the repository.

        `data/manifest.json` is the published channel pointer and only
        `tools/publish_content.sh` moves it. Between a code push and the
        next content publish the repository legitimately holds a
        manifest naming a *later* content version than the bundled
        `library.json` - that is the channel being ahead of the shipped
        floor, which is the whole point of having a channel.

        What must never happen is the manifest sorting *below* the
        bundled library. That means a code push has dragged the pointer
        backwards over a publish, and every client then reads a stale or
        url-less manifest and silently stops updating.
        """
        lib = json.loads(
            (ROOT / "data" / "library.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(self._manifest()["content_version"],
                                lib["content_version"])


class AuthenticatedProfileNavigation(unittest.TestCase):
    """A shared deck must not be able to steer the add-on's sessions.

    `data-sp-url` is an ordinary HTML attribute, so anything that can
    write card HTML can set it - which includes any deck downloaded from
    AnkiWeb. Clicking a marked span navigates a QWebEngineProfile
    holding live NCBI, DrugBank, UpToDate and chat sessions.

    `SECURITY.md` named this in scope from the start, but the only
    response was a debug-level log line: `_is_safe_url` checked the
    scheme and allowed any host. Trust is now decided by provenance -
    the hosts the add-on integrates with, plus the hosts the user has
    themselves configured. Untrusted hosts open in the normal browser
    instead, so a legitimate link still works without borrowing a
    session.
    """

    def _fns(self):
        src = (ROOT / "__init__.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        want = {"_host_of", "_user_configured_hosts", "_is_trusted_host"}
        fns = [n for n in tree.body
               if isinstance(n, ast.FunctionDef) and n.name in want]
        self.assertEqual(len(fns), 3, "trust helpers missing from __init__")
        known = [n for n in tree.body if isinstance(n, ast.Assign)
                 and any(getattr(t, "id", "") == "_KNOWN_HOSTS"
                         for t in n.targets)][0]
        from urllib.parse import urlparse
        cfg = {}

        class _cfg:
            @staticmethod
            def get(k):
                return cfg.get(k)

        ns = {"urlparse": urlparse, "_config": _cfg}
        exec(compile(ast.Module(body=[known] + fns, type_ignores=[]),
                     "<trust>", "exec"), ns)
        return ns["_is_trusted_host"], cfg

    def test_integration_hosts_are_trusted(self):
        trusted, _ = self._fns()
        for url in ("https://www.ncbi.nlm.nih.gov/books/NBK1/",
                    "https://go.drugbank.com/drugs/DB1",
                    "https://www.uptodate.com/contents/x",
                    "https://uptodate.com.acs.hcn.com.au/x"):
            self.assertTrue(trusted(url), url)

    def test_an_arbitrary_host_is_not_trusted(self):
        trusted, _ = self._fns()
        for url in ("https://evil.example/steal",
                    "http://localhost:8765/",
                    "https://192.168.1.1/",
                    ""):
            self.assertFalse(trusted(url), url)

    def test_host_matching_is_anchored_on_a_dot_boundary(self):
        """The original check was a bare `endswith`.

        That accepts `notncbi.nlm.nih.gov` and `evil-drugbank.com`, which
        an attacker can simply register. Matching must be on equality or
        on a dot-delimited suffix.
        """
        trusted, _ = self._fns()
        for url in ("https://notncbi.nlm.nih.gov/",
                    "https://evilgo.drugbank.com.attacker.test/",
                    "https://ncbi.nlm.nih.gov.evil.example/",
                    "https://www.ncbi.nlm.nih.gov@evil.example/"):
            self.assertFalse(trusted(url), url)

    def test_subdomains_of_a_trusted_host_are_trusted(self):
        trusted, _ = self._fns()
        self.assertTrue(trusted("https://pmc.ncbi.nlm.nih.gov/x"))

    def test_the_users_own_custom_term_hosts_are_trusted(self):
        """This is why the allowlist cannot be a fixed list of domains.

        The custom terms feature exists so the user can point it
        anywhere. Deriving the allowlist from their own config keeps
        that working while still excluding anything a card supplies.
        """
        trusted, cfg = self._fns()
        cfg["customTerms"] = json.dumps(
            [{"title": "Wiki", "url": "https://wiki.mydept.org/x"}])
        self.assertTrue(trusted("https://wiki.mydept.org/anything"))
        self.assertTrue(trusted("https://sub.wiki.mydept.org/x"))
        self.assertFalse(trusted("https://wiki.mydept.org.evil.example/"))

    def test_configured_provider_and_institution_hosts_are_trusted(self):
        trusted, cfg = self._fns()
        cfg["uptodateHomeUrl"] = "https://utd.myhospital.health.nsw.gov.au/"
        cfg["chatCustomProviderUrl"] = "https://chat.internal/"
        self.assertTrue(trusted("https://utd.myhospital.health.nsw.gov.au/x"))
        self.assertTrue(trusted("https://chat.internal/z"))

    def test_malformed_config_does_not_fail_open(self):
        """Failing open would silently restore the old behaviour."""
        trusted, cfg = self._fns()
        for bad in ("{not json", "[]", json.dumps(["a string", 42, {"x": 1}])):
            cfg["customTerms"] = bad
            self.assertFalse(trusted("https://evil.example/"), bad)

    def test_untrusted_urls_open_externally_rather_than_being_dropped(self):
        """Silently dropping a working link would be a bug report.

        The handler must call openLink for an untrusted host, and must
        decide this before the UpToDate branch - that branch would
        otherwise hand the URL the UTD profile.
        """
        src = (ROOT / "__init__.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "_on_js_message")
        body = ast.dump(fn)
        self.assertIn("_is_trusted_host", body)
        guard = src.index("_is_trusted_host(url)")
        utd = src.index('if "uptodate.com" in url:', guard - 4000)
        self.assertLess(guard, utd,
                        "the trust check must precede UpToDate routing")

    def test_the_scheme_check_still_runs_first(self):
        """Host trust does not replace `_is_safe_url`.

        A `javascript:` URL has no hostname, so it would be untrusted and
        handed to openLink - which is not where a javascript: URL should
        go either. The scheme gate must remain ahead of it.
        """
        src = (ROOT / "__init__.py").read_text(encoding="utf-8")
        self.assertLess(src.index("_is_safe_url(url)"),
                        src.index("_is_trusted_host(url)"))



class DrugNameCoverage(unittest.TestCase):
    """A missing spelling is not a degraded popup, it is no popup.

    Measured against 79 names an Australian student's cards actually
    use, 23 resolved to nothing before this: `frusemide`, `cephalexin`,
    `cephazolin`, `thyroxine`, `glyceryl trinitrate` and the rest. Those
    words highlighted nothing at all, which is invisible in a way a
    short summary is not - nothing appears, so nothing looks wrong.
    """

    def _drugs(self):
        from pearls import _drugs
        return _drugs

    def test_australian_spellings_resolve(self):
        d = self._drugs()
        for word, expect in (("frusemide", "furosemide"),
                             ("cephalexin", "cefalexin"),
                             ("cephazolin", "cefazolin"),
                             ("thyroxine", "levothyroxine"),
                             ("amoxycillin", "amoxicillin"),
                             ("indomethacin", "indometacin"),
                             ("cholecalciferol", "colecalciferol"),
                             ("sulphasalazine", "sulfasalazine"),
                             ("glyceryl trinitrate", "glyceryl trinitrate"),
                             ("valproate", "sodium valproate")):
            names = [x["name"] for x in d.resolve(f"Gave {word} today.")]
            self.assertIn(expect, names, word)

    def test_aliases_are_case_insensitive(self):
        """They are generics, not brands.

        Routing them through the brand path would match `frusemide`
        mid-sentence and miss `Frusemide` at the start of one.
        """
        d = self._drugs()
        for word in ("frusemide", "Frusemide", "FRUSEMIDE"):
            names = [x["name"] for x in d.resolve(f"{word} was given.")]
            self.assertIn("furosemide", names, word)

    def test_no_american_generic_is_displayed(self):
        """The popup heading is the most visible place the rule applies.

        `estradiol` and `lidocaine` were on this list until 2.2 and are
        not American - they are the current Australian Approved Names,
        and asserting otherwise is what kept the 5a decision pointing the
        wrong way for three releases. What makes a name wrong for the
        heading is that the TGA has superseded it, which is the test
        below, not that Americans also use it.
        """
        lib = json.loads(
            (ROOT / "data" / "library.json").read_text(encoding="utf-8"))
        generics = {d["generic"].lower() for d in lib["drugs"]}
        for us in ("meperidine", "rifampin", "nitroglycerin",
                   "acetaminophen", "epinephrine", "albuterol"):
            self.assertNotIn(us, generics,
                             f"{us} is displayed as a popup heading")

    def test_no_superseded_australian_name_is_displayed(self):
        """A superseded heading is invisible: it looks entirely normal.

        Every one of these is on the TGA's affected-ingredients list and
        every one of them headed a popup before 2.2. Nothing reports it,
        because a wrong-but-plausible drug name reads exactly like a
        right one - which is the same failure mode as a term that never
        highlights.
        """
        lib = json.loads(
            (ROOT / "data" / "library.json").read_text(encoding="utf-8"))
        generics = {d["generic"].lower() for d in lib["drugs"]}
        for old in ("lignocaine", "oestradiol", "phenobarbitone",
                    "beclomethasone", "cysteamine", "benztropine",
                    "frusemide", "cephalexin", "benzhexol"):
            self.assertNotIn(old, generics,
                             f"{old} is displayed as a popup heading")

    def test_superseded_and_american_spellings_still_resolve(self):
        """Renaming the heading must not drop cards written the old way.

        This is the whole reason the 5a reversal is safe: an Australian
        card saying `lignocaine` and a textbook saying `lidocaine` both
        land on the same popup, and only the heading changed.
        """
        d = self._drugs()
        for word, expect in (("meperidine", "pethidine"),
                             ("rifampin", "rifampicin"),
                             ("nitroglycerin", "glyceryl trinitrate"),
                             ("lignocaine", "lidocaine"),
                             ("lidocaine", "lidocaine"),
                             ("oestradiol", "estradiol"),
                             ("estradiol", "estradiol"),
                             ("phenobarbitone", "phenobarbital"),
                             ("beclomethasone", "beclometasone"),
                             ("cysteamine", "mercaptamine (cysteamine)"),
                             ("mercaptamine", "mercaptamine (cysteamine)")):
            names = [x["name"] for x in d.resolve(f"Gave {word} today.")]
            self.assertIn(expect, names, word)

    def test_the_mandated_dual_label_inns_resolve(self):
        """`epinephrine` is printed on Australian ampoules by regulation.

        Adrenaline and noradrenaline are dual labelled permanently, INN
        in brackets, so a card written off the ampoule carries the word.
        It resolves; the heading stays Australian.
        """
        d = self._drugs()
        for word, expect in (("epinephrine", "adrenaline"),
                             ("norepinephrine", "noradrenaline")):
            names = [x["name"] for x in d.resolve(f"Gave {word} today.")]
            self.assertIn(expect, names, word)

    def test_a_rename_keeps_its_drugbank_accession(self):
        """A rename that drops the accession downgrades the popup button
        from the drug's monograph to a search page, and looks fine.

        `glyceryl trinitrate` shipped that way from 2.1.1 to 2.2:
        DB00727 stayed keyed to `nitroglycerin` and every GTN popup
        opened a search. Nothing surfaces it, because a search page is a
        plausible result.
        """
        lib = json.loads(
            (ROOT / "data" / "library.json").read_text(encoding="utf-8"))
        ids = lib["drugbank_ids"]
        generics = {d["generic"].lower() for d in lib["drugs"]}
        for new, old in (("glyceryl trinitrate", "nitroglycerin"),
                         ("lidocaine", "lignocaine"),
                         ("estradiol", "oestradiol"),
                         ("phenobarbital", "phenobarbitone")):
            if old in ids:
                self.assertIn(new, ids,
                              f"{old} carries an accession that {new} lost")
            self.assertIn(new, generics)

    def test_no_duplicate_generics(self):
        lib = json.loads(
            (ROOT / "data" / "library.json").read_text(encoding="utf-8"))
        names = [d["generic"].lower() for d in lib["drugs"]]
        dupes = {n for n in names if names.count(n) > 1}
        self.assertFalse(dupes, f"duplicate drug entries: {dupes}")

    def test_an_alias_on_an_unknown_generic_fails_the_build(self):
        """Silent is the failure mode being prevented.

        An alias keyed on a generic that does not exist simply never
        matches, and nothing reports it. This caught `mercaptopurine`,
        which turned out to be missing from the library entirely.
        """
        src = (ROOT / "tools" / "build_library.py").read_text(encoding="utf-8")
        self.assertIn("would never match", src)



class ValidationReachesInsideLists(unittest.TestCase):
    """The 2.1 depth fix stopped one level short of where it mattered.

    `_validate` was taught to check every entry of every vocabulary
    rather than only the first. It checked that `aliases`, `brands` and
    `utd` were lists - but not what was *in* them. Every consumer
    lowercases those elements to build its lookup tables, so a single
    `int` or `None` among them raises `AttributeError` at import, which
    is the identical permanent brick the depth fix existed to prevent:
    the file validates, is written to `user_files/`, is preferred at
    every launch, and the Settings switch that would disable updates
    lives in the add-on that no longer imports.

    This was measured, not argued. Six poisoned shapes passed the
    type-only check; four of them killed the import. `_drugs.py`
    survived two of them only because it happens to carry an
    `isinstance` guard that the other six consumers do not - so the fix
    belongs in the validator, where it covers all seven at once.
    """

    def _reject(self, mutate, what):
        lib = _valid()
        mutate(lib)
        why = _library._validate(lib)
        self.assertTrue(why, f"{what} passed validation")
        return why

    def test_non_string_in_condition_aliases_is_rejected(self):
        self._reject(lambda d: d["conditions"][7].__setitem__("aliases", ["ok", 5]),
                     "an int in conditions[].aliases")
        self._reject(lambda d: d["conditions"][8].__setitem__("aliases", [None]),
                     "a None in conditions[].aliases")
        self._reject(lambda d: d["conditions"][9].__setitem__("aliases", [["x"]]),
                     "a nested list in conditions[].aliases")

    def test_non_string_in_drug_brands_is_rejected(self):
        self._reject(lambda d: d["drugs"][3].__setitem__("brands", [7]),
                     "an int in drugs[].brands")
        self._reject(lambda d: d["drugs"][4].__setitem__("aliases", [7]),
                     "an int in drugs[].aliases")

    def test_malformed_utd_pairs_are_rejected(self):
        """`utd` is not a list of strings; it is [label, query] pairs, and
        `_conditions._primary_url` reaches into it as `utd[0][1]`.

        All four of these returned "" from the shipped validator and then
        crashed `resolve()`, which runs on every card shown - so the
        symptom is a broken popup on every card, not a single import
        failure.
        """
        for val, what in (([{"a": 1}], "a dict"),
                          (["x"], "a bare string"),
                          ([[1, 2]], "a non-string pair"),
                          ([["only"]], "a 1-element pair")):
            self._reject(lambda d, v=val: d["conditions"][0].__setitem__("utd", v),
                         f"{what} in conditions[].utd")

    def test_wellformed_utd_pairs_are_accepted(self):
        lib = _valid()
        lib["conditions"][0]["utd"] = [["Adult Mx", "treatment of x"]]
        self.assertEqual(_library._validate(lib), "")

    def test_malformed_acronym_candidates_are_rejected(self):
        first = list(_valid()["acronyms"])[0]
        self._reject(lambda d: d["acronyms"].__setitem__(first, [3]),
                     "a bare int as an acronym candidate")
        self._reject(lambda d: d["acronyms"].__setitem__(first, [["a"]]),
                     "a 1-element acronym candidate")
        self._reject(lambda d: d["acronyms"].__setitem__(first, [[1, [], "d"]]),
                     "a non-string acronym expansion")
        self._reject(lambda d: d["acronyms"].__setitem__(first, [["e", [7], "d"]]),
                     "a non-string acronym context word")

    def test_the_shipped_library_still_passes(self):
        """The check has to be strict without being wrong about real content."""
        self.assertEqual(_library._validate(_valid()), "")


class UrlParsingAgreesWithTheBrowser(unittest.TestCase):
    """`_is_trusted_host` decided on one parse and Chromium loaded another.

    Trust is computed with Python's `urlparse`; the URL is then handed
    to a QWebEngineView, which follows the WHATWG URL spec. They
    disagree about a backslash in the authority - WHATWG treats it as
    `/`, `urlparse` treats it as a hostname character - and that
    disagreement is a complete bypass of the provenance check, verified
    against both parsers:

        https://evil.com\\.ncbi.nlm.nih.gov/
            urlparse -> evil.com\\.ncbi.nlm.nih.gov   -> TRUSTED
            Chromium -> evil.com

        https://evil.com\\@ncbi.nlm.nih.gov/
            urlparse -> ncbi.nlm.nih.gov              -> TRUSTED
            Chromium -> evil.com

    `data-sp-url` is card-settable, so either string in a shared deck
    loaded an attacker's host into the profile holding live NCBI,
    DrugBank, UpToDate and chat sessions. `_is_safe_url` now refuses the
    character outright, because the defect is acting on a different
    parse than the one that was checked, not the specific character.
    """

    def _is_safe_url(self):
        src = (ROOT / "__init__.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        fn = [n for n in tree.body
              if isinstance(n, ast.FunctionDef) and n.name == "_is_safe_url"]
        self.assertEqual(len(fn), 1, "_is_safe_url missing from __init__")
        ns = {}
        exec(compile(ast.Module(body=fn, type_ignores=[]), "<safe>", "exec"), ns)
        return ns["_is_safe_url"]

    def test_backslash_urls_are_refused(self):
        safe = self._is_safe_url()
        for url in ("https://evil.com\\.ncbi.nlm.nih.gov/",
                    "https://evil.com\\@ncbi.nlm.nih.gov/",
                    "https://evil.com\\/.go.drugbank.com/",
                    "https://www.uptodate.com\\@evil.com/"):
            self.assertFalse(safe(url), f"accepted {url!r}")

    def test_control_characters_are_refused(self):
        """Browsers strip tab, CR and LF before parsing; urlparse does not."""
        safe = self._is_safe_url()
        for url in ("https://evil.com\t@www.ncbi.nlm.nih.gov/",
                    "https://www.ncbi.nlm.nih.gov\r\n.evil.com/",
                    "https://evil.com\n@go.drugbank.com/"):
            self.assertFalse(safe(url), f"accepted {url!r}")

    def test_ordinary_urls_still_pass(self):
        safe = self._is_safe_url()
        for url in ("https://www.ncbi.nlm.nih.gov/books/NBK430685/",
                    "https://go.drugbank.com/drugs/DB00945",
                    "http://example.org/a?b=c#d",
                    "  https://www.uptodate.com/contents/x  "):
            self.assertTrue(safe(url), f"rejected {url!r}")

    def test_the_two_parsers_now_agree_on_everything_accepted(self):
        """The property, rather than the blocklist: anything `_is_safe_url`
        accepts must give the same host under both parsing rules."""
        from urllib.parse import urlparse
        safe = self._is_safe_url()
        cases = ["https://evil.com\\.ncbi.nlm.nih.gov/",
                 "https://evil.com\\@ncbi.nlm.nih.gov/",
                 "https://www.ncbi.nlm.nih.gov/books/NBK1/",
                 "https://evil.com\t@www.ncbi.nlm.nih.gov/",
                 "https://go.drugbank.com/drugs/DB1"]
        for url in cases:
            if not safe(url):
                continue
            # WHATWG splits the authority on the first of / \\ ? #; with
            # backslashes and control characters refused, `urlparse` and
            # that rule cannot diverge.
            host = (urlparse(url).hostname or "")
            rest = url.split("//", 1)[1]
            authority = re.split(r"[/\\?#]", rest, 1)[0].rsplit("@", 1)[-1]
            self.assertEqual(host, authority.lower().split(":")[0],
                             f"parsers disagree on {url!r}")


class ConcurrentDownloadsDoNotCorruptTheLibrary(unittest.TestCase):
    """Two checks can run at once, and they shared one temp filename.

    `check_in_background` fires at launch and the "Check now" button in
    Settings calls the same code, so two writers are reachable. With a
    fixed `library.json.part` the interleaving is:

        A  os.open(tmp, O_EXCL)          -> inode 1
        B  os.unlink(tmp)                -> A's directory entry removed
        B  os.open(tmp, O_EXCL)          -> inode 2, starts writing
        A  finishes, os.replace(tmp, ..) -> renames B's half-written file

    leaving a truncated `library.json`. `_validate` catches it at the
    next launch and falls back, so nothing breaks, but the user's
    content silently reverts with no error anywhere. A per-writer temp
    name removes the interleaving rather than narrowing it.
    """

    def test_temp_name_is_unique_per_writer(self):
        src = (ROOT / "pearls" / "_updater.py").read_text(encoding="utf-8")
        self.assertNotIn('tmp = path + ".part"', src,
                         "the shared temp filename is back")
        self.assertIn("os.getpid()", src)
        self.assertIn("threading.get_ident()", src)

    def test_concurrent_writers_leave_a_complete_file(self):
        import threading as _t
        with tempfile.TemporaryDirectory() as d:
            target = os.path.join(d, "sub", "library.json")
            payloads = [b"a" * 400_000, b"b" * 400_000]
            errors = []

            def w(body):
                try:
                    for _ in range(12):
                        _updater._write_atomically(target, body)
                except Exception as exc:                # noqa: BLE001
                    errors.append(exc)

            ts = [_t.Thread(target=w, args=(p,)) for p in payloads]
            for t in ts:
                t.start()
            for t in ts:
                t.join()
            self.assertFalse(errors, f"writer raised: {errors}")
            got = pathlib.Path(target).read_bytes()
            self.assertIn(got, payloads,
                          "library.json is neither writer's complete payload")
            leftovers = [f for f in os.listdir(os.path.dirname(target))
                         if f.endswith(".part")]
            self.assertFalse(leftovers, f"temp files left behind: {leftovers}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
