# GI / Hepatology / Renal / Endocrinology audit - 2026-09-01

## Scope

Filtered `all_rich_summaries_2026-09-01.json` (686 entries) to 90 residual entries covering upper GI motility and mucosal disease, hepatology (viral, metabolic, autoimmune, vascular, inherited), renal (AKI, glomerular, tubular, hereditary, vascular, RTA), urology (non-oncology, non-infective), and endocrinology remnants (pituitary, thyroid/parathyroid, adrenal, sex chromosome, metabolic bone, micronutrient, immunodeficiency). Explicitly excluded: entries already covered in the emergency, antimicrobial, oncology-screening or chronic-first-line audits (UTI, pyelonephritis, cellulitis, DKA, HHS, hyperkalaemia, MI, Diabetes mellitus, Chronic kidney disease, Renal osteodystrophy, Rhabdomyolysis, Ulcerative colitis, Crohn disease, GORD, hyperthyroidism, hypothyroidism, Cholangitis, Cholecystitis, Cholelithiasis, Diverticulitis, Peptic ulcer disease, Prostatitis, Herpes zoster, Varicella, Bladder / renal / cholangio-cancer, Adrenal crisis, Carbon monoxide poisoning, Torsades, Congenital hypothyroidism, Hypercalcaemia, Gastroenteritis, Epididymitis, Choledocholithiasis).

Sources consulted:
- GESA (Gastroenterological Society of Australia) consensus statements including MASLD/MAFLD, Australian HCC surveillance CPG 2023-2025 (MJA 2025 summary of recommendations)
- Kidney Health Australia CARI 2024 CKD, KDIGO 2024 CKD (BP < 120 mmHg where tolerated)
- PBS (empagliflozin PSD May 2025, dapagliflozin September 2025 expansion)
- Australian Prescriber (MAFLD/MASLD 2024, terlipressin for HRS, urology reviews)
- ASHM chronic hepatitis B testing portal (tenofovir alafenamide status)
- Haemochromatosis Australia + Lifeblood High Ferritin Application
- Australian Living Guidelines (multiple)
- eTG public excerpts (appendicitis, biliary, renal colic, priapism)
- Endocrine Society (Cushing diagnostic algorithm) and Pituitary Society consensus
- ANZUP / USANZ commentary for BPH, urolithiasis, torsion
- RCH Melbourne CPGs (biliary atresia, malrotation, intussusception, enuresis, TOF)
- NICE / BAPEN 2024 refeeding guidance (referenced only where AU-silent)
- Where eTG chapter itself paywalled, secondary AU summary or peer-reviewed AU journal used and flagged

## Findings

### SUBSTANTIVE errors (change required)

- **Non-alcoholic fatty liver disease** - The name field and lead sentence should be flipped. Since June 2023, the multi-society (AASLD, EASL, ALEH) nomenclature is `Metabolic dysfunction-associated steatotic liver disease (MASLD)` with `MASH` replacing NASH, and a new hybrid category `MetALD` (MASLD with alcohol intake 140-350 g/week women, 210-420 g/week men). GESA's own Australian primary-care assessment position now uses MAFLD/MASLD terminology. The current summary lists `MASLD` only as an alias inside the definition sentence; the entry should lead with the current name and demote NAFLD to alias. `MetALD` is missing entirely and is a testable point in 2026 exam prep.
  Suggested rewrite of the opening clauses:
  `Metabolic dysfunction-associated steatotic liver disease (MASLD; renamed from NAFLD in the 2023 multi-society consensus) is hepatic steatosis on imaging or histology with at least one cardiometabolic risk factor and no significant alcohol intake; MetALD describes MASLD with weekly alcohol intake 140-350 g (women) or 210-420 g (men); commonest chronic liver disease in Australia; progresses through steatohepatitis (MASH) to fibrosis, cirrhosis and HCC.`
  Also add the AASLD/GESA cardiometabolic-criteria list (BMI, waist, glucose/HbA1c, BP, triglycerides, HDL) since diagnosis is now inclusion-criteria-based, not exclusion-based.
  Sources: [AASLD MASLD nomenclature](https://www.aasld.org/new-masld-nomenclature); [Australian Prescriber MAFLD/MASLD update](https://australianprescriber.tg.org.au/articles/metabolic-dysfunction-associated-fatty-liver-disease-an-update.html); [GESA consensus statement (Adams et al)](https://gesa.org.au/education/gesa-guidelines/)

- **Cirrhosis** - Two overlapping issues:
  1. `6-monthly HCC surveillance` - correct in principle but the entry should specify the current Australian CPG (George et al, MJA 2025) which is `6-monthly ultrasound in all people with compensated cirrhosis; the addition of AFP is optional and the guideline notes it is not incrementally cost-effective over ultrasound alone` - the current entry implies AFP is standard.
  2. `Refer for transplant if MELD at least 15` - MELD-Na is the current listing metric in AU/NZ transplant units (via TSANZ), and Australian threshold is `MELD-Na >=15 or complications of portal hypertension despite MELD <15`. Current wording is outdated by two point-scores.
  Suggested rewrite of those two sentences:
  `Score with Child-Pugh and MELD-Na (current AU/NZ liver transplant listing uses MELD-Na, adjusted for hyponatraemia). Refer for transplant assessment when MELD-Na is at least 15 or when portal-hypertension complications (recurrent variceal bleed, refractory ascites, recurrent HE, HRS or hepatopulmonary syndrome) develop despite lower scores. Australian HCC CPG 2023 (MJA 2025) recommends 6-monthly ultrasound; AFP is optional and not incrementally cost-effective over ultrasound alone.`
  Source: [Australian HCC surveillance CPG summary MJA 2025](https://onlinelibrary.wiley.com/doi/10.5694/mja2.70061)

- **Portal hypertension** - Same HCC/MELD-Na drift as above where the entry cross-references cirrhosis surveillance. Also, `ascitic tap with SAAG >=11 g/L confirming portal origin` is correct - keep. `Non-selective beta-blockade` should specifically name **carvedilol** as first-choice in current Baveno VII / EASL practice (adopted in AU tertiary hepatology) for patients without contraindications; propranolol is the fallback. Consider adding.
  Suggested tweak: `non-selective beta-blockade (carvedilol preferred over propranolol per Baveno VII, now standard AU tertiary practice) to lower the gradient.`
  Source: Baveno VII consensus (2022), adopted in AASLD 2024 and Australian tertiary hepatology.

- **Hepatorenal syndrome** - Two issues:
  1. `add terlipressin (or noradrenaline in ICU) targeting a rise in MAP of at least 10 mmHg` - correct in general, but terlipressin was approved and PBS-listed in Australia for HRS-AKI (as of 2023, per Australian Prescriber review); the entry should note it explicitly rather than framing it as a European practice. Noradrenaline remains a valid ICU alternative where terlipressin is unavailable.
  2. `withdraw diuretics and nephrotoxins; albumin 1 g/kg on day 1 then 20 to 40 g daily` - correct doses. Current international frame (adopted in AU tertiary) is `20-40 g/day IV albumin as vasoconstrictor adjunct` for the whole treatment period.
  Suggested rewrite:
  `Mx: withdraw diuretics and nephrotoxins; albumin 1 g/kg (max 100 g) on day 1 then 20-40 g/day; add terlipressin (TGA-approved and PBS-listed for HRS-AKI, use in monitored setting due to ischaemic and pulmonary oedema risk) titrated to a MAP rise of at least 10 mmHg, or noradrenaline in ICU where terlipressin is unavailable or contraindicated. Treat precipitant. Liver transplantation is the only definitive therapy.`
  Source: [Terlipressin for HRS - Australian Prescriber](https://australianprescriber.tg.org.au/articles/terlipressin-for-hepatorenal-syndrome.html)

- **Hepatitis B** - `Chronic active disease gets tenofovir alafenamide or entecavir` - order is misleading. ASHM / WHO 2024 first-line for adults remains **tenofovir disoproxil fumarate (TDF) or entecavir**; tenofovir alafenamide (TAF) is reserved for renal impairment, low BMD, or CKD. TAF is not the default in AU practice. Also the entry omits **peg-interferon alpha** as an option for HBeAg-positive young patients seeking finite-duration therapy.
  Suggested rewrite of the Mx clause:
  `Mx: acute is supportive. Chronic active disease first-line - tenofovir disoproxil (TDF) or entecavir (both PBS-listed, oral, high genetic barrier). Switch to tenofovir alafenamide (TAF) for CKD, osteoporosis, or age-related concerns. Peg-interferon alpha for 48 weeks is an option in young HBeAg-positive patients seeking finite therapy. Triggered by ALT, HBV DNA, fibrosis or extrahepatic disease.`
  Source: [ASHM chronic HBV testing portal](https://testingportal.ashm.org.au/treatment-of-chronic-hepatitis-b-virus-infection/); WHO 2024 chronic HBV guideline.

- **Diabetic nephropathy** - `SGLT2 inhibitor` is under-specified. September 2025 PBS expansion aligned dapagliflozin CKD indication with empagliflozin - both now available from eGFR 20 mL/min/1.73 m^2 in many populations (with UACR thresholds by band). The entry should also mention **finerenone (non-steroidal MRA)** which is PBS-listed for diabetic kidney disease with albuminuria despite maximally tolerated ACE-i/ARB + SGLT2i, and **GLP-1 agonist** (FLOW trial with semaglutide, 2024) which now has renal-outcome evidence in T2DM plus CKD.
  Suggested rewrite of Mx:
  `Tight glycaemic control (HbA1c around 53 mmol/mol, individualised); BP under 130/80 with ACE inhibitor or ARB titrated to highest tolerated dose; SGLT2 inhibitor (empagliflozin or dapagliflozin, both PBS-listed for CKD from eGFR 20 after September 2025 expansion, regardless of diabetes status); finerenone (non-steroidal MRA) for residual albuminuria on maximally tolerated RAS inhibitor + SGLT2i; GLP-1 agonist semaglutide reduces major kidney events (FLOW trial 2024) - now a further recommended add-on in T2DM plus CKD. Refer to nephrology at eGFR under 30 or with heavy proteinuria.`
  Sources: [PBS empagliflozin PSD May 2025](https://www.pbs.gov.au/industry/pbac/psd/2025/05/empagliflozin-psd-may-2025.pdf?variant=3); [PBS dapagliflozin September 2025 expansion](https://thelimbic.com/nephrology/pbs-expands-eligibility-for-dapagliflozin-for-ckd/); FLOW trial (NEJM 2024).

- **IgA nephropathy** - `Corticosteroids (or targeted-release budesonide) plus mycophenolate for progressive disease` - the current treatment landscape has moved past this simple framing:
  1. `Targeted-release budesonide` (Nefecon / budesonide MR): approved in EU (April 2024) and US (Sep 2024) for adults with proteinuria at risk of progression. Not yet PBS-listed in Australia; TGA status pending. Should be positioned as `not yet PBS-accessible in Australia; consider in tertiary centres via managed access`.
  2. `Sparsentan` (dual endothelin + angiotensin II antagonist) approved for IgAN 2024; also not PBS-listed in Australia.
  3. `SGLT2 inhibitor` is now first-line background therapy (with ACE-i/ARB) in progressive IgAN regardless of proteinuria threshold - EMPA-KIDNEY and DAPA-CKD both support.
  4. `Mycophenolate` addition is Asian-population-supported (MAIN) but the TESTING trial reset the risk-benefit for steroid escalation; wording should reflect uncertainty rather than confident add-on.
  Suggested rewrite of Mx clause:
  `Mx: BP under 130/80 with ACE inhibitor or ARB titrated to reduce proteinuria under 1 g/day; sodium restriction; SGLT2 inhibitor now standard background therapy adding renoprotection (EMPA-KIDNEY, DAPA-CKD). For persistent proteinuria over 1 g/day despite optimal RAS + SGLT2i - options include reduced-dose steroids per TESTING trial or targeted-release budesonide (Nefecon; TGA/PBS pending), with tertiary nephrology input; sparsentan is an emerging non-immunosuppressive option (not PBS-listed). Rapidly progressive disease gets pulse steroids and cyclophosphamide.`
  Sources: TESTING trial (Lv 2022); DAPA-CKD; EMPA-KIDNEY; [Nefecon TGA status via managed-access commentary](https://academic.oup.com/ckj/article/18/1/sfae394/7915992).

- **Appendicitis** - `laparoscopic appendicectomy with IV antibiotics (gentamicin plus metronidazole per eTG)`. Current eTG (2024) allows either **cephazolin + metronidazole** OR **gentamicin + metronidazole** as pre-operative prophylaxis; many AU surgeons use gentamicin + metronidazole + amoxicillin (triple therapy). More importantly, current eTG explicitly includes a **non-operative management (NOM) pathway with antibiotics alone** for uncomplicated appendicitis (no faecolith, no perforation, no phlegmon, well patient, no complicating factors), evidence from APPAC trial and Cochrane 2020. The entry says `Non-operative antibiotic-only management is an option for select uncomplicated cases` which is fine but should name it as `an eTG-endorsed pathway`, not just an option.
  Suggested tweak: `Mx: laparoscopic appendicectomy with pre-op cephazolin plus metronidazole (or gentamicin plus metronidazole) per eTG. Non-operative antibiotic-only management is now an eTG-recognised alternative for uncomplicated appendicitis in selected adults (no faecolith, no perforation, no phlegmon, well patient); recurrence 20-40% at 5 years, so counsel accordingly.`

- **Metabolic syndrome** - `Diagnosis (IDF, needs 3 of 5)` uses waist thresholds of `94 cm men, 80 cm women; ethnicity-specific for South Asian and East Asian`. This is IDF 2005 wording. Current usage in AU (RACGP RedBook, NHMRC) uses **`Harmonised 2009 criteria`** where waist thresholds are population-specific (ANZ default 94 cm men / 80 cm women, per IDF-Europid) but need 3 of 5 with no obligatory central obesity requirement. Also the entry should specifically flag `HbA1c >=6.5%` as an alternative to fasting glucose since HbA1c has been accepted for T2DM diagnosis in AU since 2012.
  Suggested tweak: `Diagnosis (Harmonised 2009, needs 3 of 5): central obesity (waist over 94 cm men, 80 cm women for Europid/ANZ; population-specific for South Asian, East Asian, sub-Saharan African); triglycerides over 1.7 mmol/L; HDL under 1.0 (men) or 1.3 (women) mmol/L; BP at least 130/85 or on antihypertensive; fasting glucose at least 5.6 mmol/L, HbA1c at least 6.5% or known T2DM.`

- **Obesity** - `GLP-1 agonists (liraglutide, semaglutide) and dual GIP-GLP-1 agonists (tirzepatide) are the effective pharmacotherapies; orlistat is second line`. As of 2025-2026 in Australia:
  - **Semaglutide (Wegovy)** is TGA-approved for weight management and launched in AU market (2024); supply constrained.
  - **Tirzepatide (Mounjaro/Zepbound)** is TGA-approved for obesity management (2024).
  - Neither is PBS-listed for weight management (both are private-script only) - the entry should explicitly state PBS status because Rob's audience will be counselling patients about cost.
  - Bariatric BMI thresholds are correct (>=40 or >=35 with complications), but current AU practice extends to **>=30 with poorly controlled T2DM** per ADS/ANZMOSS 2024.
  Suggested addition/rewrite:
  `GLP-1 agonists (liraglutide/Saxenda, semaglutide/Wegovy) and dual GIP-GLP-1 agonists (tirzepatide/Mounjaro) are the effective pharmacotherapies but none are PBS-listed for weight management as of 2026 (private script only); orlistat is second line. Bariatric surgery (sleeve gastrectomy, RYGB) for BMI at or above 40, or 35 with complications, or 30 with poorly-controlled T2DM (ANZMOSS 2024).`

### MINOR issues (nice-to-fix)

- **Achalasia** - `laparoscopic Heller myotomy plus partial fundoplication, or per-oral endoscopic myotomy (POEM)` - correct. Current AU tertiary practice increasingly places **POEM as first-line for type III (spastic) achalasia** and reserves Heller for types I and II; the summary should note this subtype-based choice, which is testable.

- **Barrett oesophagus** - `Seattle-protocol biopsies (four-quadrant every 2 cm plus visible lesion)` - correct. Australian surveillance intervals per GESA (`non-dysplastic 3-5 yearly`) are correct; consider adding the **length-adjusted intervals** (short-segment <3 cm every 5 years; long-segment >=3 cm every 3 years) which is the more granular current GESA/BSG-aligned approach.

- **Autoimmune hepatitis** - `induction with prednisolone 40-60 mg daily; add azathioprine 1-2 mg/kg (check TPMT) once bilirubin improving` - correct. Current international framing is `combination prednisolone 30 mg + azathioprine from the outset` in most non-cirrhotic patients since AASLD 2019; the `add later` approach is now second-preferred. Consider tweaking.

- **Alcoholic hepatitis** - `prednisolone 40 mg for severe disease without infection (Lille score at day 7 predicts response, stop if non-responder)` - `at day 7` is one option; the Day-4 Lille score is now the more commonly used early-stopping timepoint (Louvet 2015; 2024 Dig Dis Sci confirms utility). Consider `Lille score at day 4 or 7`.

- **Wilson disease** - `copper chelation with penicillamine or trientine` - correct but the current Australian tertiary and EASL 2024 practice increasingly favours **trientine as first-line for symptomatic disease** because of penicillamine's high AE burden (up to 30% discontinuation, neurological worsening on initiation in 10-20%). The entry positions them as equivalent; a soft steer to trientine would match current practice.

- **Haemochromatosis** - `therapeutic venesection weekly (450 to 500 mL) until ferritin under 50, then every 3 to 4 months targeting 50 to 100` - matches Haemochromatosis Australia / Lifeblood High Ferritin App. Consider adding that Lifeblood provides the venesection service free once the High Ferritin App approves eligibility - a very Australian-specific piece of pathway information.

- **Primary biliary cholangitis** - `ursodeoxycholic acid 13-15 mg/kg first line, improves survival; obeticholic acid or fibrates for inadequate response` - correct. Obeticholic acid was withdrawn from the US market (Aug 2024) after post-marketing hepatotoxicity signal in cirrhosis; TGA status in AU is retained but with amended warnings. Consider adding: `Obeticholic acid is contraindicated in decompensated cirrhosis (TGA-updated boxed warning 2024). Bezafibrate/fenofibrate off-label for pruritus and biochemical response.`

- **Primary sclerosing cholangitis** - `UDCA improves LFTs but not survival` - correct; current AASLD/EASL specifically **do not recommend UDCA at doses over 28 mg/kg/day** because of harm signal at high dose. Consider noting.

- **Cushing syndrome** - `overnight dexamethasone suppression` first-line is fine. Endocrine Society guideline offers three equivalent first-line tests (1 mg overnight DST, late-night salivary cortisol x2, 24-h UFC x2), and recommends **two positive tests** before confirming. The entry says `24-hour urinary free cortisol, late-night salivary cortisol, or overnight dexamethasone suppression` - implies pick-one; should be `pick two positive tests from these three screening tests` per Endocrine Society (2008 guideline, still current).

- **Prolactinoma** - `fasting serum prolactin (usually well over 250 microg/L in prolactinoma; macroprolactinoma may need dilution to exclude hook effect)` - correct. `Prolactin` reference unit in Australia: some AU labs report in mIU/L (multiply by ~21.2), not microg/L. Consider dual units: `over 250 microg/L (5,300 mIU/L)` to match RCPA reporting.

- **Acromegaly** - `Somatostatin analogues (octreotide LAR, lanreotide) for residual disease; cabergoline for mild disease; pegvisomant for resistance` - correct. Consider adding **pasireotide** as a third-line SRL for tumours resistant to first-generation SSA (approved 2014 international; TGA-approved in AU).

- **Phaeochromocytoma / Pheochromocytoma** - **These two entries are byte-for-byte identical duplicates** (same aliases, same summary). Should collapse to a single canonical `Phaeochromocytoma` entry with `Pheochromocytoma` / `pheo` as aliases (matches Rob's `coverage_check_via_canonical` memory rule).

- **Hyperparathyroidism** - Surgical thresholds `calcium over 2.85, eGFR under 60, urinary calcium over 10 mmol/day, T-score at or below -2.5, age under 50, or fracture` - matches the AACE/AAES/BAETS 4th International Workshop (2014) - still current. However, current NICE 2019 (referenced in AU practice) also includes `nephrocalcinosis/nephrolithiasis on imaging` and `symptomatic renal or bone disease` explicitly, and the age threshold is `under 50 years`. The current summary is essentially correct - consider adding nephrolithiasis on imaging as an indication.

- **Renal colic** - `IV NSAID first line, add opioid if needed` - correct and matches NHMRC / eTG. `stones under 5 mm usually pass spontaneously; medical expulsive therapy with tamsulosin for 5 to 10 mm stones` - correct. Recent evidence (SUSPEND trial and 2023 Cochrane) shows MET benefit is smaller than previously thought for stones under 5 mm but persists at 5-10 mm - the summary reflects this correctly.

- **Nephrolithiasis** - Duplicated with Renal colic essentially. Same content, different framing. Consider one canonical entry with alias.

- **Priapism** - `intracavernosal phenylephrine 200 microg every 5 min up to 1 mg` - correct AUA/EAU dosing. Current AU eTG (Urology) is consistent. Add: `intracavernosal phenylephrine 100-500 microg every 3-5 minutes; a diluted 100 microg/mL solution reduces overdose risk.` Currently unclear on dilution.

- **Testicular torsion** - `Salvage ~90% under 6 hours, near zero after 24` - correct for typical patient; more granular current data (2024 systematic review) is `97% at 0-6h, 79% at 7-12h, 61% at 13-18h, 42% at 19-24h` - the entry's summary is fine and pedagogically simpler.

- **BPH** - `Alpha-1 blocker (tamsulosin, prazosin) gives symptom relief within days. 5-alpha reductase inhibitor (finasteride, dutasteride) shrinks the prostate over 3 to 6 months in prostates over 30 mL. Combination for larger prostates.` - correct. Consider adding the fixed-dose combination **dutasteride/tamsulosin (Duodart)** which is PBS-authority-listed and preferred where combination is indicated (better adherence than two separate pills). Also, the **PSA rule**: 5-ARIs halve PSA over 6 months - double the measured value when tracking. This is a testable AU exam point that's missing.

- **Erectile dysfunction** - `PDE5 inhibitor (sildenafil, tadalafil) first-line`. Sildenafil is PBS-listed only via authority (ED after prostatectomy, spinal cord injury, MS, T1DM). Otherwise private script. Tadalafil private only for ED (PBS-listed for BPH instead). Should note PBS constraints as counselling info.

- **Refeeding syndrome** - `parenteral thiamine 200-300 mg daily for 3 days plus vitamin B complex before any calories; start 5-10 kcal/kg/day (high risk)` - matches NICE 2006 (still current). Australian dietetic practice per NEMO / Dietitians Australia is consistent. The `parenteral thiamine 200-300 mg` should specify - AU practice is `Pabrinex (thiamine-containing IV vitamin B/C) 1 pair TDS or thiamine 100 mg IV/oral TDS` since single-agent IV thiamine 300 mg is less commonly stocked in AU hospitals than in Europe. Consider tweaking to reference Pabrinex.

- **Enuresis** - `Desmopressin (short-term or for sleepovers) if the alarm fails or is not feasible` - correct. Note: RCH recommends **oral melt formulation over tablets** in children (2023 RCH CPG update) and **do not use intranasal in enuresis due to hyponatraemia risk** (TGA warning). Consider adding warning against intranasal.

- **Malrotation with midgut volvulus** - `upper GI contrast series is reference` - correct. Recent AU paediatric surgical practice (RCH 2024) upgrades **ultrasound with SMA/SMV orientation and whirlpool sign** to reference-standard equivalent in centres with experienced operators, avoiding the delay of a contrast study. Consider noting the parity.

- **Coeliac disease** - `HLA-DQ2 in about 90% and HLA-DQ8 in most of the rest, negative HLA effectively excludes` - correct. Consider adding the current AU paediatric ESPGHAN pathway: `In symptomatic children with tTG-IgA at least 10x ULN and positive EMA on a second sample, biopsy may be omitted (ESPGHAN 2020, adopted in AU tertiary paediatric practice)`. Testable.

- **Vitamin D deficiency** - `cholecalciferol - 1000 to 2000 IU daily for mild deficiency, high-dose loading (3000 to 5000 IU daily for 6 to 12 weeks)` - matches Osteoporosis Australia / Endocrine Society AU position. Consider naming the **PBS-authority-listed high-dose 50,000 IU monthly** as the practical AU pharmacy option (vs daily dosing) for adherence.

- **Vitamin B12 deficiency** - `intramuscular hydroxocobalamin, loading then maintenance` - matches AU practice. Add specifics: `loading = 1 mg IM alternate days for 2 weeks (or three-times-weekly for 6 weeks if neurological features), then maintenance 1 mg IM every 3 months`. Current summary is under-specified for AU exam purposes.

- **Turner syndrome** - `oestrogen from age 11 to 12 for pubertal induction` - correct. Current AU/international practice (TISUPS, ESPE 2017) has shifted to **starting oestrogen from ~11 years using transdermal 17-beta-oestradiol** at low starting dose (rather than oral ethinyl oestradiol); the entry says `oestrogen` generically which is fine but transdermal-first is worth naming.

- **Klinefelter syndrome** - `testosterone replacement from puberty` - correct in principle. Timing is controversial; many centres delay to fertility-preservation completion (microTESE before HRT) because exogenous testosterone can worsen intratesticular sperm harvest. Consider adding: `Discuss fertility preservation (microTESE) before initiating testosterone, as replacement suppresses spermatogenesis.`

- **Rickets** - Correct on nutritional rickets. Consider adding **calcipenic vs phosphopenic subtype distinction** more explicitly (already implied by `X-linked hypophosphataemic and vitamin D-dependent forms`) - phosphate wasting rickets (XLH) is treated with burosumab (TGA/PBS-listed via LSDP for XLH), not phosphate/calcitriol alone anymore.

- **Osteomalacia** - Similar comment as Rickets. `Phosphate and calcitriol where the defect is renal phosphate wasting` - burosumab is now first-line for TIO and XLH in adults where the biochemistry is phosphate wasting (approved TGA 2020, PBS via LSDP).

- **Hepatitis A** - `Post-exposure - vaccine within 2 weeks` - correct per AIH (Australian Immunisation Handbook). Also permits **NHIG (normal human immunoglobulin) in patients >=60 or immunocompromised or with chronic liver disease** who cannot mount vaccine response - worth adding.

- **Hepatitis C** - `direct-acting antiviral therapy for 8 to 12 weeks achieves SVR in over 95% - sofosbuvir with velpatasvir, or glecaprevir with pibrentasvir, are pan-genotypic and PBS-listed. Any GP can prescribe.` - correct. Consider adding: `Since March 2016, HCV DAAs are PBS s85 (unrestricted) with no fibrosis threshold - all viraemic patients eligible. Retreatment options exist for DAA failure via specialist S100 referral. Elimination target 2030 (WHO).`

- **Perianal abscess** - `Antibiotics only if cellulitis, systemic features, immunocompromise or valvular disease` - correct. Add: `In Crohn-associated perianal abscess, imaging (MRI pelvis) before drainage is critical because complex fistulising disease changes surgical approach; refer to colorectal +/- gastroenterology same day.`

- **Haemorrhoids** - `Investigate the colon in anyone over 45` - current AU NBCSP starts at 45 (from 2024), so this is aligned. Consider explicit link: `NBCSP invitations now start age 45 in Australia; investigate rectal bleeding with lower endoscopy in anyone at or above screening age or with red flags.`

- **Meckel diverticulum** - `Meckel scan first` for painless massive lower-GI bleed in child <5 - correct. Consider adding: **pretreat with H2 blocker or PPI 24-48h prior** to enhance uptake by ectopic gastric mucosa (RCH nuclear medicine protocol).

- **Ischaemic colitis** - `broad-spectrum antibiotics for moderate to severe disease` - correct. Note: current AU eTG allows **withholding antibiotics in mild non-necrotising disease** (small European trials). Consider softening.

- **Mesenteric ischaemia** - `mortality 50-80%` - accurate. Consider adding **`serum lactate has poor sensitivity early`** more prominently since the entry currently buries this ("late").

- **Bowel obstruction** - `Water-soluble contrast is both prognostic and mildly therapeutic` - correct (Gastrografin challenge). Consider naming Gastrografin explicitly and noting the AU practice of 100 mL PO/NG with plain film at 6 and 24h - a testable operational point.

- **Post-operative ileus** - `Alvimopan shortens duration after bowel resection` - alvimopan is **not TGA-registered/available in Australia**. Should be flagged: `Alvimopan (US-approved) is not available in Australia; ERAS bundles and multimodal opioid-sparing analgesia are the AU mainstay for prevention.`

- **Volvulus** - `sigmoid without peritonitis gets flexible sigmoidoscopy detorsion with rectal tube` - correct. Consider naming success rate (>80%) and recurrence (40-60% without surgery) to motivate elective sigmoidectomy after first successful decompression - the entry has the recurrence data but frames it as `over 40%`; more accurate is `40-60%`.

- **Hiatal hernia** - `Nissen fundoplication if refractory` - correct. Recent AU tertiary practice (2024) also considers **magnetic sphincter augmentation (LINX)** and **transoral incisionless fundoplication (TIF)** for select refractory GORD with sliding hiatus - optional add. Consider also the increasing use of `magnetic sphincter augmentation` in AU tertiary centres.

- **Inguinal hernia** - `elective laparoscopic (TEP/TAPP) or open Lichtenstein repair with mesh` - correct. Consider adding: **watchful waiting is safe in asymptomatic inguinal hernia in men** (INCA/Fitzgibbons trial extended follow-up 2018-2019); rate of crossover to surgery due to pain is 68% at 10 years, so many still end up operated. Current summary implies WW is only for `older comorbid patients` - not accurate; it's an option for any asymptomatic hernia.

- **Irritable bowel syndrome** - `low-FODMAP under an accredited dietitian` - correct, and matches Monash/RACGP guidance (Monash is the AU-invented pathway). Consider adding: `Low-FODMAP is a three-phase protocol (elimination, reintroduction, personalisation) - long-term strict elimination is not recommended.`

- **Renal artery stenosis** - `CORAL and ASTRAL show no added benefit from stenting except for flash pulmonary oedema, rapidly declining function despite therapy, or resistant hypertension` - correct. Consider adding: `Fibromuscular dysplasia in young women with resistant HT - percutaneous transluminal angioplasty (without stent) is first-line and can be curative.`

- **Nephritic syndrome / Nephrotic syndrome / Glomerulonephritis / RPGN** - These four umbrella entries overlap significantly. Content is accurate. Consider audit-time consolidation or explicit cross-referencing to the specific-pathology entries (MCD, FSGS, membranous, IgA, PSGN, ANCA, anti-GBM, lupus nephritis) which are already present. Currently reads as slight duplication.

- **Membranous nephropathy** - `rituximab first-line (MENTOR), then cyclophosphamide plus steroid (Ponticelli)` - correct. Consider explicit: `Rituximab is PBS-listed via authority for primary MN with anti-PLA2R and nephrotic-range proteinuria` (2023 PBS listing).

- **Minimal change disease** - `prednisolone 60 mg/m2 daily for 4 to 6 weeks then taper` - matches KDIGO 2021 / RCH paediatric nephrology. Consider adding: `Maximum 60 mg/day; oral, single morning dose; taper over 4-6 months to reduce relapse`.

- **Lupus nephritis** - `induction with high-dose corticosteroids plus mycophenolate or cyclophosphamide; belimumab or voclosporin as add-on` - correct. Add: `Voclosporin (Lupkynis) is TGA-approved (2022) for LN class III/IV/V but PBS listing pending as of 2026; belimumab is PBS-listed for SLE with high-disease-activity or renal indication.`

- **Interstitial nephritis** - `Oral prednisolone if creatinine continues to rise 5 to 7 days after drug withdrawal` - matches KDIGO. Fine.

- **Renal tubular acidosis** - `type 4 - hypoaldosteronism, hyperkalaemia, urine pH under 5.5 (diabetic nephropathy, ACE-i, spironolactone, trimethoprim)` - correct.

- **Renal osteodystrophy** - already audited (chronic first-lines audit).

- **Hyperparathyroidism** - Note that **familial hypocalciuric hypercalcaemia (FHH)** is mentioned in exclusion (`24-hour urinary calcium to exclude familial hypocalciuric hypercalcaemia`) but doesn't have its own entry - consider adding one as it's a testable "do not operate" trap.

- **Subacute thyroiditis** - `radioiodine uptake` - AU nuclear medicine primarily uses `Tc-99m pertechnetate uptake` (radioiodine less commonly done for thyroiditis workup). The entry mentions both `radioiodine or Tc-99m uptake` - correct, but AU practice defaults to Tc-99m.

- **Hashimoto thyroiditis** - `iron, calcium and PPIs impair thyroxine absorption - separate dosing by 4 hours` - correct. Consider adding: `Coeliac disease association (up to 5%) - screen with tTG-IgA at any Hashimoto diagnosis given autoimmune clustering.`

- **Refeeding syndrome** - `Wernicke encephalopathy` risk correctly flagged. Consider adding **Marchiafava-Bignami disease** as a related consequence of thiamine + alcohol combo, though this is trainee-level esoteric.

- **Post-streptococcal glomerulonephritis** - `Penicillin for residual carriage` - correct AU practice. Consider adding: `In endemic Aboriginal and Torres Strait Islander community settings, secondary prevention with community-wide skin/strep programs (RHDAustralia) reduces PSGN and ARF/RHD burden` - AU-specific practice point.

- **Alport syndrome** - `ACE inhibitor or ARB from diagnosis (even in children)` - correct per KDIGO 2024 (grade 1B for boys with X-linked from diagnosis). Consider mentioning SGLT2i (adjunct data emerging).

- **Polycystic kidney disease** - `tolvaptan slows progression in rapidly progressive disease (PBS listed)` - correct. Add: `PBS authority requires meeting Mayo Clinic imaging class 1C-1E or genetic evidence of PKD1 truncating variant plus eGFR trajectory criteria; hepatotoxicity monitoring monthly x 18 then quarterly.`

- **Hypertensive nephropathy** - `BP target under 130/80 (KDIGO)` - current KDIGO 2024 target is **under 120 systolic when tolerated (using standardised office measurement)** for CKD. Consider updating to `KDIGO 2024 target SBP <120 mmHg when tolerated using standardised office BP; RACGP retains <140/90 or <130/80 (albuminuria) for primary care with less-standardised measurement`.

- **Cardio-renal syndrome** - `SGLT2i (safe to eGFR 20)` - correct. Consider adding **`acetazolamide (ADVOR trial 2022)`** which is already there, and **`dapagliflozin + acetazolamide combination`** for diuretic-resistant HF congestion (ADVOR + EMPULSE combined signals).

- **Chronic granulomatous disease** - `dihydrorhodamine (DHR) flow cytometry replaces the nitroblue tetrazolium (NBT) test` - correct. Consider adding: `Trimethoprim-sulfamethoxazole + itraconazole prophylaxis + interferon-gamma S/C 3x/week (AU access via specialist immunology + LSDP application for IFN-gamma).`

- **Acute intermittent porphyria** - `Givosiran prevents recurrence` - givosiran is TGA-approved and PBS-listed via LSDP for recurrent attacks (>=2/year); should note. Also, `porphyriadrugs.com` link - the more commonly used AU resource is `www.drugs-porphyria.org` (Norwegian) or the AMH porphyria appendix. Consider updating.

- **Budd-Chiari syndrome** - `catheter-directed thrombolysis for acute disease; TIPS for refractory ascites or progressive liver failure` - correct. Consider adding: `Doppler-negative Budd-Chiari (i.e. hepatic veins patent but sinusoidal congestion) - consider sinusoidal obstruction syndrome (post-HSCT, pyrrolizidine alkaloids) as differential.`

- **Gilbert syndrome** - `reduced clearance of irinotecan, atazanavir, indinavir` - correct. Add: **paracetamol** is often mistakenly said to be more toxic in Gilbert - it is not, at therapeutic doses (well-established, sometimes still repeated as a myth).

- **Acute liver failure** - `paracetamol level (all comers)` - correct. Consider adding: `Australian POC pathway - staggered/repeated supratherapeutic ingestion is now the commonest presentation to AU EDs (per MJA 2020 guideline); treat as high-risk even without a discrete overdose event.`

- **Acute kidney injury** - `Dialysis for AEIOU` - correct mnemonic. Current AU/international practice (STARRT-AKI trial 2020) supports **watchful waiting rather than early dialysis** for uncomplicated AKI without AEIOU criteria - the entry doesn't misstate this but could add `no benefit from early elective dialysis in absence of AEIOU indications (STARRT-AKI 2020).`

- **Ascending cholangitis / Cholangitis** - antimicrobial audit territory - skipped as noted.

- **Pituitary adenoma** - `apoplexy - sudden headache, ophthalmoplegia and visual loss - is an emergency` - correct. Should add: `hydrocortisone stress-dose (100 mg IV) before any imaging/surgery for suspected apoplexy - hypocortisolism drives haemodynamic collapse.` Testable and safety-critical.

- **Primary hyperaldosteronism** - `MRAs off 4 to 6 weeks; ACE inhibitors, ARBs, beta blockers, diuretics off 2 weeks; verapamil OK` - correct per Endocrine Society 2016. Doxazosin is also OK - consider naming as the go-to substitute during ARR workup.

- **Cholelithiasis / Cholecystitis / Choledocholithiasis** - biliary; skipped as noted (antimicrobial audit).

- **Biliary atresia** - `Kasai hepatoportoenterostomy as early as possible - best under 60 days, worse after 90` - correct. Add: `Any infant with jaundice beyond 14 days needs a split (conjugated + total) bilirubin - not just a total. Conjugated fraction >17 micromol/L or >20% is pathological.` This is already in the entry but worth emphasising as it's the most testable/preventable-harm point.

- **Tracheo-oesophageal fistula** - `Type C proximal atresia with distal fistula (85%)` - correct. Add: `VACTERL screening - vertebral X-ray, echo, renal US, spinal US in the newborn period before elective repair (RCH neonatal surgery pathway).`

- **Rickets / Osteomalacia** - see burosumab notes above.

- **Genitourinary syndrome of menopause** - `low-dose vaginal oestrogen is first-line pharmacotherapy (Ovestin cream, Vagifem pessaries, oestriol ring), highly effective with negligible systemic absorption and acceptable after breast cancer in consultation with oncology` - matches AMS (Australasian Menopause Society) 2024 position. Consider adding: `Ospemifene not TGA-listed in Australia; prasterone (Intrarosa) TGA-approved 2020, private script only.`

- **Urinary incontinence** - `Topical oestrogen for genitourinary syndrome of menopause` - correct. Consider adding: `Sacral neuromodulation and posterior tibial nerve stimulation are third-line for refractory urgency incontinence (public-listed in tertiary AU urology, waiting-list barriers).`

### VERIFIED accurate (no action)

Achalasia (aside from POEM subtype note above), Anal fissure, Autoimmune hepatitis (aside from combination-induction note), Barrett oesophagus (aside from length-adjusted intervals note), Cirrhosis (aside from MELD-Na and HCC-CPG update), Coeliac disease (aside from paediatric no-biopsy pathway note), Diverticular disease, Enuresis (aside from intranasal warning), Erectile dysfunction (aside from PBS note), Folate deficiency, Genitourinary syndrome of menopause (aside from prasterone note), Gilbert syndrome, Glomerulonephritis, Haemorrhoids (aside from NBCSP-45 note), Hashimoto thyroiditis (aside from coeliac screening note), Hepatic encephalopathy, Hepatitis A (aside from NHIG note), Hepatitis C (aside from s85 note), Hiatal hernia, Hyperparathyroidism, Hypoparathyroidism, Inguinal hernia (aside from WW-in-asymptomatic note), Interstitial nephritis, Intussusception, Irritable bowel syndrome (aside from 3-phase note), Ischaemic colitis, Klinefelter syndrome (aside from fertility-first note), Lupus nephritis (aside from voclosporin note), Malrotation with midgut volvulus (aside from US-parity note), Meckel diverticulum (aside from PPI-pretreatment note), Membranous nephropathy (aside from PBS rituximab note), Mesenteric ischaemia, Minimal change disease, Nephritic syndrome, Nephrolithiasis, Nephrotic syndrome, Oesophageal varices, Perianal abscess, Post-streptococcal glomerulonephritis, Priapism, Primary hyperaldosteronism, Primary sclerosing cholangitis (aside from high-dose UDCA note), Pseudohypoparathyroidism, Rapidly progressive glomerulonephritis, Renal artery stenosis, Renal colic, Renal tubular acidosis, Rickets (aside from burosumab note), Subacute thyroiditis (aside from Tc-99m note), Testicular torsion, Tracheo-oesophageal fistula (aside from VACTERL note), Turner syndrome (aside from transdermal note), Urinary incontinence, Volvulus - accurate to public AU sources at the granularity checked.

### UNVERIFIED (no definitive public AU source found)

- **Alport syndrome** - `post-transplant anti-GBM disease in around 3% of male X-linked recipients` - widely quoted (3-5%) but couldn't nail the AU nephrology transplant registry figure. Global literature supports it.
- **Turner syndrome** - `aortic root over 25 mm/m^2` as pregnancy contraindication threshold - matches international (Roos-Hesselink 2013, ESC 2018) but the specific AU obstetric-cardiology position statement wasn't located publicly.
- **Klinefelter syndrome** - `microTESE with ICSI can achieve biological fatherhood` - correct in principle; AU-specific success rates (~50% sperm retrieval, ~30% live birth per cycle) not sourced from an AU IVF registry paper.
- **CGD** - AU LSDP status for interferon-gamma requires specialist immunology confirmation; couldn't locate the current LSDP schedule entry publicly.
- **Refeeding syndrome** - `parenteral thiamine 200-300 mg` - matches NICE 2006. AU tertiary practice varies (some use Pabrinex, some IV thiamine 100 mg TDS, some 300 mg once daily). No single AU standard I could source publicly.

## Notes

- **Duplicate: Phaeochromocytoma / Pheochromocytoma** are byte-for-byte identical. Collapse to `Phaeochromocytoma` (AU spelling) with `Pheochromocytoma`, `pheo`, `PPGL` as aliases.
- **Near-duplicate: Nephrolithiasis / Renal colic** - substantial overlap; consider one entry with the other as alias, or keep two and cross-reference.
- **Near-duplicate: Nephritic syndrome / Nephrotic syndrome / Glomerulonephritis** - all three overlap. Content is accurate individually but the umbrella framing would benefit from clearer subordination to specific-pathology entries.
- **Missing but worth adding** (deferred to Rob):
  - **Familial hypocalciuric hypercalcaemia (FHH)** - the `do not operate` mimic of primary hyperPTH; testable.
  - **X-linked hypophosphataemic rickets (XLH)** - burosumab-eligible cohort.
  - **Sinusoidal obstruction syndrome / veno-occlusive disease** - post-HSCT; differential to Budd-Chiari.
  - **HELLP syndrome standalone** (present under pre-eclampsia in emergency audit; consider a hepatology cross-reference).
  - **Anti-GBM disease standalone** (present within RPGN and Alport entries; consider separate).
  - **Gastric outlet obstruction / gastroparesis** - missing distinct entries.
  - **Diabetes insipidus (central and nephrogenic)** - endocrine gap.
- **Australian idioms handled correctly across the reviewed entries**: KHA-CARI referenced or aligned in CKD-adjacent entries; RCH CPG referenced for paediatric entries; PBS-Authority mentioned where relevant (tolvaptan, DAAs); AU-specific epidemiology called out for PSGN in Aboriginal and Torres Strait Islander communities. Aboriginal and Torres Strait Islander phrasing used correctly in diabetic nephropathy and PSGN entries (matches Rob's ban on ATSI abbreviation).
- **AI-tells scan (75-item catalogue)**: no em-dashes detected in the 90 entries reviewed (all hyphenated per Rob's memory rule). No use of `canonical`. No proprietary-product name-drops. No `unlock` / `leverage` / `robust` / `journey` fluff. No `In conclusion` / meta-commentary. Language is clinically dense and AU-idiomatic.
- **General strength**: hepatology and endocrinology entries are unusually strong on Australian PBS pathway detail (venesection app, LSDP references implicit, s85 vs S100 for DAAs). Renal entries track CARI/KDIGO carefully. GI entries are current on non-antibiotic diverticulitis management and adherent to eTG 2024 for appendicitis prophylaxis.
- **Highest-drift categories to prioritise for a v2 rewrite**:
  1. **Hepatology nomenclature and drug landscape** (MASLD/MASH renaming, terlipressin PBS listing, obeticholic acid warning, DAA universal access).
  2. **CKD/nephrology pharmacology** (SGLT2i PBS expansion, finerenone, semaglutide FLOW, novel IgAN therapies).
  3. **Endocrine biologics/orphan drugs** (burosumab for XLH/TIO, voclosporin for LN, pasireotide for acromegaly, givosiran for AIP).

Summary line: 8 substantive errors requiring rewrite (MASLD renaming, Cirrhosis MELD-Na/HCC-CPG, Portal HTN carvedilol, HRS terlipressin/AU, HepB TDF/entecavir order, Diabetic nephropathy SGLT2i/finerenone/GLP-1, IgAN sparsentan/budesonide, Appendicitis eTG NOM pathway, Metabolic syndrome harmonised-2009, Obesity PBS status). ~50 minor issues (mostly AU-specific PBS/practice granularity). 5 unverified pending AU-specific source confirmation. Full 90-entry set reviewed 2026-09-01.
