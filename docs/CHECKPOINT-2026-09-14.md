# Checkpoint - 2026-09-14

Rob: "integrate anything from the ankidote content cloud routine and
then continue work."

## Starting state

`main` was three commits behind `origin/main`. The cloud agent had
pushed three overnight batches - 104 entries across Medicine-1
cardiology, bedside tests and ECG patterns, procedures and therapeutic
monitoring, psychiatry and paediatrics. `v2.7.0` had also been tagged
and released on GitHub at some point after the 2026-09-09 session,
which had left it waiting.

## The cloud batches, integrated

All 104 validated before publishing, not after:

- every entry highlights and resolves to itself through the runtime
  matcher, and all 104 are present in `rich_summaries`;
- `verify_batch.py` clean - no banned characters, no US spellings, no
  over-budget entries, labels all in the whitelist;
- 207 tests green; `check_refs.py` reports every destination resolving
  to the page it names.

Published as content `14.09.2026`.

## The finding that shaped the rest of the session

`triage_gaps.py` put genuinely-missing curriculum items at Medicine-1
54, O&G 68, Paediatrics 37, Psychiatry 29 - 188 in total, and the
2026-09-09 checkpoint had called O&G "the whole priority".

Almost none of it was missing content. The matcher is exact, and the
curriculum's wording is not the library's:

| curriculum says | library has |
|---|---|
| Cervical screening | Cervical screening test, under Cervical cancer screening |
| Fetal death | Stillbirth |
| Perineal laceration | Perineal tear |
| Six-week check | Six week check |
| Organic illness presenting as psychiatric illness | Organic causes of psychiatric symptoms |

So the first question about any gap item is not "what should this entry
say" but "which existing entry already says it". Checked against the
runtime matcher rather than against names, 96 of the 188 closed with
150 alias strings and no prose at all.

**The method, for the next module or the next framework.** Build the
candidate table (`scratchpad/evidence.py` pattern: nearest existing
entries by head noun, each resolved to its primary and shown with a
slice of its summary), then sort every item into ALIAS / NEW / SKIP
with the entry's own text as the evidence. Alias resolution is not
proof of coverage - read enough of the target summary to be sure it
answers the item. Roughly a third of items are legitimate SKIPs:
learning outcomes and umbrella headings with no entity a popup can
attach to. Do not invent an entry to avoid a skip.

**Aliases rejected rather than shipped**, each for a reason worth
keeping: "Sterilisation" is not "Tubal ligation" (it is also vasectomy,
and also autoclaving); "Lower urinary tract" would fire inside "lower
urinary tract symptoms"; "Upper airway obstruction" would open a
paediatric differential on an adult anaesthetics card, there being no
adult entry; "Learning delay" and "Learning disability" are ambiguous
in Australian usage; a bare "Risk management plan" also names a TGA
pharmacovigilance document.

Every applied alias was verified twice - resolves to the intended entry
and to no other, and highlights across its full length.

## Result

| module | missing at start | missing now |
|---|---:|---:|
| Medicine-1 | 54 | 32 |
| O&G | 68 | 22 |
| Paediatrics | 37 | 23 |
| Psychiatry | 29 | 15 |
| **total** | **188** | **92** |

Twenty new entries written for the residue. Three proposed entries were
dropped on inspection: "Antenatal screening" was a subset of Antenatal
care schedule; "Dysarthria" already exists thinly in the signs table;
"Liver function test" and "Proton pump inhibitor" in the singular are
owned by the acronym dictionary.

Content published as `14.09.2026.1`.

## Spelled-out acronyms - a never-executed feature, found and fixed

272 of the 485 expansions in the acronym dictionary had never fired.
The matcher is built from the keys alone, so "CRP" opened a popup and
"C-reactive protein" did not, on the same card, with the same content
behind it. Same shape as `data-sp-utd`, the chat adblock and
`hide_article_list`: the data was there and nothing looked at it.

Expansions are now matched case-insensitively - the dictionary stores
Title Case and cards write sentence case, so matching them the way
acronyms are matched would have closed the gap on paper only. That
needs a second term per hit, since one term cannot be both; the
expansion term carries the acronym term's `_article` so the popup is
still headed "CRP - C-reactive protein", and the acronym term is
dropped when the card never wrote the acronym, which stops a
three-letter key getting loose in prose.

40 expansions are blocklisted as ordinary clinical prose ("Emergency
Department", "Heart Rate", "Per Os") and 11 carry an editorial
parenthetical or slash. 272 unmatchable becomes 50, all deliberate, with
a test holding a floor so the blocklist cannot grow back into the bug.

Where a condition entry and an acronym expansion name the same thing,
the condition's richer summary still wins - checked on ESR, VTE
prophylaxis and interstitial lung disease.

## For Rob

- **This earns a minor version bump to 2.8.0** - spelled-out acronyms
  are a new user-visible behaviour, not a fix. AnkiWeb is still on
  2.6.3 and 2.7.0 is released on GitHub but not pushed there. Your
  call, and no manifest version has been touched.
- The library is **7.45 MB, 93% of the 8 MB ceiling** in clients before
  2.5.0. At roughly 2.3 KB an entry that is about 250 entries of
  headroom before those installs stop receiving content. Worth a
  decision before it is made by accident.

## Open, deliberately

- `Falls in older adults` and `Falls in the elderly` are near-duplicate
  entries that want merging.
- The `Dysarthria` signs entry is 250 characters and deserves the full
  types-causes-management treatment as a rewrite.
- 92 curriculum items remain, now genuinely content rather than wording.
- The popup's vertical rhythm, signing the content manifest, and the
  387 short abbreviation aliases all still stand from 2026-09-09.
