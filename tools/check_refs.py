#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""Check every `ENTRY_REFS` destination still leads where it claims.

A status code is not enough, and assuming it was is how a dead link
shipped. The two URLs this table was seeded with returned 200 to
`curl -sSL` and were recorded as verified. They were 301s: RANZCOG had
withdrawn the document, and both entries actually landed on a generic
patient-information hub. The popup button said "Open RANZCOG" and
opened a page about nothing in particular - the exact failure the whole
mechanism exists to prevent, shipped inside it.

So this compares the FINAL url against the requested one, ignoring only
the fragment, which curl keeps and a server never sees. A redirect to a
different page is a failure even when it answers 200.

Deliberately not part of the build or the publish: those must work
offline and must not depend on somebody else's uptime. Run it when the
table changes, and before a release that touches it.

    python3 tools/check_refs.py           # every entry
    python3 tools/check_refs.py --quiet   # only the failures
"""
import concurrent.futures as cf
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "content"))

TIMEOUT = 30
WORKERS = 8


def _curl(url: str, fmt: str) -> str:
    return subprocess.run(
        ["curl", "-sS", "-o", "/dev/null", "-w", fmt, "-L",
         "--max-time", str(TIMEOUT), url],
        capture_output=True, text=True, timeout=TIMEOUT + 10).stdout.strip()


def _strip(u: str) -> str:
    """Compare without the fragment, and without a trailing slash.

    curl reports the fragment back in `url_effective` although it never
    sends it, so leaving it on one side of the comparison and not the
    other reports every anchored link as a redirect. That false positive
    cost a round of checking; hence one function used on both sides.
    """
    return u.split("#")[0].rstrip("/")


def check(item):
    name, (label, url) = item
    try:
        code = _curl(url, "%{http_code}")
        final = _curl(url, "%{url_effective}")
    except Exception as exc:                            # noqa: BLE001
        return name, label, url, "ERR", str(exc)[:60]
    if code != "200":
        return name, label, url, code, "not 200"
    if _strip(final) != _strip(url):
        return name, label, url, code, f"redirects to {final}"
    return name, label, url, code, "ok"


def main() -> int:
    quiet = "--quiet" in sys.argv
    import _rich                                        # content/_rich.py
    refs = dict(_rich.ENTRY_REFS)
    print(f"checking {len(refs)} reference destinations "
          f"({len({u for _l, u in refs.values()})} distinct URLs)\n")

    failures = []
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for name, label, url, code, note in ex.map(check, sorted(refs.items())):
            if note != "ok":
                failures.append((name, label, url, code, note))
                print(f"  FAIL [{code}] {name}\n"
                      f"        {label}: {url}\n"
                      f"        {note}")
            elif not quiet:
                print(f"  ok         {name}  ({label})")

    print()
    if failures:
        print(f"{len(failures)} destination(s) no longer lead where they "
              f"claim. A link the reader is invited to trust and which "
              f"lands somewhere else is worse than no link at all - fix "
              f"or remove each one.")
        return 1
    print("every destination resolves to the page it names.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
