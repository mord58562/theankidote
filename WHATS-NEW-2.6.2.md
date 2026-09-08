# What's new in The AnkiDote 2.6.2

One fix, for something 2.6.1 introduced.

## The Escape fix no longer looks like a crash

2.6.1 stopped Escape being usable as a global shortcut, and cleared the
binding for anyone who had already saved one. That part worked. But it
announced the clearing in a way Anki treats as a fault, so the first
launch after updating could show a critical-error report - on a release
whose main purpose was fixing that very binding.

It now tells you what happened in a short message a couple of seconds
after launch: which shortcut was cleared, and that you can set a new one
in Settings. Nothing else has changed.

## The UpToDate sidebar says what it is doing

Clicking an UpToDate link in a popup used to open the sidebar on a blank
white page with nothing but a logo, sometimes for several seconds.
UpToDate's search is slow, the page was on its way, and there was no way
to tell that from a failure. It now names what it is looking up while it
waits.

The UpToDate sidebar also kept no diagnostic record at all, so a report
about it could not be investigated. It logs like the reference sidebar
does now.
