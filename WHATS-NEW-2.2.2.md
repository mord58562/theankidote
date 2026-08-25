# What's new in The AnkiDote 2.2.2

A small release on top of 2.2.1, fixing one thing.

## Short custom terms never highlighted

Custom Terms (Settings > Reference popups > Custom terms...) added a
term but nothing in the reviewer ever showed it, with no error and no
indication anything was wrong - reinstalling or restarting Anki made no
difference.

Any highlight term under four characters, matched without "Match case"
ticked, was being silently dropped everywhere in the add-on, custom
terms included. That rule exists to stop a short common word from
lighting up constantly through the reviewer - without it, a
case-insensitive two-letter term would match inside ordinary prose
throughout every card. It was never meant to apply to a term someone
typed into the Custom Terms table by hand: that is a deliberate choice
by the user, not something the add-on resolved on its own, and dropping
it with no feedback anywhere was a trap rather than a safeguard.

Custom terms are now exempt from that filter regardless of length or
the "Match case" setting. Everything else - acronyms, drug names,
condition names - is unaffected; the guard against short, noisy,
case-insensitive matches still applies to every term the add-on
resolves on its own.

---

**Upgrading:** nothing to do. Your settings, shortcuts, dock layout and
any custom terms you've already added carry over untouched.
