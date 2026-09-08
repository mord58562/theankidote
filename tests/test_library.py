# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""Tests for the split between content and code.

Content moved out of the Python modules and into `data/library.json` so
that a corrected summary can ship without an AnkiWeb release. That buys
a content channel and costs a class of failure the add-on did not have
before: a file it reads at startup can now be absent, truncated, stale,
malformed, or hostile. These tests are about that cost.
"""
import copy
import hashlib
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

from pearls import _conditions, _library, _updater  # noqa: E402


def _valid():
    return copy.deepcopy(_library.LIBRARY)


class BundledCopyIsTheFloor(unittest.TestCase):
    def test_bundled_library_exists_and_parses(self):
        self.assertTrue(os.path.exists(_library.BUNDLED),
                        "data/library.json is missing; a fresh install "
                        "would have no content at all")
        with open(_library.BUNDLED, encoding="utf-8") as fh:
            self.assertEqual(_library._validate(json.load(fh)), "")

    def test_manifest_matches_the_bundled_library(self):
        """The manifest may lead the bundled library, but never trail it.

        This originally asserted the two were identical, which was right
        while `data/manifest.json` was a build artefact sitting beside
        `library.json`. Since 2.0 it is the *published channel pointer*:
        `tools/publish_content.sh` moves it, and between a code release
        and the next content publish the repository legitimately holds a
        manifest naming a later content version, with a different sha
        and byte count, than the library bundled beside it. That is the
        channel being ahead of the shipped floor, which is the point of
        having a channel.

        So the test splits. When the manifest describes the bundled
        library, everything must agree exactly - a drift there means
        every client either re-downloads content it already has or
        refuses content it needs. When the manifest is ahead, only the
        invariants that must hold regardless are checked.

        What must never happen is the manifest sorting *below* the
        bundled library: that means a code push has dragged the pointer
        backwards over a publish, which silently stops updates for
        everyone until the next publish.
        """
        blob = pathlib.Path(_library.BUNDLED).read_bytes()
        manifest = json.loads(
            (pathlib.Path(_library.BUNDLED).parent / "manifest.json")
            .read_text(encoding="utf-8"))
        bundled_version = json.loads(blob.decode("utf-8"))["content_version"]

        self.assertEqual(manifest["schema"], _library.SCHEMA)
        self.assertGreaterEqual(
            manifest["content_version"], bundled_version,
            "the published manifest has been dragged behind the bundled "
            "library - a code push has overwritten a content publish")

        if manifest["content_version"] == bundled_version:
            self.assertEqual(manifest["sha256"],
                             hashlib.sha256(blob).hexdigest())
            self.assertEqual(manifest["bytes"], len(blob))


class OverridesStaySeparateFromBaseText(unittest.TestCase):
    """The rich summaries must not be merged into the base entries on disk.

    `_conditions` applies overrides by assigning to `entry["summary"]`.
    Those entries came from the loaded library, so without a copy the
    merge rewrites the library's own base text in memory - and
    `tools/build_library.py`, which reads the base back out to rebuild,
    would then write the override in as the base. The next edit to
    `content/_rich.py` would silently do nothing, because the text it
    replaces would already be there.
    """

    def test_base_text_differs_from_the_override(self):
        lib = json.loads(
            pathlib.Path(_library.BUNDLED).read_text(encoding="utf-8"))
        base = {c["name"]: c["summary"] for c in lib["conditions"]}
        shared = [n for n in lib["rich_summaries"] if n in base]
        self.assertGreater(len(shared), 20, "expected many overrides")
        identical = [n for n in shared if base[n] == lib["rich_summaries"][n]]
        self.assertEqual(
            identical, [],
            f"{len(identical)} override(s) have been baked into the base "
            f"text on disk; rebuild from the pre-merge source or the "
            f"override becomes uneditable")

    def test_importing_conditions_does_not_mutate_the_library(self):
        lib = json.loads(
            pathlib.Path(_library.BUNDLED).read_text(encoding="utf-8"))
        base = {c["name"]: c["summary"] for c in lib["conditions"]}
        loaded = {c["name"]: c["summary"]
                  for c in _library.get("conditions")}
        drifted = [n for n in base if base[n] != loaded.get(n)]
        self.assertEqual(
            drifted[:5], [],
            f"{len(drifted)} entries in the in-memory library no longer "
            f"match the file; something is mutating it in place")

    def test_overrides_still_reach_the_reader(self):
        for name in ("Vasculitis", "Hypokalaemia", "Serotonin syndrome"):
            self.assertEqual(_conditions._LOOKUP[name.lower()]["summary"],
                             _library.get("rich_summaries")[name],
                             f"{name}: override did not reach _LOOKUP")


class UpdaterRefusesBadPayloads(unittest.TestCase):
    def test_version_comparison_rejects_older_and_equal(self):
        self.assertTrue(_updater._newer("2026-09-01", "2026-08-18"))
        self.assertFalse(_updater._newer("2026-08-18", "2026-08-18"))
        self.assertFalse(_updater._newer("2026-07-01", "2026-08-18"))

    def test_unparseable_version_is_not_newer(self):
        """Refusing an update we cannot read is recoverable; applying one
        we misread is not."""
        for bogus in (None, "", 17, [], {"v": 1}):
            self.assertFalse(_updater._newer(bogus, "2026-08-18"),
                             f"{bogus!r} was treated as a newer version")

    def test_atomic_write_leaves_no_partial_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = os.path.join(tmp, "nested", "library.json")
            _updater._write_atomically(target, b'{"ok":true}')
            self.assertEqual(pathlib.Path(target).read_bytes(), b'{"ok":true}')
            self.assertFalse(os.path.exists(target + ".part"),
                             "temp file survived the rename")

    def test_atomic_write_replaces_rather_than_truncates(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = os.path.join(tmp, "library.json")
            _updater._write_atomically(target, b"first")
            _updater._write_atomically(target, b"second")
            self.assertEqual(pathlib.Path(target).read_bytes(), b"second")

    def test_updater_never_executes_the_payload(self):
        """The payload is data and must be read as data.

        `pickle.loads` or `exec` on a file fetched over the network is a
        remote shell for anyone who can spoof the host, and would put the
        add-on outside AnkiWeb's rules besides.
        """
        # Read the code, not the prose: this module's own docstring
        # explains why it does not unpickle anything, and a substring
        # search over the raw file would flag that explanation.
        import ast
        tree = ast.parse(
            (ROOT / "pearls" / "_updater.py").read_text(encoding="utf-8"))
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        names |= {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                names.add(node.module.split(".")[0])
        for forbidden in ("pickle", "exec", "eval", "marshal",
                          "__import__", "importlib", "subprocess"):
            self.assertNotIn(
                forbidden, names,
                f"{forbidden!r} is used in the updater; downloaded "
                f"content must never be executed")

    def test_download_is_size_capped(self):
        self.assertLessEqual(_updater._MAX_BYTES, 32 << 20)
        self.assertGreater(_updater._MAX_BYTES,
                           os.path.getsize(_library.BUNDLED))

    def test_the_check_is_off_the_ui_thread_and_daemonised(self):
        src = (ROOT / "pearls" / "_updater.py").read_text(encoding="utf-8")
        self.assertIn("daemon=True", src,
                      "a non-daemon thread can hold Anki open on quit")


class ShippedPackageContents(unittest.TestCase):
    def test_authoring_sources_are_not_imported_at_runtime(self):
        """`content/` is the authoring copy and is not packaged.

        If a module under `pearls/` imports it, the shipped add-on raises
        ImportError on a machine that has only the built package - which
        is every machine except this one.
        """
        for path in (ROOT / "pearls").glob("*.py"):
            src = path.read_text(encoding="utf-8")
            self.assertNotIn(
                "from ._rich import", src,
                f"{path.name} still imports the authoring copy of the "
                f"rich summaries; read them from the library instead")

    def test_build_script_ships_data_and_excludes_content(self):
        script = (ROOT / "build_ankiaddon.sh").read_text(encoding="utf-8")
        self.assertIn("data", script,
                      "data/ must be packaged or the add-on has no content")
        self.assertIn("content", script,
                      "content/ must be excluded from the package")

    # Everything at the top level is either shipped on purpose or
    # excluded on purpose. Listed here rather than inferred, so adding a
    # directory is a decision someone makes rather than a default.
    SHIPPED_TOP_LEVEL = {
        "__init__.py", "_config.py", "_dock_layout.py", "_extras.py",
        "_log.py", "_panel_pearls.py", "_theme.py", "_webengine.py",
        "chat", "config.json", "config.md", "data", "install.sh",
        "LICENSE", "manifest.json", "pearls", "README.md", "SECURITY.md",
        "uptodate", "web", "CHANGELOG.md",
    }
    # User-facing release notes, one per version, so a pattern rather
    # than a list that has to be edited on every release.
    SHIPPED_PATTERNS = ("WHATS-NEW-*.md",)

    def test_every_top_level_path_is_a_decision(self):
        """A new directory of working notes must not ship by default.

        The previous version of this class checked that the script
        mentioned the strings "data" and "content", which is true of a
        script that ships everything else in the tree. `docs/` and
        `audit/` were added months after those exclusions were written
        and went straight into every release - 1.16 MB of session
        checkpoints, coverage measurements and audit transcripts,
        including an 870 KB stale copy of summaries the package already
        carries in `data/library.json`, and the author's name and home
        directory in 24 places.

        Greping for a known name cannot catch the next one. This asserts
        the complement instead: every top-level path is either on the
        shipped list above or matched by an exclusion in the script, so
        a new one fails here until it is classified.
        """
        import fnmatch
        script = (ROOT / "build_ankiaddon.sh").read_text(encoding="utf-8")
        excludes = re.findall(r'-x "([^"]+)"', script)
        self.assertTrue(excludes, "no -x patterns found in build_ankiaddon.sh")

        unclassified = []
        for path in sorted(ROOT.iterdir()):
            name = path.name + ("/" if path.is_dir() else "")
            if path.name.startswith(".git"):
                continue
            if path.name in self.SHIPPED_TOP_LEVEL:
                continue
            if any(fnmatch.fnmatch(path.name, pat)
                   for pat in self.SHIPPED_PATTERNS):
                continue
            probe = path.name + "/x" if path.is_dir() else path.name
            if any(fnmatch.fnmatch(probe, pat) or
                   fnmatch.fnmatch(path.name, pat) for pat in excludes):
                continue
            unclassified.append(name)
        self.assertEqual(
            unclassified, [],
            f"these top-level paths would be packaged but are not on the "
            f"shipped list: {unclassified}. Either add them to "
            f"SHIPPED_TOP_LEVEL, or add an exclusion to "
            f"build_ankiaddon.sh.")


class PublishingContract(unittest.TestCase):
    """What `tools/publish_content.sh` and the updater must agree on."""

    def test_the_manifest_is_not_packaged(self):
        """`data/manifest.json` is published, not shipped.

        An earlier version of this test asserted the opposite - that the
        manifest on disk must carry no `url` - on the reasoning that a
        URL inside the .ankiaddon would be a stale pointer. The reasoning
        was right and the remedy was wrong: this file IS the published
        manifest, `tools/publish_content.sh` builds it with `--url` and
        commits it to the branch for clients to fetch, so forbidding the
        url made publishing fail its own test gate.

        Nothing in the running add-on opens it - `_library` reads
        library.json, `_updater` fetches the manifest over HTTPS - so
        the fix is to keep it out of the package instead.
        """
        script = (ROOT / "build_ankiaddon.sh").read_text(encoding="utf-8")
        self.assertIn(
            'data/manifest.json', script,
            "build_ankiaddon.sh must exclude data/manifest.json; it is "
            "the published pointer, not add-on data")

    def test_no_module_reads_the_bundled_manifest(self):
        """The exclusion above is only safe while this holds."""
        for path in list((ROOT / "pearls").glob("*.py")) + [ROOT / "__init__.py"]:
            src = path.read_text(encoding="utf-8")
            self.assertNotIn(
                'data", "manifest.json"', src,
                f"{path.name} opens the bundled manifest, which is not "
                f"shipped - read library.json instead")

    def test_a_published_manifest_names_an_https_url(self):
        """The url must be there, and must be https.

        This asserted the scheme inside `if "url" in man:` - so the one
        failure that matters, the key being absent, was the one case the
        assertion could not run in. It was absent on nineteen of the
        last forty commits that touched the file, because
        `build_library.py` rewrote the manifest on every bare build and
        only restored the url when publishing. Every client that polled
        during those windows got "the update server sent an incomplete
        reply" and stopped updating.
        """
        man = json.loads(
            (pathlib.Path(_library.BUNDLED).parent / "manifest.json")
            .read_text(encoding="utf-8"))
        self.assertIn(
            "url", man,
            "data/manifest.json has no url; this is the live channel "
            "pointer and every installed client silently stops updating "
            "until the next publish puts it back")
        self.assertTrue(
            str(man["url"]).startswith("https://"),
            f"manifest url is {man['url']!r}; content must travel "
            f"over HTTPS or the checksum is the only integrity check")

    def test_updater_ignores_a_manifest_without_a_url(self):
        src = (ROOT / "pearls" / "_updater.py").read_text(encoding="utf-8")
        self.assertIn('manifest.get("url")', src)
        self.assertIn("if not url or not want", src,
                      "the updater must bail when the manifest names no "
                      "download location, rather than guessing one")

    def test_publish_script_is_executable_and_parses(self):
        script = ROOT / "tools" / "publish_content.sh"
        self.assertTrue(script.exists(), "tools/publish_content.sh missing")
        import subprocess
        r = subprocess.run(["bash", "-n", str(script)],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_publish_script_runs_the_tests_before_pushing(self):
        """Content bypasses AnkiWeb review entirely.

        The suite is the only thing standing between a bad edit and
        every user who has updates enabled, so the publish path has to
        run it and has to stop on failure.
        """
        src = (ROOT / "tools" / "publish_content.sh").read_text(encoding="utf-8")
        self.assertIn("tests/test_*.py", src)
        self.assertIn("refusing to publish", src)
        self.assertLess(
            src.index("refusing to publish"), src.index("gh release create"),
            "the test gate must come before anything is pushed")


class ConfigParity(unittest.TestCase):
    """config.json, `_DEFAULTS` and config.md must agree.

    A key present in one and missing from another is the classic way an
    option ends up silently unreadable: `_config.get` falls through to a
    default that is not there and returns None, which for a boolean flag
    reads as "off" no matter what the user set.
    """

    def _defaults(self):
        import ast
        tree = ast.parse((ROOT / "_config.py").read_text(encoding="utf-8"))
        for node in tree.body:
            if (isinstance(node, ast.Assign)
                    and getattr(node.targets[0], "id", None) == "_DEFAULTS"):
                return ast.literal_eval(node.value)
        self.fail("_DEFAULTS not found in _config.py")

    def test_new_keys_exist_everywhere(self):
        shipped = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
        defaults = self._defaults()
        docs = (ROOT / "config.md").read_text(encoding="utf-8")
        for key in ("libraryAutoUpdate", "libraryManifestUrl",
                    "libraryAutoUpdateMigrated"):
            self.assertIn(key, shipped, f"{key} missing from config.json")
            self.assertIn(key, defaults, f"{key} missing from _DEFAULTS")
            self.assertIn(key, docs, f"{key} is undocumented in config.md")

    def test_content_updates_default_on_consistently(self):
        """config.json and `_DEFAULTS` must agree on the default.

        They are read in different situations - config.json when Anki
        loads the add-on, `_DEFAULTS` when a key is missing from a
        user's stored config - so a disagreement means the behaviour
        depends on which path the user came through.
        """
        shipped = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
        self.assertIs(shipped["libraryAutoUpdate"], True)
        self.assertIs(self._defaults()["libraryAutoUpdate"], True)

    def test_the_migration_flag_ships_false(self):
        """It must start false or the one-time flip never runs.

        `_migrate_library_auto_update` returns early when the flag is
        true, so shipping it true would leave every 2.0.0 install with
        the false frozen in meta.json and updates silently off - the
        exact state 2.0.1 exists to fix.
        """
        shipped = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
        self.assertIs(shipped["libraryAutoUpdateMigrated"], False)
        self.assertIs(self._defaults()["libraryAutoUpdateMigrated"], False)

    def test_settings_exposes_the_switch(self):
        """A config key with no user interface is not a setting.

        2.0.0 had the key and no checkbox, so the feature shipped
        effectively disabled for everyone.
        """
        src = (ROOT / "__init__.py").read_text(encoding="utf-8")
        self.assertIn("_build_library_group", src)
        self.assertIn('_config.set_value("libraryAutoUpdate"', src,
                      "the checkbox must be written back on close")

    def test_check_now_does_not_run_on_the_ui_thread(self):
        src = (ROOT / "__init__.py").read_text(encoding="utf-8")
        self.assertIn("run_in_background", src,
                      "Check now downloads up to 2 MB; on the UI thread "
                      "that freezes Anki for the duration")

    def test_the_2_0_upgrade_popup_is_gone(self):
        src = (ROOT / "__init__.py").read_text(encoding="utf-8")
        self.assertNotIn("_show_2_0_notice", src)


class DrugSummariesAreNotBakedIn(unittest.TestCase):
    """The drug override seam is new at 2.2 and inherits the same trap.

    `_drugs` now applies `drug_summaries` by assigning to
    `entry["summary"]`, exactly as `_conditions` does. The failure is
    silent in the worst way: the override still renders, so the popup
    looks right, and the only symptom is that deleting or editing the
    override in `content/_rich.py` stops having any effect.
    """

    def test_base_drug_text_differs_from_the_override(self):
        lib = json.loads(
            pathlib.Path(_library.BUNDLED).read_text(encoding="utf-8"))
        overrides = lib.get("drug_summaries") or {}
        self.assertTrue(overrides, "expected drug overrides in the library")
        base = {d["generic"].lower(): d["summary"] for d in lib["drugs"]}
        identical = [g for g, t in overrides.items()
                     if base.get(g.lower()) == t]
        self.assertEqual(
            identical, [],
            f"{len(identical)} drug override(s) have been baked into the "
            f"base text on disk; the override is now uneditable")

    def test_every_override_names_a_real_generic(self):
        """An override on a name that does not exist never renders, and
        nothing says so. A rename is the likely cause.

        `new_drugs` counts here. It is kept out of `drugs` on purpose
        (see pearls/_drugs.py), and a version of this test that forgot
        that would reject every new entry's own summary - which is
        exactly what it did the first time insulin was added.
        """
        lib = json.loads(
            pathlib.Path(_library.BUNDLED).read_text(encoding="utf-8"))
        generics = {d["generic"].lower() for d in lib["drugs"]}
        generics |= {d["generic"].lower() for d in (lib.get("new_drugs") or [])}
        orphaned = [g for g in (lib.get("drug_summaries") or {})
                    if g.lower() not in generics]
        self.assertEqual(orphaned, [])

    def test_content_channel_hosts_are_pinned(self):
        """The manifest's hash validates its own payload, so it says
        nothing about provenance: both come from wherever the URL points.
        `libraryManifestUrl` is config, and repointing it swaps the
        clinical content of every popup, durably, because the downloaded
        copy is preferred on load."""
        from pearls import _updater
        for evil in ("https://evil.example/manifest.json",
                     "https://raw.githubusercontent.com.evil.example/x",
                     "https://notgithub.com/x"):
            with self.assertRaises(ValueError, msg=f"{evil} was accepted"):
                _updater._require_https(evil, "manifest")
        for good in (_updater.DEFAULT_MANIFEST_URL,
                     "https://objects.githubusercontent.com/x",
                     "https://github.com/mord58562/theankidote/releases/x"):
            self.assertEqual(_updater._require_https(good, "manifest"), good)

    # Names pyflakes cannot see because `_rebind_theme` writes them into
    # the module's `globals()` when the palette is built, so they exist
    # at runtime and not in the source. Listed rather than suppressed
    # wholesale, so a genuine undefined name in that file still fails.
    THEME_GLOBALS = {
        # Written into `_panel_pearls` by its `_rebind_theme`.
        "_NAV_BTN_QSS", "_CLOSE_BTN_QSS", "_RESULT_BG", "_ITEM_TXT",
        "_RESULT_BDR", "_RESULT_HOVER_BG", "_RESULT_HOVER_TXT",
        "_RESULT_SEL_BG", "_RESULT_SEL_TXT",
        # Written into `_theme` itself by `refresh()`, which rebinds the
        # palette in place so callers that captured a name at import
        # time still read the current value.
        "HEADER_TXT", "BODY_TXT", "MUTED", "TEAL", "TEAL_DIM",
        "TEAL_BORDER", "NAVY", "NAVY_LIGHT", "BG_BOX", "QUOTE_TXT",
    }

    def test_every_shipped_file_parses(self):
        """`compile()` over the package, with no dependencies.

        The undefined-name guard below is the only static check on the
        Qt surface, and it skips itself when pyflakes is absent -
        silently, since `publish_content.sh` discards test output, so a
        skip and a pass look identical at the publish gate. It also read
        only pyflakes' `out` stream, and a file that fails to PARSE is
        reported on `err`. So a syntax error in `_panel_pearls.py`,
        `chat/` or `uptodate/` - none of which can be imported under
        test - would ship with the whole suite green.

        This needs nothing installed and cannot be skipped.
        """
        for path in sorted(ROOT.rglob("*.py")):
            rel = path.relative_to(ROOT)
            if rel.parts[0] in ("tests", ".git"):
                continue
            src = path.read_text(encoding="utf-8")
            try:
                compile(src, str(rel), "exec")
            except SyntaxError as exc:
                self.fail(f"{rel} does not parse: line {exc.lineno}: "
                          f"{exc.msg}")

    def test_no_undefined_names(self):
        """A name that only exists in the author's head is a NameError
        at runtime, and most of this tree cannot be imported under test
        because it needs Anki - so nothing else catches it.

        Written after moving a helper between modules and leaving its
        `_log` reference behind: the suite passed, the package imported
        nowhere, and the failure would have arrived the first time a
        keyboard shortcut failed to bind.
        """
        try:
            from pyflakes.api import check
            from pyflakes.reporter import Reporter
        except ImportError:
            self.skipTest("pyflakes not installed")
        import io
        out, err = io.StringIO(), io.StringIO()
        reporter = Reporter(out, err)
        # Only these two files write names into `globals()`, so the
        # allowlist applies only to them. It used to be matched against
        # every line from every file, which exempted a bare `TEAL` or
        # `NAVY` typo anywhere in the package.
        allowlisted_files = ("_theme.py", "_panel_pearls.py")
        for path in sorted(ROOT.rglob("*.py")):
            rel = path.relative_to(ROOT)
            if rel.parts[0] in ("tests", "content", ".git"):
                continue
            check(path.read_text(encoding="utf-8"), str(rel), reporter)
        offenders = []
        for line in out.getvalue().splitlines():
            if "undefined name" not in line:
                continue
            in_allowlisted_file = any(line.startswith(f)
                                      or f"/{f}:" in line.split(":")[0] + ":"
                                      or line.split(":")[0].endswith(f)
                                      for f in allowlisted_files)
            if in_allowlisted_file and any(f"'{n}'" in line
                                           for n in self.THEME_GLOBALS):
                continue
            offenders.append(line)
        self.assertEqual(
            err.getvalue().strip(), "",
            "pyflakes could not analyse a file - a syntax error is "
            "reported on its error stream, which this test used to "
            "ignore entirely:\n" + err.getvalue())
        self.assertEqual(
            offenders, [],
            "these names do not exist where they are used:\n"
            + "\n".join(offenders))

    # Keys the add-on manages for itself. They are real config values and
    # they are written to the user's config blob, but they are remembered
    # state rather than something anyone sets, so they stay out of the
    # `config.json` template that Anki shows in its config editor. They
    # are documented under "Internal / managed flags" instead.
    RUNTIME_STATE_KEYS = {
        "sidebarArticlesCollapsed", "sidebarLastArticleUrl",
    }

    def test_config_template_and_docs_track_the_defaults(self):
        """Three ways for these to drift, all silent.

        A key in `_DEFAULTS` and not in `config.json` is a setting the
        user cannot find. A key in `config.json` and not in `_DEFAULTS`
        is one nothing reads - `autoSearch` sat there for three releases
        after its reader was deleted. A key in neither document is one
        that appears in the user's config blob with no explanation.
        """
        import re
        cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
        src = (ROOT / "_config.py").read_text(encoding="utf-8")
        m = re.search(r"_DEFAULTS\s*=\s*\{(.*?)\n\}", src, re.S)
        self.assertIsNotNone(m, "_config.py declares no _DEFAULTS")
        defaults = set(re.findall(r'^\s*"([^"]+)"\s*:', m.group(1), re.M))

        missing = sorted(defaults - set(cfg) - self.RUNTIME_STATE_KEYS)
        self.assertEqual(
            missing, [],
            f"these are settings the user cannot see or edit, because "
            f"they are in _DEFAULTS but not in config.json: {missing}")

        orphaned = sorted(set(cfg) - defaults)
        self.assertEqual(
            orphaned, [],
            f"config.json ships these and nothing reads them: {orphaned}")

        doc = (ROOT / "config.md").read_text(encoding="utf-8")
        documented = set(re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`", doc))
        undocumented = sorted(defaults - documented)
        self.assertEqual(
            undocumented, [],
            f"these reach the user's config blob with nothing in "
            f"config.md explaining them: {undocumented}")

    def test_schema_constant_agrees_with_the_compiler(self):
        """`SCHEMA` is declared twice and nothing checked they matched.

        `pearls/_library.SCHEMA` is what a client will accept;
        `tools/build_library.SCHEMA` is what the compiler stamps. If the
        compiler's is higher, every existing install refuses the next
        publish and falls back to its bundled copy. If it is lower, a
        client that has moved on refuses it too. Either way the content
        channel stops, and the only symptom is that nothing arrives.
        """
        src = (ROOT / "tools" / "build_library.py").read_text(encoding="utf-8")
        m = re.search(r"^SCHEMA = (\d+)$", src, re.M)
        self.assertIsNotNone(m, "tools/build_library.py declares no SCHEMA")
        self.assertEqual(
            int(m.group(1)), _library.SCHEMA,
            f"build_library stamps schema {m.group(1)} but "
            f"pearls/_library accepts only {_library.SCHEMA}")

    def test_the_newer_library_copy_wins(self):
        """The downloaded copy used to win regardless of its version, so
        an add-on release carrying newer bundled content was masked by
        an older download until the channel next published."""
        older = {"content_version": "07.09.2026.1"}
        newer = {"content_version": "08.09.2026.1"}
        self.assertTrue(_library._version_newer(
            newer["content_version"], older["content_version"]))
        self.assertFalse(_library._version_newer(
            older["content_version"], newer["content_version"]))
        # Across a month rollover, which a string compare gets wrong.
        self.assertTrue(_library._version_newer("01.10.2026", "30.09.2026"))
        self.assertFalse(_library._version_newer("30.09.2026", "01.10.2026"))

    def test_content_version_is_required(self):
        """Without it `CONTENT_VERSION` is "unknown", which no remote
        version sorts above, so updates stop permanently and silently."""
        self.assertIn("content_version", _library._REQUIRED)
        lib = _valid()
        lib.pop("content_version", None)
        self.assertNotEqual(
            _library._validate(lib), "",
            "a library with no content_version was accepted; it would "
            "load and then never update again")

    def test_condition_aliases_reached_the_built_library(self):
        """The alias table is authoring source; the shipped library is
        the build artefact. An edit to `CONDITION_ALIASES` without a
        rebuild is a silent no-op - the add-on reads only the JSON - and
        this is the test that says so.

        Checked against the library on disk rather than against
        `_conditions.resolve`, because that module merges at import and
        would answer from the same authored dict it is meant to verify.
        """
        import _rich                                    # content/_rich.py
        lib = json.loads(
            pathlib.Path(_library.BUNDLED).read_text(encoding="utf-8"))
        shipped = {}
        for entry in lib["conditions"] + (lib.get("new_conditions") or []):
            for key in [entry["name"]] + list(entry.get("aliases") or []):
                shipped.setdefault(key.lower(), entry["name"])
        missing = []
        for name, aliases in _rich.CONDITION_ALIASES.items():
            for alias in aliases:
                if shipped.get(alias.lower(), "").lower() != name.lower():
                    missing.append(f"{alias!r} -> {name!r} "
                                   f"(library says {shipped.get(alias.lower())!r})")
        self.assertEqual(
            missing, [],
            f"{len(missing)} condition alias(es) are in content/_rich.py "
            f"but not in data/library.json; run tools/build_library.py "
            f"and commit the artefact: {missing[:5]}")

    def test_condition_aliases_target_a_real_condition(self):
        """Same failure as an orphaned drug override: the alias never
        matches and nothing reports it."""
        import _rich                                    # content/_rich.py
        lib = json.loads(
            pathlib.Path(_library.BUNDLED).read_text(encoding="utf-8"))
        names = {c["name"].lower() for c in lib["conditions"]}
        names |= {c["name"].lower()
                  for c in (lib.get("new_conditions") or [])}
        orphaned = [n for n in _rich.CONDITION_ALIASES
                    if n.lower() not in names]
        self.assertEqual(orphaned, [])

    def test_new_drugs_do_not_shadow_an_existing_entry(self):
        """Two entries under one generic means whichever indexes first
        wins, silently and non-deterministically."""
        lib = json.loads(
            pathlib.Path(_library.BUNDLED).read_text(encoding="utf-8"))
        base = {d["generic"].lower() for d in lib["drugs"]}
        clash = [d["generic"] for d in (lib.get("new_drugs") or [])
                 if d["generic"].lower() in base]
        self.assertEqual(clash, [])

    def test_new_drugs_are_not_appended_to_the_base_list(self):
        """If they were, the next build would read them back as base and
        the NEW_DRUGS table would stop being authoritative."""
        lib = json.loads(
            pathlib.Path(_library.BUNDLED).read_text(encoding="utf-8"))
        self.assertTrue(lib.get("new_drugs"), "expected new drug entries")
        base = {d["generic"].lower() for d in lib["drugs"]}
        for d in lib["new_drugs"]:
            self.assertNotIn(d["generic"].lower(), base)

    def test_an_absent_new_drugs_key_is_still_a_valid_library(self):
        lib = json.loads(
            pathlib.Path(_library.BUNDLED).read_text(encoding="utf-8"))
        lib.pop("new_drugs", None)
        self.assertEqual(_library._validate(lib), "")

    def test_a_poisoned_new_drugs_key_is_rejected(self):
        """These entries go straight into the matcher, so a bad shape is
        a broken popup on every card rather than a one-off."""
        lib = json.loads(
            pathlib.Path(_library.BUNDLED).read_text(encoding="utf-8"))
        for bad in ({}, ["x"], [{"generic": "z"}], [{"summary": "z"}],
                    [{"generic": "z", "summary": "  "}],
                    [{"generic": "z", "summary": "t", "aliases": "s"}],
                    [{"generic": "z", "summary": "t", "aliases": [7]}]):
            copy = dict(lib)
            copy["new_drugs"] = bad
            self.assertTrue(_library._validate(copy),
                            f"{bad!r} passed validation")

    def test_importing_drugs_does_not_mutate_the_library(self):
        lib = json.loads(
            pathlib.Path(_library.BUNDLED).read_text(encoding="utf-8"))
        base = {d["generic"]: d["summary"] for d in lib["drugs"]}
        loaded = {d["generic"]: d["summary"]
                  for d in _library.get("drugs")}
        drifted = [g for g in base if base[g] != loaded.get(g)]
        self.assertEqual(
            drifted[:5], [],
            "importing pearls._drugs rewrote the loaded library in place")

    def test_an_absent_drug_summaries_key_is_still_a_valid_library(self):
        """Libraries published before 2.2 do not carry the key, and a
        published library is preferred over the bundled one."""
        lib = json.loads(
            pathlib.Path(_library.BUNDLED).read_text(encoding="utf-8"))
        lib.pop("drug_summaries", None)
        self.assertEqual(_library._validate(lib), "")

    def test_a_poisoned_drug_summaries_key_is_rejected(self):
        lib = json.loads(
            pathlib.Path(_library.BUNDLED).read_text(encoding="utf-8"))
        for bad in ([], {"clozapine": 7}, {"clozapine": None},
                    {"clozapine": "   "}, {7: "text"}):
            copy = dict(lib)
            copy["drug_summaries"] = bad
            self.assertTrue(_library._validate(copy),
                            f"{bad!r} passed validation")


if __name__ == "__main__":
    unittest.main(verbosity=2)
