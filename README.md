# The AnkiDote

A medical reference sidebar for Anki. It highlights the conditions,
drugs and clinical vocabulary already written on your cards, explains
them on hover, and puts StatPearls, DrugBank, UpToDate and an AI chat
one keystroke away without leaving the reviewer.

Built for Australian medical students, so drug names, units and spelling
follow Australian conventions and clinical content is checked against
Australian guidance first.

The reference library is a separate file from the add-on and updates
itself over a content channel, so a corrected dose or a stale threshold
reaches you without an AnkiWeb release.

---

## What it does

### Reference popups

Terms on the current card are underlined. Hovering one shows a summary;
clicking opens the source.

Seven databases are matched:

| Database | Covers | Opens |
|---|---|---|
| Conditions | Diseases and syndromes, about 2,800 | A StatPearls chapter, or a search of the book where no chapter is mapped |
| Drugs | Generic and brand names, about 1,160 | DrugBank |
| Abbreviations | 436 acronyms carrying 463 senses | The condition behind the expansion, or a StatPearls search |
| Preclinical | Basic-science concepts | Wikipedia |
| Descriptive | Lesion morphology, symptom and lab vocabulary | Wikipedia |
| Psychiatry | Mental state exam phenomenology | Wikipedia |
| Signs | Examination and symptom vocabulary | Wikipedia |

The descriptive and signs databases exist because the gap was the wrong
way round. Cards were resolving *dermatomyositis* and not
*poikiloderma*, *telangiectasia*, *myalgia* or *pathognomonic* - but a
reader who already knows the disease name reads past it either way, and
one who doesn't is usually stuck on the descriptive word, because it is
the part of the sentence carrying the finding.

Abbreviations are read in context. Where a key carries more than one
sense, the rest of the card decides which one the popup shows, and
fourteen acronyms that are also ordinary English words - OR, ALL, PET,
CAP, AS among them - are left alone unless the card gives a reason to
read them as an acronym. When the expansion resolves to a condition the
popup carries that condition's whole summary, titled under both, as
"HTN - Hypertension".

A term is underlined in the words your card uses, not the library's:
*heart attack* underlines where you wrote it, and the popup opens under
*Myocardial infarction*. A phrase still matches when a tag runs through
it, so `<b>ectopic</b> pregnancy` is one term rather than two halves.

You can add your own terms under **Settings → General → Custom terms**.
They are matched ahead of everything shipped, so a term you define wins
over the library's reading of it.

#### What a popup carries

About 2,800 conditions carry a written summary rather than a first
paragraph lifted from an article: definition, aetiology, investigations,
management, red flags, Australian notes, PBS status and the rest of a
fixed list of section labels. Most of those headings are clickable and
open the article at that heading.

147 entries open a named document instead of a search. 95 point at an
Australian source - RANZCOG, Safer Care Victoria, KEMH, RACGP, the
Immunisation Handbook, STI Guidelines Australia, ANZCOR, NHMRC, the TGA -
and 52 at a specific StatPearls chapter. The popup's button says which,
so you know what you are about to open before you open it.

2,800 conditions also carry UpToDate searches, 4,288 of them, as green
pills under the summary. They need your own subscription.

Six accent colours say where a popup came from, including one for
summaries written for this add-on that have no chapter behind them, so
the badge is not the only thing distinguishing them.

Hovering is intent-based rather than instant: a mark has to hold the
pointer for 70 ms before it takes over from an open popup, and a pointer
travelling towards that popup keeps it for up to 600 ms whatever it
passes over. Double-clicking or dragging a selection across an
underlined term copies the word rather than opening anything.

#### Where a click lands

**Open sources in**, under Settings → General, chooses between the
sidebar and your browser. It applies to whatever the sidebar can host:
StatPearls, DrugBank, abbreviations, and custom terms pointing at a host
the add-on already trusts. Everything else opens in your normal browser,
which is most of the rest: the Wikipedia databases above, and the
Australian guideline sites behind the 147 named sources. UpToDate links
always open in the UpToDate dock.

Links written into your own cards are checked against the same host list
before anything opens. An unrecognised one goes to your browser rather
than into a dock holding your institutional session.

### The docks

Three separate docks, side by side, each with its own toggle. All three
can be open at once.

- **StatPearls / DrugBank** - reference browsing, with pills to switch
  between the two. Popup articles open here. Terms are underlined and
  explained on article pages too, exactly as they are on cards. A search
  that resolves to a single match jumps straight to it, DrugBank's
  signup banner is hidden and so is NCBI's Bookshelf bar over the search
  page, and the dock reopens on the article you left it on.
- **UpToDate** - your own institutional subscription, signed into once
  and remembered. Set your entry URL under Settings → Services if your
  institution uses an SSO proxy. The session is kept alive while you are
  actually using Anki, and when it expires anyway the dock opens itself
  at the login page rather than failing quietly. With the dock open,
  each new card searches for its front field.
- **AI chat** - your existing browser session with Claude, Perplexity,
  ChatGPT, Gemini, Copilot, DeepSeek, Grok or Duck. No API key, no
  account of ours, nothing is sent anywhere on its own. A self-hosted
  endpoint can be added as a ninth. A CSS rule hides the upgrade banners.

`Ctrl+Shift+K` sends the current text selection to the chat and
`Ctrl+Shift+J` sends the whole visible card: the dock opens, the message
box is focused, and the text is pasted through Qt's own paste so the
site's editor handles it the way it handles yours. **Nothing is
submitted - pressing Enter is always your keystroke.**

### Relevant articles

The dock lists articles matching terms found on the current card, ranked
by how central each term is to it: whether it appears in the card's
first field, how often, how early, and how specific it is. Only
conditions and drugs are listed. The other databases are underlined on
the card but have no article to offer.

It is a guess, so its header collapses to a strip you can click to bring
it back. That is a judgement about the list rather than about one card,
so it is remembered until you expand it again.

---

## Reference database

The term library ships inside the add-on and works offline. It also
updates itself, because the thing you would most want corrected quickly
is a wrong dose or a superseded threshold, and an AnkiWeb release is the
wrong unit for that.

Once per Anki launch, on a background thread, the add-on fetches a small
manifest from GitHub. Only if that manifest advertises newer content
built for a schema this version understands does it download the library
itself. What arrives is checked against the sha256 and the byte count the
manifest declares, parsed as JSON, validated for structure, and required
to carry the version the manifest advertised, before any of it is kept.
Anything that fails is discarded in favour of the copy you already have.

A new library takes effect at the next Anki launch rather than mid
session: the matcher is built once at import, and swapping the data under
a running reviewer would leave the two disagreeing.

**Settings → General → Reference database** holds the switch, the
version in use, and a **Check now** button. Turned off, the add-on makes
no content request at all.

---

## Install

From [AnkiWeb](https://ankiweb.net/shared/info/720072719), or download
the `.ankiaddon` from
[Releases](https://github.com/mord58562/theankidote/releases) and open
it with Anki.

Qt 6 is required. The package installs from Anki 2.1.50 upwards and the
code is kept compatible with it, but development is against current
Anki, so that is where it is exercised. Some features need newer Qt: the
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

These bindings are global, so that they work while the reviewer holds
focus in a webview. That rules two things out. Escape cannot be bound,
with or without a modifier, and neither can a bare key without one,
which would fire while you were typing. Either would be taken from Anki
everywhere. A field set to one is left at its previous value, and one
saved by an older version is cleared at the next launch, with a message
saying which binding went and why.

---

## Settings

**Tools → The AnkiDote → Settings**, in four tabs:

- **General** - which modules are active, reference-popup behaviour and
  custom terms, the reference database switch with the version in use
  and a Check now button, toolbar button order, and whether the docks
  reopen at the next Anki launch.
- **Services** - UpToDate institution URL, AI chat provider and paste
  behaviour.
- **Shortcuts** - every binding, editable.
- **Advanced** - verbose logging, the diagnostic log, and a web
  inspector for the sidebar webviews.

Everything writes on close, matching Anki's own Preferences. Every
setting also has a config key; see [config.md](config.md).

A welcome dialog runs once on a fresh install and can be run again from
**Tools → The AnkiDote**.

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
- **Network access** covers the sites you are browsing - StatPearls,
  DrugBank, UpToDate and your chosen chat provider - plus NCBI when
  resolving an article link.
- **The reference database** adds GitHub, on by default:
  `raw.githubusercontent.com` for the manifest, and `github.com` with
  `release-assets.githubusercontent.com` for the library file it points
  at, downloaded only when the manifest advertises a newer one.
  `objects.githubusercontent.com` is accepted as well, since that is
  where the file used to be served from. The requests are plain HTTPS
  GETs carrying nothing about you, and turning the switch off under
  **Settings → General → Reference database** stops them entirely.

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
python3 tests/test_reviewer.py      # matching, marking, popup payloads
python3 tests/test_toolbar_order.py
```

Run them as scripts rather than under `pytest`: collection imports
`__init__.py`, which imports `aqt` at module scope, and every file
errors out before a test runs.

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
study. It is not a clinical decision tool and carries no warranty - 
check current guidance before acting on anything you read here.

Version history is in [CHANGELOG.md](CHANGELOG.md).
