# What's new in The AnkiDote 2.2

## Cards render faster

Every card is scanned for terms twice, once for the question and once
for the answer. That scan took about 33ms per card. It now takes about
2.5ms.

The cause was a job half finished. Version 2.1 replaced the way terms
are found, swapping one enormous pattern for an index, because the old
approach got slower as the database grew and the database was about to
grow a lot. Five of the seven vocabularies were moved across. Two were
missed, and quietly kept paying the old cost. Between them they
accounted for nearly three quarters of the time a card scan took, and
one of them alone cost more than the other six put together.

Startup is also about 40ms quicker, from removing three large patterns
that nothing had read since 2.1.

You are unlikely to *see* 30ms. What it buys is headroom: the database
can keep growing without the reviewer getting slower, which was the
whole point of the 2.1 change and is only now actually true.

## Twelve terms that could never be highlighted

`LR+`, `LR-`, `Compliance (respiratory)`, `Vitamin B12 (cobalamin)` and
eight others were in the reference database but could not be matched by
any card, ever. Their names start or end with a bracket or a plus sign,
and the old matching rule had no way to recognise a term that does not
begin and end with a letter.

They now match where the term ends a field, which is the common case for
a cloze answer. They still will not match mid-sentence before a space -
that is the same word-boundary rule every other vocabulary follows, and
this change brings these terms in line with the rest rather than giving
them a special one.

This surfaced from testing the speed change above rather than from
anyone noticing, which is worth being honest about: nothing reported it,
because a term that never highlights looks exactly like a term you have
not written a card about.

## Fewer popups scroll

Reference popups have a height limit, and it was set too low. Not by a
little: 883 of the 2,429 entries in the library, more than a third,
rendered a scrollbar. The limit is now 900px instead of 620px, and 203
entries still scroll rather than 883.

The reason it was wrong is worth stating, because it explains why this
was never noticed. The limit was chosen against an internal estimate of
how tall each popup would render, and that estimate measured the summary
text and nothing else. It did not count the source label at the top, the
entry title, the UpToDate links, or the "Open article" button at the
bottom - about 110px of the popup that is there on every single one, and
more when UpToDate links are present. So the estimate said a popup
fitted and the popup scrolled, and every decision about entry length had
been made against that number.

Teriparatide was the entry that surfaced it. The estimate put it at
488px against a 620px limit, comfortably inside, and it scrolled anyway.
It is 650px.

Nothing about the content changed. The same summaries are simply allowed
the room they were always taking.

One thing the higher limit cannot fix: the popup never grows past the
space above or below the word you hovered. On a short window that space
decides, not the limit, and a long entry will still scroll there.

## Provider icons in the toolbar

The AI chat button shows the current provider's icon, captured from that
provider's own page the first time you open it. The capture rule kept
the first icon of a page load and threw away the rest, but a page sends
several - a small placeholder first, the real one last. If the first was
a placeholder, that placeholder became your toolbar icon and stayed
there, because the capture is preferred over the logo shipped with the
add-on.

The add-on now keeps the icon a page settles on rather than the first
one it sends, and refuses anything too small to be a real icon.

If yours already looks wrong, **Settings > AI chat > Reset provider
icons** discards the captures and falls back to the bundled logos. They
are captured again next time you open that provider.

---

**Upgrading:** nothing to do. Your settings, shortcuts and dock layout
carry over untouched, and the reference database is unchanged.

## Five drugs are now shown under their current Australian name

The heading on a drug popup should be the name on the box. For five
drugs it was not.

`lignocaine` is now **lidocaine** and `oestradiol` is now **estradiol**.
These went the other way in 2.1.1, on the reasonable-sounding grounds
that lignocaine and oestradiol are what Australians say. They are - but
they are not what the TGA approves any more. Lignocaine was dual
labelled as `lidocaine (lignocaine)` and the transition to the sole name
closed on 30 April 2026, so a medicine supplied in Australia since then
carries `lidocaine` alone. Oestradiol to estradiol was filed as a minor
spelling change and never had a transition period at all.

`phenobarbitone` is now **phenobarbital** and `beclomethasone` is now
**beclometasone**, both for the same reason.

`cysteamine` is now **mercaptamine (cysteamine)**, brackets included,
because that is the approved name in full. The TGA keeps this one dual
labelled permanently: mercaptamine and mercaptopurine are a look-alike,
sound-alike pair - one for cystinosis, one for leukaemia - and the
bracketed old name is what keeps them apart at the point of prescribing.

**Nothing you have written stops working.** Every old spelling still
matches and opens the same popup. Only the heading changed.

While checking this, one popup turned out to have been broken since
2.1.1: the oestradiol entry was a single line telling you to see the
estradiol entry, which the same change had deleted. It has been
rewritten properly.

## Thirty-four drug summaries rewritten

Insulin, thiamine, prednisolone, methotrexate, aspirin, hydrocortisone,
amiodarone, haloperidol, metronidazole, risperidone, diazepam,
gentamicin, spironolactone, ceftriaxone, heparin, doxycycline,
aripiprazole, furosemide, metformin, warfarin, naloxone, sertraline,
venlafaxine, clozapine, lithium, lamotrigine, sodium valproate,
carbamazepine, olanzapine, quetiapine, estradiol, phenobarbital,
beclometasone and mercaptamine (cysteamine).

Most of these were four lines long. Prednisolone, which appears on more
of your cards than almost anything else, was three sentences telling you
to go and read the prednisone entry.

**The word `insulin` did not highlight at all.** Six specific insulins
were in the database - glargine, detemir, lispro, aspart, isophane,
degludec - but not the plain word, which is what your cards actually
say. It is now there, covering the types, the regimens, hypoglycaemia
and sick-day rules. `insulin glargine` and the rest still open their own
entries.

The reference database has always been better at diseases than at drugs,
and the reason turned out to be structural rather than editorial: there
was no way to edit a drug summary from the source tree at all. There is
now, so drug entries can be improved and delivered the same way disease
entries have been since 2.0 - in the background, without waiting for an
add-on update.

The clozapine entry is the one worth flagging. It carried the American
haematological monitoring schedule, which is not what any Australian
service runs, and contradicted itself about the myocarditis window. Both
are fixed.

`epinephrine` and `norepinephrine` now match too, showing the
adrenaline and noradrenaline entries. Australian ampoules are required
to print both names, so cards written off a label were finding nothing.

## Drug class names now highlight

`antipsychotics`, `antibiotics`, `benzodiazepines`, `NSAIDs`,
`diuretics`, `opioids`, `corticosteroids`, `antidepressants`,
`anticoagulants`, `beta blockers` and `statins`.

None of these matched anything before, in any vocabulary. That turned
out to matter more than any individual drug: `antipsychotic` appears on
55 of your cards, which is more than any single drug name measured. Each
one now gives a class overview - how the class is subdivided, what
actually drives the choice between members, and the side effects that
belong to the class rather than to one drug.

The pattern is the same one behind the insulin gap. A word that never
highlights looks exactly like a word nobody has written a card about, so
it is never reported. These were found by going looking.

## Glyceryl trinitrate opens its DrugBank page again

Since 2.1.1 the GTN popup button opened a DrugBank search instead of the
monograph, because the drug was renamed and its DrugBank reference was
left behind under the old name. Fixed, and the same class of mistake now
fails the build rather than shipping.

