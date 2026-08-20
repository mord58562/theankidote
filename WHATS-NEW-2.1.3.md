# What's new in The AnkiDote 2.1.3

Nothing you will see. This release came out of a full review of the
codebase and fixes three defects, none of which had ever been reported
because none of them is visible until it bites.

## A shared deck could hijack the sidebar

The sidebar holds your logged-in NCBI, DrugBank, UpToDate and AI chat
sessions. Which pages it is allowed to open has been decided by
provenance since 2.1, but the check and the browser disagreed about one
character, and a deck downloaded from AnkiWeb could exploit that to
point the sidebar at any site it liked, with your sessions attached.

Nothing suggests this was ever used. It was found by looking, not by
anyone hitting it, and it is now closed.

## A corrupt content download could stop the add-on loading

The add-on downloads its reference database rather than shipping it only
through AnkiWeb updates, and it checks that download before keeping it.
That check was not thorough enough: several kinds of malformed file
passed it, were saved, were preferred at every launch, and then stopped
the add-on loading at all - including the Settings switch that would
have turned downloads off. Recovery meant deleting a file by hand.

The check is now strict enough that nothing malformed reaches the rest
of the add-on.

## Checking for content twice at once could corrupt it

Opening Settings and pressing "Check now" while the automatic check was
still running could leave a half-written database on disk. The add-on
would notice at the next launch and fall back to the bundled copy, so
nothing broke, but your content would quietly revert with no
explanation.

---

**Upgrading:** nothing to do. Your settings, shortcuts and dock layout
carry over untouched, and the reference database is unchanged.
