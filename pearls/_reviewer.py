# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.

"""Reviewer integration - mirrors AMBOSS ReviewerCardPhraseUpdater.

Two-phase highlighting:
  Phase 1 (synchronous): card_will_show hook injects sp-mark spans + CSS
    directly into the card HTML string if results are already cached.
    This is guaranteed to render - no timing/CSP issues.
  Phase 2 (async fallback): when NCBI results arrive for the first time,
    web.eval() injects the marker code into the live DOM.
"""
import json
import re
from html.parser import HTMLParser
from typing import Any, Tuple

from aqt import mw, gui_hooks

from .. import _config, _log
from . import _acronyms, _drugs, _conditions
from ._searcher import _STOPWORDS


# ── User-defined custom terms ─────────────────────────────────────────
#
# `customTerms` config key is a string holding a JSON array.  Each entry
# is a {title, summary, url, case_sensitive?} dict.  Parsed lazily on
# first read and cached - if the user updates the config we re-parse
# on the next request.

_custom_terms_cache: list = []
_custom_terms_raw: "str | None" = "<unset>"  # sentinel different from None


def _custom_terms() -> list:
    global _custom_terms_cache, _custom_terms_raw
    raw = _config.get("customTerms")
    if raw == _custom_terms_raw:
        return _custom_terms_cache
    _custom_terms_raw = raw
    _custom_terms_cache = []
    if not raw or not isinstance(raw, str):
        return _custom_terms_cache
    try:
        parsed = json.loads(raw)
    except Exception as exc:
        _log.warn(f"customTerms JSON parse failed: {exc}")
        return _custom_terms_cache
    if not isinstance(parsed, list):
        return _custom_terms_cache
    out = []
    for entry in parsed:
        if not isinstance(entry, dict):
            continue
        title = (entry.get("title") or "").strip()
        url = (entry.get("url") or "").strip()
        if not title or not url:
            continue
        if not (url.startswith("http://") or url.startswith("https://")):
            continue
        out.append({
            "title": title,
            "_article": entry.get("article") or title,
            "url": url,
            "summary": (entry.get("summary") or "").strip(),
            "source": entry.get("source") or "custom",
            "case_sensitive": bool(entry.get("case_sensitive")),
        })
    _custom_terms_cache = out
    return out

try:
    from aqt.reviewer import Reviewer
except Exception:
    Reviewer = None  # type: ignore[assignment,misc]

_ADDON_PKG  = __name__.split(".")[0]
_SCRIPT_URL = f"/_addons/{_ADDON_PKG}/web/marker.js"

# ── module-level state ────────────────────────────────────────────────────────

_on_answer    = False
_panel_ref    = None
_current_card = None  # set on show_question/show_answer for Phase 2 use
_prev_card_id: "int | None" = None  # for detecting card progression vs flip


def set_panel(panel) -> None:
    global _panel_ref
    _panel_ref = panel


# ── card text extraction ──────────────────────────────────────────────────────
# `_STOPWORDS` is imported from _searcher to keep the list in one place.


class _Stripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self._buf = []
    def handle_data(self, d):
        self._buf.append(d)
    def result(self):
        return " ".join(self._buf)


_WS_RE      = re.compile(r"\s+")
_TAG_RE     = re.compile(r"<[^>]+>")
_WORD4_RE   = re.compile(r"\b[A-Za-z]{4,}\b")
_TITLE_WORD = re.compile(r"\b[A-Za-z][A-Za-z\-]{4,}\b")
# Matches any sp-mark span we previously injected - used for self-healing.
_SP_MARK_RE = re.compile(r'<span class="sp-mark"[^>]*>(.*?)</span>', re.DOTALL)


def _strip_sp_marks(html: str) -> str:
    """Remove any existing sp-mark spans, keeping their text content."""
    return _SP_MARK_RE.sub(r'\1', html)


def _strip_html(html: str) -> str:
    s = _Stripper()
    try:
        s.feed(html)
        return _WS_RE.sub(" ", s.result()).strip()
    except Exception:
        return _TAG_RE.sub("", html).strip()


def _card_text(card) -> str:
    """Plain-text concatenation of all note fields, stripped of HTML.
    Cached on the card object so multiple consumers (query builder, acronym
    resolver) don't repeatedly re-strip."""
    cached = getattr(card, "_ap_text", None)
    if cached is not None:
        return cached
    try:
        text = " ".join(_strip_html(v) for v in card.note().values() if v.strip())
    except Exception:
        text = ""
    try:
        card._ap_text = text
    except Exception:
        pass
    return text


def _card_query(card) -> Tuple[str, str]:
    try:
        note = card.note()
        tag_words = []
        for tag in note.tags:
            words = tag.replace("::", " ").replace("_", " ").replace("-", " ").split()
            tag_words.extend(
                w for w in words
                if len(w) >= 4 and w.lower() not in _STOPWORDS and w.isalpha()
            )
        if len(tag_words) >= 2:
            return " ".join(tag_words[:8]), note.guid
        combined = _card_text(card)
        words = [
            w for w in _WORD4_RE.findall(combined)
            if w.lower() not in _STOPWORDS
        ][:8]
        return " ".join(words), note.guid
    except Exception:
        return "", ""


def _term_search_url(term: str) -> str:
    """In-book StatPearls search URL.  Targets the StatPearls book
    namespace (`/books/n/statpearls/`) so the term lands in the
    'Search this book' input rather than the Bookshelf-wide search bar."""
    from urllib.parse import quote_plus
    return ("https://www.ncbi.nlm.nih.gov/books/n/statpearls/?term="
            f"{quote_plus(term)}")


_AE_E_SWAPS = [
    # American -> British (the canonical names in _conditions.py use
    # British spelling, so we normalise expansions toward British).
    ("hematolog",   "haematolog"),
    ("hemoglob",    "haemoglob"),
    ("hemorrh",     "haemorrh"),
    ("hemochrom",   "haemochrom"),
    ("hemophil",    "haemophil"),
    ("hematuria",   "haematuria"),
    ("hematemesis", "haematemesis"),
    ("hematoma",    "haematoma"),
    ("anemia",      "anaemia"),
    ("leukemia",    "leukaemia"),
    ("leukocyte",   "leucocyte"),
    ("edema",       "oedema"),
    ("esophag",     "oesophag"),
    ("pediatric",   "paediatric"),
    ("dyspnea",     "dyspnoea"),
    ("diarrhea",    "diarrhoea"),
    ("tumor",       "tumour"),
    ("color",       "colour"),
    ("fetal",       "foetal"),
    ("fetus",       "foetus"),
]


def _normalise_for_lookup(s: str) -> str:
    """Lowercase + American->British spelling normalisation so acronym
    expansions like 'Acute Lymphoblastic Leukemia' match the condition
    entry 'Acute lymphoblastic leukaemia'."""
    n = (s or "").strip().lower()
    for am, br in _AE_E_SWAPS:
        if am in n:
            n = n.replace(am, br)
    return n


def _acronym_to_condition(expansion: str):
    """If `expansion` matches a known condition's canonical name or any
    of its aliases, return that condition entry; otherwise None.

    Used to give acronym popups a richer body: instead of the acronym's
    own short description we render the matched condition's full
    summary (Sx / Ix / Mx / Ddx) with a small 'ACRONYM = full name.'
    preface so the link between the abbreviation and the condition is
    explicit.

    Spelling-tolerant: tries direct lookup first, then a normalised
    form swapping American spelling to British (the canonical form used
    in _conditions.py) so e.g. ALL ('Acute Lymphoblastic Leukemia')
    matches the British 'Acute lymphoblastic leukaemia' entry.
    """
    if not expansion:
        return None
    lookup = getattr(_conditions, "_LOOKUP", None)
    if lookup is None:
        return None
    direct = lookup.get(expansion.strip().lower())
    if direct is not None:
        return direct
    return lookup.get(_normalise_for_lookup(expansion))


def _acronym_terms(card) -> list:
    """Resolve medical acronyms in card text → highlight terms.
    Acronym matches are case-sensitive to avoid false positives like 'pe' in
    English prose - only the uppercase form gets underlined.

    Smart enrichment: if the acronym's expansion matches a known condition
    (e.g. MI -> 'Myocardial infarction'), the popup shows the CONDITION's
    full summary instead of the acronym's short description, with a small
    'MI = Myocardial infarction.' preface so the user sees why this popup
    appeared.  Falls back to the acronym's own description when no
    matching condition exists (lab-value / instrument acronyms etc.)."""
    text = _card_text(card)
    if not text:
        return []
    out = []
    for it in _acronyms.resolve(text):
        cond = _acronym_to_condition(it["expansion"])
        if cond is not None:
            preface = f"{it['acronym']} = {cond['name']}."
            body = cond.get("summary", "") or ""
            out.append({
                "title":      it["acronym"],
                "_article":   f'{it["acronym"]} - {cond["name"]}',
                "_expansion": it["expansion"],
                "url":        _conditions._url_for(cond),
                "summary":    f"{preface} {body}".strip(),
                "source":     "statpearls",
                "case_sensitive": True,
            })
            continue
        out.append({
            "title":      it["acronym"],
            "_article":   f'{it["acronym"]} - {it["expansion"]}',
            "_expansion": it["expansion"],       # used by _upgrade_acronym_urls
            "url":        _term_search_url(it["expansion"]),
            "summary":    it["description"],
            "source":     "statpearls",
            "case_sensitive": True,
        })
    return out


def _drug_terms(card) -> list:
    """Resolve drug names in card text → highlight terms.
    Brand names are matched case-sensitively (they're capitalised), generics
    case-insensitively.  Clicking opens the DrugBank page in the sidebar."""
    text = _card_text(card)
    if not text:
        return []
    out = []
    for it in _drugs.resolve(text):
        out.append({
            "title":          it["name"],
            "_article":       it["name"],
            "url":            it.get("url", ""),
            "summary":        it["summary"],
            "source":         "drugbank",
            "case_sensitive": it.get("case_sensitive", False),
        })
    return out


def _condition_terms(card) -> list:
    """Resolve common medical conditions in card text → highlight terms.
    Each links to a StatPearls article so the user can open the full chapter
    even when the auto-search returned a slightly different article."""
    text = _card_text(card)
    if not text:
        return []
    out = []
    for it in _conditions.resolve(text):
        out.append({
            "title":          it["name"],
            "_article":       it["name"],
            "url":            it["url"],
            "summary":        it["summary"],
            "source":         it.get("source") or "statpearls",
            "case_sensitive": False,
        })
    return out


def _custom_term_matches(card) -> list:
    """User-defined popup terms.  Match by case-sensitive substring
    when `case_sensitive` is True, else case-insensitive whole-word."""
    text = _card_text(card)
    if not text:
        return []
    text_lower = text.lower()
    out = []
    for entry in _custom_terms():
        title = entry["title"]
        if entry.get("case_sensitive"):
            present = title in text
        else:
            present = title.lower() in text_lower
        if present:
            out.append(entry)
    return out


def _upgrade_acronym_urls(acronyms: list, cached: list) -> None:
    """Replace search URLs in acronym terms with direct NBK article URLs
    when the expansion fuzzy-matches a cached article title."""
    if not acronyms or not cached:
        return
    for acr in acronyms:
        exp = (acr.get("_expansion") or "").lower()
        if not exp:
            continue
        for r in cached:
            title = (r.get("title") or "").lower()
            url   = r.get("url") or ""
            if not title or not url:
                continue
            if exp == title or exp in title or title in exp:
                acr["url"] = url
                break


def _upgrade_condition_urls(conditions: list, cached: list) -> None:
    """Replace StatPearls search URLs in condition terms with direct NBK
    article URLs when a cached article title matches the condition name.
    Only upgrades terms that are still using a search URL (i.e. conditions
    without a hardcoded NBK ID in _conditions.py)."""
    if not conditions or not cached:
        return
    for cond in conditions:
        if "?term=" not in (cond.get("url") or ""):
            continue  # already a direct NBK URL - leave as-is
        name = cond.get("title", "").lower()
        if not name:
            continue
        for r in cached:
            title = (r.get("title") or "").lower()
            url   = r.get("url") or ""
            if not title or not url:
                continue
            if name == title or name in title or title in name:
                cond["url"] = url
                break


def _expand_results(results: list) -> list:
    """For each result, emit highlight terms covering both the full title and
    each significant word inside it.  All terms link to that result's URL and
    carry its summary so the tooltip can show real context."""
    out = []
    seen = set()
    for r in results:
        title   = (r.get("title") or "").strip()
        url     = r.get("url") or ""
        summary = r.get("summary") or ""
        if not title or not url:
            continue
        if title.lower() not in seen and len(title) >= 4:
            seen.add(title.lower())
            out.append({"title": title, "url": url, "summary": summary})
        for w in _TITLE_WORD.findall(title):
            lw = w.lower()
            if lw in _STOPWORDS or lw in seen:
                continue
            seen.add(lw)
            out.append({"title": w, "url": url, "summary": summary,
                        "_article": title})
    return out


# ── Phase 1: synchronous HTML injection via card_will_show ────────────────────

_HIGHLIGHT_CSS_TPL = (
    '<style>.sp-mark{{border-bottom:2px solid {c};cursor:pointer;'
    'border-radius:2px;display:inline;transition:background .1s;}}'
    '.sp-mark:hover{{background:rgba(15,202,212,.18);}}</style>'
)

_pattern_cache: dict = {}
_PATTERN_CACHE_MAX = 16


def _esc_attr(s: str) -> str:
    return (s.replace("&", "&amp;").replace('"', "&quot;")
             .replace("<", "&lt;").replace(">", "&gt;").replace("'", "&#39;"))


def _build_pattern(terms: list):
    """Build ONE combined regex that handles both case-sensitive and
    case-insensitive terms in a single pass.  Returns (regex, lookup,
    sensitive_titles_set) - the lookup keys are exact titles for sensitive
    terms and lowercased titles for insensitive terms.

    Using a single pass eliminates the corruption bug from sequential
    passes where pass 2 would match terms inside pass 1's span attributes.
    Results are cached by term fingerprint - re.compile is expensive.
    """
    # Cache key covers only fields that affect the regex/lookup - title,
    # case-sensitivity, and URL (which can change via _upgrade_*_urls).
    # Summaries and sources are static and excluded so hashing stays fast
    # even as descriptions grow long.
    cache_key = frozenset(
        (t["title"], bool(t.get("case_sensitive")), t.get("url", ""))
        for t in terms
    )
    if cache_key in _pattern_cache:
        return _pattern_cache[cache_key]

    sensitive   = sorted([t for t in terms if t.get("case_sensitive")],
                         key=lambda r: len(r["title"]), reverse=True)
    insensitive = sorted([t for t in terms if not t.get("case_sensitive")],
                         key=lambda r: len(r["title"]), reverse=True)

    parts = []
    lookup = {}
    sens_titles = set()

    # Case-sensitive alternatives first (regex tries these as-is)
    for t in sensitive:
        title = t["title"]
        parts.append(re.escape(title))
        lookup[title] = {
            "url":     _esc_attr(t["url"]),
            "article": _esc_attr(t.get("_article") or title),
            "summary": _esc_attr(t.get("summary") or ""),
            "source":  t.get("source") or "statpearls",
            "utd":     _esc_attr(json.dumps(t.get("utd") or [],
                                            separators=(",", ":"))),
        }
        sens_titles.add(title)

    # Case-insensitive alternatives wrapped in (?i:…) - scoped flag, only this
    # branch ignores case while sensitive branches above stay case-sensitive.
    if insensitive:
        ins_parts = []
        for t in insensitive:
            title = t["title"]
            ins_parts.append(re.escape(title))
            lookup[title.lower()] = {
                "url":     _esc_attr(t["url"]),
                "article": _esc_attr(t.get("_article") or title),
                "summary": _esc_attr(t.get("summary") or ""),
                "source":  t.get("source") or "statpearls",
                "utd":     _esc_attr(json.dumps(t.get("utd") or [],
                                                separators=(",", ":"))),
            }
        parts.append("(?i:" + "|".join(ins_parts) + ")")

    if not parts:
        _pattern_cache[cache_key] = (None, None, None)
        return None, None, None

    rx = re.compile(r"\b(?:" + "|".join(parts) + r")\b")
    result = rx, lookup, sens_titles
    if len(_pattern_cache) >= _PATTERN_CACHE_MAX:
        _pattern_cache.pop(next(iter(_pattern_cache)))
    _pattern_cache[cache_key] = result
    return result


def _inject_highlights(html: str, results: list, color: str) -> str:
    """Inject .sp-mark spans + CSS into card HTML string.
    Operates on the raw HTML string - no JS needed, no CSP concerns.
    """
    # Self-heal: strip any sp-mark spans already present (cheap early exit
    # if there are none - avoids running the regex on every card).
    if 'class="sp-mark"' in html:
        html = _strip_sp_marks(html)
    terms = [r for r in results
             if r.get("title")
             and (len(r["title"]) >= 4 or r.get("case_sensitive"))]
    if not terms:
        return html

    rx, lookup, sens_titles = _build_pattern(terms)
    if rx is None:
        return html

    def _replace_text(text: str) -> str:
        # ONE pass over the text using the combined regex.  No risk of a
        # later pass corrupting an earlier pass's injected HTML.
        def _span(m):
            word = m.group(0)
            t = lookup.get(word) if word in sens_titles else lookup.get(word.lower())
            if not t:
                return word
            return (f'<span class="sp-mark" '
                    f'data-sp-url="{t["url"]}" '
                    f'data-sp-title="{t["article"]}" '
                    f'data-sp-summary="{t["summary"]}" '
                    f'data-sp-source="{t.get("source", "statpearls")}" '
                    f'data-sp-utd="{t.get("utd", "[]")}">{word}</span>')
        return rx.sub(_span, text)

    # Walk the HTML string, replacing text outside <tag> blocks and
    # skipping <script> / <style> content.
    result = []
    skip = False
    i = 0
    n = len(html)
    while i < n:
        if html[i] == '<':
            j = html.find('>', i)
            if j == -1:
                result.append(html[i:])
                break
            tag = html[i:j + 1]
            # Sniff the tag name without splitting twice.
            k = 1
            if k < len(tag) and tag[k] == '/':
                k += 1
            tag_name_end = k
            while tag_name_end < len(tag) and tag[tag_name_end].isalpha():
                tag_name_end += 1
            tname = tag[k:tag_name_end].lower()
            if tname in ('script', 'style'):
                # Detect closing form; tag[1] == '/' ⇒ closing tag.
                skip = (tag[1] != '/')
            result.append(tag)
            i = j + 1
        else:
            j = html.find('<', i)
            if j == -1:
                j = n
            chunk = html[i:j]
            if not skip and chunk.strip():
                chunk = _replace_text(chunk)
            result.append(chunk)
            i = j

    return _HIGHLIGHT_CSS_TPL.format(c=color) + ''.join(result)


def _on_card_will_show(html: str, card, kind: str) -> str:
    """Phase 1: inject highlights synchronously before card renders.
    Highlights two sources:
      • Cached article-title matches (from previous searches) - link to article
      • Significant words extracted from the card itself - link to StatPearls search
    """
    if kind not in ("reviewQuestion", "reviewAnswer"):
        return html
    if not _config.get("enableHighlights"):
        return html
    if kind == "reviewQuestion" and not _config.get("enableHighlightsOnQuestions"):
        return html
    if _panel_ref is None:
        return html
    try:
        guid       = card.note().guid
        cached     = _panel_ref._searcher.cached(guid) or []
        terms      = _expand_results(cached)
        acronyms   = _acronym_terms(card)
        _upgrade_acronym_urls(acronyms, cached)
        drugs      = _drug_terms(card)
        conditions = _condition_terms(card)
        _upgrade_condition_urls(conditions, cached)
        custom     = _custom_term_matches(card)
        all_terms  = terms + acronyms + drugs + conditions + custom
        if not all_terms:
            return html
        color = _config.get("highlightColor") or "#0fcad4"
        return _inject_highlights(html, all_terms, color)
    except Exception as exc:
        _log.error("card_will_show", exc)
        return html


# ── Phase 2: async fallback via web.eval() ────────────────────────────────────

def _on_webview_will_set_content(web_content: Any, context: Any) -> None:
    """Belt-and-suspenders: also load marker.js via <script src> for tooltip events."""
    if Reviewer is None or not isinstance(context, Reviewer):
        return
    web_content.body += f'<script src="{_SCRIPT_URL}"></script>\n'


def _mark_in_reviewer(results: list) -> None:
    """Phase 2: mark the live DOM when async results first arrive."""
    try:
        reviewer = mw.reviewer
        if reviewer is None or reviewer.web is None:
            return
        if not _on_answer and not _config.get("enableHighlightsOnQuestions"):
            return

        color = _config.get("highlightColor") or "#0fcad4"
        title_terms = _expand_results(results or [])
        acro_terms  = _acronym_terms(_current_card) if _current_card else []
        _upgrade_acronym_urls(acro_terms, results or [])
        drug_terms  = _drug_terms(_current_card) if _current_card else []
        cond_terms  = _condition_terms(_current_card) if _current_card else []
        _upgrade_condition_urls(cond_terms, results or [])
        custom_terms = _custom_term_matches(_current_card) if _current_card else []
        all_terms   = title_terms + acro_terms + drug_terms + cond_terms + custom_terms
        if not all_terms:
            return
        # marker.js expects {title, url, summary, article?, case_sensitive?,
        # source, utd?} where utd is a list of {label, url} chip dicts.
        terms = [{
            "title":          t["title"],
            "url":            t["url"],
            "summary":        t.get("summary", ""),
            "article":        t.get("_article", t["title"]),
            "case_sensitive": bool(t.get("case_sensitive")),
            "source":         t.get("source", "statpearls"),
            "utd":            t.get("utd") or [],
        } for t in all_terms]
        t_json = json.dumps(terms)
        c_json = json.dumps(color)
        # marker.js is already loaded via <script src> in webview_will_set_content.
        js = "if(window.spAddon)spAddon.mark(" + t_json + "," + c_json + ");"
        reviewer.web.eval(js)
    except Exception as exc:
        _log.error("mark error", exc)


def _clear_in_reviewer() -> None:
    try:
        reviewer = mw.reviewer
        if reviewer and reviewer.web:
            reviewer.web.eval(
                'var _s=document.querySelectorAll(".sp-mark");'
                'for(var _i=0;_i<_s.length;_i++){'
                '  var _m=_s[_i];'
                '  if(_m.parentNode)_m.parentNode.replaceChild('
                '    document.createTextNode(_m.textContent),_m);'
                '}'
                'if(document.body)document.body.normalize();'
            )
    except Exception:
        pass


# ── reviewer hooks ────────────────────────────────────────────────────────────

def _local_results_for_card(card) -> list:
    """Build instant sidebar results from the local conditions/drugs databases.
    Returns a list of result dicts in the same format as NCBI search results."""
    results = []
    seen: set = set()
    for t in _condition_terms(card):
        key = t["url"]
        if key and key not in seen:
            seen.add(key)
            results.append({
                "id":      f"local_cond_{t['title']}",
                "title":   t["title"],
                "url":     t["url"],
                "summary": t.get("summary", ""),
            })
    for t in _drug_terms(card):
        key = t["url"]
        if key and key not in seen:
            seen.add(key)
            results.append({
                "id":      f"local_drug_{t['title']}",
                "title":   t["title"] + " - drug",
                "url":     t["url"],
                "summary": t.get("summary", ""),
            })
    return results


def _on_show_question(card) -> None:
    global _on_answer, _current_card, _prev_card_id
    _on_answer = False

    card_id = getattr(card, "id", None)
    card_changed = (card_id != _prev_card_id)
    _prev_card_id = card_id
    _current_card = card

    # Dismiss any open popup immediately when progressing to a new card.
    if card_changed:
        try:
            if mw.reviewer and mw.reviewer.web:
                mw.reviewer.web.eval(
                    "if(window.spAddon&&spAddon.dismissTip)spAddon.dismissTip();"
                )
        except Exception:
            pass

    # Drop any prior text cache on this card so re-shown cards re-strip lazily.
    try:
        if hasattr(card, "_ap_text"):
            del card._ap_text
    except Exception:
        pass

    if not _config.get("enableHighlights"):
        _clear_in_reviewer()
        return

    if _panel_ref is None:
        return

    # Feed instant local-database results to the sidebar before the network
    # search completes - gives immediate article suggestions with zero latency.
    if _config.get("autoSearch") and card_changed:
        local = _local_results_for_card(card)
        if local:
            _panel_ref._apply_local_results(local)

    if not _config.get("autoSearch"):
        return

    query, guid = _card_query(card)
    if query:
        _panel_ref.auto_search(query, guid)


def _on_show_answer(card) -> None:
    global _on_answer, _current_card
    _on_answer = True
    _current_card = card

    if not _config.get("enableHighlights"):
        return

    query, guid = _card_query(card)
    if not query:
        return

    if _panel_ref is not None:
        _panel_ref.auto_search(query, guid)


def on_results_available(results: list) -> None:
    """Called by the panel when NCBI search completes (async phase 2)."""
    if _config.get("enableHighlights"):
        _mark_in_reviewer(results)


# ── register hooks ────────────────────────────────────────────────────────────

def register_hooks() -> None:
    gui_hooks.webview_will_set_content.append(_on_webview_will_set_content)
    gui_hooks.reviewer_did_show_question.append(_on_show_question)
    gui_hooks.reviewer_did_show_answer.append(_on_show_answer)
    try:
        gui_hooks.card_will_show.append(_on_card_will_show)
        _log.debug("card_will_show hook registered")
    except AttributeError:
        _log.warn("card_will_show hook not available (older Anki)")
