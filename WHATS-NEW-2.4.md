# What's new in The AnkiDote 2.4

A quality release: three popup behaviours that were missing, a few
failure modes that were louder than they should have been, and a
handful of housekeeping fixes.

## Popup dismisses with Escape or click-outside

The hover popup used to close only when the pointer left the highlighted
word - awkward when you had already read it and wanted the popup gone
so you could see the card behind. Press Escape to close it, or click
anywhere outside the popup or the highlight.

## Dock respects `minWidth` in the config

The `minWidth` option in config.json was documented but ignored: setting
it did nothing. Raising it now widens the sidebar accordingly (with 520
pixels as a floor, because NCBI book pages need that much width to
render without a horizontal scrollbar). Existing configs keep working
unchanged.

## One-line notice when the reference library updates

Content updates land in the background between launches - a corrected
first-line antibiotic or a new topic popup. The rich text only takes
effect at the next Anki launch, and there was no indication anything
had changed. A short tooltip on that next launch now says the library
moved and to what version.

## Sidebar opens faster on complex cards

The article-list resolver was running the condition and drug matchers
a second time on every card change, redoing work the highlighter had
already done a moment earlier. It reuses the earlier result now, which
takes about two milliseconds off each transition on cards with many
matches.

## Diagnostic log rotates instead of growing forever

`user_files/diagnostic.log` used to append without bound. It rotates at
one megabyte now, keeping one prior file (`diagnostic.log.1`), and
starts a fresh log after that. Users who never look at it will not
notice; users who send it in for support will still get the last day
or two of activity.

## First-run install waits for consent before checking for updates

The content-update check used to fire before the welcome dialog had
been shown on a brand-new install. It now waits until you have
accepted the welcome dialog, so no add-on you have not yet approved
makes an outbound request in the background.

## Small robustness fixes

- The toolbar handler no longer crashes the crown button if a future
  Anki release renames `link_handlers`; it logs and continues.
- The tooltip source field is escaped as a matter of course, closing
  a defence-in-depth gap that the current downloads did not exploit
  but a hypothetical future library entry could have.
- The installer refuses archives that contain path-escaping entries
  before unpacking.

---

**Upgrading:** nothing to do. Your settings carry over untouched.
