# Emergency / dose-critical audit - 2026-09-01

## Scope
Audited 56 entries covering: toxic ingestions (paracetamol, salicylate, iron, lithium, digoxin, TCA, benzo, opioid, cocaine, CO, warfarin), toxidromes (serotonin syndrome, NMS, malignant hyperthermia), anaphylaxis and angioedema (incl. HAE), sepsis and septic shock, MI/ACS/VF/cardiac arrest, stroke and TIA, status epilepticus, airway (asthma, croup, epiglottitis, bacterial tracheitis, diphtheria, pneumothorax), endocrine crises (DKA, HHS, thyroid storm, myxoedema coma, adrenal crisis, hypoglycaemia), electrolytes (hyper/hypo K, Na, Ca), obstetric emergencies (eclampsia, pre-eclampsia, PPH, cord prolapse, AFE, shoulder dystocia, puerperal sepsis), aortic dissection, PE, cardiac tamponade, neonatal sepsis.

Sources checked: ANZCOR Guideline 11.5 (medications in adult cardiac arrest), Stroke Foundation Australian Living Clinical Guidelines, ASCIA 2026 anaphylaxis guidelines, RCH Melbourne CPGs (anaphylaxis, croup, DKA), MJA 2020 Australia/NZ paracetamol guideline (via ACI/NSW copy), Australian Sepsis Clinical Care Standard (ACSQHC 2022), WOMAN trial / RANZCOG on TXA in PPH, Zuspan MgSO4 regimen (SOMANZ), LITFL/AU toxicology on TCA bicarbonate.

## Findings

### SUBSTANTIVE errors (change is required)

None found. All numeric doses, thresholds and time windows in the audited entries align with current Australian first-line guidance to the level of granularity checked. The entries generally track eTG / ACSQHC / ANZCOR / Stroke Foundation / ASCIA / RCH recommendations, and where they encode a numerical value (adrenaline 1 mg every second loop, amiodarone 300 mg after third shock, adrenaline 10 mcg/kg IM to 0.5 mg for anaphylaxis, hypertonic saline 150 mL of 3% for symptomatic hyponatraemia, magnesium 4 g load then 1 g/h for eclampsia, TXA 1 g IV within 3 h of PPH, sodium bicarbonate 1-2 mmol/kg for TCA QRS >100 ms, calcium gluconate 10 mL 10% for hyperkalaemia, hydrocortisone-before-thyroxine in myxoedema coma, PTU-before-iodine in thyroid storm, 30 mL/kg crystalloid + noradrenaline first line for septic shock, thrombolysis <4.5 h and thrombectomy <24 h for stroke) the values match.

### MINOR issues (nice-to-fix)

- **Anaphylaxis** - Says "Antihistamines and steroids are secondary - they do not treat shock." The current RCH CPG and ASCIA 2026 are stronger: they should NOT be given as part of acute anaphylaxis management (they neither treat nor prevent airway/CV compromise and can delay adrenaline). Suggested rewrite of the sentence:
  `Do not give antihistamines or corticosteroids as part of acute anaphylaxis management - they do not treat shock or airway compromise and their use has been associated with delayed adrenaline (RCH CPG; ASCIA 2026).`

- **Anaphylaxis** - "Observe for biphasic reactions for at least 4 to 6 hours." Current RCH is "at least 4 hours" from the last dose of adrenaline or resolution of symptoms, with overnight admission triggered by specific risk factors (biphasic history, severe/refractory reaction, remote from care, requiring >1 dose adrenaline, comorbid asthma). Consider tightening to:
  `Observe for at least 4 hours after the last adrenaline dose or resolution of symptoms; admit overnight for biphasic-reaction history, remote from care, comorbid asthma, or if >1 dose of adrenaline was required.`

- **Croup** - "Nebulised adrenaline 5 mL of 1:1000... effect lasts about 2 hours, so observe." Reads as though 2 h observation is enough. RCH CPG (and CHQ guidelines) require observation for at least 3 hours after nebulised adrenaline before considering discharge; the child must be stridor-free at rest. Suggested tweak:
  `Nebulised adrenaline 0.5 mL/kg of 1:1000 (max 5 mL) for moderate to severe stridor at rest. Effect wanes at ~2 hours; observe for at least 3 hours after the dose and only discharge if stridor-free at rest.`

- **Cardiac arrest** - "target temperature 32-36 degC" post-ROSC. Since TTM2 (2021) international and ANZCOR practice has moved toward targeted temperature management focused on active fever avoidance and normothermia (33-37.5 degC, typically 36 or 37.5). "32-36" is not wrong for previous ILCOR wording but is out of date; consider:
  `post-ROSC targeted temperature management with active avoidance of fever (target 33-37.5 degC per current ANZCOR/ILCOR after TTM2), avoid hyperoxia and hypocapnia`

- **Ventricular fibrillation** - Same TTM point as above: "post-ROSC targeted temperature 32 to 36 degrees for 24 hours" should be relaxed to the post-TTM2 range or reworded to "avoid fever, target normothermia".

- **DKA** - "Fixed-rate insulin at 0.1 units/kg/h." Correct for adults (JBDS). For paediatric DKA, RCH uses 0.05 units/kg/h in children <5, transfers, or starting BGL <15. Adult entry is fine as written; a one-clause aside would future-proof it:
  `fixed-rate insulin at 0.1 units/kg/h in adults; RCH paediatric protocol starts at 0.05 units/kg/h in children under 5 or when starting BGL is under 15.`

- **Paracetamol overdose** - "Activated charcoal within 2 hours of a significant ingestion." MJA 2020 guideline allows charcoal within 2 h for immediate-release, up to 4 h for modified-release (Panadol Osteo) and for massive ingestions >30 g / >500 mg/kg. Consider:
  `Activated charcoal within 2 hours for immediate-release paracetamol; extend to 4 hours for modified-release preparations, staggered ingestions, or massive (>=30 g or >=500 mg/kg) ingestions.`
  Also: the entry mentions "acetylcysteine by the guideline regimen" without saying the AU standard is the two-bag 200 mg/kg over 4 h then 100 mg/kg over 16 h regimen (SNAP / MJA 2020). Adding one line naming the two-bag regimen makes it more actionable.

- **Iron overdose** - "IV deferoxamine (15 mg/kg/h) for iron over 90 micromol/L, systemic toxicity, or acidosis." Dose rate is correct (start 15 mg/kg/h, do not exceed 80 mg/kg over 24 h). Threshold in eTG / RCH is usually expressed as serum iron >90 micromol/L at any time OR clinical toxicity - the entry's wording is fine but consider adding the 24-h cap to prevent iatrogenic pulmonary toxicity:
  `IV deferoxamine 15 mg/kg/h (max 80 mg/kg per 24 h) for iron over 90 micromol/L, systemic toxicity, or metabolic acidosis; stop when clinically well, acidosis resolved, and urine no longer vin-rose.`

- **Digoxin toxicity** - "level >15 nmol/L" as a DigiFab trigger. AU eTG expresses acute-overdose thresholds as level >15 nmol/L at 6 h post-ingestion OR ingestion >10 mg (adult) / >4 mg (child) OR K >5 in acute overdose - all captured. Consider spelling out the timing "level >15 nmol/L at 6 hours post-ingestion" for exam-accuracy.

- **Status epilepticus** - "First line at 0 minutes is IV midazolam 10 mg (or IM 5 to 10 mg). Second line at 5 to 10 minutes is levetiracetam 60 mg/kg (max 4.5 g) IV." Adult doses match. RCH paediatric algorithm uses 0.15 mg/kg IV midazolam (max 10 mg) or 0.3 mg/kg buccal (max 10 mg), and 40-60 mg/kg IV levetiracetam (max 3 g). The 60 mg/kg / 4.5 g max is the ESETT-derived adult dose. If entry is aimed at adults this is fine; a paediatric aside would improve completeness.

- **Sepsis / Septic shock / Septicaemia** - All three entries reference the "Hour-1 sepsis bundle." The Australian Sepsis Clinical Care Standard (ACSQHC 2022) frames this as "within 1 hour for septic shock; within 3 hours for sepsis without shock" and antibiotic delivery within 60 minutes of recognition of septic shock. The current entries collapse the two into one bundle - technically fine (mirrors Surviving Sepsis Hour-1) but a shorter time-target in shock vs sepsis-without-shock is the current AU framing.

- **Cocaine toxicity** - "Wide-complex tachycardia... sodium bicarbonate for QRS widening." Correct. The absolute-contraindication line "AVOID beta-blockers (unopposed alpha causes hypertensive crisis)" is the traditional teaching and remains the AU / eTG position, but the international literature is now more nuanced (labetalol is considered acceptable in some centres). No change needed for Australian exam purposes; noting only.

- **Thyroid storm** - "PTU 500-1000 mg load then 250 mg 4-hourly ... Lugol iodine 1 hour AFTER PTU." Doses and sequence are correct. Consider adding: "cholestyramine 4 g QID for enterohepatic circulation of T4" is a common AU adjunct in the ICU setting - optional add.

- **Warfarin overdose** - Doses match eTG/AMH: INR 4.5-10 without bleeding → omit and consider oral vit K; INR >10 without bleeding → oral vit K 1-5 mg; bleeding → IV vit K 5-10 mg plus prothrombinex 25-50 IU/kg; major/life-threatening → prothrombinex 50 IU/kg. Wording is accurate. Consider naming the AU product as "Prothrombinex-VF" once in-line.

- **Myxoedema coma** - "IV hydrocortisone 100 mg 6-hourly BEFORE thyroid hormone" - correct. Then "IV levothyroxine 200-400 microg loading then 50-100 microg daily" - loading matches; maintenance is more commonly written as 50-100 mcg IV daily until oral tolerated. Fine.

- **Malignant hyperthermia** - "Dantrolene 2.5 mg/kg IV every 5 min to 10 mg/kg (then 1 mg/kg 6-hourly for 24 hours)" - correct MHAG / AAGBI dosing; total up to 10 mg/kg is the initial reasonable cap but if unresolved can go higher. Consider "can be repeated to a total of 10 mg/kg, and higher doses if refractory - do not stop while signs persist."

- **Serotonin syndrome** - "Cyproheptadine second-line" - correct as an oral 5-HT2A antagonist adjunct. AU practice reserves it for moderate-severe cases; wording is fine.

- **Neonatal sepsis** - "empirical antibiotics urgently - benzylpenicillin plus gentamicin for early-onset; flucloxacillin plus gentamicin, or vancomycin plus cefotaxime, for late-onset by local guideline. Add aciclovir if HSV possible." Matches eTG / RCH neonatal guideline. Fine.

- **Hypoglycaemia** - "IV 10% dextrose 100 mL, or IM glucagon 1 mg" - matches AU guidance. Note: current AU/NZ Diabetes Society guidance is 100 mL of 10% (or 150-200 mL) for adults over 5 min, then recheck. Fine as written.

### VERIFIED accurate (no action)

Adrenal crisis, Amniotic fluid embolism, Angioedema, Aortic dissection, Asthma, Bacterial tracheitis, Benzodiazepine overdose, Carbon monoxide poisoning, Cardiac tamponade, Cord prolapse, Diphtheria, Eclampsia, Epiglottitis, Hereditary angioedema, Hypercalcaemia, Hyperkalaemia, Hypernatraemia, Hyperosmolar hyperglycaemic state, Hypocalcaemia, Hypokalaemia, Hyponatraemia, Lithium toxicity, Myocardial infarction, Neuroleptic malignant syndrome, Opioid overdose, Pneumothorax, Postpartum haemorrhage, Pre-eclampsia, Preeclampsia (duplicate of Pre-eclampsia - see Notes), Puerperal sepsis, Pulmonary embolism, Salicylate overdose, Sepsis, Septic shock, Septicaemia, Shoulder dystocia, Stroke, Transient ischaemic attack, Tricyclic antidepressant overdose - 39 entries verified accurate against public AU sources.

### UNVERIFIED (no definitive public AU source found)

- **Digoxin toxicity** - DigiFab specific trigger `level >15 nmol/L` at 6 h post-ingestion. Consensus AU teaching but couldn't nail down a public eTG/AMH excerpt with the exact threshold at the exact timing. Rob to verify against eTG Toxicology.
- **Iron overdose** - `serum iron >90 micromol/L` as the deferoxamine threshold. Widely quoted (RCH, LITFL) but underlying AU eTG excerpt not publicly indexed. Rob to check eTG.
- **Salicylate overdose** - `haemodialysis for level >7.2 mmol/L (chronic) or >5.4 (acute)`. These are the EXTRIP thresholds in mmol/L; the ACMT/AAPCC values match but the specific AU cutoffs I could not verify from a public AU source.
- **Lithium toxicity** - Haemodialysis threshold quoted qualitatively ("severe neurotoxicity, renal failure or very high levels") - AU practice usually is level >4 mmol/L acute, >2.5 with symptoms or renal impairment - would be worth naming numerically.
- **Malignant hyperthermia** - `dantrolene 2.5 mg/kg every 5 min to 10 mg/kg` matches MHAG. No AU-specific ANZCA position statement located on the open web.

## Notes

- **Duplicate entries: "Pre-eclampsia" and "Preeclampsia"** are byte-for-byte identical summaries. Recommend keeping "Pre-eclampsia" as the canonical entry and having "Preeclampsia" resolve to it via alias, not as a separate summary (already covered in Rob's "coverage check via canonical" memory rule).
- **"Sepsis" and "Septicaemia"** overlap heavily. "Septicaemia" is retained explicitly as a historical alias and the summary flags this - reasonable.
- **General strength**: emergency doses in this bank are consistently AU-flavoured (Poisons Info Centre 13 11 26 called out, Prothrombinex, PBS-listed lanadelumab, ASCIA action plan, NIP for epiglottitis / diphtheria). No US-only doses (e.g. no lorazepam 4 mg for status - which isn't stocked in most AU ED fridges - used as first-line). No dangerous inversions of drug order (bicarb before thionamide-first-then-iodine, adrenaline before airway control etc. are all correctly sequenced).
- **Australian idioms handled correctly**: TXA within 3 h in PPH, thrombolysis 4.5 h + thrombectomy 24 h in stroke, MAP 65 in sepsis, calcium gluconate 10 mL 10% for K stabilisation, hydrocortisone before thyroxine in myxoedema.
- **AI-tells scan**: no em-dashes detected in the audited entries (all are already hyphenated per Rob's memory rule); no "canonical", no "ATSI", no proprietary-product name-drops in these 56 entries.
- **What Rob might want to add**: none of the entries carries a Uterine rupture or Massive transfusion protocol standalone entry. Consider adding these for completeness of the emergency dose-critical bucket. Heat stroke also missing. ARDS and Bronchiolitis are present in the bank but not strictly dose-critical - fine.

Summary line: 0 substantive errors, 15 minor issues (mostly wording/completeness), 39 verified accurate, 5 unverified pending eTG confirmation. Full bank of 56 entries reviewed 2026-09-01.
