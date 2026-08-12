# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""Resolve a condition name to its StatPearls chapter on NCBI Bookshelf.

Why this exists
---------------
Every condition entry falls back to an in-book *search* URL
(`/books/n/statpearls/?term=...`), which lands the reader on a results
list rather than the chapter.  That turns a lookup into two clicks plus
a page of NCBI search UI, which is enough friction that the sidebar goes
unused.  Resolving the term to an NBK accession once and caching it
makes "Open article" land in the article.

Design constraints
------------------
* Never block the UI thread.  Resolution runs through Anki's task
  manager; the caller gets a callback on the main thread.
* Never leave the user staring at nothing.  The caller loads the search
  URL immediately and swaps to the chapter if and when resolution wins,
  so a slow or unreachable NCBI degrades to exactly today's behaviour.
* Cache aggressively.  Chapter accessions are stable for long periods,
  and the cache is the difference between "instant" and "one request per
  term, forever".
* Be a good API citizen.  NCBI asks for <=3 requests/second without an
  API key; requests are serialised and rate-limited below that.
"""

import json
import os
import re
import threading
import time
from urllib.parse import quote_plus
from urllib.request import urlopen, Request

from .. import _log

_EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
_BOOK_URL = "https://www.ncbi.nlm.nih.gov/books/{acc}/"
_TIMEOUT = 8
_UA = "TheAnkiDote/1.2 (Anki add-on; +https://github.com/mord58562/theankidote)"

_ADDON_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CACHE_PATH = os.path.join(_ADDON_DIR, "user_files", "nbk_cache.json")

# NCBI: no more than 3 requests/second without an API key.  One in-flight
# request at a time plus a floor on the gap keeps us well inside that.
_MIN_GAP = 0.4
_net_lock = threading.Lock()
_last_call = [0.0]

_cache: dict = {}
_cache_loaded = False
_cache_dirty = False
# Terms that resolved to nothing: remembered for the session so a miss
# doesn't re-query on every hover, but not persisted - StatPearls adds
# chapters, and a permanent negative cache would never notice.
_misses: set = set()


# ── cache ────────────────────────────────────────────────────────────
def _load_cache() -> None:
    global _cache, _cache_loaded
    if _cache_loaded:
        return
    _cache_loaded = True
    try:
        with open(_CACHE_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            _cache = {k: v for k, v in data.items() if isinstance(v, str)}
    except FileNotFoundError:
        _cache = {}
    except Exception as exc:
        _log.debug(f"nbk cache unreadable, starting empty: {exc}")
        _cache = {}


def _save_cache() -> None:
    global _cache_dirty
    if not _cache_dirty:
        return
    try:
        os.makedirs(os.path.dirname(_CACHE_PATH), exist_ok=True)
        tmp = _CACHE_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(_cache, fh, ensure_ascii=False, indent=0, sort_keys=True)
        os.replace(tmp, _CACHE_PATH)
        _cache_dirty = False
    except Exception as exc:
        _log.error("nbk cache write", exc)


def cached(term: str) -> "str | None":
    """Accession for `term` if already known, else None.  Cheap and safe
    to call on the UI thread."""
    _load_cache()
    return _cache.get(_key(term))


def _key(term: str) -> str:
    return re.sub(r"\s+", " ", (term or "").strip().lower())


def _remember(term: str, acc: str) -> None:
    global _cache_dirty
    _load_cache()
    k = _key(term)
    if k and acc and _cache.get(k) != acc:
        _cache[k] = acc
        _cache_dirty = True
        _save_cache()


# ── network ──────────────────────────────────────────────────────────
def _get(url: str) -> str:
    with _net_lock:
        gap = time.time() - _last_call[0]
        if gap < _MIN_GAP:
            time.sleep(_MIN_GAP - gap)
        _last_call[0] = time.time()
        req = Request(url, headers={"User-Agent": _UA})
        with urlopen(req, timeout=_TIMEOUT) as resp:
            return resp.read().decode("utf-8", "replace")


def _resolve_blocking(term: str) -> "str | None":
    """ESearch the books database for the StatPearls chapter, then
    ESummary the top hit for its NBK accession.  Returns e.g. 'NBK430685'."""
    q = quote_plus(f'"{term}" AND statpearls[book]')
    try:
        raw = _get(f"{_EUTILS}esearch.fcgi?db=books&retmode=json&retmax=1&term={q}")
        ids = (json.loads(raw).get("esearchresult") or {}).get("idlist") or []
    except Exception as exc:
        _log.debug(f"nbk esearch failed for {term!r}: {exc}")
        return None
    if not ids:
        return None
    try:
        raw = _get(f"{_EUTILS}esummary.fcgi?db=books&retmode=json&id={ids[0]}")
        result = json.loads(raw).get("result") or {}
        doc = result.get(ids[0]) or {}
    except Exception as exc:
        _log.debug(f"nbk esummary failed for {term!r}: {exc}")
        return None
    # The accession lives under different keys across Bookshelf record
    # shapes; take the first NBK-looking value rather than guessing one.
    for k in ("ancestortitle", "bookaccession", "accession", "reportnumber", "uid"):
        v = doc.get(k)
        if isinstance(v, str) and re.fullmatch(r"NBK\d+", v.strip()):
            return v.strip()
    for v in doc.values():
        if isinstance(v, str):
            m = re.fullmatch(r"NBK\d+", v.strip())
            if m:
                return v.strip()
    return None


def article_url(acc: str) -> str:
    return _BOOK_URL.format(acc=acc)


def resolve_async(term: str, on_done) -> None:
    """Resolve `term` off the UI thread; call `on_done(accession_or_None)`
    on the main thread.  Silent no-op if the term already missed this
    session, so repeated hovers on an uncovered term cost nothing."""
    if not term or _key(term) in _misses:
        on_done(None)
        return
    hit = cached(term)
    if hit:
        on_done(hit)
        return

    def task():
        return _resolve_blocking(term)

    def done(fut):
        acc = None
        try:
            acc = fut.result()
        except Exception as exc:
            _log.debug(f"nbk resolve task failed for {term!r}: {exc}")
        if acc:
            _remember(term, acc)
        else:
            _misses.add(_key(term))
        try:
            on_done(acc)
        except Exception as exc:
            _log.error("nbk on_done", exc)

    try:
        from aqt import mw
        mw.taskman.run_in_background(task, done)
    except Exception as exc:
        # No task manager (tests, or a stripped Anki): resolve inline
        # rather than failing outright.
        _log.debug(f"taskman unavailable, resolving inline: {exc}")
        acc = _resolve_blocking(term)
        if acc:
            _remember(term, acc)
        else:
            _misses.add(_key(term))
        on_done(acc)


# ── section targeting ────────────────────────────────────────────────
# The popup's section labels are Australian/abbreviated; StatPearls uses
# fixed US chapter headings.  Mapping them lets a click on "Mx" land on
# the Treatment section rather than the top of a long chapter.
SECTION_MAP = {
    "sx": ["History and Physical", "Clinical"],
    "signs": ["History and Physical"],
    "presentation": ["History and Physical"],
    "examination": ["History and Physical"],
    "features": ["History and Physical"],
    "ix": ["Evaluation", "Diagnosis"],
    "investigations": ["Evaluation", "Diagnosis"],
    "workup": ["Evaluation"],
    "dx": ["Evaluation", "Diagnosis"],
    "diagnosis": ["Evaluation", "Diagnosis"],
    "criteria": ["Evaluation"],
    "mx": ["Treatment", "Management"],
    "management": ["Treatment", "Management"],
    "treatment": ["Treatment", "Management"],
    "tx": ["Treatment", "Management"],
    "rx": ["Treatment", "Management"],
    "aetiology": ["Etiology"],
    "etiology": ["Etiology"],
    "causes": ["Etiology"],
    "risk": ["Etiology", "Epidemiology"],
    "pathophysiology": ["Pathophysiology"],
    "epidemiology": ["Epidemiology"],
    "complications": ["Complications"],
    "prognosis": ["Prognosis"],
    "staging": ["Staging", "Evaluation"],
    "classification": ["Evaluation"],
    "differential": ["Differential Diagnosis"],
    "se": ["Adverse Effects", "Complications"],
    "ci": ["Contraindications"],
    "contraindications": ["Contraindications"],
    "indications": ["Indications"],
    "moa": ["Mechanism of Action"],
    "genetics": ["Etiology"],
    "types": ["Evaluation"],
    "subtypes": ["Evaluation"],
}


def headings_for(label: str) -> list:
    """StatPearls heading candidates for a popup section label."""
    return SECTION_MAP.get((label or "").strip().rstrip(":").lower(), [])


# ── generic URL cache (StatPearls chapters and DrugBank drug pages) ──
def remember_url(term: str, url: str) -> None:
    """Cache the canonical URL a search page resolved to.

    Used for DrugBank, which has no public lookup API, so the only
    reliable resolver is the site's own search: follow it once, keep the
    answer.  Stored under a `url:` prefix to keep it clearly distinct
    from bare NBK accessions.
    """
    global _cache_dirty
    _load_cache()
    k = "url:" + _key(term)
    if k and url and _cache.get(k) != url:
        _cache[k] = url
        _cache_dirty = True
        _save_cache()


def cached_url(term: str) -> "str | None":
    _load_cache()
    return _cache.get("url:" + _key(term))
