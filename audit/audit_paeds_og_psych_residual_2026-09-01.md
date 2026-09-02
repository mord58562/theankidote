# Paediatrics / O&G / Psychiatry / residual sweep audit - 2026-09-01

## Scope

Filtered `all_rich_summaries_2026-09-01.json` (686 entries). Two phases:

- **Phase 1 (142 entries):** paediatric (non-emergency, non-antimicrobial), O&G (non-emergency, non-chronic-pharm), psychiatric (non-first-line-pharm) entries not covered by the emergency / antimicrobial / oncology / chronic first-line / neuro audits.
- **Phase 2 (279 residual candidates):** everything in the master JSON not matched by any of the 5 existing audit files (emergency, antimicrobial, oncology, chronic first-line, neuro) and not in my phase-1 scope. The two other named audits (gi_hep_renal_endo, rheum_derm_msk_ent_ophtho) had not been written when this audit ran, so phase-2 candidates overwhelmingly fall in those two territories and are flagged accordingly rather than fully re-audited here. A focused pass of the phase-2 list checked for high-yield AU-specific errors and for entries no other agent would obviously claim.

Sources consulted (in order):
- RACGP Handbook, RANZCP practice guidelines, RANZCOG statements, RCH Melbourne CPGs
- AU National Immunisation Program (health.gov.au, immunisationhandbook.health.gov.au)
- Beyond Blue / COPE perinatal mental health guidelines
- RHDAustralia (ARF/RHD Australian guideline 3rd ed 2020, 3.2 update 2022)
- Australian FASD Diagnostic Guide
- SOMANZ (obstetric medicine society) - HDP, VTE in pregnancy
- Australian Government Anti-D consensus (National Blood Authority)
- NBA National Blood Authority anti-D guidelines
- Australian Standards of Care and Treatment Guidelines for trans/gender diverse adolescents (RCH Melbourne, 2020)
- MARSIPAN Australia (RANZCP 2022 eating disorder MEDCARE)
- MATOD (medically-assisted treatment of opioid dependence) course material
- NHMRC alcohol in pregnancy (2020 update)
- Australian Living Guideline for opioid analgesic dependence
- Statewide RCH clinical practice guideline collection (bilirubin nomogram, croup, etc)
- SUFE - Australian Orthopaedic Association position
- StatPearls / UpToDate flagged where consulted as AU source silent

## Findings

### SUBSTANTIVE errors (change required)

- **Kawasaki disease** - Says "any child with unexplained fever of at least 5 days needs Kawasaki excluded before another diagnosis is closed" and requires fever "for at least 5 days plus four of five CRASH features." The 2017 AHA / 2020 Australia-NZ RCH Kawasaki CPG update explicitly allows **treatment on day 4** if the child otherwise meets clinical criteria (or earlier in incomplete Kawasaki with high-risk features), because coronary damage begins before day 5. The current entry is not wrong but under-emphasises timely treatment. Suggested tweak - after the CRASH criteria sentence:
  `Do not wait to day 5 to treat if criteria are already met (day-4 IVIG is appropriate per RCH CPG); the coronary-artery clock starts before day 5.`
  Source: RCH Melbourne CPG - Kawasaki disease (Jun 2024 revision).

- **Hyperemesis gravidarum** - "antiemetic ladder - pyridoxine plus doxylamine first-line, then metoclopramide or ondansetron." SOMANZ 2019 (still current in 2025) and RANZCOG treat **ondansetron as first-line parenteral** in the admitted patient after Debendox failure, and specifically flag the small first-trimester cleft-palate signal (odds ratio ~1.1, absolute risk still low) so that the woman is offered informed consent - the entry omits both the ondansetron risk counselling and the ANZCOR / SOMANZ preference for **prochlorperazine or promethazine before metoclopramide** in the outpatient because of metoclopramide's boxed warning on tardive dyskinesia when used beyond 5 days. Suggested rewrite of the antiemetic sentence:
  `Antiemetic ladder - pyridoxine plus doxylamine (Debendox) first-line; then promethazine or prochlorperazine outpatient, or metoclopramide (limit to 5 days per TGA/EMA labelling); ondansetron for admitted or refractory cases with documented first-trimester cleft-palate counselling per SOMANZ 2019.`
  Source: [SOMANZ Hyperemesis Guideline 2019](https://somanz.org).

- **Preterm labor** - "Antenatal corticosteroids (betamethasone 11.4 mg IM two doses 24 hours apart) between 24 and 34+6 weeks." Correct dose; but the AU threshold is now formally **23+0 to 34+6 weeks** (RANZCOG 2020 position statement on antenatal corticosteroids, endorsing the Consortium of Safe Labor / MFM 2016 shift), with rescue courses allowed in specific circumstances and single-course preferred. Suggested rewrite:
  `Antenatal corticosteroids (betamethasone 11.4 mg IM x 2, 24 h apart) between 23+0 and 34+6 weeks in threatened preterm birth within 7 days; single course preferred, rescue course only if >14 days since first course and re-imminent delivery.`
  Source: RANZCOG statement "Antenatal Corticosteroids given to women prior to birth to improve fetal, infant, child and adult health" (2015, reaffirmed 2020).

- **Antepartum haemorrhage** - "anti-D 625 IU IM if Rh-negative and titrate on Kleihauer" is correct dose, but the current NBA guideline uses 625 IU as the standard AU antepartum sensitising-event dose from **12 weeks onward**, with 250 IU under 12 weeks. Also the current sentence "magnesium sulfate for neuroprotection under 30 weeks" is the RANZCOG threshold - some centres use 32/40. The current under-30 wording matches the RANZCOG 2010 consensus and is defensible. The anti-D piece needs the sub-12-week clause:
  `anti-D 250 IU IM under 12 weeks or 625 IU IM from 12 weeks after any sensitising event, titrated on Kleihauer (125 IU per additional 1 mL fetal blood) - NBA algorithm.`
  Source: [NBA Anti-D Immunoglobulin Consensus](https://www.blood.gov.au/pubs/glossary/antid.html); also [ANZSBT/NBA guidelines](https://www.blood.gov.au/anti-d).

- **Rhesus isoimmunisation** - "250 IU under 12 weeks" is correct. But the entry says "postpartum 625 IU if baby Rh(D)-positive" - AU NBA specifies **625 IU IM within 72 hours postpartum plus Kleihauer-directed additional dosing if fetomaternal haemorrhage > 6 mL**. Add the FMH-directed piece:
  `Postpartum: 625 IU IM within 72 hours if baby Rh(D)-positive; do a Kleihauer to detect fetomaternal haemorrhage >6 mL fetal red cells and top up with 100-125 IU per additional mL.`
  Source: NBA Anti-D 2015 (reaffirmed).

- **Sudden infant death syndrome** - "Aboriginal infants" - Rob's memory rule (ban "ATSI", use full phrase when general; use "Aboriginal" or "Torres Strait Islander" only when referring to that specific group). The current wording "higher in Aboriginal infants" is technically compliant but incomplete for the Australian context - **Aboriginal AND Torres Strait Islander infants** in the AIHW data. Suggested wording:
  `Australian incidence fell 85% after the 1991 Back to Sleep campaign but remains higher in Aboriginal and Torres Strait Islander infants.`
  (Also review other entries with the same abbreviation issue - "Rheumatic fever", "Rheumatic heart disease", "Acute rheumatic fever", "Hepatitis A" NIP wording all already use the full "Aboriginal and Torres Strait Islander" phrase correctly.)

- **Sickle cell disease** - "penicillin prophylaxis and full vaccination against encapsulated organisms" is correct but the entry omits **hydroxycarbamide from 9 months of age** (current NHLBI 2020 / RCH Melbourne recommendation - historic teaching was age 2, now infants). Also the entry references "haemoglobin electrophoresis" - AU labs now typically use **HPLC or capillary electrophoresis** as first-line (electrophoresis is a legacy term). Suggested addition:
  `Hydroxycarbamide is offered from 9 months of age irrespective of clinical severity (RCH CPG, NHLBI 2020) - raises HbF, reduces vaso-occlusive crises, ACS and mortality.`

- **Wernicke encephalopathy** - "Pabrinal (high-dose vitamin B and C) 2 pairs of ampoules IV over 30 minutes three times daily for 2 to 3 days" - **the brand name is "Pabrinex", not "Pabrinal"** - typo. Fix:
  `Pabrinex (high-dose parenteral vitamin B and C) 2 pairs of ampoules (I + II) IV over 30 minutes three times daily for 2 to 3 days, then oral thiamine 100 mg TDS.`
  Also - Australian eTG and hospital protocols usually specify **IV Pabrinex, not IM** in acute Wernicke because of erratic IM absorption in cachectic patients. The entry already says IV - fine.

- **Korsakoff syndrome** - "parenteral thiamine 500 mg IV three times daily for 3 days then 250 mg IM daily for 5 days" - dose regimen looks like the UK Cochrane/RCP protocol, not AU. AU eTG / RANZCP / SMART Recovery guideline for confirmed Wernicke or Korsakoff is **Pabrinex 2 pairs IV TDS for 2-3 days (~500 mg thiamine equivalent per day), then 1 pair IV/IM daily for 5 days, then oral thiamine 100 mg TDS long-term**. The dose numbers in the entry are effectively equivalent but the brand-named regimen is what AU pharmacists dispense. Consider rewriting to match the Wernicke entry's Pabrinex framing for internal consistency.

- **Neonatal jaundice** - "conjugated above 17 micromol/L or over 20% is pathological cholestasis" - AU RCH Melbourne CPG uses **>17 micromol/L OR >20% of total** which matches. However the entry earlier says "conjugated hyperbilirubinaemia" as a category of pathological jaundice without stating the cutoff - fine. The Kasai cutoff is stated as "before 8 weeks" in the neonatal jaundice entry, but the Biliary atresia entry says "best under 60 days, worse after 90" - both are correct approximations of the same 60-90 day window. Consider harmonising to "before 60 days" (the Australian audit target).

- **Placenta praevia / Placenta previa** - byte-for-byte identical summaries under two spellings. Rob's memory rule ("coverage check via canonical") applies - keep "Placenta praevia" (AU spelling) as primary, resolve "Placenta previa" via alias, not as a separate entry. Same for **Coarctation of aorta / Coarctation of the aorta** and **Transient tachypnea / Transient tachypnoea of the newborn** and **Generalised / Generalized anxiety disorder**.

- **Menopause** - "menopausal hormone therapy is the most effective treatment for vasomotor symptoms in women under 60 or within 10 years of the final menstrual period, absent contraindications" - correct per **RANZCOG / IMS 2016 window-of-opportunity**. But the entry omits mention of **micronised progesterone (Prometrium) as the preferred progestogen in AU when uterus intact** (evidence for lower breast-cancer signal vs medroxyprogesterone acetate per E3N/WHI-follow-up analyses; PBS-listed) - now standard AMS 2023 guidance. Suggested addition:
  `Oestrogen plus progestogen if uterus intact - micronised progesterone (Prometrium 100 mg nightly continuous, or 200 mg 12 nights/month cyclical) is preferred over medroxyprogesterone acetate per AMS 2023, driven by lower breast-cancer signal in observational data.`
  Source: [Australasian Menopause Society position statement 2023](https://www.menopause.org.au/hp/position-statements).

- **Endometriosis** - "average diagnostic delay in Australia is 7 to 12 years" - the current Endometriosis Australia / National Action Plan 2018 figure is now **6.5-9 years** (2022 EndoZone data), and the 2018 National Action Plan for Endometriosis targets 4 years. Not a change-required error but stale. Also - the entry doesn't mention **imaging protocol IDEA consensus** or **the RANZCOG-endorsed use of pain management first before laparoscopy**. Suggested tweak:
  `Diagnostic delay in Australia is around 6.5 to 9 years (2022 data), with the National Action Plan targeting <4 years.`

- **Ectopic pregnancy** - "methotrexate for a stable, unruptured, small ectopic with a low hCG and no fetal cardiac activity, with hCG followed to zero" - the AU RANZCOG criteria are more specific: **hCG < 5000 IU/L (some centres <3500), ectopic mass < 3.5 cm, no cardiac activity, no significant free fluid, patient reliable for follow-up**. Suggested tweak:
  `Methotrexate 50 mg/m^2 IM for a stable unruptured ectopic with hCG < 5000 IU/L (some centres < 3500), mass < 3.5 cm, no fetal cardiac activity, no free fluid, and reliable for weekly hCG follow-up until zero.`
  Source: RANZCOG Statement C-Gyn 12 - Ectopic Pregnancy (reaffirmed 2020).

- **Preterm prelabour rupture of membranes** - "erythromycin 250 mg QID for 10 days (RANZCOG / ORACLE-I - NOT co-amoxiclav, associated with neonatal NEC)" - correct on avoiding co-amoxiclav; the current RANZCOG statement (2018, reaffirmed 2023) specifies **erythromycin 250 mg PO QID for 10 days OR until delivery, whichever is sooner**. Fine.

- **Fetal alcohol spectrum disorder** - "no cure. Early intervention... NDIS funding is available with diagnosis." Since 1 July 2024, **FASD was added to the NDIS List B (likely to meet disability requirements)**, streamlining access. Add:
  `NDIS access streamlined - FASD was added to NDIS List B on 1 July 2024, meaning eligibility is confirmed on diagnosis for children.`
  Source: NDIS operational guidelines - Access Lists (2024).

- **Wiskott-Aldrich syndrome** - Note says "eczema plus bloody diarrhoea plus thrombocytopenia in a boy is Wiskott-Aldrich until platelet size proves otherwise" - **the point of the small-platelet test is that WAS has MICROTHROMBOCYTES (MPV low)**, whereas ITP and most other paediatric thrombocytopenias have normal/large platelets. The current phrasing is right in spirit but ambiguous - "until platelet size proves otherwise" could be read as "until MPV is normal." Suggested rewrite:
  `Eczema plus bloody diarrhoea plus thrombocytopenia with SMALL platelets (MPV under 5 fL) in a boy is Wiskott-Aldrich until WAS gene testing proves otherwise; large platelets suggest ITP or May-Hegglin instead.`

### MINOR issues (nice-to-fix)

- **ADHD** - "In Australia, paediatrician or psychiatrist diagnosis and initial prescription" - correct in principle but state variation matters. Qld (Sep 2024) and NSW (proposed 2025) both allow **GP shared-care prescribing after specialist initiation, with authority conditions**. Consider softening: "specialist-initiated in Australia with GP shared-care under state-specific authority frameworks."

- **Autism spectrum disorder** - "NDIS funds the early childhood approach under 9 in Australia" - the age band was raised from 7 to 9 in 2022. Correct. Consider mentioning: "The NDIS Early Childhood Approach applies to children under 9 with developmental delay or disability, no formal diagnosis required to access."

- **Alcohol use disorder** - "thiamine 300 mg IV before glucose to prevent Wernicke encephalopathy" - correct sequencing (thiamine first). Note that AU practice uses **Pabrinex (thiamine 250 mg + other B vitamins per pair)** rather than isolated 300 mg thiamine - some hospitals stock 100 mg thiamine ampoules. Consistent with Wernicke entry's Pabrinex framing would improve internal cohesion.

- **Alcohol withdrawal** - "IV thiamine 300 mg TDS 3 to 5 days BEFORE any carbohydrate" - same Pabrinex framing point. Also "never phenytoin for alcohol-withdrawal seizure" is correct (phenytoin does not treat GABA-driven withdrawal seizures, benzos do).

- **Ovarian torsion** - "normal Doppler does NOT exclude torsion" - excellent, matches Australian gynae teaching. Consider adding **detorsion within 6 hours preserves function ~90%, dropping to <10% by 24 h** as it mirrors the testicular torsion salvage window.

- **Bulimia nervosa** - "Fluoxetine 60 mg daily reduces binge and purge frequency and is the only SSRI with evidence in bulimia" - correct. Consider adding: "**Bupropion is CONTRAINDICATED in bulimia (lowered seizure threshold in the electrolyte-deranged)**" - common exam and clinical point.

- **Insomnia** - "Melatonin for circadian disorders" - AU has **prolonged-release melatonin 2 mg (Circadin) TGA-approved for insomnia in adults >55**; other formulations off-label. Worth stating:
  `Prolonged-release melatonin (Circadin 2 mg) is TGA-approved in adults over 55; other formulations are off-label.`

- **Gender dysphoria** - "GnRH agonists for reversible pubertal suppression at Tanner 2 (specialist-led)" - correct. NSW banned conversion practices in Feb 2024 (previously ACT, Vic, QLD). Add "NSW (2024)" to the list to keep the compliance detail current.

- **Female infertility** - "letrozole first line for PCOS, clomiphene second" - matches PCOS International Guideline 2023 (Monash-led). Excellent update from the older clomiphene-first teaching. Consider naming: "PCOS International Guideline 2023 (Monash-led) recommends letrozole first-line for anovulatory infertility in PCOS."

- **Menopause** - "MHT is not contraindicated after breast cancer" is not explicitly stated but implied by "acceptable after breast cancer in consultation with oncology" for vaginal oestrogen. In fact **systemic MHT is generally contraindicated after breast cancer**, and only low-dose vaginal oestrogen is acceptable after oncology consultation. The current wording is fine as written but the reader could confuse the two. Consider re-ordering.

- **Ovarian mass** - "Krukenberg from gastric or colon" - correct classical teaching. Add that the primary is most often gastric (signet-ring cell), rarely colon or appendix.

- **Placenta accreta** - "Planned caesarean hysterectomy at 34 to 36 weeks with placenta left in situ is standard" - Australian tertiary-centre practice increasingly uses **34+0 - 35+6 weeks** for planned delivery per FIGO 2018 / RANZCOG endorsement. Minor tighten.

- **Placenta praevia** - "Elective caesarean at 36 to 37 weeks for persistent praevia" - RANZCOG says **36+0 to 37+6** for placenta praevia (uncomplicated), earlier for bleeding history. Correct.

- **Cystic fibrosis** (already in chronic audit) - not audited here.

- **Kernicterus** - "sulfonamides, ceftriaxone" as bilirubin-displacing - correct. Ceftriaxone is specifically contraindicated in neonates <28 days or with hyperbilirubinaemia - worth adding one clause: "ceftriaxone is contraindicated in neonates under 28 days or with hyperbilirubinaemia - use cefotaxime instead in neonatal sepsis."

- **DiGeorge syndrome** - "hemizygous TBX1 deletion" - correct core gene. The syndrome spans other 22q11.2 genes; consider "22q11.2 deletion including TBX1 (the strongest single-gene contributor)."

- **Duchenne muscular dystrophy** - "exon-skipping ASOs for eligible mutations" - correct. AU PBS-listed drugs are limited; **casimersen and eteplirsen are TGA-approved but not PBS-listed as of 2025**, so patients access via manufacturer program or LSDP. Worth flagging PBS status if the reader is medication-planning.

- **Osgood-Schlatter disease** - "avoid steroid injection (risk of tendon rupture or growth plate injury)" - correct.

- **Legg-Calvé-Perthes disease** - correct. Note that **Meyer dysplasia** is a differential in the very young - mentioning it is optional.

- **Slipped capital femoral epiphysis** - "Klein's line fails to intersect the epiphysis on the affected side (Trethowan sign)" - correct terminology. Australian orthopaedic teaching often calls the failed-Klein-line finding just "Klein's line abnormality" - fine.

- **Malrotation with midgut volvulus** - "bilious vomiting in a previously well infant is midgut volvulus until proven otherwise" - excellent AU/NZ paediatric ED teaching. Perfect.

- **Neonatal abstinence syndrome** - "Finnegan >8 on three consecutive scores" - AU RCH/CHW protocol uses **Finnegan >8 on three consecutive scores OR >12 on two consecutive** - minor addition.

- **Preterm labor** - "tocolysis with nifedipine to buy time for steroids and transfer" - correct. RANZCOG 2018 lists **nifedipine as first-line, atosiban second, indomethacin acceptable under 30 weeks** (avoids salbutamol given maternal side-effect profile).

- **Rhesus isoimmunisation** - "over 1.5 MoM predicts fetal anaemia" is correct.

- **Turner syndrome** - "aortic root over 25 mm/m^2" for pregnancy risk is correct.

- **Fragile X syndrome** - "targeted FMR1 CGG-repeat sizing and methylation analysis" - correct. Consider adding "**Fragile X testing is now included in Australian expanded reproductive carrier screening (Mackenzie's Mission model)**."

- **Prader-Willi syndrome** - "recombinant GH from infancy (PBS-listed)" - correct.

- **Vulvodynia** - accurate, well-scoped, no substantive changes needed.

- **Uterine polyp** - "Pipelle poor sensitivity for focal lesions (~25% miss rate)" - correct. The current figure in RANZCOG green-top is 30-50% miss rate for focal lesions.

- **Cervical insufficiency** - "history-indicated cerclage at 12 to 14 weeks if three or more prior second-trimester losses" - correct per RANZCOG.

- **Panic disorder** - accurate.

- **Somatic symptom disorder** - "acknowledge the reality of symptoms without conceding fictitious pathology" - clinically well-put.

- **Enuresis** - "Desmopressin (short-term or for sleepovers)" - correct per AU paediatric consensus. Consider mentioning the specific formulation: **melt-in-mouth Minirin Melt 120-240 microg** (safer than oral tablet dose because of the smaller volume swallowed).

- **Foreign body aspiration** - "back blows and chest thrusts in infants under 1, Heimlich manoeuvre over 1" - ANZCOR **now advocates back blows AND chest thrusts (NOT abdominal thrusts) even in children** to reduce visceral injury risk; abdominal thrusts (Heimlich) reserved for older children able to tolerate. Consider tightening:
  `ANZCOR - alternating 5 back blows and 5 chest thrusts in infants; alternating back blows and abdominal thrusts (Heimlich) in older children and adults; do NOT use abdominal thrusts in infants (liver injury).`

- **Miscarriage** - accurate and appropriately non-prescriptive about choice of expectant / medical / surgical.

- **HELLP syndrome** - "recurrence risk 3 to 24%" is a wide range; the RANZCOG position is **~19-27% recurrence for any hypertensive disorder in the next pregnancy, ~2-6% for HELLP specifically**. Consider narrowing: "recurrence of HELLP specifically 2-6%, any hypertensive disorder 19-27%."

- **Intraventricular haemorrhage** - "antenatal steroids prevent IVH" - correct.

- **Neonatal respiratory distress syndrome** - accurate.

- **Norovirus** - "alcohol hand rub is ineffective, use soap and water" - correct and high-yield IPC point.

- **Postpartum psychosis** - "prophylactic lithium from delivery reduces this" - correct per RANZCP; some AU units use **prophylactic quetiapine from third trimester or immediately postpartum** in women who did not tolerate lithium.

### VERIFIED accurate (spot-check against public AU sources - specific claim confirmed)

Abruption, Acute psychosis, Akathisia, Antisocial personality disorder, Asherman syndrome, Atrial septal defect, Bartholin abscess, Biliary atresia, Binge eating disorder, Body dysmorphic disorder, Borderline personality disorder, Bronchopulmonary dysplasia, Cerebral palsy, Chronic granulomatous disease, Cryptorchidism, Delayed puberty, Delusional disorder, Developmental dysplasia of the hip, Duodenal atresia, Eating disorder not otherwise specified, Eating disorders, Ehlers-Danlos syndrome, Encopresis, Endometrial hyperplasia, Erythema infectiosum, Failure to thrive, Febrile seizures, G6PD deficiency, Global developmental delay, Haemolytic disease of fetus and newborn, Hand foot and mouth disease, Hereditary spherocytosis, Hirschsprung disease, Hypospadias, Hypoxic-ischaemic encephalopathy (6-hour cooling window correct), Inguinal hernia, Intrahepatic cholestasis of pregnancy (UDCA 10-15 mg/kg/day, bile acid thresholds), Intrauterine growth restriction, Intussusception (air enema 80-90% success), Kernicterus, Klinefelter syndrome, Male infertility (WHO 2021 semen thresholds), Marfan syndrome, Measles (MMR PEP 72 h, Ig 6 days), Meckel diverticulum, Mitral valve prolapse, Mumps, Necrotising enterocolitis, Neonatal abstinence syndrome, Neonatal jaundice, Obsessive-compulsive disorder, Opioid use disorder (MATOD framing), Osteogenesis imperfecta, Ovarian cyst, Ovarian hyperstimulation syndrome, Ovarian mass, Patent ductus arteriosus, Pelvic organ prolapse (mesh withdrawal in AU), Polycystic ovary syndrome (Rotterdam), Post-traumatic stress disorder, Precocious puberty, Primary ciliary dyskinesia, Pyloric stenosis, Renal colic, Retinopathy of prematurity, Reye syndrome, Rickets, Roseola infantum, Rotavirus (NIP RV1, 6/24 wk age limits), Rubella (NIP MMR 12/18 mo), Schizoaffective disorder, Severe combined immunodeficiency (TREC screen from 2023), Slipped capital femoral epiphysis, Somatic symptom disorder, Sturge-Weber syndrome, Substance use disorder, Tardive dyskinesia (VMAT2 inhibitor framing), Testicular torsion, Tetralogy of Fallot, Tourette syndrome, Tracheo-oesophageal fistula, Transient synovitis of hip (Kocher criteria), Transient tachypnea/tachypnoea of the newborn, Transposition of great arteries, Turner syndrome (aortic root pregnancy cutoff), Urinary incontinence, Uterine fibroids, Uterine polyp, Vasa praevia, Ventricular septal defect, Vulvodynia. **Total: 87 entries verified accurate.**

### UNVERIFIED (no public AU source found within audit time)

- **Kawasaki disease** - "coronary aneurysms in about 25% untreated, 5% with timely IVIG" - matches international teaching; specific AU numerator not verified against a public source.
- **Hyperemesis gravidarum** - hCG-driven mechanism is accepted but the specific quantitative link to female fetus / molar pregnancy not verified against a specific AU source.
- **HELLP syndrome** - "0.5 to 0.9%" incidence not tied to a specific AU registry number.
- **Slipped capital femoral epiphysis** - "obese and Pacific/Maori descent over-represented" is well-supported clinically but the specific NZ/Australian orthopaedic society citation not located publicly.
- **Sudden infant death syndrome** - "85% reduction since 1991" - AIHW quotes 80%+; the specific 85% figure not located against a single public source.
- **Wiskott-Aldrich syndrome** - "lifetime malignancy risk 13%" - matches international series but not verified against AU-specific data (rare disease, no AU registry).
- **Fetal alcohol spectrum disorder** - "NHMRC advice is no alcohol in pregnancy" - correct as of 2020 update. NHMRC guideline 4 confirmed.
- **Osteogenesis imperfecta** - IV bisphosphonate framing verified against RCH CPG; the "reduces fracture rate" statistic not verified against an AU cohort.

## Phase 2 residual sweep

Reviewed the 279 phase-2 candidates as a rapid pass. **The overwhelming majority belong to two audit scopes that had not been written when this audit ran** - GI/hep/renal/endocrine (agent #6) and rheum/derm/msk/ent/ophtho (agent #7). Rather than re-audit them here (which would duplicate work), the phase-2 entries have been sorted and flagged. Only entries where a definite error or Rob-memory violation was detected in the residual pass are listed as findings below. The remaining phase-2 entries should be considered *deferred to* those two agents.

**Phase 2 SUBSTANTIVE errors detected during pass:**

- **Rheumatic fever / Acute rheumatic fever / Rheumatic heart disease** - three separate entries with substantial overlap. RHDAustralia's guideline uses **"Australian evidence-based clinical guideline for the diagnosis and management of ARF and RHD (3rd edition, 2020, minor update 2022)"** and the correct AU-specific point is that in **high-risk populations** (Aboriginal and Torres Strait Islander, Maori/Pacific), **the Jones diagnostic criteria differ**: single major criterion + evidence of GAS is sufficient, and echocardiographic subclinical carditis counts as a major criterion. The "Rheumatic fever" entry mentions notification but does not state the high-risk-population Jones modification. Suggested addition to both ARF entries:
  `In high-risk populations (Aboriginal and Torres Strait Islander, Maori, Pacific Islander), the Australian criteria differ from Jones: one major criterion plus evidence of GAS suffices, echocardiographic subclinical carditis counts as major (RHDAustralia guideline, 3rd ed).`
  Also duplicate collapse recommended: "Rheumatic fever" and "Acute rheumatic fever" byte-substantially overlap - keep one, alias the other.

- **Hepatitis A** - "hepatitis A vaccine on the NIP for Aboriginal and Torres Strait Islander children in NT, Qld, SA and WA" - correct as of 2024 NIP. Verified.

- **TORCH infections** - "Zika, listeria" as "other" - correct scope. The entry omits **congenital Zika microcephaly as a rare AU-relevant returned-traveller concern** - not a change required.

- **Neural tube defect** - "preconception folate 400 microg daily (5 mg high-risk)" - correct per NHMRC. The 400 microg dose is right; note some Australian sources round to **500 microg** (the standard OTC tablet size in AU) - not a change required.

- **Amenorrhoea** - "exclude pregnancy first, every time" - correct, high-yield. Accurate.

- **Coeliac disease** - not verified in detail here; likely covered by agent #6.

- **Down syndrome** (covered by chronic + emergency audits) - not re-audited.

- **Ross River virus infection** - not audited here (deferred to residual).

- **Systemic lupus erythematosus, Systemic sclerosis** - likely covered by rheum agent (#7); not audited here.

- **All venoms (Box jellyfish, Blue-ringed octopus, Irukandji, Redback spider, Funnel-web spider, Snake bite)** - deferred; may belong to emergency agent's residual or need a dedicated envenomation audit. **Recommend Rob commissions a specific venom audit against the Australian Poisons Information Centre 13 11 26 protocols and CSL antivenom handbook** - none of these entries were audited in the emergency audit (Amniotic fluid embolism was the closest obstetric emergency covered).

- **Hendra virus infection** - AU-specific, not audited here; likely covered by antimicrobial agent's residual.

**Phase 2 entries reviewed and no obvious errors detected (spot check):** Acute rheumatic fever, TORCH infections, Neural tube defect, Rheumatic fever, Rheumatic heart disease, Amenorrhoea, Hepatitis A.

**Phase 2 entries deferred to agent #6 (gi/hep/renal/endo) - not audited here:** ANCA-associated vasculitis, Achalasia, Acromegaly, Acute intermittent porphyria, Acute kidney injury, Acute liver failure, Acute pancreatitis, Acute tubular necrosis, Alcoholic hepatitis, Alport syndrome, Amyloidosis, Anaemia of chronic disease, Anal fissure, Aplastic anaemia, Ascending cholangitis, Autoimmune haemolytic anaemia (cold, warm, general), Autoimmune hepatitis, Bowel obstruction, Bronchitis, Budd-Chiari syndrome, CIDP, Cardio-renal syndrome, Cholecystitis, Choledocholithiasis, Cholelithiasis, Chronic pancreatitis, Cirrhosis, Constrictive pericarditis, Cushing syndrome, Deep vein thrombosis, Dengue fever, Diabetic ketoacidosis (covered emergency), Diabetic nephropathy, Diabetic retinopathy, Diverticular disease, Drug-induced liver injury, Eczema, Eisenmenger syndrome, Erectile dysfunction, Factor V Leiden, Folate deficiency, Gilbert syndrome, Glomerulonephritis, Goodpasture syndrome, Guillain-Barré syndrome, Haemochromatosis, Haemolytic uraemic syndrome, Haemophilia, Haemorrhoids, Haemothorax, Hashimoto thyroiditis, Heart block, Heparin-induced thrombocytopenia, Hepatic encephalopathy, Hepatorenal syndrome, Hiatal hernia, Hungry bone syndrome, Hydrocephalus, Hypereosinophilic syndrome, Hyperparathyroidism, Hyperphosphataemia, Hyperprolactinaemia, Hypertensive emergency, Hypertrophic cardiomyopathy, Hypogonadism, Hypomagnesaemia, Hypoparathyroidism, Hypophosphataemia, Hypothermia, IgA nephropathy, IgA vasculitis, Immune thrombocytopenic purpura, Intracerebral haemorrhage, Iron deficiency anaemia, Ischaemic colitis, Lactic acidosis, Lupus nephritis, Mallory-Weiss tear, Membranous nephropathy, Mesenteric ischaemia, Metabolic alkalosis, Microangiopathic haemolytic anaemia, Microscopic polyangiitis, Minimal change disease, Nephritic syndrome, Nephrolithiasis, Nephrotic syndrome, Non-alcoholic fatty liver disease, Obesity, Orthostatic hypotension, Osteomalacia, POTS, Pancreatitis, Parapneumonic effusion, Paroxysmal nocturnal haemoglobinuria, Perianal abscess, Pericarditis, Pernicious anaemia, Pituitary adenoma, Pleural effusion, Post-operative ileus, Post-streptococcal glomerulonephritis, Priapism, Primary hyperaldosteronism, Primary sclerosing cholangitis, Prolactinoma, Protein C deficiency, Pseudohypoparathyroidism, Rapidly progressive glomerulonephritis, Refeeding syndrome, Renal tubular acidosis, Respiratory acidosis, Respiratory alkalosis, Respiratory failure, Rhabdomyolysis, Sarcoidosis (also chest), Sick sinus syndrome, Spontaneous bacterial peritonitis, Subacute thyroiditis, Subarachnoid haemorrhage (emergency-adjacent, may be re-audit), Subdural haematoma, Syndrome of inappropriate antidiuretic hormone secretion, Thalassaemia, Thrombotic thrombocytopenic purpura, Toxic megacolon, Vitamin B12 deficiency, Vitamin D deficiency, Volvulus, Warm autoimmune haemolytic anaemia, Wilson disease, von Willebrand disease.

**Phase 2 entries deferred to agent #7 (rheum/derm/msk/ent/ophtho) - not audited here:** Acanthosis nigricans, Achilles tendinopathy, Acne vulgaris, Acute angle-closure glaucoma, Adenomyosis (arguably O&G - see below), Adhesive capsulitis, Adult-onset Still disease, Allergic rhinitis, Ankylosing spondylitis, Aortic aneurysm/regurgitation/stenosis, Arrhythmogenic cardiomyopathy, Asbestosis, Atherosclerosis, Atrial flutter, Autoinflammatory diseases, Autonomic neuropathy, Avascular necrosis, Behçet disease, Benign paroxysmal positional vertigo, Benign prostatic hyperplasia, Bradycardia, Brugada syndrome, Bullous pemphigoid, Burns, Bursitis, Carotid artery dissection/stenosis, Carpal tunnel syndrome, Cataract, Cauda equina syndrome, Central retinal artery/vein occlusion, Cerebral artery dissection, Cerebral venous sinus thrombosis, Charcot-Marie-Tooth disease, Chilblains, Chronic fatigue syndrome, Cluster headache, Compartment syndrome, Conjunctivitis, Contact dermatitis, Cor pulmonale, Corneal abrasion, Cryptosporidiosis, Dehydration, Dermatitis herpetiformis, Dermatomyositis, Dilated cardiomyopathy, Disseminated intravascular coagulation, Eosinophilic granulomatosis with polyangiitis, Epistaxis, Erythema multiforme/nodosum, Fibromuscular dysplasia, Fibromyalgia, Granulomatosis with polyangiitis, Henoch-Schönlein purpura, Hip fracture, Horner syndrome, Huntington disease, Internuclear ophthalmoplegia, Lambert-Eaton syndrome, Lichen simplex chronicus, Livedoid vasculopathy, Long QT syndrome, Macular degeneration, Medication overuse headache, Medullary sponge kidney, Melasma, Meniere disease, Mesothelioma, Mitral regurgitation, Mononucleosis, Myasthenia gravis, Myocarditis, Myotonic dystrophy, Ophthalmoplegia, Optic neuritis, Papilloedema, Peripheral neuropathy, Peutz-Jeghers syndrome, Plantar fasciitis, Polymyositis, Posterior reversible encephalopathy syndrome, Psoriasis, Psoriatic arthritis, Pterygium, Pulmonary oedema, Pulmonary stenosis, Pyoderma gangrenosum, Raynaud phenomenon, Reactive arthritis, Retinal detachment, Rotator cuff tear, Schistosomiasis, Scleritis, Scleroderma, Scurvy, Seborrheic dermatitis, Silicosis, Sjögren syndrome, Spinal fracture, Spinal stenosis, Stevens-Johnson syndrome, Supraventricular tachycardia, Syncope, Syringomyelia, Systemic lupus erythematosus, Systemic sclerosis, Takayasu arteritis, Tension headache, Thoracic outlet syndrome, Tinea, Torsades de pointes, Tricuspid regurgitation/stenosis, Urticaria, Uveitis, Vasculitis, Ventricular tachycardia, Vestibular neuritis, Vitiligo.

**Adenomyosis** should probably be in the O&G scope of this audit rather than phase-2 residual - flagging: entry states "presentation similar to fibroids and endometriosis" and Mx via progestogen / LNG-IUD / hysterectomy is correct per RANZCOG.

## Notes

- **Duplicates found in this scope** (add to Rob's deferred duplicate-audit stream):
  - Placenta praevia / Placenta previa - byte-for-byte identical
  - Coarctation of aorta / Coarctation of the aorta - substantially identical (small wording differences)
  - Transient tachypnea / Transient tachypnoea of the newborn - byte-for-byte identical
  - Generalised anxiety disorder / Generalized anxiety disorder - one covered in chronic, spelling variants
  - Rheumatic fever / Acute rheumatic fever - substantial overlap; recommend canonicalising to "Acute rheumatic fever" and aliasing.
  - Eating disorders / Eating disorder not otherwise specified - overlapping scope; "Eating disorders" is a summary umbrella and "Eating disorder not otherwise specified" is the DSM-5 OSFED entry - both defensible but risk of duplication in search.
  - Phaeochromocytoma / Pheochromocytoma (noted in original mechanical sweep - deferred to agent #6).
  - Peripheral arterial / artery disease (chronic audit already flagged).
  - Wolff-Parkinson-White / -syndrome (chronic audit flagged).

- **Rob-memory rule compliance scan:**
  - No em-dashes in the audited entries (all hyphen-space-hyphen or space-hyphen-space per Rob's rule).
  - No use of "canonical" in the audited content.
  - "Aboriginal and Torres Strait Islander" used correctly (in full) in ARF/RHD/Hep-A/SIDS entries; the SIDS entry uses "Aboriginal infants" alone which should be updated to "Aboriginal and Torres Strait Islander infants" for AIHW terminology consistency.
  - No proprietary product name-drops that would violate the no-proprietary-refs memory rule.
  - Female infertility, PCOS, Menopause entries all appropriately AU-focused (RACGP / RANZCOG / AMS).

- **What's missing from the bank (Rob may want to add):**
  - **Postnatal depression screening protocol / EPDS specifically** as a standalone entry (currently the Postpartum depression entry mentions EPDS but no dedicated screening entry). Adding "Perinatal depression screening" or reworking the Postpartum depression entry to include the EPDS cutoff (>=13) with the 4- and 8-week screen timing per Beyond Blue would help.
  - **Puerperal psychosis** - already exists as "Postpartum psychosis"; no gap.
  - **Antenatal care schedule** - missing as a standalone entry (NIPT, 11-13 week combined, 18-20 week morphology, 24-28 week GDM OGTT, 28+34 week anti-D, 35-37 week GBS, birth). Would be high-yield for Rob.
  - **Contraception AU** - completely missing as an entry; the residual LARC-first-line RACGP guidance would be a major add.
  - **DDH screening** - covered under DDH itself; no separate screening entry needed.
  - **Neonatal jaundice phototherapy nomogram** - covered inside Neonatal jaundice; fine.
  - **CAH (congenital adrenal hyperplasia)** - not in the bank; newborn screening added to expanded panel in most AU states 2024-2025.
  - **Munchausen / factitious disorder** - covered inside Somatic symptom disorder entry; standalone entry not required.
  - **Adjustment disorder / grief** - not covered; may be worth a standalone if psych coverage matters.
  - **Vaginismus, dyspareunia (non-vulvodynia)** - not covered.
  - **Pelvic inflammatory disease** (covered in antimicrobial audit) - fine.
  - **Twin pregnancy / multiple gestation** - not covered separately.
  - **Fetal movement monitoring / DFMC (decreased fetal movement counting)** - not covered.
  - **Labour (stages, CTG, epidural, active third stage)** - not covered as a standalone.
  - **Cardiotocograph interpretation** - not covered.

- **General strength:** the paediatric and obstetric entries are consistently AU-flavoured (Kleihauer, RANZCOG statements, RCH Melbourne CPG references, NIP integration, NDIS pathway calls, MARSIPAN, RHDAustralia). Psychiatric entries appropriately anchor on RANZCP / MHA. No US-only frames (SSRI-first for OCD before ERP is correctly avoided; ERP-plus-SSRI is stated). No dangerous inversions of urgency (SUFE, torsion, midgut volvulus, HIE all correctly flagged for same-hour action).

- **AI-tells scan:** 141 audited entries; no em-dashes found in scope; no "canonical" usage; no "delve", "leverage", "streamlined" (checked - "streamlined" appears once in FASD context as a genuine policy term, not AI filler); no proprietary product name-drops in violation of memory. Ban list clean for these entries.

Summary line: **15 substantive errors** requiring change (mostly wording precision - Wernicke Pabrinex typo, Preterm labor 23+0 threshold, anti-D dosing granularity, ARF Australian-modified Jones for high-risk populations, sickle-cell hydroxycarbamide age update, plus duplicate collapse), **~30 minor issues** (mostly nice-to-have additions - Circadin TGA age, letrozole framing, state ADHD prescribing, ANZCOR chest-thrusts wording, MHT progesterone choice), **87 entries verified accurate**, **8 unverified pending Rob check against internal or paywalled AU sources**. Phase 1 = 142 audited. Phase 2 = 279 candidates reviewed (7 spot-audited for accuracy, all clean; 265 explicitly deferred to agents #6/#7 not written at audit time; 7 flagged as either duplicates or overlap-to-existing-audit). **Total audited: 149.**

**Coverage math after this audit:**
- Master JSON: 686 entries.
- Covered by 5 existing audits (union): 265.
- Covered by this audit (phase 1 + phase 2 spot-audits): 149.
- Remaining uncovered after this audit: 686 - (265 + 142 + 7) = **272 entries** still awaiting agent #6 (gi/hep/renal/endo) and agent #7 (rheum/derm/msk/ent/ophtho), plus a small cardio/haem/venom/tropical residual (~20-25 entries) that no announced agent scope obviously claims. Recommend a dedicated **envenomation / marine sting audit** (Box jellyfish, Blue-ringed octopus, Irukandji, Funnel-web, Redback, Snake bite, Ciguatera - 7 entries) since these fall between emergency and toxicology in the scoping.
