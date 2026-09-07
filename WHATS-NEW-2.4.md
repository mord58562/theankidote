# What's new in The AnkiDote 2.4

A quality release: three popup behaviours that were missing, a few
failure modes that were louder than they should have been, a pass
over Settings and the sidebar chrome, and a handful of housekeeping
fixes.

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

## The accent button was chosen by tab order

"Custom terms..." sat in the window filled blue while "Check now", two
groups below it, was a plain button. Neither had been picked for the
job. Qt marks every button inside a dialog as a candidate default and
promotes the first one it finds, and macOS paints the default in the
system accent colour, so the layout order was making the decision.
Buttons in Settings now decline that promotion. The accent is left for
the button that commits a window, which in a preferences sheet is
nothing.

## The restart notice now says something true

The bottom of the window used to read "Some settings take effect after
you restart Anki", permanently, and the Advanced tab said the same
thing again in its own words. Almost nothing in there needs a restart:
shortcuts rebind when the window closes, verbose logging is read each
time it is used, custom terms apply to the next card drawn. The one
exception is switching a module back on, because those load with Anki.
So that is what the line says now, naming the module, and only while it
is true. The Advanced tab's note was never about settings at all - it
reports whether the web inspector's port is open - and now says so.

## Versions are visible

The add-on's version sits in the bottom corner of Settings. Its tooltip
carries the three numbers a bug report needs - the add-on, the
reference library, and Anki itself - and clicking copies all three. The
library's own version keeps its place in the Reference database group,
labelled as the library, so that two different numbers are no longer
both called "Version".

## The three sidebars finally match

The reference panel, the UpToDate browser and the chat dock each put
the same strip of buttons above a webview, and each had been built
separately. Back and forward were drawn from one arrow family in one
dock and a different one in another, reload turned clockwise in one and
anticlockwise in the next, the UpToDate band was four pixels taller
than the other two, and closing the reference panel flashed red while
closing the other two did not. In light mode the reference panel was
also a slightly different teal from everything else, and corrected
itself the first time you switched theme.

All of that now comes from one place, so a glyph is the same glyph at
the same size wherever it appears. The reference panel's error pages
follow the theme too - they used to paint a dark slab inside a light
Anki.
