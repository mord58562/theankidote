# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""Checks for a newer term library and downloads it into `user_files/`.

Content and code ship on different clocks. A wrong dose in a drug
summary should be fixable the same day; pushing it through AnkiWeb means
a version bump, a review, and waiting for users to update. This module
is the content channel: it fetches a small manifest, and only if that
manifest advertises newer, schema-compatible content does it fetch the
library itself.

What it deliberately does not do:

  * **Run on the UI thread.** The check happens on a daemon thread with
    a short timeout. A slow or hijacked host must never be able to hang
    Anki's startup, so nothing here is awaited.
  * **Fetch anything but data.** The payload is parsed with `json.loads`
    and validated by `_library._validate`. It is never imported,
    `exec`'d or unpickled. This is also what keeps the add-on inside
    AnkiWeb's rules on downloaded code.
  * **Trust the payload's own version claim.** The manifest states a
    sha256 and a byte count; the body is checked against both before it
    is written anywhere. A truncated download is the common case and
    would otherwise land as corrupt content.
  * **Apply mid-session.** The new file is written but not loaded. The
    matcher and every lookup table are built at import, so swapping the
    library under a running reviewer would leave the two inconsistent.
    It takes effect at next launch.

On by default as of 2.0.1, with a switch in Settings. 2.0.0 shipped it
off and buried in a JSON config file, which meant the channel existed
and nobody was on it - a correction could be published and reach
essentially no one. A reference database that silently goes stale is
worse for a clinical tool than one that fetches a signed, validated data
file, so the default flipped and the control moved somewhere findable.

The switch is one checkbox in Settings > General, the host is named in
config.md, and turning it off stops all network activity for content.
"""
import hashlib
import json
import os
import threading
import urllib.request

from . import _library
from ._library import log

DEFAULT_MANIFEST_URL = (
    "https://raw.githubusercontent.com/mord58562/theankidote"
    "/main/data/manifest.json")

_TIMEOUT = 8          # seconds; a check that cannot finish is not worth having
_MAX_BYTES = 8 << 20  # a library ~40x the current size is a bug or an attack
_UA = "TheAnkiDote content updater"


def _require_https(url: str, what: str) -> str:
    """Reject anything that is not an https URL, before it reaches urllib.

    `urllib.request.urlopen` is not an HTTP client. Its default opener
    also carries `FileHandler`, `FTPHandler` and `DataHandler`, so a
    string reaching it can name `file:///`, `ftp://` or `data:` and be
    fetched. Two strings reach it here and neither is trustworthy
    enough to pass through unchecked:

      * the manifest url comes from `libraryManifestUrl` in config,
        which is a plain JSON file any other add-on can write;
      * the library url comes from the body of the manifest, so it is
        controlled by whoever controls the content host.

    Neither can currently be turned into data the attacker gets to read
    - the response has to match the manifest's sha256 and then validate
    as a schema-1 library before it is kept - but "the exfiltration path
    happens to be missing" is not the same as "this is not a file read",
    and blind requests to `http://localhost:...` on Anki startup are a
    capability worth not having.

    https only, not http. The sha256 in the manifest already protects
    the library's integrity over any transport, so this is about the
    manifest itself, which nothing else covers: fetched over http, its
    url and its checksum are both attacker-controlled at once, and every
    later check in this module is checking the attacker's numbers
    against the attacker's file.

    Redirects do not need a matching check here. CPython's
    `HTTPRedirectHandler.http_error_302` refuses to follow anything but
    http, https and ftp, so a redirect cannot reach `file:`. It can
    still downgrade https to http, which is why `_fetch` re-checks the
    URL it actually landed on.
    """
    if not isinstance(url, str) or not url.lower().startswith("https://"):
        raise ValueError(f"{what} must be an https URL, got {str(url)[:60]!r}")
    return url


def _fetch(url: str, limit: int = _MAX_BYTES, what: str = "url") -> bytes:
    _require_https(url, what)
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        # A redirect chain is allowed to move us between hosts - GitHub
        # release downloads go to objects.githubusercontent.com and the
        # asset URL is useless without following that - but it is not
        # allowed to drop us onto plain http on the way.
        final = getattr(resp, "url", None) or url
        _require_https(final, f"{what} after redirect")
        body = resp.read(limit + 1)
    if len(body) > limit:
        raise ValueError(f"response larger than {limit} bytes")
    return body


def _newer(remote: str, local: str) -> bool:
    """Order content versions in either y.m.d[.N] or d.m.y[.N] form.

    Historically the channel used `y.m.d[.N]` and a naive string
    compare ordered it correctly. From 2026-08-28 the publish script
    generates `d.m.y[.N]` (Australian) with a same-day counter that
    resets at local midnight. String compare orders d.m.y correctly
    WITHIN a month but not across month or year rollovers, so we parse
    both shapes into a (year, month, day, counter) tuple and compare
    that.

    Anything unparseable falls back to string compare and, if that is
    also not-greater, is treated as not-newer: refusing an update we do
    not understand is recoverable, applying one we misread is not.
    """
    if not (bool(remote) and isinstance(remote, str)):
        return False
    r, l = _parse_version(remote), _parse_version(local)
    if r is not None and l is not None:
        return r > l
    return remote > local


def _parse_version(v: str):
    """Return (year, month, day, counter) for a d.m.y[.N] or y.m.d[.N]
    version, or None if the shape does not match either.

    The two forms are distinguished by which component is four digits:
    2026.08.29 has the year first, 29.08.2026 has it last. Anything
    else (missing components, wrong widths, non-numeric) returns None
    so the caller falls back to string compare.
    """
    if not isinstance(v, str):
        return None
    parts = v.split(".")
    counter = 0
    if len(parts) == 4:
        try:
            counter = int(parts[3])
        except ValueError:
            return None
        parts = parts[:3]
    if len(parts) != 3:
        return None
    try:
        a, b, c = int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        return None
    if len(parts[0]) == 4:
        year, month, day = a, b, c
    elif len(parts[2]) == 4:
        day, month, year = a, b, c
    else:
        return None
    if not (1 <= month <= 12 and 1 <= day <= 31 and 1900 <= year <= 2999):
        return None
    return (year, month, day, counter)


def _write_atomically(path: str, body: bytes) -> None:
    """Write via a temp file in the same directory, then rename.

    A half-written library is worse than an old one: `_library` would
    reject it and fall back, but only after the user has restarted and
    wondered why their content went backwards. `os.replace` is atomic on
    both platforms Anki targets.

    The temp file is opened with `O_CREAT | O_EXCL | O_NOFOLLOW` rather
    than plain `open(tmp, "wb")`. `"wb"` follows symlinks, so a
    pre-planted `library.json.part` pointing at any file the Anki
    process can write turns this function into a truncate-and-overwrite
    of that target. It needs local write access to `user_files/` to set
    up, which is not a high bar for anything already running as the
    user, and the cost of closing it is three lines.

    `os.replace` needs no equivalent guard: rename operates on the
    directory entry, so a symlink at `path` is replaced rather than
    followed.

    The temp name carries the pid and thread id, and the previous fixed
    `library.json.part` was a race. Two checks can run at once - one
    started by `check_in_background` at launch, one by the "Check now"
    button in Settings - and with a shared name the sequence is:

        A  os.open(tmp, O_EXCL)          -> inode 1
        B  os.unlink(tmp)                -> A's entry gone, A's fd fine
        B  os.open(tmp, O_EXCL)          -> inode 2, starts writing
        A  finishes, os.replace(tmp,...) -> renames *B's* half-written file

    so `library.json` ends up truncated. `_validate` catches it at the
    next launch and falls back, but the user sees their content revert
    with no explanation. A unique name removes the interleaving instead
    of narrowing it: each writer only ever renames a file it finished
    writing, so the worst case is that the older of two complete and
    valid libraries wins, which is harmless.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.{os.getpid()}.{threading.get_ident():x}.part"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        os.unlink(tmp)
    except FileNotFoundError:
        pass
    fd = os.open(tmp, flags, 0o600)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(body)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    os.replace(tmp, path)


def check(manifest_url: str = None) -> str:
    """Run the check synchronously. Returns a human-readable outcome.

    Returns rather than only logs, because Settings has a "Check now"
    button and a button that appears to do nothing is worse than no
    button. Never raises.
    """
    manifest_url = manifest_url or DEFAULT_MANIFEST_URL
    try:
        return _check(manifest_url)
    except Exception as exc:                            # noqa: BLE001
        log(f"updater: check failed ({exc})")
        return f"Check failed: {exc}"


def _check(manifest_url: str) -> str:
    try:
        manifest = json.loads(
            _fetch(manifest_url, 64 << 10, "manifest url").decode("utf-8"))
    except Exception as exc:                            # noqa: BLE001
        log(f"updater: manifest check failed ({exc})")
        return "Could not reach the update server."

    if manifest.get("schema") != _library.SCHEMA:
        log(f"updater: remote content is schema "
            f"{manifest.get('schema')!r}, this build reads "
            f"{_library.SCHEMA}; update the add-on to receive it")
        return ("Newer content exists but needs a newer version of the "
                "add-on. Update it from Tools > Add-ons.")

    remote = manifest.get("content_version")
    if not _newer(remote, _library.CONTENT_VERSION):
        log(f"updater: content {_library.CONTENT_VERSION} is current")
        return f"Up to date (content {_library.CONTENT_VERSION})."

    url = manifest.get("url")
    want = manifest.get("sha256")
    if not url or not want:
        log("updater: manifest lacks url/sha256; ignoring")
        return "The update server returned an incomplete response."

    try:
        body = _fetch(url, _MAX_BYTES, "library url")
    except Exception as exc:                            # noqa: BLE001
        log(f"updater: download failed ({exc})")
        return "Download failed."

    got = hashlib.sha256(body).hexdigest()
    if got != want:
        log(f"updater: checksum mismatch (got {got[:12]}, "
            f"expected {str(want)[:12]}); discarding")
        return "Downloaded content failed its checksum; discarded."
    if manifest.get("bytes") not in (None, len(body)):
        log("updater: length mismatch; discarding")
        return "Downloaded content was the wrong size; discarded."

    try:
        lib = json.loads(body.decode("utf-8"))
    except Exception as exc:                            # noqa: BLE001
        log(f"updater: payload is not JSON ({exc}); discarding")
        return "Downloaded content was unreadable; discarded."

    why = _library._validate(lib)
    if why:
        log(f"updater: payload rejected - {why}; discarding")
        return "Downloaded content failed validation; discarded."

    try:
        _write_atomically(_library.USER_COPY, body)
    except Exception as exc:                            # noqa: BLE001
        log(f"updater: could not write library ({exc})")
        return "Could not save the downloaded content."

    log(f"updater: content {remote} downloaded; active at next restart")
    return f"Updated to content {remote}. Restart Anki to use it."


def check_in_background(manifest_url: str = DEFAULT_MANIFEST_URL) -> None:
    """Start the check. Returns immediately; never raises."""
    t = threading.Thread(target=check, args=(manifest_url,),
                         name="theankidote-content-update", daemon=True)
    t.start()
