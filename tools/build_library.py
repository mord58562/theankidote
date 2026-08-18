#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""Compile the authored content modules into `data/library.json`.

Content used to live as Python literals inside the modules that consume
it - 862 KB of `_conditions.py`, 931 KB of `_drugs.py`. That works, but
it welds content to code: correcting one summary means shipping a new
add-on version through AnkiWeb and waiting for every user to update.
Splitting the data out means content can ship on its own cadence.

The literals stay as the *authoring* format, because they carry comments
and a diffable shape that a 900 KB JSON blob does not. This script is
the compiler between the two, and the shipped add-on reads only the
JSON. Two consequences worth knowing:

  * `data/library.json` is a build artefact. Edit the modules, run this,
    commit both.
  * `content_version` is what the updater compares, so it has to change
    whenever the content does. It defaults to today's date; pass
    --version to set it explicitly.

Run from the add-on root:

    python3 tools/build_library.py

Measured on the preview-14 content: 856 KB of JSON, 305 KB gzipped,
parsed by `json.loads` in about 4 ms against 66 ms to import the
equivalent Python module. The split makes startup faster, not slower.
"""
import argparse
import datetime
import gzip
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
# `pearls` is imported directly rather than as `theankidote.pearls`,
# because this runs from a checkout where the add-on directory is not
# necessarily named `theankidote`.
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "content"))

# The schema the *code* in this tree understands. A library published
# with a higher number must be refused by older add-ons rather than
# half-loaded, so bump this whenever the shape below changes.
SCHEMA = 1


def collect() -> dict:
    import _rich                                        # content/_rich.py
    from pearls import (  # noqa: E402
        _acronyms, _conditions, _descriptive, _drugs, _preclinical,
        _psych, _signs,
    )

    # The base summaries must come from the library as it sits on disk,
    # NOT from `_conditions._LOOKUP`. Importing `_conditions` merges the
    # rich overrides into `_LOOKUP` in place, so reading it back would
    # write the current overrides into the base text permanently - and a
    # later edit to `content/_rich.py` would then be a no-op, because the
    # override it replaces is already the base. The split has to survive
    # every rebuild or it is not a split.
    from pearls import _library
    conditions = _library.get("conditions")

    return {
        "schema": SCHEMA,
        "conditions": conditions,
        "new_conditions": _rich.NEW_CONDITIONS,
        "rich_summaries": _rich.RICH_SUMMARIES,
        "drugs": _drugs._DRUGS,
        "drugbank_ids": _drugs._DRUGBANK_IDS,
        "acronyms": {k: [list(c) for c in v]
                     for k, v in _acronyms._ACRONYMS.items()},
        "signs": _signs.SIGN_TERMS,
        "descriptive": _descriptive.DESCRIPTIVE_TERMS,
        "preclinical": _preclinical.PRECLINICAL_TERMS,
        "psych": _psych.PSYCH_TERMS,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--version", default=None,
                    help="content version string (default: today's date)")
    ap.add_argument("--out", default=str(ROOT / "data" / "library.json"))
    ap.add_argument("--url", default=None,
                    help="where the built library will be downloadable. "
                         "Written into the manifest as the 'url' key; the "
                         "updater ignores a manifest without one, so the "
                         "publish script always passes it.")
    args = ap.parse_args()

    lib = collect()
    # Zero-padded dotted date, matching `date +%Y.%m.%d` in
    # tools/publish_content.sh. These two defaults must agree, and they
    # did not: this defaulted to `date.isoformat()`, which is hyphenated.
    #
    # Versions are compared as strings, and '.' (46) sorts above '-'
    # (45), so a hyphenated bundled version compares BELOW the dotted
    # version of the very same day. A build left on the default would
    # ship believing the already-published, older library was newer, and
    # every install would download 2 MB on first launch to replace its
    # own content with the previous release's. Nothing downstream would
    # report an error - the checksum matches, the schema matches, and
    # the summaries simply revert.
    #
    # Keep the padding for the same reason the publish script warns
    # about it: 2026.9.1 sorts above 2026.09.15.
    lib["content_version"] = (
        args.version or datetime.date.today().strftime("%Y.%m.%d"))

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(lib, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")
    out.write_bytes(blob)

    digest = hashlib.sha256(blob).hexdigest()
    manifest = {
        "schema": SCHEMA,
        "content_version": lib["content_version"],
        "sha256": digest,
        "bytes": len(blob),
    }
    # No url means no update: `_updater._check` bails rather than guess
    # where the library lives. The bundled manifest ships without one on
    # purpose, so a checkout that has never been published cannot point
    # clients at a file that is not there.
    if args.url:
        manifest["url"] = args.url
    (out.parent / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"{out.relative_to(ROOT)}  {len(blob) / 1024:.0f} KB"
          f"  ({len(gzip.compress(blob)) / 1024:.0f} KB gzipped)")
    for key in ("conditions", "drugs", "acronyms", "rich_summaries",
                "signs", "descriptive", "preclinical", "psych"):
        print(f"  {key:16} {len(lib[key])}")
    print(f"  content_version  {lib['content_version']}")
    print(f"  sha256           {digest[:16]}...")
    print(f"  url              {manifest.get('url', '(none - not publishable)')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
