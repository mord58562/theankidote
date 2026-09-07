# What's new in The AnkiDote 2.5.1

## The download stops carrying my notes

Every release up to 2.5.0 packaged the working documents from the
sessions that built it: checkpoints, coverage measurements, audit
transcripts, and the briefing file for the scheduled agent that writes
content. That was 422 KB of a 3.1 MB download, and most of it was a
stale copy of summaries the add-on already carries properly in its term
library - so you were downloading much of the same content twice, once
in a form nothing reads.

None of it was ever loaded by the add-on. It just travelled with it.

The package now ships what runs and the release notes, and nothing else.
Even with a large batch of new terms added in the same release, the
download is smaller than 2.5.0 was. Nothing you can see or use has been
removed, and there is no change to the terms, the popups or the library
itself.

If you already have 2.5.0 installed, updating simply removes those files
from the add-on folder.
