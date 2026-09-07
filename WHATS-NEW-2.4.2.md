# What's new in The AnkiDote 2.4.2

## Acronyms that are also ordinary words stay quiet

A card reading "1st line: [...] OR [...]" was showing a popup for the
operating room. The same went for "ALL patients", "at ALL ages" and a
handful of others: OR, ALL, PET, CAP, TEN, MEN, ARM, BED, MAP, AS and
LAST are all real medical acronyms and all ordinary English words, and
each of them expanded the moment it appeared in capitals.

They now expand only when the card also contains something from the
subject they belong to. "Taken to OR under general anaesthesia" still
resolves; "nifedipine OR indomethacin" does not. Across a 6,000-card
collection this removed about 110 wrong popups while keeping the 80
correct ones.

## And the same problem, much bigger, elsewhere

Chasing that bug turned up a worse one. Two entries in the physiology
vocabulary were reachable by the bare words "or" and "if" - the odds
ratio and intrinsic factor - and that vocabulary matches without regard
to capitals. So the ordinary conjunction was underlining itself and
offering a statistics popup on nearly every card that used it. The
single letter "F" did the same for bioavailability, and "affect" the
verb collided with affect the psychiatric sign.

Every term in the add-on, all 11,687 of them, was checked against a
dictionary of English words. Nine had this problem. All nine now need
their subject to be somewhere on the card before they will open
anything. On a 6,000-card collection that is about 3,600 fewer wrong
popups.
