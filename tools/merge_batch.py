#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""Merge authored entry batches into `content/_rich.py`.

An entry is two things in that file: a stub in `NEW_CONDITIONS` carrying
the name, aliases and UpToDate chips, and the text itself in
`RICH_SUMMARIES` keyed on the same name. This writes both, wrapped and
indented the way the file is written by hand, so the diff stays readable.

Run `tools/verify_batch.py` first. This script guards only against
writing something twice; it does not judge content.

Usage, from the add-on root:

    python3 tools/verify_batch.py drafts/*.json && \
    python3 tools/merge_batch.py drafts/*.json

It is also the right tool for a conflict in `_rich.py` after the
scheduled agent has pushed to the same branch: take the remote file
whole and re-apply the local batch through this, rather than resolving
the text by hand. A union merge silently duplicates an entry that both
sides added, and a duplicate key is the failure that costs most to find.
"""
import argparse
import json
import pathlib
import re
import sys
import textwrap

ROOT = pathlib.Path(__file__).resolve().parent.parent
RICH = ROOT / "content" / "_rich.py"

# The close of NEW_CONDITIONS, which is also the open of RICH_SUMMARIES.
NC_ANCHOR = "\n]\n\n\nRICH_SUMMARIES = {"
# The close of RICH_SUMMARIES. Matched by pattern rather than a fixed
# string because an earlier merge left no blank line before the brace and
# a literal marker then failed outright. Failing loudly was correct - it
# wrote nothing - but the anchor should tolerate either.
RS_ANCHOR = re.compile(r"\n\n?\}\n\n\n# ═══")


def stub(e):
    aliases = ", ".join(json.dumps(a, ensure_ascii=False)
                        for a in e.get("aliases", []))
    utd = ", ".join(
        "[" + ", ".join(json.dumps(x, ensure_ascii=False) for x in pair) + "]"
        for pair in e.get("utd", []))
    return ('    {\n'
            f'        "name": {json.dumps(e["name"], ensure_ascii=False)},\n'
            f'        "aliases": [{aliases}],\n'
            f'        "utd": [{utd}],\n'
            '        "summary": "",\n'
            '    },\n')


def fmt(name, text):
    lines = textwrap.wrap(text, width=60, break_long_words=False,
                          break_on_hyphens=False)
    body = "\n".join(f'        "{l} "' for l in lines[:-1])
    body += ("\n" if body else "") + f'        "{lines[-1]}"'
    return f'    {json.dumps(name, ensure_ascii=False)}: (\n{body}\n    ),\n'


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("files", nargs="+", type=pathlib.Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    entries = []
    for f in args.files:
        entries += json.load(open(f, encoding="utf-8"))

    t = RICH.read_text(encoding="utf-8")
    seen, kept = set(), []
    for e in entries:
        n = e["name"]
        if n in seen:
            print(f"SKIP duplicate within batch: {n}")
            continue
        if f'"name": {json.dumps(n, ensure_ascii=False)}' in t \
                or f'\n    {json.dumps(n, ensure_ascii=False)}: (' in t:
            print(f"SKIP already in the file: {n}")
            continue
        if "—" in json.dumps(e, ensure_ascii=False):
            print(f"SKIP em-dash present: {n}")
            continue
        seen.add(n)
        kept.append(e)

    print(f"inserting {len(kept)} of {len(entries)}")
    if not kept or args.dry_run:
        return 0

    if t.count(NC_ANCHOR) != 1:
        raise SystemExit("the NEW_CONDITIONS anchor is not unique; "
                         "aborting, nothing written")
    t = t.replace(NC_ANCHOR,
                  "\n" + "".join(stub(e) for e in kept).rstrip("\n") + NC_ANCHOR,
                  1)

    m = RS_ANCHOR.search(t)
    if m is None:
        raise SystemExit("could not find the close of RICH_SUMMARIES; "
                         "aborting, nothing written")
    block = "\n" + "".join(fmt(e["name"], e["summary"]) for e in kept)
    t = t[:m.start()] + "\n" + block.rstrip("\n") + t[m.start():]

    RICH.write_text(t, encoding="utf-8")
    print(f"written to {RICH.relative_to(ROOT)}")
    print("next: python3 tools/build_library.py && python3 tests/test_vocab.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
