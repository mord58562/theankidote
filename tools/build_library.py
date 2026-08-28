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

    # Merge the spelling-variant table into the drug entries. Done here
    # rather than in `_drugs.py` so the aliases travel in library.json
    # and reach existing installs over the content channel, instead of
    # waiting for an AnkiWeb release.
    #
    # `aliases` is an additive field: schema stays 1, and a 2.0.x client
    # that does not read it simply ignores it, so publishing this does
    # not strand anyone.
    #
    # An alias keyed on a generic that is not in the library is a typo,
    # and a silent one - the alias would simply never match and nothing
    # would say so. Fail the build instead.
    # Same rule as the conditions above, and for the same reason: as of
    # 2.2 `_drugs.py` merges `drug_summaries` over its entries at import,
    # so `_drugs._DRUGS` is the *overridden* text. Compiling from that
    # would write each override into the base permanently and make the
    # next edit to `content/_rich.py` a silent no-op. Read the library as
    # it sits on disk.
    drugs = [dict(d) for d in _library.get("drugs")]
    by_generic = {d.get("generic", "").lower(): d for d in drugs}
    drugbank_ids = dict(_drugs._DRUGBANK_IDS)

    # Fold each American duplicate into its Australian entry, keeping the
    # US spelling as an alias so those cards still resolve. Done before
    # the alias merge so DRUG_ALIASES can key on the surviving name.
    for us, au in _rich.DRUG_US_MERGES.items():
        us_e, au_e = by_generic.get(us.lower()), by_generic.get(au.lower())
        if not au_e:
            raise SystemExit(f"DRUG_US_MERGES target {au!r} is not in the library")
        if not us_e:
            continue
        merged = list(au_e.get("aliases") or [])
        if us not in merged:
            merged.append(us)
        for extra in us_e.get("aliases") or []:
            if extra not in merged:
                merged.append(extra)
        au_e["aliases"] = merged
        brands = list(au_e.get("brands") or [])
        for b in us_e.get("brands") or []:
            if b not in brands:
                brands.append(b)
        if brands:
            au_e["brands"] = brands
        drugs.remove(us_e)
        del by_generic[us.lower()]

    # Rename a generic to the name that should head the popup, keeping
    # the old spelling as an alias so cards written the old way still
    # resolve.
    for old, new in _rich.DRUG_RENAMES.items():
        # The accession carry-over sits OUTSIDE the "is this entry still
        # here" guard on purpose. A rename applied in an earlier build is
        # already baked into library.json, so the entry is no longer
        # found under its old name and the loop below skips it - which is
        # exactly how `nitroglycerin` kept DB00727 while every `glyceryl
        # trinitrate` popup opened a search page from 2.1.1 to 2.2. The
        # repair has to run on renames that already happened, not only on
        # the one being applied now.
        db_old = drugbank_ids.get(old.lower())
        if db_old and not drugbank_ids.get(new.lower()):
            drugbank_ids[new.lower()] = db_old
        e = by_generic.get(old.lower())
        if not e:
            continue
        e["generic"] = new
        # Dedupe, and drop any alias that is now the generic itself. The
        # 2.1.1 merge left `lignocaine` carrying `["lidocaine",
        # "lignocaine"]`, so renaming it without this produces an entry
        # aliased to its own heading twice.
        seen, merged = {new.lower()}, []
        for a in list(e.get("aliases") or []) + [old]:
            if isinstance(a, str) and a.lower() not in seen:
                seen.add(a.lower())
                merged.append(a)
        if merged:
            e["aliases"] = merged
        else:
            e.pop("aliases", None)
        # Carry the DrugBank accession across, or the rename silently
        # downgrades the popup button from the drug's monograph to a
        # search URL. Handled above, before the guard.
        by_generic[new.lower()] = e
        del by_generic[old.lower()]

    # An alias identical to its own generic is a leftover from a merge or
    # rename and does nothing but appear twice in the matcher's index.
    # Swept across the whole vocabulary rather than only the entries
    # touched this build, because the ones already in library.json were
    # written by earlier releases.
    for e in drugs:
        gen = (e.get("generic") or "").lower()
        kept, seen = [], {gen}
        for a in e.get("aliases") or []:
            if isinstance(a, str) and a.lower() not in seen:
                seen.add(a.lower())
                kept.append(a)
        if kept:
            e["aliases"] = kept
        else:
            e.pop("aliases", None)
    unknown = [g for g in _rich.DRUG_ALIASES if g.lower() not in by_generic]
    if unknown:
        raise SystemExit(
            f"DRUG_ALIASES names {len(unknown)} generic(s) not in the "
            f"library, so the aliases would never match: {unknown}")
    for generic, aliases in _rich.DRUG_ALIASES.items():
        entry = by_generic[generic.lower()]
        merged = list(entry.get("aliases") or [])
        for a in aliases:
            if a.lower() != generic.lower() and a not in merged:
                merged.append(a)
        entry["aliases"] = merged

    # An override keyed on a generic that is not in the library fails the
    # same way an alias does - silently. The text simply never reaches a
    # popup and nothing says so. A rename is the likely cause: writing
    # `DRUG_SUMMARIES["phenobarbitone"]` after renaming the entry to
    # `phenobarbital` produces exactly this, and the summary that was
    # meant to correct a wrong drug name would be the thing that never
    # shipped.
    # NEW_DRUGS is not appended to `drugs` - see the note in
    # pearls/_drugs.py. It is registered here only so DRUG_SUMMARIES and
    # DRUG_ALIASES may key on a new name without the guards below
    # rejecting it as unknown.
    new_drugs = [dict(d) for d in _rich.NEW_DRUGS]
    for d in new_drugs:
        d["summary"] = _rich.DRUG_SUMMARIES.get(d["generic"], d.get("summary", ""))
        if not d["summary"].strip():
            raise SystemExit(
                f"NEW_DRUGS entry {d['generic']!r} has no summary; add one "
                f"to DRUG_SUMMARIES keyed on that generic")
        if d["generic"].lower() in by_generic:
            raise SystemExit(
                f"NEW_DRUGS entry {d['generic']!r} is already in the "
                f"library; edit it through DRUG_SUMMARIES instead")
        by_generic[d["generic"].lower()] = d

    new_preclinical = [dict(t) for t in _rich.NEW_PRECLINICAL]
    # From the library on disk, NOT from _preclinical.PRECLINICAL_TERMS.
    # That module now merges the new entries at import, so checking
    # against it would make every entry clash with itself on the second
    # build - and emitting it below would bake them into the base list
    # permanently. Same rule as the drugs above.
    _pre_names = {t["name"].lower() for t in _library.get("preclinical")}
    for t in new_preclinical:
        if not (t.get("summary") or "").strip():
            raise SystemExit(
                f"NEW_PRECLINICAL entry {t['name']!r} has no summary")
        if t["name"].lower() in _pre_names:
            raise SystemExit(
                f"NEW_PRECLINICAL entry {t['name']!r} is already in the "
                f"library; two entries under one name means whichever "
                f"indexes first wins")

    orphaned = [g for g in _rich.DRUG_SUMMARIES if g.lower() not in by_generic]
    if orphaned:
        raise SystemExit(
            f"DRUG_SUMMARIES names {len(orphaned)} generic(s) not in the "
            f"library, so the text would never match: {orphaned}")

    return {
        "schema": SCHEMA,
        "conditions": conditions,
        "new_conditions": _rich.NEW_CONDITIONS,
        "rich_summaries": _rich.RICH_SUMMARIES,
        "drugs": drugs,
        "new_drugs": new_drugs,
        "drug_summaries": _rich.DRUG_SUMMARIES,
        "drugbank_ids": drugbank_ids,
        "acronyms": {k: [list(c) for c in v]
                     for k, v in _acronyms._ACRONYMS.items()},
        "signs": _signs.SIGN_TERMS,
        "descriptive": _descriptive.DESCRIPTIVE_TERMS,
        "preclinical": _library.get("preclinical"),
        "new_preclinical": new_preclinical,
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
    # Zero-padded d.m.y dotted date, matching `date +%d.%m.%Y` in
    # tools/publish_content.sh. These two defaults must agree.
    #
    # Versions are compared as strings by the client (see `_newer` in
    # pearls/_updater.py). Under d.m.y this sorts chronologically WITHIN
    # a calendar month but not ACROSS month or year rollovers. The
    # in-tree client parses both d.m.y[.N] and y.m.d[.N] as (year,
    # month, day, counter) tuples so mid-history transition is safe;
    # anything installed from an AnkiWeb push before that update lands
    # will need a bump before the next month rollover.
    #
    # Keep the padding: 1.9.2026 sorts above 15.09.2026 as strings.
    lib["content_version"] = (
        args.version or datetime.date.today().strftime("%d.%m.%Y"))

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
