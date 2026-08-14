# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""
TheAnkiDote.chat._compose - put the copied text into the provider's
message box instead of leaving it on the clipboard.

Until 1.4 the send-to-chat shortcuts stopped at the clipboard and asked
the user to paste.  That was one keystroke away from done and, worse,
left the dock focused on nothing in particular: you opened the sidebar,
clicked the box, then pasted.  This module closes that gap.

How it works, and why in this order:

1.  `_FOCUS_JS` locates the composer on whatever provider is loaded and
    focuses it, putting the caret at the end of any draft already
    there.  Provider-specific selectors are tried first, then a generic
    scan scored on size, position and editability - so a provider
    redesigning their DOM degrades to the generic path rather than
    breaking outright.

2.  Qt's own `WebAction.Paste` does the insertion.  This is the real
    browser paste path: a trusted `paste` event carrying the real
    clipboard payload, handled by the site's own paste logic.  That
    matters because every current provider composer is a rich-text
    editor (ProseMirror on Claude and ChatGPT, Quill on Gemini, Lexical
    elsewhere) which turns newlines into paragraph nodes on paste but
    silently flattens or drops them when text is injected by script.
    A whole Anki card is multi-line, so this distinction is the whole
    ballgame.

3.  Only if the box is still empty afterwards does `_INSERT_JS` fall
    back to script insertion - a synthetic paste event first, then
    `execCommand("insertText")`, then a direct value write with an
    `input` event for plain textareas.  Whatever happens, the text is
    already on the clipboard, so the worst case is the pre-1.4
    behaviour plus a focused box.

Nothing here submits the message.  The text lands in the box and the
user reads it, edits it, and presses Enter themselves.
"""

import json

from .. import _log

# Providers whose composer we know by selector.  Matched on hostname
# substring, most specific first.  A miss here is not fatal - the
# generic scan below picks up anything shaped like a message box.
_PROVIDER_SELECTORS = {
    "claude.ai": [
        'div[contenteditable="true"].ProseMirror',
        'div[contenteditable="true"][aria-label*="prompt" i]',
    ],
    "chatgpt.com": ['#prompt-textarea', 'div[contenteditable="true"].ProseMirror'],
    "openai.com": ['#prompt-textarea', 'div[contenteditable="true"].ProseMirror',
                   'textarea[data-id]'],
    "gemini.google.com": ['div.ql-editor[contenteditable="true"]',
                          'rich-textarea div[contenteditable="true"]'],
    "copilot.microsoft.com": ['textarea#userInput',
                              'textarea[data-testid="composer-input"]',
                              'div[contenteditable="true"]'],
    "perplexity.ai": ['#ask-input', 'div[contenteditable="true"]',
                      'textarea[placeholder]'],
    "chat.deepseek.com": ['textarea#chat-input', 'textarea'],
    "grok.com": ['textarea[aria-label]', 'textarea'],
    "duck.ai": ['textarea[name="user-prompt"]', 'textarea'],
    "duckduckgo.com": ['textarea[name="user-prompt"]', 'textarea'],
}

# Retry ladder in milliseconds.  A cold dock has to build the webview,
# load the provider and let its editor mount before there is anything
# to focus; a dock that was already open is ready on the first tick.
_ATTEMPT_DELAYS = (250, 700, 1500, 2800, 4500)

# Delay between triggering the native paste and checking whether it
# landed.  Long enough for the editor's paste handler to run, short
# enough that the fallback still feels instant.
_VERIFY_DELAY = 220

# Sanity ceiling.  Beyond this the paste is more likely to hang the
# provider's editor than to be useful, so we leave it on the clipboard.
_MAX_CHARS = 40000


def _qtimer():
    try:
        from PyQt6.QtCore import QTimer
    except (ImportError, AttributeError):
        from PyQt5.QtCore import QTimer
    return QTimer


def _paste_action():
    try:
        from PyQt6.QtWebEngineCore import QWebEnginePage
    except (ImportError, AttributeError):
        from aqt.qt import QWebEnginePage
    return QWebEnginePage.WebAction.Paste


def _focus_js(selectors: list) -> str:
    """Build the focus script for the loaded provider.

    Scoring, in words: a hinted selector wins outright; otherwise
    prefer the biggest visible editable sitting lowest in the viewport,
    which is where a chat composer lives on every one of the eight
    providers.  Elements inside our own popup chrome, or ones that are
    clearly search boxes, are excluded.
    """
    return r"""
(function () {
  try {
    var HINTS = __HINTS__;
    function visible(el) {
      if (!el || el.disabled || el.readOnly) return false;
      if (el.getAttribute && el.getAttribute("aria-hidden") === "true") return false;
      var r = el.getBoundingClientRect();
      if (r.width < 60 || r.height < 16) return false;
      var s = window.getComputedStyle(el);
      if (s.visibility === "hidden" || s.display === "none" || s.opacity === "0")
        return false;
      return true;
    }
    function placeCaret(el) {
      el.focus({ preventScroll: false });
      try {
        if (el.tagName === "TEXTAREA" || el.tagName === "INPUT") {
          var n = el.value.length;
          el.setSelectionRange(n, n);
        } else {
          var sel = window.getSelection();
          var rng = document.createRange();
          rng.selectNodeContents(el);
          rng.collapse(false);
          sel.removeAllRanges();
          sel.addRange(rng);
        }
      } catch (e) {}
      try { el.scrollIntoView({ block: "nearest" }); } catch (e) {}
      return document.activeElement === el ||
             (el.contains && el.contains(document.activeElement));
    }

    for (var i = 0; i < HINTS.length; i++) {
      var hit = document.querySelector(HINTS[i]);
      if (hit && visible(hit)) { return placeCaret(hit) ? 1 : 0; }
    }

    var cands = document.querySelectorAll(
      'textarea, div[contenteditable="true"], [role="textbox"][contenteditable="true"]');
    var best = null, bestScore = -1;
    var vh = window.innerHeight || 800;
    for (var j = 0; j < cands.length; j++) {
      var el = cands[j];
      if (!visible(el)) continue;
      if (el.closest && el.closest("#tad-tip, .tad-tip, #_tad_root")) continue;
      var role = (el.getAttribute("type") || "") + " " +
                 (el.getAttribute("aria-label") || "") + " " +
                 (el.getAttribute("placeholder") || "") + " " +
                 (el.getAttribute("name") || "");
      if (/\bsearch\b/i.test(role)) continue;
      var r = el.getBoundingClientRect();
      var score = Math.min(r.width * r.height, 200000) / 1000;
      score += (r.top / vh) * 40;                 // lower on screen is better
      if (el.tagName !== "TEXTAREA") score += 5;  // rich editors are the norm now
      var txt = el.value !== undefined ? el.value : (el.innerText || "");
      if (!txt.trim()) score += 10;               // an empty box is the live one
      if (score > bestScore) { bestScore = score; best = el; }
    }
    if (!best) return 0;
    return placeCaret(best) ? 1 : 0;
  } catch (e) { return 0; }
})();
""".replace("__HINTS__", json.dumps(selectors))


# Read back what is in the focused box.  Used both to decide whether the
# native paste landed and to avoid double-inserting on a retry.
_READ_JS = r"""
(function () {
  try {
    var el = document.activeElement;
    if (!el) return "";
    if (el.value !== undefined) return el.value;
    return el.innerText || el.textContent || "";
  } catch (e) { return ""; }
})();
"""


def _insert_js(text: str) -> str:
    """Script-side insertion, used only when the native paste is a no-op.

    Three tiers, because no single technique survives all eight
    providers: a synthetic paste event (respects the editor's own
    newline handling), `execCommand("insertText")` (correct undo stack,
    fires the events React listens for), and finally a direct value
    write with a dispatched `input` event for a plain textarea.
    """
    return r"""
(function () {
  var TEXT = __TEXT__;
  try {
    var el = document.activeElement;
    if (!el) return 0;
    var editable = el.value !== undefined ||
                   el.isContentEditable === true;
    if (!editable) return 0;

    try {
      var dt = new DataTransfer();
      dt.setData("text/plain", TEXT);
      var ev = new ClipboardEvent("paste",
        { bubbles: true, cancelable: true, clipboardData: dt });
      var notCancelled = el.dispatchEvent(ev);
      if (!notCancelled) return 1;   // the editor handled it
    } catch (e) {}

    try { if (document.execCommand("insertText", false, TEXT)) return 1; } catch (e) {}

    if (el.value !== undefined) {
      try {
        var proto = el.tagName === "TEXTAREA"
          ? window.HTMLTextAreaElement.prototype
          : window.HTMLInputElement.prototype;
        var setter = Object.getOwnPropertyDescriptor(proto, "value").set;
        setter.call(el, el.value + TEXT);
        el.dispatchEvent(new Event("input", { bubbles: true }));
        return 1;
      } catch (e) {}
    }
    return 0;
  } catch (e) { return 0; }
})();
""".replace("__TEXT__", json.dumps(text))


def _selectors_for(url: str) -> list:
    host = ""
    try:
        host = (url or "").split("//", 1)[-1].split("/", 1)[0].lower()
    except Exception:
        pass
    out: list = []
    for needle, sels in _PROVIDER_SELECTORS.items():
        if needle in host:
            out.extend(sels)
    return out


def paste_into_composer(browser, text: str, on_done=None) -> None:
    """Focus the composer in `browser` and put `text` in it.

    `on_done(ok: bool)` fires exactly once.  `text` is expected to be on
    the clipboard already - the native paste path uses it from there,
    and a failure at any stage leaves the user exactly where the
    pre-1.4 behaviour left them.
    """
    text = (text or "").strip()
    done = {"fired": False}

    def _finish(ok: bool) -> None:
        if done["fired"]:
            return
        done["fired"] = True
        if on_done is not None:
            try:
                on_done(bool(ok))
            except Exception as exc:
                _log.error("autopaste callback", exc)

    if not text or browser is None or len(text) > _MAX_CHARS:
        _finish(False)
        return

    QTimer = _qtimer()

    def _page():
        try:
            return browser.view.page()
        except Exception:
            return None

    def _attempt(idx: int) -> None:
        if done["fired"]:
            return
        page = _page()
        if page is None:
            _finish(False)
            return
        try:
            browser.view.setFocus()
        except Exception:
            pass
        try:
            url = browser.view.url().toString()
        except Exception:
            url = ""
        try:
            page.runJavaScript(_focus_js(_selectors_for(url)),
                               lambda res: _on_focused(res, idx))
        except Exception as exc:
            _log.error("autopaste focus", exc)
            _retry(idx)

    def _retry(idx: int) -> None:
        if done["fired"]:
            return
        nxt = idx + 1
        if nxt >= len(_ATTEMPT_DELAYS):
            _finish(False)
            return
        QTimer.singleShot(_ATTEMPT_DELAYS[nxt] - _ATTEMPT_DELAYS[idx],
                          lambda: _attempt(nxt))

    def _on_focused(res, idx: int) -> None:
        if done["fired"]:
            return
        if not res:
            _retry(idx)
            return
        page = _page()
        if page is None:
            _finish(False)
            return
        # Snapshot the box before pasting so a composer that already
        # held a draft isn't mistaken for a successful paste.
        try:
            page.runJavaScript(_READ_JS, lambda before: _do_paste(before or "", idx))
        except Exception:
            _do_paste("", idx)

    def _do_paste(before: str, idx: int) -> None:
        if done["fired"]:
            return
        page = _page()
        if page is None:
            _finish(False)
            return
        try:
            page.triggerAction(_paste_action())
        except Exception as exc:
            _log.error("autopaste trigger", exc)
        QTimer.singleShot(_VERIFY_DELAY, lambda: _verify(before, idx))

    def _verify(before: str, idx: int) -> None:
        if done["fired"]:
            return
        page = _page()
        if page is None:
            _finish(False)
            return
        try:
            page.runJavaScript(_READ_JS, lambda after: _judge(before, after or "", idx))
        except Exception:
            _fallback(idx)

    def _judge(before: str, after: str, idx: int) -> None:
        if done["fired"]:
            return
        # A rich editor may normalise whitespace on paste, so compare on
        # length rather than equality - anything meaningfully longer than
        # what was there means the paste landed.
        if len(after.strip()) > len(before.strip()) + max(8, len(text) // 4):
            _finish(True)
            return
        _fallback(idx)

    def _fallback(idx: int) -> None:
        if done["fired"]:
            return
        page = _page()
        if page is None:
            _finish(False)
            return
        try:
            page.runJavaScript(_insert_js(text),
                               lambda ok: _finish(True) if ok else _retry(idx))
        except Exception as exc:
            _log.error("autopaste insert", exc)
            _retry(idx)

    QTimer.singleShot(_ATTEMPT_DELAYS[0], lambda: _attempt(0))
