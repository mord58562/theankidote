# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""Tiny logging shim - one place to gate addon-wide debug output.

Used everywhere we previously wrote `print(f"[TheAnkiDote] ...")` or
swallowed exceptions with `except Exception: pass`.  Centralising it
means:

  * Debug output can be silenced for an AnkiWeb release by flipping
    `_DEBUG` to False (or via the addon config flag `debug`) without
    chasing prints across every file.
  * When a user sends in a stack trace we can ask them to set
    `debug: true` in the config and reproduce - no addon rebuild needed.

Intentionally minimal - no rotating files, no JSON, no levels beyond
debug/warn/error.  This is an Anki addon, not a server.
"""

import sys
import traceback
from typing import Optional


_TAG = "[TheAnkiDote]"


def _debug_enabled() -> bool:
    # Defer the import so this module can be imported before _config
    # has its mw reference (during early addon load).
    try:
        from . import _config
        return bool(_config.get("debug"))
    except Exception:
        return False


def debug(msg: str) -> None:
    """Print an informational message when the user has set
    `debug: true` in the addon config.  Silent otherwise."""
    if _debug_enabled():
        print(f"{_TAG} {msg}")


def warn(msg: str) -> None:
    """Always-visible warning.  Goes to stderr so it shows up in
    Anki's debug console regardless of the debug flag."""
    print(f"{_TAG} WARN: {msg}", file=sys.stderr)


def error(context: str, exc: Optional[BaseException] = None) -> None:
    """Always-visible error.  When the optional exception is provided,
    its traceback is included; this is what every former
    `try/except Exception: pass` site should call instead.

    We never re-raise - the addon must not crash Anki's review loop
    just because a non-critical sidebar feature failed.
    """
    if exc is None:
        print(f"{_TAG} ERROR: {context}", file=sys.stderr)
        return
    print(f"{_TAG} ERROR: {context}: {exc}", file=sys.stderr)
    if _debug_enabled():
        traceback.print_exc(file=sys.stderr)
