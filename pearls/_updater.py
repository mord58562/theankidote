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
import urllib.parse
import urllib.request

from . import _library
from ._library import log

DEFAULT_MANIFEST_URL = (
    "https://raw.githubusercontent.com/mord58562/theankidote"
    "/main/data/manifest.json")

# Hosts the content channel is allowed to come from.
#
# The manifest carries a sha256 and the payload is checked against it,
# which sounds like it settles provenance and does not: the manifest and
# the payload come from the same place, so a manifest an attacker wrote
# validates a payload the same attacker wrote. The hash proves the
# download was not truncated or corrupted in transit. It proves nothing
# about who wrote it.
#
# `libraryManifestUrl` is config, and config is a file on disk that a
# hand edit, a pasted config or another add-on can reach. Repointing it
# silently replaces the clinical content of every popup, and
# `_library._load` prefers the downloaded copy, so the substitution
# survives restarts. Pinning the host is the cheap half of the fix; the
# other half is signing the manifest against a key shipped in the
# package, which is the real answer and a larger change.
# GitHub has renamed the host it redirects release downloads to at
# least once, and the rename broke every client silently: the updater
# refused the new host, logged one line, and kept serving whatever copy
# it already had, while `publish_content.sh` verified the same asset
# with `curl -L` and saw a healthy 200. Both hosts are listed because
# the rollover is not atomic, and the publish check now runs through
# `_fetch` so the next rename fails a publish instead of the fleet.
_ALLOWED_HOSTS = frozenset({
    "raw.githubusercontent.com",              # the manifest
    "github.com",                             # release asset, pre-redirect
    "objects.githubusercontent.com",          # where it used to land
    "release-assets.githubusercontent.com",   # where it lands now
})

_TIMEOUT = 8          # seconds; a check that cannot finish is not worth having
_MAX_BYTES = 32 << 20  # backstop against a forged manifest; see _library_limit
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
    host = urllib.parse.urlsplit(url).hostname or ""
    if host.lower() not in _ALLOWED_HOSTS:
        raise ValueError(
            f"{what} points at {host!r}, which is not one of the hosts "
            f"the content channel is published from")
    return url


def _fetch(url: str, limit: int = _MAX_BYTES, what: str = "url") -> bytes:
    _require_https(url, what)
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        # A redirect chain is allowed to move us between hosts - a
        # GitHub release download lands on a separate asset CDN and the
        # asset URL is useless without following that - but it is not
        # allowed to drop us onto plain http, or onto a host outside
        # the allowlist, on the way.
        final = getattr(resp, "url", None) or url
        _require_https(final, f"{what} after redirect")
        body = resp.read(limit + 1)
    if len(body) > limit:
        raise ValueError(f"response larger than {limit} bytes")
    return body


def _library_limit(declared):
    """How many bytes we are willing to read for one library download.

    The ceiling used to be a flat 8 MB, chosen when the library was a
    few hundred kilobytes. Content publishing took it to 5.9 MB in
    nineteen days, so that constant was about to become the thing that
    quietly switched the content channel off: the download would fail,
    every client would keep its bundled copy, and the only symptom
    would be content that stopped arriving.

    The manifest already declares `bytes`, and a payload whose length
    disagrees with that number is discarded a few lines below. So the
    honest limit is what the manifest declares, which scales with the
    content on its own and never needs revisiting. `_MAX_BYTES` stays
    as a backstop for a manifest that declares something absurd, which
    is the case the old constant was really there to catch.
    """
    if isinstance(declared, int) and not isinstance(declared, bool):
        if 0 < declared <= _MAX_BYTES:
            return declared
    return _MAX_BYTES


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


# `_parse_version` moved to `pearls/_library`, which needs it too and
# cannot import this module - `_updater` imports `_library`. One parser,
# imported rather than copied.
_parse_version = _library._parse_version


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
        # The exception goes to the log; the reader gets a sentence.
        # This string is shown in a launch toast and in the Settings
        # window, so someone with no network was being told "Check
        # failed: <urlopen error [Errno 8] nodename nor servname
        # provided, or not known>" - an internal cause they cannot act
        # on, from the one surface here that did not say what happened
        # in plain words.
        log(f"updater: check failed ({exc})")
        return ("Could not reach the content server. Usually that means "
                "no connection.")


def _check(manifest_url: str) -> str:
    try:
        manifest = json.loads(
            _fetch(manifest_url, 64 << 10, "manifest url").decode("utf-8"))
    except Exception as exc:                            # noqa: BLE001
        log(f"updater: manifest check failed ({exc})")
        return ("Could not check for new terms - no connection to the "
                "update server. Your terms still work; it will try "
                "again next time Anki starts.")

    if manifest.get("schema") != _library.SCHEMA:
        log(f"updater: remote content is schema "
            f"{manifest.get('schema')!r}, this build reads "
            f"{_library.SCHEMA}; update the add-on to receive it")
        return ("Newer content exists but needs a newer version of the "
                "add-on. Update it from Tools > Add-ons.")

    remote = manifest.get("content_version")
    if not _newer(remote, _library.CONTENT_VERSION):
        log(f"updater: content {_library.CONTENT_VERSION} is current")
        return "Up to date."

    url = manifest.get("url")
    want = manifest.get("sha256")
    if not url or not want:
        log("updater: manifest lacks url/sha256; ignoring")
        return ("The update server sent an incomplete reply, so nothing "
                "was downloaded. Your terms are unchanged.")

    try:
        body = _fetch(url, _library_limit(manifest.get("bytes")), "library url")
    except Exception as exc:                            # noqa: BLE001
        log(f"updater: download failed ({exc})")
        return ("New terms were available but the download did not "
                "finish. Your terms are unchanged; it will try again "
                "next time Anki starts.")

    got = hashlib.sha256(body).hexdigest()
    if got != want:
        log(f"updater: checksum mismatch (got {got[:12]}, "
            f"expected {str(want)[:12]}); discarding")
        return ("The downloaded terms did not match their checksum, so "
                "they were discarded rather than used. Your existing "
                "terms are untouched. If this repeats, report it.")
    if manifest.get("bytes") not in (None, len(body)):
        log("updater: length mismatch; discarding")
        return ("The downloaded terms were the wrong size, so they were "
                "discarded. Your existing terms are untouched. If "
                "this repeats, report it.")

    try:
        lib = json.loads(body.decode("utf-8"))
    except Exception as exc:                            # noqa: BLE001
        log(f"updater: payload is not JSON ({exc}); discarding")
        return ("The downloaded terms could not be read, so they were "
                "discarded. Your existing terms are untouched. If "
                "this repeats, report it.")

    why = _library._validate(lib)
    if why:
        log(f"updater: payload rejected - {why}; discarding")
        return ("The downloaded terms were not in a shape this version "
                "understands, so they were discarded. Your existing "
                "terms are untouched.")

    # The payload has to be the version the manifest advertised.
    #
    # Nothing downstream re-reads this. `_library._load` picks whichever
    # of the bundled and downloaded copies carries the newer
    # `content_version`, so a payload stamped older than the bundled
    # library is written to disk, ignored at every launch, and leaves
    # `CONTENT_VERSION` where it was - which is exactly the value the
    # check at the top of this function compares the manifest against.
    # The result is a download on every single launch, each one ending
    # with a message telling the user to restart to apply an update
    # that can never apply.
    #
    # `tools/publish_content.sh` asserts the two agree, so a mismatch
    # cannot come from a normal publish; it means a stale file behind
    # the manifest URL, a half-finished upload, or a host that is not
    # ours. Those are the cases the rest of this module is written
    # against, and the answer is the same one the checksum branch
    # gives: keep what works.
    payload_version = lib.get("content_version")
    if payload_version != remote:
        log(f"updater: manifest advertised content {remote!r} but the "
            f"payload is {payload_version!r}; discarding")
        return ("The update server described the terms it sent "
                "incorrectly, so they were discarded rather than used. "
                "Your existing terms are untouched. If this repeats, "
                "report it.")

    try:
        _write_atomically(_library.USER_COPY, body)
    except Exception as exc:                            # noqa: BLE001
        log(f"updater: could not write library ({exc})")
        return ("New terms downloaded but could not be saved - check that "
                "Anki can write to its add-on folder, and that the "
                "disk is not full.")

    log(f"updater: content {remote} downloaded; active at next restart")
    return f"Downloaded {remote}. Restart Anki to apply."


# The one outcome that needs no telling. Everything else `check` can
# return is either a failure or a change the reader would want to know
# about, and all of them used to go to the log alone.
QUIET_RESULT = "Up to date."


def check_in_background(manifest_url: str = DEFAULT_MANIFEST_URL,
                        on_result=None) -> None:
    """Start the check. Returns immediately; never raises.

    `on_result` is called with the outcome string, on the UI thread. It
    is optional because the check must still work with nowhere to
    report to, but the launch path passes one: without it a user who is
    offline, behind a proxy, or being handed a payload that fails its
    checksum saw nothing at all, and simply stopped receiving content.
    """
    def _run():
        result = check(manifest_url)
        if on_result is None:
            return
        try:
            from aqt import mw
            mw.taskman.run_on_main(lambda: on_result(result))
        except Exception as exc:                        # noqa: BLE001
            log(f"updater: could not report result ({exc})")

    t = threading.Thread(target=_run,
                         name="theankidote-content-update", daemon=True)
    t.start()
