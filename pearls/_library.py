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


# Identity field per vocabulary list, and the fields every entry of that
# list must carry as strings. Anything not named here is optional and
# unconstrained, so content can add fields without a code release; what
# is named here is what the consumers dereference without checking.
_ENTRY_REQUIRED = {
    "conditions":     ("name", "summary"),
    "new_conditions": ("name", "summary"),
    "drugs":          ("generic", "summary"),
    "signs":          ("name", "summary"),
    "descriptive":    ("name", "summary"),
    "preclinical":    ("name", "summary"),
    "psych":          ("name", "summary"),
}

# Optional fields whose type is still load-bearing: `_conditions` iterates
# `aliases` and `utd`, `_drugs` iterates `brands`. A string where a list
# belongs iterates character by character rather than raising, which is
# the worst outcome - thousands of one-character phrases enter the
# matcher and every card lights up.
_ENTRY_STR_LISTS = ("aliases", "brands")

# `utd` is not a list of strings. Each element is a [label, query] pair,
# and `_conditions._primary_url` reaches straight into it as
# `utd[0][1]`. Measured against the shipped validator: `[{"a": 1}]`,
# `["x"]`, `[[1, 2]]` and `[["only"]]` all returned "" from `_validate`
# and every one of them crashed `resolve()` - which runs on every card
# shown, so that is a broken popup on every card until the file is
# deleted by hand, not a one-off import failure.
_ENTRY_PAIR_LISTS = ("utd",)

_ENTRY_STRS = ("nbk", "source", "category")

# How many entries deep to check. The library is ~2,500 entries and this
# runs at every launch and on every download, so the whole file is
# checked rather than a sample: a poisoned entry at index 900 is exactly
# what a sampling validator would wave through, and the cost measured on
# the shipped library is under 10 ms.
_MAX_URL_SCHEMES = ("http://", "https://")


def _validate_entries(lib) -> str:
    """Check every entry of every vocabulary, not just the first one.

    The previous version spot-checked `conditions[0]` and accepted
    everything after it. That was demonstrably not enough: a library in
    which `conditions[7]` is a bare string passes, is written to
    `user_files/`, is preferred over the bundled copy at every launch,
    and then raises `ValueError` inside `_conditions.py` at import -
    which kills the add-on permanently, because the Settings dialog that
    could turn updates off lives in the add-on that no longer imports.
    Recovery required deleting a file by hand.

    So the gate is the whole file. Fall-back-never-fail only works if
    the check is strict enough that anything reaching the consumers is
    known-good.
    """
    for key, required in _ENTRY_REQUIRED.items():
        for i, entry in enumerate(lib[key]):
            if not isinstance(entry, dict):
                return f"{key}[{i}] is {type(entry).__name__}, expected object"
            for field in required:
                val = entry.get(field)
                if not isinstance(val, str):
                    return (f"{key}[{i}].{field} is "
                            f"{type(val).__name__}, expected string")
                if not val.strip():
                    return f"{key}[{i}].{field} is empty"
            for field in _ENTRY_PAIR_LISTS:
                if field in entry:
                    pairs = entry[field]
                    if not isinstance(pairs, list):
                        return (f"{key}[{i}].{field} is "
                                f"{type(pairs).__name__}, expected list")
                    for j, pair in enumerate(pairs):
                        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                            return (f"{key}[{i}].{field}[{j}] is not a "
                                    f"2-element [label, query] pair")
                        if not all(isinstance(x, str) for x in pair):
                            return (f"{key}[{i}].{field}[{j}] holds a "
                                    f"non-string")

            for field in _ENTRY_STR_LISTS:
                if field in entry:
                    if not isinstance(entry[field], list):
                        return (f"{key}[{i}].{field} is "
                                f"{type(entry[field]).__name__}, expected list")
                    # The type of the list is not the whole check. Every
                    # consumer lowercases these elements to build its
                    # lookup - `_conditions` does `[n] + list(aliases)`,
                    # `_drugs` the same for `brands` - and an `int` or a
                    # `None` among them raises `AttributeError` at
                    # import. That is the identical brick described
                    # above, one level deeper: the file validates, is
                    # written to `user_files/`, is preferred at every
                    # launch, and the add-on holding the switch that
                    # would disable updates is the one that no longer
                    # imports.
                    #
                    # Measured against the shipped library rather than
                    # assumed: of six poisoned shapes that passed the
                    # type-only check, four killed the import outright
                    # and `_drugs.py` survived only because it happens
                    # to carry an `isinstance` guard the other six
                    # consumers do not. Guarding here fixes all seven.
                    for j, item in enumerate(entry[field]):
                        if not isinstance(item, str):
                            return (f"{key}[{i}].{field}[{j}] is "
                                    f"{type(item).__name__}, expected string")
            for field in _ENTRY_STRS:
                if field in entry and not isinstance(entry[field], str):
                    return (f"{key}[{i}].{field} is "
                            f"{type(entry[field]).__name__}, expected string")
            # A url is navigated to in the authenticated panel profile, so
            # a downloaded entry naming `javascript:` or `file:` must not
            # reach the DOM at all. `_is_safe_url` in `__init__.py` is the
            # second gate; this is the first, and it is the one that stops
            # the value being stored rather than merely acted on.
            url = entry.get("url")
            if url is not None:
                if not isinstance(url, str):
                    return f"{key}[{i}].url is {type(url).__name__}"
                if not url.lower().startswith(_MAX_URL_SCHEMES):
                    return f"{key}[{i}].url is not http(s)"

    # `_acronyms.py` does `[tuple(c) for c in v]` and then unpacks each
    # as `(exp, ctx, desc)`, lowercasing every element of `ctx`. So the
    # shape is load-bearing three levels down, and checking only that
    # `v` is a non-empty list leaves `[[1, 2, 3]]` and `[["a"]]` both
    # passing and both fatal at import.
    for k, v in lib["acronyms"].items():
        if not isinstance(k, str) or not isinstance(v, list) or not v:
            return f"acronyms[{k!r}] is not a non-empty list"
        for j, cand in enumerate(v):
            if not isinstance(cand, (list, tuple)) or len(cand) != 3:
                return (f"acronyms[{k!r}][{j}] is not a 3-element "
                        f"expansion/context/description")
            exp, ctx, desc = cand
            if not isinstance(exp, str) or not isinstance(desc, str):
                return f"acronyms[{k!r}][{j}] expansion/description is not a string"
            if not isinstance(ctx, (list, tuple)):
                return (f"acronyms[{k!r}][{j}] context is "
                        f"{type(ctx).__name__}, expected list")
            for w in ctx:
                if not isinstance(w, str):
                    return (f"acronyms[{k!r}][{j}] context holds a "
                            f"{type(w).__name__}, expected strings")
    for k, v in lib["drugbank_ids"].items():
        if not isinstance(k, str) or not isinstance(v, str):
            return f"drugbank_ids[{k!r}] is not a string"
    for k, v in lib["rich_summaries"].items():
        if not isinstance(k, str) or not isinstance(v, str):
            return f"rich_summaries[{k!r}] is not a string"

    # `drug_summaries` is optional, because it did not exist before 2.2
    # and a library published before then is still a valid library. It
    # is NOT in `_REQUIRED` for that reason - but when it is present it
    # is dereferenced without checking, exactly like `rich_summaries`,
    # so it gets the same treatment. Leaving an optional key
    # unvalidated is how a poisoned download reaches `.strip()` on an
    # int and bricks the add-on at import, which is the failure the
    # whole validator exists to stop.
    # `new_drugs` is optional for the same reason as `drug_summaries`,
    # and load-bearing for a stronger one: its entries go straight into
    # the matcher, so a bad shape here is a broken popup on every card
    # rather than a one-off. Validated as a drugs list would be.
    nd = lib.get("new_drugs")
    if nd is not None:
        if not isinstance(nd, list):
            return f"key 'new_drugs' is {type(nd).__name__}, expected list"
        for i, entry in enumerate(nd):
            if not isinstance(entry, dict):
                return (f"new_drugs[{i}] is {type(entry).__name__}, "
                        f"expected object")
            for field in ("generic", "summary"):
                val = entry.get(field)
                if not isinstance(val, str) or not val.strip():
                    return f"new_drugs[{i}].{field} is not a non-empty string"
            for field in _ENTRY_STR_LISTS:
                if field in entry:
                    vals = entry[field]
                    if not isinstance(vals, list):
                        return (f"new_drugs[{i}].{field} is "
                                f"{type(vals).__name__}, expected list")
                    for v in vals:
                        if not isinstance(v, str):
                            return (f"new_drugs[{i}].{field} holds a "
                                    f"{type(v).__name__}, expected strings")

    # Same contract as new_drugs, and load-bearing for the same reason:
    # these go straight into the matcher.
    npc = lib.get("new_preclinical")
    if npc is not None:
        if not isinstance(npc, list):
            return (f"key 'new_preclinical' is {type(npc).__name__}, "
                    f"expected list")
        for i, entry in enumerate(npc):
            if not isinstance(entry, dict):
                return (f"new_preclinical[{i}] is {type(entry).__name__}, "
                        f"expected object")
            for field in ("name", "summary"):
                val = entry.get(field)
                if not isinstance(val, str) or not val.strip():
                    return (f"new_preclinical[{i}].{field} is not a "
                            f"non-empty string")
            if "aliases" in entry:
                vals = entry["aliases"]
                if not isinstance(vals, list):
                    return (f"new_preclinical[{i}].aliases is "
                            f"{type(vals).__name__}, expected list")
                for v in vals:
                    if not isinstance(v, str):
                        return (f"new_preclinical[{i}].aliases holds a "
                                f"{type(v).__name__}, expected strings")

    ds = lib.get("drug_summaries")
    if ds is not None:
        if not isinstance(ds, dict):
            return (f"key 'drug_summaries' is {type(ds).__name__}, "
                    f"expected object")
        for k, v in ds.items():
            if not isinstance(k, str) or not isinstance(v, str):
                return f"drug_summaries[{k!r}] is not a string"
            if not v.strip():
                return f"drug_summaries[{k!r}] is empty"
    return ""


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
    return _validate_entries(lib)


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _quarantine(path: str, why: str) -> None:
    """Move a rejected downloaded copy aside instead of leaving it in place.

    Falling back covers the current launch, but the bad file stays the
    preferred copy and is re-read, re-parsed and re-rejected on every
    launch after it. Renaming it means the failure happens once, the
    evidence is kept for a bug report, and the next successful check can
    write a clean file without contending with it.

    Only ever applied to the downloaded copy. A bundled copy that fails
    means the install itself is damaged, and renaming it would turn a
    reinstallable problem into an unrecoverable one.
    """
    try:
        dest = path + ".rejected"
        os.replace(path, dest)
        log(f"library: quarantined bad downloaded copy to {dest} ({why})")
    except Exception as exc:                           # noqa: BLE001
        log(f"library: could not quarantine {path} ({exc})")


def _load():
    for path, label in ((USER_COPY, "downloaded"), (BUNDLED, "bundled")):
        if not os.path.exists(path):
            continue
        try:
            lib = _read(path)
        except Exception as exc:                       # noqa: BLE001
            log(f"library: {label} copy unreadable ({exc}); falling back")
            if label == "downloaded":
                _quarantine(path, f"unreadable: {exc}")
            continue
        why = _validate(lib)
        if why:
            log(f"library: {label} copy rejected - {why}; falling back")
            if label == "downloaded":
                _quarantine(path, why)
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


_MISSING = object()


def get(key, default=_MISSING):
    """Fetch a vocabulary by name.

    With no `default`, this raises on an absent key - which is right for
    everything in `_REQUIRED`, because `_validate` has already
    guaranteed those exist with the right type and callers should not
    carry their own defensive default for something that cannot be
    missing.

    `default` exists for keys added after schema 1 was frozen. A client
    can be handed a library published before the key existed, and the
    published library is preferred over the bundled one, so "the key is
    absent" is a normal state rather than corruption. Passing a default
    is the caller saying so explicitly; it is not a licence to skip
    validation, which still runs on the key when it is present.
    """
    if default is _MISSING:
        return LIBRARY[key]
    return LIBRARY.get(key, default)
