# What's new in The AnkiDote 2.3.3

A small release on top of 2.3.2, tightening a few popup behaviours.

## Roman-numeral acronyms no longer hijack context

"Rome IV", "DSM-IV", "type IV collagen" and "grade IV" used to make
the sidebar underline the trailing "IV" as if it meant intravenous.
The matcher now checks the word before a bare Roman numeral, and
skips the acronym when the numeral follows a classifier ("Rome",
"DSM", "type", "grade", "class", "stage", "NYHA", "factor", "cranial
nerve", and the rest). Same fix covers II, III, VI through XII.

## Drug titles are capitalised

Drug popups titled themselves in whatever case the match text used,
so a card that read "desmopressin" led to a popup titled
"desmopressin". Titles now capitalise the first letter regardless of
how the term appeared in the card.

## Extra section labels are recognised

Popups render a handful of prefixed section labels ("Aetiology:",
"Clinical features:", "Ix:", "Mx:", "Note:") as headings with the
following content bulleted. "Grading:" and "Sites:" now render the
same way instead of running through as body text.

## New topic popups can arrive between add-on releases

Popups for topics that were not in the original term library used to
need a full add-on release before they would highlight and link at
all. New topics can now ship through the content channel as stubs
(name plus StatPearls link) and the sidebar will pick them up on the
next Anki launch; the rich summary text follows in a later content
update. This is transparent - you keep seeing the popups you already
had, plus new ones as they land.

---

**Upgrading:** nothing to do. Your settings carry over untouched.
The reference database keeps updating itself in the background as
before.
