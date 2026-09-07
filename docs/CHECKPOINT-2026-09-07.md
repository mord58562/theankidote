# TheAnkiDote checkpoint - 2026-09-07

Supersedes `CHECKPOINT-2026-09-03.md` for state; that file's style rules and
publish-flow section are still the reference and are not repeated here.

## State

- **Content channel:** `07.09.2026.2` (published)
- **Add-on version:** `2.3.2` (unchanged - AnkiWeb gate still closed; 2.3.3 code work still on the backburner)
- **Rich summaries:** 1927 (686 on 03-09, 1853 at the start of this session)
- **NEW_CONDITIONS:** 1103. **Base conditions:** 826. **Acronyms:** 424.
- **Ratchet:** `OVER_CAP_BUDGET["conditions"] = 29` - real headroom, unlike the 79/79 of 03-09
- **Tests:** 133/133 pass. AST scan shows no duplicate RICH_SUMMARIES keys.

## What shipped this session

1. **Batch 80 - 74 new entries** across four clusters that were genuinely
   uncovered: clinical scores and decision rules (24), bedside procedures and
   anaesthesia (15), investigations (21), Australian health systems and
   medicolegal (14). Drafted by four parallel agents, verified by the parent
   (budget, labels, dupes, banned tokens, spelling, cross-batch collisions).
2. **Acronym-alias false-positive fix.** Eight short all-caps condition aliases
   were shadowing the context-aware acronym matcher and firing wrong popups on
   real cards: TGA, GBS, ED, LAST, ARF, TCA, CVS, BED. Removed from their
   owning conditions; LAST/ARF/CVS/BED added to the acronym dictionary with
   context keywords, and Therapeutic Goods Administration added as TGA's first
   candidate.
3. Banned dead-metaphor word purged from code comments, test docstrings and
   audit prose.
4. `.claude/settings.json` now tracked (`model: opus`, `effortLevel: high`) so
   the cloud routine inherits high effort; `.gitignore` narrowed to allow it.

## The AnkiConnect method - use it every session

Anki must be open. `http://127.0.0.1:8765`, `findNotes` on `deck:*` then
`notesInfo` in batches of 800 dumps all 6,088 notes in seconds. Two things it
answers that guesswork cannot:

- **Which candidates are worth writing.** Word-boundary count every candidate
  name and alias against the collection text. Batch 80 scored 43 of 74 firing
  on current cards; the zero-hit ones (Wells, Child-Pugh, MELD, qSOFA, Ottawa)
  are real gaps in Rob's deck, not bad picks.
- **Which aliases are wrong.** Running `pearls._conditions.resolve` over every
  note surfaces false positives directly. That is how all eight bad aliases
  above were found. Re-run it after any batch that adds short all-caps aliases.

Scripts left in the session scratchpad (regenerate if gone): `dupecheck.py`,
`check_budget.py`, `merge_batch.py`, `freq.py`.

## Coverage picture

967 distinct conditions currently fire across the collection. Roughly 38% of
notes match no condition at all - that set is the best source of candidates for
the next batch and has not been mined yet.
