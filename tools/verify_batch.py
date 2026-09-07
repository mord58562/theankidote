#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""Check authored entry batches before they are merged into `_rich.py`.

Content arrives in batches - a topic at a time, often written in
parallel - and every failure this checks for has actually shipped or
nearly shipped at least once. The suite catches most of them too, but
only after the batch is merged into a 3.5 MB source file, where backing
one entry out is a diff to unpick rather than a file to delete.

Input is one or more JSON files, each a list of:

    {"name": ..., "aliases": [...], "utd": [["Overview", "..."]],
     "summary": "..."}

Usage, from the add-on root:

    python3 tools/verify_batch.py drafts/*.json

Exits non-zero if anything failed. Warnings are printed and do not.

The alias-ambiguity check needs AnkiConnect on 127.0.0.1:8765 and is
skipped with a warning when Anki is not running, because a short
all-caps alias is only judgeable against the collection it will fire in.
The count is pulled live every run and never cached: the collection
changes while a session works, and a stale number reads as authoritative.
"""
import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

BANNED_CHARS = [("—", "em-dash"), ("–", "en-dash"),
                ("**", "markdown bold"), (" ", "non-breaking space")]
BANNED_TOKENS = ["ATSI", "canonical"]

# `(?<![a-z])` and not `(?<![oa])`: 'edema' is a substring of
# Beckwith-Wiedemann, which the looser lookbehind flagged as US spelling.
US_SPELLINGS = [
    (r"(?<![a-z])edema", "oedema"), (r"\blymphedema", "lymphoedema"),
    (r"\banemi", "anaemia"), (r"\besophag", "oesophag"),
    (r"\btumor\b", "tumour"), (r"\bdiarrhea", "diarrhoea"),
    (r"\bleukemi", "leukaemia"), (r"(?<![a-z])ischemi", "ischaemia"),
    (r"\betiolog", "aetiolog"), (r"\bpediatric", "paediatric"),
    (r"(?<![a-z])hemorrhag", "haemorrhag"), (r"\bcesarean", "caesarean"),
    (r"\bfetal\b", "foetal"), (r"\bhematolog", "haematolog"),
]

MAX_CHARS = 1200
MAX_PX = 900
LABEL_RE = re.compile(r"(?:^|(?<=[.!?]) )([A-Z][A-Za-z0-9 /-]{1,30}):")


def known_labels():
    """Read the whitelist off the test that enforces it.

    Duplicating the set here would let the two drift, and the drift is
    silent - an unrecognised label renders as body text rather than
    raising.
    """
    src = (ROOT / "tests" / "test_vocab.py").read_text(encoding="utf-8")
    m = re.search(r"KNOWN_LABELS\s*=\s*(?:frozenset\()?\{(.*?)\}", src, re.S)
    if m is None:
        raise SystemExit("KNOWN_LABELS not found in tests/test_vocab.py")
    return {s.lower() for s in re.findall(r'"([^"]+)"', m.group(1))}


def collection_text():
    """Every note in the running collection as one blob, or None."""
    import urllib.error
    import urllib.request
    def call(action, **params):
        req = urllib.request.Request(
            "http://127.0.0.1:8765",
            data=json.dumps({"action": action, "version": 6,
                             "params": params}).encode(),
            headers={"Content-Type": "application/json"})
        r = json.load(urllib.request.urlopen(req, timeout=180))
        if r.get("error"):
            raise SystemExit(f"AnkiConnect error: {r['error']}")
        return r["result"]
    try:
        ids = call("findNotes", query="deck:*")
    except (urllib.error.URLError, OSError):
        return None
    out = []
    for i in range(0, len(ids), 800):
        for n in call("notesInfo", notes=ids[i:i + 800]):
            t = " ".join(f["value"] for f in n["fields"].values())
            t = re.sub(r"<[^>]+>", " ", t)
            t = re.sub(r"&nbsp;", " ", t).replace("&amp;", "&")
            t = re.sub(r"\{\{c\d+::(.*?)(?:::[^}]*)?\}\}", r"\1", t)
            out.append(re.sub(r"\s+", " ", t).strip())
    return " \n ".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("files", nargs="+", type=pathlib.Path)
    ap.add_argument("--no-anki", action="store_true",
                    help="skip the alias-ambiguity check")
    args = ap.parse_args()

    entries = []
    for f in args.files:
        batch = json.load(open(f, encoding="utf-8"))
        for e in batch:
            e["_src"] = f.name
        entries += batch
        print(f"{f.name:28s} {len(batch):3d} entries")
    print(f"TOTAL {len(entries)}\n")

    fail, warn = [], []

    for e in entries:
        for k in ("name", "aliases", "utd", "summary"):
            if k not in e:
                fail.append(f"{e.get('name')}: missing key {k!r}")
        if not e.get("summary", "").strip():
            fail.append(f"{e.get('name')}: empty summary")
    if fail:
        report(fail, warn)
        return 1

    blob = json.dumps(entries, ensure_ascii=False)
    for ch, label in BANNED_CHARS:
        if ch in blob:
            fail.append(f"BANNED {label} x{blob.count(ch)}")
    for tok in BANNED_TOKENS:
        n = len(re.findall(r"\b" + tok + r"\b", blob, re.I))
        if n:
            fail.append(f"BANNED token {tok!r} x{n}")

    # Two batches writing the same name is not caught by the alias check
    # below - that fires when two DIFFERENT entries claim one term, and
    # two copies of one name are not different entries. The merge script
    # would silently keep the first and drop the second.
    by_name = {}
    for e in entries:
        by_name.setdefault(e["name"], []).append(e["_src"])
    for name, srcs in by_name.items():
        if len(srcs) > 1:
            fail.append(f'DUPLICATE ENTRY NAME "{name}" in {sorted(srcs)}')

    owner = {}
    for e in entries:
        for term in [e["name"]] + list(e["aliases"]):
            t = term.lower()
            if t in owner and owner[t] != e["name"]:
                fail.append(f'COLLISION "{term}": '
                            f'{owner[t]} vs {e["name"]}')
            owner[t] = e["name"]

    known = known_labels()
    for e in entries:
        labels = [l.strip() for l in LABEL_RE.findall(e["summary"])]
        for lbl in labels:
            if lbl.lower() not in known:
                fail.append(f'{e["name"]}: unknown section label '
                            f'"{lbl}" - it renders as body text')
        if len([l for l in labels if l.lower() in known]) < 3:
            warn.append(f'{e["name"]}: fewer than 3 recognised sections')
        for pat, want in US_SPELLINGS:
            if re.search(pat, e["summary"], re.I):
                fail.append(f'{e["name"]}: US spelling, want {want}')

    from tests.test_vocab import PopupHeightBudget       # noqa: E402
    est = PopupHeightBudget()
    for e in entries:
        # Cost the chip row off the DRAFT, not off the library. Looking
        # the name up there returns None for every entry in a new batch -
        # they are not in it yet, which is the point - so the UpToDate
        # chips were costed at zero and an entry could verify clean and
        # then fail `test_over_cap_backlog_only_shrinks` on merge. That
        # is exactly what "Cancer immunotherapy" did: 812px here, 914px
        # once its one chip row was counted.
        px = est._estimate_px(e["summary"], e["name"], e)
        if px > MAX_PX or len(e["summary"]) > MAX_CHARS:
            fail.append(f'{e["name"]}: over budget '
                        f'({len(e["summary"])} chars, {px:.0f} px)')

    # A short all-caps alias is the one kind that can shadow the acronym
    # dictionary, and the only way to judge it is against the collection
    # it will fire in.
    if args.no_anki:
        warn.append("alias-ambiguity check skipped (--no-anki)")
    else:
        notes = collection_text()
        if notes is None:
            warn.append("AnkiConnect unreachable, so short all-caps "
                        "aliases were NOT checked against the collection")
        else:
            lib = json.loads((ROOT / "data" / "library.json")
                             .read_text(encoding="utf-8"))
            acronyms = set(lib["acronyms"])
            for e in entries:
                for a in e["aliases"]:
                    if not (2 <= len(a) <= 5 and a.isupper() and a.isalpha()):
                        continue
                    if a in acronyms:
                        fail.append(f'{e["name"]}: alias "{a}" is already '
                                    f'in the acronym dictionary')
                        continue
                    n = len(re.findall(r"(?<![A-Za-z])" + a + r"(?![A-Za-z])",
                                       notes))
                    if n >= 25:
                        warn.append(f'{e["name"]}: alias "{a}" fires {n}x in '
                                    f'the collection - check every context '
                                    f'means this entry')

    return report(fail, warn)


def report(fail, warn):
    print("--- FAILURES ---" if fail else "--- NO FAILURES ---")
    for f in fail:
        print("  ", f)
    print("\n--- WARNINGS (review by hand) ---" if warn else "\n--- no warnings ---")
    for w in warn:
        print("  ", w)
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
