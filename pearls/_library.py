# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""Loads the term library, preferring a downloaded copy over the bundled one.

The add-on ships `data/library.json` and that copy is the floor: it is
always present, always valid, and a fresh install works offline forever
without ever touching the network. `_updater.py` may write a newer copy
into `user_files/`, which survives add-on upgrades, and this module
prefers it when it is loadable.

Three rules govern what "loadable" means, and they are the whole point
of this file:

  * **JSON only.** Nothing downloaded is ever executed. No `pickle`, no
    `exec`, no import of downloaded modules. `pickle.loads` on a file
    fetched over the network is arbitrary code execution, and an add-on
    that does it would be a remote shell for anyone who can spoof the
    host. The library is data, so it travels as data.
  * **Schema before content.** A library published for schema 2 is
    refused by code that understands schema 1 rather than half-loaded.
    Otherwise the first structural change to the format breaks every
    installation that has not upgraded, simultaneously, with no way to
    roll back.
  * **Fall back, never fail.** Any problem - missing file, bad JSON,
    wrong schema, missing key, wrong type - drops silently to the
    bundled copy and logs. A corrupted download must degrade the add-on
    to last month's content, not stop Anki from starting.
"""
import json
import os


def log(msg):
    """Deferred, defensive shim around `.._log.log`.

    This module is imported by `pearls.*` at package-import time, and the
    test suite imports `pearls` directly rather than as a subpackage of
    the add-on, so a top-level `from .._log import log` reaches outside
    the package and raises. Logging is not worth an ImportError, and the
    add-on must load whether or not Anki is around it.
    """
    try:
        from .._log import log as _log
        _log(msg)
    except Exception:                                   # noqa: BLE001
        pass

SCHEMA = 1

_REQUIRED = {
    "conditions": list,
    "new_conditions": list,
    "rich_summaries": dict,
    "drugs": list,
    "drugbank_ids": dict,
    "acronyms": dict,
    "signs": list,
    "descriptive": list,
    "preclinical": list,
    "psych": list,
}

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLED = os.path.join(_HERE, "data", "library.json")
USER_COPY = os.path.join(_HERE, "user_files", "library.json")


def _validate(lib) -> str:
    """Return "" if `lib` is a usable library, else why it is not."""
    if not isinstance(lib, dict):
        return "not a JSON object"
    schema = lib.get("schema")
    if schema != SCHEMA:
        return (f"schema {schema!r}, this build understands {SCHEMA} "
                f"(update the add-on)")
    for key, want in _REQUIRED.items():
        got = lib.get(key)
        if not isinstance(got, want):
            return f"key {key!r} is {type(got).__name__}, expected {want.__name__}"
        if not got:
            return f"key {key!r} is empty"
    # Spot-check the shape one level down. A file that is structurally
    # JSON but semantically junk should be caught here, not by an
    # AttributeError in the middle of building the matcher.
    first = lib["conditions"][0]
    if not isinstance(first, dict) or "name" not in first or "summary" not in first:
        return "conditions entries lack 'name'/'summary'"
    return ""


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _load():
    for path, label in ((USER_COPY, "downloaded"), (BUNDLED, "bundled")):
        if not os.path.exists(path):
            continue
        try:
            lib = _read(path)
        except Exception as exc:                       # noqa: BLE001
            log(f"library: {label} copy unreadable ({exc}); falling back")
            continue
        why = _validate(lib)
        if why:
            log(f"library: {label} copy rejected - {why}; falling back")
            continue
        if label == "downloaded":
            log(f"library: using downloaded content "
                f"{lib.get('content_version')}")
        return lib
    raise RuntimeError(
        "no usable term library: neither data/library.json nor "
        "user_files/library.json loaded. The add-on install is damaged; "
        "reinstall from AnkiWeb.")


LIBRARY = _load()
CONTENT_VERSION = LIBRARY.get("content_version", "unknown")


def get(key):
    """Fetch a vocabulary by name. Present because `_validate` has already
    guaranteed the key exists and has the right type, so callers do not
    need their own defensive default."""
    return LIBRARY[key]
