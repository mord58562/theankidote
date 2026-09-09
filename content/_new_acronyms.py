# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""Acronyms added since the base vocabulary was frozen.

`pearls/_acronyms.py` reads its dictionary out of `library.json`, and
`build_library.py` writes that same dictionary back, so the vocabulary
round-tripped with no way in: conditions, drugs and preclinical terms
each grew a `NEW_*` overlay and acronyms were left without one. Adding
a single acronym meant hand-editing the compiled artefact. This is that
overlay, and like the others it is content, so an addition reaches
installed clients on the next content check.

Shape matches the compiled one: each key maps to a list of candidate
senses, and each sense is

    (expansion, context_keywords, tooltip description)

`context_keywords` is how an acronym with more than one meaning picks
the right sense: `pearls/_acronyms.resolve` scores each candidate
against the surrounding card text and takes the best. An acronym with a
single unambiguous sense can carry a short list, but an ambiguous one
must give each sense enough distinct vocabulary to separate it from its
sibling, or the first candidate wins by default and the popup is wrong
half the time.

Merge rules, enforced in `build_library.collect`:
  * a key absent from the base is added
  * a key already present has its new senses appended, deduplicated on
    expansion, so this file can sharpen an existing acronym without
    restating the sense the base already has
"""

NEW_ACRONYMS: dict = {
    # Written as three letters, these two never underline: the matcher
    # skips surfaces under four characters for case-insensitive terms,
    # so that ordinary words are not lit up. The acronym table is
    # case-sensitive, which is the right home for them.
    #
    # Checked against the collection before adding rather than assumed:
    # every uppercase occurrence of both is the psychotherapy sense,
    # 6 each. "ACT" is deliberately NOT here - it appears in 1,499 notes,
    # almost all of them the ordinary word or the territory, and the
    # "ACT therapy" alias on the full entry covers the safe case.
    "DBT": [
        ("Dialectical Behaviour Therapy",
         ["borderline", "personality", "self-harm", "suicidality",
          "emotion regulation", "distress tolerance", "mindfulness",
          "skills group", "Linehan", "psychotherapy"],
         "Structured cognitive behavioural treatment for chronic "
         "suicidality and self-harm, and the best-evidenced "
         "psychotherapy for borderline personality disorder. Four "
         "skills modules with individual therapy, a skills group and "
         "phone coaching."),
    ],
    # The two commonest of all, and neither fired: 71 and 47 uppercase
    # occurrences in the collection, both unambiguous. Their full-name
    # entries already exist, so this only supplies the route from the
    # abbreviation a card actually writes.
    "CBT": [
        ("Cognitive Behavioural Therapy",
         ["depression", "anxiety", "psychotherapy", "thought", "behaviour",
          "exposure", "insomnia", "first-line", "sessions", "psychological"],
         "Structured, time-limited psychotherapy targeting the "
         "relationship between thoughts, feelings and behaviour. "
         "First-line psychological treatment for depression and for "
         "most anxiety disorders in Australian practice, and "
         "PBS-subsidised under a mental health treatment plan."),
    ],
    "ECT": [
        ("Electroconvulsive Therapy",
         ["depression", "catatonia", "psychosis", "treatment-resistant",
          "anaesthetic", "seizure", "bilateral", "unilateral", "memory",
          "mania"],
         "Induction of a generalised seizure under general anaesthesia. "
         "The most effective acute treatment for severe depression, and "
         "first-line where there is catatonia, food refusal, high "
         "suicide risk or psychotic depression. Main adverse effect is "
         "anterograde and retrograde memory disturbance, usually "
         "transient."),
    ],
    # Three occurrences in the collection, all unambiguous, and it now
    # has a full entry to point at - which it did not when CBT and ECT
    # went in.
    "MBT": [
        ("Mentalisation-Based Therapy",
         ["borderline", "personality", "psychotherapy", "attachment",
          "mentalise", "Bateman", "Fonagy", "DBT", "schema", "group"],
         "Psychodynamically grounded therapy for borderline personality "
         "disorder, aimed at the capacity to hold in mind that behaviour "
         "arises from mental states that can be misread. One of the three "
         "structured psychotherapies named first-line in Australian "
         "practice, alongside DBT and schema therapy."),
    ],
    "IPT": [
        ("Interpersonal Psychotherapy",
         ["depression", "psychotherapy", "grief", "role transition",
          "role dispute", "perinatal", "bulimia", "CBT", "sessions"],
         "Time-limited psychotherapy for depression that works on the "
         "relationships around the illness rather than on cognition. "
         "One of four problem areas - grief, role dispute, role "
         "transition or interpersonal deficits - is agreed at the "
         "outset. As well evidenced as CBT and less often offered."),
    ],

    # "PCR" in an obstetric card is the urine protein:creatinine ratio,
    # not amplification. Both senses are common in this collection, so
    # neither can simply win: 31 notes mean the molecular sense and the
    # pre-eclampsia cards mean the ratio.
    "PCR": [
        ("Polymerase Chain Reaction",
         ["swab", "nucleic acid", "NAAT", "virus", "viral", "chlamydia",
          "gonorrhoea", "tuberculosis", "respiratory", "stool", "CSF",
          "amplification", "DNA", "RNA", "genotype", "culture"],
         "Nucleic acid amplification detecting pathogen DNA or RNA "
         "directly, so it is far more sensitive than culture and works "
         "on organisms that will not grow. It detects nucleic acid "
         "rather than viable organism, so it can stay positive after "
         "treatment has worked."),
        ("Protein:Creatinine Ratio",
         ["proteinuria", "pre-eclampsia", "preeclampsia", "urine",
          "urinary", "mg/mmol", "ACR", "albumin", "nephrotic",
          "antenatal", "gestational", "dipstick"],
         "Spot urine protein indexed to creatinine, which has replaced "
         "the 24-hour collection. In pregnancy 30 mg/mmol or more is "
         "significant proteinuria, and with new hypertension after 20 "
         "weeks it supports a diagnosis of pre-eclampsia."),
    ],

    # ── Collection scan, 2026-09-09 ─────────────────────────────
    # A scan of the live collection (6,088 notes, 2.38 MB of text)
    # found 517 capitalised tokens no vocabulary resolved. These are
    # the 60 worth carrying. The largest group is Australian bodies
    # and schemes, which are frequent here precisely because they are
    # the cards' own citation sources and are the terms a student is
    # least likely to already know in full.


    # ---- Australian institutions, guideline bodies and schemes ----
    # This is the highest-value cluster in the collection: these are its
    # citation sources, they appear in the "source:" line of card after
    # card, and a student reads past them without ever learning which
    # body is which. PBS alone is 319 occurrences.
    "PBS": [
        ("Pharmaceutical Benefits Scheme",
         ["listed", "subsidy", "subsidised", "restricted", "authority",
          "streamlined", "schedule", "script", "prescribing", "criteria",
          "co-payment", "TGA", "s85", "medicine"],
         "The Commonwealth scheme that subsidises prescription medicines "
         "in Australia. A drug can be TGA-registered and still not "
         "PBS-listed, and a PBS restriction sets who may be prescribed it "
         "at the subsidised price."),
    ],
    "MBS": [
        ("Medicare Benefits Schedule",
         ["item", "rebate", "rebated", "funded", "Medicare", "bulk-bill",
          "referral", "billing", "eligible", "out-of-pocket", "MSAC"],
         "The list of medical services attracting a Medicare rebate, each "
         "with an item number. Whether an investigation is MBS-rebated "
         "often decides the Australian diagnostic pathway more than the "
         "evidence does."),
    ],
    # 229 occurrences, and every one is the Melbourne hospital's guideline
    # set rather than any other Royal Children's. Naming the city matters
    # because the cards cite it as "RCH Melbourne CPG".
    "RCH": [
        ("The Royal Children's Hospital Melbourne",
         ["CPG", "paediatric", "children", "child", "infant", "guideline",
          "Melbourne", "bronchiolitis", "sepsis", "dosing", "neonate"],
         "Melbourne quaternary paediatric hospital whose Clinical Practice "
         "Guidelines are the most widely used paediatric reference in "
         "Australian practice, well beyond Victoria."),
    ],
    "CPG": [
        ("Clinical Practice Guideline",
         ["guideline", "RCH", "RANZCP", "recommendation", "source",
          "evidence", "consensus", "college", "position", "statement"],
         "A formal, evidence-graded recommendation set issued by a college "
         "or health service. Cited constantly in this collection as the "
         "source line for management steps."),
    ],
    "NSW": [
        ("New South Wales",
         ["Health", "Act", "state", "notifiable", "policy", "directive",
          "CEC", "Ambulance", "public health unit", "jurisdiction",
          "Sydney", "legislation"],
         "The state whose law and health policy govern this collection. "
         "State-specific material here should be read as NSW unless the "
         "card says otherwise."),
    ],
    "RACGP": [
        ("Royal Australian College of General Practitioners",
         ["general practice", "GP", "preventive", "Red Book", "primary care",
          "guideline", "deprescribing", "screening", "HANDI", "college"],
         "The college for Australian general practice. Publishes the Red "
         "Book on preventive activities and much of the primary care "
         "guidance cited here."),
    ],
    "RANZCP": [
        ("Royal Australian and New Zealand College of Psychiatrists",
         ["psychiatry", "psychiatrist", "mood", "schizophrenia", "bipolar",
          "clinical practice guideline", "college", "fellowship",
          "perinatal", "antipsychotic", "lithium"],
         "The binational psychiatry college. Its clinical practice "
         "guidelines for mood disorders and for schizophrenia are the "
         "primary Australian psychiatric references in this collection."),
    ],
    "NHMRC": [
        ("National Health and Medical Research Council",
         ["guideline", "approved", "evidence", "alcohol", "infant feeding",
          "national", "research", "funding", "statement", "standard drinks"],
         "Australia's peak body for health and medical research and the "
         "national approver of clinical guidelines. NHMRC approval is what "
         "makes a guideline the Australian standard."),
    ],
    "ADIPS": [
        ("Australasian Diabetes in Pregnancy Society",
         ["GDM", "gestational diabetes", "OGTT", "pregnancy", "metformin",
          "insulin", "fasting", "glucose", "antenatal", "RANZCOG"],
         "Sets the Australian gestational diabetes diagnostic thresholds "
         "and pregnancy glycaemic targets. The 75 g OGTT cut-offs used in "
         "Australia are the ADIPS ones."),
    ],
    "SOMANZ": [
        ("Society of Obstetric Medicine of Australia and New Zealand",
         ["hypertension in pregnancy", "pre-eclampsia", "preeclampsia",
          "severe HTN", "blood pressure", "aspirin", "obstetric medicine",
          "guideline", "antenatal", "postpartum"],
         "Publishes the Australian guideline on hypertensive disorders of "
         "pregnancy, which is the source of the local pre-eclampsia "
         "definitions and blood pressure thresholds."),
    ],
    "CSANZ": [
        ("Cardiac Society of Australia and New Zealand",
         ["cardiology", "atrial fibrillation", "AF", "NHFA", "heart failure",
          "genetic testing", "inherited", "guideline", "anticoagulation",
          "arrhythmia"],
         "The binational cardiology society. Writes the Australian atrial "
         "fibrillation and heart failure guidelines jointly with the Heart "
         "Foundation."),
    ],
    "ASHM": [
        ("Australasian Society for HIV, Viral Hepatitis and Sexual Health "
         "Medicine",
         ["HIV", "hepatitis", "HCV", "HBV", "chlamydia", "gonorrhoea",
          "STI", "ART", "doxycycline", "sexual health", "PrEP"],
         "The Australian authority on HIV, viral hepatitis and sexual "
         "health management. Its STI treatment recommendations are what "
         "Australian practice follows."),
    ],
    "AIHW": [
        ("Australian Institute of Health and Welfare",
         ["statistics", "incidence", "prevalence", "mortality", "burden",
          "data", "report", "mothers and babies", "cancer", "national"],
         "The national health statistics agency. Any epidemiological figure "
         "quoted for Australia in this collection traces back to an AIHW "
         "release."),
    ],
    "COPE": [
        ("Centre of Perinatal Excellence",
         ["perinatal", "EPDS", "postnatal", "antenatal", "depression",
          "screening", "mental health", "pregnancy", "puerperal",
          "NHMRC-approved"],
         "Australian body behind the NHMRC-approved perinatal mental health "
         "guideline, including universal EPDS screening at booking and "
         "postpartum."),
    ],
    "NBA": [
        ("National Blood Authority",
         ["anti-D", "Rh D", "immunoglobulin", "blood product", "transfusion",
          "funded", "625 IU", "250 IU", "obstetric", "consent"],
         "The Commonwealth agency managing the national blood supply. Its "
         "anti-D immunoglobulin guidance sets the Australian doses and the "
         "sensitising events that trigger them."),
    ],
    # 32 occurrences and every one is the diabetes society: DKA position
    # statements, T1DM guidelines, periprocedural SGLT2i advice. Nothing
    # here is an alcohol and drug service, so this stays a single sense.
    "ADS": [
        ("Australian Diabetes Society",
         ["diabetes", "DKA", "ketoacidosis", "SGLT2i", "euglycaemic",
          "insulin", "T1DM", "glucose", "ADEA", "position statement",
          "periprocedural"],
         "The Australian professional body for diabetes medicine. Source of "
         "the local DKA protocols and the withhold-SGLT2i-before-surgery "
         "advice."),
    ],
    "ANZCOR": [
        ("Australian and New Zealand Committee on Resuscitation",
         ["resuscitation", "ALS", "BLS", "defibrillation", "arrest",
          "adrenaline", "guideline 11", "CPR", "biphasic", "algorithm"],
         "Writes the Australian resuscitation guidelines. Its numbered "
         "guidelines, not the American ones, set local adult and paediatric "
         "arrest algorithms."),
    ],
    "NHFA": [
        ("National Heart Foundation of Australia",
         ["heart", "cardiovascular", "CVD risk", "blood pressure", "AF",
          "CSANZ", "guideline", "CHA2DS2-VA", "cholesterol", "prevention"],
         "The Australian cardiovascular charity and guideline body, "
         "co-author with CSANZ of the local atrial fibrillation and heart "
         "failure guidelines."),
    ],
    "CEC": [
        ("Clinical Excellence Commission",
         ["sepsis", "SEPSIS KILLS", "NSW", "pathway", "deteriorating",
          "between the flags", "safety", "quality", "escalation", "bundle"],
         "The NSW Health patient safety agency. Its SEPSIS KILLS pathway is "
         "the sepsis recognition and escalation standard in NSW hospitals."),
    ],
    "TSANZ": [
        ("Thoracic Society of Australia and New Zealand",
         ["respiratory", "lung", "cough", "cystic fibrosis", "asthma",
          "spirometry", "position statement", "bronchiectasis", "oxygen",
          "sleep"],
         "The binational respiratory medicine society. Its position "
         "statements set Australian practice on chronic cough, "
         "bronchiectasis and cystic fibrosis care."),
    ],
    "RCPA": [
        ("Royal College of Pathologists of Australasia",
         ["reference interval", "harmonised", "manual", "pathology",
          "genetic testing", "laboratory", "assay", "cut-off", "specimen",
          "HFE"],
         "The pathology college. Its Manual and harmonised reference "
         "intervals are why Australian laboratory cut-offs differ from "
         "textbook American ones."),
    ],
    "KHA": [
        ("Kidney Health Australia",
         ["CKD", "eGFR", "ACR", "albuminuria", "nephrology", "CARI",
          "dialysis", "renal", "screening", "referral", "proteinuria"],
         "The Australian kidney charity and guideline body. Its KHA-CARI "
         "guidelines and CKD colour chart set local screening intervals and "
         "nephrology referral thresholds."),
    ],
    # Every one of the 23 occurrences is the Mental Health Act, and all
    # but one names the NSW instrument explicitly (the exception pairs
    # NSW MHA 2007 with Vic MHA 2014 to make the point that section
    # numbering differs by state). Written NSW-first for that reason.
    "MHA": [
        ("Mental Health Act",
         ["schedule", "involuntary", "s19", "s14", "mentally ill",
          "mentally disordered", "detention", "tribunal", "MHRT", "ECT",
          "NSW", "2007", "inquiry"],
         "In NSW the Mental Health Act 2007. Defines the 'mentally ill' and "
         "'mentally disordered' persons, the scheduling powers and the "
         "involuntary treatment framework. Section numbering differs "
         "between states, so a section reference is only meaningful with "
         "the jurisdiction attached."),
    ],
    "CPMS": [
        ("Clozapine Patient Monitoring Service",
         ["clozapine", "FBC", "neutropenia", "agranulocytosis", "weekly",
          "18 weeks", "registration", "monitoring", "ClopineCentral",
          "dispensing", "treatment-resistant"],
         "The mandatory registration and haematological monitoring service "
         "for clozapine in Australia. Weekly full blood count for 18 weeks, "
         "then monthly for the life of the treatment."),
    ],

    # ---- Dosing frequency and unit shorthand ----
    # 122 occurrences, and the collection makes a point of it: "AU dose
    # unit is IU (not UI)". Worth an entry for that alone.
    "IU": [
        ("International Units",
         ["anti-D", "625", "250", "bHCG", "dose", "vitamin", "FSH",
          "calcitonin", "IU/L", "units", "potency"],
         "A potency-based unit used where mass does not describe biological "
         "activity. Anti-D and bHCG are both reported this way in "
         "Australian practice."),
    ],
    "BD": [
        ("Twice Daily",
         ["mg", "PO", "IV", "dose", "dosing", "days", "daily", "doxycycline",
          "regimen", "12-hourly", "b.d."],
         "From bis die. Twice a day, conventionally 12-hourly. The standard "
         "Australian prescribing abbreviation."),
    ],
    "TDS": [
        ("Three Times Daily",
         ["mg", "PO", "IV", "dose", "dosing", "days", "8-hourly",
          "amoxicillin", "regimen", "thiamine", "t.d.s."],
         "From ter die sumendus. Three times a day, roughly 8-hourly. "
         "Written TDS in Australia where American sources write TID."),
    ],
    "QID": [
        ("Four Times Daily",
         ["mg", "PO", "IV", "dose", "dosing", "days", "6-hourly",
          "cefalexin", "regimen", "tranexamic", "q.i.d."],
         "From quater in die. Four times a day, roughly 6-hourly."),
    ],

    # ---- Examination, investigation and obstetric shorthand ----
    "WOB": [
        ("Work of Breathing",
         ["increased", "accessory", "recession", "tachypnoea", "asthma",
          "bronchiolitis", "respiratory", "grunting", "distress", "infant",
          "wheeze"],
         "The visible effort of breathing: accessory muscle use, recession, "
         "tracheal tug, grunting and nasal flaring. Increased work of "
         "breathing is the core paediatric respiratory severity sign."),
    ],
    "MSU": [
        ("Mid-Stream Urine",
         ["urine", "UTI", "culture", "CFU", "clean-catch", "bacteriuria",
          "dipstick", "specimen", "urinary", "asymptomatic", "sample"],
         "Clean-catch urine collected after the first stream has washed the "
         "urethra, sent for microscopy and culture. A single pure growth at "
         "or above 10^8 CFU/L is diagnostic in a symptomatic non-pregnant "
         "patient."),
    ],
    "TVUS": [
        ("Transvaginal Ultrasound",
         ["endometrial", "ovarian", "cervical length", "adnexal", "cyst",
          "gynaecology", "postmenopausal bleeding", "thickness", "uterus",
          "pelvic", "imaging"],
         "The first-line pelvic imaging modality in gynaecology, giving far "
         "better resolution of the endometrium and adnexa than a "
         "transabdominal scan."),
    ],
    "TVS": [
        ("Transvaginal Scan",
         ["bHCG", "ectopic", "intrauterine", "IUP", "discriminatory zone",
          "gestational sac", "placenta", "praevia", "early pregnancy",
          "3500"],
         "The same study as TVUS, written this way in the early pregnancy "
         "cards. Above the discriminatory bHCG of 3500 IU/L, an empty "
         "uterus on TVS is diagnostic of ectopic pregnancy."),
    ],
    "FHR": [
        ("Fetal Heart Rate",
         ["CTG", "accelerations", "decelerations", "variability", "NST",
          "cardiotocograph", "auscultate", "reactive", "baseline",
          "ectopic", "intrapartum"],
         "The core fetal wellbeing measure, assessed by intermittent "
         "auscultation or continuous CTG. Absence of an FHR is also part of "
         "the criteria for medical management of ectopic pregnancy."),
    ],
    "WCC": [
        ("White Cell Count",
         ["FBC", "neutrophils", "leucocytosis", "neutropenia", "CSF",
          "anaemia", "platelets", "infection", "bloods", "differential",
          "raised"],
         "Total leucocyte count on the full blood count, and separately the "
         "cell count on a CSF sample. Australian cards write WCC where "
         "American ones write WBC."),
    ],
    "IUP": [
        ("Intrauterine Pregnancy",
         ["ectopic", "bHCG", "TVS", "discriminatory", "gestational sac",
          "viable", "3500", "early pregnancy", "location", "yolk sac"],
         "A pregnancy sited within the uterine cavity. Confirming or "
         "excluding a viable IUP is the pivot of every early pregnancy "
         "assessment."),
    ],
    "IUS": [
        ("Intrauterine System",
         ["LNG", "Mirena", "levonorgestrel", "contraception", "HMB",
          "heavy menstrual bleeding", "hyperplasia", "endometrial",
          "progestogen", "device", "PBS"],
         "A progestogen-releasing intrauterine device. The "
         "levonorgestrel-releasing IUS is first-line for heavy menstrual "
         "bleeding without structural cause and for endometrial hyperplasia "
         "without atypia."),
    ],
    "CD4": [
        ("CD4+ T Lymphocyte Count",
         ["HIV", "AIDS", "opportunistic", "prophylaxis", "PJP", "toxoplasma",
          "viral load", "ART", "cells", "immunosuppression", "200"],
         "The helper T cell count that stages HIV immunosuppression and "
         "triggers opportunistic infection prophylaxis. Australian practice "
         "now starts antiretrovirals regardless of CD4."),
    ],
    # Two senses, and they are far apart: 19 occurrences are almost all
    # the team, but the leprosy cards use the WHO regimen sense and would
    # otherwise get a popup about heart teams and tertiary centres.
    "MDT": [
        ("Multidisciplinary Team",
         ["team", "meeting", "referral", "tertiary", "heart team",
          "discussion", "centre", "physiotherapist", "dietitian",
          "specialist", "care"],
         "The standing group of clinicians from different disciplines that "
         "makes management decisions jointly. Australian care for cancer, "
         "cystic fibrosis and complex obstetrics is organised around it."),
        ("Multi-Drug Therapy",
         ["leprosy", "WHO", "paucibacillary", "multibacillary", "dapsone",
          "rifampicin", "clofazimine", "regimen", "free-of-charge",
          "Hansen"],
         "The WHO combination regimen for leprosy, supplied free of charge "
         "and given as paucibacillary or multibacillary courses."),
    ],
    "TXA": [
        ("Tranexamic Acid",
         ["PPH", "bleeding", "haemorrhage", "menorrhagia", "HMB", "1 g",
          "antifibrinolytic", "epistaxis", "WOMAN trial", "haematuria",
          "trauma"],
         "An antifibrinolytic that blocks plasminogen binding to fibrin. "
         "Give 1 g IV within 3 hours of postpartum haemorrhage onset; "
         "avoid in haematuria because of clot retention."),
    ],
    "MTX": [
        ("Methotrexate",
         ["ectopic", "DMARD", "rheumatoid", "weekly", "steroid-sparing",
          "folate", "AZA", "csDMARD", "psoriasis", "teratogenic",
          "50 mg/m2"],
         "A dihydrofolate reductase inhibitor used weekly as the anchor "
         "csDMARD in rheumatoid arthritis and as a single dose for medical "
         "management of unruptured ectopic pregnancy. Never dose daily."),
    ],
    "CN": [
        ("Cranial Nerve",
         ["palsy", "III", "VI", "VII", "nerve", "ophthalmoplegia",
          "cavernous sinus", "ptosis", "diplopia", "V1", "V2", "brainstem"],
         "One of the twelve paired nerves arising from the brain, "
         "conventionally numbered in Roman numerals. CN III, VI and VII "
         "palsies carry the most localising value."),
    ],
    "DC": [
        ("Direct Current",
         ["cardioversion", "shock", "synchronised", "defibrillation",
          "biphasic", "joules", "4 J/kg", "unstable", "VT", "AF", "arrest"],
         "Direct current cardioversion or defibrillation. Synchronised for "
         "an unstable tachyarrhythmia with a pulse, unsynchronised for "
         "pulseless VT and VF."),
    ],
    "IAP": [
        ("Intrapartum Antibiotic Prophylaxis",
         ["GBS", "group B", "benzylpenicillin", "labour", "membranes",
          "35-37", "neonatal sepsis", "3 g IV", "screening", "risk-based",
          "delivery"],
         "Antibiotic given in labour to prevent early-onset neonatal group "
         "B streptococcal sepsis. The Australian regimen is "
         "benzylpenicillin 3 g IV loading then 1.8 g 4-hourly until birth."),
    ],
    "HFE": [
        ("Homeostatic Iron Regulator Gene",
         ["haemochromatosis", "C282Y", "H63D", "genotype", "iron",
          "ferritin", "transferrin saturation", "chromosome 6",
          "homozygous", "venesection", "genetic testing"],
         "The gene on chromosome 6 whose C282Y and H63D variants cause "
         "hereditary haemochromatosis. HFE genotyping has superseded liver "
         "biopsy for Australian diagnosis."),
    ],
    "CFTR": [
        ("Cystic Fibrosis Transmembrane Conductance Regulator",
         ["cystic fibrosis", "CF", "modulator", "elexacaftor", "Trikafta",
          "F508del", "variant", "chloride", "sweat", "newborn screening",
          "IRT"],
         "The chloride channel whose loss of function causes cystic "
         "fibrosis. CFTR modulators are PBS-listed in Australia for "
         "patients aged 2 years and over with a responsive variant."),
    ],
    "HLA": [
        ("Human Leukocyte Antigen",
         ["B27", "DR3", "DR4", "DQ2", "association", "autoimmune",
          "ankylosing", "spondyloarthritis", "coeliac", "typing",
          "susceptibility", "allele"],
         "The human major histocompatibility complex. Specific alleles "
         "carry disease association rather than diagnostic weight: HLA-B27 "
         "supports axial spondyloarthritis but does not confirm it."),
    ],
    "LNG": [
        ("Levonorgestrel",
         ["IUS", "Mirena", "emergency contraception", "1.5 mg", "72 hours",
          "progestogen", "IUD", "UPA", "OTC", "contraception", "HMB"],
         "A second-generation progestogen. Used as 1.5 mg oral emergency "
         "contraception up to 72 hours, and as the hormone in the "
         "levonorgestrel intrauterine system."),
    ],
    "UPA": [
        ("Ulipristal Acetate",
         ["emergency contraception", "EllaOne", "30 mg", "120 hours",
          "Schedule 3", "S3", "progesterone receptor modulator", "UPSI",
          "LNG", "pharmacist"],
         "A selective progesterone receptor modulator used as 30 mg "
         "emergency contraception up to 120 hours after intercourse. "
         "Schedule 3 in Australia, and hormonal contraception must be "
         "delayed 5 days after it."),
    ],
    # The brief expected "polycystic ovary morphology syndrome". The
    # collection does not say that anywhere: all 53 occurrences expand
    # PMOS as Polyendocrine Metabolic Ovarian Syndrome, unanimously and
    # in 10 separately worded notes. Written to match the collection.
    # PCOS itself already resolves in the base vocabulary, so only the
    # new name needs an entry.
    "PMOS": [
        ("Polyendocrine Metabolic Ovarian Syndrome",
         ["PCOS", "renamed", "anovulation", "letrozole", "hyperandrogenism",
          "oligomenorrhoea", "OGTT", "insulin resistance", "RANZCOG",
          "Rotterdam", "ovulation induction"],
         "The renaming of polycystic ovary syndrome adopted in 2026 and "
         "welcomed by RANZCOG. Same condition and same criteria; the new "
         "name drops the misleading morphological emphasis. Letrozole is "
         "first-line for anovulation."),
    ],

    # ---- Tokens with more than one live sense in this collection ----
    # 25 occurrences, all pneumonia: severity-stratified eTG regimens,
    # SMART-COP, tropical melioidosis cover. No RANZCP assessment sense
    # and no capsule sense appears, so this stays single.
    "CAP": [
        ("Community-Acquired Pneumonia",
         ["pneumonia", "SMART-COP", "CORB", "CURB-65", "amoxicillin",
          "doxycycline", "ceftriaxone", "azithromycin", "severity",
          "benzylpenicillin", "HAP", "eTG"],
         "Pneumonia acquired outside hospital. Australian therapy is chosen "
         "by severity score, with amoxicillin for mild disease and "
         "benzylpenicillin plus doxycycline for moderate, adding "
         "melioidosis cover in the northern wet season."),
    ],
    # 25 occurrences and every one is the operation. No Cushing syndrome
    # or caesarean-scar sense appears in isolation, so a single entry is
    # safe here.
    "CS": [
        ("Caesarean Section",
         ["VBAC", "praevia", "accreta", "elective", "emergency", "delivery",
          "lower-segment", "uterine rupture", "breech", "37 weeks",
          "obstetric", "classical"],
         "Operative abdominal delivery. Elective timing in Australia is "
         "39+0 weeks for an uncomplicated repeat, earlier for praevia or "
         "placenta accreta spectrum."),
    ],
    "GAS": [
        ("Group A Streptococcus",
         ["Streptococcus pyogenes", "pharyngitis", "ARF", "rheumatic fever",
          "impetigo", "scarlet fever", "ASO", "anti-DNase B", "throat swab",
          "benzathine", "toxic shock"],
         "Streptococcus pyogenes. Evidence of preceding GAS infection is "
         "required to diagnose a first episode of acute rheumatic fever, by "
         "throat culture or by rising ASO or anti-DNase B titres."),
    ],
    "CF": [
        ("Cystic Fibrosis",
         ["CFTR", "sweat chloride", "newborn screening", "IRT", "Trikafta",
          "modulator", "pancreatic", "Creon", "bronchiectasis", "F508del",
          "CBAVD", "centre"],
         "Autosomal recessive CFTR channel disease. On the Australian "
         "newborn bloodspot panel in every state and territory, screened by "
         "IRT then a CFTR variant panel and confirmed on sweat chloride."),
    ],
    "HF": [
        ("Heart Failure",
         ["HFrEF", "HFpEF", "ejection fraction", "decompensated",
          "congestive", "SGLT2i", "NHFA", "digoxin", "hospitalisation",
          "cardiomegaly", "diuretic"],
         "Failure of cardiac output to meet demand at normal filling "
         "pressures. Australian cut-offs split HFrEF at 40 per cent or less "
         "from HFpEF at 50 per cent or more."),
    ],
    # Two senses that share almost no vocabulary: the myeloproliferative
    # neoplasm and the vaginal route. 18 occurrences, split roughly
    # evenly, so neither can be allowed to win by position alone.
    "PV": [
        ("Polycythaemia Vera",
         ["JAK2", "V617F", "venesection", "haematocrit", "HCT",
          "erythropoietin", "hydroxyurea", "myeloproliferative",
          "ruxolitinib", "thrombosis", "aspirin"],
         "A JAK2-driven myeloproliferative neoplasm with autonomous red "
         "cell production and a low erythropoietin. Managed by venesection "
         "to a haematocrit under 0.45 plus low-dose aspirin."),
        ("Per Vaginam",
         ["misoprostol", "pessary", "clindamycin cream", "bleeding",
          "route", "nocte", "vaginal", "examination", "800 microgram",
          "speculum", "discharge"],
         "By the vaginal route, or on vaginal examination. Written on a "
         "drug order it is the route, as in misoprostol 800 microgram PV."),
    ],
    # 17 occurrences across two unrelated senses, plus 2 that are the
    # first half of NT-proBNP rather than a token in their own right.
    # Both real senses are kept because the obstetric one is common and
    # the geographic one carries the tropical infection and vaccine
    # schedule material.
    "NT": [
        ("Nuchal Translucency",
         ["CFTS", "combined first trimester", "11+0", "13+6", "PAPP-A",
          "bHCG", "3.5 mm", "screening", "aneuploidy", "ultrasound",
          "dating scan"],
         "The subcutaneous fluid space at the fetal neck, measured between "
         "11+0 and 13+6 weeks as part of combined first trimester "
         "screening. A measurement above 3.5 mm prompts diagnostic testing "
         "regardless of the combined risk."),
        ("Northern Territory",
         ["remote", "tropical", "wet season", "melioidosis", "QLD", "WA",
          "SA", "hepatitis A", "immunisation schedule", "jurisdiction",
          "APY", "state"],
         "The jurisdiction whose remote and tropical epidemiology drives "
         "several Australian schedule variations, including additional "
         "hepatitis A vaccination and empirical melioidosis cover."),
    ],
    # 28 occurrences. The imaging sense is the larger, but the obstetric
    # cards use PET for pre-eclampsia and one of them spells it out as
    # "PET (Pre-eclampsia)". Splitting on pregnancy vocabulary separates
    # them cleanly.
    "PET": [
        ("Positron Emission Tomography",
         ["staging", "PET-CT", "FDG", "metastases", "NSCLC", "lymphoma",
          "nodes", "MBS-funded", "amyloid", "DOTATATE", "uptake",
          "endocarditis"],
         "Functional imaging using a radiolabelled tracer, usually "
         "18F-FDG, combined with CT for anatomical localisation. The "
         "standard Australian staging study for most solid tumours and "
         "lymphoma."),
        ("Pre-Eclampsia Toxaemia",
         ["pregnancy", "proteinuria", "IUGR", "FGR", "20 weeks",
          "hypertension", "antenatal", "GDM", "obstetric", "aspirin",
          "growth scan"],
         "An older obstetric shorthand for pre-eclampsia, still written on "
         "Australian antenatal cards and referral forms. New hypertension "
         "after 20 weeks with end-organ involvement."),
    ],
    # 27 occurrences and two clearly separated senses: rupture of
    # membranes throughout the obstetric cards, range of motion in the
    # musculoskeletal ones. Obstetric first because it is the larger.
    "ROM": [
        ("Rupture of Membranes",
         ["PROM", "PPROM", "labour", "amniorrhexis", "GBS", "18 hours",
          "chorioamnionitis", "liquor", "induction", "preterm", "speculum",
          "artificial"],
         "Breach of the amniotic membranes. Membranes ruptured for 18 hours "
         "or more is an indication for intrapartum antibiotic prophylaxis, "
         "and induction is offered within 24 hours of term prelabour "
         "rupture."),
        ("Range of Motion",
         ["joint", "restricted", "septic arthritis", "reduced", "passive",
          "active", "weight-bear", "physiotherapy", "contracture", "hip",
          "shoulder"],
         "The arc through which a joint moves. Restricted range with an "
         "inability to weight-bear is a Kocher criterion for septic "
         "arthritis."),
    ],
    # 34 occurrences and genuinely two things: the ECG interval and the
    # rectal route. The ECG cards are the majority, but misoprostol 800
    # microgram PR would get a popup about Mobitz I without a split.
    "PR": [
        ("PR Interval",
         ["ECG", "AV block", "Mobitz", "Wenckebach", "prolonged",
          "200 ms", "delta wave", "depression", "pericarditis", "P wave",
          "first degree", "short"],
         "The ECG interval from the start of the P wave to the start of the "
         "QRS, measuring atrioventricular conduction. Over 200 ms is first "
         "degree block; progressive lengthening before a dropped beat is "
         "Mobitz I."),
        ("Per Rectum",
         ["misoprostol", "rectal", "route", "examination", "bleeding",
          "800 mcg", "suppository", "empty rectum", "digital", "PPH",
          "indomethacin"],
         "By the rectal route, or on rectal examination. On a drug order it "
         "is the route, as in misoprostol 800 microgram PR for postpartum "
         "haemorrhage."),
    ],
    # 23 occurrences. The urine ratio dominates, but the rheumatology
    # cards cite EULAR/ACR classification criteria and the gout and lupus
    # cards would otherwise get a nephrology popup.
    "ACR": [
        ("Albumin:Creatinine Ratio",
         ["urine", "urinary", "albuminuria", "mg/mmol", "CKD", "eGFR",
          "nephropathy", "ACEi", "ARB", "SGLT2i", "proteinuria",
          "screening", "KHA"],
         "Spot urine albumin indexed to creatinine, the Australian measure "
         "of albuminuria. Referral to nephrology is prompted at 30 mg/mmol "
         "or more, and SGLT2 inhibitors are PBS-listed for chronic kidney "
         "disease from 25 mg/mmol."),
        ("American College of Rheumatology",
         ["EULAR", "classification criteria", "SLE", "gout", "rheumatoid",
          "2019", "1997", "rheumatology", "society", "guideline",
          "flare"],
         "The American rheumatology body, whose classification criteria are "
         "usually cited jointly with EULAR. Classification criteria are "
         "built for research cohorts and are not diagnostic criteria."),
    ],
}
