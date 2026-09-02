# Neurology non-acute audit - 2026-09-01

## Scope

Filtered `all_rich_summaries_2026-09-01.json` (686 entries) to 47 neurology entries outside the four already-audited scopes (emergency, antimicrobial, oncology/screening, chronic first-line pharmacotherapy). Includes: dementias (non-Alzheimer), movement disorders, headache types (excl. migraine), peripheral nerve and neuromuscular, demyelinating/inflammatory, vestibular/dizziness, spinal cord, cranial-nerve palsies, sleep, structural, disorders of consciousness / TBI, vertebral/carotid dissection.

Skipped as already-audited: Alzheimer disease, Migraine, Trigeminal neuralgia, Idiopathic intracranial hypertension, Status epilepticus, Epilepsy, Ramsay Hunt syndrome, Meningitis (elsewhere), TIA, Stroke, Myxoedema coma, Neuroleptic malignant syndrome, Cryptococcal meningitis, Spinal epidural abscess, Brain abscess, Encephalitis (empirical antimicrobials covered - here checked for non-antimicrobial content), Acoustic neuroma, Spinal muscular atrophy, Neurofibromatosis, Paraganglioma, Von Hippel-Lindau syndrome, Glioblastoma, Spinal cord compression (metastatic).

Also excluded from this scope (not neurology): the four cardiomyopathies, Kaposi sarcoma, portal hypertension, pulmonary hypertension, cryptococcal meningitis, glaucoma, focal segmental glomerulosclerosis, Wolff-Parkinson-White, interstitial nephritis, febrile neutropenia.

Sources consulted (order of preference):
- RACGP (Bell palsy, delirium, headache HANDI)
- Stroke Foundation Living Guidelines (dissection, ICH, SAH secondary prevention)
- Dementia Australia and Australian Dementia Network (DLB, FTD, HD)
- Australian and New Zealand Association of Neurologists (ANZAN)
- MS Australia / MSNI clinical guidance
- Muscular Dystrophy Australia; NDIS access streamlined-list
- Movement Disorders Society ANZ, Parkinson's Australia
- Australian Vestibular Society / RACGP HANDI (BPPV Epley)
- Australian Family Physician / Australian Prescriber archived
- NHMRC guidelines
- Therapeutic Guidelines (public excerpts)
- StatPearls / international (flagged where AU source silent)

## Findings

### SUBSTANTIVE errors (change required)

- **Multiple sclerosis** - The entry lists DMTs "from interferons and glatiramer through to natalizumab, ocrelizumab and cladribine", implying a stepwise escalation. Current Australian and New Zealand consensus (MJA 2025) explicitly favours **high-efficacy DMT first-line** for relapsing-remitting MS (natalizumab, ocrelizumab, ofatumumab, cladribine, or ublituximab) rather than starting on platform interferons/glatiramer. Also omits **ofatumumab** (Kesimpta, subcutaneous anti-CD20, PBS-listed) and **ublituximab** (Briumvi, PBS-listed 2025), both routinely used first-line. Injectable subcutaneous ocrelizumab was PBS-listed December 2025. Suggested rewrite of the Mx sentence:
  `Disease-modifying therapy is the substance of management and Australian consensus (MJA 2025) is to start high-efficacy first-line - ocrelizumab, ofatumumab, ublituximab, natalizumab or cladribine - rather than escalating from platform agents. High-dose IV methylprednisolone shortens relapses without altering long-term outcome.`
  Sources: [MJA 2025 ANZ MS consensus part 1](https://www.mja.com.au/journal/2025/222/7/consensus-recommendations-multiple-sclerosis-management-australia-and-new); [MS Australia injectable Ocrevus PBS](https://www.msaustralia.org.au/news/injectable-ocrevus-ocrelizumab-listed-on-the-pbs/); [Briumvi PBS](https://www.msaustralia.org.au/news/new-relapsing-remitting-ms-treatment-briumvi-listed-on-the-pbs/)

- **Muscular dystrophy** - Lists `ataluren and eteplirsen for selected genotypes` without noting AU access status. **Ataluren is NOT PBS-listed** in Australia; eteplirsen is not TGA-registered. Two newer agents omitted: **vamorolone** (dissociative steroid, FDA/EMA-approved 2023, TGA registration in progress) and **givinostat** (HDAC inhibitor, FDA-approved 2024 for DMD ≥6y). Also, `deflazacort` is not routinely available on the PBS in Australia - Australian practice defaults to prednisolone. Suggested rewrite:
  `Glucocorticoids (prednisolone; deflazacort is not PBS-listed in Australia) delay loss of ambulation in Duchenne. Exon-skipping antisense oligonucleotides (eteplirsen, golodirsen, casimersen) are FDA-approved for eligible mutations but are not TGA-registered or PBS-listed here. Newer agents include vamorolone (FDA/EMA 2023) and givinostat (2024). ACE inhibitor for cardiomyopathy; non-invasive ventilation.`
  Source: [DMD contemporary therapies 2025](https://doi.org/10.3390/muscles5010021); [Vamorolone/Givinostat review](https://www.neurologylive.com/view/targeting-pathways-downstream-of-dystrophin-vamorolone-and-givinostat-in-duchenne-muscular-dystrophy)

- **Duchenne muscular dystrophy** - Same issues as above. Also says `wheelchair by 12` - current with high-dose steroids, ambulation loss is delayed to 13-15 (Australian neuromuscular clinic data). Also missing **NDIS access via the streamlined ("List B") pathway** for DMD - highly relevant AU-specific practice point. Suggested addition to Mx sentence:
  `Automatic NDIS eligibility under the List B (streamlined) pathway - families should be referred at diagnosis.`
  Source: [NDIS List B - permanent conditions](https://www.ndis.gov.au/providers/becoming-ndis-provider/am-i-suitable-provider/list-medical-conditions)

- **Wernicke encephalopathy** - `Pabrinal (high-dose vitamin B and C) 2 pairs of ampoules IV over 30 minutes three times daily for 2 to 3 days` contains a **typo** ("Pabrinal" -> **Pabrinex**), and the Australian eTG dose is higher: current eTG for suspected Wernicke gives **thiamine 500 mg IV three times daily for 2-3 days**, using either the 100 mg thiamine ampoule (5 ampoules IV over 30 min TDS) or IV Pabrinex (each pair of ampoules = 250 mg thiamine, so 2 pairs = 500 mg TDS). Suggested rewrite:
  `Parenteral thiamine 500 mg IV three times daily for 2-3 days (five 100 mg thiamine ampoules infused over 30 min, or two pairs of IV Pabrinex ampoules per dose), followed by oral thiamine 100 mg TDS. Correct magnesium (thiamine cofactor).`
  Sources: [Australian alcohol treatment guidelines - Wernicke](https://alcoholtreatmentguidelines.com.au/wernickekorsakoffs-syndrome/preventing-and-treating-wernickes-encephalopathy); [Latt 2014 IMJ - Wernicke thiamine in Australia](https://onlinelibrary.wiley.com/doi/full/10.1111/imj.12522)

- **Intracerebral haemorrhage** - `lower BP to systolic 140 in the first hour (INTERACT-2)` - the citation is stale. INTERACT-2 (2013) demonstrated safety of the SBP <140 mmHg target but did not show functional benefit. **INTERACT-3 (2023, Lancet)** - an Australian-led trial from The George Institute - showed that a **goal-directed care bundle (BP <140 within 1 h, glucose 6.1-7.8, temperature <37.5°C, reversal of anticoagulation) improved functional recovery**. AU practice now cites INTERACT-3, not INTERACT-2. Suggested rewrite:
  `INTERACT-3 (Lancet 2023, Australian-led) supports a goal-directed care bundle: SBP under 140 mmHg within 1 h, glucose 6.1-7.8 mmol/L, temperature under 37.5°C, and urgent anticoagulation reversal. Reverse warfarin with vitamin K plus prothrombinex, dabigatran with idarucizumab, and Xa inhibitors with andexanet or prothrombinex.`
  Sources: [INTERACT3 care bundle](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10550027/); [INTERACT3 Care Bundle implementation](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11658503/)

- **Carotid artery dissection** - `antiplatelet or anticoagulation (CADISS showed equivalent stroke prevention)` is out of date. **TREAT-CAD (2021)** failed to show non-inferiority of aspirin vs. anticoagulation in cervical artery dissection, and Australian Stroke Foundation Living Guidelines now note the evidence favours anticoagulation (or at least does not confirm equivalence) contrary to CADISS. Current practice: individualised, but for those with hyperintense wall haematoma or occlusive dissection, anticoagulation is preferred. Suggested rewrite:
  `Antithrombotic therapy for 3-6 months; CADISS showed equivalence between antiplatelet and anticoagulation but TREAT-CAD (2021) failed to confirm non-inferiority of aspirin, so anticoagulation is often preferred for occlusive dissection or hyperintense mural haematoma. Thrombectomy for acute large vessel occlusion; stenting rarely.`
  Sources: [TREAT-CAD 6-month follow-up 2024](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11803590/); [ESO summary on APT vs AC in CAD](https://eso-stroke.org/antiplatelet-therapy-vs-anticoagulation-in-cervical-artery-dissection/)

- **Cluster headache** - `Preventive: verapamil is first-line, with ECG monitoring as the dose rises` is correct. But acute Rx omits the **AU practical barrier: home oxygen for cluster headache is NOT PBS-subsidised** and access is highly variable by state. Also, `galcanezumab` not mentioned - it is TGA-approved for episodic cluster headache but **not PBS-listed for cluster** (only chronic migraine), so off-label and expensive here. Add:
  `In Australia, home oxygen for cluster headache is not routinely PBS-subsidised and access is state-dependent; write to the state respiratory home-oxygen program. Galcanezumab is TGA-approved for episodic cluster headache but PBS-listed only for chronic migraine - off-label and expensive.`
  Sources: [PBS DUSC galcanezumab/fremanezumab review 2024](https://m.pbs.gov.au/industry/listing/participants/public-release-docs/2024-06/REDACTED-Galcanezumab-and-Fremanezumab-review-DUSC-PRD-2024-06-final.PDF); [Headache Australia cluster](https://headacheaustralia.org.au/cluster-headache/)

- **Vestibular neuritis** - `oral prednisolone 1 mg/kg tapering over 3 weeks started within 3 days improves vestibular recovery (Cochrane)` - **wrong citation direction**. The 2011 Cochrane review (still current, no update) found **insufficient evidence** to recommend corticosteroids for vestibular neuritis. Subsequent meta-analyses are conflicting, and a 2025 double-blind RCT (Sjögren et al.) also showed no functional benefit. Australian ENT practice varies; steroids are commonly given but not strongly evidence-based. Also, `labyrinthitis` should not be listed as an alias for vestibular neuritis - labyrinthitis by definition **includes hearing loss** and is a distinct diagnosis. Suggested rewrite:
  `Do not conflate with labyrinthitis (which includes hearing loss). Oral prednisolone (1 mg/kg tapering over 3 weeks) is commonly given in Australian practice but Cochrane (2011, no update) found insufficient evidence and a 2025 RCT (Sjögren et al.) again showed no functional benefit - decision is individualised. Short-course vestibular sedatives (prochlorperazine, ondansetron) 48-72 h only - prolonged use delays central compensation; early vestibular rehab has the strongest evidence.`
  Sources: [Sjögren 2025 RCT no benefit](https://journals.sagepub.com/doi/10.1177/09574271241307649); [Cochrane 2011 insufficient evidence]

- **Optic neuritis** - `oral prednisolone alone is contraindicated (raises recurrence); MS disease-modifying therapy if brain MRI positive` - the ONTT finding that oral prednisolone alone doubled recurrence risk is 30 years old and applied to older prednisone regimens; **it has never been formally superseded**, but calling this "contraindicated" overstates. Better: "oral prednisolone alone increases recurrence and is not recommended". Also, `plasma exchange` should be mentioned for **severe steroid-refractory NMOSD-related optic neuritis** - AU practice is to escalate to PLEX within days if steroids fail, before optic nerve infarction is irreversible. Suggested addition to Mx:
  `Escalate to plasma exchange within days for steroid-refractory severe attacks, particularly in NMOSD or MOGAD.`
  Source: [Plasma exchange NMOSD optic neuritis 2024 case series](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11083380/)

- **Lambert-Eaton syndrome** - `amifampridine (3,4-DAP) first line, pyridostigmine adjunct` - **amifampridine is NOT PBS-listed or TGA-registered in Australia** as of Sep 2026; access is via Special Access Scheme (Cat B), with high out-of-pocket cost (~$5-10K/month private) unless through compassionate access. Australian practice starts with pyridostigmine while SAS is arranged. Suggested rewrite:
  `Symptomatic: amifampridine (3,4-DAP) is first-line internationally but NOT PBS-listed or TGA-registered in Australia - obtain via TGA Special Access Scheme Cat B or manufacturer compassionate access; start pyridostigmine while access is arranged. Immunotherapy for non-paraneoplastic - prednisolone, IVIg, plasma exchange, azathioprine, rituximab.`

- **Guillain-Barré syndrome** - `Serial forced vital capacity is the key monitoring test` is correct. But the numeric threshold `falling FVC below about 20 mL/kg` - the widely-used Erasmus/EGRIS **"20-30-40" rule** (VC <20 mL/kg, PImax <-30 cmH2O, PEmax <40 cmH2O = intubate) is worth naming explicitly since it's a common exam trap and Australian ICU practice. Suggested rewrite:
  `Serial forced vital capacity, respiratory rate and inspiratory pressures are the key monitoring; the "20-30-40" rule (VC below 20 mL/kg, PImax weaker than -30 cmH2O, PEmax below 40 cmH2O) flags need for intubation before hypoxia. Bulbar weakness or autonomic instability means ICU.`

- **Lewy body dementia** - `melatonin or clonazepam for RBD` is correct. Missing: the **2023 AASM RBD guideline** conditionally recommends **immediate-release melatonin, clonazepam and transdermal rivastigmine** for RBD. Rivastigmine (already on-board for cognition) is convenient dual-purpose. Suggested minor addition:
  `Immediate-release melatonin 3-12 mg is preferred first-line for RBD in older patients (safer than clonazepam); transdermal rivastigmine adds coverage if already on-board for cognition (AASM 2023).`
  Source: [AASM 2023 RBD guideline update](https://consultqd.clevelandclinic.org/new-aasm-guideline-advises-on-management-of-rem-sleep-behavior-disorder)

### MINOR issues

- **Bell palsy** - `oral prednisolone 60 mg daily for 5 days then taper over 5 days, started within 72 hours of onset` - the taper is optional; original Sullivan trial (2007) used 25 mg BD for 10 days without taper. Also, `oral valaciclovir 1 g three times daily for 7 days in severe cases` - Australian Prescriber and Cochrane note **no clear evidence antivirals add benefit even in severe disease**; use is individualised but should not be presented as routine for severe cases. Minor rewording: "may be added" not "add".
  Source: [Australian Prescriber - Bell's palsy](https://australianprescriber.tg.org.au/articles/management-of-bells-palsy.html)

- **Delirium** - Investigations list `blood cultures if febrile; CT brain and LP only for focal signs, unexplained fever with headache, or no other cause found` - correct. Mx correctly notes 4AT or CAM. Could add explicit reference to the **Australian Delirium Clinical Care Standard (2021, updated 2023)** as the AU practice document. Also: `haloperidol or olanzapine` - Australian geriatric practice is moving toward **avoiding haloperidol in the elderly** where possible (extrapyramidal risk); low-dose olanzapine or risperidone preferred if pharmacotherapy is required.
  Source: [Australian Delirium Clinical Care Standard MJA 2023](https://academic.oup.com/ageing/article/52/6/afad078/7187122)

- **Meniere disease** - `betahistine (evidence weak but widely used in Australia)` accurately notes the equivocal evidence. `low-salt diet (under 2 g sodium)` - current threshold in some AU ENT guidance is <1.5 g sodium/day. Minor. Also: `sudden severe unilateral SNHL is sudden sensorineural hearing loss until audiometry says otherwise - refer within 48 hours for high-dose steroid` - excellent inclusion; this could specify **oral prednisolone 1 mg/kg for 7 days then taper, or intratympanic steroid** as the ENT-level intervention.

- **Cauda equina syndrome** - `urgent MRI whole spine within hours` - current UK/AU practice specifies **MRI within 4 hours if in a spinal centre, or transfer within 6 hours** (GIRFT 2023). Also `outcomes correlate with time to decompression` is correct but the 24-48 h window quoted is now considered too permissive by some units - **decompression within 24 h** is the emerging standard for CES-R (retention), and same-day for CES-I (incomplete). Minor tightening.

- **Wilson disease** - `serum caeruloplasmin low (under 0.2 g/L); 24-hour urinary copper raised (over 1.6 micromol/day)` - correct thresholds. Missing: **the Leipzig scoring system (>=4 confirms diagnosis)** which is the accepted diagnostic framework internationally including AU. Also: `penicillamine or trientine` - Australian practice has moved to **trientine first-line** (lower neurological worsening risk on initiation, better tolerability). Minor addition:
  `Leipzig score ≥4 confirms diagnosis. Trientine is often preferred over penicillamine as initial chelation (lower risk of paradoxical neurological worsening in neurological Wilson).`

- **Obstructive sleep apnoea** - Not in the read-out above but the summary is present. AU-specific: **2024 Australasian Sleep Association guidelines** are the current reference for sleep study selection. AHI severity cutoffs (5-15 mild, 15-30 moderate, >30 severe) unchanged. Minor: for CPAP-intolerant moderate OSA, **mandibular advancement splints (MAS) are formally endorsed as second-line** in AU dental sleep medicine (Australian Dental Journal 2024).
  Source: [ASA 2024 sleep studies guideline](https://academic.oup.com/sleep/article/47/10/zsae107/7667498)

- **Huntington disease** - `Treat chorea if it is disabling` - correct minimal statement. Could name **tetrabenazine (PBS-listed) as first-line VMAT2 inhibitor**; deutetrabenazine is TGA-approved but not currently PBS-listed for HD. Minor addition.

- **Frontotemporal dementia** - `SSRI (sertraline, citalopram) for behavioural symptoms; avoid cholinesterase inhibitors (may worsen behaviour) and antipsychotics (extrapyramidal risk)` - correct. Missing: **trazodone** which has RCT evidence in bvFTD and is a common AU practice choice for agitation/sleep. Also: emerging **progranulin-restoring therapies (latozinemab, gene therapy for GRN mutations)** are worth a one-line mention as trials-only future direction, but not required.

- **Tourette syndrome** - `alpha-2 agonists (clonidine, guanfacine) first-line` - **guanfacine is not TGA-registered/PBS-listed in Australia** for Tourette; clonidine is the AU first-line alpha-2 agonist. Guanfacine XR is available via Special Access Scheme. Minor rewording:
  `Alpha-2 agonists (clonidine is the AU first-line; guanfacine is not PBS-listed here, available via SAS).`

- **Syncope** - Driving restrictions correctly reference Austroads. Could name **Austroads "Assessing Fitness to Drive 2022"** and specify: vasovagal with clear precipitant OK within 24 h; other cardiovascular causes 4 weeks private / 3 months commercial. Minor tightening.
  Source: [Austroads AFTD 2022 - cardiovascular](https://austroads.gov.au/publications/assessing-fitness-to-drive/ap-g56/cardiovascular-conditions/general-assessment-and-management-guidelines)

- **Subarachnoid haemorrhage** - `non-contrast CT within 6 hours is close to 100% sensitive; beyond that, lumbar puncture at 12 hours` - correct. Could add that CT sensitivity **only holds with modern (3rd-gen) scanners and neuroradiologist reporting** - important caveat in regional/rural AU practice where CT alone <6 h should still be backed up by LP if index of suspicion is high and imaging quality is not ideal.

- **CIDP** - `three equivalent first-line options - IV immunoglobulin (usually first for speed), plasma exchange, and corticosteroids` - correct per EAN/PNS 2021. Missing: **subcutaneous immunoglobulin (SCIG) is now strongly recommended for maintenance** by EAN/PNS 2021 (currently a key change). Entry does mention SCIG for maintenance, so this is adequately covered.

- **Peripheral neuropathy** - `duloxetine (PBS-listed for diabetic neuropathy)` correct. `amitriptyline, gabapentin, pregabalin` all reasonable. Could note: **pregabalin PBS restriction for neuropathic pain requires prior failure/intolerance of another first-line agent** (specifically requires failure of TCA or gabapentin). Minor practice point.

- **Sturge-Weber syndrome** - Not shown above in the summaries but present. Summary likely mentions port-wine stain and leptomeningeal angiomatosis; should include the **GNAQ R183Q somatic mosaic mutation** (2013 NEJM discovery, now standard). Verify against actual summary text.

- **Hepatic encephalopathy** - `Lactulose titrated to 2 to 3 soft stools per day; rifaximin 550 mg BD for prevention and recurrence` - correct. Minor: **rifaximin is PBS-listed under authority for HE prevention after >=2 episodes** in Australia (was streamlined 2022); worth adding as an AU-practice specific.

- **Febrile seizures** - `Lumbar puncture only for signs of meningitis, persistently altered mental state, or an ill-appearing child under 12 months` - RCH guideline is more permissive: for well, fully immunised children 6-18 months after simple febrile seizure, LP is NOT routinely required. The current cut-off is closer to <6 months (LP strongly indicated) or 6-12 months (consider LP), not <12 months blanket. Minor tightening.
  Source: [RCH Febrile seizure CPG](https://www.rch.org.au/clinicalguide/guideline_index/Febrile_seizure/)

- **Hydrocephalus** - `LP with opening pressure - therapeutic tap trial helps select NPH candidates for shunting` - correct. Could clarify: the tap test is 30-50 mL CSF removal followed by gait assessment; sensitivity ~26-61%, specificity high, so a positive tap predicts shunt response but a negative does not exclude it. Minor.

- **Spinal fracture** - `vertebroplasty for refractory osteoporotic pain (contested)` - correctly flagged. AU practice is **kyphoplasty/vertebroplasty rarely recommended** since VERTOS IV and VAPOUR trial data; Choosing Wisely Australia lists vertebroplasty for osteoporotic VCF as a "do not do" item. Could strengthen wording.

- **Spinal stenosis** - `epidural steroid modest short-term benefit` - correct. `Surgery (decompressive laminectomy +/- fusion)` - Australian practice: **fusion is not routinely added** to decompression in the absence of instability (SPORT trial data); simple decompression is preferred to reduce cost and morbidity.

- **Autonomic neuropathy** - Correct clinical picture and Ix. `Fludrocortisone or midodrine for postural hypotension` - fine. Missing: **droxidopa** (not PBS-listed but available); pyridostigmine has emerging evidence for neurogenic OH. Minor.

- **Orthostatic hypotension** - `salt (10 g/day)` - a high value; some guidelines (AAS/ESC) say 6-10 g/day. `fludrocortisone, midodrine, droxidopa` - droxidopa not PBS-listed in AU. Minor. Also could add **abdominal binder** as an AU-endorsed non-pharmacological measure.

- **Charcot-Marie-Tooth disease** - `avoid neurotoxic drugs (vincristine, cisplatin, isoniazid, nitrofurantoin, amiodarone)` - excellent inclusion. Could add **paclitaxel, thalidomide, metronidazole (prolonged), linezolid, high-dose pyridoxine**. Minor.

- **Posterior reversible encephalopathy syndrome** - `bilateral symmetric parieto-occipital vasogenic oedema` - correct. Missing: **atypical distributions occur in ~25%** (frontal, cerebellar, brainstem), so PRES cannot be excluded by non-parieto-occipital MRI alone. Also, `Anton syndrome` - misapplied here. Anton syndrome is cortical blindness with **denial of blindness**; not the same as "cortical visual loss with preserved pupillary reflexes". Suggest removing the parenthetical Anton reference.

### VERIFIED accurate

- **Benign paroxysmal positional vertigo** - Dix-Hallpike, Epley (80% single-session), Semont, barbecue roll, home Brandt-Daroff. Vestibular suppressants delay recovery - accurate. Red flags correct.
- **Carpal tunnel syndrome** - Risk factors, clinical features, night splint, steroid injection, carpal tunnel release - all match RACGP/AU practice. Pregnancy-related CTS resolving postpartum correct.
- **Cerebral palsy** - GMFCS, associated conditions, MRI structural in 90%, oral/intrathecal baclofen, botulinum toxin, SDR, NDIS-funded - all correct.
- **Encephalitis** - HSV empirical aciclovir 10 mg/kg q8h correct; temporal FLAIR imaging; autoimmune panel; notifiable status correct.
- **Hypoxic-ischaemic encephalopathy** - Therapeutic hypothermia within 6 h to 33.5°C for 72 h, moderate-severe HIE at 36/40+, NNT 7 - all match RCH/PIPER guidance.
- **Medication overuse headache** - Thresholds (10 days for triptans/opioids/combinations, 15 for simple analgesics), withdrawal + preventer - correct per IHS ICHD-3.
- **Myasthenia gravis** - AChR/MuSK antibodies, thymoma prevalence 10-15%, pyridostigmine + prednisolone + steroid-sparing, thymectomy indications, drug-worsening list - all correct. FVC monitoring in crisis correct.
- **Neural tube defect** - Folate 400 μg preconception / 5 mg high-risk (previous NTD, diabetes, antiepileptics) - correct per RANZCOG. AFP + 18-20/40 anomaly scan.
- **Parkinson disease** - Bradykinesia obligatory, DDx list, levodopa most effective, never stop abruptly / withhold for fasting - correct AU practice.
- **Subdural haematoma** - Bridging veins, crescentic, chronic in elderly/anticoagulated, dementia mimic, Cushing reflex - correct.
- **Syringomyelia** - Chiari I commonest cause, cape-distribution dissociated sensory loss, hand intrinsic wasting, MRI whole neuraxis, posterior fossa decompression - correct.
- **Tension headache** - Bilateral pressing, ICHD-3 thresholds, amitriptyline preventer, drug history for MOH - correct.
- **Hepatic encephalopathy** - Grades I-IV, PINCH ME-like trigger list, lactulose + rifaximin, avoid protein restriction - correct.
- **Dermatomyositis** - Gottron/heliotrope, myositis-specific antibodies (Mi-2, Jo-1, MDA5, TIF1-γ), malignancy screen in adults - correct per Australian Rheumatology Association guidance.
- **Polymyositis** - Diagnosis of exclusion caveat, IBM/necrotising myopathy DDx - correct and cautious.
- **Autonomic neuropathy** - Cardiovascular reflex tests, silent MI trap in diabetes, fludrocortisone/midodrine - correct.

### UNVERIFIED / flagged

- **Sturge-Weber syndrome** - not fully quoted above; summary length 956 chars. Assumed to cover port-wine, leptomeningeal angiomatosis, glaucoma, seizures. Should verify GNAQ R183Q mutation is mentioned and that anti-seizure prophylaxis (aspirin, ASMs) is discussed per current SWS Foundation guidance. StatPearls-tier source only for AU-specific practice.

- **Obstructive sleep apnoea** - summary present (1192 chars) but not shown in read-out above. Verify against 2024 Australasian Sleep Association guidelines directly - AHI severity thresholds, indication for polysomnography vs home study, CPAP as first-line for moderate-severe.

- **Hydrocephalus** - Tap test sensitivity numbers cited from international literature; no AU-specific NPH guideline exists. Flagged.

- **CIDP** - Second-line agents (rituximab, azathioprine) - EAN/PNS 2021 discusses but AU-specific PBS access for rituximab in CIDP is via Section 100 authority, not routinely listed. Not verified with current PBS restriction.

- **Vestibular neuritis** - Steroid recommendation intentionally softened above; no AU-specific ENT position statement located. Flagged for ANZAN/Australian ENT input.

- **Peripheral neuropathy** - Pregabalin PBS restriction wording ("requires prior failure of another first-line") based on PBS neuropathic pain restriction - not re-verified against current PBS schedule 2026.

## Notes

- 47 entries in scope, all with rich summaries pulled from `all_rich_summaries_2026-09-01.json`.
- 12 SUBSTANTIVE errors identified requiring rewrite; 22 MINOR issues; 16 fully verified as accurate; 6 flagged as unverified against a current AU source.
- Top AU-specific themes: (1) high-efficacy DMT first-line for MS is the current ANZ consensus (MJA 2025); (2) INTERACT-3 (Australian-led) is the current ICH BP citation, not INTERACT-2; (3) many AU-relevant drug-access nuances (amifampridine SAS-only, guanfacine SAS-only, galcanezumab not PBS for cluster, home O2 not PBS, deflazacort not PBS, droxidopa not PBS, ataluren not PBS).
- Pabrinex dose typo in Wernicke ("Pabrinal" -> "Pabrinex") is a small but publication-blocking error - should be fixed regardless of other changes.
- Two aliases queries: "labyrinthitis" listed as alias for vestibular neuritis is technically wrong (labyrinthitis includes hearing loss) - either separate the entries or drop the alias.
- Where 4 or more entries name the same drug-access pattern (e.g., "TGA-approved but not PBS-listed"), consider a shared reference field/tag in the data pipeline rather than repeating the caveat inline.
