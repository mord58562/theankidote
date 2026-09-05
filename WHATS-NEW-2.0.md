# What's new in The AnkiDote 2.0

## Popups fit

Short lists are set as sentences now instead of bullets. That sounds
cosmetic and isn't: a bullet occupied a whole line however little it
held, so `Causes: A; B; C` spent about 60 pixels saying what fits on one
22-pixel line. Across the reference database this was the single largest
cause of popups that overflowed and scrolled.

Lists still bullet where bullets earn their space - four or more items,
at least one of them long enough to be worth scanning for.

Nothing was shortened to achieve this. On the layout change alone, the
tallest condition popup dropped from about 1,200 pixels to 995, and 40
conditions and 29 drug entries came back inside the popup.

## Fourteen conditions rewritten

Vasculitis, pleural effusion, acute liver failure, septic arthritis,
colorectal cancer, anorexia nervosa, peptic ulcer disease, hypokalaemia,
aortic dissection, rhabdomyolysis, infective endocarditis, coeliac
disease, ankylosing spondylitis and serotonin syndrome.

These were chosen by how often each comes up in real use rather than by
how badly each overflowed. The two orderings turned out to disagree
almost completely: the tallest entries in the whole database were
conditions like Fournier gangrene, tularaemia and pellagra, which almost
nobody has a card about.

Australian sources throughout - eTG, the National Bowel Cancer Screening
Program, PBS criteria for biologics, eviQ protocols.

## Eight popups were titled something other than what they described

A summary written about community-acquired pneumonia appeared under the
heading "Pneumonia". One written about acute coronary syndrome appeared
under "Myocardial infarction". The text was narrower than the heading
claimed, and nothing flagged it because the popup was otherwise working
exactly as designed. All eight corrected.

## The reference database can now update itself

Every condition, drug, acronym and sign used to live inside the add-on's
Python code, which meant a correction - a wrong dose, a superseded
guideline - could only reach you as a new AnkiWeb release, reviewed and
then waited for. The database is now a separate data file, and can be
updated on its own.

This is on by default, and the switch is in **Settings → General →
Reference database**, along with the content version currently in use
and a "Check now" button. Turning it off stops all content-related
network activity; nothing else about the add-on needs an internet
connection.

With it on, the add-on checks a small version file at startup on a
background thread, and only downloads anything if newer content exists
that this version knows how to read. What arrives is checked against a
published checksum and validated before it is kept; anything that fails
is discarded in favour of what you already have. Updated content applies
at the next Anki launch rather than mid-session.

Only reference text is downloaded. Nothing about your collection, your
cards or your review history is sent anywhere.

Downloaded content is only ever read as data. It is never imported,
executed, or unpickled. You can point `libraryManifestUrl` at your own
copy if you would rather control what your install receives.

## Under the hood

The test that was supposed to stop oversized summaries shipping had
never looked at most of them - it checked the rewritten entries, the
acronyms and the drugs, but not the several hundred conditions still
carrying their original text, which is where the length actually was. It
now checks every summary the popup can render, and a second test pins
the backlog of oversized entries so it can only shrink.

---

**Upgrading:** nothing to do. Your settings, shortcuts and dock layout
carry over untouched.

*2.0.1 adds the Settings control described above, turns updates on by
default, moves the "Note" line to the bottom of the popup where it
belongs (it was appearing above "Red flags"), and drops the upgrade
popup that 2.0.0 showed on first launch.*
