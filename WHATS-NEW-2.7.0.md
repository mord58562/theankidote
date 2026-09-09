# What's new in The AnkiDote 2.7.0

Mostly things that were quietly wrong in the popup and the reference
docks, found by using them rather than by reading the code.

## The popup

The button at the bottom of a popup used to scroll out of sight on any
entry long enough to need scrolling, which is most of them. It is
pinned to the bottom now. It has not moved, changed size or changed
what it says; it simply stays where it is while the text scrolls.

Section headings inside a popup could be clicked to jump to that
section of the chapter behind it. On an entry with no chapter, that
click ran a plain search and threw the section away, so it looked
broken because it was. The headings are now links only where there is
a chapter to land in.

Spacing has been reworked. The section labels were rendering dimmed,
because the fade meant for the body text sat on an element that
contained the labels as well, and nothing could lift it off them. They
are at full strength now, with more air between sections and less
between a label and the text under it. Popups are slightly shorter
than before rather than longer, so less scrolling, not more.

## Brand names and spellings

A brand name showed the generic's summary under the brand's heading
and never said the two were the same drug. Clopine gave clozapine's
entry with nothing to say so. Every brand name now states the
relationship in a line of its own, and so does every alternate
spelling, so frusemide says it is another spelling of furosemide
instead of silently showing a heading that disagrees with your card.

Twenty-one brand names are shared by more than one generic. Those were
resolving to whichever entry happened to be loaded later, which was
stable only by accident. Combination products now name the combined
entry.

## Terms that were being swallowed

Some entries carried an alternate name that included another entry's
name inside it. Because the longest phrase wins, that phrase ate its
neighbour: on a card asking for the positive symptoms of schizophrenia,
the word schizophrenia was absorbed and its own entry never appeared,
so hovering it gave the wrong popup. Five entries did this. They resolve
separately now, and the build refuses the pattern so it cannot come
back.

## The reference docks

StatPearls changed the address it hands out for an in-book search. The
add-on strips the surrounding site furniture from that results page,
but it was checking for the old address, so the page arrived with the
database dropdown, display settings and pagination stacked above the
results in a narrow dock. It is stripped again.

A DrugBank page no longer shows a popup for the drug whose page you are
already reading. Other drugs mentioned on the page still work as
before.

DrugBank's own promotional strip across the top of its pages is hidden
in the dock, as is the second loading bar it draws under ours.

The dock's loading bar could stay on screen at a partial fill if the
page's renderer died, since that path never reports the load as
finished. It now always clears.

## UpToDate

Clicking an UpToDate chip on a popup opened the public UpToDate site
rather than the address configured in settings. If you reach UpToDate
through an institutional proxy, your session does not exist on the
public site, so the article opened as an abstract with a sign-in
prompt, while pressing Home worked normally. Chips now open through
the same address as Home.

## Accessibility

Animated popup backgrounds now stop when the operating system is set
to reduce motion.
