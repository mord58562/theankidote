# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""Structured replacements for condition summaries.

The base summaries in `_conditions.py` are not thin - median 800
characters - but they are unstructured: one dense block with section
labels used inconsistently, which is exactly what makes a long popup
unreadable. The information is there and none of it is findable.

This file holds rewritten versions keyed by canonical name, merged over
the base at import. An override layer rather than edits in place,
because:

  * `_conditions.py` is a 2,589-entry generated-looking file, and
    hand-editing entries scattered through it is how you lose them;
  * progress is trackable - `len(RICH_SUMMARIES)` is the count of
    conditions upgraded so far, and the test suite can assert every
    override targets a real entry;
  * a bad override is one dict key to delete, not a diff to unpick.

House style, matching the scaffold used on the cards these popups sit
beside: a one-line lede defining the condition, then `Label:` sections
in the order Epidemiology, Causes, Pathophysiology, Clinical features,
Investigations, Differential, Management - including only the sections
that earn their place. `Note:` carries the single most discriminating
fact, and `Red flags:` anything time-critical.

**Length is governed by bullet count, not characters.** Measured across
the shipped library, the overrides that fit the popup carry a median of
4 bulleted points and the ones that scroll carry 10 - at an identical
median length of about 1,000 characters. Character count does not
discriminate between the two, which is why the previous rule here (cap
1,200, aim for 1,050) produced entries that were the right length and
scrolled anyway: 30 of the first 55 were over the cap.

The cap is 900px as of 2.2, raised from 620. Do not read that as 280px
of new room to fill. The estimator was corrected in the same release and
had been understating every popup by at least 114px, because it costed
the summary text and nothing else - not the source label, the title, the
UpToDate chip row or the footer button, which together are 110px before
a word is written. An entry that measured 500px under the old model
measures about 650px under the new one and has gained nothing.

The working budget is five or six sections, and few *bulleted* points. A
section bullets when it splits into four or more points with at least
one of them substantial - `_worthBulleting` in web/marker.js - so a run
of short items is both cheaper and more readable set as prose. Check
against `PopupHeightBudget` in tests/test_vocab.py, which estimates
rendered height directly; a character count tells you nothing.

Australian guidance first (eTG, AMH, PBS, RANZCP), and where a popup
would otherwise imply a US pathway the entry says what is done here.
"""

# Conditions the base database never listed. Kept here beside their
# summaries rather than appended to `_conditions.py`, so the whole of a
# new entry - name, aliases, article link and text - lives in one place.
# `summary` is filled from RICH_SUMMARIES below at import.
# No `nbk` accession here on purpose. An NBK id has to be verified
# against the actual article - a plausible-looking one that belongs to
# something else is worse than none, because it opens the wrong page
# confidently. Three invented ids made it into preview 8 before this
# was caught: NBK519494, used for febrile neutropenia, is in fact
# "Anatomy, Bony Pelvis and Lower Limb, Knee Lateral Meniscus". Without
# an accession these fall back to a StatPearls in-book search, which now
# uses US spelling and finds the article.
NEW_CONDITIONS = [
    {
        "name": "Febrile neutropenia",
        "aliases": ["Neutropenic fever", "Neutropenic sepsis"],
        "utd": [["Overview", "overview of neutropenic fever syndromes"]],
        "summary": "",
    },
    {
        "name": "Syndrome of inappropriate antidiuretic hormone secretion",
        "aliases": ["SIADH", "Inappropriate ADH secretion",
                    "Syndrome of inappropriate ADH"],
        "utd": [["Overview", "pathophysiology and etiology of the syndrome "
                             "of inappropriate antidiuretic hormone secretion"]],
        "summary": "",
    },
    {
        "name": "Tumour lysis syndrome",
        "aliases": ["Tumor lysis syndrome", "TLS"],
        "utd": [["Overview", "tumor lysis syndrome prevention and treatment"]],
        "summary": "",
    },
]


RICH_SUMMARIES = {

    # ═══════ TOPIC 3: NEUROLOGY, ENDOCRINE AND DIABETES ═════════════════

    "Stroke": (
        "Acute neurological deficit from cerebral infarction (about 85%) or "
        "haemorrhage (about 15%). "
        "Clinical features: sudden focal deficit fitting a vascular "
        "territory - anterior circulation gives hemiparesis, hemisensory "
        "loss, dysphasia or neglect; posterior gives ataxia, diplopia, "
        "vertigo and crossed signs. "
        "Ix: non-contrast CT immediately to exclude haemorrhage, then CT "
        "angiography and perfusion; BGL, since hypoglycaemia mimics stroke; "
        "ECG and prolonged monitoring for AF; carotid imaging. "
        "Mx: thrombolysis within 4.5 hours with BP below 185/110; "
        "thrombectomy up to 24 hours for large vessel occlusion with "
        "favourable imaging. Admit to a stroke unit - this alone improves "
        "outcomes as much as any drug. Haemorrhagic stroke needs BP lowering "
        "and anticoagulation reversal. "
        "Secondary prevention: antiplatelet or anticoagulation for AF, "
        "statin, BP control, carotid endarterectomy where indicated. "
        "DDx: Todd paralysis after seizure; hypoglycaemia; migraine with aura; "
        "subdural haematoma; hypertensive encephalopathy; tumour. "
        "Note: time is brain - the target is door-to-needle under 60 "
        "minutes, so investigation and treatment run in parallel."
    ),

    "Transient ischaemic attack": (
        "Transient focal neurological deficit from ischaemia without "
        "infarction - now defined on tissue rather than the old 24-hour "
        "clock, so imaging matters. "
        "Clinical features: sudden onset, resolving typically within an "
        "hour; amaurosis fugax, hemiparesis, dysphasia. "
        "Ix: urgent MRI with diffusion weighting is preferred - it "
        "reclassifies many TIAs as minor stroke; carotid imaging, ECG and "
        "prolonged rhythm monitoring, glucose, lipids. "
        "Mx: dual antiplatelet therapy with aspirin and clopidogrel for 21 "
        "days then single agent, started immediately in high-risk TIA; "
        "anticoagulate if AF; high-intensity statin; BP control; carotid "
        "endarterectomy within 2 weeks for symptomatic stenosis of 70-99%. "
        "Note: the risk of completed stroke is highest in the first 48 "
        "hours, so a TIA is an emergency, not a reassuring event. Australian "
        "guidance is for specialist assessment within 24 hours in high-risk "
        "patients. Advise not to drive and notify licensing requirements. "
        "Red flags: crescendo TIAs, or symptoms with a known critical "
        "stenosis, warrant admission."
    ),

    "Subarachnoid haemorrhage": (
        "Bleeding into the subarachnoid space, usually from a ruptured "
        "berry aneurysm. "
        "Risk factors: hypertension, smoking, family history, polycystic "
        "kidney disease, Ehlers-Danlos and Marfan syndromes. "
        "Clinical features: thunderclap headache reaching maximum intensity "
        "within a minute, classically the worst of the patient's life; "
        "vomiting, neck stiffness, photophobia, reduced consciousness, "
        "seizure. A sentinel bleed may precede it by days to weeks. "
        "Ix: non-contrast CT within 6 hours is close to 100% sensitive; "
        "beyond that, lumbar puncture at 12 hours looking for xanthochromia. "
        "CT angiography to define the aneurysm. "
        "Mx: neurosurgical referral; endovascular coiling or surgical "
        "clipping; nimodipine to reduce delayed cerebral ischaemia; blood "
        "pressure and analgesia control. "
        "Complications: rebleeding, delayed cerebral ischaemia from "
        "vasospasm at days 4-14, hydrocephalus, hyponatraemia from cerebral "
        "salt wasting or SIADH. "
        "Red flags: any thunderclap headache needs imaging, regardless of "
        "how well the patient looks by the time they are seen."
    ),

    "Epilepsy": (
        "Enduring predisposition to unprovoked seizures - two or more "
        "separated by 24 hours, or one with a high recurrence risk. "
        "Classification: focal (aware or impaired awareness, with or "
        "without progression to bilateral tonic-clonic) or generalised "
        "(tonic-clonic, absence, myoclonic, atonic). Classification drives "
        "drug choice, so it is not academic. "
        "Ix: EEG supports classification but a normal one does not exclude "
        "epilepsy; MRI brain for structural cause; BGL, UEC, calcium and "
        "toxicology to exclude provoked seizures; ECG, since cardiac syncope "
        "is the commonest mimic. "
        "Mx: antiseizure medication after a second seizure, or after a "
        "first with a structural lesion or epileptiform EEG. Levetiracetam or "
        "lamotrigine for both focal and generalised; sodium valproate is "
        "effective in generalised epilepsy but contraindicated in people who "
        "could become pregnant. "
        "Note: driving restrictions under Austroads apply from the first "
        "seizure and must be discussed and documented; the patient carries "
        "the reporting obligation in most states. "
        "Red flags: seizure over 5 minutes is status epilepticus - "
        "benzodiazepine, then a second-line agent."
    ),

    "Multiple sclerosis": (
        "Immune-mediated demyelinating disease of the central nervous "
        "system, disseminated in time and space. "
        "Epidemiology: onset 20-40; women about 3 times more than men; "
        "incidence rises with latitude, and Tasmania has among the highest "
        "rates in the world. "
        "Clinical features: optic neuritis with painful monocular visual "
        "loss; internuclear ophthalmoplegia; transverse myelitis; sensory "
        "disturbance; Lhermitte sign; Uhthoff phenomenon of transient "
        "worsening with heat. Fatigue and bladder dysfunction dominate later "
        "disability. "
        "Types: relapsing-remitting in about 85% at onset, most evolving to "
        "secondary progressive; primary progressive in the rest. "
        "Ix: MRI brain and cord with gadolinium showing periventricular, "
        "juxtacortical, infratentorial and spinal lesions; CSF "
        "oligoclonal bands; visual evoked potentials. "
        "Mx: high-dose methylprednisolone shortens relapses without altering "
        "outcome. Disease-modifying therapy is the substance of management "
        "and works best started early - from interferons and glatiramer "
        "through to natalizumab, ocrelizumab and cladribine. "
        "Note: vitamin D deficiency and smoking are modifiable risks for "
        "progression."
    ),

    "Parkinson disease": (
        "Neurodegenerative disease from dopaminergic neurone loss in the "
        "substantia nigra with alpha-synuclein Lewy body deposition. "
        "Clinical features: bradykinesia is obligatory, plus rest tremor at "
        "4-6 Hz, rigidity, or both. Asymmetry at onset is characteristic. "
        "Non-motor features precede motor ones by years - REM sleep behaviour "
        "disorder, hyposmia, constipation, depression. "
        "DDx: drug-induced parkinsonism (antipsychotics, metoclopramide - "
        "symmetrical and reversible), progressive supranuclear palsy (early "
        "falls, vertical gaze palsy), multiple system atrophy (autonomic "
        "failure), vascular parkinsonism (lower body predominant), essential "
        "tremor (postural not rest, improves with alcohol). "
        "Mx: levodopa with carbidopa is the most effective symptomatic "
        "therapy; dopamine agonists and MAO-B inhibitors are alternatives in "
        "younger patients to defer motor complications. Physiotherapy, "
        "speech therapy and exercise all have evidence. "
        "Note: never stop Parkinson medication abruptly in hospital, and "
        "never withhold it for fasting - missed doses cause severe akinesia "
        "and can precipitate a neuroleptic malignant-like syndrome."
    ),

    "Myasthenia gravis": (
        "Autoimmune disorder of the neuromuscular junction causing fatigable "
        "weakness. "
        "Pathophysiology: antibodies against the postsynaptic acetylcholine "
        "receptor in about 85%, or against MuSK in most of the rest, "
        "reducing endplate potential and causing failure with repeated use. "
        "Clinical features: fatigable weakness worsening through the day - "
        "ptosis and diplopia in most at onset, then bulbar involvement with "
        "dysarthria, dysphagia and nasal speech, then proximal limb and "
        "respiratory weakness. "
        "Ix: acetylcholine receptor and MuSK antibodies; repetitive nerve "
        "stimulation showing decrement, or single-fibre EMG; CT chest for "
        "thymoma, present in 10-15%; TFT. "
        "Mx: pyridostigmine for symptoms; prednisolone with azathioprine or "
        "mycophenolate for immunosuppression; thymectomy in thymoma and in "
        "younger seropositive patients. "
        "Note: many common drugs worsen myasthenia - aminoglycosides, "
        "macrolides, fluoroquinolones, beta-blockers, magnesium - so check "
        "any new prescription. "
        "Red flags: myasthenic crisis with respiratory failure needs "
        "monitoring of forced vital capacity, not oximetry, since saturation "
        "falls only after decompensation."
    ),

    "Guillain-Barré syndrome": (
        "Acute immune-mediated polyradiculoneuropathy causing ascending "
        "weakness, typically 1-3 weeks after infection. "
        "Causes: Campylobacter jejuni most often, then CMV, EBV, Mycoplasma "
        "and influenza. "
        "Clinical features: symmetrical ascending flaccid weakness with "
        "areflexia, developing over days to 4 weeks; sensory symptoms are "
        "usually mild relative to weakness; back and limb pain is common; "
        "autonomic instability with arrhythmia and labile blood pressure; "
        "facial and bulbar involvement. Miller Fisher variant gives "
        "ophthalmoplegia, ataxia and areflexia. "
        "Ix: nerve conduction studies showing demyelination; CSF with raised "
        "protein and normal cell count - albuminocytological dissociation - "
        "though this may be normal in the first week. Serial forced vital "
        "capacity is the key monitoring test. "
        "Mx: intravenous immunoglobulin or plasma exchange, equally "
        "effective and not combined; supportive care with VTE prophylaxis "
        "and cardiac monitoring. Corticosteroids do not work here. "
        "Red flags: falling FVC below about 20 mL/kg, bulbar weakness or "
        "autonomic instability means ICU. Respiratory failure develops "
        "before hypoxia appears on oximetry."
    ),

    "Syphilis": (
        "Sexually transmitted infection caused by the spirochaete Treponema "
        "pallidum; notifiable in every Australian jurisdiction and "
        "resurgent. Clinical features: primary, 9-90 days - painless "
        "indurated chancre at the inoculation site with regional "
        "lymphadenopathy, heals spontaneously; secondary, 6-12 weeks - "
        "maculopapular rash involving palms and soles, condylomata lata, "
        "alopecia, hepatitis, uveitis; latent - asymptomatic with positive "
        "serology; tertiary, 10-30 years - gummas, aortitis with aortic "
        "regurgitation, neurosyphilis. Ix: dark-field microscopy or PCR of "
        "a lesion swab; treponemal EIA or TPHA screens and stays positive "
        "for life; RPR or VDRL titres track activity and response. Mx: "
        "benzathine benzylpenicillin 1.8 g IM single dose for primary, "
        "secondary and early latent; three weekly doses for late latent and "
        "tertiary; benzylpenicillin IV for 15 days in neurosyphilis. Note: "
        "tabes dorsalis gives a wide-based gait, lancinating pains and "
        "Argyll Robertson pupils, which accommodate but do not react to "
        "light. Red flags: Jarisch-Herxheimer reaction within 24 hours of "
        "the first dose - fever, rigors, hypotension; screen every "
        "pregnancy for congenital syphilis."
    ),

    "Neuroleptic malignant syndrome": (
        "Potentially fatal idiosyncratic reaction to antipsychotics, "
        "typical more than atypical, or to dopamine agonist withdrawal; D2 "
        "blockade in striatum and hypothalamus. Sx (tetrad): hyperthermia "
        "above 38°C, often above 40°C; lead-pipe rigidity; altered "
        "consciousness progressing to coma; autonomic instability with "
        "diaphoresis, tachycardia, labile BP and tachypnoea. Onset: hours "
        "to days after starting or increasing an antipsychotic, or stopping "
        "a dopaminergic. Ix: CK often above 1000 and can exceed 100,000; "
        "leukocytosis; raised LFTs; metabolic acidosis; myoglobinuria "
        "progressing to AKI. Ddx: serotonin syndrome - clonus and "
        "hyperreflexia, onset under 24 hours; malignant hyperthermia - "
        "inhalational anaesthetic or suxamethonium; anticholinergic "
        "toxidrome - dry skin, normal reflexes. Mx: stop the causative "
        "drug; IV fluids, active cooling, respiratory support; "
        "bromocriptine or dantrolene for rigidity; benzodiazepines for "
        "agitation; ECT if refractory or catatonic. Red flags: recovery "
        "takes days to weeks; rechallenge with a different antipsychotic no "
        "sooner than 2 weeks."
    ),

    "Horner syndrome": (
        "Interruption of the oculosympathetic pathway, producing ipsilateral "
        "partial ptosis, miosis and anhidrosis. "
        "Causes: first-order, hypothalamus to C8-T2 - lateral medullary "
        "infarct, MS, syringomyelia, cord tumour; second-order preganglionic "
        "- Pancoast tumour, cervical rib, neck surgery, neuroblastoma in "
        "children; third-order postganglionic - carotid dissection, "
        "cavernous sinus lesion, cluster headache. "
        "Clinical features: partial ptosis from denervation of the superior "
        "tarsal muscle, not the complete ptosis of a third nerve palsy; "
        "miosis with dilation lag and anisocoria greater in dim light; "
        "pupillary light response preserved; iris heterochromia if "
        "congenital. "
        "Ix: apraclonidine is the test of choice, reversing anisocoria "
        "through denervation supersensitivity; hydroxyamphetamine separates "
        "third-order from more proximal lesions; imaging follows the level "
        "suspected - CT or MR angiography of the neck, CT chest for an "
        "apical lesion. "
        "Note: anhidrosis localises - hemibody in first-order, face in "
        "second-order, absent in third-order. "
        "Red flags: painful Horner syndrome is carotid dissection until "
        "excluded; new Horner syndrome in a child needs urinary "
        "catecholamines for neuroblastoma."
    ),

    "Diabetic ketoacidosis": (
        "Acute hyperglycaemic emergency from absolute insulin deficiency, "
        "with ketosis and metabolic acidosis. "
        "Criteria: hyperglycaemia (though euglycaemic DKA occurs); ketonaemia "
        "3.0 mmol/L or more; pH below 7.3 or bicarbonate below 15. "
        "Triggers: infection, missed insulin, new-onset type 1 diabetes, "
        "myocardial infarction, and SGLT2 inhibitors. "
        "Clinical features: polyuria and thirst; vomiting and abdominal pain; "
        "Kussmaul respiration; ketotic breath; drowsiness. "
        "Mx: fluid first - the deficit is usually 5-7 L. Then fixed-rate "
        "insulin at 0.1 units/kg/h. Potassium from the outset unless above "
        "5.5, since total body potassium is depleted however normal the level "
        "looks. Add glucose-containing fluid once BGL falls below 14 while "
        "continuing insulin, which is clearing ketones, not glucose. "
        "Note: euglycaemic DKA on SGLT2 inhibitors is easily missed - check "
        "ketones in any unwell patient on one regardless of the glucose. "
        "Red flags: cerebral oedema, mainly in children and after rapid "
        "osmolar shifts; hypokalaemia is the commonest avoidable cause of "
        "death."
    ),

    "Diabetes mellitus": (
        "Chronic hyperglycaemia from insulin resistance with progressive "
        "beta-cell failure. "
        "Ix: HbA1c of 6.5% or above, fasting glucose 7.0 or above, or a "
        "2-hour OGTT value of 11.1 or above - confirmed on a second sample "
        "unless symptomatic. HbA1c is unreliable in haemoglobinopathy, "
        "recent transfusion and chronic kidney disease. "
        "Mx: lifestyle plus metformin first-line for most. Then choose by "
        "comorbidity rather than by HbA1c alone - an SGLT2 inhibitor for "
        "heart failure or chronic kidney disease, a GLP-1 receptor agonist "
        "for obesity or established cardiovascular disease. Target HbA1c is "
        "around 7% generally, relaxed in the frail or in hypoglycaemia "
        "unawareness. "
        "Monitoring: HbA1c 3- to 6-monthly; annual retinal screening, urine "
        "ACR, eGFR, foot examination with monofilament, and lipids. "
        "Note: PBS criteria govern access to SGLT2 inhibitors and GLP-1 "
        "agonists in Australia and change periodically - check before "
        "prescribing. Metformin needs holding around iodinated contrast and "
        "in acute illness. "
        "Red flags: rapid weight loss or ketosis suggests type 1 or "
        "pancreatic disease, not type 2."
    ),

    "Hypothyroidism": (
        "Deficiency of thyroid hormone, most often from autoimmune "
        "thyroiditis. "
        "Causes: Hashimoto thyroiditis is commonest in iodine-replete "
        "countries; also post-thyroidectomy, radioiodine, amiodarone, "
        "lithium, and central causes from pituitary disease. "
        "Clinical features: fatigue, cold intolerance, weight gain; "
        "constipation and dry skin; menorrhagia; depression and cognitive "
        "slowing; bradycardia with delayed reflex relaxation. Onset is "
        "insidious and often attributed elsewhere for months. "
        "Ix: TSH first - raised with low free T4 in primary disease; raised "
        "TSH with normal T4 is subclinical. TPO antibodies confirm autoimmune "
        "cause. Low TSH with low T4 means central hypothyroidism. "
        "Mx: levothyroxine, starting low in the elderly or those with "
        "ischaemic heart disease, retesting TSH after 6-8 weeks. Take on an "
        "empty stomach, separated from calcium, iron and proton pump "
        "inhibitors. "
        "Note: in pregnancy, requirements rise by 25-50% from early in the "
        "first trimester and undertreatment affects fetal neurodevelopment - "
        "increase the dose promptly and check TSH early."
    ),

    "Hyperthyroidism": (
        "Excess thyroid hormone, most often from Graves disease. "
        "Causes: Graves disease (TSH receptor antibodies), toxic multinodular "
        "goitre, toxic adenoma, thyroiditis with a transient release phase, "
        "amiodarone, and excess levothyroxine. "
        "Clinical features: weight loss with preserved appetite; heat "
        "intolerance and sweating; tremor and anxiety; palpitations or AF; "
        "diarrhoea; goitre. Graves adds orbitopathy and pretibial myxoedema, "
        "which no other cause produces. "
        "Ix: suppressed TSH with raised free T4 or T3; TSH receptor antibodies "
        "for Graves; uptake scan separates Graves and toxic nodules (high) "
        "from thyroiditis (low) - which decides whether antithyroid drugs "
        "help at all. "
        "Mx: carbimazole, or propylthiouracil in the first trimester of "
        "pregnancy; beta-blocker for symptom control; then radioiodine or "
        "surgery for definitive treatment. "
        "Note: warn every patient starting carbimazole to stop and seek an "
        "urgent FBC with fever or sore throat - agranulocytosis is rare but "
        "can be fatal. "
        "Red flags: thyroid storm - fever, agitation, tachyarrhythmia and "
        "heart failure - has high mortality and needs ICU."
    ),

    "Addison disease": (
        "Primary adrenal insufficiency with deficient cortisol and "
        "aldosterone. "
        "Causes: autoimmune adrenalitis in developed countries; tuberculosis "
        "worldwide; adrenal haemorrhage, metastases, and adrenoleukodystrophy. "
        "Clinical features: insidious fatigue, anorexia and weight loss; "
        "nausea and abdominal pain; salt craving; postural hypotension; "
        "hyperpigmentation of palmar creases and buccal mucosa, which "
        "distinguishes primary from secondary insufficiency. "
        "Ix: hyponatraemia with hyperkalaemia is characteristic; early "
        "morning cortisol, with a short synacthen test to confirm; ACTH is "
        "raised in primary disease and low in secondary; adrenal antibodies; "
        "imaging if not autoimmune. "
        "Mx: hydrocortisone in divided doses replicating diurnal rhythm, plus "
        "fludrocortisone. Sick day rules - double the dose during illness - "
        "with a parenteral emergency kit and alert bracelet. "
        "Red flags: adrenal crisis presents with hypotension, vomiting and "
        "hyponatraemia. Give intravenous hydrocortisone and fluid "
        "immediately on suspicion; do not wait for cortisol results, which "
        "can be taken first but must not delay treatment."
    ),

    "Cushing syndrome": (
        "Clinical state of chronic glucocorticoid excess. "
        "Causes: exogenous corticosteroid is overwhelmingly the commonest "
        "and is often overlooked. Endogenous causes are ACTH-dependent - "
        "pituitary adenoma (Cushing disease) or ectopic ACTH from small cell "
        "lung cancer - or ACTH-independent adrenal adenoma or carcinoma. "
        "Clinical features: central obesity with thin limbs; moon face and "
        "interscapular fat pad; hypertension, hyperglycaemia, osteoporosis. "
        "The discriminating features are proximal myopathy, wide violaceous "
        "striae and easy bruising, since obesity alone produces the rest. "
        "Ix: confirm cortisol excess with 24-hour urinary free cortisol, "
        "late-night salivary cortisol, or overnight dexamethasone "
        "suppression. Then ACTH to establish dependence, and image "
        "accordingly. "
        "Mx: withdraw exogenous steroid gradually where that is the cause; "
        "otherwise transsphenoidal surgery, adrenalectomy, or treatment of "
        "the ectopic tumour. "
        "Note: ectopic ACTH often presents with hypokalaemic alkalosis and "
        "pigmentation rather than the classic habitus, because it develops "
        "too fast for the phenotype to appear."
    ),

    "Syndrome of inappropriate antidiuretic hormone secretion": (
        "Euvolaemic hypotonic hyponatraemia from unsuppressed ADH. "
        "Causes: malignancy especially small cell lung cancer; CNS disease "
        "including stroke, haemorrhage and meningitis; pulmonary disease; "
        "and drugs - SSRIs, carbamazepine, and thiazides among others. "
        "Criteria: hyponatraemia with low serum osmolality, "
        "inappropriately concentrated urine above 100 mOsm/kg, urinary "
        "sodium above 30 mmol/L, clinical euvolaemia, and normal thyroid, "
        "adrenal and renal function. "
        "Clinical features: often asymptomatic when chronic; nausea, "
        "headache, confusion, and seizure or coma when severe or rapid. Rate "
        "of fall matters more than the absolute level. "
        "Mx: treat the cause; fluid restriction first-line; salt tablets or "
        "tolvaptan in resistant cases. Hypertonic saline only for severe "
        "symptoms. "
        "Note: correct no faster than 8-10 mmol/L in 24 hours - overly rapid "
        "correction of chronic hyponatraemia causes osmotic demyelination "
        "syndrome, which is irreversible. Volume status is what separates "
        "SIADH from hypovolaemic and hypervolaemic hyponatraemia, so assess "
        "it before treating."
    ),

    # ═══════════ TOPIC 7: ONCOLOGY AND HAEMATOLOGY ══════════════════════

    "Iron deficiency anaemia": (
        "Anaemia from depleted iron stores, the commonest anaemia worldwide. "
        "Causes: blood loss is the assumption until disproven - menstrual in "
        "premenopausal women, gastrointestinal otherwise. Also malabsorption "
        "(coeliac disease, atrophic gastritis, bariatric surgery), poor "
        "intake, and increased demand in pregnancy and infancy. "
        "Clinical features: fatigue, dyspnoea, pallor; angular stomatitis, "
        "glossitis, koilonychia and pica when chronic. "
        "Ix: microcytic hypochromic film; ferritin is the single best test - "
        "low is diagnostic, but it is an acute-phase reactant so a normal "
        "level does not exclude deficiency during inflammation. Transferrin "
        "saturation below 16% supports it. "
        "Mx: oral iron, alternate-day dosing giving better absorption than "
        "daily by avoiding a hepcidin rise; intravenous iron for intolerance "
        "or malabsorption. Recheck at 2-4 weeks, and continue 3 months past "
        "normalisation to refill stores. "
        "Note: iron deficiency anaemia in a man of any age, or a "
        "postmenopausal woman, mandates gastroscopy and colonoscopy - it is "
        "colorectal cancer until proven otherwise. Also test for coeliac "
        "disease."
    ),

    "Vitamin B12 deficiency": (
        "Deficiency causing megaloblastic anaemia and, independently, "
        "neurological disease. "
        "Causes: pernicious anaemia (autoimmune loss of intrinsic factor); "
        "gastrectomy or ileal resection; Crohn disease; metformin and "
        "long-term proton pump inhibitors; strict vegan diet. "
        "Clinical features: fatigue and pallor; glossitis; and neurological "
        "features - symmetrical paraesthesiae, loss of proprioception and "
        "vibration from subacute combined degeneration of the cord, ataxia, "
        "and cognitive or mood change. "
        "Ix: macrocytic anaemia with hypersegmented neutrophils; low serum "
        "B12; raised methylmalonic acid and homocysteine confirm functional "
        "deficiency when B12 is borderline. Intrinsic factor antibodies are "
        "specific but insensitive for pernicious anaemia. "
        "Mx: intramuscular hydroxocobalamin, loading then maintenance; "
        "lifelong if the cause is not reversible. High-dose oral is adequate "
        "in dietary deficiency. "
        "Note: neurological disease occurs without anaemia and can be "
        "irreversible if treatment is delayed - do not wait for a low "
        "haemoglobin. Never replace folate alone in combined deficiency; it "
        "corrects the anaemia while the cord degeneration progresses."
    ),

    "Multiple myeloma": (
        "Clonal plasma cell malignancy producing monoclonal immunoglobulin "
        "and end-organ damage. "
        "Epidemiology: median onset around 70; preceded by monoclonal "
        "gammopathy of undetermined significance in essentially all cases. "
        "Clinical features: CRAB - hyperCalcaemia, Renal impairment, Anaemia, "
        "Bone lesions - with bone pain, fracture and recurrent infection. "
        "Ix: serum and urine electrophoresis with immunofixation; serum free "
        "light chain ratio; FBC, UEC, calcium, beta-2 microglobulin; "
        "whole-body low-dose CT rather than skeletal survey; marrow biopsy "
        "for plasma cell percentage and cytogenetics. "
        "Mx: induction with a proteasome inhibitor, an immunomodulatory drug "
        "and dexamethasone, then autologous stem cell transplant if fit, then "
        "maintenance. Bisphosphonates for skeletal protection, plus "
        "analgesia and radiotherapy for painful lesions. "
        "Note: the rouleaux and raised ESR often come before anything else, "
        "and myeloma is a leading cause of an unexplained normocytic anaemia "
        "with renal impairment in an older patient. "
        "Red flags: back pain with neurological signs is cord compression; "
        "hypercalcaemia and hyperviscosity are both emergencies."
    ),

    "Hodgkin lymphoma": (
        "B-cell lymphoma defined by Reed-Sternberg cells in a reactive "
        "inflammatory background. "
        "Epidemiology: bimodal, peaking in the 20s and again after 60; "
        "associated with Epstein-Barr virus. "
        "Clinical features: painless, rubbery cervical or supraclavicular "
        "lymphadenopathy spreading contiguously between nodal groups; "
        "mediastinal mass; B symptoms - fever, drenching night sweats, weight "
        "loss over 10% in 6 months. Alcohol-induced nodal pain and pruritus "
        "are uncommon but characteristic. "
        "Ix: excisional node biopsy, not fine-needle aspiration, since "
        "architecture is needed; PET-CT for staging; FBC, ESR, LDH, LFT, "
        "HIV and hepatitis serology. "
        "Mx: ABVD chemotherapy with or without radiotherapy, guided by stage "
        "and interim PET response. Cure rates are high, above 80% overall. "
        "Note: contiguous spread and a young peak distinguish it clinically "
        "from non-Hodgkin lymphoma, which skips nodal groups and is more "
        "often extranodal. "
        "Complications: long-term survivorship risks matter as much as the "
        "disease - secondary malignancy, cardiotoxicity from anthracyclines, "
        "bleomycin lung toxicity, and infertility, so counsel on fertility "
        "preservation before treatment."
    ),

    "Non-Hodgkin lymphoma": (
        "Heterogeneous group of lymphoid malignancies, mostly B-cell, "
        "spanning indolent to highly aggressive behaviour. "
        "Classification: aggressive - diffuse large B-cell lymphoma "
        "(commonest), Burkitt, mantle cell; indolent - follicular, marginal "
        "zone, small lymphocytic. The split determines everything about "
        "management. "
        "Clinical features: painless lymphadenopathy with non-contiguous "
        "spread; extranodal involvement is common - gut, skin, CNS, testis; "
        "B symptoms; cytopenias from marrow involvement. "
        "Ix: excisional biopsy with immunohistochemistry; PET-CT; bone marrow "
        "biopsy; LDH (prognostic); HIV, hepatitis B and C serology before "
        "rituximab. "
        "Mx: aggressive disease is treated with curative intent - R-CHOP for "
        "diffuse large B-cell lymphoma. Indolent disease is often watched, "
        "since treating an asymptomatic follicular lymphoma does not improve "
        "survival. "
        "Note: the counterintuitive part is that aggressive lymphomas are "
        "curable and indolent ones generally are not - fast-growing tumours "
        "are more chemosensitive. "
        "Red flags: hepatitis B reactivation with rituximab can be fatal, so "
        "screen and give antiviral prophylaxis."
    ),

    "Chronic lymphocytic leukaemia": (
        "Clonal proliferation of mature but functionally incompetent B "
        "lymphocytes; the commonest leukaemia in adults in Australia. "
        "Epidemiology: median age around 70; often found incidentally on a "
        "routine FBC. "
        "Clinical features: frequently asymptomatic; otherwise "
        "lymphadenopathy, splenomegaly, fatigue, recurrent infection from "
        "hypogammaglobulinaemia, and later marrow failure. "
        "Ix: persistent lymphocytosis above 5 x 10^9/L with smudge cells on "
        "film; flow cytometry showing CD5, CD19, CD23 co-expression is "
        "diagnostic; FISH for del(17p) and TP53, which predict poor response "
        "to chemoimmunotherapy; direct antiglobulin test. "
        "Mx: watch and wait while asymptomatic - early treatment does not "
        "prolong survival. Treat for progressive cytopenias, bulky or "
        "symptomatic disease, or constitutional symptoms, with targeted "
        "agents such as BTK or BCL-2 inhibitors. "
        "Complications: autoimmune haemolytic anaemia and immune "
        "thrombocytopenia; recurrent infection; Richter transformation to "
        "aggressive lymphoma, suggested by rapid nodal growth with fever and "
        "a rising LDH."
    ),

    "Acute myeloid leukaemia": (
        "Clonal proliferation of myeloid blasts with arrested "
        "differentiation, causing rapid marrow failure. "
        "Epidemiology: median onset around 68; risk raised by prior "
        "chemotherapy, radiation, myelodysplasia and Down syndrome. "
        "Clinical features: days to weeks of fatigue, infection and "
        "bleeding, reflecting anaemia, neutropenia and thrombocytopenia; gum "
        "hypertrophy and skin infiltration in monocytic subtypes. "
        "Ix: blasts on film, often with Auer rods; marrow with 20% or more "
        "blasts; flow cytometry, cytogenetics and molecular testing (FLT3, "
        "NPM1, CEBPA) drive both prognosis and drug choice; coagulation "
        "screen, LDH, urate. "
        "Mx: intensive induction chemotherapy then consolidation or "
        "allogeneic transplant in fit patients; hypomethylating agents with "
        "venetoclax in those unfit for intensive therapy. "
        "Note: acute promyelocytic leukaemia is the subtype to recognise "
        "immediately - it presents with DIC and life-threatening bleeding, "
        "and is treated with all-trans retinoic acid started on suspicion "
        "rather than on confirmation. "
        "Red flags: fever with neutropenia is a medical emergency; "
        "hyperleukocytosis causes leukostasis with hypoxia and confusion."
    ),

    "Chronic myeloid leukaemia": (
        "Myeloproliferative neoplasm driven by the BCR-ABL1 fusion from the "
        "Philadelphia chromosome, t(9;22). "
        "Clinical features: often incidental leukocytosis; otherwise "
        "fatigue, weight loss, sweats, and splenomegaly which may be "
        "massive and cause early satiety or left upper quadrant pain. "
        "Phases: chronic (most at diagnosis), accelerated, and blast crisis "
        "resembling acute leukaemia. "
        "Ix: marked leukocytosis with the full spectrum of myeloid "
        "precursors and basophilia; low leukocyte alkaline phosphatase; "
        "BCR-ABL1 by PCR or cytogenetics is diagnostic. "
        "Mx: a tyrosine kinase inhibitor - imatinib, or a second-generation "
        "agent - with molecular monitoring of BCR-ABL1 transcript levels "
        "against defined milestones. Some with sustained deep molecular "
        "response can attempt treatment-free remission. "
        "Note: CML is the model of targeted therapy - a disease that was "
        "uniformly fatal now has near-normal life expectancy on a tablet, "
        "and adherence is the main determinant of outcome. "
        "Red flags: rising basophils, blasts or a rising transcript level "
        "signal progression."
    ),

    "Immune thrombocytopenic purpura": (
        "Autoimmune platelet destruction and impaired production, with "
        "isolated thrombocytopenia and no alternative cause. "
        "Clinical features: petechiae, purpura, mucosal bleeding - "
        "epistaxis, gum bleeding, menorrhagia. Bleeding risk is low above "
        "30 x 10^9/L. Children typically have an abrupt post-viral course "
        "that resolves; adults are usually chronic. "
        "Ix: a diagnosis of exclusion. Isolated thrombocytopenia on FBC with "
        "a normal film apart from large platelets; exclude pseudo-"
        "thrombocytopenia from EDTA clumping by repeating in citrate. Test "
        "HIV, hepatitis C and Helicobacter pylori. Marrow biopsy only in "
        "atypical cases. "
        "Mx: treat bleeding or a count below about 20-30 x 10^9/L, not the "
        "number alone. Prednisolone or dexamethasone first-line, with IVIg "
        "when a rapid rise is needed; then thrombopoietin receptor agonists, "
        "rituximab or splenectomy. "
        "Note: platelet transfusion is largely ineffective and reserved for "
        "life-threatening bleeding, since transfused platelets are destroyed "
        "by the same process."
    ),

    "Disseminated intravascular coagulation": (
        "Systemic activation of coagulation that consumes platelets and "
        "clotting factors, producing simultaneous thrombosis and bleeding. "
        "Causes: sepsis (commonest); major trauma; obstetric catastrophe "
        "including abruption and amniotic fluid embolism; malignancy, "
        "especially acute promyelocytic leukaemia. "
        "Pathophysiology: massive tissue factor release drives widespread "
        "microthrombi, which consume the substrate needed for haemostasis - "
        "hence bleeding in a hypercoagulable state. "
        "Clinical features: oozing from cannula and venepuncture sites, "
        "purpura fulminans, and organ dysfunction from microvascular "
        "thrombosis. "
        "Ix: thrombocytopenia, prolonged PT and APTT, low fibrinogen, "
        "markedly raised D-dimer, schistocytes on film. The trend across "
        "serial results is more informative than any single set. "
        "Mx: treat the underlying cause, which is the only definitive "
        "therapy. Support with platelets, fresh frozen plasma and "
        "cryoprecipitate guided by bleeding rather than by numbers alone. "
        "Note: fibrinogen falls late and a normal level early does not "
        "exclude DIC - it is an acute-phase reactant, so a normal value in a "
        "septic patient may already represent a fall."
    ),

    "Febrile neutropenia": (
        "Fever in a neutropenic patient - an oncological emergency, since "
        "the usual signs of infection are absent when neutrophils are. "
        "Definition: single temperature of 38.3 degrees, or 38.0 sustained "
        "over an hour, with neutrophils below 0.5 x 10^9/L or expected to "
        "fall below it. "
        "Clinical features: fever may be the only sign - there is no pus, "
        "little erythema, and often no localising feature. Hypotension may "
        "be the first indication of sepsis. "
        "Ix: blood cultures from peripheral and any central line before "
        "antibiotics; FBC, UEC, LFT, lactate; chest X-ray; cultures directed "
        "by symptoms. Do not delay treatment for results. "
        "Mx: broad-spectrum antipseudomonal beta-lactam - piperacillin-"
        "tazobactam or cefepime - within one hour of presentation. Add "
        "vancomycin for suspected line infection or haemodynamic "
        "instability. G-CSF where prophylaxis is indicated. "
        "Note: the one-hour target matters more than antibiotic choice; "
        "mortality rises measurably with each hour of delay. Any patient on "
        "chemotherapy with a fever needs assessment now, not in the morning."
    ),

    "Tumour lysis syndrome": (
        "Metabolic emergency from massive tumour cell breakdown releasing "
        "intracellular contents. "
        "Risk factors: bulky, rapidly proliferating, chemosensitive disease - "
        "Burkitt lymphoma, ALL, AML with high white count - plus "
        "pre-existing renal impairment or volume depletion. Usually within "
        "72 hours of starting treatment, occasionally spontaneous. "
        "Clinical features: from the electrolyte derangement - arrhythmia, "
        "tetany, seizures, and acute kidney injury from urate and calcium "
        "phosphate deposition. "
        "Ix: hyperkalaemia, hyperphosphataemia, hyperuricaemia and "
        "consequent hypocalcaemia, with rising creatinine. Monitor 6- to "
        "12-hourly in high-risk patients. "
        "Mx: prevention is the whole game - vigorous intravenous hydration, "
        "with allopurinol for moderate risk and rasburicase for high risk or "
        "established disease. Treat hyperkalaemia urgently; dialysis for "
        "refractory derangement or oliguric renal failure. "
        "Note: do not give calcium for asymptomatic hypocalcaemia - it "
        "precipitates with the high phosphate and worsens renal injury. "
        "Rasburicase is contraindicated in G6PD deficiency."
    ),

    "Spinal cord compression": (
        "Compression of the cord or cauda equina by tumour, most often from "
        "vertebral metastasis. "
        "Causes: breast, lung and prostate primaries account for most; also "
        "myeloma, renal and lymphoma. "
        "Clinical features: back pain first, typically for weeks and often "
        "worse lying flat or on coughing, then neurological signs - limb "
        "weakness, sensory level, and finally bladder and bowel dysfunction. "
        "Ix: whole-spine MRI within 24 hours, and sooner with neurological "
        "signs. Whole spine, because multiple levels are involved in about a "
        "third and imaging only the painful level misses them. "
        "Mx: dexamethasone 16 mg immediately on suspicion, before imaging "
        "confirms it, with proton pump cover and glucose monitoring. Then "
        "urgent radiotherapy or surgical decompression depending on "
        "stability, prognosis and tissue diagnosis. "
        "Note: pretreatment ambulatory status is the strongest predictor of "
        "walking afterwards, so the window for useful intervention closes "
        "with the loss of power, not with the onset of pain. "
        "Red flags: new back pain in anyone with known malignancy is cord "
        "compression until imaging says otherwise."
    ),

    "Hypercalcaemia": (
        "Raised serum calcium. Primary hyperparathyroidism and malignancy "
        "account for about 90% of cases between them - the first dominates in "
        "outpatients, the second in inpatients. "
        "Mechanism: in malignancy, PTH-related peptide in about 80% - squamous "
        "cell, renal and breast; osteolytic metastases in myeloma; rarely "
        "tumour calcitriol in lymphoma. "
        "Clinical features: the classic bones, stones, groans and psychic "
        "moans - polyuria and thirst, nausea, constipation, confusion, "
        "weakness. Onset is often rapid, so symptoms appear at lower levels "
        "than in primary hyperparathyroidism. "
        "Ix: corrected calcium or ionised calcium; PTH is suppressed in "
        "malignancy and raised or inappropriately normal in primary "
        "hyperparathyroidism; UEC, phosphate. "
        "Mx: aggressive intravenous normal saline first - these patients are "
        "profoundly volume-deplete from calcium-induced polyuria. Then a "
        "bisphosphonate (zoledronic acid), which takes 2-4 days to work, or "
        "denosumab in renal impairment. Calcitonin for rapid but transient "
        "control. "
        "Note: avoid loop diuretics until volume-replete - they were "
        "traditionally taught but worsen dehydration and are now reserved "
        "for fluid overload."
    ),

    # ══════════════════ TOPIC 4: RHEUMATOLOGY ═══════════════════════════

    "Polymyalgia rheumatica": (
        "Inflammatory condition causing aching and morning stiffness of the "
        "shoulder and hip girdles and neck, without true weakness. "
        "Epidemiology: age over 50, peak 70s; women 3x more than men. "
        "Pathophysiology: inflames peri-articular structures, not muscle - "
        "hence normal CK and preserved strength. "
        "Clinical features: bilateral girdle ache, morning stiffness over 45 "
        "min; constitutional symptoms. "
        "Ix: raised ESR/CRP, normocytic anaemia; CK normal; RF and anti-CCP "
        "negative. "
        "Mx: prednisolone 12.5-25 mg daily, tapered over 12-24 months on "
        "symptoms not ESR; bone protection. "
        "Note: steroid response is dramatic and near-diagnostic - no "
        "substantial improvement within a week means another diagnosis. "
        "Red flags: headache, jaw claudication or visual symptoms mean giant "
        "cell arteritis - high-dose steroids same day."
    ),

    "Giant cell arteritis": (
        "Granulomatous large-vessel vasculitis of the aorta and branches, "
        "especially the extracranial carotid branches. "
        "Epidemiology: over 50, peak 70-80; women > men; half have "
        "polymyalgia rheumatica. "
        "Clinical features: new temporal headache, scalp tenderness, jaw "
        "claudication, amaurosis fugax or sudden painless visual loss from "
        "anterior ischaemic optic neuropathy. "
        "Ix: ESR and CRP raised; temporal artery ultrasound halo sign; biopsy "
        "is the diagnostic standard. "
        "Mx: high-dose prednisolone immediately on suspicion - IV "
        "methylprednisolone first if visual symptoms; add aspirin and bone "
        "protection. "
        "Note: biopsy stays positive 1-2 weeks after starting steroids, so "
        "treatment never waits for it. "
        "Red flags: any visual symptom is an emergency - vision rarely "
        "returns and the other eye is at risk within days."
    ),

    "Dermatomyositis": (
        "Idiopathic inflammatory myopathy: symmetrical proximal weakness "
        "plus characteristic skin changes. "
        "Epidemiology: bimodal 5-15 and 40-60 yr; women > men. "
        "Pathophysiology: complement-mediated microangiopathy of endomysial "
        "capillaries, giving perifascicular atrophy. "
        "Clinical features: proximal weakness over weeks to months (deltoids, "
        "hip flexors, neck flexors); Gottron papules and heliotrope eruption "
        "are pathognomonic; photodistributed poikiloderma (shawl, V and "
        "Holster signs); ILD, myocarditis, dysphagia. "
        "Ix: CK 2-100x normal; ANA; myositis-specific antibodies (anti-Mi-2 "
        "good prognosis, anti-Jo-1 ILD, anti-MDA5 rapidly progressive ILD, "
        "anti-TIF1-gamma malignancy); muscle biopsy diagnostic. "
        "Mx: prednisolone plus methotrexate or azathioprine; IVIg if "
        "refractory. "
        "Note: adult disease carries markedly raised malignancy risk, "
        "highest in the first 3 years - CT chest, abdomen and pelvis plus "
        "age-appropriate screening."
    ),

    "Polymyositis": (
        "Idiopathic inflammatory myopathy causing symmetrical proximal "
        "weakness without the skin changes of dermatomyositis. "
        "Epidemiology: peak 30-60 yr, rare in children; women > men. "
        "Pathophysiology: CD8 T-cell cytotoxicity with endomysial "
        "inflammation - cell-mediated, unlike dermatomyositis. "
        "Clinical features: insidious proximal weakness of shoulder and hip "
        "girdles; dysphagia; no rash. "
        "Ix: CK markedly raised; ANA and anti-Jo-1; muscle biopsy shows "
        "endomysial infiltrate invading non-necrotic fibres. "
        "Differential: inclusion body myositis (older, asymmetric, distal - "
        "finger flexors and quadriceps - and steroid-unresponsive); "
        "immune-mediated necrotising myopathy including statin-associated "
        "anti-HMGCR; hypothyroid and drug-induced myopathy. "
        "Note: a diagnosis of exclusion, and diagnosed far more often than "
        "it occurs - asymmetric, distal or steroid-unresponsive weakness "
        "should prompt reconsideration."
    ),

    "Rheumatoid arthritis": (
        "Chronic symmetrical inflammatory polyarthritis of small joints with "
        "an erosive synovitis and systemic features. "
        "Epidemiology: onset 30-50 yr; women 3x more than men; smoking is "
        "the strongest modifiable risk. "
        "Pathophysiology: citrullinated self-proteins drive anti-CCP; synovial "
        "pannus releases proteases and RANKL, eroding bone. "
        "Clinical features: symmetrical MCP, PIP, wrist and MTP swelling; "
        "morning stiffness over an hour, easing with use; DIPs spared. "
        "Extra-articular: nodules, ILD, scleritis. "
        "Ix: anti-CCP (more specific, predicts erosions), RF, raised "
        "ESR/CRP; X-ray periarticular osteopenia and marginal erosions. "
        "Mx: methotrexate within weeks of diagnosis, treat-to-target to "
        "remission; escalate to biologic or JAK inhibitor per PBS; steroids "
        "only to bridge. "
        "Note: the window to prevent erosions is months - suspected "
        "inflammatory arthritis needs urgent referral, not a trial of NSAIDs."
    ),

    "Systemic lupus erythematosus": (
        "Multisystem autoimmune disease from immune complex deposition, "
        "relapsing and remitting. "
        "Epidemiology: women 9x more than men, reproductive years; more "
        "common and more severe in Aboriginal and Torres Strait Islander "
        "people. "
        "Clinical features: malar rash sparing nasolabial folds, "
        "photosensitivity, oral ulcers, alopecia; non-erosive arthritis; "
        "serositis; lupus nephritis; cytopenias. "
        "Ix: ANA screens (a negative makes lupus very unlikely); anti-dsDNA "
        "and anti-Sm are specific, dsDNA titre tracks activity; low C3/C4 in "
        "flares; urinalysis with ACR at every visit. "
        "Mx: hydroxychloroquine for nearly everyone - reduces flares, damage "
        "and mortality; mycophenolate or cyclophosphamide for "
        "organ-threatening disease. "
        "Note: lupus nephritis is usually asymptomatic until advanced, so "
        "routine urinalysis is what detects it."
    ),

    "Gout": (
        "Inflammatory arthritis from monosodium urate crystal deposition. "
        "Epidemiology: men >> premenopausal women; markedly increased in "
        "Aboriginal and Torres Strait Islander, Maori and Pacific peoples. "
        "Pathophysiology: urate crystals activate the NLRP3 inflammasome, "
        "releasing IL-1 beta. "
        "Clinical features: abrupt exquisitely painful monoarthritis peaking "
        "within 24 h, classically first MTP (podagra); tophi and erosions "
        "later. "
        "Ix: aspiration shows negatively birefringent needles and excludes "
        "sepsis; urate may be normal during an attack - recheck at 2 weeks. "
        "Mx: NSAID, colchicine or prednisolone for the attack. Allopurinol for "
        "recurrent attacks, tophi or erosions - target urate below "
        "0.36 mmol/L, with colchicine cover. "
        "Note: check HLA-B*5801 in high-risk ancestries before allopurinol. "
        "Red flags: a hot swollen joint is septic arthritis until aspiration "
        "says otherwise - the two can coexist."
    ),

    "Pseudogout": (
        "Arthropathy from calcium pyrophosphate dihydrate crystal "
        "deposition, formerly pseudogout. "
        "Epidemiology: strongly age-related, uncommon under 60. "
        "Clinical features: acute severe pain with overlying erythema, "
        "reduced range of movement, swelling and warmth. "
        "Differential: distinguished from acute gout by the joints involved "
        "- knee and wrist rather than first MTP - a longer duration of "
        "attacks, and more frequent systemic symptoms. "
        "Ix: aspiration shows positively birefringent rhomboid crystals, the "
        "mirror image of gout; chondrocalcinosis on X-ray is common with age "
        "and not diagnostic alone. "
        "Mx: NSAIDs, colchicine or intra-articular steroid. No equivalent of "
        "urate-lowering therapy exists. "
        "Note: look for a secondary cause if young or polyarticular - check "
        "ferritin, calcium, PTH and magnesium for haemochromatosis, "
        "hyperparathyroidism and hypomagnesaemia."
    ),

    "Fibromyalgia": (
        "Chronic widespread pain with fatigue, unrefreshing sleep and "
        "cognitive difficulty, understood as central sensitisation rather "
        "than tissue damage. "
        "Epidemiology: women > men; often coexists with mood disorders and "
        "irritable bowel syndrome. "
        "Clinical features: widespread pain over 3 months, fatigue, "
        "non-restorative sleep, cognitive fog, hypersensitivity to touch and "
        "sound. "
        "Ix: inflammatory markers, CK and imaging are all normal - and that "
        "normality is the finding. Investigate only what the history "
        "suggests; repeated negative testing entrenches illness beliefs. "
        "Mx: graded patient-led exercise has the best evidence, with sleep "
        "measures, CBT and pain education; amitriptyline or duloxetine may "
        "help; opioids do not and cause harm. "
        "Note: coexists with inflammatory disease often enough that finding "
        "one does not exclude the other."
    ),


    # ═══════════ TOPIC 1: CARDIOVASCULAR AND RESPIRATORY ════════════════

    "Heart failure": (
        "Clinical syndrome in which cardiac output is inadequate for tissue "
        "demand, or is achieved only at raised filling pressures. "
        "Classification: HFrEF 40% or below; HFmrEF 41-49%; HFpEF 50% or "
        "above. Only HFrEF has therapy that reliably improves mortality. "
        "Causes: ischaemic heart disease and hypertension dominate; valvular "
        "disease; arrhythmia; alcohol; chemotherapy; cardiomyopathy. "
        "Clinical features: exertional dyspnoea and orthopnoea; raised JVP; "
        "displaced apex with a third heart sound; bibasal crackles; "
        "peripheral oedema. "
        "Ix: BNP or NT-proBNP - a normal level essentially excludes it; a "
        "normal ECG makes HFrEF unlikely; echocardiography gives the "
        "phenotype; UEC, TFT, iron studies. "
        "Mx: HFrEF gets the four pillars - ARNI or ACE inhibitor; "
        "beta-blocker; mineralocorticoid receptor antagonist; SGLT2 "
        "inhibitor - started early at low dose and uptitrated, since each "
        "independently reduces mortality. Diuretics relieve congestion "
        "without changing survival. In HFpEF, an SGLT2 inhibitor. "
        "Note: correct iron deficiency even without anaemia - IV iron improves "
        "symptoms and admissions in HFrEF. ""Red flags: hypotension with cool peripheries and oliguria means "
        "cardiogenic shock."
    ),

    "Myocardial infarction": (
        "Spectrum of myocardial ischaemia from unstable plaque: unstable "
        "angina, NSTEMI, STEMI. "
        "Pathophysiology: plaque rupture with superimposed thrombus. Complete "
        "occlusion gives ST elevation; partial occlusion gives NSTEMI or "
        "unstable angina. "
        "Clinical features: central crushing chest pain radiating to jaw or "
        "arm; sweating, nausea, dyspnoea. Frequently atypical in women, older "
        "people and diabetes - dyspnoea or collapse without chest pain. "
        "Ix: ECG within 10 minutes, repeated if pain continues; "
        "high-sensitivity troponin at 0 and 1-3 hours, where the change "
        "matters more than a single value. "
        "Mx: aspirin 300 mg immediately, a second antiplatelet, "
        "anticoagulation and glyceryl trinitrate. STEMI needs reperfusion - "
        "primary PCI within 90 minutes, or thrombolysis if PCI is not "
        "achievable within 120, the usual constraint outside metro Australia. "
        "NSTEMI is risk-stratified with GRACE. "
        "Secondary prevention: dual antiplatelet therapy; statin; ACE "
        "inhibitor; beta-blocker; cardiac rehabilitation. "
        "Note: a normal troponin does not exclude unstable angina; posterior "
        "STEMI shows ST depression in V1-V3. "
        "Red flags: new murmur, hypotension or pulmonary oedema suggests "
        "mechanical complication."
    ),

    "Atrial fibrillation": (
        "Supraventricular arrhythmia with disorganised atrial activity and an "
        "irregularly irregular ventricular response. "
        "Causes: hypertension; ischaemic and valvular heart disease; "
        "thyrotoxicosis; alcohol; sepsis; obstructive sleep apnoea. "
        "Clinical features: palpitations, dyspnoea, fatigue or syncope - or "
        "asymptomatic and found incidentally, which is common. "
        "Ix: ECG shows absent P waves, irregularly irregular; TFT, UEC; "
        "echocardiography; Holter if paroxysmal. "
        "Mx: three separate decisions. Rate control with a beta-blocker or "
        "diltiazem suits most; rhythm control - flecainide, amiodarone or "
        "cardioversion - where symptoms persist or the AF is new. "
        "Anticoagulation is decided independently of rate or rhythm, on "
        "CHA2DS2-VASc against HAS-BLED, DOAC preferred except in moderate to "
        "severe mitral stenosis or a mechanical valve. "
        "Note: anticoagulation decisions do not change once sinus rhythm is "
        "restored - stroke risk tracks the underlying substrate, not the "
        "rhythm on the day. "
        "Red flags: instability means immediate synchronised cardioversion. A "
        "very rapid, broad, irregular complex suggests pre-excited AF in WPW "
        "- avoid AV nodal blockers, which can precipitate VF."
    ),

    "COPD": (
        "Progressive airflow limitation that is not fully reversible, from "
        "chronic bronchitis and emphysema. "
        "Causes: smoking overwhelmingly; biomass exposure; occupational dust; "
        "alpha-1 antitrypsin deficiency if young or basal-predominant. "
        "Clinical features: chronic dyspnoea; productive cough and wheeze; "
        "recurrent infection; hyperinflation. Clubbing is not a feature and "
        "should prompt a search for cancer or bronchiectasis. "
        "Ix: post-bronchodilator spirometry showing FEV1/FVC below 0.7 is "
        "required for diagnosis; chest X-ray; alpha-1 antitrypsin if "
        "indicated. "
        "Mx: smoking cessation is the only intervention that alters "
        "progression. Pulmonary rehabilitation and vaccination; inhaled "
        "therapy stepped from a reliever through LAMA or LABA to dual "
        "therapy, adding an inhaled corticosteroid if exacerbations persist "
        "or eosinophils are raised. Long-term oxygen only for chronic "
        "hypoxaemia. "
        "Note: check inhaler technique before escalating - poor technique is "
        "commoner than genuine treatment failure. Target saturations of "
        "88-92% in exacerbation, since over-oxygenation worsens hypercapnia. "
        "Red flags: rising CO2 with acidosis needs non-invasive ventilation."
    ),

    "Asthma": (
        "Chronic inflammatory airway disease with variable, largely "
        "reversible airflow obstruction and airway hyperresponsiveness. "
        "Clinical features: episodic wheeze, cough, chest tightness and "
        "dyspnoea, worse at night and provoked by exercise, cold air, "
        "allergens or infection. Variability is the diagnostic hallmark. "
        "Ix: spirometry with bronchodilator reversibility - FEV1 rise of 12% "
        "and 200 mL; peak flow variability. Normal spirometry between "
        "episodes does not exclude asthma. "
        "Mx: Australian practice has moved away from short-acting beta agonist "
        "monotherapy - adults and adolescents use budesonide-formoterol as "
        "anti-inflammatory reliever, as needed or as maintenance-and-reliever "
        "therapy. Add LAMA or a biologic in severe disease. Written action "
        "plan for everyone. "
        "Note: high short-acting reliever use - more than about three "
        "canisters a year - independently predicts exacerbation and death, "
        "and is the single most useful thing to ask about. "
        "Red flags: a silent chest, exhaustion, cyanosis, or a normalising "
        "CO2 in acute severe asthma all indicate life-threatening disease - "
        "the rising CO2 means the patient is tiring, not improving."
    ),

    "Pulmonary embolism": (
        "Occlusion of pulmonary arteries by thrombus, usually embolised from "
        "a deep vein thrombosis of the lower limb or pelvis. "
        "Clinical features: dyspnoea and pleuritic chest pain, tachycardia, "
        "tachypnoea, hypoxaemia; haemoptysis, syncope, or signs of DVT. "
        "Presentation is frequently non-specific, which is why a structured "
        "probability assessment matters more than clinical impression. "
        "Ix: apply Wells or revised Geneva first. Low probability with a "
        "negative D-dimer excludes PE; otherwise CT pulmonary angiography, or "
        "V/Q in pregnancy or renal impairment. ECG usually shows sinus "
        "tachycardia, S1Q3T3 being uncommon. "
        "Mx: anticoagulate on suspicion where imaging is delayed. A DOAC is "
        "first-line; low molecular weight heparin in pregnancy and cancer. "
        "Thrombolysis for massive PE. Duration 3 months if provoked, longer "
        "if unprovoked or recurrent. "
        "Note: D-dimer is useful only to rule out, and only when pretest "
        "probability is low - ordering it in a high-probability patient "
        "cannot change management and delays imaging. "
        "Red flags: hypotension or arrest means massive PE - consider "
        "immediate thrombolysis."
    ),

    "Pneumonia": (
        "Acute lower respiratory tract infection acquired outside hospital, "
        "with consolidation on imaging. "
        "Causes: Streptococcus pneumoniae most commonly; Haemophilus "
        "influenzae; Mycoplasma; Legionella; respiratory viruses. "
        "Clinical features: fever, productive cough, pleuritic pain, "
        "dyspnoea; bronchial breathing, focal crackles, dullness to "
        "percussion. Older patients may present only with confusion or a "
        "fall. "
        "Ix: chest X-ray; FBC, UEC, CRP; blood and sputum cultures if moderate "
        "to severe. Severity is scored with CORB or SMART-COP in Australia "
        "rather than CURB-65. "
        "Mx: per eTG - amoxicillin for mild disease, adding doxycycline for "
        "atypical cover; IV benzylpenicillin with doxycycline for moderate; "
        "ceftriaxone with azithromycin for severe. Review at 48 hours. "
        "Note: tropical northern Australia is the exception that changes "
        "management - Burkholderia pseudomallei (melioidosis) and Acinetobacter "
        "require meropenem-based cover in severe disease, so ask about "
        "location and wet-season exposure. "
        "Red flags: failure to improve by 48-72 hours suggests empyema, "
        "abscess, resistant organism or an obstructing lesion."
    ),

    "Hypertension": (
        "Persistently raised arterial pressure - in Australia, clinic readings "
        "of 140/90 mmHg or above on repeated occasions. "
        "Causes: primary in about 90%; renal parenchymal and renovascular "
        "disease; primary aldosteronism; phaeochromocytoma; Cushing "
        "syndrome; coarctation; obstructive sleep apnoea; NSAIDs and the "
        "COCP. Almost always asymptomatic - detection is by measurement. "
        "Ix: confirm with ambulatory or home monitoring. Assess end-organ "
        "damage - UEC, urine ACR, fundoscopy, ECG - and calculate absolute "
        "cardiovascular risk, since Australian thresholds follow that risk "
        "rather than the pressure alone. "
        "Mx: lifestyle for all. First-line agents are an ACE inhibitor or ARB, "
        "a dihydropyridine calcium channel blocker, or a thiazide-like "
        "diuretic; low-dose combination beats maximising one agent. "
        "Note: investigate for a secondary cause when hypertension resists "
        "three agents, presents before 30, or comes with hypokalaemia. "
        "Primary aldosteronism is commoner than traditionally taught and is "
        "potentially curable. "
        "Red flags: BP above 180/110 with end-organ damage is a hypertensive "
        "emergency needing controlled intravenous reduction - dropping it too "
        "fast causes watershed infarction."
    ),

    # ══════════════════ TOPIC 4: DERMATOLOGY ════════════════════════════

    "Erythema nodosum": (
        "Septal panniculitis presenting as tender erythematous nodules on "
        "the anterior shins - the commonest reactive panniculitis. "
        "Clinical features: tender poorly demarcated nodules 1-10 cm, "
        "bilateral, evolving from red to bruise-like and resolving over 2-8 "
        "weeks. They never ulcerate or scar, which distinguishes them from "
        "nodular vasculitis. "
        "Causes: streptococcal pharyngitis (commonest); sarcoidosis - Lofgren "
        "syndrome with hilar adenopathy, arthritis and fever has a good "
        "prognosis; tuberculosis; IBD; pregnancy and the COCP; Behcet "
        "disease. About half are idiopathic. "
        "Ix: clinical; biopsy only if atypical. Seek the cause with ASOT, "
        "chest X-ray, ACE and TSH. "
        "Mx: treat the cause; NSAIDs, rest and elevation; potassium iodide "
        "if refractory. "
        "Note: chest X-ray in essentially everyone - sarcoidosis and "
        "tuberculosis both present this way and are otherwise missed."
    ),

    "Acne vulgaris": (
        "Chronic inflammatory disease of the pilosebaceous unit with "
        "comedones, papules, pustules and, when severe, nodules and cysts. "
        "Epidemiology: begins in early puberty, settling through the 20s-30s. "
        "Pathophysiology: androgen-driven sebum, follicular "
        "hyperkeratinisation forming the comedone, C. acnes colonisation, "
        "then inflammation - each first-line agent hits a different step, "
        "which is why combinations beat monotherapy. "
        "Clinical features: face, chest, upper back. Mild is comedonal; "
        "moderate adds papules and pustules; severe has nodules and scarring. "
        "Mx: mild - topical benzoyl peroxide and/or a retinoid (adapalene, "
        "tretinoin). Moderate - add oral doxycycline, or the COCP in women. "
        "Severe - oral isotretinoin via dermatology. "
        "Note: never use an antibiotic without benzoyl peroxide or a "
        "retinoid alongside - monotherapy breeds resistance and eTG advises "
        "against it. Isotretinoin is highly teratogenic."
    ),

    "Psoriasis": (
        "Chronic immune-mediated disease of accelerated keratinocyte "
        "turnover producing well-demarcated scaly plaques. "
        "Epidemiology: bimodal onset in the 20s and 50s; strongly genetic. "
        "Pathophysiology: an IL-23/Th17 axis shortens epidermal transit from "
        "about a month to days, giving parakeratosis and thick silvery "
        "scale. "
        "Clinical features: plaques on extensor surfaces, scalp and sacrum; "
        "Auspitz and Koebner signs; nail pitting. Variants: guttate, "
        "flexural, pustular, erythrodermic. "
        "Associations: psoriatic arthritis in up to 30%; metabolic syndrome, "
        "cardiovascular disease. "
        "Mx: topical corticosteroid with calcipotriol; phototherapy if "
        "extensive; methotrexate or acitretin; biologics per PBS. "
        "Note: ask about joints at every review - psoriatic arthritis is "
        "erosive and skin usually precedes it by years. Avoid systemic "
        "steroids, which risk pustular rebound on withdrawal."
    ),

    "Eczema": (
        "Chronic relapsing pruritic inflammatory skin disease, the "
        "commonest eczema and part of the atopic triad. "
        "Epidemiology: begins in infancy; most improve by adolescence. "
        "Pathophysiology: barrier dysfunction first - filaggrin "
        "loss-of-function is the strongest genetic risk - allowing allergen "
        "entry and Th2 inflammation. That order is why emollients are "
        "treatment, not adjunct. "
        "Clinical features: itch is obligatory; facial and extensor in "
        "infants, flexural in older children and adults, with "
        "lichenification and excoriation marking chronicity. "
        "Mx: liberal emollients regardless of activity; topical steroid "
        "matched to site; calcineurin inhibitors for face and flexures. "
        "Note: undertreatment through steroid phobia causes more harm than "
        "appropriate steroid use, and is the commonest reason treatment "
        "fails. Monomorphic punched-out erosions mean eczema herpeticum - "
        "urgent aciclovir."
    ),

    "Cellulitis": (
        "Acute bacterial infection of deep dermis and subcutaneous tissue, "
        "usually Streptococcus pyogenes then Staphylococcus aureus. "
        "Clinical features: spreading erythema, warmth, swelling and "
        "tenderness with poorly demarcated borders, usually one lower limb, "
        "often with fever and an entry point such as tinea pedis. "
        "Differential: bilateral presentation is almost never cellulitis - "
        "consider venous eczema, lipodermatosclerosis, chronic oedema, DVT. "
        "Ix: clinical. Blood cultures only if systemically unwell; mark the "
        "erythema border to track progress. "
        "Mx: oral flucloxacillin or cefalexin; IV if systemically unwell. "
        "Elevate the limb and treat the entry point to reduce recurrence. "
        "Note: erythema often appears to extend in the first 24-48 h despite "
        "effective treatment, so that alone is not a reason to switch. "
        "Red flags: pain out of proportion, crepitus, bullae or necrosis "
        "suggest necrotising fasciitis - a surgical emergency."
    ),

    "Urticaria": (
        "Transient pruritic wheals from mast cell degranulation, with or "
        "without angioedema. "
        "Clinical features: individual wheals resolve within 24 h leaving no "
        "mark, though the eruption may persist far longer. Acute is under 6 "
        "weeks, chronic beyond. "
        "Causes: acute - viral infection (commonest), drugs, food, stings. "
        "Chronic spontaneous urticaria is usually autoimmune. "
        "Ix: none in typical acute disease; FBC and ESR/CRP if chronic. "
        "Extensive allergy testing has poor yield. "
        "Mx: a second-generation antihistamine (cetirizine, fexofenadine), "
        "up-titrated to four times standard dose if needed; omalizumab if "
        "refractory. "
        "Note: a single lesion lasting beyond 24 h, or leaving bruising, is "
        "urticarial vasculitis and needs biopsy. "
        "Red flags: wheals with airway or GI symptoms or hypotension are "
        "anaphylaxis - IM adrenaline, not an antihistamine."
    ),

    # ── Batch 1 ───────────────────────────────────────────────
    # Chosen by deck frequency, not by height: queried against the
    # live collection over AnkiConnect and kept only the over-cap
    # conditions that actually appear on cards. The tallest entries
    # in the database - Fournier gangrene, Tularaemia, Pellagra,
    # McArdle disease - returned zero notes, so ordering by height
    # would have spent the batch on conditions never looked up.
    "Vasculitis":
        "Inflammation of blood vessel walls, classified by the size of "
        "vessel predominantly involved. Classification: large vessel - "
        "giant cell arteritis, Takayasu arteritis; medium vessel - "
        "polyarteritis nodosa, Kawasaki disease; small vessel "
        "ANCA-associated - granulomatosis with polyangiitis, microscopic "
        "polyangiitis, eosinophilic granulomatosis with polyangiitis; small "
        "vessel immune complex - IgA vasculitis, cryoglobulinaemic, "
        "anti-GBM. Clinical features: constitutional illness with "
        "multi-organ involvement - palpable purpura, glomerulonephritis, "
        "alveolar haemorrhage, mononeuritis multiplex, and sinusitis with "
        "saddle-nose deformity in GPA. Ix: ANCA with PR3 specificity in GPA "
        "and MPO in MPA and EGPA; anti-GBM, complement, cryoglobulins; "
        "urinalysis for red cell casts; biopsy of the affected organ "
        "confirms. Mx: induction with rituximab or cyclophosphamide plus "
        "high-dose prednisolone; maintenance with rituximab or "
        "azathioprine; plasma exchange for anti-GBM disease or severe "
        "alveolar haemorrhage. Note: the emergency is a rising creatinine "
        "with an active sediment, not the rash.",
    "Pleural effusion":
        "Fluid in the pleural space, separated into transudate and exudate "
        "by Light criteria. Criteria: exudate if pleural to serum protein "
        "exceeds 0.5, pleural to serum LDH exceeds 0.6, or pleural LDH "
        "exceeds two thirds the upper limit of normal serum LDH. Causes: "
        "transudate - heart failure, cirrhosis, nephrotic syndrome, "
        "hypothyroidism; exudate - parapneumonic, malignancy, tuberculosis, "
        "pulmonary embolism, connective tissue disease, oesophageal "
        "rupture. Sx: dyspnoea and pleuritic pain, with a stony dull "
        "percussion note, reduced breath sounds and reduced vocal resonance "
        "at the base. Ix: erect chest radiograph blunts the costophrenic "
        "angle beyond about 200 mL; ultrasound-guided aspiration for "
        "protein, LDH, glucose, pH, cytology, MCS and adenosine deaminase. "
        "Mx: treat the cause; intercostal drain for a complicated "
        "parapneumonic effusion or empyema; indwelling pleural catheter or "
        "talc pleurodesis for recurrent malignant effusion. Note: pleural "
        "pH below 7.2 in a parapneumonic effusion means it needs drainage, "
        "not more antibiotics.",
    "Acute liver failure":
        "Coagulopathy with encephalopathy developing within 26 weeks in "
        "someone without pre-existing liver disease. Causes: paracetamol is "
        "the commonest in Australia; also hepatitis A and E, idiosyncratic "
        "drug reaction, Wilson disease, Budd-Chiari syndrome, ischaemic "
        "hepatitis, acute fatty liver of pregnancy. Clinical features: "
        "jaundice preceding encephalopathy graded I to IV, asterixis "
        "progressing to coma; cerebral oedema in grade III to IV is the "
        "leading cause of death. Ix: INR and lactate track severity; "
        "paracetamol concentration, viral serology, caeruloplasmin, hepatic "
        "vein Doppler; watch glucose, creatinine and cultures for the usual "
        "complications. Mx: intensive care; acetylcysteine, which benefits "
        "non-paracetamol causes as well; glucose and electrolyte support; "
        "early referral to a transplant unit against King's College "
        "criteria; avoid sedation. Note: INR is the prognostic marker here, "
        "so correcting it without active bleeding discards the best measure "
        "of trajectory.",
    "Septic arthritis":
        "Bacterial infection of a joint. Cartilage is destroyed within "
        "days, so this is a same-day emergency. Causes: Staphylococcus "
        "aureus most often; streptococci; Neisseria gonorrhoeae in young "
        "sexually active adults; Gram-negative bacilli in the elderly and "
        "immunosuppressed. Risk factors: prosthetic joint, rheumatoid "
        "arthritis, diabetes, injecting drug use, immunosuppression, "
        "overlying skin infection. Sx: a single hot swollen joint, severe "
        "pain on any movement, inability to weight-bear, fever. Ix: urgent "
        "joint aspiration before antibiotics for synovial white cell count, "
        "Gram stain, culture and crystal microscopy; blood cultures; CRP. "
        "Mx: flucloxacillin intravenously as empirical cover per eTG, "
        "vancomycin where MRSA is likely, ceftriaxone for gonococcal "
        "disease; joint washout or repeated aspiration alongside. Note: a "
        "synovial white cell count under 50 x 10^9/L does not exclude it, "
        "particularly in a prosthetic joint, and crystals do not exclude it "
        "either.",
    "Colorectal cancer":
        "Adenocarcinoma of the colon or rectum, and the second commonest "
        "cause of cancer death in Australia. Screening: the National Bowel "
        "Cancer Screening Program offers immunochemical faecal occult blood "
        "testing every two years from 45 to 74, with colonoscopy for a "
        "positive result. Causes: adenoma-carcinoma sequence through APC, "
        "KRAS and TP53; mismatch repair deficiency in Lynch syndrome; the "
        "serrated pathway through BRAF. Risk factors: inflammatory bowel "
        "disease, family history, processed meat, obesity, alcohol, "
        "smoking. Sx: right-sided disease gives iron deficiency anaemia and "
        "a mass; left-sided gives altered bowel habit, rectal bleeding, "
        "tenesmus and obstruction. Ix: colonoscopy with biopsy; staging CT "
        "of chest, abdomen and pelvis; MRI rectum for local staging and "
        "circumferential margin. Mx: resection; neoadjuvant "
        "chemoradiotherapy for locally advanced rectal disease; adjuvant "
        "oxaliplatin-based chemotherapy for stage III per eviQ.",
    "Anorexia nervosa":
        "Restriction of intake relative to requirements, with intense fear "
        "of weight gain and disturbed experience of body weight or shape. "
        "Epidemiology: onset usually in adolescence with female "
        "predominance; the highest mortality of any psychiatric disorder, "
        "from medical complications and from suicide. Complications: "
        "bradycardia, hypotension, hypothermia, prolonged QT, hypokalaemia, "
        "hypophosphataemia, amenorrhoea, reduced bone mineral density, "
        "dental erosion where there is purging. Ix: ECG, electrolytes, "
        "phosphate, magnesium, glucose, liver function, bone densitometry. "
        "Mx: medical stabilisation first, with thiamine before nutrition "
        "and daily phosphate, potassium and magnesium as intake increases; "
        "psychological therapy is definitive - CBT-E, MANTRA or specialist "
        "supportive clinical management in adults, family-based treatment "
        "in adolescents. Antidepressants do not restore weight. Australian "
        "notes: an Eating Disorder Plan funds extended psychological and "
        "dietetic sessions under Medicare. Note: DSM-5-TR sets no BMI "
        "threshold for diagnosis; BMI grades severity only.",
    "Peptic ulcer disease":
        "Mucosal break extending through the muscularis mucosae of the "
        "stomach or duodenum. Causes: Helicobacter pylori and NSAIDs "
        "account for nearly all of it, the latter by suppressing mucosal "
        "prostaglandins; gastrinoma is rare. Sx: epigastric burning pain. "
        "Duodenal ulcer eases with food and wakes the patient at night; "
        "gastric ulcer is provoked by eating and comes with weight loss. "
        "Complications: bleeding with haematemesis or melaena, perforation, "
        "gastric outlet obstruction, penetration into the pancreas. Ix: "
        "gastroscopy is definitive and every gastric ulcer is biopsied to "
        "exclude malignancy; urea breath test or faecal antigen for H. "
        "pylori, off proton pump inhibitor for two weeks. Mx: eradication "
        "where H. pylori is present, esomeprazole with amoxycillin and "
        "clarithromycin for seven days per eTG; stop the NSAID; endoscopic "
        "haemostasis for bleeding; surgery for perforation. Note: serology "
        "cannot separate current from past infection and must not be used "
        "to confirm eradication.",
    "Hypokalaemia":
        "Serum potassium below 3.5 mmol/L; below 2.5 mmol/L is "
        "life-threatening. Causes: renal loss through diuretics, "
        "hyperaldosteronism, Cushing syndrome or renal tubular acidosis; "
        "gastrointestinal loss through vomiting or diarrhoea; shift into "
        "cells with insulin, beta-2 agonists or alkalosis. Sx: weakness, "
        "cramps, ileus, polyuria and palpitations, with rhabdomyolysis when "
        "severe. Ix: ECG shows T-wave flattening, U waves, ST depression "
        "and a long QU interval; check magnesium, bicarbonate and urinary "
        "potassium. Mx: oral potassium chloride if mild; intravenous "
        "potassium chloride for severe or symptomatic hypokalaemia, no "
        "faster than 10 mmol/hour peripherally and faster only with central "
        "access and cardiac monitoring; replace magnesium alongside. Note: "
        "potassium will not correct while magnesium is low, because "
        "magnesium depletion disinhibits the ROMK channel and drives renal "
        "potassium wasting.",
    "Aortic dissection":
        "Intimal tear allowing blood into the aortic media and creating a "
        "false lumen. Classification: Stanford A involves the ascending "
        "aorta and is surgical; Stanford B is confined distal to the left "
        "subclavian artery. Risk factors: hypertension above all, bicuspid "
        "aortic valve, Marfan and Ehlers-Danlos syndromes, Turner syndrome, "
        "coarctation, cocaine, third trimester pregnancy. Sx: abrupt "
        "tearing chest or interscapular pain, maximal at onset; blood "
        "pressure differential over 20 mmHg between arms; new aortic "
        "regurgitation; stroke, paraplegia or limb ischaemia from branch "
        "vessel occlusion. Ix: CT aortography; transoesophageal "
        "echocardiography if too unstable to move. A normal chest "
        "radiograph excludes nothing. Mx: rate control before pressure "
        "control - intravenous esmolol or labetalol to a heart rate under "
        "60, then a vasodilator to systolic 100 to 120 mmHg. Type A goes to "
        "theatre immediately; uncomplicated type B is medical; complicated "
        "type B gets endovascular repair.",
    "Rhabdomyolysis":
        "Skeletal muscle breakdown releasing myoglobin, potassium, "
        "phosphate and creatine kinase into the circulation. Causes: crush "
        "injury, a long lie after a fall, seizures, extreme exertion, "
        "statins, alcohol, psychostimulants, heat stroke, neuroleptic "
        "malignant syndrome. Sx: myalgia, weakness and dark cola-coloured "
        "urine, though the full triad appears in a minority. Ix: creatine "
        "kinase above five times the upper limit confirms it; urine "
        "dipstick positive for blood with no red cells on microscopy; "
        "follow potassium, phosphate, calcium, urate and creatinine. Mx: "
        "early high-volume 0.9% sodium chloride titrated to urine output "
        "above 1 to 2 mL/kg/hour; treat hyperkalaemia; dialysis for "
        "refractory acidosis, hyperkalaemia or oliguric acute kidney "
        "injury. Note: early hypocalcaemia reflects calcium deposition in "
        "damaged muscle and rebounds during recovery, so leave it alone "
        "unless symptomatic.",
    "Infective endocarditis":
        "Infection of the endocardium, usually a valve, and usually one "
        "already abnormal - prosthetic, rheumatic, congenital, previously "
        "infected - or in the setting of injecting drug use or an "
        "intracardiac device. Causes: Staphylococcus aureus commonest "
        "overall and in injecting drug use; viridans streptococci after "
        "oral bacteraemia; coagulase-negative staphylococci on prosthetic "
        "valves; enterococci, HACEK organisms and Coxiella burnetii make up "
        "most of the rest. Sx: fever with a new murmur, embolic stroke, or "
        "heart failure from acute regurgitation; peripheral stigmata are "
        "uncommon but specific. Ix: three sets of blood cultures before "
        "antibiotics, then echocardiography, transoesophageal if the "
        "transthoracic is unrevealing; modified Duke criteria. Mx: "
        "prolonged intravenous antibiotics directed at the organism, "
        "empirically flucloxacillin with benzylpenicillin and gentamicin "
        "per eTG; surgery for heart failure, uncontrolled infection, "
        "abscess or a large mobile vegetation. Note: rheumatic heart "
        "disease remains a major substrate in Aboriginal and Torres Strait "
        "Islander communities.",
    "Coeliac disease":
        "Immune-mediated enteropathy triggered by gluten in HLA-DQ2 or DQ8 "
        "carriers, causing villous atrophy and malabsorption. Sx: "
        "diarrhoea, steatorrhoea, bloating and weight loss, although the "
        "commonest adult presentation is iron deficiency anaemia with no "
        "bowel symptoms at all. Extraintestinal: dermatitis herpetiformis, "
        "osteoporosis, transaminitis, gluten ataxia, peripheral neuropathy, "
        "hyposplenism. Associations: type 1 diabetes, autoimmune thyroid "
        "disease, selective IgA deficiency, Down syndrome. Ix: anti-tissue "
        "transglutaminase IgA with a total IgA, taken while still eating "
        "gluten; duodenal biopsy showing intraepithelial lymphocytosis, "
        "crypt hyperplasia and villous atrophy confirms it in adults. Mx: "
        "lifelong gluten-free diet with dietitian input; replace iron, "
        "folate, B12, calcium and vitamin D; bone densitometry; "
        "pneumococcal vaccination for hyposplenism. Note: serology "
        "normalises on a gluten-free diet, so anyone already avoiding "
        "gluten needs a formal gluten challenge before testing.",
    "Ankylosing spondylitis":
        "Chronic inflammatory arthritis of the sacroiliac joints and spine, "
        "the radiographic form of axial spondyloarthritis; over 90% carry "
        "HLA-B27. Epidemiology: onset before 45 and usually in the "
        "twenties, with male predominance. Sx: inflammatory back pain with "
        "morning stiffness beyond an hour that eases with movement and "
        "worsens with rest; alternating buttock pain; reduced chest "
        "expansion; enthesitis at the Achilles and plantar fascia. "
        "Extra-articular: acute anterior uveitis, inflammatory bowel "
        "disease, psoriasis, aortic regurgitation, conduction block, apical "
        "pulmonary fibrosis. Ix: MRI of the sacroiliac joints shows bone "
        "marrow oedema years before radiographic sacroiliitis; HLA-B27 and "
        "CRP support the diagnosis without making it. Mx: continuous "
        "exercise and physiotherapy are the mainstay; NSAIDs first-line; a "
        "TNF or IL-17 inhibitor where disease stays active, which on the "
        "PBS requires a BASDAI of 4 or more after an adequate NSAID trial. "
        "Conventional DMARDs do not work for axial disease.",
    "Serotonin syndrome":
        "Excess serotonergic activity, usually from a drug combination, "
        "developing within hours rather than days. Causes: an SSRI or SNRI "
        "with a monoamine oxidase inhibitor is the most dangerous pairing; "
        "also tramadol, pethidine, fentanyl, linezolid, triptans, lithium, "
        "St John's wort, MDMA and cocaine. Sx: neuromuscular excitation "
        "with clonus, hyperreflexia and tremor, greatest in the lower "
        "limbs; autonomic instability with hyperthermia, tachycardia and "
        "diaphoresis; agitation and delirium. Criteria: Hunter criteria "
        "require a serotonergic agent plus spontaneous clonus, or inducible "
        "or ocular clonus with agitation or diaphoresis, or tremor with "
        "hyperreflexia, or hypertonia with temperature above 38.5 C and "
        "clonus. Differential: neuroleptic malignant syndrome evolves over "
        "days with lead-pipe rigidity and hyporeflexia. Mx: stop the "
        "offending drugs; benzodiazepines for agitation and rigidity; "
        "active cooling; oral cyproheptadine; intubation and paralysis if "
        "hyperthermia is uncontrolled.",

    # ═══════ BATCH 2: ordered by measured deck frequency ════════════════
    #
    # Selected by querying deck:active::current::* through AnkiMCP, not
    # by rendered height. The two orderings disagree: Breast cancer is
    # the third tallest un-overridden entry at 933px and returns two
    # notes, while Lung cancer returns 52. Acute appendicitis returns
    # zero. Stem queries were used rather than exact phrases because
    # findNotes does not resolve aliases - "acute pancreatitis" returns
    # 3 where "pancreatitis" returns 14.

    "Lung cancer": (
        "Malignancy arising from bronchial or alveolar epithelium, split "
        "for management into non-small cell (about 85%) and small cell "
        "(about 15%). Causes: smoking dominates; also asbestos, radon, air "
        "pollution and prior thoracic radiotherapy. Adenocarcinoma is the "
        "type most often seen in never-smokers. Clinical features: cough, "
        "haemoptysis, dyspnoea, weight loss. Local invasion gives "
        "hoarseness from recurrent laryngeal palsy, SVC obstruction, or "
        "Pancoast syndrome with Horner and T1 wasting. Ix: CT chest and "
        "upper abdomen, then PET-CT for staging; tissue by bronchoscopy, "
        "EBUS or CT-guided biopsy; molecular testing (EGFR, ALK, ROS1) and "
        "PD-L1 on non-small cell. Mx: surgery for early non-small cell with "
        "adjuvant chemotherapy, or stereotactic radiotherapy if inoperable. "
        "Locally advanced disease gets chemoradiotherapy then durvalumab. "
        "Metastatic disease is directed by molecular result - targeted "
        "therapy where a driver is present, otherwise immunotherapy with "
        "chemotherapy. Small cell is chemotherapy and radiotherapy from the "
        "outset. Note: paraneoplastic syndromes point to histology - SIADH "
        "and Lambert-Eaton with small cell, PTHrP hypercalcaemia with "
        "squamous."
    ),

    "Lithium toxicity": (
        "Toxicity from a drug with a therapeutic index narrow enough that "
        "the treatment range and the toxic range nearly touch. Causes: "
        "dehydration, intercurrent illness, and any drug that cuts renal "
        "clearance - thiazides, ACE inhibitors and ARBs, NSAIDs. Acute "
        "overdose and chronic accumulation behave differently; chronic is "
        "the more dangerous at any given level. Clinical features: coarse "
        "tremor, ataxia, dysarthria, vomiting and diarrhoea early; then "
        "confusion, myoclonus, seizures and arrhythmia. Neurological signs, "
        "not the number, drive urgency. Ix: lithium level (timed 12 hours "
        "post-dose), EUC, calcium, TFTs, ECG. Repeat levels - a single "
        "value taken early after ingestion understates a rising "
        "concentration. Mx: stop lithium, correct volume with sodium "
        "chloride 0.9%, and discuss with the Poisons Information Centre on "
        "13 11 26. Haemodialysis for severe neurotoxicity, renal failure or "
        "very high levels. Note: SILENT - persistent cerebellar deficit "
        "after apparent recovery - is the reason not to wait and watch."
    ),

    "Miscarriage": (
        "Loss of pregnancy before 20 weeks, occurring in roughly one in "
        "five recognised pregnancies. Types: threatened (bleeding, closed "
        "os, viable); inevitable (open os); incomplete; complete; missed "
        "(no cardiac activity, closed os); septic. Ix: transvaginal "
        "ultrasound; serial beta-hCG where the location is uncertain; blood "
        "group and antibody screen. Mx: expectant, medical with "
        "misoprostol, or surgical evacuation - choice is largely the "
        "woman's, guided by bleeding, sepsis and preference. Give anti-D to "
        "Rh-negative women. Offer follow-up and written information; "
        "recurrence risk after one loss is not meaningfully raised. Red "
        "flags: pain with a positive test and an empty uterus is ectopic "
        "until excluded; fever, offensive loss or tenderness suggests "
        "septic miscarriage and needs antibiotics and urgent evacuation. "
        "Note: investigate for a cause after three consecutive losses, or "
        "earlier if there is a second-trimester loss."
    ),

    "Polycystic ovary syndrome": (
        "Common endocrine disorder of hyperandrogenism and ovulatory "
        "dysfunction, diagnosed on the Rotterdam criteria - two of three: "
        "oligo-ovulation, clinical or biochemical hyperandrogenism, "
        "polycystic ovarian morphology. Pathophysiology: insulin resistance "
        "drives ovarian androgen production and lowers SHBG, raising free "
        "testosterone. Clinical features: oligomenorrhoea, hirsutism, acne, "
        "subfertility, acanthosis nigricans. Ix: testosterone and SHBG with "
        "free androgen index, LH and FSH, prolactin and TFTs to exclude "
        "mimics; 17-hydroxyprogesterone if androgens are markedly raised; "
        "oral glucose tolerance test. Ultrasound is not required if the "
        "other two criteria are met, and is not used within 8 years of "
        "menarche. Mx: weight management is first-line and improves every "
        "domain. Combined oral contraceptive for cycle control and "
        "hyperandrogenism; metformin for metabolic features; letrozole "
        "first-line for ovulation induction. Note: anovulatory cycles leave "
        "unopposed oestrogen, so endometrial protection matters - "
        "investigate cycles longer than 90 days."
    ),

    "Cystic fibrosis": (
        "Autosomal recessive CFTR defect producing thick secretions across "
        "exocrine organs, with F508del the commonest Australian variant. "
        "Clinical features: recurrent chest infection with bronchiectasis, "
        "pancreatic insufficiency with steatorrhoea and failure to thrive, "
        "and male infertility from absent vas deferens. Meconium ileus is "
        "the neonatal presentation. Ix: newborn screening by immunoreactive "
        "trypsinogen then genetic panel; sweat chloride above 60 mmol/L "
        "confirms. Mx: multidisciplinary CF centre care - airway clearance "
        "physiotherapy, inhaled mucolytics, pancreatic enzyme replacement "
        "with fat-soluble vitamins, and aggressive treatment of "
        "exacerbations. CFTR modulators (elexacaftor-tezacaftor-ivacaftor) "
        "are PBS-listed for eligible genotypes and have changed the "
        "trajectory of the disease. Note: chronic Pseudomonas aeruginosa "
        "colonisation marks a step down in prognosis, which is why "
        "segregation and early eradication are taken seriously. Red flags: "
        "haemoptysis, pneumothorax and distal intestinal obstruction "
        "syndrome are the acute presentations."
    ),

    "Pre-eclampsia": (
        "New hypertension after 20 weeks with evidence of maternal organ "
        "dysfunction or uteroplacental insufficiency. Proteinuria is "
        "supportive but no longer required. Pathophysiology: failed spiral "
        "artery remodelling gives placental ischaemia and release of "
        "antiangiogenic factors, producing systemic endothelial "
        "dysfunction. Clinical features: headache, visual disturbance, "
        "epigastric or right upper quadrant pain, oedema, hyperreflexia. "
        "Ix: BP, urine protein-creatinine ratio, FBC, EUC, LFT, urate, and "
        "fetal assessment with CTG and growth ultrasound. Mx: the only cure "
        "is delivery. Treat severe hypertension with labetalol, nifedipine "
        "or hydralazine; magnesium sulfate for seizure prophylaxis and "
        "treatment; corticosteroids for fetal lung maturity before 34 "
        "weeks. Timing of birth balances maternal deterioration against "
        "prematurity. Note: aspirin from 12 weeks reduces recurrence in "
        "women at high risk, and calcium supplementation helps where "
        "dietary intake is low. Red flags: HELLP, eclampsia, abruption and "
        "pulmonary oedema."
    ),

    "Paracetamol overdose": (
        "Australia's commonest deliberate self-poisoning, and one where the "
        "antidote works reliably if given early enough. Pathophysiology: "
        "therapeutic doses are conjugated; in overdose these pathways "
        "saturate and NAPQI accumulates, depleting glutathione and causing "
        "centrilobular hepatic necrosis. Clinical features: asymptomatic or "
        "nausea for the first 24 hours, then right upper quadrant pain and "
        "rising transaminases at 24-72 hours, then encephalopathy and "
        "coagulopathy. The well-looking patient at presentation is the "
        "trap. Ix: paracetamol level at 4 hours or later post-ingestion "
        "plotted on the Australian nomogram; ALT, INR, EUC, BGL, VBG. Mx: "
        "activated charcoal within 2 hours of a significant ingestion. "
        "Acetylcysteine by the guideline regimen, started without waiting "
        "for a level if presentation is late, staggered, or the time is "
        "unknown. Discuss with the Poisons Information Centre on 13 11 26. "
        "Note: refer for transplant assessment using the King's College "
        "criteria - acidosis, or the triad of INR above 6.5, creatinine "
        "above 300 micromol/L and grade III-IV encephalopathy."
    ),

    "Oesophageal varices": (
        "Portosystemic collaterals in the lower oesophagus that form when "
        "portal pressure rises, and bleed with high mortality. "
        "Pathophysiology: a hepatic venous pressure gradient above 12 mmHg "
        "is needed for varices to bleed, which is why the gradient rather "
        "than the varix size drives risk. Ix: gastroscopy is both "
        "diagnostic and therapeutic; screen at diagnosis of cirrhosis and "
        "periodically thereafter. Mx (acute bleeding): resuscitate with a "
        "restrictive transfusion target of about 70 g/L, since "
        "over-transfusion raises portal pressure. Give a vasoactive agent "
        "(octreotide or terlipressin) and prophylactic antibiotics, then "
        "endoscopic band ligation within 12 hours. Balloon tamponade or "
        "TIPS if bleeding continues. Prevention: non-selective beta-blocker "
        "or band ligation for primary prophylaxis; both after a bleed. "
        "Note: antibiotics are not optional - they reduce mortality in "
        "variceal bleeding independently of controlling the bleed itself."
    ),

    "Acute pancreatitis": (
        "Acute pancreatic inflammation diagnosed on two of three: "
        "characteristic pain, lipase above three times the upper limit, or "
        "imaging. Causes: gallstones and alcohol account for most; also "
        "hypertriglyceridaemia, hypercalcaemia, drugs, post-ERCP and "
        "trauma. Clinical features: severe epigastric pain radiating to the "
        "back, relieved by sitting forward, with vomiting. Cullen and Grey "
        "Turner signs are late and rare. Ix: lipase (more specific than "
        "amylase), LFT and lipids to find the cause, calcium, and abdominal "
        "ultrasound for gallstones in everyone. CT is for complications, "
        "not diagnosis, and is best deferred 72 hours. Mx: aggressive fluid "
        "resuscitation with compound sodium lactate, analgesia, and early "
        "enteral feeding rather than fasting. Antibiotics only for proven "
        "infection. Cholecystectomy during the same admission for mild "
        "gallstone pancreatitis. Note: severity is a moving target - "
        "reassess rather than scoring once, and persistent organ failure "
        "beyond 48 hours defines severe disease."
    ),

    "Diabetes insipidus": (
        "Failure to concentrate urine, from deficient ADH (cranial) or "
        "renal resistance to it (nephrogenic), now often called arginine "
        "vasopressin deficiency and resistance. Causes: cranial from "
        "pituitary surgery, tumour, trauma or infiltration; nephrogenic "
        "from lithium, hypercalcaemia, hypokalaemia or inherited defects. "
        "Clinical features: polyuria of more than 3 L a day, nocturia and "
        "intense thirst, with hypernatraemia if access to water is "
        "restricted. Ix: paired serum and urine osmolality - dilute urine "
        "against concentrated plasma is the finding. Water deprivation "
        "testing with desmopressin separates the two types; copeptin has "
        "largely replaced it where available. MRI pituitary for cranial "
        "causes. Mx: desmopressin for cranial disease. Nephrogenic disease "
        "needs the cause removed, with a thiazide and a low-solute diet. "
        "Note: the danger is not the polyuria but losing access to water - "
        "an unconscious or post-operative patient can become profoundly "
        "hypernatraemic within hours."
    ),

    "Phaeochromocytoma": (
        "Catecholamine-secreting tumour of adrenal chromaffin cells; the "
        "extra-adrenal counterpart is a paraganglioma. Epidemiology: up to "
        "40% are germline, so all patients are offered genetic testing - "
        "SDHx, VHL, RET and NF1. Clinical features: the classic triad is "
        "episodic headache, sweating and palpitations on a background of "
        "hypertension, though presentation is often just resistant or "
        "paroxysmal hypertension. Ix: plasma free metanephrines or 24-hour "
        "urinary metanephrines, taken supine after 30 minutes rest. Locate "
        "with CT or MRI once biochemistry is positive, then functional "
        "imaging. Mx: alpha blockade with phenoxybenzamine or prazosin for "
        "10-14 days first, adding a beta-blocker only afterwards, then "
        "surgical resection with an experienced anaesthetic team. Note: "
        "beta blockade before alpha blockade leaves unopposed alpha "
        "stimulation and can precipitate hypertensive crisis - the sequence "
        "is the exam point and the clinical one. Red flags: crisis can be "
        "triggered by anaesthesia, contrast or abdominal palpation."
    ),

    "Hyperosmolar hyperglycaemic state": (
        "Severe hyperglycaemia with marked hyperosmolality and profound "
        "volume depletion, without significant ketosis - residual insulin "
        "is enough to suppress ketogenesis but not gluconeogenesis. "
        "Epidemiology: type 2 diabetes, usually older, often precipitated "
        "by infection, myocardial infarction or missed medication. Clinical "
        "features: days to weeks of polyuria and thirst, then confusion "
        "progressing to coma. Focal neurological signs and seizures occur "
        "and reverse with treatment. Ix: BGL usually above 30 mmol/L, "
        "effective osmolality above 320 mOsm/kg, pH above 7.3 with "
        "bicarbonate above 15, minimal ketones. Look for the precipitant. "
        "Mx: fluid is the treatment - sodium chloride 0.9%, replacing the "
        "deficit over 24-48 hours. Insulin at a lower rate than in DKA, and "
        "only once fluids are running. Replace potassium. "
        "Thromboprophylaxis, since the thrombotic risk is high. Note: "
        "lowering osmolality too fast risks cerebral oedema, so aim for a "
        "fall of no more than 3-8 mOsm/kg per hour."
    ),

    "Sickle cell disease": (
        "Autosomal recessive haemoglobinopathy in which HbS polymerises "
        "when deoxygenated, deforming red cells and causing vaso-occlusion "
        "and haemolysis. Clinical features: painful vaso-occlusive crises, "
        "dactylitis in infants, and functional asplenia from repeated "
        "infarction. Chronic haemolysis gives anaemia, gallstones and leg "
        "ulcers. Ix: haemoglobin electrophoresis or HPLC; film shows sickle "
        "cells and Howell-Jolly bodies. Mx: hydroxycarbamide raises HbF and "
        "reduces crises and mortality. Penicillin prophylaxis and full "
        "vaccination against encapsulated organisms. Crises need prompt "
        "analgesia including opioids, hydration, oxygen and a search for "
        "infection. Transfusion or exchange for stroke, acute chest "
        "syndrome or priapism. Note: fever in a functionally asplenic "
        "patient is a medical emergency, not a symptom to observe. Red "
        "flags: acute chest syndrome, stroke, splenic sequestration and "
        "aplastic crisis from parvovirus B19."
    ),

    "Bowel obstruction": (
        "Mechanical blockage of the intestinal lumen, classified by level "
        "and by whether the bowel is strangulated. Causes: adhesions "
        "dominate the small bowel, then hernia and malignancy; in the large "
        "bowel, malignancy, volvulus and diverticular stricture. Clinical "
        "features: colicky pain, vomiting (early in proximal, late in "
        "distal), distension and absolute constipation. Bowel sounds are "
        "tinkling then absent. Ix: CT abdomen with contrast identifies "
        "level, cause and strangulation. Erect chest film if perforation is "
        "suspected. EUC and VBG for lactate. Mx: drip and suck - "
        "nasogastric decompression, intravenous fluid and correction of "
        "electrolytes - is the initial approach for adhesional obstruction, "
        "and many settle. Surgery for strangulation, closed loop, "
        "perforation, or failure to resolve. Water-soluble contrast is both "
        "prognostic and mildly therapeutic. Red flags: constant rather than "
        "colicky pain, tachycardia, fever, peritonism or rising lactate "
        "mean strangulation and immediate operation."
    ),

    "Nephrotic syndrome": (
        "Proteinuria above 3.5 g a day with hypoalbuminaemia and oedema, "
        "from podocyte injury and loss of glomerular charge selectivity. "
        "Causes: minimal change disease in children; membranous "
        "nephropathy, focal segmental glomerulosclerosis and diabetic "
        "nephropathy in adults. Secondary causes include SLE, amyloid, "
        "hepatitis B and C, and malignancy. Clinical features: periorbital "
        "and peripheral oedema, frothy urine, and in severe cases ascites "
        "and pleural effusions. Ix: urine protein-creatinine ratio, "
        "albumin, lipids, EUC; immunology screen; PLA2R antibody for "
        "membranous disease. Renal biopsy in adults, but not usually in "
        "children who respond to steroids. Mx: salt restriction and loop "
        "diuretics for oedema; ACE inhibitor or ARB to reduce proteinuria; "
        "statin; treat the underlying cause. Corticosteroids for minimal "
        "change disease. Note: loss of antithrombin III in the urine makes "
        "this a prothrombotic state, and renal vein thrombosis is the "
        "characteristic complication."
    ),

    # ═══════ BATCH 3: ordered by measured deck frequency ════════════════
    #
    # Same method as batch 2, and the same two traps confirmed again.
    # Exact phrases undercount: "ectopic pregnancy" returns 0 where
    # the stem `ectopic` returns 13. And a combined OR query hides
    # which term carried it - `"placenta praevia" OR abruption`
    # returned 27, but praevia alone returns 0, so all 27 were
    # abruption and Placenta praevia was correctly left out.
    #
    # Frequencies: abruption 27, aortic aneurysm 15, portal
    # hypertension 15, ectopic 13, PAD 8, incontinence 8, the three
    # headaches 8 combined, prostate cancer 7, ATN 5, osteomyelitis 4,
    # subdural 3, chronic pancreatitis within pancreatitis 14.

    "Abruption": (
        "Premature separation of a normally sited placenta after 20 weeks, "
        "and the obstetric emergency in which the visible blood loss "
        "understates the real one. Causes: hypertension and pre-eclampsia, "
        "trauma, smoking and cocaine, polyhydramnios with rapid "
        "decompression, and previous abruption. Clinical features: constant "
        "abdominal pain with a woody, tender uterus, dark vaginal bleeding, "
        "and fetal compromise. Concealed abruption bleeds behind the "
        "placenta with little or nothing revealed. Ix: this is a clinical "
        "diagnosis - ultrasound cannot exclude it. FBC, coagulation "
        "profile, fibrinogen, group and hold or crossmatch, Kleihauer, and "
        "continuous CTG. Mx: resuscitate, give oxygen and large-bore "
        "access, and deliver. Caesarean for fetal compromise or maternal "
        "instability; vaginal birth may be appropriate after fetal death. "
        "Anti-D for Rh-negative women. Corticosteroids if preterm and the "
        "situation allows. Note: a falling fibrinogen is the earliest "
        "marker of the consumptive coagulopathy abruption causes, and it "
        "falls before the INR moves."
    ),

    "Aortic aneurysm": (
        "Permanent dilatation of the aorta to more than 1.5 times its "
        "normal diameter, most often infrarenal abdominal. Causes: "
        "atherosclerotic degeneration with smoking as the strongest "
        "modifiable risk; connective tissue disease (Marfan, vascular "
        "Ehlers-Danlos) in younger patients; less often infection or "
        "arteritis. Clinical features: usually silent and found "
        "incidentally. A pulsatile expansile abdominal mass, back or flank "
        "pain, or the triad of pain, hypotension and a pulsatile mass in "
        "rupture. Ix: ultrasound for detection and surveillance; CT "
        "angiography before repair and in suspected rupture if the patient "
        "is stable. Mx: modify risk - stop smoking, treat blood pressure, "
        "statin and antiplatelet. Surveillance by size, with elective "
        "repair considered at about 55 mm for abdominal aneurysms, or "
        "smaller if growing quickly, symptomatic, or in a woman. "
        "Endovascular or open repair depending on anatomy and fitness. Red "
        "flags: sudden severe back or abdominal pain with haemodynamic "
        "compromise is rupture - straight to theatre, not to the scanner."
    ),

    "Portal hypertension": (
        "A hepatic venous pressure gradient above 5 mmHg, becoming "
        "clinically significant above 10 and the threshold for variceal "
        "bleeding above 12. Causes: classified by site. Prehepatic is "
        "portal vein thrombosis; hepatic is cirrhosis in most Australian "
        "practice, also schistosomiasis and nodular regenerative "
        "hyperplasia; posthepatic is Budd-Chiari or constrictive "
        "pericarditis. Clinical features: the consequences rather than the "
        "pressure - varices, ascites, splenomegaly with thrombocytopenia, "
        "caput medusae, and hepatic encephalopathy from portosystemic "
        "shunting. Ix: ultrasound with Doppler for flow direction and "
        "portal vein patency; gastroscopy for varices; ascitic tap with a "
        "serum-ascites albumin gradient of 11 g/L or more confirming portal "
        "origin. Mx: treat the cause, non-selective beta-blockade to lower "
        "the gradient, and manage each complication on its own terms. TIPS "
        "for refractory ascites or bleeding. Note: thrombocytopenia here "
        "reflects splenic sequestration, not marrow failure, and does not "
        "need treating on its own."
    ),

    "Ectopic pregnancy": (
        "Implantation outside the uterine cavity, most often ampullary "
        "tubal, and the leading cause of first-trimester maternal death. "
        "Causes: anything that damages tubal transport - previous ectopic, "
        "pelvic inflammatory disease, tubal surgery, endometriosis, "
        "smoking, and pregnancy with an intrauterine device in place. "
        "Clinical features: amenorrhoea then unilateral pelvic pain and "
        "bleeding at 6-8 weeks. Shoulder tip pain, syncope or peritonism "
        "suggest rupture with haemoperitoneum. Ix: urine beta-hCG then "
        "transvaginal ultrasound. Above the discriminatory zone of about "
        "1,500 IU/L an empty uterus is ectopic until proven otherwise; "
        "below it, serial hCG that fails to double in 48 hours points the "
        "same way. Mx: methotrexate for a stable, unruptured, small ectopic "
        "with a low hCG and no fetal cardiac activity, with hCG followed to "
        "zero. Laparoscopic salpingectomy for rupture, instability, or "
        "failed medical management. Anti-D if Rh-negative. Red flags: "
        "haemodynamic instability means theatre, not another scan."
    ),

    "Peripheral arterial disease": (
        "Atherosclerotic narrowing of the limb arteries, and a marker of "
        "systemic vascular risk as much as a limb problem. Clinical "
        "features: intermittent claudication, reproducible at a fixed "
        "distance and relieved by rest. Progression gives rest pain "
        "relieved by hanging the leg down, then ulceration and gangrene. "
        "Signs are absent pulses, hair loss, cool shiny skin and delayed "
        "capillary return. Ix: ankle-brachial index - below 0.9 is "
        "diagnostic, above 1.4 suggests incompressible calcified vessels "
        "and is unreliable, typically in diabetes or chronic kidney "
        "disease. Duplex ultrasound, then CT or MR angiography before "
        "intervention. Mx: supervised exercise therapy is first-line for "
        "claudication and outperforms most expectations. Stop smoking, "
        "antiplatelet, high-intensity statin, and tight glycaemic and blood "
        "pressure control. Revascularisation for chronic limb-threatening "
        "ischaemia or lifestyle-limiting symptoms that fail conservative "
        "care. Note: beta-blockers are not contraindicated, despite the "
        "persistent belief that they are."
    ),

    "Urinary incontinence": (
        "Involuntary loss of urine, classified by mechanism because "
        "treatment differs entirely between the types. Types: stress, from "
        "urethral sphincter weakness; urgency, from detrusor overactivity; "
        "mixed; overflow, from chronic retention; and functional, where "
        "continence fails for reasons outside the urinary tract. Ix: "
        "bladder diary, urinalysis to exclude infection, post-void "
        "residual, and examination for prolapse or atrophy. Urodynamics "
        "only before surgery or when the picture is unclear. Mx: pelvic "
        "floor muscle training for at least three months is first-line for "
        "stress incontinence. Bladder training for urgency, then an "
        "antimuscarinic or mirabegron - prefer mirabegron in older "
        "patients, since antimuscarinic anticholinergic load is associated "
        "with cognitive decline. Topical oestrogen for genitourinary "
        "syndrome of menopause. Surgery for stress incontinence that fails "
        "conservative care. Note: treat constipation, review diuretics and "
        "caffeine, and check for retention before escalating - reversible "
        "contributors are common and easily missed."
    ),

    "Cluster headache": (
        "The most severe of the trigeminal autonomic cephalalgias, and "
        "distinctive enough that the history alone usually makes it. "
        "Clinical features: strictly unilateral, excruciating orbital or "
        "temporal pain lasting 15 to 180 minutes, once to eight times a "
        "day, in bouts of weeks to months. Ipsilateral autonomic features - "
        "lacrimation, conjunctival injection, rhinorrhoea, ptosis, miosis. "
        "Patients are restless and pace, unlike migraine. Epidemiology: "
        "more common in men, often with nocturnal attacks that wake at a "
        "consistent hour, and alcohol triggers during a bout only. Ix: "
        "clinical, but image with MRI at least once to exclude a pituitary "
        "or posterior fossa lesion. Mx (acute attack): high-flow oxygen "
        "12-15 L/min via a non-rebreather, or subcutaneous sumatriptan. "
        "Oral triptans are too slow. Prevention: verapamil is first-line, "
        "with ECG monitoring as the dose rises; a short prednisolone course "
        "or greater occipital nerve block can bridge until it works."
    ),

    "Tension headache": (
        "The commonest primary headache, and the one most often "
        "over-investigated and under-managed. Clinical features: bilateral, "
        "pressing or tightening, mild to moderate, not aggravated by "
        "routine activity, without vomiting. Photophobia or phonophobia may "
        "occur but not both. Pericranial tenderness is common. "
        "Classification: episodic if fewer than 15 days a month, chronic if "
        "15 or more for over three months. Ix: none if the history is "
        "typical and examination normal. Mx: simple analgesia for "
        "infrequent attacks, limited to fewer than 15 days a month. "
        "Amitriptyline is the best-supported preventer for chronic tension "
        "headache. Address sleep, posture, stress and neck pain, since "
        "these do more work than the medication does. Note: the single most "
        "useful question in a frequent headache is how many days a month "
        "analgesia is taken - medication overuse converts episodic headache "
        "into chronic daily headache and no preventer works until it is "
        "withdrawn."
    ),

    "Medication overuse headache": (
        "Headache on 15 or more days a month in someone with a pre-existing "
        "primary headache who is regularly overusing acute treatment. Dx: "
        "the thresholds are 10 days a month or more for triptans, opioids, "
        "ergots and combination analgesics, and 15 days a month or more for "
        "simple analgesics such as paracetamol and NSAIDs. Clinical "
        "features: a headache that has crept from episodic to near-daily, "
        "often present on waking, with the original headache type still "
        "recognisable underneath. Ix: none beyond excluding a secondary "
        "cause if red flags are present. The diagnosis is made on the drug "
        "history. Mx: withdraw the overused medication, either abruptly or "
        "by taper, with a clear warning that headache worsens for one to "
        "two weeks first. Start a preventer at the same time. Review at "
        "four to twelve weeks; most improve substantially. Note: opioids "
        "and codeine-containing combinations are the worst offenders and "
        "the hardest to withdraw, which is a reason not to start them for "
        "headache at all."
    ),

    "Prostate cancer": (
        "Adenocarcinoma of the prostate, usually peripheral zone, with a "
        "natural history slow enough that overtreatment is a real harm. "
        "Epidemiology: the commonest cancer in Australian men. Risk rises "
        "with age, family history and African ancestry. Clinical features: "
        "usually asymptomatic when localised. Lower urinary tract symptoms "
        "more often reflect benign hyperplasia. Bone pain suggests "
        "metastatic disease, which is characteristically sclerotic. Ix: PSA "
        "with digital rectal examination, then multiparametric MRI before "
        "biopsy, then transperineal biopsy. Grade with the ISUP grade "
        "group. Stage with PSMA PET where indicated. Mx: active "
        "surveillance for low-risk disease, which is the default rather "
        "than a compromise. Radical prostatectomy or radiotherapy for "
        "intermediate and high risk. Androgen deprivation for advanced "
        "disease, with an androgen receptor pathway inhibitor or docetaxel "
        "added up front in metastatic disease. Note: population PSA "
        "screening is not recommended in Australia; the discussion is "
        "individual and should cover overdiagnosis explicitly."
    ),

    "Acute tubular necrosis": (
        "The commonest cause of intrinsic acute kidney injury in hospital, "
        "from ischaemic or toxic damage to tubular epithelium. Causes: "
        "ischaemic, following any sustained prerenal insult such as sepsis, "
        "hypovolaemia or cardiac surgery; or toxic, from aminoglycosides, "
        "contrast, cisplatin, or myoglobin in rhabdomyolysis. Clinical "
        "features: an oliguric phase, then a polyuric recovery phase as "
        "tubules regenerate before concentrating ability returns. Ix: "
        "urinary sodium above 40 mmol/L and fractional excretion of sodium "
        "above 2% distinguish it from prerenal injury, which conserves "
        "sodium avidly. Urine microscopy shows muddy brown granular casts "
        "and renal tubular epithelial cells. Mx: supportive. Restore "
        "perfusion, stop the nephrotoxin, avoid further insults, and "
        "dialyse for the usual indications. No agent shortens the course, "
        "and loop diuretics do not - they manage fluid, nothing more. Note: "
        "watch potassium and volume closely through the polyuric phase, "
        "when losses can be litres a day."
    ),

    "Osteomyelitis": (
        "Infection of bone, haematogenous in children and usually "
        "contiguous or secondary to vascular insufficiency in adults. "
        "Causes: Staphylococcus aureus dominates. Consider Salmonella in "
        "sickle cell disease, Pseudomonas after a penetrating foot injury "
        "through footwear, and polymicrobial flora in diabetic foot "
        "infection. Clinical features: local pain, warmth and swelling with "
        "fever in acute disease; a chronically discharging sinus or a "
        "non-healing ulcer in chronic disease. In diabetic foot, a probe "
        "reaching bone makes it likely. Ix: MRI is the imaging of choice "
        "and is positive early; plain films lag by two weeks. Blood "
        "cultures, CRP and ESR for monitoring. Bone biopsy for culture "
        "before antibiotics wherever possible - swabs of a sinus mislead. "
        "Mx: targeted antibiotics, typically intravenous initially, guided "
        "by eTG and culture, with surgical debridement of dead bone or "
        "infected hardware. Duration is weeks, not days. Note: "
        "culture-directed therapy matters more here than almost anywhere, "
        "because the course is long and relapse is common."
    ),

    "Subdural haematoma": (
        "Bleeding between dura and arachnoid from torn bridging veins, "
        "crossing suture lines and appearing crescentic on CT. "
        "Epidemiology: acute after significant trauma; chronic in older "
        "people, those on anticoagulants, and those with alcohol-related "
        "brain atrophy, where the causative injury may be trivial or not "
        "recalled. Clinical features: acute disease presents with impaired "
        "consciousness after trauma. Chronic disease presents insidiously "
        "with headache, confusion, gait disturbance or focal weakness, and "
        "is a reversible mimic of dementia. Ix: non-contrast CT head. Acute "
        "blood is hyperdense, chronic is hypodense, and subacute can be "
        "isodense to brain - look for midline shift and effaced sulci "
        "rather than the collection itself. Mx: reverse anticoagulation "
        "urgently and discuss with neurosurgery. Surgical evacuation by "
        "burr hole for symptomatic chronic collections, craniotomy for "
        "acute ones. Small asymptomatic collections may be observed. Red "
        "flags: falling GCS, anisocoria or a rising blood pressure with "
        "bradycardia mean herniation and immediate escalation."
    ),

    "Chronic pancreatitis": (
        "Irreversible fibrosis of the pancreas with progressive loss of "
        "exocrine and eventually endocrine function. Causes: alcohol is the "
        "commonest in Australia; also smoking, which is independently "
        "causative, genetic variants, obstruction, and autoimmune "
        "pancreatitis. Clinical features: recurrent or constant epigastric "
        "pain radiating to the back, steatorrhoea and weight loss once "
        "exocrine reserve falls below about 10%, and diabetes late. Ix: CT "
        "or MRCP showing calcification, ductal dilatation and atrophy; "
        "endoscopic ultrasound is most sensitive early. Faecal elastase for "
        "exocrine insufficiency. Lipase is often normal, which surprises "
        "people expecting it to be raised. Mx: stop alcohol and smoking - "
        "both change the trajectory. Pancreatic enzyme replacement with "
        "fat-soluble vitamins, structured analgesia, and screening for "
        "diabetes and osteoporosis. Endoscopic or surgical drainage for "
        "obstructing disease. Note: the diabetes here is type 3c - glucagon "
        "is lost alongside insulin, so hypoglycaemia is a genuine hazard of "
        "treatment."
    ),

    # ═══════ BATCH 4: ordered by measured deck frequency ════════════════
    #
    # Weighted toward Medicine and Psychiatry (MEDI6101), which is the
    # live rotation. Note the psych *vocabulary* needed nothing: all 53
    # entries in `psych` are already under cap, as are signs,
    # descriptive and preclinical. The psychiatric entries worth
    # rewriting live in `conditions`.
    #
    # Frequencies: amenorrhoea 30, rheumatic heart disease 15,
    # diverticular disease 13, CVST 12, haemorrhoids ~9, angle-closure
    # ~8, osteomalacia/rickets 6, anal fissure 5, uveitis 4,
    # Huntington 3, chronic fatigue syndrome within 3.

    "Amenorrhoea": (
        "Absence of menstruation. Primary means no menarche by 15 with "
        "secondary sexual characteristics, or by 13 without them; secondary "
        "means periods stopping for three cycles or six months. Causes: "
        "exclude pregnancy first, every time. Then by compartment - "
        "hypothalamic (functional, from energy deficit, excessive exercise "
        "or stress), pituitary (prolactinoma, Sheehan), ovarian (PCOS, "
        "premature ovarian insufficiency, Turner), or outflow tract "
        "(Asherman, imperforate hymen, Mullerian agenesis). Ix: beta-hCG, "
        "then FSH, LH, oestradiol, prolactin and TFTs. High FSH points to "
        "the ovary, low or normal FSH to the hypothalamus or pituitary. Add "
        "testosterone if virilised, karyotype in primary amenorrhoea, and "
        "pelvic ultrasound for anatomy. Mx: treat the cause. Restore energy "
        "balance in functional disease; oestrogen replacement in premature "
        "ovarian insufficiency; dopamine agonist for prolactinoma. Note: "
        "hypo-oestrogenism of any cause costs bone, so ask about duration "
        "and consider DXA - this is the harm that outlasts the amenorrhoea "
        "itself."
    ),

    "Rheumatic heart disease": (
        "Chronic valve damage following acute rheumatic fever, and in "
        "Australia a disease of profound inequity - rates among Aboriginal "
        "and Torres Strait Islander people are among the highest reported "
        "anywhere. Pathophysiology: molecular mimicry between group A "
        "streptococcal M protein and cardiac tissue drives autoimmune "
        "valvulitis. Clinical features: the mitral valve is affected most "
        "often, then aortic. Mitral stenosis gives exertional dyspnoea, "
        "atrial fibrillation and haemoptysis; regurgitation gives volume "
        "overload and heart failure. Ix: echocardiography defines and "
        "grades it, and detects subclinical disease in screening programs. "
        "ECG, and ASOT or anti-DNase B if acute rheumatic fever is "
        "suspected. Mx: secondary prophylaxis with benzathine "
        "benzylpenicillin G every 28 days is the single most important "
        "intervention and continues for years. Manage the valve lesion "
        "medically, then repair or replace. Register the patient with the "
        "state RHD control program. Note: acute rheumatic fever is "
        "notifiable, and diagnosis uses the Australian criteria, which "
        "differ from Jones in high-risk groups."
    ),

    "Diverticular disease": (
        "Herniation of colonic mucosa through the muscular wall at points "
        "where vasa recta penetrate, overwhelmingly sigmoid in Western "
        "populations. Classification: diverticulosis is the anatomical "
        "finding, diverticular disease is symptomatic, and diverticulitis "
        "is inflammation of a diverticulum. Clinical features: most "
        "diverticulosis is silent. Diverticulitis gives left iliac fossa "
        "pain, fever and altered bowel habit. Painless brisk rectal "
        "bleeding is the other presentation, from an eroded vas rectum. Ix: "
        "CT abdomen with contrast for acute diverticulitis, staging by the "
        "Hinchey classification. Colonoscopy is deferred six to eight weeks "
        "after an episode to exclude a masked malignancy, and is avoided "
        "acutely. Mx: uncomplicated diverticulitis in a well patient is "
        "managed without antibiotics in current Australian guidance - "
        "analgesia, fluids and review. Antibiotics for systemic upset, "
        "immune suppression or comorbidity. Percutaneous drainage for an "
        "abscess; surgery for perforation, obstruction or fistula. Note: "
        "the old advice to avoid nuts and seeds has been disproven and "
        "should not be repeated."
    ),

    "Cerebral venous sinus thrombosis": (
        "Thrombosis of the dural sinuses or cortical veins, causing raised "
        "intracranial pressure and venous infarction that does not respect "
        "arterial territories. Causes: prothrombotic states, especially "
        "pregnancy and the puerperium, combined oral contraceptive, "
        "thrombophilia and malignancy; or local causes such as mastoiditis "
        "or sinusitis. Clinical features: headache in most, often "
        "progressive over days and worse lying flat. Then seizures, focal "
        "deficits, papilloedema or encephalopathy. A young patient with a "
        "new persistent headache and a seizure is the pattern to recognise. "
        "Ix: CT or MR venography. Plain CT is normal in a large minority "
        "and a negative D-dimer does not exclude it either. Mx: "
        "anticoagulate with heparin even when there is haemorrhagic "
        "infarction - the bleeding is venous and secondary to the clot. "
        "Then oral anticoagulation for months. Treat seizures and raised "
        "pressure; endovascular therapy or decompression for deterioration. "
        "Note: investigate for an underlying thrombophilia and review "
        "hormonal contraception afterwards."
    ),

    "Haemorrhoids": (
        "Symptomatic enlargement and distal displacement of the normal anal "
        "cushions, which are vascular structures contributing to continence "
        "rather than varicose veins. Classification: internal haemorrhoids "
        "arise above the dentate line and are graded I to IV by prolapse "
        "and reducibility; external arise below it and are somatically "
        "innervated, which is why they hurt and internal ones usually do "
        "not. Clinical features: painless bright rectal bleeding on wiping "
        "or coating the stool, pruritus, and a palpable lump. Severe acute "
        "pain suggests thrombosis or a fissure instead. Ix: inspection, "
        "digital rectal examination and proctoscopy. Investigate the colon "
        "in anyone over 45, with iron deficiency, or with a change in bowel "
        "habit - attributing bleeding to haemorrhoids without looking is "
        "how bowel cancer is missed. Mx: fibre, fluid and avoiding "
        "straining are the foundation. Topical preparations give symptom "
        "relief only. Rubber band ligation for grades I to III; "
        "haemorrhoidectomy for grade IV or failed banding. Note: a "
        "thrombosed external haemorrhoid presenting within 72 hours can be "
        "excised under local anaesthetic."
    ),

    "Acute angle-closure glaucoma": (
        "Sudden obstruction of aqueous outflow at the trabecular meshwork "
        "by apposition of the peripheral iris, and a true ophthalmic "
        "emergency - vision is lost in hours. Epidemiology: hypermetropic "
        "eyes, older patients, women, and East Asian ancestry. Precipitated "
        "by dim light, and by anticholinergic, sympathomimetic and some "
        "antidepressant drugs. Clinical features: severe unilateral eye "
        "pain, blurred vision with haloes around lights, and a red eye. "
        "Nausea and vomiting are prominent enough that this is mistaken for "
        "an abdominal or neurological problem. The eye is hard, the cornea "
        "hazy, and the pupil mid-dilated and unreactive. Ix: tonometry - "
        "intraocular pressure is typically well above 40 mmHg. Gonioscopy "
        "confirms the closed angle. Mx: discuss with ophthalmology "
        "immediately. Lie the patient flat, give topical agents to lower "
        "pressure and constrict the pupil, and acetazolamide systemically. "
        "Definitive treatment is laser peripheral iridotomy, offered to the "
        "fellow eye as well. Red flags: any red painful eye with reduced "
        "vision needs a pressure measured before it is called "
        "conjunctivitis."
    ),

    "Osteomalacia": (
        "Defective mineralisation of osteoid in the mature skeleton, "
        "producing soft bone with a normal or increased matrix volume. "
        "Causes: vitamin D deficiency dominates - inadequate sun exposure, "
        "covering dress, dark skin, malabsorption, and chronic kidney or "
        "liver disease. Also hypophosphataemia from renal phosphate "
        "wasting, and long-term anticonvulsants. Clinical features: diffuse "
        "bone pain and proximal myopathy giving a waddling gait and "
        "difficulty rising from a chair. Fractures, and pseudofractures "
        "(Looser zones) on imaging. Ix: 25-hydroxyvitamin D, calcium, "
        "phosphate, ALP and PTH. The characteristic pattern is low or "
        "low-normal calcium and phosphate with raised ALP and secondary "
        "hyperparathyroidism. Mx: colecalciferol replacement, with calcium "
        "if dietary intake is poor, and correction of the underlying cause. "
        "Recheck at three months. Phosphate and calcitriol where the defect "
        "is renal phosphate wasting. Note: ALP rises before calcium falls, "
        "so a normal calcium does not exclude it."
    ),

    "Rickets": (
        "The childhood counterpart of osteomalacia: defective "
        "mineralisation at the growth plate, so the deformity is of growing "
        "bone rather than only of bone strength. Causes: nutritional "
        "vitamin D deficiency is commonest, particularly in exclusively "
        "breastfed infants without supplementation, with dark skin or "
        "limited sun exposure. Also X-linked hypophosphataemic and vitamin "
        "D-dependent forms. Clinical features: frontal bossing, rachitic "
        "rosary, wrist and ankle widening, bowing of the legs once "
        "weight-bearing, and delayed milestones. Hypocalcaemic seizures in "
        "infancy. Ix: wrist radiograph showing metaphyseal cupping, "
        "splaying and fraying, with the same biochemistry as osteomalacia. "
        "Mx: colecalciferol with adequate dietary calcium, treating the "
        "mother too if the infant is breastfed. Phosphate and calcitriol "
        "for hypophosphataemic forms, or burosumab in selected cases. Note: "
        "deformity in a young child largely remodels once biochemistry is "
        "corrected."
    ),

    "Anal fissure": (
        "A longitudinal tear in the anoderm distal to the dentate line, "
        "over 90% in the posterior midline. Pathophysiology: hard stool "
        "tears the anoderm, pain causes internal sphincter spasm, spasm "
        "reduces perfusion, and the ischaemia prevents healing. Treatment "
        "is aimed at breaking that cycle rather than at the tear. Clinical "
        "features: severe tearing pain during defaecation persisting for up "
        "to hours afterwards, with bright blood on the paper. A sentinel "
        "skin tag marks chronicity. Ix: gentle inspection by parting the "
        "buttocks is usually enough. Digital examination is often "
        "intolerable acutely. A lateral or multiple fissure suggests Crohn "
        "disease, tuberculosis, malignancy or HIV and warrants examination "
        "under anaesthetic. Mx: fibre, fluid, stool softeners and warm "
        "baths heal most acute fissures. Topical glyceryl trinitrate or "
        "diltiazem relaxes the sphincter for chronic ones; headache limits "
        "GTN. Botulinum toxin, then lateral internal sphincterotomy. Note: "
        "sphincterotomy carries a real risk of incontinence, so counsel "
        "explicitly, particularly in women who have given birth."
    ),

    "Uveitis": (
        "Inflammation of the uveal tract, classified anatomically because "
        "the site predicts both the associations and the risk. Types: "
        "anterior (iritis) is commonest; intermediate, posterior and "
        "panuveitis carry more risk to vision. Causes: about half are "
        "idiopathic. Otherwise HLA-B27-associated disease, sarcoidosis, "
        "juvenile idiopathic arthritis, or infection with herpes viruses, "
        "toxoplasma or syphilis. Clinical features: anterior disease gives "
        "a painful red eye with photophobia, blurred vision and a small "
        "irregular pupil, with circumcorneal injection. Posterior disease "
        "is painless with floaters and visual loss. Ix: slit lamp "
        "examination showing cells and flare in the anterior chamber, with "
        "targeted serology guided by the pattern. Mx: ophthalmology review. "
        "Topical corticosteroid with a cycloplegic to relieve spasm and "
        "prevent synechiae; systemic immunosuppression for severe or "
        "posterior disease. Note: JIA-associated uveitis is typically "
        "asymptomatic and white, which is why those children are screened "
        "rather than waiting."
    ),

    "Huntington disease": (
        "Autosomal dominant neurodegeneration from a CAG trinucleotide "
        "expansion in HTT on chromosome 4, with striatal medium spiny "
        "neurons lost first. Genetics: 40 or more repeats is fully "
        "penetrant; 36 to 39 is reduced penetrance. Anticipation occurs, "
        "and is more marked with paternal transmission because expansion "
        "happens in spermatogenesis. Clinical features: the triad is "
        "movement disorder, cognitive decline and psychiatric illness, and "
        "the psychiatric features often come first. Chorea early, giving "
        "way to bradykinesia, dystonia and rigidity later. Depression and a "
        "substantially raised suicide risk throughout. Ix: genetic testing, "
        "which in an asymptomatic person must follow formal predictive "
        "testing protocols with counselling before and after. MRI shows "
        "caudate atrophy. Mx: no disease-modifying therapy. Treat chorea if "
        "it is disabling, treat depression and psychosis actively, and "
        "involve a multidisciplinary team early for speech, swallow, "
        "nutrition and advance care planning. Note: the psychiatric burden "
        "is what most affects quality of life, and it is treatable even "
        "though the disease is not."
    ),

    "Chronic fatigue syndrome": (
        "Also myalgic encephalomyelitis. A disabling multisystem illness "
        "defined by post-exertional malaise, not by fatigue alone. Dx: six "
        "months or more of substantial reduction in function, with "
        "post-exertional malaise, unrefreshing sleep, and either cognitive "
        "impairment or orthostatic intolerance. Post-exertional malaise is "
        "the required feature and distinguishes this from fatigue of other "
        "causes. Ix: there is no confirmatory test. Investigate to exclude "
        "mimics - FBC, EUC, LFT, TFT, coeliac serology, CRP, ferritin, "
        "glucose, and vitamin D - and stop there rather than searching "
        "indefinitely. Mx: symptom-focused and individualised. Activity "
        "pacing within an energy envelope; treat sleep, pain and "
        "orthostatic intolerance; manage comorbid mood disorder without "
        "implying it is the cause. Graded exercise therapy is no longer "
        "recommended as a curative treatment and can worsen post-exertional "
        "malaise. Note: patients are commonly disbelieved before they are "
        "diagnosed, and the therapeutic relationship depends on not "
        "repeating that."
    ),

    # ═══════ BATCH 5: ordered by measured deck frequency ════════════════
    #
    # Ranked by direct scan of every note in the live Anki collection
    # (~/Library/Application Support/Anki2/User 1/collection.anki2),
    # word-boundary counting each condition name and every alias across
    # all fields with HTML and cloze markers stripped. Restricted to
    # conditions with no rich override yet.
    #
    # Frequencies for this batch: MDD 207, schizophrenia 102, meningitis
    # 95, delirium 89, sepsis 87, HIV 77, syncope 62, AKI 57,
    # hypoglycaemia 54, gestational diabetes 52.

    "Major depressive disorder": (
        "Persistent low mood or anhedonia with functional impairment for "
        "at least two weeks. Dx: five or more of nine DSM-5 symptoms with "
        "mood or anhedonia among them, near-daily for two weeks and causing "
        "dysfunction; SIGECAPS covers the rest - sleep, interest, guilt, "
        "energy, concentration, appetite, psychomotor and suicidality. "
        "Screen with PHQ-9. Ix: no test confirms the diagnosis; investigate "
        "to exclude organic mimics with TFT, FBC and ferritin, B12 and "
        "folate, EUC, glucose, and a targeted drug and alcohol history. "
        "Mx: mild disease responds to CBT, behavioural activation or "
        "interpersonal therapy alone; moderate to severe adds an "
        "antidepressant, SSRI first line in Australia (sertraline, "
        "escitalopram), with SNRI or mirtazapine as second choice. Review "
        "at 2 weeks for tolerability and 4 to 6 for response, then switch "
        "class or augment if inadequate. ECT for melancholia, psychotic "
        "features, catatonia or urgent suicide risk. Note: assess suicide "
        "risk at every visit and document specifically, not just at the "
        "first; Australian guidance is the RANZCP mood disorders CPG."
    ),

    "Schizophrenia": (
        "Chronic psychotic disorder with continuous illness for at least "
        "six months and active-phase symptoms for at least one month. "
        "Dx: two or more of delusions, hallucinations, disorganised speech, "
        "grossly disorganised or catatonic behaviour, and negative "
        "symptoms - at least one from the first three. Onset typically late "
        "teens to mid twenties in males, later in females. Ix: no "
        "confirmatory test; exclude organic causes with FBC, EUC, LFT, TFT, "
        "calcium, B12, urine drug screen, HIV and syphilis serology, and "
        "MRI brain in atypical or late-onset presentation. Mx: "
        "second-generation antipsychotic first line - risperidone, "
        "olanzapine, aripiprazole, paliperidone; long-acting injectables "
        "improve adherence and are offered early rather than after multiple "
        "relapses. Clozapine for treatment resistance (inadequate response "
        "to two adequate trials), with mandatory neutrophil monitoring and "
        "clinical review for myocarditis. CBT for psychosis, family "
        "intervention and vocational support are core, not optional. Note: "
        "physical health mortality gap is about 15 years, largely "
        "cardiometabolic, so metabolic monitoring is part of the treatment "
        "plan from the first script."
    ),

    "Meningitis": (
        "Inflammation of the meninges, usually infective. Causes: bacterial "
        "in adults is most often Streptococcus pneumoniae and Neisseria "
        "meningitidis, with Listeria in the very young, over-50s, pregnant "
        "or immunocompromised; viral is commonly enterovirus; consider TB "
        "and cryptococcus in chronic or immunocompromised presentations. "
        "Clinical features: fever, neck stiffness and altered mental state "
        "is the classic triad but is present in only about 40%; headache "
        "and photophobia are more sensitive; a non-blanching petechial rash "
        "suggests meningococcaemia. Kernig and Brudzinski are specific but "
        "not sensitive. Ix: blood cultures then lumbar puncture without "
        "delay; CT before LP only if focal deficit, GCS below 12, seizure, "
        "immunocompromise, or papilloedema. Mx: give empiric ceftriaxone 2g "
        "IV plus dexamethasone 10mg IV before or with the first antibiotic "
        "dose; add benzylpenicillin or amoxicillin if Listeria risk; add "
        "vancomycin if resistant pneumococcus is plausible. Notify public "
        "health and offer household contact prophylaxis for meningococcus. "
        "Red flags: purpuric rash, shock or reduced GCS - treat before "
        "imaging."
    ),

    "Delirium": (
        "Acute fluctuating disturbance of attention and awareness with "
        "cognitive change, developing over hours to days and caused by "
        "another medical condition. Types: hyperactive (agitated, "
        "hallucinating), hypoactive (withdrawn, quiet - the more common "
        "and the more missed), or mixed. Causes: PINCH ME - Pain, "
        "Infection, Nutrition, Constipation and dehydration, Hypoxia, "
        "Medication (anticholinergics, opioids, benzodiazepines, steroids, "
        "polypharmacy), Environment change, and Electrolyte or metabolic "
        "derangement. Alcohol and benzodiazepine withdrawal are specific "
        "traps. Ix: bedside screen (4AT or CAM), then FBC, EUC, calcium, "
        "glucose, LFT, TFT, urinalysis, CXR, ECG, blood cultures if febrile; "
        "CT brain and LP only for focal signs, unexplained fever with "
        "headache, or no other cause found. Mx: treat the underlying cause. "
        "Reorientate, restore sleep-wake, correct sensory impairment, "
        "mobilise, and avoid restraint. Antipsychotics (haloperidol or "
        "olanzapine) only for severe distress or safety, at the lowest "
        "dose and shortest duration; benzodiazepines only in alcohol or "
        "benzodiazepine withdrawal. Note: independently associated with "
        "mortality, longer admission and new dementia, so prevention is "
        "treatment."
    ),

    "Sepsis": (
        "Life-threatening organ dysfunction from a dysregulated host "
        "response to infection. Septic shock is sepsis with lactate over "
        "2 mmol/L and vasopressor need to keep MAP at least 65 mmHg "
        "despite fluid resuscitation. Ix: lactate, blood cultures before "
        "antibiotics where possible, FBC, EUC, LFT, coagulation, VBG, "
        "urinalysis and cultures from any plausible source (urine, sputum, "
        "wound, line, CSF); imaging directed by source. Mx: Hour-1 sepsis "
        "bundle - measure lactate, take cultures, give broad-spectrum IV "
        "antibiotics, start 30 mL/kg crystalloid if hypotensive or lactate "
        "over 4, and start vasopressors (noradrenaline first line) if MAP "
        "stays under 65 after fluids. Source control - drain, remove or "
        "debride - within hours where relevant. Reassess fluid status "
        "dynamically after the initial bolus rather than repeating it "
        "blindly. DDx: pancreatitis, major trauma or burns can mimic SIRS "
        "without infection; anaphylaxis and adrenal crisis look septic "
        "briefly. Red flags: lactate over 4, GCS drop, oliguria, mottling "
        "or a rising vasopressor requirement mean escalate now, not after "
        "the next set of bloods."
    ),

    "HIV": (
        "Retroviral infection depleting CD4 T cells; untreated it "
        "progresses through acute seroconversion, chronic asymptomatic "
        "and AIDS (CD4 under 200 or an AIDS-defining illness). Clinical "
        "features: seroconversion 2 to 4 weeks after exposure looks like "
        "flu with fever, pharyngitis, lymphadenopathy, maculopapular rash "
        "and oral ulcers; the chronic phase is asymptomatic for years. "
        "Ix: fourth-generation combined HIV antigen and antibody assay is "
        "the screen; positives are confirmed with a differentiation assay "
        "and quantified with viral load. Baseline CD4, genotype, HBV and "
        "HCV serology, syphilis, STI screen and vaccine status. Mx: start "
        "antiretroviral therapy at diagnosis regardless of CD4 - integrase "
        "inhibitor plus two NRTIs (bictegravir with tenofovir alafenamide "
        "and emtricitabine is a standard fixed-dose combination). Target "
        "undetectable viral load, which also prevents sexual transmission "
        "(U=U). Offer PrEP to HIV-negative people at ongoing risk. "
        "Notifiable in every Australian jurisdiction. Note: opportunistic "
        "infection prophylaxis follows CD4 - cotrimoxazole under 200 for "
        "PCP, azithromycin under 50 for MAC."
    ),

    "Syncope": (
        "Transient loss of consciousness from global cerebral "
        "hypoperfusion, with spontaneous complete recovery. Types: reflex "
        "or vasovagal is commonest (prodrome of nausea, sweating and "
        "warmth, triggered by prolonged standing, pain or emotion); "
        "orthostatic (drop of at least 20/10 mmHg on standing, from volume "
        "depletion, autonomic failure or drugs); and cardiac (arrhythmia "
        "or structural such as aortic stenosis, HCM or pulmonary "
        "embolism). Cardiac syncope has no or brief prodrome, often on "
        "exertion or supine, and carries the mortality. Ix: 12-lead ECG "
        "on everyone; lying and standing blood pressure; echo if murmur, "
        "exertional syncope or abnormal ECG; ambulatory monitoring or an "
        "implantable loop recorder for recurrent unexplained events. "
        "Bloods only where the history suggests cause. Mx: reassure and "
        "educate for reflex syncope - trigger avoidance, counter-pressure "
        "manoeuvres, adequate salt and fluid; treat the cause for "
        "orthostatic and cardiac; admit any cardiac or high-risk "
        "presentation. Note: driving restrictions under Austroads apply "
        "and depend on the type - a single reflex event is not the same "
        "as cardiac or recurrent, and the patient carries the reporting "
        "obligation."
    ),

    "Acute kidney injury": (
        "Rapid decline in renal function defined by KDIGO as a serum "
        "creatinine rise of at least 26 micromol/L in 48 hours, a rise to "
        "at least 1.5 times baseline within 7 days, or urine output under "
        "0.5 mL/kg/h for 6 hours. Causes: pre-renal from volume depletion, "
        "sepsis, heart failure or hepatorenal syndrome; intrinsic from "
        "acute tubular necrosis (ischaemic or nephrotoxic), acute "
        "interstitial nephritis (drug rash and eosinophiluria), or "
        "glomerulonephritis (haematuria and proteinuria); post-renal from "
        "obstruction at any level. Ix: EUC, FBC, urinalysis and "
        "microscopy, FENa if oliguric (under 1% pre-renal, over 2% ATN), "
        "renal ultrasound to exclude obstruction and assess size; "
        "immunology (ANA, ANCA, complement) and myeloma screen where "
        "intrinsic disease is plausible. Mx: treat the cause - resuscitate "
        "with crystalloid, remove nephrotoxins (NSAIDs, ACE inhibitors, "
        "aminoglycosides, contrast where possible), relieve obstruction, "
        "treat sepsis. Dialysis for AEIOU - refractory Acidosis, "
        "Electrolytes (especially hyperkalaemia), Ingestion, refractory "
        "fluid Overload, Uraemic complications. Note: an AKI episode is a "
        "risk factor for future CKD, so follow up creatinine after "
        "discharge."
    ),

    "Hypoglycaemia": (
        "Blood glucose under 3.9 mmol/L with Whipple triad - low glucose, "
        "consistent symptoms, and resolution with correction. Causes: in "
        "diabetes, insulin or sulfonylurea excess relative to intake or "
        "activity, or renal failure prolonging drug half-life; without "
        "diabetes, alcohol, sepsis, adrenal or pituitary insufficiency, "
        "severe liver disease, or insulinoma. Clinical features: autonomic "
        "warning (sweating, tremor, palpitations, hunger) then "
        "neuroglycopenia (confusion, slurred speech, focal deficit, "
        "seizure, coma). Hypoglycaemia unawareness develops with recurrent "
        "lows and is a major driver of severe episodes. Mx: conscious and "
        "able to swallow - 15g fast-acting oral carbohydrate (jelly beans "
        "or juice), retest in 15 minutes, repeat if still low, then a "
        "longer-acting snack. Impaired consciousness or unable to "
        "swallow - IV 10% dextrose 100 mL, or IM glucagon 1 mg if no IV "
        "access; recheck at 10 minutes. Investigate a first episode "
        "without diabetes with a 72-hour fast measuring paired glucose, "
        "insulin, C-peptide and beta-hydroxybutyrate. Note: sulfonylurea "
        "hypoglycaemia recurs for many hours, so these patients need "
        "admission and an octreotide infusion, not a single dextrose "
        "bolus and discharge."
    ),

    "Gestational diabetes": (
        "Glucose intolerance first recognised in pregnancy, distinct from "
        "pre-existing diabetes and resolving after delivery in most. "
        "Pathophysiology: placental hormones (human placental lactogen, "
        "progesterone, cortisol, growth hormone) drive insulin resistance "
        "from mid-pregnancy; GDM is the failure of beta cells to keep up. "
        "Risk factors: BMI over 30, previous GDM, previous macrosomia over "
        "4.5 kg, South Asian, Middle Eastern or Aboriginal ethnicity, "
        "first-degree relative with type 2 diabetes, PCOS, and maternal "
        "age over 40. Ix: universal 75g OGTT at 24 to 28 weeks; diagnostic "
        "under ADIPS if fasting is at least 5.1, 1-hour at least 10.0, or "
        "2-hour at least 8.5 mmol/L. Earlier testing in high risk. Mx: "
        "dietitian-led carbohydrate management and monitored exercise "
        "first; self-monitor fasting and 1-hour post-meal glucose "
        "targeting under 5.0 fasting and under 7.4 post-prandial. Add "
        "insulin (or metformin where insulin is not acceptable) if "
        "targets are not met within one to two weeks. Serial growth "
        "ultrasound. Note: repeat OGTT at 6 to 12 weeks postpartum; 50% "
        "develop type 2 diabetes within 10 years, so annual glucose "
        "review continues indefinitely."
    ),

    # ═══════ BATCH 6: ordered by measured deck frequency ════════════════
    #
    # Continues the Batch 5 method - direct scan of every note in the
    # live Anki collection with word-boundary counting across all fields.
    # Frequencies: rubella 51, GORD 51, PPH 51, measles 50, CKD 49,
    # varicella 48, tuberculosis 47, heart block 47, menopause 46,
    # obstructive sleep apnoea 45.

    "Rubella": (
        "Togavirus infection, usually a mild childhood exanthem; matters "
        "because of congenital rubella syndrome. Clinical features: "
        "prodrome of low-grade fever with tender posterior cervical and "
        "suboccipital lymphadenopathy, then a fine pink maculopapular "
        "rash starting on the face and spreading down over 24 hours, "
        "fading in the same order. Arthralgia is common in adults, "
        "particularly women. Up to half of infections are subclinical. "
        "Ix: rubella IgM and rising IgG, or PCR of throat or urine "
        "within the first week of rash; confirm on serology in pregnancy "
        "rather than clinically. Mx: supportive; isolate for 7 days "
        "after rash onset and keep away from pregnant women. Notifiable "
        "urgently. Complications: congenital rubella syndrome after "
        "first-trimester maternal infection - sensorineural deafness, "
        "cataracts, patent ductus arteriosus, microcephaly and "
        "intellectual disability. Note: MMR at 12 and 18 months on the "
        "Australian NIP is why local infections are now almost all "
        "imported; check rubella immunity pre-pregnancy and vaccinate "
        "postpartum if non-immune (MMR is contraindicated in pregnancy)."
    ),

    "Gastro-oesophageal reflux disease": (
        "Symptoms or mucosal injury from retrograde flow of gastric "
        "contents into the oesophagus. Pathophysiology: transient lower "
        "oesophageal sphincter relaxations are the commonest mechanism; "
        "reduced tone from a hiatus hernia and raised intragastric "
        "pressure from obesity or pregnancy contribute. Clinical "
        "features: heartburn and regurgitation are the classic pair; "
        "water brash, chronic cough, hoarseness, non-cardiac chest pain "
        "and dental erosions are extraoesophageal presentations. Ix: "
        "empirical PPI trial is diagnostic in typical disease; endoscopy "
        "for alarm features - dysphagia, odynophagia, weight loss, "
        "anaemia, haematemesis or melaena, onset after 55, or failure "
        "of 4 to 8 weeks of PPI. Mx: lifestyle first - weight loss, "
        "smaller evening meals, no recumbency for 3 hours after eating, "
        "elevate the head of the bed, reduce alcohol. Pantoprazole or "
        "esomeprazole once daily before breakfast for 4 to 8 weeks, "
        "then step down. H2 antagonist at night for nocturnal "
        "breakthrough. Fundoplication for objectively confirmed disease "
        "refractory to full-dose PPI. Complications: erosive "
        "oesophagitis, stricture, Barrett oesophagus and adenocarcinoma."
    ),

    "Postpartum haemorrhage": (
        "Blood loss of at least 500 mL from the genital tract within 24 "
        "hours of birth (primary), or between 24 hours and 12 weeks "
        "postpartum (secondary). Major primary PPH is 1000 mL or more, "
        "or any loss with haemodynamic compromise. Causes: 4 Ts - Tone "
        "(uterine atony, 70 to 80%), Trauma (perineal, vaginal or "
        "cervical laceration, rupture), Tissue (retained placenta or "
        "membranes), Thrombin (coagulopathy). Secondary PPH is usually "
        "endometritis or retained products. Ix: FBC, coagulation, "
        "fibrinogen, group and crossmatch, VBG with lactate; ultrasound "
        "for retained products. Mx: bimanual uterine massage; two "
        "large-bore IV lines, warmed crystalloid then blood products via "
        "massive-transfusion protocol; empty the bladder; then "
        "uterotonics in sequence - IV oxytocin (bolus then infusion), "
        "IM ergometrine (avoid in hypertension), IM carboprost (avoid "
        "in asthma), misoprostol per rectum. Tranexamic acid 1 g IV "
        "within 3 hours "
        "reduces mortality. Escalate to intrauterine balloon tamponade, "
        "uterine artery embolisation, compression sutures or "
        "hysterectomy if bleeding continues. Note: active third-stage "
        "management with prophylactic oxytocin 10 units IM is the "
        "single most effective prevention."
    ),

    "Measles": (
        "Paramyxovirus infection, one of the most contagious diseases "
        "known (R0 around 15). Clinical features: 7 to 14 day "
        "incubation, then a 2 to 4 day prodrome of high fever with the "
        "3 Cs - cough, coryza and conjunctivitis - and Koplik spots on "
        "the buccal mucosa (pathognomonic). A maculopapular rash then "
        "appears behind the ears and spreads down, becoming confluent. "
        "Infectious from 4 days before to 4 days after rash onset. Ix: "
        "measles IgM and IgG, and RNA by PCR on nasopharyngeal swab or "
        "urine within the first week; notify public health on suspicion, "
        "before results. Mx: supportive; airborne isolation until 4 "
        "days after rash onset. Offer MMR to susceptible contacts within "
        "72 hours, or immunoglobulin within 6 days to pregnant women, "
        "infants under 6 months and immunocompromised contacts. "
        "Complications: otitis media (commonest), pneumonia (the usual "
        "cause of death), encephalitis, and subacute sclerosing "
        "panencephalitis years later. Note: MMR at 12 and 18 months on "
        "the Australian NIP; a single suspected case triggers contact "
        "tracing across every shared setting."
    ),

    "Chronic kidney disease": (
        "Sustained eGFR under 60 mL/min/1.73 m2 or albuminuria for at "
        "least 3 months. Causes: diabetes and hypertension account for "
        "most Australian cases; glomerulonephritis, polycystic kidney "
        "disease and reflux nephropathy are the main non-vascular "
        "causes. Classification: G1 to G5 by eGFR combined with A1 to "
        "A3 by urine albumin-to-creatinine ratio (KDIGO heatmap) drives "
        "risk. Ix: eGFR, urine ACR on a first-morning sample, "
        "urinalysis, renal ultrasound; screen for reversible "
        "contributors (obstruction, NSAIDs, dehydration); pursue "
        "intrinsic cause when there is haematuria, heavy proteinuria, "
        "systemic features or rapid decline. Mx: slow progression - BP "
        "under 130/80 with an ACE inhibitor or ARB, glycaemic control "
        "targeting HbA1c around 53 mmol/mol, an SGLT2 inhibitor "
        "(dapagliflozin or empagliflozin) if eGFR at least 20 with "
        "albuminuria, smoking cessation, lipid control. Treat CKD-MBD, "
        "anaemia and acidosis as they emerge. Refer to nephrology at "
        "eGFR under 30 or with heavy proteinuria; plan vascular access "
        "around eGFR 20. Note: RACGP kidney health check annually in "
        "anyone with diabetes, hypertension, CVD, or Aboriginal or "
        "Torres Strait Islander background."
    ),

    "Varicella": (
        "Primary infection with varicella-zoster virus. Clinical "
        "features: 10 to 21 day incubation, then a brief prodrome of "
        "fever and malaise before successive crops of pruritic vesicles "
        "at different stages (macule, papule, vesicle, crust), starting "
        "centrally and spreading to include the scalp and mucous "
        "membranes. Infectious from 1 to 2 days before rash until every "
        "lesion has crusted. Ix: clinical in typical disease; VZV PCR "
        "from a vesicle swab if atypical or high-risk. Mx: supportive "
        "with paracetamol and antihistamine or calamine; avoid NSAIDs "
        "(necrotising fasciitis) and aspirin in children (Reye "
        "syndrome). Oral aciclovir within 24 hours of rash onset in "
        "adolescents, adults, pregnant women and household contacts; IV "
        "aciclovir in the immunocompromised and in severe disease. "
        "Offer VZIG to non-immune pregnant contacts, neonates and the "
        "immunocompromised within 96 hours of exposure. Complications: "
        "bacterial superinfection, varicella pneumonia (adults and "
        "pregnant women), encephalitis, cerebellar ataxia, and "
        "congenital varicella syndrome from first- or second-trimester "
        "maternal infection. Note: MMRV at 18 months on the Australian "
        "NIP; school exclusion until all lesions have crusted."
    ),

    "Tuberculosis": (
        "Mycobacterium tuberculosis infection by respiratory droplet "
        "nuclei, as latent infection (positive IGRA or TST, no symptoms, "
        "not infectious) or active disease. Clinical features: "
        "pulmonary TB with cough over 3 weeks, haemoptysis, night "
        "sweats, weight loss and low-grade fever; extrapulmonary sites "
        "include lymph node, pleural, spinal (Pott disease), meningeal, "
        "miliary and genitourinary. Ix: three sputum samples for AFB "
        "smear, mycobacterial culture and Xpert MTB/RIF; chest imaging "
        "(apical cavitating infiltrate in reactivation, hilar "
        "lymphadenopathy in primary); HIV test on every new diagnosis. "
        "IGRA is preferred over TST in the BCG-vaccinated. Mx: active "
        "pulmonary TB gets RIPE (rifampicin, isoniazid, pyrazinamide, "
        "ethambutol) for 2 months, then rifampicin and isoniazid for 4 "
        "months, under a specialist TB service with directly observed "
        "therapy in Australia. Add pyridoxine; check baseline LFTs and "
        "visual acuity. For latent TB, isoniazid for 6 to 9 months, or "
        "rifampicin for 4 months, if at risk of reactivation. "
        "Notifiable. Note: multidrug resistance changes both regimen "
        "and duration - never start empirical retreatment without "
        "susceptibility results."
    ),

    "Heart block": (
        "Impaired conduction through the AV node or His-Purkinje "
        "system. Classification: first-degree is PR over 200 ms with "
        "every P conducted, benign in isolation; Mobitz I (Wenckebach) "
        "shows progressive PR ending in a dropped beat, usually AV "
        "nodal and benign; Mobitz II shows fixed PR with sudden "
        "non-conducted P waves, is infranodal and unstable, and "
        "warrants pacing; third-degree has AV dissociation with an "
        "escape rhythm whose rate and QRS width predict stability. "
        "Causes: idiopathic fibrosis, inferior MI (nodal, often "
        "transient), anterior MI (infranodal, ominous), calcific "
        "aortic valve disease, cardiac surgery, endocarditis with root "
        "abscess, Lyme, sarcoidosis, hyperkalaemia, and drugs (beta "
        "blockers, verapamil, diltiazem, digoxin, amiodarone). Ix: "
        "12-lead ECG; ambulatory monitoring for intermittent symptoms; "
        "EUC, TFT, troponin; echo. Mx: stop offending drug and correct "
        "electrolytes. Symptomatic bradycardia gets atropine, then "
        "isoprenaline or transcutaneous pacing while a transvenous "
        "wire is arranged. Permanent pacemaker for symptomatic AV "
        "block, all Mobitz II, and all third-degree outside reversible "
        "causes. Note: Austroads driving restrictions apply until "
        "pacing is established."
    ),

    "Menopause": (
        "Permanent cessation of menstruation, diagnosed retrospectively "
        "after 12 months of amenorrhoea; average age at final "
        "menstrual period is 51 in Australia. Premature ovarian "
        "insufficiency is menopause before 40. Clinical features: "
        "vasomotor symptoms in about three quarters, sleep disturbance, "
        "mood change, genitourinary syndrome (vaginal dryness, "
        "dyspareunia, urinary urgency), and accelerated bone loss. Ix: "
        "clinical over 45; FSH is unreliable in perimenopause because "
        "of cycle variability. Under 45, measure FSH twice at least a "
        "month apart to confirm POI, and exclude pregnancy and thyroid "
        "disease. Mx: lifestyle first - exercise, cooling strategies, "
        "weight management, reduced alcohol. Menopausal hormone "
        "therapy is the most effective treatment for vasomotor symptoms "
        "in women under 60 or within 10 years of the final menstrual "
        "period, absent contraindications - oestrogen alone if "
        "hysterectomised, oestrogen plus progestogen otherwise "
        "(RANZCOG). Non-hormonal options include SSRI or SNRI, "
        "gabapentin, and CBT. Vaginal oestrogen alone treats "
        "genitourinary syndrome with negligible systemic exposure. "
        "Note: POI needs oestrogen replacement at least until the "
        "average age of menopause."
    ),

    "Obstructive sleep apnoea": (
        "Repeated upper airway collapse during sleep causing apnoeas, "
        "desaturation and arousals. Risk factors: obesity (BMI over "
        "30), male sex, middle age, large neck circumference (over 40 "
        "cm), retrognathia and craniofacial abnormalities, tonsillar "
        "hypertrophy, evening alcohol. Clinical features: loud snoring "
        "with witnessed apnoeas, excessive daytime sleepiness (Epworth "
        "over 10), morning headache, nocturia, unrefreshing sleep, "
        "cognitive complaints. Ix: STOP-BANG or OSA-50 for screening; "
        "laboratory polysomnography is the reference standard and "
        "grades severity by apnoea-hypopnoea index (mild 5 to 14, "
        "moderate 15 to 29, severe 30 or more). Home sleep studies are "
        "acceptable in high pre-test probability with limited "
        "comorbidity. Mx: weight loss where relevant, avoid supine "
        "sleep and evening alcohol and sedatives. CPAP is first line "
        "for moderate to severe disease and for symptomatic mild "
        "disease; mandibular advancement splints for mild to moderate "
        "or CPAP intolerance. Associations: resistant hypertension, "
        "atrial fibrillation, stroke, type 2 diabetes and depression. "
        "Note: Austroads rules - excessive sleepiness with a positive "
        "study means no commercial driving until treated and "
        "controlled."
    ),
}


# ═══════════════════════════════════════════════════════════════════════
# Australian and British spelling variants for drug generics.
# ═══════════════════════════════════════════════════════════════════════
#
# Keyed by the INN generic already in the library; each value is a list
# of other spellings the same drug is written under. `tools/build_library.py`
# merges these into each drug entry as an `aliases` list, and
# `pearls/_drugs.py` indexes them case-insensitively alongside the
# generic. The popup still shows the INN spelling - an alias changes
# what the matcher recognises, never what is displayed.
#
# This exists because a missing alias is not a degraded popup, it is NO
# popup. Measured against 79 probes of names an Australian student's
# cards actually use, 23 resolved to nothing: `frusemide` is what NSW
# Health and the PBS call furosemide, `cephalexin` and `cephazolin` are
# the universal Australian spellings, `thyroxine` is what every endocrine
# card says, and `glyceryl trinitrate` is the Australian name for a drug
# the library only knew as nitroglycerin. Those cards highlighted nothing
# at all.
#
# This block used to say that `norepinephrine` and `beclometasone` were
# non-Australian forms deliberately not added, and that `epinephrine` was
# left unmatched for the same reason. Both halves were wrong, and both
# are corrected at 2.2:
#
# `beclometasone` is the Australian Approved Name. It is on the TGA's
# affected-ingredients list as a minor spelling change from
# `beclomethasone`, so the form this file called non-Australian is the
# only one a current Australian label may carry. The library's canonical
# spelling is renamed below rather than aliased.
#
# `epinephrine` and `norepinephrine` are printed on Australian labels by
# regulation. Adrenaline and noradrenaline are the two ingredients the
# TGA requires to be dual labelled permanently, as `adrenaline
# (epinephrine)` and `noradrenaline (norepinephrine)` - Australian name
# first, INN in brackets. So every ampoule in every Australian resus
# trolley carries the word `epinephrine`, and a card written from the
# ampoule, or from any international source, matched nothing.
#
# The house rule is not broken by adding them, because an alias never
# reaches the heading: `resolve()` reports `d["generic"]`, which stays
# `adrenaline`. The rule is about what is displayed, and
# `test_no_american_generic_is_displayed` is what enforces it.

DRUG_ALIASES = {
    # Australian spellings in routine use
    "furosemide":        ["frusemide"],
    "cefalexin":         ["cephalexin"],
    "cefazolin":         ["cephazolin", "cefazolin sodium"],
    "levothyroxine":     ["thyroxine"],
    "amoxicillin":       ["amoxycillin"],
    "indometacin":       ["indomethacin"],
    "colecalciferol":    ["cholecalciferol"],
    "ciclosporin":       ["cyclosporin", "cyclosporine"],
    "sulfasalazine":     ["sulphasalazine"],
    "co-trimoxazole":    ["cotrimoxazole", "trimethoprim-sulfamethoxazole"],
    "salbutamol":        ["albuterol"],

    # Names the library holds only in one form
    "sodium valproate":  ["valproate", "valproic acid"],
    "glyceryl trinitrate": ["GTN"],

    # Very common Australian brand written lower-case in practice, so the
    # case-sensitive brand path misses it
    "enoxaparin":        ["clexane"],

    # Printed on the Australian label by regulation - see the note above.
    # The heading stays `adrenaline` and `noradrenaline`.
    "adrenaline":        ["epinephrine"],
    "noradrenaline":     ["norepinephrine"],

    # The generic here is a bracketed dual label, and a phrase ending in
    # `)` only matches at the end of the text - so without this the bare
    # INN, which is what a prescription and a DrugBank page both say,
    # resolved to nothing. The heading is unaffected.
    "mercaptamine (cysteamine)": ["mercaptamine"],

    # ── Superseded Australian Approved Names, from the TGA's own list ──
    #
    # The 2.1.1 aliases were assembled by hand from names Rob's cards
    # happened to use, which found eleven and missed eleven. This block
    # is the remainder of the TGA "Updating medicine ingredient names"
    # active-ingredient table, restricted to rows where the new name is
    # already a generic in this library, so each is a pure alias with no
    # summary to write:
    #   tga.gov.au/updating-medicine-ingredient-names-list-affected-ingredients
    #
    # Textbooks, older lecture slides and hospital protocols still carry
    # the left-hand form, so a card written from any of them matched
    # nothing.
    "trihexyphenidyl":   ["benzhexol"],
    "flupentixol":       ["flupenthixol"],
    "dexamfetamine":     ["dexamphetamine"],
    "hydroxycarbamide":  ["hydroxyurea"],
    "formoterol":        ["eformoterol"],
    "glycopyrronium":    ["glycopyrrolate"],
    "chlorphenamine":    ["chlorpheniramine"],
    "colestyramine":     ["cholestyramine"],
    "clomifene":         ["clomiphene"],
    "ethinylestradiol":  ["ethinyloestradiol"],
    "dactinomycin":      ["actinomycin D"],
}

# ═══════════════════════════════════════════════════════════════════════
# American generics displayed as popup headings.
# ═══════════════════════════════════════════════════════════════════════
#
# The house rule is Australian-first, and these broke it at the most
# visible point there is: the heading of the popup. Measured across the
# 1,165 drug generics, five were the US form.
#
# Four of them duplicated an entry that already existed under the
# Australian name, so the library was carrying the same drug twice with
# two summaries and whichever matched first won. For those, the US entry
# is dropped and its name kept as an alias, so a card written the
# American way still resolves - it just displays the Australian name.
#
# `nitroglycerin` had no Australian counterpart at all, so it is renamed
# rather than merged.
#
# Format: US form -> the Australian entry to fold it into, or None to
# rename in place using DRUG_ALIASES for the old spelling.

# `estradiol` and `lidocaine` were here until 2.2, folded into
# `oestradiol` and `lignocaine`. That was backwards, and the two rows
# have moved to DRUG_RENAMES pointing the other way. See the note there.
# `pethidine` and `rifampicin` are unaffected: neither is on the TGA
# list, so those two merges stand on their own.

DRUG_US_MERGES = {
    "meperidine": "pethidine",
    "rifampin":   "rifampicin",
}

# ═══════════════════════════════════════════════════════════════════════
# Generics renamed to the name that should head the popup.
# ═══════════════════════════════════════════════════════════════════════
#
# The old spelling is kept as an alias by the rename machinery, so a card
# written either way still resolves. This only decides what the heading
# says.

DRUG_RENAMES = {
    "nitroglycerin": "glyceryl trinitrate",

    # `benztropine mesylate` -> `benzatropine mesilate` on the TGA list,
    # so benzatropine is the Australian Approved Name and benztropine is
    # the superseded US form. The library carried only the US form, so
    # unlike the four merges above there is no duplicate to fold in and
    # nothing is lost by renaming. The old spelling is kept as an alias
    # by the rename machinery.
    #
    # This one is worth more than its size: benzatropine is the drug on
    # every acute-dystonia and drug-induced-parkinsonism card, so the
    # heading was showing the American name on exactly the material a
    # psychiatry rotation runs on.
    "benztropine": "benzatropine",

    # ── The 5a reversal ────────────────────────────────────────────────
    #
    # 2.1.1 merged these the other way, on the reading that `lignocaine`
    # and `oestradiol` are the Australian names. Under the TGA's own list
    # they are the superseded ones:
    #
    #   Lignocaine -> lidocaine was dual labelled as `lidocaine
    #   (lignocaine)`. The sole-name transition closed 30 April 2026, so
    #   a medicine released for supply in Australia from 1 May 2026 must
    #   show `lidocaine` alone. That date is past.
    #
    #   Oestradiol -> estradiol is filed as a minor spelling change. It
    #   never had a dual labelling period at all, because the two forms
    #   are transparently the same word.
    #
    # Australian speech, hospital protocols and exam papers still say
    # lignocaine and oestradiol, which is the whole argument for the old
    # direction - but that argument is about what a card SAYS, and a card
    # saying either word resolves either way. The heading is the one
    # place a name has to be the current one, because it is the name the
    # box in front of him will carry.
    #
    # What settled it was opening the entries rather than arguing the
    # principle. The 2.1.1 merge kept the wrong side of the pair: the
    # surviving `oestradiol` summary is 158 characters reading
    # "Australian/British spelling of estradiol ... See estradiol entry",
    # and the estradiol entry it points at is the one the merge deleted.
    # That popup has been a dead cross-reference in every release since.
    # The full text is rewritten in DRUG_SUMMARIES below.
    "lignocaine": "lidocaine",
    "oestradiol": "estradiol",

    # ── 5b: superseded canons ──────────────────────────────────────────
    #
    # Straight renames of the `benzatropine` kind. Both are on the TGA
    # list and neither has a duplicate entry to fold in.
    #
    #   `phenobarbitone` was dual labelled as `phenobarbital
    #   (phenobarbitone)` and is under the same 30 April 2026 sole-name
    #   deadline as lidocaine.
    #
    #   `beclomethasone` -> `beclometasone` is a minor spelling change,
    #   like oestradiol. See the corrected note above DRUG_ALIASES.
    "phenobarbitone": "phenobarbital",
    "beclomethasone": "beclometasone",

    # The third name in 5b is not a straight rename, and reading the TGA
    # list rather than assuming is what caught it.
    #
    # `mercaptamine` is on the short list of names that stay dual
    # labelled in the Australian Approved Names List **with no planned
    # transition to a sole name** - alongside alimemazine (trimeprazine)
    # and Mycobacterium bovis (BCG strain). The reason is a TGA safety
    # advisory in its own right: `mercaptamine` and `mercaptopurine` are
    # a look-alike/sound-alike pair, one for nephropathic cystinosis and
    # one for leukaemia and IBD, and the bracketed old name is what keeps
    # them apart at the point of prescribing.
    #
    # So the Australian Approved Name here is the whole string, brackets
    # included, and renaming to a bare `mercaptamine` would replace one
    # wrong heading with a different wrong heading - and would do it on
    # the exact name a regulator has flagged as dangerous on its own.
    #
    # Note what this does NOT extend to. Adrenaline and noradrenaline are
    # also permanently dual labelled, but their AAN brackets the *INN*
    # after the Australian name rather than the reverse, so the heading
    # is already correct and the bracketed word belongs in DRUG_ALIASES.
    # The rule is: the heading leads with the current AAN, and carries a
    # bracket only where the AAN itself does and the leading name would
    # otherwise be one the reader cannot place.
    "cysteamine": "mercaptamine (cysteamine)",
}


# Drugs absent from the library entirely, found by the same sweep. These
# need adding as entries, not as aliases, and the build refuses an alias
# keyed on a generic it cannot find - which is how `mercaptopurine` was
# caught here rather than shipping as an alias that silently never fired.
#
#   mercaptopurine (and 6-mercaptopurine) - IBD and ALL maintenance
#   dalteparin, tinzaparin                - LMWHs on the PBS
#
# Not added in this pass: adding a drug means writing its summary, and
# these belong in a batch with the rest rather than bolted onto an alias
# fix.


# Fill the new entries' summaries from the table above, so the text is
# written once and a mismatch between the two is impossible.
for _nc in NEW_CONDITIONS:
    _nc["summary"] = RICH_SUMMARIES.get(_nc["name"], "")


# ═══════════════════════════════════════════════════════════════════════
# Structured rewrites for drug entries.
# ═══════════════════════════════════════════════════════════════════════
#
# The same seam as RICH_SUMMARIES, for drugs. Before 2.2 there was none:
# condition text has had an authoring copy here since the 2.0 split,
# drug text lived only in `data/library.json`, which is a build artefact
# nobody hand-edits. So "rewrite this drug summary" had no procedure,
# which is the real reason the drug backlog never moved while the
# condition backlog did four batches.
#
# Keyed on the canonical generic AFTER any rename above, because that is
# what heads the popup. `tools/build_library.py` fails the build on a key
# it cannot find, which is the guard against writing an override for a
# name that was renamed out from under it.
#
# Selection rule, from the 2.1.3 finding: the drugs Rob actually studies
# are too THIN, not too tall. The specialist tail is where the over-cap
# entries are and it returns zero notes. So these are chosen by clinical
# weight on a Medicine and Psychiatry rotation, and written into the
# available height rather than trimmed to fit.

DRUG_SUMMARIES = {

    # ═══════ Forced by the 5a/5b renames ════════════════════════════════

    # Replaces 158 characters that said "see estradiol entry" about an
    # entry the same merge had just deleted.
    "estradiol": (
        "Oestrogen (17-beta-estradiol), identical to the principal "
        "premenopausal ovarian oestrogen. "
        "MOA: agonist at nuclear oestrogen receptors alpha and beta; "
        "restores hypothalamic-pituitary feedback and reverses "
        "target-tissue atrophy. "
        "Indications: menopausal hormone therapy for vasomotor and "
        "genitourinary symptoms; premature ovarian insufficiency and "
        "hypogonadism, where it is replacement rather than treatment and "
        "continues to the average age of menopause; feminising "
        "gender-affirming hormone therapy. "
        "Route: transdermal patch or gel is preferred - it bypasses "
        "first-pass metabolism, so it does not raise VTE risk the way "
        "oral oestrogen does, and it is the clear choice with obesity, "
        "migraine or thrombotic risk. "
        "CI: oestrogen-dependent malignancy, undiagnosed vaginal "
        "bleeding, active VTE or arterial thrombosis, active liver "
        "disease. "
        "SE: breast tenderness, nausea, headache, breakthrough bleeding. "
        "Note: an intact uterus mandates a progestogen, because "
        "unopposed oestrogen causes endometrial hyperplasia and "
        "carcinoma - micronised progesterone nightly, or cyclically for "
        "12 to 14 days a month if a withdrawal bleed is acceptable. "
        "Australian notes: `estradiol` is the current Australian "
        "Approved Name, filed by the TGA as a minor spelling change; "
        "wards and exam papers still write oestradiol, and both resolve."
    ),

    # The old text asserted "AU/UK: phenobarbitone; US: phenobarbitone",
    # which is wrong on both halves of its own comparison.
    "phenobarbital": (
        "Barbiturate antiepileptic, the oldest anticonvulsant still in "
        "routine use. "
        "MOA: binds GABA-A and prolongs the DURATION of chloride channel "
        "opening - benzodiazepines increase the frequency, which is why "
        "barbiturates keep working without GABA present and depress "
        "respiration where benzodiazepines plateau. "
        "Indications: neonatal seizures, still first line worldwide on "
        "parenteral availability, cost and a long safety record; "
        "refractory status epilepticus after a benzodiazepine and a "
        "second-line agent. "
        "Half-life 80 to 100 hours, so once daily and a fortnight to "
        "steady state. "
        "SE: sedation and cognitive blunting, paradoxical hyperactivity "
        "in children, tolerance and dependence, respiratory depression "
        "on rapid IV loading, osteomalacia with chronic use. "
        "Interactions: potent inducer of CYP3A4, 2C9 and "
        "glucuronidation - lowers combined oral contraceptives to the "
        "point of contraceptive failure, and lowers warfarin, the DOACs "
        "and most co-prescribed antiepileptics. "
        "CI: acute porphyria, severe respiratory insufficiency. "
        "Note: never stop abruptly - withdrawal precipitates seizures "
        "and a delirium closer to alcohol withdrawal. `phenobarbital` is "
        "the Australian Approved Name; the sole-name transition from "
        "phenobarbital (phenobarbitone) closed on 30 April 2026."
    ),

    "beclometasone": (
        "Inhaled corticosteroid (ICS) - a preventer, not a reliever. "
        "MOA: beclometasone dipropionate is a prodrug, hydrolysed in "
        "airway tissue to active 17-BMP; glucocorticoid receptor "
        "binding suppresses NF-kB driven transcription, reducing airway "
        "eosinophilic inflammation and bronchial hyperresponsiveness "
        "over days to weeks. It does nothing acutely. "
        "Indications: asthma preventer therapy in adults and children. "
        "Dose: the extrafine HFA formulation (about 1.1 micrometre "
        "particles) deposits far better in small airways and is roughly "
        "twice as potent as the older CFC product, so its dose bands are "
        "about half those of budesonide - read the Australian Asthma "
        "Handbook table rather than converting between ICS by eye, "
        "because that error runs in both directions. "
        "SE: oral candidiasis and dysphonia, both largely preventable by "
        "rinsing and spitting after use and by a spacer; at high dose "
        "and long duration, adrenal suppression, reduced bone mineral "
        "density, cataract, glaucoma, and a small reduction in growth "
        "velocity in children that is mostly recovered. "
        "Note: Australian practice for mild asthma has moved away from "
        "short-acting beta agonist alone toward as-needed "
        "ICS-formoterol, and beclometasone monotherapy is not a "
        "maintenance-and-reliever product - if a patient is using it "
        "that way, the regimen is wrong rather than the dose."
    ),

    # Trimmed from 1,910 characters. The mechanism was three clauses deep
    # into lysosomal transport for a drug a Year 4 student will meet
    # once; the look-alike name it is now called by was not mentioned at
    # all.
    "mercaptamine (cysteamine)": (
        "Aminothiol cystine-depleting agent for nephropathic cystinosis. "
        "MOA: the free thiol reacts with intralysosomal cystine to form "
        "a mixed disulfide that leaves through an intact transporter, "
        "bypassing the defective CTNS carrier and lowering lysosomal "
        "cystine load. "
        "Indications: nephropathic cystinosis - started as early as "
        "possible and continued for life, delaying progression from "
        "Fanconi syndrome to end-stage kidney disease; ophthalmic drops "
        "separately for corneal crystals, because systemic drug does not "
        "reach the avascular cornea. "
        "Monitoring: leukocyte cystine about 6 hours post-dose, titrated "
        "to target. "
        "SE: a penetrating sulfurous breath and body odour from excreted "
        "metabolites, which is the dominant adherence problem and not a "
        "trivial one socially; nausea and vomiting; skin striae. "
        "Red flags: `mercaptamine` and `mercaptopurine` are a "
        "look-alike, sound-alike pair with a standing TGA safety "
        "advisory - one treats cystinosis, the other leukaemia and IBD, "
        "and a reported swap left an infant pancytopenic. "
        "Australian notes: the Approved Name is the whole dual-labelled "
        "string, and it is one of a handful the TGA has no plan to "
        "shorten, precisely because the bracket keeps the pair apart."
    ),

    # ═══════ Medicine and Psychiatry rotation, chosen by clinical weight ═

    "clozapine": (
        "Atypical antipsychotic (dibenzodiazepine) and the only agent "
        "with proven superiority in treatment-resistant schizophrenia. "
        "MOA: low-affinity, rapidly dissociating D2 antagonism plus "
        "5-HT2A, D4, H1, M1 and alpha-1 blockade - the loose D2 binding "
        "is why it causes almost no EPS and no hyperprolactinaemia. "
        "Indications: treatment-resistant schizophrenia after two "
        "adequate antipsychotic trials; persistent suicidality in "
        "schizophrenia or schizoaffective disorder; psychosis in "
        "Parkinson disease. "
        "Monitoring: FBC at baseline, WEEKLY for 18 weeks, then every 28 "
        "days for as long as the drug continues, through a mandatory "
        "monitoring service. Amber is neutrophils 1.5 to 2.0 or WCC 3.0 "
        "to 3.5 and means twice-weekly counts; red is neutrophils below "
        "1.5 or WCC below 3.0 and means cease immediately with no "
        "rechallenge. Troponin and CRP at baseline and weekly for the "
        "first four weeks. "
        "SE: agranulocytosis, highest between weeks 6 and 18; "
        "myocarditis, peaking in weeks 2 to 3; dose-related seizures "
        "above about 600 mg daily; the worst metabolic burden of any "
        "antipsychotic; constipation progressing to ileus, which kills "
        "more patients than agranulocytosis does and warrants "
        "prophylactic aperients; hypersalivation, sedation, postural "
        "hypotension and tachycardia on titration. "
        "Note: a CYP1A2 substrate, so stopping smoking removes an "
        "inducer and levels can nearly double within days - a patient "
        "admitted to a smoke-free ward is the classic presentation. A "
        "break of over 48 hours requires full retitration."
    ),

    "lithium": (
        "Mood stabiliser, and the only psychotropic with a replicated "
        "anti-suicide effect independent of its mood effect. "
        "MOA: inhibits inositol monophosphatase, depleting the "
        "phosphoinositide pool, and inhibits GSK-3. "
        "Indications: acute mania; bipolar maintenance, where it remains "
        "first line and prevents BOTH poles; augmentation in "
        "treatment-resistant depression. "
        "Monitoring: not metabolised - cleared renally and handled like "
        "sodium, which is the origin of every interaction it has. Trough "
        "level 12 hours post-dose, weekly until stable then "
        "three-monthly; maintenance 0.6 to 0.8 mmol/L; eGFR, calcium and "
        "TFTs six-monthly. "
        "SE: fine tremor, polyuria and polydipsia from nephrogenic "
        "diabetes insipidus, weight gain, hypothyroidism, "
        "hyperparathyroidism, chronic interstitial nephritis. "
        "Interactions: NSAIDs, ACE inhibitors and ARBs, and thiazides "
        "all cut renal clearance and raise the level, as do dehydration, "
        "vomiting, diarrhoea and a low-salt diet. "
        "Red flags: above 1.5 mmol/L expect coarse tremor, ataxia, "
        "dysarthria, vomiting, confusion and myoclonus; above 2.5 is "
        "life-threatening. Stop, rehydrate, dialyse if severe. Prescribe "
        "by brand - Australian modified-release and immediate-release "
        "lithium carbonate are not bioequivalent."
    ),

    "lamotrigine": (
        "Anticonvulsant and bipolar maintenance agent. "
        "MOA: use-dependent blockade of voltage-gated sodium channels, "
        "reducing presynaptic glutamate release. "
        "Indications: focal and generalised seizures including absence "
        "and Lennox-Gastaut; bipolar maintenance, where it prevents "
        "DEPRESSIVE relapse specifically and does not treat acute mania. "
        "Dose: about 10% of patients get a rash and roughly 1 in 1,000 "
        "get SJS or TEN, and the risk is driven almost entirely by "
        "starting dose and titration speed - so 25 mg daily for two "
        "weeks, 50 mg for two weeks, then fortnightly increases. Any "
        "rash means stop and review, not watch and wait. "
        "Interactions: this is the examinable part. Valproate inhibits "
        "glucuronidation and roughly doubles lamotrigine levels, so the "
        "starting dose is halved. Carbamazepine, phenytoin and "
        "phenobarbital induce it and the dose roughly doubles. "
        "Oestrogen-containing contraceptives induce it too, dropping "
        "levels by about half, with a rebound rise in the hormone-free "
        "week. Clearance rises sharply through pregnancy. "
        "SE: rash, headache, diplopia, insomnia, tremor; rarely aseptic "
        "meningitis and haemophagocytic lymphohistiocytosis. "
        "Note: with levetiracetam, one of the two preferred "
        "antiepileptics in pregnancy. After a break of more than five "
        "days, retitrate from the beginning."
    ),

    "sodium valproate": (
        "Broad-spectrum anticonvulsant and mood stabiliser. "
        "MOA: raises GABA by inhibiting GABA transaminase and inducing "
        "GAD, blocks voltage-gated sodium channels, and blocks T-type "
        "calcium channels - the last is why it works in absence "
        "seizures where carbamazepine makes them worse. "
        "Indications: absence seizures, juvenile myoclonic epilepsy and "
        "generalised tonic-clonic seizures, all first line; acute mania "
        "and bipolar maintenance; migraine prophylaxis. "
        "SE: weight gain, tremor, alopecia, polycystic ovarian "
        "morphology, thrombocytopenia and platelet dysfunction, "
        "idiosyncratic hepatotoxicity, pancreatitis, and hyperammonaemic "
        "encephalopathy that occurs with entirely normal LFTs and "
        "responds to carnitine. "
        "Interactions: an enzyme INHIBITOR, unlike most older "
        "antiepileptics - it raises lamotrigine, phenobarbital and the "
        "active carbamazepine epoxide. "
        "CI: pregnancy and women or girls of childbearing potential "
        "unless every alternative has failed; known or suspected "
        "mitochondrial disease, where POLG variants make fatal liver "
        "failure far more likely; urea cycle disorders. "
        "Red flags: the most teratogenic antiepileptic in use - major "
        "congenital malformation in about 10%, and neurodevelopmental "
        "impairment or autism in a much larger fraction of exposed "
        "children. The TGA carries a boxed warning; prescribing to a "
        "woman of childbearing potential requires a documented "
        "discussion and effective contraception, and this is "
        "specifically examined."
    ),

    "carbamazepine": (
        "Anticonvulsant, mood stabiliser and first-line drug for "
        "trigeminal neuralgia. "
        "MOA: use-dependent blockade of voltage-gated sodium channels, "
        "reducing high-frequency repetitive firing. "
        "Indications: focal seizures; trigeminal neuralgia; bipolar "
        "disorder second line. "
        "CI: absence and myoclonic seizures and generalised epilepsies "
        "such as JME, which it aggravates - prescribing it for an "
        "undifferentiated generalised epilepsy makes the patient worse. "
        "Screening: test HLA-B*1502 before starting in patients of Han "
        "Chinese, Thai, Malay or other South-East Asian ancestry - the "
        "allele carries a large increase in SJS and TEN risk. "
        "SE: rash in 5 to 10%, DRESS, dose-related hyponatraemia from "
        "SIADH that is worse in the elderly, benign leucopenia commonly "
        "and aplastic anaemia rarely, neural tube defects in pregnancy. "
        "Interactions: a potent CYP3A4, 2C9 and UGT inducer - lowers "
        "combined oral contraceptives to the point of contraceptive "
        "failure, and lowers warfarin, the DOACs, lamotrigine and "
        "quetiapine. It also induces its own metabolism over two to four "
        "weeks, so a dose that worked initially stops working. FBC, LFTs "
        "and sodium at baseline and periodically."
    ),

    "olanzapine": (
        "Atypical antipsychotic (thienobenzodiazepine). "
        "MOA: D2 and 5-HT2A antagonism with substantial M1, H1 and "
        "alpha-1 blockade. "
        "Indications: schizophrenia; acute mania and bipolar "
        "maintenance; acute behavioural disturbance by IM injection; "
        "adjunct in treatment-resistant depression; also well evidenced "
        "for chemotherapy-induced nausea and for appetite in palliative "
        "care. "
        "SE: the largest weight gain and metabolic burden of any "
        "antipsychotic except clozapine, with insulin resistance and "
        "dyslipidaemia that appear within months; sedation; "
        "anticholinergic dry mouth and constipation; postural "
        "hypotension. EPS and prolactin rise are modest at usual doses. "
        "Monitoring: weight and waist circumference, blood pressure, "
        "fasting glucose or HbA1c and lipids at baseline, at three "
        "months and then at least yearly. Metabolic monitoring after a "
        "first episode is the intervention most often skipped and most "
        "often regretted. "
        "Note: IM olanzapine given close to a parenteral benzodiazepine "
        "risks excessive sedation and cardiorespiratory depression - "
        "separate them by at least an hour. Weight gain is a leading "
        "reason young patients stop antipsychotics, so raise it before "
        "it happens; metformin has reasonable evidence for attenuating "
        "it."
    ),

    "quetiapine": (
        "Atypical antipsychotic (dibenzothiazepine) whose "
        "pharmacology changes with dose - which is the whole point of "
        "the drug. "
        "MOA: D2 and 5-HT2A antagonism with very fast D2 dissociation; "
        "potent H1 blockade gives sedation and alpha-1 blockade gives "
        "postural drop; the active metabolite norquetiapine is a "
        "noradrenaline reuptake inhibitor and 5-HT2C antagonist, which "
        "is where the antidepressant effect comes from. "
        "Dose: below about 50 mg the effect is essentially "
        "antihistamine sedation with no antipsychotic action at all; 150 "
        "to 300 mg is the antidepressant range; 400 to 800 mg is needed "
        "for schizophrenia. "
        "Indications: schizophrenia; acute mania; bipolar DEPRESSION, "
        "where it is one of very few agents with real evidence; adjunct "
        "in major depression. "
        "SE: sedation, postural hypotension during titration, weight "
        "gain and metabolic syndrome, dry mouth, QT prolongation. EPS "
        "and prolactin elevation are minimal, which with clozapine makes "
        "it one of the two usable antipsychotics in Parkinson disease. "
        "Note: low-dose quetiapine is widely prescribed as a hypnotic. "
        "It has no good evidence in that role, carries the full "
        "metabolic risk, is not subsidised for it, and is diverted in "
        "custodial and inpatient settings - recognising the "
        "inappropriate indication is worth more marks than reciting the "
        "receptor profile."
    ),

    # ═══════ Batch 2: measured by deck frequency, 21 August ═════════════
    #
    # AnkiMCP against `deck:active::current::*`, one term per query, stems
    # rather than exact phrases, per the distortions recorded in the
    # handover. Note counts in the comment beside each. Ordered by
    # frequency, not by how interesting the drug is: prednisolone returns
    # 32 notes and had a 4-line summary that deferred to a `prednisone`
    # entry, which is the same dead-cross-reference shape the oestradiol
    # merge left behind.
    #
    # Deliberately NOT written, so nobody re-measures them: mirtazapine
    # 0, pantoprazole 0, clopidogrel 0, salbutamol 0, escitalopram 2,
    # lorazepam 2.

    "prednisolone": (  # 32 notes
        "Intermediate-acting glucocorticoid and the default oral "
        "corticosteroid in Australian practice. "
        "MOA: glucocorticoid receptor agonist, about four times the "
        "potency of hydrocortisone with much less mineralocorticoid "
        "effect; already active, unlike prednisone, which needs hepatic "
        "conversion - so prednisolone is the one to use in liver "
        "disease. 5 mg prednisolone is equivalent to 20 mg "
        "hydrocortisone. "
        "Indications: asthma and COPD exacerbations; acute gout; "
        "polymyalgia rheumatica and giant cell arteritis, where visual "
        "symptoms mean high dose now, not after biopsy; IBD flares. "
        "SE: hyperglycaemia, which will unmask or destabilise diabetes; "
        "weight gain and Cushingoid change; hypertension; osteoporosis "
        "and avascular necrosis; myopathy; cataract and "
        "glaucoma; thin skin and bruising; insomnia and mood change up "
        "to frank steroid psychosis; infection risk, including "
        "reactivation of tuberculosis and strongyloides. "
        "Note: a course under three weeks can usually stop outright, but "
        "longer or repeated courses suppress the HPA axis and must be "
        "tapered - and that patient then needs sick-day rules, because "
        "an intercurrent illness on a suppressed axis is an adrenal "
        "crisis. Consider bone protection at 7.5 mg for three months, "
        "and PJP prophylaxis at 20 mg for four weeks."
    ),

    "methotrexate": (  # 18 notes
        "Antifolate, and the anchor DMARD in rheumatoid arthritis. "
        "MOA: inhibits dihydrofolate reductase, but the low-dose "
        "anti-inflammatory effect is mostly adenosine-mediated rather "
        "than antiproliferative - hence a DMARD dose a hundredth of the "
        "oncology dose. "
        "Indications: rheumatoid and psoriatic arthritis, psoriasis, "
        "IBD; ectopic pregnancy and gestational trophoblastic disease; "
        "high dose in ALL and lymphoma. "
        "Dose: WEEKLY, and this is the most dangerous prescribing error "
        "in the drug book - daily dosing causes fatal pancytopenia and "
        "mucositis, and it happens through transcription rather than "
        "ignorance. Name the day on the script. Co-prescribe folic acid "
        "on a different day. "
        "SE: nausea, mucositis, hepatotoxicity, myelosuppression, "
        "alopecia, and an idiosyncratic pneumonitis that can appear at "
        "any point as dry cough and breathlessness. "
        "Interactions: trimethoprim and co-trimoxazole are also "
        "antifolates and the combination causes pancytopenia; NSAIDs and "
        "PPIs reduce renal clearance. "
        "CI: pregnancy, significant renal impairment, active infection, "
        "significant liver disease. "
        "Monitoring: FBC, LFTs and renal function at baseline, then "
        "fortnightly to monthly for the first three months and "
        "three-monthly after. Rescue is folinic acid, not folic acid."
    ),

    "aspirin": (  # 16 notes
        "Antiplatelet at low dose, NSAID at high dose. "
        "MOA: irreversibly acetylates COX-1, so thromboxane A2 "
        "production is gone for that platelet's whole 7 to 10 day life "
        "while nucleated endothelium simply makes more enzyme - that "
        "asymmetry is the entire basis of low-dose selectivity, and it "
        "is why the effect outlasts the drug. "
        "Indications: acute coronary syndrome, loading dose then daily; "
        "secondary prevention after MI, ischaemic stroke or in "
        "peripheral arterial disease; dual antiplatelet therapy after "
        "stenting; low dose nocte from early pregnancy for pre-eclampsia "
        "prophylaxis in women at high risk. Not routine for primary "
        "prevention - the bleeding cost outweighs the benefit in most "
        "people. "
        "SE: gastric erosion and upper GI bleeding, dyspepsia, "
        "bronchospasm in aspirin-exacerbated respiratory disease, which "
        "runs with asthma and nasal polyps; tinnitus at high dose. "
        "CI: children and adolescents with a viral illness, because of "
        "Reye syndrome; active bleeding; third trimester. "
        "Note: salicylate overdose gives a respiratory alkalosis and a "
        "metabolic acidosis together, with tinnitus, hyperventilation "
        "and hyperthermia. Because inhibition is irreversible, stopping "
        "it days before surgery does not restore platelet function "
        "immediately."
    ),

    "hydrocortisone": (  # 15 notes
        "Short-acting glucocorticoid, and the reference against which "
        "the others are measured. "
        "MOA: binds both glucocorticoid and mineralocorticoid receptors "
        "- the substantial mineralocorticoid activity is precisely why "
        "it is the REPLACEMENT steroid rather than an anti-inflammatory "
        "one. 20 mg hydrocortisone is equivalent to 5 mg prednisolone. "
        "Indications: adrenal insufficiency, given in divided doses with "
        "the larger dose on waking to approximate the diurnal rhythm; "
        "adrenal crisis, as a bolus followed by regular dosing alongside "
        "aggressive fluid resuscitation; severe asthma; as an adjunct "
        "after adrenaline in anaphylaxis, where it does nothing acutely "
        "and must never delay or replace the adrenaline; topically in "
        "eczema. "
        "Note: in suspected adrenal crisis, treat first and confirm "
        "later - but hydrocortisone cross-reacts in the cortisol assay "
        "and dexamethasone does not, so if the diagnosis genuinely has "
        "to be established, dexamethasone is the steroid to give. "
        "Every patient on replacement needs sick-day rules, a steroid "
        "card and an emergency ampoule at home: double the dose for a "
        "febrile illness, and give it parenterally if vomiting."
    ),

    "amiodarone": (  # 14 notes
        "Class III antiarrhythmic that in practice blocks all four "
        "Vaughan Williams classes. "
        "MOA: prolongs repolarisation by potassium channel blockade, "
        "with sodium channel, beta and calcium channel effects on top. "
        "Indications: shock-refractory VF and pulseless VT; "
        "haemodynamically stable VT; rhythm control in atrial "
        "fibrillation, including where structural heart disease rules "
        "out flecainide. "
        "Half-life 50 to 100 days with an enormous volume of "
        "distribution, so it needs loading, and both its effect and its "
        "toxicity persist for months after the last dose. "
        "SE: the molecule is 37% iodine by weight, so thyroid disease is "
        "common in both directions - hypothyroidism is usually managed "
        "with thyroxine while continuing the drug, whereas "
        "thyrotoxicosis splits into iodine-induced type 1 and a "
        "destructive thyroiditis type 2 treated with corticosteroid. "
        "Also pulmonary toxicity and fibrosis, presenting as dry cough "
        "and exertional dyspnoea; hepatitis; near-universal corneal "
        "microdeposits; a slate-grey photosensitive skin discolouration; "
        "optic and peripheral neuropathy; bradycardia. "
        "Interactions: roughly doubles digoxin levels and markedly "
        "potentiates warfarin, so both doses come down when amiodarone "
        "starts; raises statin myopathy risk. "
        "Monitoring: TFTs and LFTs at baseline and six-monthly, chest "
        "imaging at baseline and if symptomatic, ECG."
    ),

    "haloperidol": (  # 13 notes
        "High-potency typical antipsychotic (butyrophenone). "
        "MOA: potent D2 antagonism, and the four dopamine pathways "
        "explain the whole side-effect profile - mesolimbic blockade is "
        "the antipsychotic effect, nigrostriatal blockade the "
        "extrapyramidal effects, tuberoinfundibular blockade the "
        "prolactin rise. "
        "Indications: schizophrenia; acute behavioural disturbance; "
        "short-term in hyperactive delirium at the lowest dose; "
        "Tourette; intractable nausea in palliative care. "
        "CI: Parkinson disease and dementia with Lewy bodies, where "
        "sensitivity reactions can be severe and prolonged. "
        "SE: acute dystonia within hours to days, reversed with "
        "benzatropine; akathisia, an inner restlessness that is "
        "repeatedly mistaken for worsening agitation and treated by "
        "raising the dose, which makes it worse; drug-induced "
        "parkinsonism over weeks; tardive dyskinesia over months to "
        "years, which may not reverse. Hyperprolactinaemia gives "
        "galactorrhoea and reduced bone density. "
        "Red flags: dose-related QT prolongation, worst with the IV "
        "route - check the ECG and correct potassium and magnesium. "
        "Neuroleptic malignant syndrome is fever, lead-pipe rigidity, "
        "autonomic instability and a raised CK, and it is a stop-the-drug "
        "emergency. "
        "Note: antipsychotics raise mortality and stroke risk in "
        "dementia."
    ),

    "risperidone": (  # 10 notes
        "Atypical antipsychotic (benzisoxazole). "
        "MOA: D2 plus 5-HT2A antagonism; the 5-HT2A blockade is what "
        "buys the reduced EPS, and it stops buying it above about 6 mg "
        "daily, at which point risperidone behaves like a typical. "
        "Indications: schizophrenia; bipolar mania; short-term for "
        "behavioural and psychological symptoms of dementia, the only "
        "antipsychotic with an Australian indication for it and one "
        "limited to a few weeks; irritability in autism. "
        "SE: the highest prolactin elevation of any atypical, which "
        "matters clinically rather than as a number - galactorrhoea, "
        "amenorrhoea, sexual dysfunction and reduced bone density are "
        "common reasons young patients stop taking it and do not say "
        "why. Dose-related EPS, moderate weight gain, postural "
        "hypotension during titration. "
        "Note: its active metabolite is paliperidone, cleared renally, "
        "so renal impairment demands a dose reduction where hepatic "
        "impairment matters less. The fortnightly long-acting injection "
        "does not reach therapeutic levels for about three weeks and "
        "needs oral cover over that gap - stopping the tablets on the "
        "day of the first injection is a relapse waiting to happen."
    ),

    "diazepam": (  # 8 notes
        "Long-acting benzodiazepine. "
        "MOA: positive allosteric modulation at the GABA-A "
        "benzodiazepine site, increasing the FREQUENCY of chloride "
        "channel opening - it needs GABA already present, which is why "
        "it has a ceiling that barbiturates do not. "
        "Indications: alcohol withdrawal, symptom-triggered; status "
        "epilepticus; muscle spasm and spasticity; short-term severe "
        "anxiety. "
        "Half-life is long and its active metabolites longer still, so "
        "it accumulates - a single dose is short-acting because the drug "
        "redistributes out of the brain, not because it has left the "
        "body. In alcohol withdrawal that long tail is a feature, since "
        "the drug self-tapers; in an older patient or in liver disease "
        "it is the problem, and oxazepam or lorazepam are the ones to "
        "reach for because they are only glucuronidated. "
        "SE: sedation, anterograde amnesia, falls and hip fractures in "
        "the elderly, respiratory depression when combined with opioids "
        "or alcohol, paradoxical disinhibition, and tolerance and "
        "dependence within weeks of regular use. "
        "Note: never stop abruptly after regular use - withdrawal "
        "causes seizures and delirium. Flumazenil is rarely the right "
        "answer and precipitates seizures in a dependent or mixed "
        "overdose."
    ),

    "spironolactone": (  # 7 notes
        "Potassium-sparing diuretic and mineralocorticoid receptor "
        "antagonist. "
        "MOA: competitive MR blockade in the collecting duct reduces "
        "sodium reabsorption and potassium excretion; it also blocks "
        "androgen and progesterone receptors, which is simultaneously "
        "its main nuisance effect and its therapeutic mechanism in "
        "hirsutism. "
        "Indications: HFrEF added to standard therapy, with a mortality "
        "benefit; resistant hypertension, where it is the fourth-line "
        "agent of choice; primary aldosteronism; ascites in cirrhosis, "
        "where it is the first-line diuretic and is combined with "
        "furosemide in a fixed ratio; acne and hirsutism in women. "
        "SE: hyperkalaemia is the dominant risk and it is the one that "
        "kills - multiplied by an ACE inhibitor or ARB, NSAIDs, "
        "potassium supplements, renal impairment and, easily missed, "
        "trimethoprim, which blocks the epithelial sodium channel like "
        "amiloride. Gynaecomastia and breast tenderness in men, "
        "menstrual irregularity in women. "
        "Monitoring: potassium and creatinine at baseline, at about one "
        "week and one month, after every dose change, and during any "
        "intercurrent illness - withhold it in acute illness with "
        "vomiting, diarrhoea or dehydration. "
        "Note: a small creatinine rise on starting is haemodynamic and "
        "expected. Eplerenone is the alternative if gynaecomastia is "
        "intolerable."
    ),

    "aripiprazole": (  # 5 notes
        "Atypical antipsychotic and dopamine system stabiliser. "
        "MOA: D2 PARTIAL agonist, so it behaves as an antagonist where "
        "dopamine is high and an agonist where it is low, with 5-HT2A "
        "antagonism and 5-HT1A partial agonism alongside. "
        "Indications: schizophrenia; bipolar mania; adjunct in major "
        "depression; irritability in autism; Tourette syndrome. "
        "SE: akathisia is the signature effect and the reason patients "
        "stop it - an inner restlessness that reads as anxiety or "
        "agitation, is often answered with a dose increase, and gets "
        "worse when it is. Treat by reducing the dose, and propranolol "
        "helps. Nausea, insomnia and headache early on. "
        "Red flags: impulse control disorders - pathological gambling, "
        "hypersexuality, compulsive shopping and binge eating - carry a "
        "TGA warning and resolve on withdrawal. Patients almost never "
        "volunteer them, so ask directly at review. "
        "Note: metabolically the most favourable of the atypicals and "
        "close to prolactin-sparing, which is what earns it a place "
        "despite the akathisia. Because it is a partial agonist, "
        "switching to it abruptly from a full antagonist can precipitate "
        "rebound psychosis and agitation - cross-taper."
    ),

    "furosemide": (  # 5 notes
        "Loop diuretic. "
        "MOA: inhibits NKCC2 in the thick ascending limb, abolishing the "
        "medullary concentrating gradient and producing the most potent "
        "natriuresis available. In acute pulmonary oedema it also "
        "venodilates within minutes, before any diuresis, which is why "
        "the patient improves before the catheter bag fills. "
        "Indications: acute pulmonary oedema; congestion in chronic "
        "heart failure; oedema in nephrotic syndrome and cirrhosis; "
        "hypercalcaemia once the patient is volume-replete. "
        "Dose: oral bioavailability is about half and highly variable, "
        "so the IV dose is roughly half the oral one. The drug only "
        "works from inside the tubular lumen, reached by active "
        "secretion, so anything competing for that transporter - NSAIDs "
        "in particular - or a low albumin blunts the response. That is "
        "most of what is meant by diuretic resistance. "
        "SE: hypokalaemia, hypomagnesaemia, hyponatraemia, metabolic "
        "alkalosis, hyperuricaemia and gout, hypovolaemia and prerenal "
        "AKI, hyperglycaemia, and ototoxicity with rapid IV "
        "administration, high doses or concurrent aminoglycosides. "
        "Monitoring: electrolytes, renal function, daily weight and "
        "fluid balance."
    ),

    "sertraline": (  # 4 notes
        "SSRI, and a reasonable default first-line antidepressant. "
        "MOA: blocks the serotonin transporter, raising synaptic 5-HT; "
        "the receptor change takes weeks, which is why the effect does "
        "and the side effects do not. "
        "Indications: major depression, generalised anxiety, panic "
        "disorder, OCD, PTSD, social anxiety. "
        "SE: nausea and loose stools in the first week or two, usually "
        "transient; sexual dysfunction, which is common, persistent and "
        "under-reported unless asked about directly; insomnia or "
        "sedation; hyponatraemia from SIADH, particularly in older "
        "patients in the first weeks; increased bleeding risk, "
        "compounded by NSAIDs or anticoagulants. "
        "Note: minimal CYP inhibition makes it the SSRI of choice with "
        "polypharmacy, after myocardial infarction, and in pregnancy and "
        "breastfeeding. Anxiety can worsen in the first week, so start "
        "low and warn the patient, or they will stop on day three. "
        "Red flags: review within one to two weeks in patients under 25, "
        "in whom suicidal ideation may increase early. Serotonin "
        "syndrome with MAOIs, tramadol, linezolid or triptans is "
        "agitation, clonus, hyperreflexia and hyperthermia. Taper on "
        "stopping."
    ),

    "venlafaxine": (  # 4 notes
        "SNRI. "
        "MOA: serotonin reuptake inhibition at low dose, with "
        "noradrenaline reuptake inhibition added only at higher doses - "
        "so below about 150 mg daily it is functionally an SSRI, and a "
        "patient described as having failed an SNRI at 75 mg has not. "
        "Indications: major depression, generalised anxiety, panic "
        "disorder, social anxiety, neuropathic pain. "
        "SE: dose-related hypertension from the noradrenergic effect, so "
        "check blood pressure before and after any dose increase; "
        "nausea; sweating; sexual dysfunction. "
        "Red flags: the worst discontinuation syndrome of the class, "
        "because the half-life is short - dizziness, electric-shock "
        "sensations, irritability and flu-like symptoms within a day of "
        "a missed dose. Use the extended-release form and taper slowly. "
        "It is also more cardiotoxic in overdose than any SSRI, with "
        "seizures and arrhythmias, which is worth weighing when suicide "
        "risk is part of the presentation. "
        "CI: an MAOI within the preceding two weeks; caution in "
        "uncontrolled hypertension."
    ),

    # ═══════ Batch 3: measured 21 August, same method ═══════════════════
    #
    # Deliberately NOT written: amoxicillin 3, vancomycin 2,
    # flucloxacillin 2, morphine 2.

    "insulin": (  # 26 notes - NEW ENTRY, see NEW_DRUGS below
        "Anabolic peptide hormone, given as replacement in type 1 "
        "diabetes and as escalation in type 2. "
        "MOA: insulin receptor tyrosine kinase drives GLUT4 to the "
        "membrane in muscle and fat, suppresses hepatic "
        "gluconeogenesis, and switches off lipolysis and ketogenesis - "
        "the last is why its absence gives ketoacidosis and why a type 1 "
        "patient never stops basal insulin, even when not eating. "
        "Types: rapid-acting analogues (aspart, lispro) act within about "
        "15 minutes and cover a meal; short-acting neutral insulin is "
        "slower; intermediate isophane sits between; long-acting "
        "analogues (glargine, degludec) are near-peakless basal cover. "
        "Indications: all type 1 diabetes; type 2 when other agents fail "
        "or during acute illness, steroids, surgery or pregnancy; DKA and "
        "hyperosmolar states as an infusion; hyperkalaemia, with glucose. "
        "SE: hypoglycaemia, the dose-limiting toxicity - autonomic "
        "warning symptoms are blunted by beta blockers and lost in "
        "hypoglycaemia unawareness; weight gain; "
        "lipohypertrophy at unrotated injection sites, which makes "
        "absorption erratic and is worth palpating for when control "
        "looks inexplicably unstable. "
        "Note: sick-day rules run opposite to intuition - during "
        "intercurrent illness insulin requirements RISE, so basal "
        "insulin continues even if the patient is not eating, with "
        "increased monitoring and ketone testing."
    ),

    "thiamine": (  # 24 notes
        "Water-soluble vitamin B1. "
        "MOA: as thiamine pyrophosphate it is the cofactor for pyruvate "
        "dehydrogenase, alpha-ketoglutarate dehydrogenase and "
        "transketolase, so deficiency blocks aerobic glucose metabolism "
        "in exactly the tissues that cannot use anything else. Stores "
        "last only two to three weeks. "
        "Indications: Wernicke encephalopathy, established or suspected; "
        "prophylaxis in alcohol withdrawal, chronic alcohol use, "
        "hyperemesis gravidarum, bariatric surgery, prolonged vomiting "
        "or malnutrition; refeeding syndrome; wet and dry beriberi. "
        "Red flags: Wernicke is a clinical diagnosis and the classical "
        "triad of confusion, ophthalmoplegia and ataxia is present in a "
        "minority - so treat on suspicion, because untreated Wernicke "
        "becomes Korsakoff amnesia, which does not reverse. Give "
        "high-dose PARENTERAL thiamine; oral absorption is saturable and "
        "cannot achieve the required levels. "
        "Note: give thiamine BEFORE or with glucose in anyone at risk. A "
        "glucose load in a thiamine-deplete patient consumes what little "
        "cofactor remains and can precipitate the encephalopathy it was "
        "meant to treat. This is one of the few genuinely "
        "iatrogenic-if-you-get-the-order-wrong interventions on the "
        "ward. Anaphylaxis to IV thiamine is very rare and is not a "
        "reason to withhold it."
    ),

    "metronidazole": (  # 11 notes
        "Nitroimidazole antimicrobial covering anaerobes and protozoa. "
        "MOA: reduced by anaerobic organisms to a nitro radical that "
        "fragments DNA - so it is selectively activated only where there "
        "is no oxygen, which is also why it has no aerobic activity at "
        "all. "
        "Indications: intra-abdominal and pelvic sepsis, in combination "
        "for Gram-negative and enterococcal cover; Clostridioides "
        "difficile colitis; dental and other anaerobic abscesses; "
        "aspiration pneumonia; bacterial vaginosis and trichomoniasis; "
        "amoebiasis and giardiasis; part of Helicobacter pylori "
        "eradication. "
        "SE: metallic taste, nausea, and with prolonged courses a "
        "peripheral neuropathy that may not fully recover - the practical "
        "consequence is that duration matters more than dose. Rarely "
        "encephalopathy and cerebellar toxicity. "
        "Interactions: a disulfiram-like reaction with alcohol - "
        "flushing, vomiting, tachycardia - so warn the patient during "
        "treatment and for a day or two after. It also potentiates "
        "warfarin. "
        "Note: excellent oral bioavailability, so there is rarely a "
        "reason to keep it intravenous once the patient is absorbing."
    ),

    "gentamicin": (  # 7 notes
        "Aminoglycoside, active against aerobic Gram negatives including "
        "Pseudomonas, and synergistic with a beta lactam against "
        "enterococci and staphylococci. "
        "MOA: irreversibly binds the 30S ribosomal subunit causing "
        "misreading; uptake is oxygen-dependent, hence no anaerobic "
        "activity, and impaired in the acidic environment of an abscess. "
        "Concentration-dependent killing with a long post-antibiotic "
        "effect, which is the rationale for once-daily dosing. "
        "Indications: severe Gram-negative sepsis, usually empirically "
        "and for a short course; pyelonephritis; surgical prophylaxis; "
        "infective endocarditis in combination. "
        "Dose: on lean or adjusted body weight, with renal function and "
        "levels guiding subsequent doses - a trough that has not fallen "
        "means the drug has not cleared, not that the dose was small. "
        "SE: nephrotoxicity, typically non-oliguric and usually "
        "reversible; ototoxicity, both cochlear and vestibular, which is "
        "NOT reversible and is the reason short courses are the rule; "
        "rarely neuromuscular blockade. "
        "Note: risk rises with duration, concurrent loop diuretics, "
        "vancomycin, contrast and pre-existing renal impairment. Beyond "
        "48 to 72 hours, the question is whether it can stop rather than "
        "what the next dose is."
    ),

    "heparin": (  # 6 notes
        "Unfractionated heparin, an indirect parenteral anticoagulant. "
        "MOA: binds antithrombin and accelerates it roughly a thousandfold "
        "against thrombin (IIa) and factor Xa. Inhibiting thrombin needs "
        "the long saccharide chain to bridge both molecules, which is the "
        "structural reason UFH inhibits IIa and Xa about equally while the "
        "shorter low molecular weight heparins are far more Xa-selective. "
        "Indications: where anticoagulation may need to be switched off "
        "quickly or renal function is poor - the half-life is about an "
        "hour and it is not renally cleared, so it is preferred in severe "
        "renal impairment, around surgery and in the unstable patient. "
        "Monitoring: APTT ratio or anti-Xa on an infusion. LMWH needs no "
        "routine monitoring, which is most of why it displaced UFH. "
        "SE: bleeding; heparin-induced thrombocytopenia, an "
        "immune-mediated PROTHROMBOTIC platelet fall around day 5 to 10 "
        "that must not be treated with platelet transfusion and requires "
        "stopping all heparin including flushes; osteoporosis with "
        "prolonged use; hyperkalaemia from aldosterone suppression. "
        "Note: protamine reverses UFH fully and LMWH only partially."
    ),

    "warfarin": (  # 5 notes
        "Vitamin K antagonist. "
        "MOA: inhibits vitamin K epoxide reductase, so factors II, VII, "
        "IX and X cannot be gamma-carboxylated. Onset follows each "
        "factor's half-life, and because protein C goes first there is a "
        "transient PROCOAGULANT window - which is why loading without "
        "heparin cover risks skin necrosis and why bridging exists. "
        "Indications: mechanical heart valves and moderate to severe "
        "mitral stenosis with AF, where the DOACs are contraindicated "
        "and warfarin remains the only option; antiphospholipid "
        "syndrome; VTE and AF where a DOAC is unsuitable. "
        "Monitoring: INR, target 2 to 3 for most indications and higher "
        "for mechanical valves. "
        "Interactions: extensive, and the two directions matter equally. "
        "Antibiotics, amiodarone, metronidazole, azole antifungals, "
        "cranberry juice and acute alcohol raise the INR; carbamazepine, "
        "phenobarbital, rifampicin, St John's wort and a sudden increase "
        "in dietary vitamin K lower it. Intercurrent illness alone will "
        "move it. "
        "Note: reversal depends on bleeding, not on the number - withhold "
        "for a high INR without bleeding, oral vitamin K if higher, and "
        "for major bleeding give IV vitamin K with prothrombin complex "
        "concentrate, since vitamin K alone takes hours."
    ),

    "naloxone": (  # 5 notes
        "Competitive opioid receptor antagonist. "
        "MOA: displaces opioids at the mu receptor with higher affinity "
        "and no intrinsic activity. "
        "Indications: opioid-induced respiratory depression. The target "
        "is adequate ventilation, NOT full consciousness - titrate in "
        "small increments, because a large bolus in a dependent patient "
        "precipitates acute withdrawal, agitation and vomiting into an "
        "unprotected airway, and occasionally flash pulmonary oedema. "
        "Half-life is shorter than that of most opioids, and far shorter "
        "than methadone, slow-release oxycodone or a fentanyl patch - so "
        "the patient who wakes up can re-sedate an hour later, and either "
        "needs prolonged observation or an infusion. Discharging them "
        "after a single dose is the classic error. "
        "Route: IV, IM or intranasal; the take-home intranasal product is "
        "available without prescription in Australia and is a reasonable "
        "thing to offer anyone on high-dose opioids or with a history of "
        "overdose. "
        "Note: it does nothing for a non-opioid cause, so an unimproved "
        "conscious state after adequate naloxone is a reason to look "
        "elsewhere rather than to give more."
    ),

    "ceftriaxone": (  # 6 notes
        "Third-generation cephalosporin. "
        "MOA: beta lactam binding penicillin-binding proteins to block "
        "cell wall cross-linking. "
        "Indications: community-acquired pneumonia requiring admission; "
        "pyelonephritis; bacterial meningitis, where it crosses inflamed "
        "meninges well and is given with dexamethasone in adults; "
        "gonorrhoea as a single IM dose; septic arthritis and cellulitis "
        "with atypical risk; empirical cover in sepsis of unknown source. "
        "Note: once-daily dosing and biliary as well as renal excretion, "
        "so no dose adjustment in renal impairment - which together with "
        "the long half-life is why it suits home and outpatient "
        "parenteral therapy. "
        "CI: neonates, in whom it displaces bilirubin from albumin and "
        "risks kernicterus, and it must never be co-administered with "
        "calcium-containing fluids in that group. "
        "SE: rash, diarrhoea including C. difficile, biliary sludging "
        "that can mimic cholecystitis, and rarely haemolysis. "
        "Red flags: it does not cover Pseudomonas, Listeria or MRSA - so "
        "meningitis in the elderly, pregnant or immunosuppressed needs "
        "benzylpenicillin added for Listeria, and cross-reactivity with "
        "penicillin allergy is real but much lower than the traditional "
        "10% figure."
    ),

    "doxycycline": (  # 6 notes
        "Tetracycline. "
        "MOA: binds the 30S subunit and blocks aminoacyl-tRNA docking; "
        "bacteriostatic, with broad activity including the intracellular "
        "organisms that beta lactams cannot reach. "
        "Indications: atypical and community-acquired pneumonia; "
        "chlamydia and pelvic inflammatory disease; Q fever, rickettsial "
        "infection, leptospirosis, melioidosis eradication and Lyme "
        "disease; acne and rosacea; malaria prophylaxis; COPD "
        "exacerbation. "
        "SE: photosensitivity, which matters in Australia and needs "
        "saying out loud; pill-induced oesophagitis, so take it upright "
        "with a full glass of water and not at bedtime; nausea; "
        "candidiasis; benign intracranial hypertension. "
        "CI: pregnancy, breastfeeding and children under eight, because "
        "it chelates calcium in developing bone and teeth and causes "
        "permanent discolouration. "
        "Interactions: absorption is blocked by calcium, iron, magnesium "
        "and antacids, so separate them by at least two hours - a "
        "genuinely common reason for apparent treatment failure. "
        "Note: unlike other tetracyclines it is safe in renal impairment, "
        "being cleared largely through the gut."
    ),

    "metformin": (  # 5 notes
        "Biguanide, and first-line pharmacotherapy in type 2 diabetes. "
        "MOA: activates AMP-activated protein kinase, suppressing hepatic "
        "gluconeogenesis and improving peripheral insulin sensitivity. It "
        "does not stimulate insulin secretion, which is why it does not "
        "cause hypoglycaemia on its own and does not cause weight gain. "
        "Indications: type 2 diabetes, alone or with anything else; "
        "polycystic ovary syndrome, for cycle regularity and ovulation; "
        "attenuating antipsychotic-associated weight gain. "
        "SE: nausea, diarrhoea and abdominal discomfort, which are the "
        "usual reason people stop - start low, take it with food, and "
        "switch to the extended-release form rather than abandoning the "
        "drug. Long-term use lowers vitamin B12, so check it if there is "
        "anaemia or a peripheral neuropathy. "
        "Red flags: lactic acidosis is rare but has high mortality, and "
        "it happens when metformin accumulates in renal impairment or "
        "when tissue hypoxia is already present. Withhold during any "
        "acute illness with dehydration, vomiting, sepsis or "
        "hypoperfusion, and around iodinated contrast and surgery. "
        "Renal: reduce the dose as eGFR falls and stop below about 30."
    ),
}


# ═══════════════════════════════════════════════════════════════════════
# Drugs absent from the base vocabulary entirely.
# ═══════════════════════════════════════════════════════════════════════
#
# Mirrors NEW_CONDITIONS. Compiled into the library under its own
# `new_drugs` key and merged by `pearls/_drugs.py` at runtime, NOT
# appended to `drugs` - see the note there. The summary is taken from
# DRUG_SUMMARIES rather than written here, so the text lives in one
# place and the two cannot drift.
#
# `insulin` is the first entry and shows why the mechanism was needed.
# Six specific insulins are in the library - glargine, detemir, lispro,
# aspart, isophane and degludec - but the bare word `insulin` was not,
# and the bare word is what 26 notes in the active decks actually say.
# So the single highest-frequency drug term measured across three
# batches highlighted nothing at all, and it looked exactly like a term
# nobody had written a card about.

NEW_DRUGS = [
    {
        "generic": "insulin",
        "aliases": ["insulin therapy"],
        "brands": [],
        "summary": "",
    },
]

# ═══════════════════════════════════════════════════════════════════════
# Preclinical terms absent from the base vocabulary: drug CLASSES.
# ═══════════════════════════════════════════════════════════════════════
#
# Compiled under a `new_preclinical` key and merged by
# `pearls/_preclinical.py` at runtime, for the same reasons NEW_DRUGS is
# kept out of `drugs`.
#
# Why preclinical rather than NEW_DRUGS: a class is not a drug. It has no
# generic name and no DrugBank monograph, so routing it through the drug
# path would label the popup DrugBank and offer a button that searches
# for the word "antibiotics". `preclinical` already carries a
# `pharmacology` category with 30 entries, gives the right source label,
# and falls back to a Wikipedia search.
#
# Why they exist at all: the insulin finding generalised. Probing 33
# class terms across all seven vocabularies returned exactly two hits,
# both accidental - `ACE` and `DOAC` matched as acronyms. Everything
# else matched nothing, and the frequencies are the highest measured
# anywhere in the library:
#
#   antipsychotic 55, antibiotic 39, benzodiazepine 33, NSAID 31,
#   diuretic 28, chemotherapy 26, opioid 23, immunosuppress- 23,
#   corticosteroid 21, antidepressant 21, anticoagulation 21,
#   beta blocker 15, statin 14
#
# Every one of those was dead. Whole categories of card highlighted
# nothing, and it was invisible for the reason the twelve preclinical
# terms were invisible in §3 of the handover: silence looks like
# absence of content, not absence of matching.

NEW_PRECLINICAL = [
    {
        "name": "Antipsychotics",  # 55 notes
        "aliases": ["antipsychotic", "neuroleptic", "neuroleptics"],
        "category": "pharmacology",
        "summary": (
            "Drug class defined by dopamine D2 receptor antagonism in the "
            "mesolimbic pathway. "
            "Classification: first generation (typicals - haloperidol, "
            "chlorpromazine, zuclopenthixol) are high-affinity D2 "
            "antagonists with prominent extrapyramidal effects; second "
            "generation (atypicals - olanzapine, quetiapine, risperidone, "
            "aripiprazole, clozapine) add 5-HT2A antagonism or partial "
            "agonism, trading EPS for metabolic burden. The division is "
            "clinically useful and pharmacologically loose. "
            "Note: efficacy against positive symptoms is essentially "
            "equivalent across the class, with the single exception of "
            "clozapine in treatment resistance. So the choice is made on "
            "side-effect profile and on what the patient will actually "
            "keep taking, not on potency. "
            "SE: the four dopamine pathways predict most of it - "
            "nigrostriatal blockade gives acute dystonia, akathisia, "
            "parkinsonism and tardive dyskinesia; tuberoinfundibular "
            "blockade gives hyperprolactinaemia. Off-target: metabolic "
            "syndrome, QT prolongation, sedation, anticholinergic burden, "
            "postural hypotension. "
            "Red flags: neuroleptic malignant syndrome. In dementia the "
            "whole class raises mortality and stroke risk. "
            "Monitoring: weight and waist, blood pressure, fasting "
            "glucose or HbA1c, lipids and ECG at baseline, at three "
            "months and then yearly."
        ),
    },
    {
        "name": "Antibiotics",  # 39 notes
        "aliases": ["antibiotic", "antibacterial", "antibacterials",
                    "antimicrobial", "antimicrobials"],
        "category": "pharmacology",
        "summary": (
            "Drugs that kill or inhibit bacteria, grouped by the "
            "structure they attack. "
            "Classification: cell wall synthesis (beta lactams - "
            "penicillins, cephalosporins, carbapenems - and glycopeptides "
            "such as vancomycin); protein synthesis at the 30S "
            "(aminoglycosides, tetracyclines) or 50S (macrolides, "
            "lincosamides, oxazolidinones); nucleic acid (quinolones "
            "inhibit DNA gyrase, rifampicin RNA polymerase); folate "
            "synthesis (trimethoprim, sulfonamides); membrane disruption "
            "(polymyxins). "
            "Note: beta lactams and glycopeptides are time-dependent, so "
            "the driver of killing is how long the concentration stays "
            "above MIC - which is why they are dosed frequently or by "
            "infusion. Aminoglycosides and quinolones are "
            "concentration-dependent with a post-antibiotic effect, hence "
            "once-daily dosing. "
            "Australian notes: prescribing follows Therapeutic "
            "Guidelines: Antibiotic, which is narrower than most "
            "international sources - Australian empirical regimens use "
            "less third-generation cephalosporin and less "
            "fluoroquinolone, and a US protocol read straight off a "
            "textbook will be wrong here. "
            "Red flags: reported penicillin allergy is wrong in about 90% "
            "of cases and delabelling matters, because the alternatives "
            "are broader, more toxic and less effective."
        ),
    },
    {
        "name": "Benzodiazepines",  # 33 notes
        "aliases": ["benzodiazepine", "benzo", "benzos"],
        "category": "pharmacology",
        "summary": (
            "Positive allosteric modulators at the GABA-A receptor. "
            "MOA: increase the FREQUENCY of chloride channel opening, "
            "which requires GABA already to be present - the reason the "
            "class has a ceiling on respiratory depression that "
            "barbiturates do not, and the reason that ceiling disappears "
            "the moment an opioid or alcohol is added. "
            "Classification: by half-life and by metabolism. Diazepam and "
            "clonazepam are long-acting with active metabolites; "
            "temazepam and oxazepam are short and undergo glucuronidation "
            "ONLY, which is what makes them the choice in liver disease "
            "and the elderly; midazolam is short-acting and parenteral. "
            "Indications: alcohol withdrawal, status epilepticus, "
            "procedural sedation, acute severe anxiety and agitation, "
            "muscle spasm. All short-term. "
            "SE: sedation, anterograde amnesia, falls and fractures, "
            "paradoxical disinhibition, cognitive impairment, and "
            "tolerance and dependence within weeks of daily use. "
            "Note: the harms are almost entirely a function of duration "
            "rather than dose, so the prescribing decision that matters "
            "is the stop date, set at the start. Withdrawal after regular "
            "use causes seizures and delirium and needs a slow taper. "
            "Flumazenil is rarely the right answer in overdose."
        ),
    },
    {
        "name": "NSAIDs",  # 31 notes
        "aliases": ["NSAID", "non-steroidal anti-inflammatory drug",
                    "non-steroidal anti-inflammatories"],
        "category": "pharmacology",
        "summary": (
            "Non-steroidal anti-inflammatory drugs. "
            "MOA: inhibit cyclo-oxygenase, blocking prostaglandin "
            "synthesis. COX-1 is constitutive and maintains gastric "
            "mucosa, renal perfusion and platelet thromboxane; COX-2 is "
            "induced at sites of inflammation. Selectivity for COX-2 "
            "(celecoxib, meloxicam at low dose) spares the stomach and "
            "does not spare the kidney or the cardiovascular system. "
            "Indications: inflammatory pain, gout, dysmenorrhoea, renal "
            "colic, and closure of a patent ductus arteriosus. "
            "SE: the three that matter are gastrointestinal ulceration "
            "and bleeding, acute kidney injury, and cardiovascular "
            "events. Also fluid retention and worsening hypertension and "
            "heart failure, bronchospasm in aspirin-exacerbated "
            "respiratory disease. "
            "Red flags: the triple whammy - an NSAID with an ACE "
            "inhibitor or ARB and a diuretic - removes all three "
            "compensations for renal hypoperfusion at once and is a "
            "leading avoidable cause of AKI in older Australians. Ask "
            "about over-the-counter ibuprofen specifically, because "
            "patients do not report it as a medication. "
            "CI: third trimester, significant renal impairment, active "
            "peptic ulceration, established heart failure."
        ),
    },
    {
        "name": "Diuretics",  # 28 notes
        "aliases": ["diuretic"],
        "category": "pharmacology",
        "summary": (
            "Drugs that increase urinary sodium and water excretion, "
            "classified by where along the nephron they act. "
            "Classification: carbonic anhydrase inhibitors at the "
            "proximal tubule (acetazolamide); loop diuretics blocking "
            "NKCC2 in the thick ascending limb (furosemide), the most "
            "potent; thiazides blocking NCC in the distal convoluted "
            "tubule (hydrochlorothiazide, indapamide), the "
            "antihypertensives; potassium-sparing agents in the "
            "collecting duct, either mineralocorticoid antagonists "
            "(spironolactone) or ENaC blockers (amiloride); and osmotic "
            "agents (mannitol). "
            "Note: the calcium handling splits the two main classes and "
            "is examined constantly - loops WASTE calcium, which is why "
            "they are used in hypercalcaemia, and thiazides RETAIN it, "
            "which is why they help in recurrent calcium stones. "
            "SE: hypokalaemia and metabolic alkalosis with loops and "
            "thiazides, hyperkalaemia with the potassium-sparing agents; "
            "hyponatraemia, worst with thiazides and in older women; "
            "hypovolaemia and prerenal AKI; hyperuricaemia and gout; "
            "hyperglycaemia; ototoxicity with high-dose intravenous "
            "loops. "
            "Monitoring: electrolytes, renal function, daily weight."
        ),
    },
    {
        "name": "Corticosteroids",  # 21 notes
        "aliases": ["corticosteroid", "glucocorticoid", "glucocorticoids",
                    "steroids", "steroid therapy"],
        "category": "pharmacology",
        "summary": (
            "Synthetic analogues of adrenal steroid hormones. "
            "MOA: bind the cytosolic glucocorticoid receptor, which "
            "translocates to the nucleus and suppresses NF-kB driven "
            "transcription of inflammatory cytokines - a genomic effect, "
            "which is why the anti-inflammatory action takes hours and "
            "not minutes. "
            "Classification: by duration and by mineralocorticoid "
            "activity. Hydrocortisone is short-acting with substantial "
            "mineralocorticoid effect, making it the replacement steroid; "
            "prednisolone is intermediate and the oral workhorse; "
            "dexamethasone is long-acting with none, making it the choice "
            "where fluid retention matters or where a cortisol assay must "
            "stay interpretable. 20 mg hydrocortisone is 5 mg "
            "prednisolone is 0.75 mg dexamethasone. "
            "SE: hyperglycaemia, weight gain and Cushingoid change, "
            "hypertension, osteoporosis, avascular necrosis, proximal "
            "myopathy, cataract and glaucoma, skin thinning, insomnia and "
            "psychiatric disturbance, and infection risk including "
            "reactivation of tuberculosis and strongyloides. "
            "Red flags: more than about three weeks of treatment "
            "suppresses the HPA axis, so stopping abruptly or failing to "
            "increase the dose during illness precipitates adrenal "
            "crisis. Every patient on a prolonged course needs sick-day "
            "rules."
        ),
    },
    {
        "name": "Anticoagulants",  # 21 notes
        "aliases": ["anticoagulant", "anticoagulation"],
        "category": "pharmacology",
        "summary": (
            "Drugs that interrupt the coagulation cascade, as distinct "
            "from antiplatelets, which act on primary haemostasis - the "
            "two are not interchangeable, and arterial thrombosis is "
            "largely a platelet problem while venous and cardioembolic "
            "thrombosis is a coagulation problem. "
            "Classification: vitamin K antagonists (warfarin); indirect "
            "antithrombin-dependent parenteral agents (unfractionated "
            "heparin, enoxaparin, fondaparinux); direct oral "
            "anticoagulants, either factor Xa inhibitors (apixaban, "
            "rivaroxaban) or direct thrombin inhibitors (dabigatran). "
            "Note: DOACs are first line in non-valvular AF and in VTE, "
            "needing no routine monitoring and having far fewer dietary "
            "and drug interactions. They are contraindicated in "
            "mechanical valves and in moderate to severe mitral stenosis, "
            "where warfarin remains the only option, and they accumulate "
            "in renal impairment - dabigatran most of all. "
            "SE: bleeding, and the assessment is always net benefit "
            "rather than absolute risk. "
            "Reversal: vitamin K with prothrombin complex concentrate for "
            "warfarin, protamine for heparin, idarucizumab for "
            "dabigatran, andexanet alfa where available for the Xa "
            "inhibitors."
        ),
    },
    {
        "name": "Antidepressants",  # 21 notes
        "aliases": ["antidepressant"],
        "category": "pharmacology",
        "summary": (
            "Drugs acting on monoamine neurotransmission in depression "
            "and anxiety disorders. "
            "Classification: SSRIs (sertraline, escitalopram, fluoxetine) "
            "first line on tolerability; SNRIs (venlafaxine, duloxetine); "
            "the noradrenergic and specific serotonergic agent "
            "mirtazapine, useful where sedation and appetite are wanted; "
            "tricyclics (amitriptyline, nortriptyline), effective but "
            "cardiotoxic in overdose and dangerous where suicide risk is "
            "high; MAOIs, now rarely used and requiring dietary "
            "restriction. "
            "Note: efficacy is broadly comparable across the classes, so "
            "selection is driven by side-effect profile, comorbidity, "
            "interactions and overdose risk. Mood response takes two to "
            "four weeks and full effect six to eight, while side effects "
            "start on day one - which is the single most useful thing to "
            "tell a patient, because it is why they stop. "
            "SE: gastrointestinal upset, sexual dysfunction, "
            "hyponatraemia in the elderly, increased bleeding risk, "
            "weight change, and discontinuation syndrome on abrupt "
            "cessation. "
            "Red flags: review within one to two weeks in patients under "
            "25, in whom suicidal ideation may increase early. Serotonin "
            "syndrome is agitation, clonus, hyperreflexia and "
            "hyperthermia. Antidepressant monotherapy in bipolar "
            "depression can precipitate a manic switch."
        ),
    },
    {
        "name": "Opioids",  # 23 notes
        "aliases": ["opioid", "opiate", "opiates", "narcotic analgesic"],
        "category": "pharmacology",
        "summary": (
            "Agonists at opioid receptors, principally mu. "
            "MOA: presynaptic inhibition of calcium influx and "
            "postsynaptic potassium efflux reduce nociceptive "
            "transmission at the dorsal horn and modulate the descending "
            "pathways; the same mu action in the brainstem depresses "
            "respiratory drive and in the gut slows transit. "
            "Classification: weak (codeine, tramadol), strong (morphine, "
            "oxycodone, hydromorphone, fentanyl), and partial agonists or "
            "mixed agents (buprenorphine). Codeine and tramadol are "
            "prodrugs requiring CYP2D6, so effect varies from none in "
            "poor metabolisers to toxicity in ultrarapid ones. "
            "SE: constipation, which does not develop tolerance and needs "
            "a laxative prescribed alongside from day one; nausea, "
            "sedation, pruritus, urinary retention, and respiratory "
            "depression. Tolerance, dependence and hyperalgesia with "
            "prolonged use. "
            "Renal: morphine's active metabolite accumulates in renal "
            "impairment, causing myoclonus and sedation - use "
            "hydromorphone or fentanyl instead. "
            "Note: dose in oral morphine equivalents when converting, "
            "reduce by 25 to 50% for incomplete cross-tolerance, and "
            "offer take-home naloxone at higher doses."
        ),
    },
    {
        "name": "Statins",  # 14 notes
        "aliases": ["statin", "HMG-CoA reductase inhibitor",
                    "HMG-CoA reductase inhibitors"],
        "category": "pharmacology",
        "summary": (
            "HMG-CoA reductase inhibitors. "
            "MOA: block the rate-limiting step of hepatic cholesterol "
            "synthesis; the resulting fall in intracellular cholesterol "
            "upregulates LDL receptors, which is what actually clears LDL "
            "from plasma. Plaque stabilisation and anti-inflammatory "
            "effects contribute beyond the lipid number. "
            "Indications: secondary prevention after any atherosclerotic "
            "event, where the benefit is large and the argument is "
            "settled; primary prevention based on absolute "
            "cardiovascular risk rather than the cholesterol level "
            "alone; familial hypercholesterolaemia. "
            "SE: myalgia is reported by up to 10% but blinded trials show "
            "most is not attributable to the drug - so a rechallenge or a "
            "switch is usually the right response rather than abandoning "
            "the class. True myositis with a raised CK is uncommon and "
            "rhabdomyolysis rare. Transaminase rise, usually transient; a "
            "small increase in new-onset diabetes that does not offset "
            "the cardiovascular benefit. "
            "Interactions: myopathy risk rises with CYP3A4 inhibitors - "
            "clarithromycin, azole antifungals, amiodarone, diltiazem and "
            "grapefruit - which affects atorvastatin and simvastatin "
            "more than rosuvastatin or pravastatin. "
            "CI: pregnancy and breastfeeding."
        ),
    },
    {
        "name": "Beta blockers",  # 15 notes
        "aliases": ["beta blocker", "beta-blocker", "beta-blockers",
                    "beta adrenergic antagonist"],
        "category": "pharmacology",
        "summary": (
            "Beta adrenoceptor antagonists. "
            "MOA: block beta-1 receptors in the heart, reducing rate, "
            "contractility and AV conduction, and renin release from the "
            "juxtaglomerular apparatus. "
            "Classification: cardioselective for beta-1 (metoprolol, "
            "bisoprolol, atenolol), preferred where airways disease or "
            "diabetes is a concern; non-selective (propranolol, sotalol, "
            "which also has class III activity); and those with "
            "additional alpha blockade (carvedilol, labetalol). "
            "Selectivity is relative and is lost at higher doses. "
            "Indications: HFrEF, where only bisoprolol, carvedilol and "
            "metoprolol succinate have a mortality benefit and the drug "
            "is started low and titrated slowly; rate control in AF; "
            "angina; post-MI; thyrotoxicosis; portal hypertension; "
            "essential tremor; migraine prophylaxis. "
            "SE: bradycardia and heart block, fatigue, cold peripheries, "
            "erectile dysfunction, bronchospasm with non-selective "
            "agents. "
            "Red flags: they mask the adrenergic warning symptoms of "
            "hypoglycaemia. Never start during decompensated heart "
            "failure, and never stop abruptly - rebound tachycardia and "
            "ischaemia follow. Avoid in cocaine toxicity and in "
            "phaeochromocytoma before alpha blockade."
        ),
    },
]
