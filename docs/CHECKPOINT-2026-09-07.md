# TheAnkiDote checkpoint - 2026-09-07 (end of session)

Supersedes `CHECKPOINT-2026-09-03.md` for state. That file's style rules and
publish flow still apply and are not repeated here.

## State

- **Content channel:** `07.09.2026.4`, published
- **Add-on:** **2.5.0 built, NOT yet on AnkiWeb.** Everything new folds into
  2.5.0 until Rob confirms the push; do not open 2.5.1.
- **Rich summaries:** 2224. **NEW_CONDITIONS:** 1400. **Base conditions:** 826.
  **Acronyms:** 429.
- **Tests:** 133/133. AST scan shows no duplicate keys.

## Releases

2.4.0 was built and never uploaded. 2.4.1 shipped to AnkiWeb (tag `v2.4.1` at
`66ed54b`, GitHub release published). 2.4.2 was built, never uploaded, and
folded into 2.5.0. So 2.5.0 carries everything since 2.4.1.

## What shipped this session

- **Batches 80-82, ~370 entries.** Clinical scores and decision rules,
  procedures, investigations, Australian health-system and medicolegal topics,
  then two data-driven rounds against the notes that trigger no popup.
- **Dock chrome unified.** `_theme.py` owns header metrics, the glyph set,
  per-glyph optical sizes and the nav stylesheet; the three docks had drifted
  into two arrow families, three glyph-sizing systems and header heights of
  40/40/44.
- **Settings pass.** No content button takes the accent by tab order; the
  restart notice is state-driven and names the module in both directions; the
  version sits in a real footer strip.
- **Three classes of false-positive matching found and fixed** - see below.

## The three false-positive classes (the session's main lesson)

1. **Condition aliases shadowing the acronym dictionary.** TGA fired
   Transposition of the Great Arteries on 175 notes that meant the Therapeutic
   Goods Administration. Also GBS, ED, LAST, ARF, TCA, CVS, BED, and AMH caught
   before shipping.
2. **Acronyms that are ordinary English words.** `resolve()` skips context
   scoring for single-candidate acronyms, so OR, ALL, PET, CAP, TEN, MEN, ARM,
   BED, MAP, TI, IF and DID expanded on sight. `_ENGLISH_WORD_ACRONYMS` now
   requires a context keyword. Worse, "OR" and "IF" were also aliases in the
   preclinical vocabulary, which matches case-insensitively - firing on 1,889
   and 1,101 notes.
3. **Popups claiming articles that do not exist.** Only 635 of 2,226 condition
   entries have an NBK id; the rest fell back to a StatPearls search while the
   badge said "StatPearls" and the button said "Open article". Same for
   Wikipedia-search and DrugBank-search entries. `_link_kind()` now drives both.
   2,635 popups stopped overstating themselves.

## Coverage, and why the number went up

Live via AnkiConnect: of 6,088 notes, about 13% trigger no popup. Roughly 640
of those are image-occlusion cards carrying under six words, which can never
match text, leaving ~165 genuinely addressable. The figure rose from 12% to 13%
after the false-positive purge - correct, because bad aliases had been
spuriously counting as coverage.

## The richest seam is not new entries

Repeatedly, the highest-value finding was an **alias gap**: the entity already
exists and only the card's wording misses it. Plurals, hyphenation,
possessives, apostrophe-less eponyms ("Turners"), bare surnames ("McRoberts"
against "McRoberts manoeuvre"), and abbreviations ("Abx", 59 notes, no acronym
entry at all). Sweep for these before writing anything new, and make every
drafting agent report them as a deliverable rather than a side note.

## Never work from a snapshot

The collection changes while a session runs. Every frequency or context
question goes to AnkiConnect at the moment it is asked. `anki_freq.py` in the
session scratchpad does this with no cache; hand agents that rather than a
dumped file. Scripts worth recreating: `anki_freq.py`, `dupecheck.py` (scans
every vocabulary, not just conditions), `check_budget.py`, `merge_batch.py`,
`verify_batch.py`.
