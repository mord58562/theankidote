# What's new in The AnkiDote 2.8.0

Two things that had been quietly limiting what the add-on could see and
what it could be given, plus the largest content batch so far.

## Abbreviations written out in full

If a card said "CRP", you got a popup. If the same card said
"C-reactive protein", you got nothing. Same term, same explanation
sitting behind it, and no way to tell from the outside why one worked
and the other did not.

That was true of 272 of the 485 abbreviations in the list. The matcher
was built from the short forms only, so every spelled-out form was
invisible to it.

Both forms are now recognised. A card that writes the abbreviation once
and the full term later gets both underlined; a card that only spells it
out does not get a stray three-letter match added on top. The popup is
headed the same way either way, so "CRP - C-reactive protein" is what
you see whichever the card used.

Forty phrases are deliberately left alone. "Emergency department",
"heart rate", "per os" and the like are ordinary clinical prose, and
underlining them everywhere would be noise rather than help. Eleven more
carry an editorial note in brackets that no real card contains.

Where a term has both a full entry and an abbreviation entry, the fuller
one still wins.

## The term library can grow

The library updates itself separately from the add-on, and the updater
carried a maximum size it was willing to download. That figure was
chosen when the library was a few hundred kilobytes, and had already
been raised once. The library reached 93 per cent of it this week.

Had it been crossed, nothing would have appeared to go wrong. Downloads
would simply have stopped, every install would have kept the copy it
already had, and new content would have quietly stopped arriving.

The ceiling is now high enough that content will not reach it. Nothing
about the safety of the update changes: the download is still bounded by
the size the library file declares for itself, still has to match a
checksum published alongside it, and still has to come from an approved
address before any of it is read.

## Content

124 new entries, and 150 alternate names for entries that already
existed.

The alternate names are the larger change in practice. Terms were
matched exactly, and a course does not always use the same words a
textbook does. A card saying "cervical screening" found nothing, because
the entry was filed under "cervical screening test". "Fetal death" found
nothing, because the entry is "stillbirth". "Perineal laceration" found
nothing, because the entry is "perineal tear". Around a hundred and
fifty of those now resolve.

Measured against the Year 4 Australian curriculum frameworks, the number
of topics with no entry at all fell from 188 to 92 across Medicine,
Obstetrics and Gynaecology, Paediatrics and Psychiatry. Most of that gap
was never missing content. It was the wrong words.

New entries include obstetric and gynaecological history taking,
fertilisation and cervical dilatation, support in labour, first
trimester drug risk, genetic counselling, liver function test
interpretation, proton pump inhibitors, unintentional weight loss,
fatigue, abdominal distension, infective dysentery, change in bowel
habit, cutaneous paraneoplastic syndromes, herd immunity, health
literacy, the Australian cancer screening programs, gender-affirming
hormone therapy, pain at the end of life, intellectual disability,
hearing loss in children, joint pain and swelling in children, and older
persons mental health.

The term library updates itself, so the content arrives on your next
launch whether or not you update the add-on.
