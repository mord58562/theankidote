# What's new in The AnkiDote 2.4.1

## The version sits where it belongs

2.4 put the add-on's version in Settings for the first time, on a row of
its own above the Close button - which left it floating in a band of
empty space with nothing to align to. It now anchors one footer strip
under a hairline: the version, then whatever is waiting on a restart,
then Close. Its tooltip still carries the three numbers a bug report
needs, and clicking still copies them.

## Fixes found auditing this release

The add-on could fail to load altogether on older Anki builds, because
one type annotation used syntax that only exists from Python 3.10 and
four vocabularies import that module at startup. Fixed.

Three pieces of Settings text were wrong or incomplete: the Advanced tab
said the web inspector needed a normal restart when it needs its own
relaunch, and the restart notice named modules being switched on but not
off. Selecting the version text with the mouse did not work, and its
tooltip could fall out of step with the library version after an
in-window update.
