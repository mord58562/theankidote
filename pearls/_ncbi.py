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

_CACHE_VERSION = 2   # bump to discard caches built by an older resolver
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
            if int(data.get("__version", 0)) != _CACHE_VERSION:
                # Entries from before the chapter-title fix can point at
                # an unrelated article; there is no way to tell which,
                # so discard the lot rather than keep serving them.
                _log.diag("nbk cache from an older resolver - discarding")
                _cache = {}
                return
            _cache = {k: v for k, v in data.items()
                      if isinstance(v, str) and k != "__version"}
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
            json.dump(dict(_cache, __version=_CACHE_VERSION), fh,
                  ensure_ascii=False, indent=0, sort_keys=True)
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
    # Search titles only, and resolve to the parent chapter.  NCBI's book
    # index is section-level: an unrestricted search returns records whose
    # own title is a heading such as "Morphology", belonging to a chapter
    # that may have nothing to do with the term.
    q = quote_plus(f'"{term}"[Title] AND statpearls[book]')
    try:
        raw = _get(f"{_EUTILS}esearch.fcgi?db=books&retmode=json&retmax=20&term={q}")
        ids = (json.loads(raw).get("esearchresult") or {}).get("idlist") or []
    except Exception as exc:
        _log.diag(f"esearch failed for {term!r}: {exc}")
        return None
    if not ids:
        _log.diag(f"esearch: no chapter titled {term!r}")
        return None
    try:
        raw = _get(f"{_EUTILS}esummary.fcgi?db=books&retmode=json&id={','.join(ids[:20])}")
        result = json.loads(raw).get("result") or {}
    except Exception as exc:
        _log.diag(f"esummary failed for {term!r}: {exc}")
        return None

    best = None
    for i in ids[:20]:
        doc = result.get(i)
        if not isinstance(doc, dict):
            continue
        acc = (doc.get("chapteraccessionid") or doc.get("accessionid") or "").strip()
        if not re.fullmatch(r"NBK\d+", acc):
            continue
        info = doc.get("bookinfo") or ""
        m = re.search(r'type="chapter"[^>]*>\s*<Title>(.*?)</Title>', info)
        ctitle = m.group(1) if m else (doc.get("title") or "" if doc.get("rtype") == "chapter" else "")
        sc = _score(ctitle, term)
        if sc is None:
            continue
        if best is None or sc < best[0]:
            best = (sc, acc, ctitle)
    if best is None:
        _log.diag(f"no chapter title matched {term!r}")
        return None
    _log.diag(f"resolved {term!r} -> {best[1]} {best[2]!r}")
    return best[1]


_NORM_RE = re.compile(r"[^a-z0-9 ]+")


def _norm(t: str) -> str:
    return _NORM_RE.sub(" ", str(t or "").lower()).replace("  ", " ").strip()


def _score(chapter_title: str, term: str):
    """Lower is better; None rejects.

    Only a title that *is* the condition is accepted, optionally with a
    trailing synonym in brackets.  Looser matching produced links that
    looked right and were not - "Stroke" resolving to "Heat Stroke",
    "Sepsis" to "Neonatal Sepsis", "Hypertension" to "Portal
    Hypertension".  Nothing on the opened page signals the mismatch, so
    a search page is the safer failure.
    """
    ct, t = _norm(chapter_title), _norm(term)
    if not ct or not t:
        return None
    if "archiv" in ct:
        return None
    if ct == t:
        return (0, len(ct))
    if re.match(r"^\s*" + re.escape(term) + r"\s*\(", chapter_title or "", re.I):
        return (1, len(ct))
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
# Popup section label -> candidate StatPearls headings, matched by text
# against the article's own h1-h4 (see `_SCROLL_JS` in _panel_pearls.py),
# longest-intent-first within each list. Prefix matching means
# "Treatment" finds the real heading "Treatment / Management".
#
# StatPearls chapters are built from a fixed template, so the target set
# is small and stable: Continuing Education Activity, Introduction,
# Etiology, Epidemiology, Pathophysiology, Histopathology, History and
# Physical, Evaluation, Treatment / Management, Differential Diagnosis,
# Staging, Prognosis, Complications, Consultations, Deterrence and
# Patient Education, Pearls and Other Issues, Enhancing Healthcare Team
# Outcomes. Drug chapters add Mechanism of Action, Administration,
# Adverse Effects, Contraindications, Monitoring, Toxicity.
#
# Every label registered in `_SECTION_LABELS` (web/marker.js) that has a
# genuine counterpart above belongs here, because a label absent from
# this map is a click that silently opens the article at the top. That
# was the state of things through preview 11: "Clinical features",
# "Note" and "Red flags" alone accounted for 124 of 138 dead clicks,
# 47% of every section label rendered.
#
# Labels with no honest counterpart are deliberately absent - see
# `_SECTION_LINKABLE` in web/marker.js, which reads this map's keys and
# renders unmapped labels as plain headings rather than dead controls.
SECTION_MAP = {
    # ── history and examination ──
    "sx": ["History and Physical", "Clinical"],
    "hx": ["History and Physical"],
    "signs": ["History and Physical"],
    "symptoms": ["History and Physical"],
    "presentation": ["History and Physical"],
    "examination": ["History and Physical"],
    "features": ["History and Physical"],
    "clinical features": ["History and Physical"],
    # Organ-specific spillover sections are still the article's
    # history-and-examination material.
    "extra-articular": ["History and Physical"],
    "extrahepatic": ["History and Physical"],
    "extraintestinal": ["History and Physical"],
    # ── definition and mechanism ──
    "definition": ["Introduction"],
    "mechanism": ["Pathophysiology", "Mechanism of Action"],
    "mechanisms": ["Pathophysiology", "Mechanism of Action"],
    "pathophysiology": ["Pathophysiology"],
    "pathology": ["Histopathology", "Pathophysiology"],
    "phases": ["Pathophysiology"],
    # ── cause ──
    "aetiology": ["Etiology"],
    "etiology": ["Etiology"],
    "causes": ["Etiology"],
    "risk": ["Etiology", "Epidemiology"],
    "risk factors": ["Etiology", "Epidemiology"],
    "triggers": ["Etiology"],
    "associations": ["Etiology"],
    "genetics": ["Etiology"],
    "epidemiology": ["Epidemiology"],
    # ── investigation ──
    "ix": ["Evaluation", "Diagnosis"],
    "investigations": ["Evaluation", "Diagnosis"],
    "workup": ["Evaluation"],
    "dx": ["Evaluation", "Diagnosis"],
    "diagnosis": ["Evaluation", "Diagnosis"],
    "criteria": ["Evaluation"],
    "classification": ["Evaluation"],
    "types": ["Evaluation"],
    "subtypes": ["Evaluation"],
    "variants": ["Evaluation"],
    "staging": ["Staging", "Evaluation"],
    "stages": ["History and Physical", "Staging"],
    "screening": ["Evaluation", "Deterrence and Patient Education"],
    # ── differential ──
    "differential": ["Differential Diagnosis"],
    "ddx": ["Differential Diagnosis"],
    # ── management ──
    "mx": ["Treatment", "Management"],
    "management": ["Treatment", "Management"],
    "treatment": ["Treatment", "Management"],
    "tx": ["Treatment", "Management"],
    "rx": ["Treatment", "Management"],
    "follow-up": ["Treatment", "Management"],
    # Drug chapters carry a real Monitoring heading; disease chapters do
    # not, so fall through to Treatment / Management there.
    "monitoring": ["Monitoring", "Treatment", "Management"],
    "prevention": ["Deterrence and Patient Education", "Etiology"],
    "secondary prevention": ["Treatment", "Management",
                             "Deterrence and Patient Education"],
    # ── outcome ──
    "complications": ["Complications"],
    "prognosis": ["Prognosis"],
    "px": ["Prognosis"],
    # ── drug-shaped ──
    "se": ["Adverse Effects", "Complications"],
    "adverse effects": ["Adverse Effects", "Complications"],
    "ci": ["Contraindications"],
    "contraindications": ["Contraindications"],
    "cautions": ["Contraindications", "Adverse Effects"],
    # StatPearls has no interactions heading; DrugBank does.
    "interactions": ["Interactions", "Adverse Effects"],
    # DrugBank titles this section in the singular, StatPearls in the
    # plural, and the same popup label has to reach both.
    "indications": ["Indications", "Indication"],
    "uses": ["Indications", "Indication"],
    "moa": ["Mechanism of Action"],
    "pk": ["Pharmacokinetics", "Absorption", "Mechanism of Action"],
    "pd": ["Pharmacodynamics", "Mechanism of Action"],
    "dose": ["Administration"],
    "dosing": ["Administration"],
    "route": ["Administration"],
    "metabolism": ["Metabolism"],
    "half-life": ["Half-life"],
    # ── editorial ──
    # "Pearls" has a genuine target; "Note", "Notes", "Red flags",
    # "Mnemonic", "Key point", "Exam tip", "PBS" and "Australian notes"
    # do not, and are intentionally left out. They are this add-on's own
    # synthesis - a discriminating fact, a time-critical warning, an
    # Australian prescribing note - drawn from across the article rather
    # than from one heading, and "Pearls and Other Issues" is not even
    # present in every chapter. Pointing them somewhere plausible would
    # be the heading-level version of inventing an NBK accession.
    "pearls": ["Pearls and Other Issues"],
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
