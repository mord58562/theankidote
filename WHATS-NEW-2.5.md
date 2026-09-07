# What's new in The AnkiDote 2.5

Two kinds of dishonesty in the popup, both fixed.

## The sidebar highlights terms as well

Until now the underlines and popups only appeared on your cards. Open a
StatPearls or DrugBank article in the sidebar and hit a term you do not
know, and you were on your own. Those pages are now marked up the same
way, with the same popups, drawn from the same library - so a term you
meet while reading about something else is one hover away, in the panel
you are already in. Clicking through follows the link in the sidebar
rather than opening a browser.

It can be turned off in Settings if you would rather read the page
clean.

## Eponyms with apostrophes work again

If a card said "Addison's disease" and the apostrophe was the curly one
your editor inserts automatically, the add-on saw a different word and
showed nothing. That was true of every one of the 107 terms in the
library with an apostrophe in it - Crohn's, Bell's, Graves', Meniere's -
and it failed silently, so there was nothing to notice except an
absence. Both forms are now treated as the same character.

## Popups no longer promise articles that do not exist

Every condition popup carried a StatPearls badge and an "Open article"
button. Only about a quarter of them actually have a StatPearls article
behind them. For the rest the button ran a search, which is how a popup
headed "Notifiable disease" came to offer an article about it - there
isn't one, because notifiable disease is an Australian statutory idea
and StatPearls is American.

The badge was wrong in the same way. Those summaries are not from
StatPearls; they were written for this add-on. So the badge now says so,
and the button says what it will really do - search StatPearls, search
Wikipedia, search DrugBank - unless there is a genuine article waiting,
in which case nothing has changed. About 2,600 popups stop overstating
themselves.

## Acronyms that are also ordinary words stay quiet

A card reading "1st line: [...] OR [...]" was showing a popup for the
operating room. The same went for "ALL patients", "at ALL ages" and a
handful of others: OR, ALL, PET, CAP, TEN, MEN, ARM, BED, MAP, AS and
LAST are all real medical acronyms and all ordinary English words, and
each of them expanded the moment it appeared in capitals.

They now expand only when the card also contains something from the
subject they belong to. "Taken to OR under general anaesthesia" still
resolves; "nifedipine OR indomethacin" does not. Across a 6,000-card
collection this removed about 110 wrong popups while keeping the 80
correct ones.

## And the same problem, much bigger, elsewhere

Chasing that bug turned up a worse one. Two entries in the physiology
vocabulary were reachable by the bare words "or" and "if" - the odds
ratio and intrinsic factor - and that vocabulary matches without regard
to capitals. So the ordinary conjunction was underlining itself and
offering a statistics popup on nearly every card that used it. The
single letter "F" did the same for bioavailability, and "affect" the
verb collided with affect the psychiatric sign.

Every term in the add-on, all 11,687 of them, was checked against a
dictionary of English words. Nine had this problem. All nine now need
their subject to be somewhere on the card before they will open
anything. On a 6,000-card collection that is about 3,600 fewer wrong
popups.

## The download stops carrying my notes

Every release up to this one packaged the working documents from the
sessions that built it: checkpoints, coverage measurements, audit
transcripts, and the briefing file for the scheduled agent that writes
content. That was 422 KB of a 3.1 MB download, and most of it was a
stale copy of summaries the add-on already carries properly in its term
library, so you were downloading much of the same content twice, once in
a form nothing reads.

None of it was ever loaded by the add-on. It just travelled with it.

The package now ships what runs and the release notes, and nothing else.
Even with a large batch of new terms added in the same release, the
download is smaller than the last one was. Nothing you can see or use
has been removed.

## Smaller things that were quietly wrong

Pressing Escape to dismiss a popup also dropped you out of the
reviewer, because the key reached Anki as well.

Resizing the AI chat dock reloaded the page. Dragging the splitter
while a conversation was open threw the conversation away, and a
half-typed message with it.

Popups opened over a StatPearls or DrugBank page in the sidebar were
always styled light, whatever your theme, because they were looking for
a signal that only exists on a card.

Searching from an acronym's expansion used Australian spelling against
a database that only indexes American, so "oesophageal varices" found
nothing.

Opening an article by clicking a popup hid the article list entirely,
and the header that brings it back went with it, so the only way back
was to close the sidebar and open it again. It collapses now. That path
also never remembered which article you were reading, while pressing
Home did not forget the one you had just left - so the next card
brought it back.

A popup stayed on screen when you flipped a card over, hanging above
content it no longer described, and one opened near the bottom of the
window ran off the edge.

If a content update fails - no network, a bad download - you are now
told. Before, it went to a log file, which was itself not being
written: Settings has always offered to reveal a diagnostic log that
never existed. It does now.
