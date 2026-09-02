# Chronic disease AU first-lines audit - 2026-09-01

## Scope

Filtered `all_rich_summaries_2026-09-01.json` (686 entries) to 68 chronic-disease entries recommending specific pharmacotherapy. Focus: AU-specific first-line drugs, targets, PBS restrictions, and 2023-2026 guideline drift.

Sources consulted:
- Heart Foundation / CSANZ (2023 CVD risk guideline, ACS guideline, 2018 AF guideline)
- Australian Diabetes Society (2024 T2DM algorithm)
- National Asthma Council of Australia (Australian Asthma Handbook 2025)
- GINA 2024
- RACGP + Healthy Bones Australia (2024 osteoporosis guideline)
- RACGP (hip/knee OA guideline)
- Kidney Health Australia / CARI (2024 CKD)
- RANZCP (bipolar / valproate PPP)
- Australian Prescriber / NPS MedicineWise
- PBS listings (pbs.gov.au)
- Australian Rheumatology Assn (Living Guideline for pharmacological management of RA)
- Endocrine Society / ADS (thyroid, adrenal)
- eTG public excerpts

## Findings

### SUBSTANTIVE errors (change required)

- **Atrial fibrillation** — states "CHA2DS2-VASc against HAS-BLED, DOAC preferred". Australian practice (CSANZ/NHF 2018, endorsed by 2024 ESC update) uses **CHA2DS2-VA** (female sex point dropped). This is a Rob-flagged AU-specific rule per memory. Also, "anticoagulation decisions do not change once sinus rhythm is restored" is defensible but the score name is the concrete error. Suggested rewrite of the Mx sentence:
  `Anticoagulation is decided independently of rate or rhythm, on CHA2DS2-VA (Australian sex-neutral score) against bleeding risk; DOAC preferred except in moderate to severe mitral stenosis or a mechanical valve.`
  Sources: [CSANZ 2018 AF guideline / MJA](https://www.mja.com.au/journal/2018/new-guidelines-atrial-fibrillation-heart-failure); [Heart Lung Circ CHA2DS2-VA position](https://www.heartlungcirc.org/article/S1443-9506(18)31866-3/abstract)

- **Chronic kidney disease** — states "SGLT2 inhibitor (dapagliflozin or empagliflozin) if eGFR at least 20 with albuminuria". The PBS eGFR thresholds differ by drug: **empagliflozin ≥20**, **dapagliflozin ≥25** mL/min/1.73 m² for CKD indication. Also, current PBS/KDIGO no longer strictly requires albuminuria for empagliflozin (EMPA-KIDNEY expanded eligibility). Suggested rewrite:
  `an SGLT2 inhibitor for CKD - empagliflozin (PBS from eGFR 20) or dapagliflozin (PBS from eGFR 25), regardless of diabetes status`
  Sources: [PBS empagliflozin PSD May 2025](https://www.pbs.gov.au/industry/pbac/psd/2025/05/empagliflozin-psd-may-2025.pdf?variant=3); [KHA/CARI 2024]

- **Diabetes mellitus** — "Target HbA1c is around 7% generally". ADS uses **HbA1c ≤7% (53 mmol/mol)** as the general target for most; individualised per comorbidity. Also, the summary lumps T1/T2 into one entry - given the entry is titled "Diabetes mellitus" it needs at minimum a T1DM sentence. The current text implicitly describes T2DM only ("metformin first-line"). Suggested addition to Mx:
  `T1DM needs basal-bolus insulin or pump from diagnosis - not metformin. In T2DM: lifestyle plus metformin first-line for most...`
  Source: [Australian T2DM algorithm June 2024](https://www.racgp.org.au/getattachment/df4380d5-c2f6-40cd-93db-f638b3f32ec3/Australian-type-2-diabetes-management-algorithm-June-2024.pdf.aspx); [ADS position statements](https://diabetessociety.com.au/position-statements-guidelines-type-2.asp)

- **Asthma** — Currently OK on AIR concept, but weak on the Track 1 vs Track 2 framing and Australian Asthma Handbook 2025 stepped approach. Also LAMA/biologic escalation is described only "in severe" - should specify Step 4-5 and mention tiotropium. Not wrong, but under-specified for a first-line-focused summary. Minor rewrite:
  `Australian Asthma Handbook 2025 (aligned with GINA Track 1): budesonide-formoterol as anti-inflammatory reliever (AIR) at all steps 1-2, maintenance-and-reliever therapy (MART) at step 3 onward. Add tiotropium (LAMA) at step 4 and a biologic (omalizumab, mepolizumab, benralizumab, dupilumab, tezepelumab) for severe uncontrolled disease.`
  Source: [Asthma Australia AAH Update 2025](https://asthma.org.au/health-professionals/asthma-digest/aah-update-2025/)

- **Antiphospholipid syndrome** — Says "DOACs less effective, especially in triple-positive - avoid." The TGA in 2024 updated all DOAC Product Information to warn against use in **any** APS, not just triple-positive. Should escalate the warning. Suggested rewrite:
  `Warfarin (INR 2-3, or 3-4 recurrent) is the anticoagulant of choice. TGA (2024) updated DOAC PIs to warn against use in any patient with APS after increased recurrent thrombosis events - avoid DOACs regardless of antibody profile.`
  Source: [TGA DOAC safety update](https://www.tga.gov.au/news/safety-updates/direct-acting-oral-anticoagulants-and-risk-recurrent-thrombotic-events)

- **Rheumatoid arthritis** — "methotrexate within weeks of diagnosis, treat-to-target to remission; escalate to biologic or JAK inhibitor per PBS". The Australian Living Guideline (ARA/ANZMUSC) explicitly considers **triple therapy (MTX + SSZ + HCQ)** as an alternative to methotrexate + bDMARD before biologic escalation, with equivalent ACR50 response. Under-inclusive. Suggested addition:
  `Methotrexate within weeks; if inadequate response, add either triple csDMARD therapy (methotrexate + sulfasalazine + hydroxychloroquine) or escalate to a bDMARD/JAK inhibitor per PBS (bDMARD/tsDMARD preferred in modern AU practice due to poor long-term triple-therapy tolerance).`
  Source: [Australian Living Guideline for Pharmacological Management of Inflammatory Arthritis](https://files.magicapp.org/guideline/388ad793-879e-4774-be5f-9b4791cede41/published_guideline_7974-3_4.pdf)

- **Alzheimer disease** — "anti-amyloid monoclonals not yet PBS-listed" was correct as of 2024 but **stale**: as of Sep 2025, **lecanemab (Leqembi)** and **donanemab (Kisunla)** are both **TGA-approved**; donanemab was rejected for PBS listing, lecanemab is TGA-approved for MCI/mild dementia in ApoE ε4 non-carriers or heterozygotes only (not homozygotes due to ARIA risk). Suggested rewrite:
  `Anti-amyloid monoclonals: lecanemab (Leqembi) and donanemab (Kisunla) are TGA-approved (2025); lecanemab restricted to ApoE ε4 non-carriers or heterozygotes for early Alzheimer disease. Neither PBS-listed - private prescription only.`
  Sources: [Biogen/Eisai TGA approval](https://investors.biogen.com/news-releases/news-release-details/leqembir-lecanemab-approved-treatment-alzheimers-disease); [Australian Dementia Network 2025](https://www.australiandementianetwork.org.au/2025/09/24/another-alzheimers-treatment-approval-means-hope-and-choice-for-patients/)

- **Migraine** — "CGRP antagonists on PBS with prior therapy failures" is correct for chronic migraine but under-specified. As of 2024 PBS: **galcanezumab and fremanezumab** are PBS-listed for chronic migraine (≥15 headache days/month); **erenumab** is not PBS-listed (private only ~$800/month); **eptinezumab** is IV, private. Also, gepants (rimegepant, ubrogepant) not yet PBS-listed for acute - the entry lists them for acute Rx without a PBS caveat. Suggested rewrite:
  `Preventive when 4 or more per month uses propranolol, amitriptyline, topiramate or sodium valproate (avoid valproate in pregnancy/childbearing potential). PBS-listed CGRP mAbs galcanezumab and fremanezumab for chronic migraine (≥15 days/month) after failure of ≥3 preventives; erenumab TGA-approved but private-only.`
  Source: [Migraine Australia CGRP](https://www.migraine.org.au/cgrp); [Australian Prescriber CGRP](https://australianprescriber.tg.org.au/articles/calcitonin-gene-related-peptide%E2%80%93targeted-therapies-for-migraine.html)

- **Bipolar disorder** — "sodium valproate (contraindicated in people who could become pregnant)" underplays the AU regulatory position. RANZCP-endorsed **Valproate Pregnancy Prevention Program (PPP)** since 2023 requires LARC and annual specialist review before valproate can be prescribed to any female of childbearing potential. Suggested rewrite:
  `Sodium valproate requires a Pregnancy Prevention Program (RANZCP/TGA 2023) - LARC in place and annual specialist review - if prescribed to any female of childbearing potential; avoid entirely where alternatives exist.`
  Source: [RANZCP valproate resources](https://www.ranzcp.org/news-analysis/ranzcp-secures-major-pbs-listing-for-bipolar-disorder-treatment)

- **Osteoporosis** — "Oral bisphosphonate (alendronate or risedronate) is first line, with denosumab or IV zoledronate as alternatives." The **2024 RACGP + Healthy Bones Australia** guideline supersedes 2017 and: (a) recommends **very-high-risk patients start with anabolic agent (teriparatide, romosozumab) first-line, not bisphosphonate**, referred to specialist; (b) explicitly warns denosumab must **never** be discontinued without follow-on antiresorptive (rebound vertebral fracture). Suggested rewrite:
  `Oral bisphosphonate (alendronate, risedronate) first-line for most; denosumab or IV zoledronate as alternatives. Very-high-risk patients (T-score ≤-3, multiple vertebral fractures) get up-front bone anabolic (teriparatide, romosozumab) per 2024 RACGP/Healthy Bones Australia guideline - specialist referral. Denosumab must never be stopped without follow-on bisphosphonate or zoledronate infusion - rebound vertebral fractures.`
  Source: [MJA 2024 RACGP/HBA guideline](https://www.mja.com.au/journal/2025/222/9/2024-royal-australian-college-general-practitioners-and-healthy-bones-australia)

- **Hypertension** — "First-line agents are an ACE inhibitor or ARB, a dihydropyridine calcium channel blocker, or a thiazide-like diuretic". Correct for AU practice, but current summary omits the **2023 Australian CVD Risk Guideline** framing - AU practice is now to treat by **absolute 5-year CVD risk** (low <5%, intermediate 5-10%, high ≥10%), not BP threshold alone, with pharmacotherapy at ≥10% risk. Suggested addition:
  `Australian threshold for initiating antihypertensive is guided by absolute 5-year CVD risk (Aus CVD Risk Calculator 2023): pharmacotherapy at ≥10% (high risk) or persistent BP ≥160/100 regardless of risk. First-line agents are an ACE inhibitor or ARB, a dihydropyridine calcium channel blocker, or a thiazide-like diuretic; low-dose combination beats maximising one agent.`
  Sources: [2023 Aus CVD Risk Guideline MJA](https://www.mja.com.au/journal/2024/220/9/2023-australian-guideline-assessing-and-managing-cardiovascular-disease-risk); [cvdcheck.org.au](https://www.cvdcheck.org.au/)

### MINOR issues

- **Osteoarthritis** — "Paracetamol then topical NSAID (diclofenac gel); oral NSAID in short bursts with PPI." Current RACGP guideline is more skeptical of paracetamol monotherapy for knee/hip OA (small effect size); topical NSAID for knee/hand OA is now first-line pharmacological. Add duloxetine (recommended by ACR, considered in AU practice for refractory pain). Minor rephrase to lead with topical NSAID for knee/hand.

- **Heart failure** — Four pillars correctly listed. Minor: "ARNI or ACE inhibitor" - AU practice (per CSANZ 2018 consensus + 2022 MJA update) now recommends **ARNI first-line** for HFrEF (not just as ACEi alternative), reserving ACEi/ARB where sacubitril/valsartan not tolerated or PBS criteria unmet. Also "In HFpEF, an SGLT2 inhibitor" is correct for 2024, but could mention that finerenone (non-steroidal MRA) has emerging evidence in HFpEF (not yet PBS-listed for HF).

- **Hyperthyroidism / Graves disease** — Says "propylthiouracil in the first trimester of pregnancy" which is correct. But should note the **switch back to carbimazole after week 16** to avoid PTU hepatotoxicity. Currently missing that switch.

- **Hypothyroidism** — Doses OK. Missing: standard weight-based starting dose of **1.6 microgram/kg/day** for healthy young adults (or 25-50 mcg titrated in elderly/IHD) - only "starting low in the elderly" is mentioned. Minor.

- **Pulmonary embolism / DVT** — DOAC first-line correct. Missing: **DOACs now acceptable for cancer-associated VTE** per updated ISTH 2022 and NPS guidance (previously LMWH only). Summary says "low molecular weight heparin in pregnancy and cancer" which is stale for cancer.

- **Post-MI (Myocardial infarction)** — Secondary prevention listed as "dual antiplatelet therapy; statin; ACE inhibitor; beta-blocker". CSANZ 2025 ACS update: **beta-blocker only if LVEF <40%** for long-term; no benefit beyond 12 months in preserved EF (REDUCE-AMI etc). Currently reads as universal.

- **Gout** — Urate target 0.36 mmol/L given. Missing the tighter target of **<0.30 mmol/L for tophaceous or erosive disease**. Also, RACGP allopurinol start dose is typically 50-100 mg/day (not the 100 mg the summary implies via omission) with slow titration in CKD; the entry is silent on start dose which is fine at summary level.

- **OCD** — "SSRI at higher doses than for depression (fluoxetine 40 to 80 mg, sertraline 100 to 200 mg, escitalopram 20 mg)" — dosing is accurate. Minor: "12 weeks before judging response" - RANZCP suggests **8-12 weeks at max tolerated dose**. Consistent.

- **Epilepsy** — "Levetiracetam or lamotrigine for both focal and generalised" — acceptable summary, but NICE (which AU largely mirrors via eTG) recommends **lamotrigine or levetiracetam first-line for focal**; **sodium valproate first-line for generalised in males/post-menopausal females**; **lamotrigine or levetiracetam for generalised in childbearing potential**. Current wording is broadly correct but generic.

- **CGRP for migraine** — see substantive above.

- **GORD** — Says "Pantoprazole or esomeprazole once daily before breakfast for 4 to 8 weeks, then step down." Correct per NPS. Minor: NPS explicitly recommends attempting step-down/PRN dosing after 4-8 weeks - the "then step down" is right but could be strengthened. No error.

- **Ulcerative colitis / Crohn** — Biologic lists include tofacitinib/upadacitinib (JAK) which are current for AU. Minor: **risankizumab** now PBS-listed for UC (Sept 2024) - correctly listed under Crohn but could add under UC.

- **Adrenal insufficiency / Addison** — Sick-day rule is stated as "double the dose during illness" which is correct for moderate stress. Missing IM hydrocortisone kit and steroid card as active recommendations - both are mentioned but as afterthought. Minor.

- **SLE** — Hydroxychloroquine anchor correct. Minor: **belimumab** and **anifrolumab** now PBS-listed for active SLE (Sept 2023 onwards) - not mentioned; only mycophenolate/cyclophosphamide listed for organ-threatening.

- **Trigeminal neuralgia** — Carbamazepine first-line correct. Missing sodium monitoring caveat (SIADH risk, particularly in older patients) which is a common AU exam and clinical point. Entry mentions "check sodium and FBC" - actually adequate.

- **Peripheral arterial disease (duplicate entries 471 and 472)** — Two identical entries (word-for-word) exist. Not a content error but a data hygiene issue for Rob to consider dedup.

- **Generalised / Generalized anxiety disorder (duplicate entries 243 and 244)** — Two very similar entries, one with US spelling. Data hygiene.

- **Wolff-Parkinson-White (duplicates 683 and 684)** — same.

### VERIFIED accurate

- Addison disease (hydrocortisone + fludrocortisone, sick-day double rule, IM emergency kit)
- Adrenal crisis (hydrocortisone 100 mg IV stat, 200 mg/24h)
- Bronchiectasis (airway clearance foundation, azithromycin selected, Pseudomonas eradication)
- COPD (post-BD FEV1/FVC <0.7, stepped inhaler LAMA/LABA → dual → +ICS if eosinophils; target sats 88-92% in exacerbation)
- Congenital hypothyroidism (levothyroxine 10-15 mcg/kg/day before 2 weeks, separate from soy/iron)
- Crohn disease (biologic ladder inc. risankizumab; smoking cessation; surveillance colonoscopy)
- Cystic fibrosis (elexacaftor-tezacaftor-ivacaftor PBS-listed for eligible genotypes)
- Diabetes insipidus (desmopressin for cranial; thiazide for nephrogenic)
- Eclampsia / Pre-eclampsia (magnesium sulfate; aspirin from 12 weeks for high risk)
- Frontotemporal dementia (SSRI for BPSD; avoid cholinesterase inhibitors)
- Gastro-oesophageal reflux disease (4-8 week PPI, alarm features for endoscopy)
- Gestational diabetes (ADIPS thresholds 5.1/10.0/8.5)
- Hashimoto (levothyroxine titrated; separate from iron/calcium/PPI by 4 hours)
- Hyperlipidaemia (statin dosed by absolute risk; PCSK9 PBS-restricted for FH)
- Hyperthyroidism (agranulocytosis warning; storm needs ICU)
- Hypertensive nephropathy (BP <130/80 KDIGO; ACEi/ARB even without proteinuria)
- Irritable bowel syndrome (Rome IV; low-FODMAP; peppermint oil; tricyclic for pain-predominant)
- Juvenile idiopathic arthritis (n/a scope)
- Lewy body dementia (avoid antipsychotics - neuroleptic sensitivity)
- Major depressive disorder (SSRI first-line; sertraline/escitalopram; RANZCP mood CPG)
- Multiple sclerosis (DMT started early; MRI + oligoclonal bands)
- Obstructive sleep apnoea (CPAP first-line for mod-severe; Austroads commercial driving)
- Oesophageal varices (restrictive Tx target 70 g/L; vasoactive + antibiotics + banding)
- Parkinson disease (levodopa most effective; never stop abruptly; DA agonists in younger)
- Polyarteritis nodosa (rituximab/cyclophosphamide + steroids)
- Polycystic kidney disease (BP <110/75 HALT-PKD; tolvaptan PBS)
- Polymyalgia rheumatica (prednisolone 12.5-25 mg with taper; giant cell arteritis red flags)
- Portal hypertension (SAAG ≥11 confirming portal origin)
- Postpartum depression (EPDS screening; sertraline preferred in breastfeeding)
- Primary biliary cholangitis (UDCA 13-15 mg/kg first-line; obeticholic acid second)
- Pseudogout (NSAID/colchicine/steroid; check ferritin/calcium/PTH/Mg for secondary)
- Pulmonary fibrosis (pirfenidone/nintedanib PBS-listed for confirmed IPF)
- Pulmonary hypertension (right heart cath confirms; group-specific therapy)
- Renal artery stenosis (medical therapy first; CORAL/ASTRAL; stenting only for narrow indications)
- Renal osteodystrophy (non-calcium binders preferred; calcimimetic for refractory)
- Schizophrenia (SGA first-line; clozapine for TR with mandatory neutrophil monitoring; metabolic monitoring)
- Social anxiety disorder (CBT + SSRI/SNRI; beta-blocker for performance-only)
- Thyroid eye disease (smoking cessation critical; IV methylpred EUGOGO)
- Thyroid storm (PTU before iodine; propranolol; hydrocortisone; ICU)

### UNVERIFIED (no clean public AU source found in scope)

- **ADHD** — "In Australia, paediatrician or psychiatrist diagnosis and initial prescription" is broadly true but the specifics vary by state (e.g., NSW/Vic allow GP shared-care after specialist initiation; QLD 2024 changes allow GP prescribing under conditions). Statement is safe but state-specific detail not audited here.
- **ADHD comorbidities** — accurate impression, not verified against specific numerator.
- **Idiopathic intracranial hypertension** — didn't verify acetazolamide/topiramate specifics against AU source.
- **Peripheral arterial disease** — "beta-blockers are not contraindicated, despite the persistent myth" - correct per ACC/AHA and BHF but not verified against a specific AU statement.
- **Renal osteodystrophy** — target PTH range (2-9x ULN in KDIGO 2017) not restated in entry; verified adequate at summary level.
- **Trigeminal neuralgia** — MRI dedicated sequences and MVD (Jannetta) as durable Rx - correct per international sources; no dedicated AU society guideline located.

## Notes

- **Duplicate entries** — three near-duplicates found (Peripheral arterial disease vs Peripheral artery disease; Generalised vs Generalized anxiety disorder; Wolff-Parkinson-White vs Wolff-Parkinson-White syndrome). Not part of first-line audit but worth Rob's eyes for the deferred duplicate-audit work-stream flagged in memory. Confirms the coverage-check-via-canonical concern.
- **CHA2DS2-VA rule** is high-priority - Rob's memory explicitly flags this as an AU-specific exam and clinical point.
- **Anti-amyloid drift** — the Alzheimer entry was correct 12-18 months ago; now stale. Worth adding a "check date" convention for anti-amyloid / DMARD / PBS references so drift is easier to spot.
- **PBS is a moving target** — Migraine CGRP mAb list, biologic lists (UC/Crohn/RA/SLE), and SGLT2i CKD thresholds are the highest-drift areas. Rob may want a PBS-listing sweep as a separate pass.
- **No em-dashes used**; per memory rule. Space-hyphen-space throughout.
- The summary "Diabetes mellitus" entry needs a T1DM split - either separate entries or a mandatory T1DM sentence early in the Mx. This is the single most user-facing gap.
- **Post-MI beta-blocker duration** (12 months preserved EF vs indefinite for LVEF <40%) is a growing exam and clinical point per CSANZ 2025 ACS update - worth revisiting as more data accrues.
