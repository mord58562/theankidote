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
}
