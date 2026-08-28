# What's new in The AnkiDote 2.2.1

Bug fixes only.

## Content updates keep applying across a month boundary

The check that decides whether the reference library on the update
channel is newer than the copy you already have was a raw text
compare. That was correct when new releases were stamped
`YYYY.MM.DD`, but the channel format changed on 2026-08-28 to
`DD.MM.YYYY` and the text compare gets that shape right within a
month and wrong across a month rollover (`01.09.2026` sorts below
`31.08.2026` as text). Under 2.2 that would have silently stopped
content updates from applying at midnight on the first of any month
under the new format.

2.2.1 parses either shape into a real date and compares that, so the
channel keeps working through month and year boundaries without a
further update.

---

**Upgrading:** nothing to do. Your settings, shortcuts and dock
layout carry over untouched. The reference database keeps updating
itself in the background as before.
