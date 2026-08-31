# Rich summary priority gaps - snapshot 2026-08-31

Generated from a direct sqlite scan of Rob's Anki collection
(`~/Library/Application Support/Anki2/User 1/collection.anki2`, 6,088 notes)
after batches 44-51 shipped. All conditions with rich summary coverage were
excluded. AnkiMCP is configured (see `~/.claude.json`) but its tools were not
loaded in the session that produced this file; direct sqlite gave the same
answer.

Rich summary total when this scan ran: 639.

## Top uncovered conditions by card mentions

All remaining uncovered conditions appear only 1-2 times each in Rob's cards.
That plateau is the coverage signal: the sqlite-driven priority list has
essentially been worked through, and future batches should be driven by Y4
curriculum priority rather than card frequency alone.

```
    2  Eating disorder not otherwise specified
    1  Tourette syndrome
    1  Seborrheic dermatitis
    1  Spinal stenosis
    1  Biliary atresia
    1  Follicular lymphoma
    1  Corticobasal degeneration
    1  Psittacosis
    1  Protein C deficiency
    1  Cardio-renal syndrome
    1  Parapneumonic effusion
    1  Chronic granulomatous disease
    1  Duodenal atresia
    1  Scurvy
    1  Warm autoimmune haemolytic anaemia
    1  Melasma
    1  Cryptococcosis
    1  Paraganglioma
    1  Rabies
    1  Filariasis
    1  Body dysmorphic disorder
    1  Spinal epidural abscess
    1  Sézary syndrome
    1  Angioimmunoblastic T-cell lymphoma
    1  Pityriasis lichenoides chronica
    1  Uterine polyp
```

## Cards mention it, base library does not have it

From a multi-word title-case n-gram scan of all note fields (not just card
titles), phrases that occur >=3 times and are neither a base-library
condition/drug/acronym nor obvious question-stem boilerplate. Most were
question-stem language, but a few point to real Y4 topics worth adding as
NEW_CONDITIONS entries with rich summaries:

- Microangiopathic haemolytic anaemia (11) - MAHA differential (HUS, TTP,
  DIC, HELLP, malignant hypertension) - candidate for a new rich summary
  since none of the individual entries frames the group syndrome
- Teratogenic Medications (11) - useful reference topic that could ship as
  a rich summary
- Peripheral blood smear findings (12) - candidate reference topic
- Personality disorders (14) - BPD is present but the umbrella entry
  isn't
- Newborn examination (21) - not a condition; skip
- Anxiety disorders (21) - covered as GAD/panic/social/OCD/PTSD; skip
- Glomerular disease (11) - covered piecemeal (nephritic/nephrotic and
  each glomerulonephritis); skip

## Recommended next-batch priorities

Combining the two lists plus Y4 exam-classic gaps I've been holding:

1. Microangiopathic haemolytic anaemia (umbrella differential)
2. Follicular lymphoma
3. Biliary atresia
4. Spinal stenosis
5. Cryptococcosis (Aus HIV-relevant)
6. Duodenal atresia (double-bubble, Down syndrome)
7. Rabies (returned-traveller / bat exposure in Australia)
8. Protein C deficiency (with S deficiency and Factor V Leiden covered
   already, C completes the inherited thrombophilias set)
9. Warm autoimmune haemolytic anaemia (Coombs+, IgG, warm)
10. Body dysmorphic disorder (OCD-spectrum, common presentation)

## Re-generate this scan

```
python3 << 'PY'
import sqlite3, shutil, re, sys
src = '/Users/robrussell/Library/Application Support/Anki2/User 1/collection.anki2'
dst = '/tmp/anki_collection_copy.anki2'
shutil.copy(src, dst)
conn = sqlite3.connect(f'file:{dst}?mode=ro', uri=True)
cur = conn.cursor()
rows = cur.execute('SELECT flds FROM notes').fetchall()
tag = re.compile(r'<[^>]+>')
big = ' '.join(tag.sub(' ', flds.replace('\x1f',' ')).lower() for (flds,) in rows)
sys.path.insert(0, '/Users/robrussell/theankidote')
from content._rich import RICH_SUMMARIES
covered = set(k.lower() for k in RICH_SUMMARIES.keys())
from pearls import _conditions
condition_names = [(c['name'], c.get('aliases', [])) for c in _conditions._CONDITIONS]
from collections import Counter
freq = Counter()
for name, aliases in condition_names:
    if name.lower() in covered: continue
    total = sum(len(re.findall(r'\b' + re.escape(t.lower()) + r'\b', big))
                for t in [name] + aliases)
    if total > 0: freq[name] = total
for name, count in freq.most_common(40):
    print(f'  {count:4d}  {name}')
PY
```
