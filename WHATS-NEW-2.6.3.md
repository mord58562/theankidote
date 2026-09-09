# What's new in The AnkiDote 2.6.3

Term updates had stopped arriving. This release is why, and the fix.

## Term updates work again

The add-on downloads its term library separately from the add-on
itself, so new topics reach you without waiting for a release. That
download has been failing.

GitHub changed the address it hands out for release files. The add-on
only follows a redirect to an address it recognises - deliberately,
because the term library decides what every popup says, and following
a redirect anywhere would mean anyone able to move that link could
replace the clinical content. The new address was not on the list, so
every download was refused. The add-on kept the copy it already had
and logged one line about it, which is the safe behaviour and also a
quiet one.

Eleven library updates went out during that period and none of them
arrived. Once you are on 2.6.3 they all do, in a single download on
the next launch.

If you want to confirm it worked: Settings names the content version
you are running underneath the add-on version. It should read
`09.09.2026` or later after two launches - the download happens in the
background on one launch and is applied on the next, so the matcher is
never swapped underneath a session you are in the middle of.

## Smaller things

The diagnostic file was filling with reports that the reference
sidebar had opened on its own, every time it had in fact been opened
normally. Those entries were wrong, and they buried the real ones. If
you have ever sent a log in, this is why it was longer than it should
have been.
