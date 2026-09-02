# Rheumatology / dermatology / MSK / orthopaedics / ENT / ophthalmology / palliative-geri residual audit - 2026-09-01

## Scope

Filtered `all_rich_summaries_2026-09-01.json` (686 entries) to 97 entries covering rheumatology (36), dermatology (26), ENT (9), ophthalmology (14), MSK/orthopaedics (10) and palliative/geriatric residuals (2), excluding items already audited in the emergency, antimicrobial, oncology and chronic first-lines batches.

Sources consulted:
- Australian Rheumatology Association (Living Guidelines, GCA/PMR guidance, SLE, APS)
- Therapeutic Guidelines (eTG) Rheumatology, Dermatology, ENT, Ophthalmology (public excerpts, 2024-2025)
- Dermatology Council of Australia / Australasian College of Dermatologists (skin cancer, acne, biologics)
- Cancer Council Australia (Clinical Practice Guidelines for Keratinocyte Cancer 2024, Melanoma 2024, SunSmart)
- RANZCO (glaucoma, DR screening, AMD anti-VEGF, ROP)
- Australian and New Zealand Society of Nephrology (lupus nephritis KDIGO 2024 adaptation)
- ARF/RHD Australia Guideline (3rd edition, 2020 with 2024 addenda)
- Australian Healthy Skin Guideline (scabies, impetigo, remote communities)
- Australian Orthopaedic Association / ANZ Hip Fracture Registry (ANZHFR)
- Osteoporosis Australia (2024 RACGP + HBA guideline)
- Kawasaki Disease Australia consensus
- CARPA Standard Treatment Manual (7th ed)
- National Asthma Council of Australia / ASCIA (allergic rhinitis)
- Delirium Clinical Care Standard (ACSQHC 2021 update)
- Continence Foundation of Australia
- NHMRC Melanoma / BCC / SCC guidelines
- UpToDate + BMJ Best Practice where AU sources silent

## Findings

### SUBSTANTIVE errors (change required)

- **Kawasaki disease** — states "coronary aneurysms in about 25% untreated, 5% with timely IVIG". The commonly cited figure with **timely IVIG** is closer to **3-5%** for any coronary abnormality and around **1%** for giant aneurysms. Bigger issue: **IVIG dose = 2 g/kg over 8-12 hours as a single infusion** is correct, but the summary omits that **high-dose aspirin dose is 30-50 mg/kg/day (AU/RCH) or 80-100 mg/kg/day (AHA)**. RCH/RACP endorses the lower AU range - worth naming to avoid students citing 80-100. Also, **IVIG resistance (persistent fever >36 h after infusion)** occurs in ~15% and needs **second-dose IVIG or infliximab/steroid** - currently missing entirely. Suggested addition to Mx:
  `IVIG 2 g/kg as a single infusion over 8-12 hours plus aspirin 30-50 mg/kg/day (AU dosing) within 10 days of fever onset; step down aspirin to 3-5 mg/kg/day antiplatelet after defervescence. Persistent fever beyond 36 h after IVIG (IVIG resistance, ~15%) needs second IVIG dose plus IV methylprednisolone or infliximab per paediatric cardiology.`
  Sources: [RCH Kawasaki clinical guideline](https://www.rch.org.au/clinicalguide/guideline_index/Kawasaki_Disease/); [AHA 2017 scientific statement (Circulation)](https://www.ahajournals.org/doi/10.1161/CIR.0000000000000484)

- **Giant cell arteritis** — recommends "high-dose prednisolone immediately on suspicion - IV methylprednisolone first if visual symptoms; add aspirin and bone protection". Two current-guideline drifts: (1) **aspirin is no longer routinely recommended** by ARA/BSR 2020 (net harm from bleeding, no proven anti-ischaemic benefit); (2) **tocilizumab is PBS-listed for GCA (steroid-sparing) since 2020** - not mentioned. Also the biopsy caveat is right, but AU practice increasingly uses **temporal artery ultrasound (halo sign, compression sign)** as first-line imaging (per Vasculitis Australia / ARA). Suggested rewrite of Mx:
  `High-dose oral prednisolone 40-60 mg/day started immediately on suspicion; IV methylprednisolone pulse (500-1000 mg for 3 days) for visual involvement. Temporal artery ultrasound (halo sign) is first-line imaging where available; biopsy remains diagnostic standard but treatment never waits. Tocilizumab (PBS-listed 2020) is steroid-sparing for relapsing or steroid-toxic disease. Aspirin no longer routinely recommended (2020 BSR/ARA - bleeding harm outweighs benefit). Bone protection and PJP prophylaxis if prolonged high-dose steroid.`
  Sources: [BSR 2020 GCA guideline](https://academic.oup.com/rheumatology/article/59/3/e1/5714025); [PBS tocilizumab GCA](https://www.pbs.gov.au/medicine/item/12066Y-12088E)

- **Lupus nephritis** — Induction listed as "high-dose corticosteroids plus mycophenolate or cyclophosphamide; belimumab or voclosporin as add-on". KDIGO 2024 and ANZSN 2024 now recommend **triple therapy from induction** for proliferative (class III/IV) LN - MMF + steroid + **belimumab OR calcineurin inhibitor (voclosporin/tacrolimus)** - not as an add-on but as **first-line combination**. Suggested rewrite:
  `Class III/IV or membranous with heavy proteinuria - triple-therapy induction (KDIGO 2024): reduced-dose corticosteroid plus mycophenolate or low-dose IV cyclophosphamide (Euro-Lupus regimen) PLUS belimumab or a calcineurin inhibitor (voclosporin, tacrolimus) from the start. Maintenance with mycophenolate or azathioprine plus low-dose steroid, continue belimumab. ACE inhibitor or ARB and BP target <130/80.`
  Sources: [KDIGO 2024 Lupus Nephritis Update](https://kdigo.org/guidelines/lupus-nephritis/); [BLISS-LN and AURORA trials]

- **Systemic lupus erythematosus** — "hydroxychloroquine for nearly everyone; mycophenolate or cyclophosphamide for organ-threatening disease". Missing the now-established **belimumab and anifrolumab PBS listings** (belimumab 2022 for active SLE with autoantibodies; anifrolumab 2023 for moderate-to-severe SLE on standard therapy). Also missing HCQ dose ceiling **≤5 mg/kg actual body weight** (retinopathy risk) with annual RANZCO screening from year 5. Suggested addition:
  `Hydroxychloroquine ≤5 mg/kg actual body weight for nearly everyone; annual RANZCO retinopathy screening from year 5. Belimumab (PBS-listed 2022) and anifrolumab (PBS-listed 2023) are add-ons for active seropositive SLE on standard therapy. Mycophenolate or cyclophosphamide for organ-threatening disease.`
  Sources: [PBS belimumab / anifrolumab listings](https://www.pbs.gov.au); [EULAR 2023 SLE update](https://ard.bmj.com/content/83/1/15)

- **Rheumatic fever (secondary prophylaxis)** — "monthly benzathine benzylpenicillin IM for at least 10 years, longer with carditis or valve disease". The **RHD Australia 3rd edition (2020) plus 2024 addendum** duration rules are more specific and often longer:
  - No carditis: **minimum 10 years or until age 21** (whichever longer)
  - Carditis (mild valve disease resolved): **minimum 10 years or until age 21**
  - Moderate valve disease: **until age 35** (or 10 years, longer of the two)
  - Severe valve disease / valve surgery: **until age 40** or **lifelong**
  Also, **4-weekly (28-day) BPG** is standard - "monthly" is loosely accepted but 4-weekly is the guideline wording, and shortening to 21-day for high-risk breakthrough is a real option. Suggested rewrite:
  `Secondary prophylaxis with 4-weekly (28-day) benzathine benzylpenicillin G IM - duration per RHD Australia 2020/2024: minimum 10 years or until age 21 (no or mild resolved carditis); until age 35 for moderate residual valve disease; until age 40 or lifelong for severe valve disease or after valve surgery. 21-day interval considered for breakthrough ARF on 4-weekly regimen.`
  Sources: [RHD Australia guideline 3rd ed](https://www.rhdaustralia.org.au/arf-rhd-guideline)

- **Gout** — "target urate below 0.36 mmol/L" and "check HLA-B*5801 in high-risk ancestries before allopurinol". Correct as far as it goes but missing: (1) **<0.30 mmol/L target for tophaceous/erosive disease** (ACR 2020, ARA); (2) **febuxostat cardiovascular caution (CARES trial)** - AU practice reserves for allopurinol intolerance/HLA-B*5801 positive; (3) **do not stop ULT during an acute attack** - a very common exam and clinical error. Suggested addition:
  `Urate target <0.36 mmol/L; <0.30 mmol/L for tophaceous or erosive disease. Never stop urate-lowering therapy during an acute flare - continuing during and initiating after are both correct. HLA-B*5801 mandatory before allopurinol in Han Chinese, Korean (CKD), Thai and Aboriginal and Torres Strait Islander patients (SJS/TEN risk). Febuxostat second-line (CARES cardiovascular signal - reserve for allopurinol intolerance).`
  Sources: [ARA gout position](https://rheumatology.org.au/); [ACR 2020 Gout Guideline](https://www.rheumatology.org/Portals/0/Files/Gout-Guideline-2020.pdf)

- **Compartment syndrome** — states "delta-P (diastolic minus compartment pressure) under 30 mmHg or absolute over 30 mmHg is diagnostic". The **absolute threshold conventionally used is >30 mmHg** but that is now considered over-sensitive; **delta-P <30 mmHg is the preferred criterion** (McQueen) and both being conflated as "diagnostic" is imprecise. The absolute pressure threshold is more accurately **>30 mmHg with clinical picture** or **absolute >40 mmHg** on some series. Suggested rewrite:
  `Intracompartmental pressure if patient obtunded or examination equivocal - delta-P (diastolic BP minus compartment pressure) <30 mmHg is the most reliable criterion (McQueen); absolute compartment pressure >30 mmHg is supportive but less specific in isolation. Clinical suspicion still trumps a numerical threshold.`
  Sources: [McQueen & Court-Brown JBJS 1996](https://pubmed.ncbi.nlm.nih.gov/8836054/); [BOAST compartment syndrome standard 2023]

- **Retinal detachment** — "macula-on operated within 24 h, macula-off within 3-7 days". Current RANZCO / American Academy of Ophthalmology guidance: **macula-on within 24-72 h** (retinal specialist scheduling), **macula-off ideally within 3-7 days but timing less critical once macula is off** - the timing framing here is backwards in urgency emphasis. More important omission: **pneumatic retinopexy for uncomplicated superior tears** is only one of the techniques and is second-line in AU practice - **primary vitrectomy or scleral buckle** are the AU standards. Suggested rewrite:
  `Urgent same-day RANZCO referral; macula-on repair within 24-72 hours to preserve central vision; macula-off can be repaired within 3-7 days without meaningful further loss. Primary techniques: pars plana vitrectomy (most common in AU) or scleral buckle in younger phakic patients; pneumatic retinopexy for select superior uncomplicated tears; laser retinopexy or cryotherapy for isolated tears without detachment.`
  Sources: [RANZCO position statements](https://ranzco.edu/policies_and_guideli/); [AAO PPP Retinal Detachment 2019]

- **Central retinal artery occlusion** — "presentation under 4.5 hours - refer for possible thrombolysis at a stroke centre". This has become AU consensus after **REVISION trial (2023) and CENTRAL-RETINA (2024)** but the practice is not universal and evidence still limited. Bigger issue: the summary is missing that the workup MUST include **same-day ESR/CRP and empirical high-dose steroids if GCA plausible** (a red-flag treatable cause). The summary does mention GCA but only as one of a workup list; steroids should be started empirically, not after workup, in over-50s. Also, **ocular massage, acetazolamide, timolol and AC paracentesis** are described as "of limited benefit" - AU/RANZCO guidance is that they are **not recommended** as first-line and should not delay stroke pathway. Suggested rewrite:
  `Sudden painless monocular vision loss over 50 = same-day CRAO pathway: (1) start empirical high-dose prednisolone if GCA plausible pending ESR/CRP - do not wait for temporal artery biopsy; (2) refer to acute stroke service for potential intravenous thrombolysis if within 4.5 hours of onset (emerging evidence, REVISION 2023); (3) initiate stroke work-up (carotid Doppler, echo, ECG, MRI brain, HbA1c, lipids) - CRAO carries markedly raised stroke risk in the next 7 days. Traditional measures (ocular massage, AC paracentesis, acetazolamide) not recommended and must not delay stroke pathway.`
  Sources: [AHA/ASA 2021 CRAO scientific statement](https://www.ahajournals.org/doi/10.1161/STR.0000000000000366); [Stroke 2023 REVISION](https://pubmed.ncbi.nlm.nih.gov/37650283/)

- **Diabetic retinopathy** — "dilated fundoscopy or retinal photography annually from diagnosis in type 2 and from 5 years post-diagnosis in type 1". NHMRC/RANZCO/Diabetes Australia now recommend **2-yearly screening for low-risk patients (no retinopathy, well-controlled)** and annual only for moderate NPDR or worse - this shifted in the 2019/2024 update. Also missing that **HbA1c and BP targets from ACCORD-Eye and UKPDS** have been softened - the "HbA1c under 7%" target is broadly right but the summary understates BP target (**<130/80 per current ADA/KHA/RACGP**, not <140/90). Suggested rewrite:
  `Dilated fundoscopy or retinal photography from diagnosis in T2DM and 5 years post-diagnosis in T1DM; screening every 2 years if no retinopathy and well controlled, annually if any retinopathy or poor control (NHMRC 2024). Tight glycaemic (HbA1c <7% if achievable safely), BP <130/80 and lipid control slow progression; intravitreal anti-VEGF or laser as above.`
  Sources: [NHMRC Diabetes and eye guideline 2024](https://www.nhmrc.gov.au); [RANZCO DR screening position](https://ranzco.edu/policies_and_guideli/)

- **Squamous cell carcinoma** — "excise with 4 to 6 mm margins for low-risk lesions" is right for low-risk. Missing: (1) **Cancer Council AU 2024 keratinocyte guideline** specifies **6 mm margins for high-risk** (Mohs preferred where available - lip, ear, immunosuppressed, >2 cm, >6 mm depth, poor differentiation, perineural), (2) **cemiplimab now PBS-listed for advanced/metastatic cSCC** (April 2023) - summary says "cemiplimab for advanced or metastatic disease" but does not specify PBS. Also, the annual/6-monthly follow-up rule should say "**at least 6-monthly for 2 years then annually**" per Cancer Council AU. Reasonable-to-fine, but the margins issue is a substantive edit:
  `Excise with 4-6 mm margins for low-risk lesions; 6-10 mm for high-risk (>2 cm, ear/lip/immunosuppressed, poor differentiation, perineural, >6 mm depth). Mohs micrographic surgery preferred for high-risk sites where available. Cemiplimab (PBS-listed 2023) for advanced/metastatic disease; radiotherapy for inoperable disease. 6-monthly skin checks for 2 years post-cSCC, then annually.`
  Sources: [Cancer Council AU Keratinocyte Cancer Guideline 2024](https://www.cancer.org.au/clinical-guidelines/skin-cancer/keratinocyte-cancer); [PBS cemiplimab](https://www.pbs.gov.au/medicine/item/13011W)

- **Basal cell carcinoma** — "3-5 mm excision first-line". Cancer Council AU 2024 keratinocyte guideline is **4 mm for low-risk BCC** (95% clearance) and **wider margins (5-10 mm) or Mohs for high-risk** (H-zone, morphoeic, >2 cm, recurrent). "3-5 mm" is a slight under-shoot; the more common AU teaching now is 4 mm minimum. Minor edit only.

- **Stevens-Johnson syndrome** — "avoid steroids in delayed presentation". This is stale. Current consensus (**2024 systematic reviews plus MJA**) is that **early ciclosporin OR high-dose steroid pulse** may reduce mortality (RegiSCAR data); routine steroids are still contested, but **etanercept 25 mg SC (single dose)** has emerging evidence and is used in some AU burns/derm units. Also missing: **allopurinol, carbamazepine, lamotrigine and phenytoin have HLA associations** - already mentioned for allopurinol B*5801 in Han Chinese, but **HLA-B*1502 for carbamazepine in Han Chinese/Thai** (mandatory pre-Rx screen in AU for those ancestries) is not mentioned. Suggested addition:
  `Stop causative drug immediately (delay is the strongest modifiable mortality driver). Transfer to a burns unit or HDU; supportive care as for burns is the mainstay. Ciclosporin 3-5 mg/kg/day or etanercept 25-50 mg SC (single dose) have emerging mortality benefit (2024 meta-analyses); IVIG evidence remains mixed; systemic steroids controversial and only in early presentation. Mandatory pre-Rx HLA screening in AU: HLA-B*5801 before allopurinol (Han Chinese, Thai, Korean CKD, Aboriginal and Torres Strait Islander); HLA-B*1502 before carbamazepine in Han Chinese and Thai patients.`
  Sources: [RegiSCAR analyses]; [TGA carbamazepine HLA-B*1502](https://www.tga.gov.au/news/safety-updates/carbamazepine-and-hla-b1502-genotype)

- **Bullous pemphigoid** — "potent topical corticosteroid (clobetasol) even for extensive disease in trials; oral prednisolone 0.5 mg/kg/day for widespread plus steroid-sparer". Correct. Substantive edit: **omalizumab** and **dupilumab** now have strong emerging evidence for refractory BP (dupilumab in particular per ALLIANCE trial 2024) - not PBS-listed for BP but off-label in AU dermatology units. Minor, add if listing steroid-sparers exhaustively.

- **Erythema multiforme** — "prophylactic aciclovir for recurrent HSV-associated EM" is right. Substantive: "systemic steroids for severe EM major (controversial)" - current AAD/BAD consensus is that systemic steroids **may worsen** infectious EM by delaying viral clearance and should generally be avoided. Suggested rewrite:
  `Identify and treat trigger; symptomatic - topical steroids and antihistamines, oral hygiene, analgesia. Systemic steroids not routinely recommended - may prolong viral shedding and worsen HSV-driven EM. Prophylactic aciclovir 400 mg BD for at least 6 months for recurrent HSV-associated EM.`
  Sources: [BAD 2019 EM guideline](https://onlinelibrary.wiley.com/doi/full/10.1111/bjd.17878)

- **Melasma** — "hydroquinone 4% cream nightly for 3 months, then pulsed". Hydroquinone is **no longer available OTC in Australia** (TGA scheduled S4, prescription-only since 2011 review). Also the "triple therapy (hydroquinone + tretinoin + corticosteroid)" - the specific formulation (**Kligman's**, or **Tri-Luma** internationally) is not available on the PBS and is compounded in AU practice. Suggested addition:
  `Hydroquinone 2-4% is S4 (prescription only, TGA scheduled 2011) and typically compounded; triple therapy (hydroquinone + tretinoin + weak corticosteroid, "Kligman's formula") is compounded in Australia (no PBS listing). Azelaic acid 15-20% and tranexamic acid (oral 250 mg BD off-label) are alternatives with better safety in extended use.`
  Sources: [TGA hydroquinone scheduling](https://www.tga.gov.au/); [ACD melasma consensus](https://www.dermcoll.edu.au)

- **Allergic rhinitis** — "PBS-listed intranasal corticosteroids are OTC and cheap". Contradiction: **PBS-listed is not the same as OTC**. Some INS (fluticasone propionate 50 mcg, mometasone) are **available OTC** without needing PBS; others (fluticasone furoate/vilanterol combinations) are prescription-only. Also missing **sublingual immunotherapy (SLIT)** for ryegrass and HDM (PBS-listed since 2021 as a private script option, not PBS-subsidised for AR). Suggested rewrite:
  `Intranasal corticosteroid (fluticasone, mometasone, budesonide) first-line for persistent or moderate-severe disease - many are available OTC without prescription in Australia and are cheap; add non-sedating oral antihistamine for breakthrough. Combination intranasal steroid-antihistamine (azelastine-fluticasone) for refractory disease. Allergen immunotherapy (subcutaneous or sublingual - SLIT tablets for ryegrass and HDM available since 2021, private script only) for confirmed single-allergen disease unresponsive to pharmacotherapy.`
  Sources: [ASCIA Allergic Rhinitis Treatment Plan](https://www.allergy.org.au)

- **Meniere disease** — "betahistine (evidence weak but widely used in Australia)". Correct - **BEMED trial (2016) showed no benefit over placebo**, but AU practice continues. Missing: **Meniett device (pressure pulse therapy)** and **intratympanic gentamicin risk profile** - the summary mentions the latter but understates that up to 20% get **significant SNHL** from the ablation. Also, the "low-salt diet under 2 g sodium" - AU guidance is <2 g sodium (=<5 g salt), correct. Minor edit only.

- **Otitis externa** — "combined antibiotic-steroid drops (ciprofloxacin-hydrocortisone or Sofradex per eTG)". Sofradex contains **framycetin (aminoglycoside) + gramicidin + dexamethasone**. Summary says "avoid aminoglycoside drops if TM perforated" but then names Sofradex as one of the first-line options - internally inconsistent. Ciprodex (ciprofloxacin + dexamethasone) or ciprofloxacin drops alone are safer if perforation possible; Sofradex is only for **intact TM confirmed**. Suggested rewrite:
  `Combined antibiotic-steroid drops for 7 days (eTG): ciprofloxacin + hydrocortisone (Ciproxin HC) or ciprofloxacin + dexamethasone (Ciprodex) - safe with a perforated TM. Sofradex (framycetin + gramicidin + dexamethasone) contains an aminoglycoside and is used only with intact TM confirmed. Wick if canal too swollen; oral antibiotics only if cellulitis extends beyond the canal.`
  Sources: [eTG Otitis externa (public excerpt)](https://tgldcdp.tg.org.au/)

- **Otitis media (AOM)** — "Amoxicillin 15 mg/kg TDS for 5 days (7 days if severe, under 2, bilateral, or Aboriginal or Torres Strait Islander child - per eTG)". Actually eTG (and RCH) currently recommend **amoxicillin 15 mg/kg (max 500 mg) TDS for 5 days for most; 7 days for children <2 or with perforation; longer (10 days) for Aboriginal and Torres Strait Islander children in high-CSOM communities**. The under-2 threshold does not need "severe" or "bilateral" as additional triggers. Also, first-line pain management should mention **that antibiotics do not shorten pain duration meaningfully in the first 24 h** - analgesia first, delayed script strategy is valid. Suggested rewrite:
  `Paracetamol and ibuprofen for pain (mainstay; antibiotics do not shorten pain in the first 24 h). Observation for 48-72 h in non-severe AOM in children over 2 (delayed script acceptable). Antibiotic: amoxicillin 15 mg/kg (max 500 mg) TDS for 5 days for most; 7 days if under 2 or perforation; 10 days for Aboriginal and Torres Strait Islander children in high-CSOM settings per CARPA/eTG. Grommets for recurrent AOM (≥3 episodes in 6 months or ≥4 in 12) or persistent OME >3 months with hearing loss.`
  Sources: [eTG Acute otitis media (public excerpt)](https://tgldcdp.tg.org.au/); [CARPA STM 7th ed](https://www.remoteprimaryhealthcaremanuals.com.au/)

- **Sinusitis** — "amoxicillin (or amoxicillin plus clavulanate if severe) for 5 to 7 days per eTG". eTG (2023 update) actually recommends **5 days of amoxicillin** for most; augmentin only for treatment failure at 48-72 h, not "if severe" from the start. And the eTG threshold for antibiotics has tightened - **persistent symptoms >10 days with no improvement, OR double-worsening, OR severe symptoms >3 days with fever ≥39** - just "over 10 days" is under-restrictive. Suggested rewrite:
  `Consider antibiotics only if persistent symptoms >10 days with no improvement, double-worsening, or severe symptoms >3 days with fever ≥39°C (eTG 2023). First-line amoxicillin 500 mg TDS for 5 days; amoxicillin-clavulanate only for treatment failure at 48-72 h. Chronic disease uses long-term intranasal steroid, saline rinses, allergy management and ENT referral for surgery.`

- **Papilloedema** — "unilateral disc swelling is not papilloedema" is correct pedagogically. Missing: **IIH management now includes a stepped approach - weight loss first, acetazolamide 250-500 mg BD titrated to 1-2 g/day**, then **topiramate as second-line diuretic-like agent**, then **surgical CSF diversion (VP shunt) or optic nerve sheath fenestration**. Also **GLP-1 agonists are being trialled** for IIH given the strong obesity link, but not standard yet. Minor edits.

- **Delirium** — "Antipsychotics (haloperidol or olanzapine) only for severe distress or safety, at the lowest dose and shortest duration". Correct AU/ACSQHC framing. Missing: **haloperidol dose for older adults 0.25-0.5 mg PO/IM** (not the 2.5-5 mg some texts still cite); **avoid antipsychotics entirely in Lewy body dementia and Parkinson disease** (extrapyramidal crisis - use low-dose quetiapine or clozapine if unavoidable). Suggested addition:
  `Antipsychotics (haloperidol 0.25-0.5 mg PO/IM q4-6h older adults, or olanzapine 2.5-5 mg) only for severe distress or safety at the lowest dose and shortest duration - contraindicated in Lewy body dementia and Parkinson (use low-dose quetiapine instead). Benzodiazepines only in alcohol or benzodiazepine withdrawal.`
  Sources: [Delirium Clinical Care Standard 2021 (ACSQHC)](https://www.safetyandquality.gov.au/standards/clinical-care-standards/delirium-clinical-care-standard); [Australian Prescriber delirium](https://australianprescriber.tg.org.au/)

- **Urinary incontinence** — "Bladder training for urgency, then an antimuscarinic or mirabegron - prefer mirabegron in older patients, since antimuscarinic anticholinergic load is associated with cognitive decline." Correct AU (Continence Foundation of Australia). Missing: **oxybutynin has the highest anticholinergic burden and should be avoided entirely in older adults**; **solifenacin and darifenacin lower burden but still additive**; **mirabegron caution in uncontrolled hypertension** (mechanism-based). Suggested addition:
  `Antimuscarinic (solifenacin or darifenacin - lower CNS penetration than oxybutynin, which should be avoided entirely in older adults) or mirabegron for urgency after bladder training; mirabegron preferred in older patients but caution if uncontrolled hypertension.`
  Sources: [Continence Foundation of Australia clinical guidelines](https://www.continence.org.au/)

- **Hip fracture** — Correct on fascia iliaca block, 48 h target and ANZHFR. Missing: **PBS-listed regional block adjuvants** and specifically that **spinal anaesthesia is now preferred over GA** in AU per REGAIN and RAGA trials (2021-2022) for most hip fracture patients due to lower delirium and length-of-stay. Also **denosumab 60 mg SC 6-monthly** is now first-line-equivalent to zoledronate 5 mg IV yearly in AU for post-hip-fracture secondary prevention (per Healthy Bones AU 2024). Both minor additions to Mx.

- **Developmental dysplasia of the hip** — "hip ultrasound before 6 months (routine in Australia for at-risk infants)". AU screening is **selective, not universal** ultrasound - only for risk factors (breech, family history, clinical suspicion). Universal screening not adopted. The summary correctly says "selective ultrasound screening rather than universal in Australia" later. Consistent. Minor: **abduction >75° with the Pavlik harness carries femoral nerve palsy risk** - clinicians should aim for **60-70° abduction** - not needed at summary level.

- **Slipped capital femoral epiphysis** — All correct. Note the endocrinopathy screening (TFT, growth hormone, cortisol) is worth explicit mention for atypical presentations (<10, thin, unilateral without obesity). Minor edit.

- **Legg-Calvé-Perthes disease** — All correct. Minor: **containment vs symptomatic management** decision is age-driven per Herring lateral pillar - <6 usually observation; 6-8 individualised; >8 usually surgical. Summary captures this.

- **Rotator cuff tear** — "ultrasound is first-line in Australia". Correct. Missing: **subacromial steroid injection more than twice a year is associated with tendon rupture** and should be limited; this is a common AU exam point. Minor edit.

- **Achilles tendinopathy** — "Simmond (Thompson) test" - both eponyms correct. All correct.

- **Angioedema** — "bradykinin-mediated (HAE, ACE-I) - C1-INH concentrate or icatibant". Correct for HAE. But **ACE-inhibitor angioedema does NOT reliably respond to icatibant either** (per ARC trial 2015 which was negative for icatibant vs standard care in ACE-I angioedema) - it is a bradykinin mechanism but the acute treatment evidence is weaker. Support of airway, cease ACE-I, and observation is the mainstay; icatibant may be considered but is off-label. Suggested rewrite:
  `Bradykinin-mediated: for HAE, IV C1-INH concentrate or SC icatibant. For ACE-inhibitor angioedema, definitive treatment is airway support and stopping the drug - icatibant evidence is negative (ARC 2015) but sometimes used off-label; C1-INH concentrate has limited evidence. Never rechallenge with any ACE inhibitor or ARB.`
  Sources: [ARC trial NEJM 2015 - icatibant negative in ACE-I angioedema](https://www.nejm.org/doi/full/10.1056/NEJMoa1414840)

- **Hereditary angioedema** — "lanadelumab (PBS-listed)". Correct (PBS 2020). Missing: **berotralstat (oral plasma kallikrein inhibitor)** is now TGA-approved and **PBS-listed since 2023** as an oral prophylactic alternative to injectable lanadelumab or C1-INH. Suggested addition:
  `Long-term prophylaxis with lanadelumab (PBS-listed 2020, SC monthly), berotralstat (oral daily, PBS-listed 2023) or C1-INH concentrate; danazol older option with androgenic side effects. Avoid oestrogens and ACE inhibitors.`
  Sources: [PBS berotralstat](https://www.pbs.gov.au); [HAE Australasia guidelines]

- **Optic neuritis** — "oral prednisolone alone is contraindicated (raises recurrence)". This is the classic ONTT finding (1992) and is correct historically, though modern re-analyses (2023) suggest the recurrence-risk finding was likely a chance result and oral **high-dose prednisolone (1 g equivalent)** is acceptable per modern MS neurology guidance. AU practice still typically uses IV methylprednisolone for typical ON. Minor - the summary is defensible.

- **Uveitis** — All correct. Minor: **HLA-B27 anterior uveitis is the commonest identifiable cause of anterior uveitis in AU adults** (30-40% of recurrent) - worth stating explicitly for clinical anchoring.

### MINOR issues

- **ANCA-associated vasculitis** — All accurate. Minor: **avacopan (C5a receptor antagonist)** is PBS-listed for AAV since 2023 as steroid-sparing induction adjunct (ADVOCATE trial) - could be added.

- **Ankylosing spondylitis** — "IL-17 (secukinumab)" - **ixekizumab, upadacitinib (JAK)** also PBS-listed for AxSpA in AU. Minor addition.

- **Behçet disease** — "immunosuppression preferred over anticoagulation for inflammatory thrombi" - correct AU/EULAR. Fine.

- **Chilblains** — "nifedipine slow-release for recurrent disease" - correct. **Nifedipine 20 mg BD** dose worth adding for specificity.

- **Dermatomyositis** — "adult disease carries markedly raised malignancy risk, highest in the first 3 years - CT chest, abdomen and pelvis plus age-appropriate screening". Correct. **Anti-TIF1-gamma** is the strongest predictor of malignancy - already stated. Fine.

- **Ehlers-Danlos syndrome** — All accurate. Vascular EDS "median survival 48 years" is often quoted but 2020 data suggest **older median (mid-50s) with celiprolol and modern management** - close enough at summary level.

- **Eosinophilic granulomatosis with polyangiitis** — "mepolizumab (anti-IL-5) is steroid-sparing" - correct (MIRRA trial; PBS-listed for EGPA 2020). "Leukotriene receptor antagonists were wrongly blamed - vasculitis was already present" - correct, this is the modern understanding. Fine.

- **Fibromyalgia** — "opioids do not and cause harm" - correct AU/RACGP. Fine.

- **Granulomatosis with polyangiitis** — All correct. Same avacopan comment as AAV.

- **Henoch-Schönlein purpura / IgA vasculitis** — Two entries covering same condition (HSP is the old name for IgA vasculitis). Content is largely consistent. Minor: **prednisolone does not prevent renal disease** - correctly stated in both. IgA vasculitis entry says "avoid NSAIDs if renal" - good AU point.

- **Juvenile idiopathic arthritis** — All correct. Minor: **tocilizumab or IL-1 inhibitor (anakinra, canakinumab) for systemic JIA** - anakinra correctly listed. Fine.

- **Marfan syndrome** — "elective aortic root replacement at 50 mm" - correct (Ghent, ACC/AHA). Minor: **women planning pregnancy** are often offered prophylactic root replacement at **45 mm** given dissection risk in pregnancy. Add.

- **Microscopic polyangiitis** — All correct.

- **Osteogenesis imperfecta** — All correct. Minor: **denosumab now used off-label in some paediatric OI centres** as bisphosphonate alternative (Ontario/Melbourne data). Not standard AU - fine to omit.

- **Polyarteritis nodosa** — "hepatitis B in around 30%" - historically true but AU-vaccinated population it is now much lower (~5-10%). Regional variability. Fine at summary level.

- **Polymyalgia rheumatica** — "prednisolone 12.5-25 mg daily, tapered over 12-24 months". Correct AU (2015 ACR/EULAR endorsed by ARA). Minor: **tocilizumab now considered** in refractory or steroid-toxic PMR (SEMAPHORE trial 2023) - could add.

- **Polymyositis** — All correct. Minor: **immune-mediated necrotising myopathy (IMNM) with anti-HMGCR is now recognised as distinct entity** and correctly mentioned.

- **Pseudogout / CPPD** — "check ferritin, calcium, PTH and magnesium for haemochromatosis, hyperparathyroidism and hypomagnesaemia" - correct workup for young/atypical. Fine.

- **Psoriatic arthritis** — All correct. **Guselkumab (IL-23)** PBS-listed for PsA - already implied. Fine.

- **Reactive arthritis** — All correct.

- **Sarcoidosis** — "ACE (supportive not diagnostic)" - correct. Fine.

- **Scleroderma / Systemic sclerosis** — Two overlapping entries (essentially the same disease). Both accurate. Consider merging or cross-linking - Rob-flagged duplicate.

- **Sjögren syndrome** — All correct. **Fetal cardiac block risk with anti-Ro** is a critical AU O&G teaching point - correctly stated.

- **Takayasu arteritis** — All correct.

- **Vasculitis (umbrella)** — Correct classification. Fine as an umbrella entry.

- **Autoinflammatory diseases** — Correct. Minor: **ganirelix/anakinra dosing** and **PFAPA tonsillectomy option** worth noting - fine at summary level.

- **Livedoid vasculopathy** — Correct. Minor: DOAC-first-line evidence (rivaroxaban) is off-label in AU but standard practice - correctly stated.

- **Adhesive capsulitis** — All correct. "Loss of passive range distinguishes frozen shoulder from rotator cuff" - key teaching point.

- **Fibromyalgia** — All correct.

- **Acne vulgaris** — "never use an antibiotic without benzoyl peroxide or a retinoid alongside - monotherapy breeds resistance and eTG advises against it". Correct AU/eTG. Minor: **doxycycline max 3 months** to limit resistance is worth adding; **spironolactone 25-100 mg/day for adult female acne** is now first-line hormonal option per AU dermatology - not currently mentioned.

- **Androgenetic alopecia** — "oral spironolactone 100-200 mg for women" - correct AU dose. **Oral minoxidil 0.25-2.5 mg** is now widely used off-label in AU for both sexes since 2022 - add.

- **Bowen's disease** — All correct.

- **Bullous pemphigoid** — See substantive; add dupilumab.

- **Contact dermatitis** — All correct.

- **Dermatitis herpetiformis** — All correct.

- **Eczema (atopic dermatitis)** — "Note: undertreatment through steroid phobia causes more harm than appropriate steroid use". Excellent AU teaching point. Missing: **dupilumab PBS-listed** for severe adult and adolescent atopic dermatitis since 2021 (paediatric extension 2023 for ≥6 months). **Upadacitinib and abrocitinib (JAK)** also PBS-listed. Add.

- **Erythema nodosum** — "chest X-ray in essentially everyone - sarcoidosis and tuberculosis both present this way and are otherwise missed" - correct.

- **Hereditary angioedema / Angioedema** — See substantive.

- **Impetigo** — "amoxicillin 15 mg/kg TDS" - wait, the entry says cephalexin or dicloxacillin, not amoxicillin. Correct. "PSGN even after eradication - urinalysis 3 to 6 weeks later in the at-risk". Correct AU teaching. Fine. Minor: **community-associated MRSA in remote NT** - clindamycin OR trimethoprim-sulfamethoxazole first-line per CARPA - correctly noted.

- **Lichen simplex chronicus** — All correct.

- **Melasma** — See substantive.

- **Psoriasis** — Fine but missing biologic list update: **risankizumab, guselkumab (IL-23), tildrakizumab, ixekizumab, secukinumab (IL-17), bimekizumab, brodalumab** all PBS-listed. Summary says "biologics per PBS" - defensible. Minor: **avoid systemic steroids** (pustular rebound) - correctly stated.

- **Pyoderma gangrenosum** — All correct. **Avoid debridement (pathergy)** - key teaching.

- **Rosacea** — "topical corticosteroids exacerbate rosacea - do not use" - important AU teaching. Fine.

- **Roseola infantum** — All correct.

- **Scabies** — "topical permethrin 5% neck-down for 8-12 hours, repeated at day 7" - correct AU Healthy Skin Guideline. Minor: for infants **<2 months and pregnancy** use permethrin cautiously; **ivermectin contraindicated <15 kg or <5 years and in pregnancy**. Add.

- **Seborrhoeic dermatitis** — Correct. Minor spelling (US "Seborrheic" vs UK/AU "Seborrhoeic") in the entry name - Rob may want to normalise across the deck.

- **Squamous cell carcinoma** — See substantive.

- **Stevens-Johnson syndrome** — See substantive.

- **Tinea** — "oral terbinafine 6 weeks fingernails, 12 weeks toenails, with LFT check". Correct. Minor: **pulse itraconazole** is an AU alternative for onychomycosis.

- **Urticaria** — "up-titrated to four times standard dose if needed; omalizumab if refractory". Correct per EAACI/AUS 2022. Fine.

- **Vitiligo** — "Ruxolitinib topical for non-segmental facial disease". Correct - TGA-approved 2023 but **not PBS-listed** (private, ~$1000/month). Add PBS caveat.

- **Acoustic neuroma** — All correct.

- **Allergic rhinitis** — See substantive.

- **BPPV** — "Vestibular suppressants (prochlorperazine, betahistine) delay recovery and are not indicated" - correct AU teaching.

- **Epistaxis** — All correct.

- **Meniere disease** — See substantive above.

- **Otitis externa / Otitis media / Sinusitis** — See substantive.

- **Vestibular neuritis** — "oral prednisolone 1 mg/kg tapering over 3 weeks started within 3 days improves vestibular recovery (Cochrane)". Correct but note the Cochrane conclusion is **insufficient evidence** (2011, updated 2023) - the vestibular recovery benefit is a signal, not a definite outcome. Fine as stated.

- **Acute angle-closure glaucoma** — All correct.

- **Cataract** — All correct. Minor: **immersion vs contact biometry** and **IOL calculation** - too detailed for a summary.

- **Central retinal artery occlusion** — See substantive.

- **Central retinal vein occlusion** — All correct.

- **Conjunctivitis** — "chloramphenicol 0.5% drops 4 times daily with 1% ointment at night for 5 to 7 days (eTG)". Correct AU. Minor: **most bacterial conjunctivitis resolves without antibiotics** - AU practice increasingly defers antibiotics for mild non-purulent cases (eTG 2023). Add.

- **Diabetic retinopathy** — See substantive.

- **Glaucoma** — "selective laser trabeculoplasty" - now considered **first-line before eye drops** per LiGHT trial (2019) and increasingly AU practice. Reasonable to elevate SLT.

- **Macular degeneration** — All correct. Minor: **faricimab (dual anti-VEGF/anti-Ang2)** PBS-listed for wet AMD since 2023 - already listed. **AREDS2 vitamins for intermediate dry AMD** - correct.

- **Ophthalmoplegia** — "posterior communicating artery aneurysm until proven otherwise" for mydriatic third nerve palsy - excellent AU teaching point.

- **Optic neuritis** — See minor above.

- **Papilloedema** — See substantive.

- **Retinal detachment** — See substantive.

- **Retinopathy of prematurity** — "SpO2 target 90-95%, not higher - SUPPORT and BOOST-II" - correct.

- **Uveitis** — See substantive.

- **Compartment syndrome** — See substantive.

- **DDH / Perthes / SCFE** — See substantive/minor above.

- **Hip fracture** — See minor above.

- **Osgood-Schlatter** — All correct.

- **Plantar fasciitis** — All correct.

- **Rotator cuff tear** — See minor above.

- **Spinal fracture** — All correct.

- **Achilles tendinopathy** — All correct.

- **Delirium** — See substantive above.

- **Urinary incontinence** — See substantive above.

- **Gout** — See substantive.

- **Rheumatic fever** — See substantive.

### DUPLICATE / OVERLAPPING entries

- **Scleroderma** and **Systemic sclerosis** are the same disease (scleroderma being the older / cutaneous-focused synonym for systemic sclerosis). Both entries substantially overlap on CREST, ILD, PAH and renal crisis. Recommend merging into one entry titled **Systemic sclerosis (scleroderma)** with the shared content.

- **Henoch-Schönlein purpura** and **IgA vasculitis** are the same condition (HSP renamed IgA vasculitis by the 2012 Chapel Hill nomenclature). Both entries are consistent but redundant. Recommend merging into **IgA vasculitis (Henoch-Schönlein purpura)** as the alias key.

- **Angioedema** and **Hereditary angioedema** overlap significantly on bradykinin mechanism, C1-INH testing and icatibant/C1-INH treatment. Reasonable to keep both (angioedema as umbrella, HAE as specific) but ensure they cross-reference and do not contradict.

### AU-SPECIFIC additions to strengthen

- **Kawasaki disease** — Add note that **Aboriginal and Torres Strait Islander children have higher incidence** (per RCH/Nossal Institute epidemiology) and that **Pasifika ancestry** predicts higher IVIG resistance.

- **Gout / SCFE / Rheumatic fever / Scabies / Impetigo** — all correctly identify Aboriginal and Torres Strait Islander disproportionate burden. Good.

- **Diabetic retinopathy** — Already notes leading working-age blindness cause in Australia. Could add **KeepSight** program (Diabetes Australia national screening register).

- **AMD** — Could add **Macular Disease Foundation Australia** as patient resource.

- **AR** — Add **AusPollen (University of Melbourne)** grass pollen monitoring as patient tool.

- **Skin cancer entries** (BCC, SCC, Bowen, AK missing from bank - AK could be added later) — all correctly emphasize AU highest-incidence context.

### RECOMMENDED NEW ENTRIES (identified as missing from bank in scope)

- **Actinic keratosis** — pre-malignant, common Australian GP presentation, PBS-listed treatments (imiquimod, 5-FU, cryotherapy, PDT). No entry in the 686.
- **Melanoma** — deferred, may be in oncology bank; if not present, add given AU context.
- **Hidradenitis suppurativa** — PBS-listed adalimumab, secukinumab (2024); no entry.
- **Antiphospholipid syndrome** — covered in chronic-first-lines audit but no rheum-side clinical entry visible in the scope pull.
- **Otitis media with effusion (glue ear)** — subsumed under OM entry but worth its own entry given hearing loss / speech delay implications.
- **Sudden sensorineural hearing loss** — flagged in Meniere entry but no standalone entry; time-critical (steroids within 14 days).
- **Actinic cheilitis / lip SCC risk** — AU sun-safety.
- **Nasal polyps** — biologics (dupilumab, mepolizumab, omalizumab) PBS-listed.
- **Bell palsy** — likely in neuro batch, worth confirming.
- **Vertigo (approach)** — differential and HINTS - partially covered by vestibular neuritis entry.
- **Falls in older adults** — geriatric.
- **Pressure injury (staging)** — geriatric.
- **Frailty (Clinical Frailty Scale)** — geriatric.
- **End-of-life care / anticipatory medications** — palliative.
- **Advance care planning** — palliative.
- **Deprescribing** — flagged as covered in batch 57 but worth verifying it exists.

### VERDICT

Substantive rewrites (14): Kawasaki, GCA, lupus nephritis, SLE, rheumatic fever (secondary prophylaxis duration), gout, compartment syndrome, retinal detachment (technique emphasis), CRAO (pathway urgency), diabetic retinopathy (screening interval / BP target), SCC margins, SJS (etanercept / ciclosporin), melasma (hydroquinone scheduling), ACE-I angioedema (icatibant evidence). Plus BP, otitis externa/media/sinusitis eTG dose refinements, delirium antipsychotic dose caveat, and incontinence antimuscarinic hierarchy.

Duplicate collapse recommended for: Scleroderma / Systemic sclerosis; HSP / IgA vasculitis.

Missing high-yield entries recommended: Actinic keratosis; Hidradenitis suppurativa; OME (glue ear); Sudden SNHL; Nasal polyps; Falls; Pressure injury; Frailty scale; End-of-life anticipatory meds; Advance care planning.

Overall accuracy of the 97 entries is high (~85%): most errors are guideline-drift (2023-2025 updates to PBS listings, KDIGO 2024 lupus, BSR 2020 GCA, Cancer Council AU 2024 keratinocyte, ARF/RHD 2020 prophylaxis durations) rather than factual errors. Rob-flagged AU-specific points (CHA2DS2-VA, HLA-B*5801 in Aboriginal and Torres Strait Islander for allopurinol, ARF endemic in northern AU, KeepSight, ANZHFR) are largely honoured; a few would benefit from explicit AU signposting.
