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
import os
import re
import time
from html.parser import HTMLParser
from typing import Any

from aqt import mw, gui_hooks

from .. import _config, _log
from . import (_acronyms, _drugs, _conditions, _preclinical,
               _descriptive, _psych, _signs)


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
            "label": (entry.get("label") or "").strip(),
            "case_sensitive": bool(entry.get("case_sensitive")),
            "user_defined": True,
        })
    _custom_terms_cache = out
    return out

try:
    from aqt.reviewer import Reviewer
except Exception:
    Reviewer = None  # type: ignore[assignment,misc]

_ADDON_PKG  = __name__.split(".")[0]


def _marker_fingerprint() -> str:
    """Short content hash of web/marker.js, used to bust the webview cache.

    marker.js is delivered to the reviewer as `<script src=...>` from
    Anki's media server, and that URL was byte-identical in every
    release. QtWebEngine caches by URL, so an install that had already
    fetched the file kept running its cached copy across upgrades - the
    add-on's Python side updated, the JavaScript side did not. That is
    why bullet rendering, added in preview 9, appeared not to work at
    all: the logic, the data and the CSS were all correct, and the
    reviewer was simply executing an older marker.js.

    Hashing the file rather than the manifest version means the URL also
    changes between builds of the same version, so editing marker.js
    during development takes effect on the next card instead of after a
    profile-wide cache clear.
    """
    try:
        import hashlib
        path = os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), "web", "marker.js")
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()[:12]
    except Exception:
        # Never fatal: a timestamp still busts the cache, it just does so
        # on every restart rather than only when the file changes.
        return str(int(time.time()))


_SCRIPT_URL = f"/_addons/{_ADDON_PKG}/web/marker.js?v={_marker_fingerprint()}"

# ── module-level state ────────────────────────────────────────────────────────

_on_answer    = False
_panel_ref    = None
_current_card = None  # set on show_question/show_answer for Phase 2 use
_prev_card_id: "int | None" = None  # for detecting card progression vs flip


def set_panel(panel) -> None:
    global _panel_ref
    _panel_ref = panel


# ── card text extraction ──────────────────────────────────────────────────────

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
    summary (Sx / Ix / Mx / Ddx). The popup title already reads
    'ACRONYM - full name', so the body starts straight into the
    condition rather than restating the expansion a second time.

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
    full summary instead of the acronym's short description. The title
    ('MI - Myocardial infarction') already carries the expansion, so the
    body doesn't restate it. Falls back to the acronym's own description
    when no matching condition exists (lab-value / instrument acronyms
    etc.)."""
    text = _card_text(card)
    if not text:
        return []
    out = []
    for it in _acronyms.resolve(text):
        cond = _acronym_to_condition(it["expansion"])
        if cond is not None:
            out.append({
                "title":      it["acronym"],
                "_article":   f'{it["acronym"]} - {cond["name"]}',
                "_expansion": it["expansion"],
                "url":        _conditions._url_for(cond),
                "summary":    (cond.get("summary", "") or "").strip(),
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


def _preclinical_terms(card) -> list:
    """Resolve preclinical / basic-science terms in card text. Standalone
    library, fully free, no UpToDate dependency. Links to Wikipedia for
    further reading on click."""
    text = _card_text(card)
    if not text:
        return []
    out = []
    # Several databases, one popup source. `_preclinical` holds
    # basic-science concepts, `_descriptive` the vocabulary cards are
    # written in (lesion morphology, symptom words, lab descriptors),
    # and `_psych` the mental state exam. They resolve together because
    # the reader has no reason to care which file a definition came
    # from. Order settles collisions: the first database to claim a name
    # keeps it, and `tests/test_vocab.py` asserts there are none.
    for it in (list(_preclinical.resolve(text))
               + list(_descriptive.resolve(text))
               + list(_psych.resolve(text))
               + list(_signs.resolve(text))):
        if any(o["title"] == it["name"] for o in out):
            continue
        out.append({
            "title":          it["name"],
            "_article":       it["name"],
            "url":            it["url"],
            "summary":        it["summary"],
            "source":         "preclinical",
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
            "badge":   _esc_attr(t.get("label") or ""),
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
                "badge":   _esc_attr(t.get("label") or ""),
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
    # A term under 4 characters matched case-insensitively is noise -
    # "hi", "is", "an" would light up constantly. Case-sensitive terms
    # are exempt because the casing itself is discriminating (acronyms:
    # "PE" won't match "pe" in prose). User-defined custom terms are
    # exempt too: the user typed this one in deliberately, so silently
    # dropping it because it happens to be short is worse than the
    # noise the filter exists to prevent.
    terms = [r for r in results
             if r.get("title")
             and (len(r["title"]) >= 4 or r.get("case_sensitive")
                  or r.get("user_defined"))]
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
                    f'data-sp-badge="{t.get("badge", "")}" '
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
    Sourced from the bundled term databases (acronyms, drugs, conditions)
    plus user-defined custom terms - all instant, no network call."""
    if kind not in ("reviewQuestion", "reviewAnswer"):
        return html
    if not _config.get("enableHighlights"):
        return html
    if kind == "reviewQuestion" and not _config.get("enableHighlightsOnQuestions"):
        return html
    if _panel_ref is None:
        return html
    try:
        acronyms    = _acronym_terms(card)
        drugs       = _drug_terms(card)
        conditions  = _condition_terms(card)
        preclinical = _preclinical_terms(card)
        custom      = _custom_term_matches(card)
        all_terms   = acronyms + drugs + conditions + preclinical + custom
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

def _first_field_text(card) -> str:
    """The card's opening field, lowercased.

    On essentially every note type this is the subject line - the thing
    the card is *about* - so a term appearing there is categorically
    more relevant than one mentioned in passing further down."""
    try:
        vals = [v for v in card.note().values() if v.strip()]
        return _strip_html(vals[0]).lower() if vals else ""
    except Exception:
        return ""


def _rank_results(card, items: list) -> list:
    """Order the sidebar's article list by how central each term is.

    The list used to be every match on the card in the order the
    resolvers happened to find them, conditions first and drugs after.
    On a card about calcium pyrophosphate deposition disease that put
    "gout" - mentioned once, as a contrast - above the disease the card
    is actually about, and buried the drug the card is teaching under
    every condition named anywhere in the text.

    Four signals, in rough order of how much they matter:
      * the term appears in the first field (the card's subject);
      * how many times it appears at all;
      * how early the first mention is;
      * how specific the term is, since a long name is a narrower claim
        about the card's content than a short one.
    """
    text = (_card_text(card) or "").lower()
    head = _first_field_text(card)
    if not text:
        return items
    for it in items:
        name = (it.get("_term") or it.get("title") or "").lower()
        if not name:
            it["_score"] = 0.0
            continue
        count = text.count(name)
        pos = text.find(name)
        score = 0.0
        if name in head:
            score += 100.0
        score += min(count, 6) * 8.0
        if pos >= 0:
            score += max(0.0, 20.0 - pos / 40.0)
        score += min(len(name), 40) / 4.0
        it["_score"] = score
    items.sort(key=lambda r: -r.get("_score", 0.0))
    return items


def _local_results_for_card(card) -> list:
    """Build the sidebar's article list from the local databases.

    Ranked by `_rank_results` and capped at `maxResults`, because an
    unbounded list scrolls and a scrolling list of guesses is worse than
    a short one: the reader stops reading it either way, and the short
    one at least stays out of the way."""
    results = []
    seen: set = set()
    for t in _condition_terms(card):
        key = t["url"]
        if key and key not in seen:
            seen.add(key)
            results.append({
                "id":      f"local_cond_{t['title']}",
                "title":   t["title"],
                "_term":   t["title"],
                "url":     t["url"],
                "summary": t.get("summary", ""),
            })
    for t in _drug_terms(card):
        key = t["url"]
        if key and key not in seen:
            seen.add(key)
            results.append({
                "id":      f"local_drug_{t['title']}",
                # Kept separate from `_term` so the " - drug" label does
                # not end up in the text we score against the card.
                "title":   t["title"] + " - drug",
                "_term":   t["title"],
                "url":     t["url"],
                "summary": t.get("summary", ""),
            })
    _rank_results(card, results)
    try:
        cap = int(_config.get("maxResults") or 8)
    except Exception:
        cap = 8
    if cap > 0:
        results = results[:cap]
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

    # Feed instant local-database matches to the sidebar's article list.
    # Empty list hides the list section entirely (no "searching..." stub).
    if card_changed:
        _panel_ref.apply_local_results(_local_results_for_card(card))


def _on_show_answer(card) -> None:
    global _on_answer, _current_card
    _on_answer = True
    _current_card = card


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
