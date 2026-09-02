# Oncology + AU screening audit - 2026-09-01

## Scope

Audited 65 rich-summary entries covering solid tumours, haematological malignancies, paediatric onc, neuro-onc, endocrine onc/MEN, oncology emergencies, hereditary cancer syndromes, palliative/pain, HPV vaccination and Australian screening / newborn programs. Selection was name-matched from the 686-entry corpus in `all_rich_summaries_2026-09-01.json`.

Sources used: health.gov.au (NBCSP, NCSP, BreastScreen, NLCSP, NBS expansion), Cancer Council Australia, Cancer Australia, RACGP, PCFA 2026 guidelines (NHMRC-approved 18 May 2026), eviQ (APML4, testicular carboplatin, HCC), MJA Insight, Australian Immunisation Handbook, ALLG protocols, ECHELON-1 & POLARIX trial data, PBS Public Summary Documents, AIHW screening monitoring reports 2025. StatPearls/NCCN not used except where AU source was silent (noted in each case).

## Findings

### SUBSTANTIVE errors (change required)

- **Prostate cancer** - claim: "population PSA screening is not recommended in Australia; the discussion is individual and should cover overdiagnosis explicitly." - This was correct under the 2016 PCFA/RACGP guidance but is now outdated. NHMRC approved new PCFA "2026 Guidelines for the Early Detection of Prostate Cancer" on 18 May 2026. These now positively recommend biennial PSA for men 50-69 after informed discussion, with defined age-stratified action levels (>=1.0 ug/L at 45-49 if higher-risk, >=3.0 at 50-69, >=5.5 at 70+), earlier testing (from 45) for higher-risk men (family history, Black sub-Saharan ancestry, BRCA2), mpMRI before biopsy, and >70 testing where life expectancy >7 years. RACGP has voiced concerns but the guideline is NHMRC-endorsed and is the current AU reference. Suggested rewrite of the Ix + Note sentences:
  `Ix: PSA with DRE after informed discussion; mpMRI before any biopsy, then transperineal biopsy for PI-RADS >=3; ISUP grade group on histology; PSMA-PET for staging where indicated. Mx: active surveillance for low-risk disease (the default, not a compromise); radical prostatectomy or radiotherapy for intermediate and high risk; androgen deprivation plus an ARPI or docetaxel up front for metastatic disease. Note: 2026 PCFA/NHMRC guidelines recommend biennial PSA for men 50-69 after informed discussion; earlier (from 45) with lower action thresholds for higher-risk men (family history, BRCA2, Black sub-Saharan ancestry); >70 testing where life expectancy exceeds 7 years.`
  Sources: https://www.racgp.org.au/clinical-resources/clinical-guidelines/key-racgp-guidelines/view-all-racgp-guidelines/prostate-cancer-screening ; https://www.pcfa.org.au/news-media/news/what-are-the-current-guidelines-for-early-prostate-cancer-detection-in-australia/

- **Lung cancer** - claim: entry omits the National Lung Cancer Screening Program entirely. NLCSP is Australia's newest population screening program, funded and launched 1 July 2025 (annual LDCT for ages 50-70 with >=30 pack-year smoking history who currently smoke or quit within 10 years). For a Year-4 Australian audience this is now a core exam and clinical fact. Suggested addition to the Ix line:
  `Screening: National Lung Cancer Screening Program (from 1 July 2025) - annual LDCT for asymptomatic people aged 50-70 with a >=30 pack-year smoking history, currently smoking or quit within 10 years. Ix (symptomatic): CT chest and upper abdomen, then PET-CT for staging...`
  Sources: https://www.health.gov.au/our-work/nlcsp ; https://www.canceraustralia.gov.au/key-initiatives/national-lung-cancer-screening-program ; https://insightplus.mja.com.au/2025/35/the-national-lung-cancer-screening-program-is-now-available-what-doctors-need-to-know/

- **Acute myeloid leukaemia** (APL specifically) - claim: "acute promyelocytic leukaemia... treated with all-trans retinoic acid started on suspicion rather than on confirmation." True but incomplete for the AU context. The Australian standard (ALLG APML4 protocol on eviQ) is triple induction with ATRA + arsenic trioxide + idarubicin; the low-risk international standard is ATRA + ATO alone (chemo-free). Rob's summary implies ATRA monotherapy. Suggested rewrite of the APL sentence:
  `Note: acute promyelocytic leukaemia is the subtype to recognise immediately - it presents with DIC and life-threatening bleeding, and ATRA is started on suspicion rather than confirmation. Definitive treatment is ATRA + arsenic trioxide (chemo-free) for low/intermediate-risk disease; ATRA + arsenic trioxide + idarubicin (Australian ALLG APML4 protocol) for high-risk disease.`
  Sources: https://www.eviq.org.au/haematology-and-bmt/leukaemias/acute-promyelocytic-leukaemia/1939-apml4-overview

### MINOR issues

- **Colorectal cancer** - "NBCSP immunochemical FOBT every 2 years age 45-74" is factually accurate on eligibility, but omits that only 50-74 get automatic mail-out; 45-49 need to opt in via webform or 1800 627 701. Worth adding for a GP-facing audience since this drives GP conversations. Suggested tweak:
  `NBCSP iFOBT every 2 years age 45-74 (mail-out automatic 50-74; ages 45-49 opt in).`
  Source: https://www.health.gov.au/our-work/national-bowel-cancer-screening-program

- **Hodgkin lymphoma** - "ABVD chemotherapy with or without radiotherapy" is still the safe exam answer, but as of ECHELON-1 5-year OS data BV-AVD (brentuximab vedotin + AVD) has demonstrated a survival benefit over ABVD in advanced-stage disease and is now first-line in many AU centres for stage III/IV disease. No change strictly required but worth flagging so Rob knows. Suggested optional tweak:
  `Mx: ABVD (early-stage) or BV-AVD (brentuximab vedotin + AVD; ECHELON-1 OS benefit, now standard for advanced stage III/IV) with or without radiotherapy; guided by stage and interim PET response.`
  Source: https://www.nejm.org/doi/full/10.1056/NEJMoa2206125

- **Multiple myeloma** - "induction with a proteasome inhibitor, an immunomodulatory drug and dexamethasone" (i.e. VRd) is correct historical AU standard. Daratumumab has been added to first-line induction (DVRd/D-VTd quadruplets) internationally and is PBS-listed for MM. The recent PBAC decision on frontline dara + LenDex for transplant-ineligible was mixed. Not strictly wrong; entry could mention the CD38 quadruplet direction. Optional; no forced rewrite.
  Source: https://www.health.gov.au/ministers/the-hon-mark-butler-mp/media/cheaper-cancer-and-chronic-conditions-medicines-now-on-pbs

- **Superior vena cava syndrome** - final sentence "Note: SVCS is rarely emergent." reads as contradicting the same entry's description of airway compromise and cerebral oedema. Standard teaching is that <5% of SVCS is truly emergent, but the sentence is stripped of context and could mislead. Suggest:
  `Note: SVCS is usually subacute; only a minority (~5%) with stridor, laryngeal oedema, or altered consciousness is a true emergency requiring immediate stenting.`

- **Testicular cancer** - "stage I seminoma - surveillance or single-dose carboplatin" is correct per eviQ protocol 325 (AUC7). Only nit: adjuvant radiotherapy remains a third option in AU (though used less due to secondary-cancer risk); can note "surveillance preferred; single-dose carboplatin AUC7 or para-aortic RT for higher-risk features". Optional.
  Source: https://www.eviq.org.au/medical-oncology/urogenital/testicular/325-testicular-germ-cell-seminoma-adjuvant-carbopl

- **Waldenström macroglobulinaemia** - "urgent plasmapheresis for hyperviscosity" is correct; the "do NOT start rituximab first - IgM flare worsens viscosity" caution is well-taught. Accurate.

- **Colorectal cancer / Lynch** - Lynch entry correctly cites CAPP2 trial and 100 mg aspirin. Verified.

- **Congenital hypothyroidism** - "10-15 microgram/kg/day, crush in breastmilk/formula/water - not soy or iron together" is accurate per RCH Melbourne and AACB. The "start before 2 weeks" figure is a well-established target (some sources use 14 days, RCH says by 2 weeks; ideal <10 days). No change.

- **Phenylketonuria** - "aspartame is metabolised to phenylalanine - PKU patients must avoid it (warnings on packaging in Australia)" - accurate; FSANZ Standard 1.2.3 mandates the warning. Fine.

- **Spinal muscular atrophy** - "newborn screening now in NSW, Vic and elsewhere" understates: NBS for SMA is being rolled out nationally with staggered state implementation (Qld from May 2023, NSW/ACT from Aug 2018 pilot then routine, Vic from mid-2023, WA/SA/Tas/NT progressively). Could tighten to "nationally rolled out with state-varying start dates". Optional.
  Source: https://www.health.gov.au/our-work/newborn-bloodspot-screening/expansion

- **Melanoma** - "sentinel node biopsy if Breslow above 0.8 mm or ulcerated" - matches current AU consensus (Melanoma Institute Australia / Cancer Council CPG). Fine.

- **Human papillomavirus infection** - "Gardasil 9 on NIP at school year 7 as single dose since Feb 2023; funded catch-up to age 25" verified accurate to the letter.
  Source: https://www.health.gov.au/news/changes-to-hpv-vaccine-dose-schedule-for-young-australians

- **Endometrial cancer** - "postmenopausal cut-off 4 mm" for endometrial thickness is accepted AU cut-off (RANZCOG). Correct.

- **Ovarian cancer** - "PARP inhibitors (olaparib, niraparib) for BRCA-mutated or HRD-positive disease" - correct, both PBS-listed for the relevant indications.

- **Pancreatic cancer** - "adjuvant modified FOLFIRINOX" is correct AU standard (PRODIGE 24). Fine.

### VERIFIED accurate (no changes)

Acoustic neuroma, Acute lymphoblastic leukaemia, Barrett oesophagus, Basal cell carcinoma, Bladder cancer, Bowen's disease, Breast cancer, Burkitt lymphoma, Carcinoid syndrome, Cervical cancer, Cervical ectropion, Cholangiocarcinoma, Chronic lymphocytic leukaemia, Chronic myeloid leukaemia, Chronic non-cancer pain, Congenital hypothyroidism (see minor note), Diffuse large B-cell lymphoma, Endometrial cancer, Ewing sarcoma, Familial adenomatous polyposis, Febrile neutropenia, Follicular lymphoma, Gestational trophoblastic disease, Glioblastoma, Hairy cell leukaemia, Hepatocellular carcinoma, Human papillomavirus infection, Hypercalcaemia, Insulinoma, Lynch syndrome, Mantle cell lymphoma, Medullary thyroid carcinoma, Melanoma, Multiple endocrine neoplasia, Multiple endocrine neoplasia type 2, Multiple myeloma (see minor note), Myelofibrosis, Neurofibromatosis, Non-Hodgkin lymphoma, Oesophageal cancer, Osteosarcoma, Ovarian cancer, Pancreatic cancer, Paraganglioma, Phaeochromocytoma, Phenylketonuria, Pheochromocytoma, Polycythaemia vera, Postmenopausal bleeding, Primary CNS lymphoma, Renal cell carcinoma, Spinal cord compression, Spinal muscular atrophy (see minor note), Squamous cell carcinoma, Testicular cancer (see minor note), Thyroid cancer, Tumour lysis syndrome, Von Hippel-Lindau syndrome, Waldenström macroglobulinaemia.

### UNVERIFIED (no public AU source directly consulted; content matches international standard)

- **Glioblastoma** - Stupp protocol (concurrent TMZ chemoradiotherapy then adjuvant TMZ) is international standard; MGMT methylation as prognostic biomarker is correct. No AU-specific NHMRC/eviQ guideline was reviewed but the content matches eviQ TMZ protocols.
- **Ewing sarcoma** - VDC/IE regimen, 70% localised / <30% metastatic survival figures match international standard (COG); no AU source reviewed.
- **Osteosarcoma** - MAP regimen (methotrexate/doxorubicin/cisplatin), 60-70% localised survival matches international standard; no AU source reviewed.
- **Cholangiocarcinoma** - gem/cis + durvalumab per TOPAZ-1 matches international first-line; PBS status not directly verified.
- **Waldenström** - MYD88 L265P prevalence >90% and BTKi first-line direction match international NCCN and WMUK guidance; not AU-source-verified.

## Notes

1. The single biggest issue is that **prostate cancer screening in Australia was rewritten in May 2026**. Rob's current summary reflects the 2016 stance and is now materially outdated. This is the most exam-relevant fix.
2. The **lung cancer entry has no NLCSP mention** - the program launched 1 July 2025 and is a core Australian primary-care conversation. Adding a Screening line is a moderate-priority fix.
3. The **APL entry** understates the Australian ALLG APML4 protocol (triple induction with ATRA + ATO + idarubicin for high-risk) - worth aligning since this is what Australian haematologists actually give.
4. Overall the oncology corpus is high-quality and Australian-flavoured (NBCSP/NCSP/BreastScreen figures accurate, eviQ-consistent chemo regimens, appropriate PBS-listed targeted therapies). No fabricated staging systems or invented drug names spotted.
5. Rob may want to consider a companion "General cancer screening" entry that consolidates NBCSP + NCSP + BreastScreen + NLCSP + NBS + NIPT in one place - currently each program appears only inside its specific-cancer entry. Not in scope for this audit, just an observation.
