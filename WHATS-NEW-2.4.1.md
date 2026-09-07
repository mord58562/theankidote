# What's new in The AnkiDote 2.4.1

Three fixes in Settings, all of them things that looked wrong before
they were wrong.

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
