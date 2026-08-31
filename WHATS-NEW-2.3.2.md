# What's new in The AnkiDote 2.3.2

A small release on top of 2.3.1, tidying the Settings dialog.

## Settings dialog reads more like Anki, less like a manual

A few labels in Settings were doing the work that a tooltip already
does. The "Reference popups" tab had a checkbox reading "Open clicked
popups in the side panel (uncheck to use external browser)" - the
parenthetical explained the negation of the checkbox instead of just
being what a checkbox is. That label now reads "Open in side panel",
and the browser-fallback note lives on hover where it belongs.

The Modules tab dropped "and sidebar" from the reference-popups row -
the label was fighting for space with itself. The database tab's
"Keep the reference database up to date" is now "Check for updates on
launch", which is the same instruction in half the words.

Under the database checkbox, the current content version used to
appear twice: once as a label ("Content 30.08.2026.3.") and again
inside the Check-now status message ("Up to date (content
30.08.2026.3)."). It appears once now.

None of these change what the settings do; they just stop the dialog
sounding like a printed manual.

---

**Upgrading:** nothing to do. Your settings, shortcuts and dock
layout carry over untouched. The reference database keeps updating
itself in the background as before.
