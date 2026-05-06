# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.

"""Async StatPearls searcher via PubMed API.

PubMed indexes every StatPearls chapter as a citable article with its
full chapter title.  The esummary articleids list contains a
'bookaccession' entry (e.g. NBK430742) which we turn into the NCBI
books URL for the side panel.

Two-step flow:  esearch (get PMIDs)  →  esummary (get titles + NBK URLs)
Results cached by note GUID to avoid redundant requests.
"""
import html as _html
import json
import re
from urllib.parse import quote_plus

try:
    from PyQt6.QtCore import QObject, QTimer, QUrl, pyqtSignal
    from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest
except ImportError:
    from PyQt5.QtCore import QObject, QTimer, QUrl, pyqtSignal
    from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest

from .. import _config

_NCBI      = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
_EMAIL     = "theankidote@noreply.example.com"
_UA        = b"TheAnkiDote/1.0"
_CACHE_MAX = 30

_STOPWORDS = frozenset({
    "what","is","are","the","a","an","of","for","in","on","at","to",
    "with","how","why","when","where","which","who","be","was","were",
    "has","have","had","do","does","did","will","would","could","should",
    "can","this","that","these","those","and","or","but","not","if",
    "then","than","so","as","it","its","he","she","they","we","you",
    "from","by","about","used","most","common","first","line","versus",
    "describe","explain","define","name","list","cause","causes",
    "mechanism","treatment","management","diagnosis","patient",
    "occurs","following","associated","often","seen","found","also",
    "their","your","more","less","such","each","over","under","type",
    "types","class","classes","drug","drugs","agent","agents",
})


_WORD4_RE        = re.compile(r"\b[A-Za-z]{4,}\b")
_PUBMED_ARTICLE  = re.compile(r"<PubmedArticle\b[^>]*>(.*?)</PubmedArticle>", re.S)
_PMID_RE         = re.compile(r"<PMID[^>]*>(\d+)</PMID>")
# Capture the optional NlmCategory/Label so we can drop methodology sections.
_ABSTRACT_RE     = re.compile(
    r'<AbstractText\b([^>]*)>(.*?)</AbstractText>', re.S
)
_LABEL_RE        = re.compile(r'(?:NlmCategory|Label)="([^"]+)"', re.I)
_INNER_TAG_RE    = re.compile(r"<[^>]+>")
_WS_RE           = re.compile(r"\s+")
_SENTENCE_RE     = re.compile(r"(?<=[.!?])\s+")
# Boilerplate phrases that pad StatPearls / NCBI abstracts with non-clinical
# medical-education filler.  Sentences containing any of these are dropped so
# the popup focuses on bedside-relevant content (definition, presentation,
# diagnosis, treatment, complications).
_BOILERPLATE_RE  = re.compile(
    r"(?:"
    r"this activity (?:reviews?|outlines?|describes?|illustrates?|examines?)"
    r"|this article (?:reviews?|describes?|outlines?)"
    r"|this chapter"
    r"|(?:purpose|objective|aim)s? of this (?:article|activity|review|chapter|study)"
    r"|interprofessional (?:team|approach|care)"
    r"|healthcare (?:provider|professional|team|workers?)"
    r"|highlights? the role"
    r"|role of (?:the )?(?:interprofessional |healthcare )?team"
    r"|team[- ]based (?:approach|care)"
    r"|improve (?:patient )?outcomes? for"
    r"|clinicians? (?:should|must|need)"
    r")",
    re.IGNORECASE,
)
# Drop these structured-abstract sections - they describe methodology, not
# clinical content useful in a 1-line tooltip.
_SKIP_LABELS = frozenset({
    "methods", "method", "design", "study design", "setting", "participants",
    "intervention", "interventions", "main outcome measures", "data sources",
    "study selection", "data extraction", "data synthesis", "limitations",
    "funding", "funders", "trial registration",
})


def _clean_query(raw: str) -> list:
    """Extract meaningful medical terms from raw card text."""
    return [w for w in _WORD4_RE.findall(raw)
            if w.lower() not in _STOPWORDS][:8]


class StatPearlsSearcher(QObject):
    results_ready  = pyqtSignal(list, int)
    search_started = pyqtSignal()
    search_failed  = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._nam          = QNetworkAccessManager(self)
        self._req_id       = 0
        self._active_id    = 0
        self._pending_q    = ""
        self._pending_guid = ""
        self._cache: dict  = {}
        self._timer        = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._fire)

    # -----------------------------------------------------------------------
    # Public
    # -----------------------------------------------------------------------

    def search(self, query: str, note_guid: str = "") -> None:
        """Debounced search - fires shortly after the last call."""
        self._pending_q    = query.strip()
        self._pending_guid = note_guid
        self._timer.start(100)

    def cached(self, note_guid: str):
        return self._cache.get(note_guid)

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def _get(self, url: str):
        req = QNetworkRequest(QUrl(url))
        req.setRawHeader(b"User-Agent", _UA)
        return self._nam.get(req)

    def _fire(self):
        q = self._pending_q
        if not q:
            return

        clean = _clean_query(q)
        if not clean:
            clean = q.split()[:5]

        self._req_id += 1
        req_id = self._req_id
        self._active_id = req_id
        self.search_started.emit()

        max_r = int(_config.get("maxResults") or 8)
        term  = quote_plus(" ".join(clean))

        # PubMed indexes every StatPearls chapter with full title + NBK accession
        url = (
            f"{_NCBI}/esearch.fcgi"
            f"?db=pubmed"
            f"&term={term}+AND+StatPearls%5BPublisher%5D"
            f"&retmode=json&retmax={max_r}"
            f"&email={_EMAIL}"
        )
        reply = self._get(url)
        reply.finished.connect(lambda: self._on_esearch(reply, req_id))

    def _on_esearch(self, reply, req_id: int):
        try:
            if req_id != self._active_id:
                return
            raw  = bytes(reply.readAll()).decode("utf-8", errors="replace")
            data = json.loads(raw)
            ids  = data.get("esearchresult", {}).get("idlist", [])
        except Exception as exc:
            self.search_failed.emit(str(exc))
            return
        finally:
            reply.deleteLater()

        if not ids:
            self._emit([], req_id)
            return

        url = (
            f"{_NCBI}/esummary.fcgi"
            f"?db=pubmed&id={','.join(ids)}"
            f"&retmode=json&email={_EMAIL}"
        )
        reply2 = self._get(url)
        reply2.finished.connect(lambda: self._on_esummary(reply2, req_id))

    def _on_esummary(self, reply, req_id: int):
        try:
            if req_id != self._active_id:
                return
            raw  = bytes(reply.readAll()).decode("utf-8", errors="replace")
            data = json.loads(raw)
            uids = data.get("result", {}).get("uids", [])
        except Exception as exc:
            self.search_failed.emit(str(exc))
            return
        finally:
            reply.deleteLater()

        results = []
        for uid in uids:
            info  = data["result"].get(uid, {})
            title = info.get("title", "").strip().rstrip(".")
            if not title:
                continue

            title = _html.unescape(title)

            # Extract NBK accession → canonical NCBI books URL
            nbk_url = None
            for aid in info.get("articleids", []):
                if isinstance(aid, dict) and aid.get("idtype") == "bookaccession":
                    nbk_url = f"https://www.ncbi.nlm.nih.gov/books/{aid['value']}/"
                    break
            if nbk_url is None:
                nbk_url = f"https://pubmed.ncbi.nlm.nih.gov/{uid}/"

            results.append({"id": uid, "title": title, "url": nbk_url, "summary": ""})

        # Show the article list NOW with empty summaries so the panel
        # populates as soon as titles are known.  Summaries arrive in a
        # second pass via efetch.
        self._emit(results, req_id)

        if not results:
            return

        ids_for_fetch = [r["id"] for r in results]
        url = (
            f"{_NCBI}/efetch.fcgi"
            f"?db=pubmed&id={','.join(ids_for_fetch)}"
            f"&rettype=abstract&retmode=xml"
            f"&email={_EMAIL}"
        )
        reply3 = self._get(url)
        reply3.finished.connect(lambda: self._on_efetch(reply3, req_id, results))

    def _on_efetch(self, reply, req_id: int, results: list):
        # NOTE: deliberately do NOT bail out for stale searches.  `results`
        # is the same list that was already cached by guid in _on_esummary,
        # so mutating it here populates summaries for the original card
        # even if the user has moved to a different card mid-fetch.
        try:
            raw = bytes(reply.readAll()).decode("utf-8", errors="replace")
        except Exception:
            reply.deleteLater()
            return
        reply.deleteLater()

        # Parse PubmedArticle blocks → map PMID → clinically-focused summary.
        # Structured abstracts label sections (Background, Methods, Results,
        # Conclusions, etc.); prefer clinical sections, but always fall back
        # to the full abstract if filtering would otherwise leave nothing.
        try:
            abstracts = {}
            for art in _PUBMED_ARTICLE.findall(raw):
                pmid_m = _PMID_RE.search(art)
                if not pmid_m:
                    continue
                pieces, all_pieces = [], []
                for attrs, body in _ABSTRACT_RE.findall(art):
                    cleaned = _INNER_TAG_RE.sub("", body)
                    all_pieces.append(cleaned)
                    label_m = _LABEL_RE.search(attrs)
                    label = (label_m.group(1).strip().lower()
                             if label_m else "")
                    if label not in _SKIP_LABELS:
                        pieces.append(cleaned)
                # Fall back to ALL sections if label-filtering removed
                # everything (e.g. abstract is only Methods + Funding).
                if not pieces:
                    pieces = all_pieces
                if not pieces:
                    continue
                joined = _html.unescape(_WS_RE.sub(" ", " ".join(pieces)).strip())
                # Drop boilerplate sentences; fall back to original if the
                # filter would empty the summary.
                sentences = _SENTENCE_RE.split(joined)
                clinical  = [s for s in sentences if s and not _BOILERPLATE_RE.search(s)]
                if clinical:
                    joined = " ".join(clinical)
                if len(joined) > 420:
                    joined = joined[:417].rstrip() + "…"
                abstracts[pmid_m.group(1)] = joined
            for r in results:
                if r["id"] in abstracts:
                    r["summary"] = abstracts[r["id"]]
        except Exception as exc:
            print(f"[TheAnkiDote] efetch parse error: {exc}")
            return

        # Only push to subscribers if this is still the active search -
        # otherwise we'd risk caching these results under a different
        # card's guid via _emit's reliance on self._pending_guid.
        if req_id == self._active_id:
            self._emit(results, req_id)

    def _emit(self, results: list, req_id: int):
        guid = self._pending_guid
        if guid:
            self._cache[guid] = results
            if len(self._cache) > _CACHE_MAX:
                self._cache.pop(next(iter(self._cache)))
        self.results_ready.emit(results, req_id)
