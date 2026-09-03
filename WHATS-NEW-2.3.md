# What's new in The AnkiDote 2.3

## Custom terms now say so

A term from **Settings → General → Custom terms…** popped up looking
exactly like a StatPearls result - same "STATPEARLS" badge, same
colour, no way to tell it apart from the reference database at a
glance. `source` was meant to drive this ("free-form source label
shown in the popup", the docs claimed), but the popup only ever
recognised four fixed values and treated everything else - including
every custom term - as StatPearls.

Custom terms now badge themselves **CUSTOM**, in a colour that belongs
to neither StatPearls' teal nor DrugBank's amber, so a custom popup
reads as custom before you've read a word of it. The "Open article →"
button says "Open link →" instead, for the same reason.

Each custom term can also carry its own label instead of the generic
one. **Custom terms…** has a new optional **Label** column - leave it
blank and the badge reads "CUSTOM", or type your own ("Lecture notes",
"UpToDate", whatever the source actually is).

The badge colour is a fresh hue not used anywhere else in the popup,
tuned separately for light and dark mode so it holds up in both.

---

**Upgrading:** nothing to do. Existing custom terms carry over with no
label set, so they badge as "CUSTOM" until you give them one.
