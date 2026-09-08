# What's new in The AnkiDote 2.6

Several things this add-on has always claimed to do, it has never
actually done. This release is mostly them.

## Terms you wrote as an alias are underlined now

The library knows that "heart attack" means myocardial infarction, that
"high blood pressure" means hypertension, and that frusemide and
furosemide are the same drug. It has always known. It just never
underlined any of them.

The alias was used to look the term up and then thrown away: what got
underlined was the primary name, so unless your card happened to spell
the term the same way the library did, nothing appeared. Of the 6,044
alternative names for conditions in the library, 5,457 do not contain
the primary name anywhere inside them, so none of those could ever be
marked. Nearly every drug alias was in the same position.

Your cards are now marked up in the words you wrote them in. The popup
still opens under the primary name, so "heart attack" underlines where
it sits and the popup is headed Myocardial infarction.

The one thing still missing is short abbreviations written on their own.
"HTN" on a card will not underline unless it is also in the acronym
table, because matching three-letter forms case-blind would light up
ordinary words in your prose. Moving those into the acronym table is
content work and it is on the list.

## Condition popups have an UpToDate row

824 of the 826 conditions in the library carry UpToDate links - Acute
Mx, HFrEF, Resistant, Pregnancy, whichever ones make sense for that
condition. The popup has had the code to draw them since the feature
was written.

It has never drawn one. The links were assembled correctly, the popup
read the right attribute, and the step in between quietly dropped them,
so every popup ever shown said it had none. If you have an UpToDate
subscription or institutional access, that row is worth a look now.

## A less-than sign no longer stops the highlighting

`Sodium < 130 in SIADH` marked nothing at all. Neither SIADH nor
hyponatraemia, even though both are in the library and both would have
been marked if the sentence had not contained a `<`.

The add-on treated every `<` as the start of an HTML tag, went looking
for the `>` that closes it, and on not finding one gave up on the rest
of the text. Anything after the first `<` in a paragraph was invisible
to it. This hit the sidebar hardest, where StatPearls and DrugBank prose
is full of `sodium <135` and `FEV1/FVC <0.70`.

The same fault ran the other way on cards: a `>` inside an image's alt
text ended the tag early and the add-on could write into the middle of
it. That is gone too.

## Your reference sidebar stops losing your place

Several separate faults, all of which cost you the page you were
reading:

The article list stopped following the card. Once you opened an article
from a popup, every later card kept showing the previous card's article
list, under the previous card's count, until you pressed the toolbar
button. Opening one article that way also silently changed a setting, so
the list stayed collapsed on every card afterwards and across restarts.

Clicking the DrugBank pill while already reading a DrugBank page
correctly kept you on the page, and then forgot it - so restarting Anki
opened the DrugBank home page instead of what you were reading.

Worst of the set: the sidebar could learn the wrong article permanently.
If a term failed to resolve and left you on a search page, whatever you
searched for next was recorded as the answer for the original term - so
clicking an Atrial fibrillation popup could open the Warfarin chapter,
from then on, across restarts, with nothing in the interface to undo it.

Drug pages also work properly. Roughly half the drugs in the library
have no direct DrugBank page and go through a search that resolves to
one exact match, and the step that was meant to follow that match had
never once run. You landed on the search results and picked it by hand,
every single time, because the result was never remembered either.

## Content updates were switched off more often than not

The add-on checks a small file on GitHub to see whether new reference
content is available. That file was being rewritten, without the address
of the content, by a routine part of the build - so for long stretches
every install checked, found an incomplete answer, and quietly did
nothing. Nineteen of the last forty updates to that file went out in
that state.

If you have had reference updates enabled and never seemed to get any,
that is why. It is fixed at the source, and there is now a test that
fails if it ever happens again.

## The chat sidebar

The option to hide upgrade banners on chat sites has been on by default
since it shipped and has never worked - the code that installed it was
not valid JavaScript and the browser refused it on every page load,
silently. It works now.

Sending a selected term to the chat box pasted it twice if it was eight
characters or shorter, which is most of what anyone sends: ECG, MASLD,
T2DM, sepsis, warfarin all arrived doubled. The button labelled "Reload"
did nothing at all; it reloads, and keeps your conversation rather than
starting a new one. And the chat sidebar now opens beside the other
panels instead of on top of whichever one you already had open.

## Smaller things you may notice

- The add-on wrote to Anki's settings file after every card you
  answered. It no longer does.
- The longer of two overlapping terms wins, so "G6PD deficiency"
  underlines as one term rather than losing to "G6PD".
- Terms ending in a bracket, like "Vitamin B12 (cobalamin)", match in
  the middle of a sentence and not only at the very end.
- A handful of terms that exist in two of the databases were sending you
  to the weaker one. Splenomegaly went to a Wikipedia search instead of
  StatPearls; glucagon went there instead of DrugBank.
- In light mode, a DrugBank popup was amber at the top and StatPearls
  teal everywhere else. The whole popup takes the colour of its source
  in both themes now.
- Double-clicking an entry in the article list opened it twice.
  Double-clicking a term on a card did the same.
- "Open in side panel" in Settings is now two labelled options, because
  its off state - open in your browser instead - was written only in a
  tooltip.
- The update check told you "Check failed" followed by a raw error from
  inside Python. It says what happened in words now.
- The Tools menu ticks agreed with Settings only until you changed
  something in Settings.

## Under the hood

Around forty defects in total, found by auditing the whole add-on
against itself. The test suite went from 164 checks to 185; twenty-one
of the new ones fail against 2.5.0, which is the point of them.

Nothing in this release changes the content format, so your reference
library carries over untouched.
