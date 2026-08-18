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


def _fetch(url: str, limit: int = _MAX_BYTES) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        body = resp.read(limit + 1)
    if len(body) > limit:
        raise ValueError(f"response larger than {limit} bytes")
    return body


def _newer(remote: str, local: str) -> bool:
    """Content versions are ISO dates, so a string compare orders them.

    Anything unparseable sorts as not-newer: refusing an update we do
    not understand is recoverable, applying one we misread is not.
    """
    return bool(remote) and isinstance(remote, str) and remote > local


def _write_atomically(path: str, body: bytes) -> None:
    """Write via a temp file in the same directory, then rename.

    A half-written library is worse than an old one: `_library` would
    reject it and fall back, but only after the user has restarted and
    wondered why their content went backwards. `os.replace` is atomic on
    both platforms Anki targets.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".part"
    with open(tmp, "wb") as fh:
        fh.write(body)
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
        manifest = json.loads(_fetch(manifest_url, 64 << 10).decode("utf-8"))
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
        body = _fetch(url)
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
