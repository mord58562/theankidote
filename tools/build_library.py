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
import re
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
#
# Adding an optional key is not such a change. `_library._validate`
# walks the keys it knows and ignores the rest, and `_library.get`
# takes a default for exactly this case, so an older client reads a
# library carrying a new key and simply does not use it. Bumping for
# an addition would instead make every older client refuse the whole
# library and stop receiving content. Bump when an existing key
# changes shape or meaning; do not bump to add one.
SCHEMA = 1


def collect() -> dict:
    import _rich                                        # content/_rich.py
    import _blocklist                                   # content/_blocklist.py
    import _new_acronyms                                # content/_new_acronyms.py
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
    #
    # WARNING, and this has cost content once: `data/library.json` is
    # BOTH the output of this script and the source of the base
    # vocabularies below. So `git checkout -- data/library.json` is
    # harmless after a plain rebuild and destructive after a content
    # edit - it silently reverts conditions, drugs, acronyms and
    # preclinical to whatever was last published. 85 rewritten acronym
    # glosses were lost that way, and the publish that followed shipped
    # the reverted file without anything looking wrong. Edit it, build,
    # test, then PUBLISH - `publish_content.sh` commits it. Never revert
    # it to tidy up.
    #
    # And they must come from the BUNDLED copy specifically.
    # `_library._load` prefers `user_files/library.json` when it carries
    # the newer content version, which is right at runtime and wrong
    # here: both paths resolve relative to this checkout, so a library
    # downloaded for debugging and dropped into `user_files/` would
    # silently become the base vocabulary for the next build, and the
    # publish would ship it. `user_files/` is gitignored, so nothing in
    # review would show it either.
    if pathlib.Path(_library.USER_COPY).exists():
        raise SystemExit(
            f"{_library.USER_COPY} exists. The runtime loader prefers it "
            f"over the bundled library when it is newer, so a build would "
            f"take its base vocabulary from a downloaded file. Move it "
            f"aside before building.")
    conditions = [dict(c) for c in _library.get("conditions")]

    # Merge the alternate-name table into the condition entries, on the
    # same terms as the drug aliases below: `aliases` is additive, schema
    # stays 1, and the names travel over the content channel instead of
    # waiting for an AnkiWeb release.
    #
    # A key that names no condition is a typo and a silent one - the
    # alias would never match and nothing would say so - so fail the
    # build. `NEW_CONDITIONS` counts as a target: those entries are part
    # of the shipped vocabulary even though they are not in the base
    # list yet.
    by_condition = {}
    for c in conditions:
        by_condition.setdefault(c["name"].lower(), c)
    new_conditions = [dict(c) for c in _rich.NEW_CONDITIONS]
    for c in new_conditions:
        by_condition.setdefault(c["name"].lower(), c)

    unknown = [n for n in _rich.CONDITION_ALIASES
               if n.lower() not in by_condition]
    if unknown:
        raise SystemExit(
            f"CONDITION_ALIASES names {len(unknown)} condition(s) not in "
            f"the library, so the aliases would never match: {unknown}")

    # An alias already claimed by a different entry is worse than one
    # that never matches: `_conditions._LOOKUP` is built first-occurrence
    # wins, so the popup would silently keep showing whichever entry
    # happened to index first and the new alias would look like it had
    # simply been ignored.
    claimed = {}
    for c in conditions + new_conditions:
        for key in [c["name"]] + list(c.get("aliases") or []):
            claimed.setdefault(key.lower(), c["name"])
    for name, aliases in _rich.CONDITION_ALIASES.items():
        entry = by_condition[name.lower()]
        merged = list(entry.get("aliases") or [])
        have = {a.lower() for a in merged} | {entry["name"].lower()}
        for a in aliases:
            owner = claimed.get(a.lower())
            if owner is not None and owner.lower() != name.lower():
                raise SystemExit(
                    f"CONDITION_ALIASES[{name!r}] claims {a!r}, which "
                    f"already belongs to {owner!r}; the lookup is "
                    f"first-occurrence wins, so the alias would never "
                    f"reach {name!r}")
            if a.lower() in have:
                continue
            have.add(a.lower())
            merged.append(a)
            claimed[a.lower()] = entry["name"]
        entry["aliases"] = merged

    # Merge the reference-destination table. A condition with no NBK
    # chapter falls back to a search inside the StatPearls book, and for
    # most of the 2,099 summaries without a chapter that search answers
    # a different question than the one asked. An entry here names a
    # real destination for the popup's button instead.
    #
    # Validated the same way as the aliases above: a key naming no
    # condition is a typo, and a silent one, because the popup would
    # simply keep its old button.
    unknown_refs = [n for n in _rich.ENTRY_REFS
                    if n.lower() not in by_condition]
    if unknown_refs:
        raise SystemExit(
            f"ENTRY_REFS names {len(unknown_refs)} condition(s) not in "
            f"the library: {unknown_refs[:8]}")
    for name, ref in _rich.ENTRY_REFS.items():
        if (not isinstance(ref, (list, tuple)) or len(ref) != 2
                or not all(isinstance(x, str) and x.strip() for x in ref)):
            raise SystemExit(
                f"ENTRY_REFS[{name!r}] must be [label, url]; got {ref!r}")
        label, url = ref
        if not url.startswith("https://"):
            raise SystemExit(
                f"ENTRY_REFS[{name!r}] url is {url!r}; a reference the "
                f"reader is asked to trust travels over HTTPS")
        by_condition[name.lower()]["ref"] = [label.strip(), url.strip()]

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

    # `pearls/_acronyms` reads this dictionary out of the library and we
    # write it straight back, so without an overlay the vocabulary has no
    # way in - the one vocabulary that never grew a `NEW_*` file. Merge
    # it here on the same terms as the others.
    acronyms = {k: [list(c) for c in v]
                for k, v in _acronyms._ACRONYMS.items()}
    for key, senses in getattr(_new_acronyms, "NEW_ACRONYMS", {}).items():
        bucket = acronyms.setdefault(key, [])
        have = {str(c[0]).lower() for c in bucket}
        for sense in senses:
            if len(sense) != 3:
                raise SystemExit(
                    f"NEW_ACRONYMS[{key!r}] sense is not "
                    f"(expansion, keywords, description): {sense!r}")
            expansion, keywords, desc = sense
            if not (expansion and desc):
                raise SystemExit(
                    f"NEW_ACRONYMS[{key!r}] has an empty expansion or "
                    "description")
            if not isinstance(keywords, (list, tuple)):
                raise SystemExit(
                    f"NEW_ACRONYMS[{key!r}] keywords must be a list")
            if str(expansion).lower() in have:
                continue
            have.add(str(expansion).lower())
            bucket.append([expansion, list(keywords), desc])
        # An acronym carrying more than one sense is disambiguated only
        # by its keywords; a sense with none can never lose, so it would
        # silently shadow its siblings.
        if len(bucket) > 1:
            starved = [c[0] for c in bucket if not c[1]]
            if starved:
                raise SystemExit(
                    f"acronym {key!r} has {len(bucket)} senses but "
                    f"{starved} carry no context keywords")

    blocklist = sorted({
        t.strip() for t in getattr(_blocklist, "BLOCKLIST", []) if t.strip()})
    bad = [t for t in blocklist if not isinstance(t, str)]
    if bad:
        raise SystemExit(f"BLOCKLIST holds non-strings: {bad[:3]}")

    # An alias must not be this entry's own name joined to another
    # entry's name by a connective.
    #
    # The matcher is longest-form-wins and non-overlapping, so such an
    # alias does not merely add a surface - it eats its neighbour. The
    # entry "Positive symptoms" carried the alias "positive symptoms of
    # schizophrenia", so on a card reading "the 3 positive symptoms of
    # schizophrenia" the 33-character form won, consumed the word
    # schizophrenia, and Schizophrenia's own entry never resolved at
    # all. Every one of those runs then rendered the Positive symptoms
    # popup, including the run that was literally the word
    # schizophrenia. Four more had the same shape: the Ranson, Light and
    # Duke criteria each swallowed the disease they score, and Negative
    # symptoms swallowed schizophrenia the same way its sibling did.
    #
    # The rule is deliberately narrow, because most relational aliases
    # are correct and must survive. "dementia with Lewy bodies" contains
    # the primary name "Dementia" and SHOULD win the whole phrase, since
    # the phrase names one disease. What separates the harmful case is
    # that the left half is already this entry's own name, so the alias
    # adds no surface the primary name did not already match - it can
    # only take words away from a neighbour. Nothing is lost by refusing
    # it: "Ranson criteria" still matches on its own.
    connective = r"(?:\s+(?:of|in|with|for|after|versus|vs|during)\s+)"
    primaries = {}
    for e in conditions + new_conditions:
        primaries[e["name"].lower()] = e["name"]
    swallowing = []
    for e in conditions + new_conditions:
        own = e["name"].lower()
        for a in (e.get("aliases") or []):
            m = re.fullmatch(r"(.+?)" + connective + r"(.+)", a.lower().strip())
            if not m:
                continue
            left, right = m.group(1).strip(), m.group(2).strip()
            if left == own and right in primaries and right != own:
                swallowing.append((e["name"], a, primaries[right]))
    if swallowing:
        lines = "\n".join(f"  {n!r} alias {a!r} swallows {v!r}"
                          for n, a, v in swallowing)
        raise SystemExit(
            f"{len(swallowing)} alias(es) are this entry's own name joined "
            f"to another entry's name, which makes the matcher consume the "
            f"neighbour instead of resolving it:\n{lines}\n"
            f"Drop the alias - the primary name already matches its first "
            f"half. If a case here is genuinely one concept rather than "
            f"two, rename the entry instead of aliasing across the join.")

    return {
        "schema": SCHEMA,
        "conditions": conditions,
        "new_conditions": new_conditions,
        "rich_summaries": _rich.RICH_SUMMARIES,
        "drugs": drugs,
        "new_drugs": new_drugs,
        "drug_summaries": _rich.DRUG_SUMMARIES,
        "drugbank_ids": drugbank_ids,
        "acronyms": acronyms,
        "signs": _signs.SIGN_TERMS,
        "descriptive": _descriptive.DESCRIPTIVE_TERMS,
        "preclinical": _library.get("preclinical"),
        "new_preclinical": new_preclinical,
        "psych": _psych.PSYCH_TERMS,
        "blocklist": blocklist,
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
    manifest_path = out.parent / "manifest.json"
    # `data/manifest.json` is not a build artefact. It is the live
    # channel pointer: every installed client polls it on launch, and
    # `_updater._check` bails with "the update server sent an incomplete
    # reply" the moment it has no `url`.
    #
    # This rewrote it unconditionally and only put the url back when
    # `--url` was passed, which only `publish_content.sh` does. A bare
    # `python3 tools/build_library.py` - the documented usage, what
    # `merge_batch.py` prints as the next step, and what the scheduled
    # content agent runs - therefore stripped the url and the next
    # commit shipped a dead channel. Nineteen of the last forty commits
    # touching this file carried no url; updates were off for every user
    # from each of those until the next publish restored the key.
    #
    # So a build that is not publishing leaves the pointer alone. It
    # describes an asset that has been uploaded, and only the publish
    # knows where that is; rewriting its version and sha to describe a
    # library nobody can download is not an improvement on omitting the
    # url, it is the same outage with a checksum failure in front of it.
    if args.url:
        manifest_path.write_text(
            json.dumps({
                "schema": SCHEMA,
                "content_version": lib["content_version"],
                "sha256": digest,
                "bytes": len(blob),
                "url": args.url,
            }, indent=2) + "\n", encoding="utf-8")
        manifest_note = args.url
    else:
        try:
            held = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest_note = (f"unchanged - still points at "
                             f"{held.get('content_version', '?')}")
        except Exception:
            manifest_note = "unchanged (none on disk yet)"

    try:
        shown = out.relative_to(ROOT)
    except ValueError:                  # --out pointed outside the repo
        shown = out
    print(f"{shown}  {len(blob) / 1024:.0f} KB"
          f"  ({len(gzip.compress(blob)) / 1024:.0f} KB gzipped)")
    for key in ("conditions", "drugs", "acronyms", "rich_summaries",
                "signs", "descriptive", "preclinical", "psych"):
        print(f"  {key:16} {len(lib[key])}")
    print(f"  content_version  {lib['content_version']}")
    print(f"  sha256           {digest[:16]}...")
    print(f"  manifest         {manifest_note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
