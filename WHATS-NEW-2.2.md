# What's new in The AnkiDote 2.2

A large release. 2.1.1 was the last AnkiWeb push, and everything since
then - a security fix, faster card rendering, a matcher overhaul, a
long round of Australian drug names, custom-term popups that identify
themselves, an acronym popup fix, and about 130 new condition summaries
- lands here as 2.2.

If you had auto-update on for the reference database, most of the
content changes have already reached you in the background since 2.1.1.
This release captures them alongside the code changes.

## Card rendering is 13x faster

Every card is scanned for terms twice, once for the question and once
for the answer. That scan took about 33ms per card. It now takes about
2.5ms.

Version 2.1 replaced the way terms are found, swapping one enormous
regular-expression pattern for an index, because the old approach got
slower as the database grew and the database was about to grow a lot.
Five of the seven vocabularies were moved across. Two were missed and
quietly kept paying the old cost - between them they accounted for
nearly three quarters of the time a card scan took, and one alone cost
more than the other six put together. Both are now on the index.

Startup is also about 40ms quicker, from removing three large patterns
that nothing had read since 2.1.

You are unlikely to *see* 30ms. What it buys is headroom: the database
can keep growing without the reviewer getting slower, which was the
whole point of the 2.1 change and is only now actually true.

## A security fix in the sidebar

The sidebar holds your logged-in NCBI, DrugBank, UpToDate and AI chat
sessions. Which pages it is allowed to open has been decided by
provenance since 2.1, but the check and the browser disagreed about one
character, and a deck downloaded from AnkiWeb could exploit that to
point the sidebar at any site it liked, with your sessions attached.

Nothing suggests this was ever used. It was found by looking, not by
anyone hitting it, and it is now closed.

Two related content-download defects were fixed in the same review: a
corrupt download that could stop the add-on loading (recovery meant
deleting a file by hand), and a race between two concurrent checks
that could leave a half-written database on disk. Both are silent bugs
that would show up rarely and confusingly, so they are worth naming
even though nothing user-visible changes.

## Twelve reference terms that could never be highlighted

`LR+`, `LR-`, `Compliance (respiratory)`, `Vitamin B12 (cobalamin)` and
eight others were in the reference database but could not be matched by
any card, ever. Their names start or end with a bracket or a plus sign,
and the old matching rule had no way to recognise a term that does not
begin and end with a letter.

They now match where the term ends a field, which is the common case
for a cloze answer. They still will not match mid-sentence before a
space - that is the same word-boundary rule every other vocabulary
follows, and this change brings these terms in line with the rest
rather than giving them a special one.

## Custom Terms popups say CUSTOM instead of STATPEARLS

A term from **Settings → General → Custom terms…** used to pop up
looking exactly like a StatPearls result - same teal badge, same
layout, no way to tell it apart from the reference database at a
glance. `source` was meant to drive this, but the popup only ever
recognised four fixed values and treated everything else - including
every custom term - as StatPearls.

Custom terms now badge themselves **CUSTOM** in a distinct hue that
belongs to neither StatPearls' teal nor DrugBank's amber, so a custom
popup reads as custom before you have read a word of it. The "Open
article →" button says "Open link →" for the same reason. Each custom
term can also carry its own label instead of the generic one -
**Custom terms…** has a new optional **Label** column, so you can
write "Reddit" or "Lecture notes" or whatever the source actually is,
and the badge shows that.

The badge colour is tuned separately for light and dark mode so it
holds up in both.

## Short custom terms now highlight

Custom Terms added a term but nothing in the reviewer ever showed it
if the term was under four characters and "Match case" was unticked.
No error, no indication - just no popup, ever.

Any highlight term under four characters, matched without "Match
case", was being silently dropped everywhere in the add-on, custom
terms included. That rule exists to stop a short common word from
lighting up constantly through the reviewer - without it, a
case-insensitive two-letter term would match inside ordinary prose
throughout every card. It was never meant to apply to a term someone
typed into the Custom Terms table by hand: that is a deliberate choice
by the user, not something the add-on resolves on its own. Custom
terms are now exempt from the filter regardless of length or "Match
case". Everything else - acronyms, drug names, condition names - is
unaffected.

## The AI chat dark mode reaches everything now

Every StatPearls / DrugBank result in the AI chat panel's RELEVANT
ARTICLES list kept a white background and navy text no matter what
theme Anki was running - five colours were hardcoded to the light
palette and never read the dark flag at all. Switching Anki to dark
mode restyled the rest of the sidebar and left that one list looking
like a hole punched through it. It now follows Anki's theme, including
on a live switch mid-session.

## Acronym popups stopped repeating themselves

When an acronym's expansion matches a known condition - HHS to
Hyperosmolar hyperglycaemic state, MI to Myocardial infarction, and so
on - the popup shows that condition's full summary instead of the
acronym's own short description. The title already read "HHS -
Hyperosmolar hyperglycaemic state", but the body used to open with
"HHS = Hyperosmolar hyperglycaemic state." before getting into the
actual content, restating what the title had just said. The body now
starts straight into the summary.

## Fewer popups scroll

Reference popups have a height limit, and it was set too low. 883 of
the 2,429 entries in the library, more than a third, rendered a
scrollbar. The limit is now 900px instead of 620px, and 203 entries
still scroll rather than 883.

The reason it was wrong is worth stating, because it explains why this
was never noticed. The limit was chosen against an internal estimate
of how tall each popup would render, and that estimate measured the
summary text and nothing else. It did not count the source label, the
entry title, the UpToDate links, or the "Open article" button - about
110px of the popup that is there on every single one, and more when
UpToDate links are present. So the estimate said a popup fitted and
the popup scrolled, and every decision about entry length had been
made against that number. Nothing about the content changed. The same
summaries are simply allowed the room they were always taking.

One thing the higher limit cannot fix: the popup never grows past the
space above or below the word you hovered. On a short window that
space decides, not the limit, and a long entry will still scroll
there.

## Provider icons in the toolbar

The AI chat button shows the current provider's icon, captured from
that provider's own page the first time you open it. The capture rule
kept the first icon of a page load and threw away the rest, but a page
sends several - a small placeholder first, the real one last. If the
first was a placeholder, that placeholder became your toolbar icon and
stayed there, because the capture is preferred over the logo shipped
with the add-on.

The add-on now keeps the icon a page settles on rather than the first
one it sends, and refuses anything too small to be a real icon. If
yours already looks wrong, **Settings > AI chat > Reset provider
icons** discards the captures and falls back to the bundled logos.
They are captured again next time you open that provider.

## Five drugs shown under their current Australian name

The heading on a drug popup should be the name on the box. For five
drugs it was not.

`lignocaine` is now **lidocaine** and `oestradiol` is now **estradiol**.
These went the other way in 2.1.1, on the reasonable-sounding grounds
that lignocaine and oestradiol are what Australians say. They are -
but they are not what the TGA approves any more. Lignocaine was dual
labelled as `lidocaine (lignocaine)` and the transition to the sole
name closed on 30 April 2026, so a medicine supplied in Australia
since then carries `lidocaine` alone. Oestradiol to estradiol was
filed as a minor spelling change and never had a transition period at
all.

`phenobarbitone` is now **phenobarbital** and `beclomethasone` is now
**beclometasone**, both for the same reason. `cysteamine` is now
**mercaptamine (cysteamine)**, brackets included, because that is the
approved name in full - the TGA keeps this one dual labelled
permanently, since mercaptamine and mercaptopurine are a look-alike,
sound-alike pair and the bracketed old name is what keeps them apart
at the point of prescribing.

**Nothing you have written stops working.** Every old spelling still
matches and opens the same popup. Only the heading changed.

## More Australian drug names that now highlight

2.1.1 added twenty-three drug aliases that had been matching nothing.
This release takes the rest of the TGA's own list of updated
ingredient names - twelve more rows where the old spelling was in the
wild and the new name was already in the database:

`benzhexol`, `flupenthixol`, `dexamphetamine`, `hydroxyurea`,
`eformoterol`, `glycopyrrolate`, `chlorpheniramine`, `cholestyramine`,
`clomiphene`, `ethinyloestradiol`, `actinomycin D`, plus
`benzatropine` as a rename of the American `benztropine`. Textbooks,
older lecture slides and ward protocols still use the left-hand form
freely, so a card written from any of them used to show no popup at
all.

## Thirty-four drug summaries rewritten, plus insulin and drug classes

Insulin, thiamine, prednisolone, methotrexate, aspirin, hydrocortisone,
amiodarone, haloperidol, metronidazole, risperidone, diazepam,
gentamicin, spironolactone, ceftriaxone, heparin, doxycycline,
aripiprazole, furosemide, metformin, warfarin, naloxone, sertraline,
venlafaxine, clozapine, lithium, lamotrigine, sodium valproate,
carbamazepine, olanzapine, quetiapine, estradiol, phenobarbital,
beclometasone and mercaptamine (cysteamine).

Most were four lines long. Prednisolone, which appears on more of your
cards than almost anything else, was three sentences telling you to go
and read the prednisone entry.

**The word `insulin` did not highlight at all.** Six specific insulins
were in the database - glargine, detemir, lispro, aspart, isophane,
degludec - but not the plain word, which is what your cards actually
say. It is now there, covering the types, the regimens, hypoglycaemia
and sick-day rules.

The clozapine entry is the one worth flagging. It carried the American
haematological monitoring schedule (which is not what any Australian
service runs) and contradicted itself about the myocarditis window.
Both are fixed.

`epinephrine` and `norepinephrine` now match too, showing the
adrenaline and noradrenaline entries. Australian ampoules are required
to print both names, so cards written off a label used to find
nothing.

## Drug class names now highlight

`antipsychotics`, `antibiotics`, `benzodiazepines`, `NSAIDs`,
`diuretics`, `opioids`, `corticosteroids`, `antidepressants`,
`anticoagulants`, `beta blockers` and `statins`. None of these matched
anything before, in any vocabulary. `antipsychotic` alone appears on
55 of your cards, which is more than any single drug name measured.
Each one now gives a class overview - how the class is subdivided,
what actually drives the choice between members, and the side effects
that belong to the class rather than to one drug.

## About 130 new condition summaries

Bacterial meningitis, delirium, sepsis, HIV, syncope, acute kidney
injury, hypoglycaemia, gestational diabetes, rubella, GORD, postpartum
haemorrhage, measles, chronic kidney disease, varicella, tuberculosis,
heart block, menopause, obstructive sleep apnoea, Kawasaki disease,
supraventricular tachycardia, eclampsia, uterine fibroids, croup,
eating disorders, bipolar disorder, sarcoidosis, PTSD, metabolic
acidosis, and roughly a hundred more.

The condition side of the library was thinner than the drug side, and
this release fixes that where it matters. Each new entry is written to
the same structured Label pattern the shipped entries use, so section
headings turn into the same click targets and long lists render as
bullets. Australian guidance is preferred where it differs from the
US default - eTG antibiotic regimens, RACGP, RANZCOG, RANZCP, ADIPS,
NIP, Austroads, PBS listings.

## Glyceryl trinitrate opens its DrugBank page again

Since 2.1.1 the GTN popup button opened a DrugBank search instead of
the monograph, because the drug was renamed and its DrugBank reference
was left behind under the old name. Fixed, and the same class of
mistake now fails the build rather than shipping.

## Settings is quieter

The three module switches are now three plain checkboxes. The captions
underneath two of them said what the checkbox label already said, so
they have gone.

---

**Upgrading:** nothing to do. Your settings, shortcuts, dock layout
and any custom terms carry over untouched. If you had
`libraryAutoUpdate` on since 2.1.1, most of the content changes have
already reached you in the background; this release bundles them into
the .ankiaddon for new installs and for anyone with auto-update off.
