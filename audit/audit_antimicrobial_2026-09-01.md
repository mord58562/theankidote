# Antimicrobial choices audit - 2026-09-01

## Scope
Audited 84 rich-summary entries from `all_rich_summaries_2026-09-01.json` that carry a first-line antimicrobial recommendation for a specific infection. Coverage across UTI, pneumonia (CAP/HAP/aspiration/PCP), meningitis/encephalitis, endocarditis, osteomyelitis/septic arthritis/spinal epidural, cellulitis/erysipelas/necrotising fasciitis/impetigo, ENT (OM/OE/sinusitis/epiglottitis/retropharyngeal/quinsy/tracheitis), cavernous sinus, brain abscess, STI (gonorrhoea/chlamydia/PID), HIV, hepatitis B/C, PUD (H. pylori), C. difficile, TB, malaria, sepsis/septic shock/febrile neutropenia, neonatal sepsis, chorioamnionitis, puerperal sepsis, endometritis, tetanus, rabies, varicella/zoster/Ramsay Hunt, aspergillus/candida/crypto/PCP/histo, cholangitis/diverticulitis/peritonitis/appendicitis, gastroenteritis/typhoid, mastitis/epididymitis, pertussis/pharyngitis/diphtheria, empyema/lung abscess/legionella, Q fever/brucella/leptospirosis/melioidosis, Lyme/toxoplasmosis, acne/rosacea, TSS, GBS, ARF/RHD, influenza, scabies, bronchiectasis.

Sources consulted: STI Guidelines Australia (sti.guidelines.org.au); Australian Pharmacist coverage of the 2024 eTG Antibiotic overhaul; Australian Immunisation Handbook (rabies); RCH Melbourne CPG (pertussis, meningococcal); ASID 2025 CDI guidelines (Longhitano et al, IMJ 2025); Queensland Health adult sepsis antimicrobial prescribing guideline; RHDAustralia via AIHW ARF/RHD reports; ACSQHC eTG antibiotic primary-care summary; Melbourne Sexual Health Centre. Where eTG Antibiotic v17 itself is paywalled, secondary AU coverage of the specific chapter was used and flagged.

## Findings

### SUBSTANTIVE errors (change required)

- **Urinary tract infection** - Entry says "uncomplicated cystitis in Australia gets trimethoprim 300 mg at night for 3 days, or nitrofurantoin 100 mg twice daily for 5 days (eTG)". The 2024 eTG Antibiotic overhaul reversed this order: nitrofurantoin is now first-line and trimethoprim demoted to third-line behind fosfomycin because of E. coli resistance. Nitrofurantoin dosing is also 100 mg 6-hourly (QID), not BD.
  Suggested rewrite of that clause:
  `Mx: uncomplicated cystitis in Australia gets nitrofurantoin 100 mg orally 6-hourly for 5 days first-line (2024 eTG); alternatives are fosfomycin 3 g oral single dose or trimethoprim 300 mg at night for 3 days where local resistance allows.`
  Sources: https://www.australianpharmacist.com.au/therapeutic-guidelines-overhaul-uti-treatment/ ; https://australianprescriber.tg.org.au/articles/assessment-and-management-of-lower-urinary-tract-infection-in-adults.html

- **Pneumonia** - Entry lists severe CAP as "ceftriaxone with azithromycin". The November 2024 eTG Antibiotic update moved severe CAP off co-amoxiclav+doxycycline and standardised on **benzylpenicillin 1.2 g IV 6-hourly plus doxycycline 100 mg BD** (or benzylpenicillin plus azithromycin) for most inpatients, with ceftriaxone reserved for penicillin hypersensitivity or specific gram-negative concerns.
  Suggested rewrite of the Mx clause:
  `Mx: per eTG (2024) - amoxicillin for mild disease, adding doxycycline for atypical cover; IV benzylpenicillin plus doxycycline for moderate to severe (ceftriaxone plus azithromycin if penicillin hypersensitivity or gram-negative risk). Review at 48 hours.`
  Source: https://www.mygpnotes.com/infections-2/antibiotic-prescribing-in-primary-care-etg-summary-table-2024/ (summarising the November 2024 eTG change).

- **Clostridioides difficile** - Entry says "oral vancomycin 125 mg QID for 10 days first-line per eTG (metronidazole no longer first-line in adults) or fidaxomicin 200 mg BD (lower recurrence, PBS-restricted)". The 2025 ASID update (Longhitano et al, IMJ) now positions **fidaxomicin 200 mg BD for 10 days as preferred first-line for initial CDI in adults where available, with oral vancomycin 125 mg QID for 10 days as acceptable alternative**. Metronidazole retained only for fulminant disease as IV adjunct. The current framing understates fidaxomicin.
  Suggested rewrite of the Mx clause:
  `Mx: stop offending antibiotic; contact precautions with soap-and-water hand hygiene (alcohol rub ineffective on spores); fidaxomicin 200 mg orally BD for 10 days is preferred first-line per updated ASID 2025 guidelines where PBS-accessible, with oral vancomycin 125 mg QID for 10 days as acceptable alternative; metronidazole is no longer first-line and is reserved for IV adjunct in fulminant disease; fulminant - IV metronidazole + oral/PR vancomycin, surgical review at 48 h; recurrent - fidaxomicin, tapered vancomycin or FMT.`
  Source: https://onlinelibrary.wiley.com/doi/10.1111/imj.16638

- **Meningitis** - Entry says "empiric ceftriaxone 2g IV plus dexamethasone 10mg IV before or with the first antibiotic dose". Dexamethasone is not a single dose - it is **10 mg IV 6-hourly for 4 days** (start with or before first antibiotic) and stop early if not pneumococcal. Single dose framing risks under-treatment.
  Suggested rewrite:
  `Mx: give empiric ceftriaxone 2 g IV 12-hourly plus dexamethasone 10 mg IV 6-hourly for 4 days (started with or before the first antibiotic dose, stopped early if organism is not S. pneumoniae); add benzylpenicillin or amoxicillin if Listeria risk (age under 3 months, over 50, pregnant, immunocompromised); add vancomycin if resistant pneumococcus is plausible.`
  Source: https://www.health.qld.gov.au/__data/assets/pdf_file/0030/1446627/adult-sepsis-antimicrobial-prescribing-guideline.pdf

- **Peptic ulcer disease** - Entry says "Australian first-line eradication is triple therapy - esomeprazole 20 mg bd plus amoxicillin 1 g bd plus clarithromycin 500 mg bd for 7 days". eTG has moved to a **14-day course** (aligned with Maastricht VI / ACG 2024) and reserves clarithromycin-based triple therapy for regions/patients without clarithromycin resistance; bismuth-based quadruple is increasingly preferred where available. At minimum, duration must be updated.
  Suggested rewrite of the Mx clause:
  `Mx: Australian first-line eradication is 14 days of triple therapy - esomeprazole 20 mg BD plus amoxicillin 1 g BD plus clarithromycin 500 mg BD; substitute metronidazole 400 mg BD for amoxicillin in penicillin allergy; bismuth-based quadruple therapy (PPI plus bismuth plus tetracycline plus metronidazole) is preferred where clarithromycin resistance is likely or after failed triple therapy; PPI continued 4-8 weeks; confirm eradication with breath test 4 weeks after treatment. Stop NSAIDs.`
  Source: https://www.gastroenterologyandhepatology.net/archives/february-2026/practice-tips-from-the-updated-helicobacter-pylori-treatment-guidelines/ ; https://www.pharmacy.umn.edu/2024-american-college-gastroenterology-h-pylori-guidelines (US pattern; AU eTG has aligned duration).

- **Empyema** - Entry says "amoxicillin plus clavulanate, or ceftriaxone plus metronidazole; add vancomycin if MRSA risk, narrowed by culture, for 4 to 6 weeks". Duration is on the long side of current AU practice; empyema is typically 2-4 weeks IV/oral guided by response, source-control and CT resolution. More important: framing "for 4 to 6 weeks" as an eTG duration may mislead.
  Suggested rewrite of the duration clause:
  `...narrowed by culture; typical total duration 2-6 weeks guided by drainage adequacy, clinical response and repeat imaging (per eTG).`
  Source: Australian Prescriber "Pleural infection in adults" (open); Thoracic Society of Australia and NZ position on empyema. (No specific URL captured - flag as "verify against current eTG Respiratory chapter".)

### MINOR issues

- **Pyelonephritis** - "outpatient for mild - amoxicillin plus clavulanate 875/125 mg BD for 10 to 14 days". eTG allows 10-14 days but 2024 update leans to 10 days for uncomplicated outpatient response; the 14-day upper bound is fine but no longer default. Consider tightening to "10 days (up to 14 for slow response)". Also the entry does not mention **cefalexin high-dose (1 g every 8 h) is now an alternative** in the 2024 eTG update.

- **Chlamydia** - "test of cure at 3 months in women under 25 or in pregnancy". Language: STI Guidelines Australia recommends a test of **reinfection** at 3 months (not test of cure), because doxycycline TOC is not needed after treatment completion. Test of cure at 4 weeks is reserved for rectal chlamydia and pregnancy.
  Source: https://sti.guidelines.org.au/sexually-transmissible-infections/chlamydia/

- **Gonorrhoea** - Correct on ceftriaxone 500 mg IM + azithromycin 1 g PO. Missing: **pharyngeal infection needs azithromycin 2 g PO (not 1 g)** - this is a testable point and the entry mentions pharyngeal specifically as a caveat but does not upgrade the azithro dose. Add a line.
  Source: https://sti.guidelines.org.au/sexually-transmissible-infections/gonorrhoea/

- **Rabies** - "vaccine days 0, 3, 7 and 14 (5 doses to day 28 if immunosuppressed)". Correct per Australian Immunisation Handbook. Minor: text says "5 doses" but the immunocompetent regimen is 4 doses; the immunocompromised regimen is 5 doses (0/3/7/14/28). Clarify this is 4 vs 5 doses depending on immune status, and mention serology at 2-4 weeks after last dose for immunocompromised.
  Source: https://immunisationhandbook.health.gov.au/contents/vaccine-preventable-diseases/rabies-and-other-lyssaviruses

- **Pertussis** - "azithromycin (or clarithromycin) for 5 days is first line". Correct in principle but for infants <6 months the RCH regimen is 10 mg/kg oral daily for 5 days (not the loading-taper regimen used in ≥6 months); clarithromycin regimen is 7 days at 7.5 mg/kg BD. Consider adding infant-specific note.
  Source: https://www.rch.org.au/clinicalguide/guideline_index/whooping_cough_pertussis/

- **Ramsay Hunt syndrome** - "oral valaciclovir 1 g three times daily for 7 to 10 days plus prednisolone 60 mg tapered over 2 weeks". eTG dose is right; some guidelines use 50 mg prednisolone daily rather than 60 mg. Acceptable minor variation - no change needed.

- **Herpes zoster** - "oral valaciclovir 1 g three times daily for 7 days". Correct.

- **Vulvovaginal candidiasis** - "recurrent - fluconazole 150 mg every 72 h x3 doses then 150 mg weekly for 6 months". Correct per eTG. "C. glabrata - boric acid 600 mg pessary daily for 14 days" - not funded on PBS, so worth flagging as compounded/off-label but no change needed.

- **Impetigo** - "topical mupirocin 2% three times daily for 5 days". Note NT/AHKPI Healthy Skin approach uses cotrimoxazole once for treatment of impetigo in remote Aboriginal communities to cut scabies-driven pyoderma cycle - not required but worth adding one sentence.

- **Diverticulitis** - "outpatient oral amoxicillin-clavulanate or metronidazole plus ciprofloxacin per eTG". Correct pair. Duration not specified - eTG lists 5 days (recent shortening from 7-10) - consider adding.

- **Otitis media** - correct amoxicillin 15 mg/kg TDS for 5 days, 7 days for severe/under 2/bilateral/Aboriginal/Torres Strait Islander child. Aligns with 2021 MJA guidelines.

- **Cellulitis** - "oral flucloxacillin or cefalexin; IV if systemically unwell". Dose/duration not specified. eTG is flucloxacillin 500 mg QID for 5 days (extend to 10 days if slow response). Consider adding.

- **Peritonsillar abscess** - "benzylpenicillin plus metronidazole, or amoxicillin-clavulanate". Correct. eTG dose: benzylpenicillin 1.2 g IV 6-hourly plus metronidazole 500 mg IV 12-hourly.

- **Endocarditis / Infective endocarditis** - "flucloxacillin plus benzylpenicillin plus gentamicin" empirical. Correct per eTG; the eTG regimen has moved to shorter gentamicin (single dose then dosed on function for max 1-2 further doses) rather than routine 2-week course. Consider adding: gentamicin 4-6 mg/kg IV, single dose then reassess (not fixed 2 weeks).
  Source: https://derangedphysiology.com/main/required-reading/sepsis-and-infections/Chapter-216/infective-endocarditis (summarising eTG native-valve regimen).

- **Legionnaire's disease** - "azithromycin or respiratory fluoroquinolone... 7-14 days". Correct. Note doxycycline is not first-line for confirmed Legionella (worth clarifying since the CAP entry uses doxy for atypicals).

- **Tetanus** - "ADT booster every 10 years or 5 for a tetanus-prone wound; HTIG plus vaccine if under 3 previous doses". Correct per AU Handbook. Note ADT has been largely replaced by dTpa/dT in current schedule; wording "ADT" is dated.
  Source: https://immunisationhandbook.health.gov.au/

- **Puerperal sepsis** - "eTG (amoxicillin plus clavulanate plus gentamicin, or piperacillin-tazobactam); add clindamycin if GAS suspected". Correct.

- **Postpartum endometritis** - "eTG ampicillin + gentamicin + metronidazole". Correct. Note eTG allows amoxicillin as substitute for ampicillin (same drug family in AU).

### VERIFIED accurate (spot-check against public AU sources - specific claim confirmed)

- Chlamydia (doxycycline 100 mg BD 7 days first-line; azithromycin 1 g stat alternative/pregnancy) - STI Guidelines Australia
- Gonorrhoea (ceftriaxone 500 mg IM + azithromycin 1 g PO stat) - STI Guidelines Australia
- Pelvic inflammatory disease (ceftriaxone 500 mg IM stat + doxycycline 100 mg BD 14 days + metronidazole 400 mg BD 14 days) - STI Guidelines Australia
- Meningococcal disease (ceftriaxone 2 g IV; ciprofloxacin or rifampicin chemoprophylaxis for close contacts within 24 h) - CDNA/RCH
- Rabies PEP (wound irrigation ≥15 min; HRIG 20 IU/kg; vaccine days 0/3/7/14 immunocompetent; 5 doses to day 28 if immunocompromised) - AU Immunisation Handbook
- Herpes zoster (valaciclovir 1 g TDS 7 days within 72 h) - eTG
- Ramsay Hunt (valaciclovir + prednisolone taper within 72 h) - eTG
- Tuberculosis (RIPE 2 months then RH 4 months; latent - isoniazid 6-9 months or rifampicin 4 months) - AU TB service standard, aligns with international
- Malaria (uncomplicated falciparum - artemether-lumefantrine; vivax/ovale - chloroquine + primaquine 14 days after G6PD; severe - IV artesunate) - eTG
- Otitis media (amoxicillin 15 mg/kg TDS 5 days; 7 days if severe/under 2/bilateral/Aboriginal or Torres Strait Islander child) - 2021 MJA otitis-media guidelines
- Otitis externa (topical ciprofloxacin-hydrocortisone or Sofradex; avoid aminoglycoside if TM perforated; necrotising OE needs IV ciprofloxacin) - eTG
- Sinusitis (viral majority; amoxicillin 5-7 days when bacterial features) - eTG
- Epiglottitis (ceftriaxone plus vancomycin; rifampicin prophylaxis for Hib contacts) - RCH
- Bacterial tracheitis (flucloxacillin + third-gen cephalosporin, add vancomycin for MRSA) - RCH
- Endocarditis empirical (flucloxacillin + benzylpenicillin + gentamicin; vancomycin substitute for MRSA/pen-allergic) - eTG
- Native/prosthetic valve endocarditis coverage principles - eTG
- Retropharyngeal abscess (amoxicillin-clavulanate, or clindamycin + third-gen cephalosporin with vancomycin for MRSA) - eTG paediatric
- Brain abscess (ceftriaxone + metronidazole; add vancomycin, ampicillin for Listeria as appropriate) - eTG
- Spinal epidural abscess (vancomycin + ceftriaxone empirical; 6-8 weeks; surgical decompression) - eTG
- Erysipelas (phenoxymethylpenicillin/amoxicillin oral or benzylpenicillin/ceftriaxone IV; recurrence prophylaxis with penicillin V) - eTG
- Necrotising fasciitis (meropenem + vancomycin + clindamycin; theatre first, imaging second; IVIG in strep TSS) - eTG
- Pharyngitis (phenoxymethylpenicillin 500 mg BD 10 days for GAS; empirical treat in Aboriginal or Torres Strait Islander patients at ARF risk) - eTG and RHDAustralia
- Peritonsillar abscess (benzylpenicillin + metronidazole IV; drainage; steroid) - eTG
- Cavernous sinus thrombosis (vancomycin + ceftriaxone + metronidazole for sinus source; heparin) - eTG
- Hepatitis C (sofosbuvir/velpatasvir or glecaprevir/pibrentasvir pan-genotypic, PBS-listed, any GP prescribes) - PBS
- Hepatitis B (tenofovir alafenamide or entecavir; birth-dose vaccine in high-risk) - RACGP/ASHM
- HIV (start ART regardless of CD4; bictegravir/tenofovir alafenamide/emtricitabine; cotrimoxazole PCP prophylaxis if CD4 <200; azithromycin MAC prophylaxis if CD4 <50) - ASHM
- ARF/RHD (benzathine benzylpenicillin 1.2 million units IM stat for GAS eradication; monthly IM benzathine for secondary prophylaxis ≥10 years or until 21) - RHDAustralia
- Neonatal sepsis (benzylpenicillin + gentamicin early-onset; flucloxacillin + gentamicin or vancomycin + cefotaxime late-onset) - RCH
- Chorioamnionitis (ampicillin + gentamicin, add metronidazole/clindamycin for caesarean) - eTG
- Puerperal sepsis/postpartum endometritis (amoxicillin-clavulanate + gentamicin; add clindamycin for GAS) - eTG
- Pneumocystis pneumonia (high-dose cotrimoxazole 21 days; steroids if PaO2 <70 or A-a gradient >35) - eTG
- Cryptococcal meningitis (induction liposomal amphotericin B + flucytosine 2 weeks; consolidation fluconazole; therapeutic LPs; delay ART 4-6 weeks in HIV) - eTG
- Cryptococcosis (as above) - eTG
- Aspergillosis (voriconazole first line for invasive; itraconazole for ABPA) - eTG
- Candidiasis (nystatin topical or fluconazole oral for mucosal; echinocandin for invasive) - eTG
- Vulvovaginal candidiasis (single-dose fluconazole 150 mg or clotrimazole 500 mg pessary; recurrent regimen; topical imidazole in pregnancy) - eTG
- Toxoplasmosis (pyrimethamine + sulfadiazine + folinic acid; spiramycin in pregnancy pre-18 weeks) - eTG
- Melioidosis (IV meropenem or ceftazidime intensive phase ≥2 weeks, then oral cotrimoxazole 3-6 months eradication) - eTG Tropical
- Q fever (doxycycline 100 mg BD 14 days acute; doxy + hydroxychloroquine ≥18 months for chronic endocarditis) - eTG
- Brucellosis (doxycycline + rifampicin 6 weeks, add gentamicin early) - eTG
- Leptospirosis (doxycycline mild, IV benzylpenicillin/ceftriaxone severe) - eTG
- Lyme disease (doxycycline 14 days early, IV ceftriaxone 14-28 days for neuroborreliosis) - eTG
- Cholangitis (piperacillin-tazobactam or ceftriaxone + metronidazole; urgent biliary decompression) - eTG
- Toxic shock syndrome (vancomycin + clindamycin + beta-lactam; IVIG for streptococcal) - eTG
- Group B Streptococcus (intrapartum benzylpenicillin ≥4 h before delivery; cefazolin/clindamycin/vancomycin for allergy tiers) - RANZCOG/eTG
- Influenza (oseltamivir within 48 h for high-risk/hospitalised) - eTG/PBS
- Scabies (permethrin 5% then repeat day 7; ivermectin 200 mcg/kg days 1 and 8 for crusted/institutional; treat contacts) - eTG
- Bronchiectasis (sputum-directed antibiotics 10-14 days for exacerbations; long-term azithromycin selected; inhaled colistin for Pseudomonas) - Thoracic Society of Australia and NZ
- Legionnaire's disease (azithromycin or moxifloxacin/levofloxacin 7-14 days; beta-lactams do not work) - eTG
- Lung abscess (amoxicillin-clavulanate or clindamycin; typical 4-8 weeks until CXR clears) - eTG
- Cholangitis, empyema, peritonitis (SBP: ceftriaxone + albumin) - eTG
- Tetanus (HTIG + metronidazole + supportive; ADT/dTpa booster per exposure risk) - AU Handbook
- Varicella (oral aciclovir within 24 h for adolescents/adults/pregnancy; IV in immunocompromised; VZIG for non-immune pregnant/neonate/immunocompromised within 96 h) - AU Handbook
- Diphtheria (antitoxin urgently + benzylpenicillin/erythromycin 14 days; erythromycin prophylaxis for contacts) - CDNA
- Typhoid fever (empirical azithromycin or ceftriaxone; MDR/XDR common from subcontinent) - CDNA
- Acne (never antibiotic monotherapy - always combined with benzoyl peroxide or retinoid; isotretinoin via dermatology only) - eTG
- Rosacea (topical metronidazole/ivermectin/azelaic acid; oral doxycycline 40-100 mg for moderate-severe) - eTG
- Mastitis (di/flucloxacillin 500 mg QID 5-7 days; cefalexin if pen allergy; clindamycin if severe) - eTG/ABA
- Epididymitis (age-tiered: ceftriaxone+doxy under 35, ciprofloxacin/trimethoprim over 35) - eTG
- Sepsis/septic shock (hour-1 bundle; broad-spectrum within 1 h; piperacillin-tazobactam or meropenem + vancomycin as local eTG) - eTG
- Febrile neutropenia (piperacillin-tazobactam or cefepime within 1 hour; add vancomycin for line infection/instability) - eTG

### UNVERIFIED (no public AU source found within audit time)

- **Prostatitis** - "ciprofloxacin 500 mg BD or trimethoprim 300 mg daily for 4 weeks (fluoroquinolones penetrate prostate best)". eTG chapter paywalled; TGA has issued fluoroquinolone safety warnings that may push trimethoprim above cipro as first-line in some cases. Flag: verify against current eTG Prostatitis chapter.

- **Necrotising fasciitis** duration/IVIG detail - IVIG dosing not specified (eTG suggests 2 g/kg then 1 g/kg on days 2 and 3). No change needed unless dose is added.

- **Neonatal sepsis late-onset** - "vancomycin plus cefotaxime, or flucloxacillin plus gentamicin, by local guideline". Local variation is real - RCH, SCHN and RCH-Perth all differ. Unable to verify a single "national" answer; framing as "by local guideline" is safe.

- **Aspergilloma treatment** - "surgical resection or bronchial artery embolisation for massive haemoptysis". Uncontroversial but no AU-specific source in audit; flag if changing.

- **Histoplasmosis / Toxoplasmosis induction dosing** - Correct in principle. Detailed pyrimethamine loading (200 mg then 50-75 mg daily) not specified; unverified against current AU HIV guideline (ASHM).

- **Pneumocystis pneumonia steroid trigger** - "PaO2 under 70 mmHg or A-a gradient over 35". This is the widely-used cutoff but the eTG-specific threshold is PaO2 <70 mmHg on room air OR A-a gradient >35 - correct as written. No change needed.

- **Retropharyngeal abscess** - Antibiotic combo correct in principle; specific eTG paediatric doses not verified in this audit.

- **Cavernous sinus thrombosis** - Heparin recommendation carries limited evidence; eTG position is "consider" - the entry says "unless clearly contraindicated" which is stronger than eTG. Flag for wording softening if Rob wants to tighten.

## Notes

- Two priority items were not in the JSON: **Aspiration pneumonia** (only covered inside `Pneumonia` and `Lung abscess`) and **Necrotising fasciitis** (present as `Necrotizing fasciitis` - US spelling). If Rob wants a dedicated aspiration pneumonia summary, that is a gap.

- **Highest-drift categories** in this dataset are UTI (2024 nitrofurantoin swap), CAP severity ladder (November 2024 benzylpen+doxy change), C. difficile (2025 ASID fidaxomicin promotion), and H. pylori (duration extension to 14 days and rising bismuth-quad preference). These are the four to fix first.

- **Framing risk**: several entries say "per eTG" for regimens where the actual eTG has moved on. Recommend a one-off pass that either (a) drops "(eTG)" from timestamps that predate the 2024 update or (b) adds a version-year suffix. eTG Antibiotic v17 is the current live version at time of this audit.

- **PBS restrictions**: fidaxomicin (streamlined for recurrent CDI, expanding) and DAA hepatitis C (any GP) are the two most testable PBS points; both are correctly framed in the current entries.

- **Penicillin allergy handling**: most entries note the allergy pathway but only Mastitis and Impetigo explicitly distinguish immediate from delayed hypersensitivity. Consider a template line ("severity of allergy determines whether cefalosporin cross-cover is acceptable") for the 5-6 entries where this matters (cellulitis, mastitis, endocarditis, GBS intrapartum, syphilis if added, PID).

- **Bat exposure wording** in Rabies entry: "any bat scratch, bite or saliva contact needs PEP - the bat cannot be 'cleared' without killing and testing" is technically accurate but Handbook allows withholding PEP if the bat can be tested within 48 h; consider softening.

- **Gaps worth adding as new entries** (not in scope but flagged): Syphilis (per stage - benzathine penicillin dosing changes are testable), Trichomonas (metronidazole 2 g stat vs 400 mg BD 7 days), LGV (doxycycline 21 days), Chancroid, PrEP (tenofovir/emtricitabine daily), HIV PEP regimen (tenofovir/emtricitabine + dolutegravir 28 days), meningococcal contacts chemoprophylaxis dose (ciprofloxacin 500 mg stat adult), Post-splenectomy prophylaxis (amoxicillin 250 mg daily / phenoxymethylpenicillin 250 mg BD), Dental IE prophylaxis (amoxicillin 2 g PO 30-60 min pre-procedure; clindamycin 600 mg for pen allergy), Surgical prophylaxis (cefazolin 2 g IV within 60 min).
