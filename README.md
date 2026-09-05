# The AnkiDote

A medical reference sidebar for Anki. It highlights the conditions,
drugs and clinical vocabulary already written on your cards, explains
them on hover, and puts StatPearls, DrugBank, UpToDate and an AI chat
one keystroke away without leaving the reviewer.

Built for Australian medical students, so drug names, units and spelling
follow Australian conventions and clinical content is checked against
Australian guidance first.

---

## What it does

### Reference popups

Terms on the current card are underlined. Hovering one shows a
definition; clicking opens the full article in the side panel, or in
your browser if you prefer.

Six databases are matched:

| Database | Covers | Opens |
|---|---|---|
| Conditions | Diseases and syndromes | StatPearls, or UpToDate where mapped |
| Drugs | Generic and brand names | DrugBank |
| Preclinical | Basic-science concepts | Wikipedia |
| Descriptive | Lesion morphology, symptom and lab vocabulary | Wikipedia |
| Psychiatry | Mental state exam phenomenology | Wikipedia |
| Signs | Examination and symptom vocabulary | Wikipedia |

The last one exists because the gap was the wrong way round. Cards were
resolving *dermatomyositis* and not *poikiloderma*, *telangiectasia*,
*myalgia* or *pathognomonic* - but a reader who already knows the
disease name reads past it either way, and one who doesn't is usually
stuck on the descriptive word, because it is the part of the sentence
carrying the finding.

You can add your own terms under **Settings → General → Custom terms**.

### The sidebar

A dock on the right of the reviewer, with three modes:

- **StatPearls / DrugBank** - reference browsing, with pills to switch
  between the two. Popup articles open here.
- **UpToDate** - your own institutional subscription, signed into once
  and remembered. Set your entry URL under Settings → Services if your
  institution uses an SSO proxy.
- **AI chat** - your existing browser session with Claude, ChatGPT,
  Gemini, Copilot, Perplexity, DeepSeek, Grok or a self-hosted endpoint.
  No API key, no account of ours, nothing is sent anywhere on its own.

`Ctrl+Shift+K` sends the current text selection to the chat and
`Ctrl+Shift+J` sends the whole visible card: the dock opens, the message
box is focused, and the text is pasted into it. **Nothing is submitted  - 
pressing Enter is always your keystroke.**

### Relevant articles

The sidebar lists articles matching terms found on the current card,
ranked by how central each term is to it: whether it appears in the
card's first field, how often, how early, and how specific it is. It is
a guess, so it has a close button; dismissing it hides it for that card
only.

---

## Install

From [AnkiWeb](https://ankiweb.net/shared/info/720072719), or download
the `.ankiaddon` from
[Releases](https://github.com/mord58562/theankidote/releases) and open
it with Anki.

Requires Anki 25.02 or newer with Qt 6. Some features need newer Qt: the
dark rendering of reference pages needs Qt 6.7+, and degrades to normal
light pages below that.

---

## Shortcuts

| Action | Default |
|---|---|
| Toggle StatPearls / DrugBank | `Ctrl+Shift+S` |
| Toggle UpToDate | `Ctrl+Shift+U` |
| Toggle AI chat | `Ctrl+Shift+A` |
| Search selection in UpToDate | `Ctrl+Shift+L` |
| Send selection to AI chat | `Ctrl+Shift+K` |
| Send whole card to AI chat | `Ctrl+Shift+J` |

macOS maps `Ctrl` to `⌘`, so these appear as `⌘⇧S` and so on.

All of them are editable under **Settings → Shortcuts**: click a field,
press the keys you want, and the new binding applies as soon as you
close the window. Clear a field to disable that shortcut. **Restore
defaults** is there if you lose one, and clashing bindings are flagged.

---

## Settings

**Tools → The AnkiDote → Settings**, in four tabs:

- **General** - which modules are active, reference-popup behaviour,
  custom terms, toolbar button order.
- **Services** - UpToDate institution URL, AI chat provider and paste
  behaviour.
- **Shortcuts** - every binding, editable.
- **Advanced** - verbose logging, the diagnostic log, and a web
  inspector for the sidebar webviews.

Everything writes on close, matching Anki's own Preferences. Every
setting also has a config key; see [config.md](config.md).

---

## Privacy

- **No telemetry.** Nothing is collected, and there is no server of ours
  to collect it.
- **No API keys.** The AI chat is your own browser session in an
  embedded webview. Cookies persist so you sign in once per provider.
- **No message submission.** The send-to-chat shortcuts copy, focus the
  message box and paste. They never press Enter.
- **Your collection stays local.** Card text is read to find terms and
  is never transmitted anywhere.
- **Network access** is limited to the sites you are browsing  - 
  StatPearls, DrugBank, UpToDate and your chosen chat provider - plus
  NCBI when resolving an article link.

---

## Known limitations

- **Passkey and Touch ID sign-in do not work** in an embedded webview.
  This is a macOS restriction affecting every Anki sidebar add-on. Use a
  password with 2FA; cookies persist, so it is once per provider.
- **DrugBank sits behind Cloudflare.** A search may pause on a bot
  check. The panel waits it out rather than interrupting it, but a check
  that never clears has to be finished in your normal browser.
- **UpToDate needs your own subscription.** The add-on provides no
  content of its own.
- **The article list is a guess.** It is ranked, not authoritative.

---

## Contributing

Issues and pull requests:
[github.com/mord58562/theankidote](https://github.com/mord58562/theankidote)

Bug reports are much easier to act on with a diagnostic log: turn on
**Settings → Advanced → Verbose logging**, reproduce the problem, then
use **Show log**.

Tests live in `tests/` and run with plain `python3` - no Anki required:

```bash
python3 tests/test_security.py      # untrusted content, updater, URL trust
python3 tests/test_vocab.py         # database integrity, popup height budget
python3 tests/test_library.py       # library validation, publishing contract
python3 tests/test_toolbar_order.py
```

The suite is deliberately small and covers one thing: defects that do
not announce themselves. A broken phrase matcher is obvious on the next
card; a summary that quietly joins the scrolling backlog, an override
baked into its own base text, or a URL that Python and Chromium parse
differently are not. Tests that restated the implementation were removed
at 2.2.

---

## Licence

GPL-3.0-or-later. See [LICENSE](LICENSE).

Clinical content is compiled from public sources and is intended for
study. It is not a clinical decision tool and carries no warranty  - 
check current guidance before acting on anything you read here.

Version history is in [CHANGELOG.md](CHANGELOG.md).
