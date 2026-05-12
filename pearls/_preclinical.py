# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
"""Preclinical / basic-medical-science term library.

Standalone, fully free. No UpToDate dependency. Source references are
free-tier educational sites (Deranged Physiology and similar) - all
summaries are reworded in plain language.
"""

PRECLINICAL_TERMS = [
    # ───────────────────────── PHYSIOLOGY: CARDIAC ─────────────────────────
    {
        "name": "Frank-Starling law",
        "aliases": ["Frank Starling mechanism", "Starling's law of the heart", "Frank-Starling mechanism"],
        "category": "physiology",
        "summary": "Stroke volume increases with end-diastolic volume up to a physiological limit. Mechanism: greater sarcomere stretch produces more optimal actin-myosin overlap, so each contraction is stronger. The curve plateaus and falls in heart failure (descending limb), which is why preload reduction relieves congestive symptoms.",
    },
    {
        "name": "Stroke volume",
        "aliases": ["SV"],
        "category": "physiology",
        "summary": "Volume of blood ejected by the left ventricle per beat, normally about 70 mL at rest. Determined by preload, afterload, and contractility. Cardiac output equals stroke volume times heart rate.",
    },
    {
        "name": "Cardiac output",
        "aliases": ["CO"],
        "category": "physiology",
        "summary": "Volume of blood the heart pumps per minute, normally 4 to 8 L/min at rest. Equal to stroke volume times heart rate. Cardiac index normalises this to body surface area (normal 2.5 to 4 L/min/m^2).",
    },
    {
        "name": "Ejection fraction",
        "aliases": ["EF", "LVEF"],
        "category": "physiology",
        "summary": "Fraction of end-diastolic volume ejected with each beat, normally 55 to 70 percent. HFrEF is defined as EF below 40 percent, HFmrEF 40 to 49, HFpEF 50 or above. Reflects contractility rather than overall cardiac output.",
    },
    {
        "name": "Preload",
        "aliases": [],
        "category": "physiology",
        "summary": "Ventricular wall tension at end-diastole, clinically approximated by end-diastolic volume or pressure. Determined by venous return and ventricular compliance. Reduced by venodilators, diuretics, and bleeding.",
    },
    {
        "name": "Afterload",
        "aliases": [],
        "category": "physiology",
        "summary": "Resistance the ventricle must overcome to eject blood, clinically approximated by systemic vascular resistance (or aortic pressure for the left ventricle). Increased by hypertension and aortic stenosis. Reduced by arterial vasodilators.",
    },
    {
        "name": "Contractility",
        "aliases": ["Inotropy"],
        "category": "physiology",
        "summary": "Intrinsic force of myocardial contraction independent of preload and afterload. Increased by sympathetic stimulation, beta-1 agonists, calcium, and digoxin. Decreased by beta-blockers, acidosis, hypoxia, and ischaemia.",
    },
    {
        "name": "Cardiac action potential",
        "aliases": [],
        "category": "physiology",
        "summary": "Ventricular myocyte action potential has five phases: phase 0 fast Na+ in, phase 1 transient K+ out, phase 2 plateau (Ca2+ in balanced by K+ out), phase 3 repolarisation (K+ out), phase 4 resting. Pacemaker cells lack a true phase 0 from Na+; depolarisation is driven by funny current (If) and Ca2+ influx.",
    },
    {
        "name": "Pacemaker funny current",
        "aliases": ["If current", "I_f"],
        "category": "physiology",
        "summary": "HCN-channel-mediated mixed Na+/K+ inward current active during diastolic depolarisation in SA and AV nodal cells. Sets the rate of spontaneous firing and is the target of ivabradine, which slows heart rate without affecting contractility.",
    },
    {
        "name": "Excitation-contraction coupling",
        "aliases": ["ECC"],
        "category": "physiology",
        "summary": "Process linking myocyte depolarisation to contraction. Action potential opens L-type Ca2+ channels, the small Ca2+ influx triggers a larger release from the sarcoplasmic reticulum via ryanodine receptors (calcium-induced calcium release), and Ca2+ binds troponin C to enable cross-bridge cycling.",
    },
    {
        "name": "Wiggers diagram",
        "aliases": [],
        "category": "physiology",
        "summary": "Composite graph aligning aortic, ventricular, and atrial pressures with ventricular volume, ECG, and heart sounds across one cardiac cycle. Used to teach valve timing: S1 at mitral closure (onset of systole), S2 at aortic closure (onset of diastole).",
    },
    {
        "name": "Pressure-volume loop",
        "aliases": ["PV loop"],
        "category": "physiology",
        "summary": "Plot of ventricular pressure against volume across one cycle, forming a rectangle-like loop. Width represents stroke volume. The end-systolic pressure-volume relationship slope is a load-independent index of contractility.",
    },
    {
        "name": "Mean arterial pressure",
        "aliases": ["MAP"],
        "category": "physiology",
        "summary": "Average arterial pressure across the cardiac cycle, approximated by diastolic plus one-third pulse pressure. Drives organ perfusion; target above 65 mmHg in shock to maintain end-organ blood flow.",
    },
    {
        "name": "Pulse pressure",
        "aliases": [],
        "category": "physiology",
        "summary": "Difference between systolic and diastolic blood pressures, normally 30 to 50 mmHg. Widened in aortic regurgitation, high-output states, and stiff arteries; narrowed in cardiac tamponade and severe aortic stenosis.",
    },
    {
        "name": "Baroreceptor reflex",
        "aliases": ["Baroreflex"],
        "category": "physiology",
        "summary": "Negative feedback loop that buffers acute blood pressure changes. Carotid sinus and aortic arch stretch receptors signal via CN IX and X to the nucleus tractus solitarius; rising BP triggers vagal slowing and sympathetic withdrawal. Resets over days and so does not correct chronic hypertension.",
    },
    {
        "name": "Bainbridge reflex",
        "aliases": ["Atrial reflex"],
        "category": "physiology",
        "summary": "Heart rate increases when atrial stretch receptors detect rising venous return. Mediated via vagal afferents producing sympathetic activation. Explains the tachycardia seen with rapid volume loading.",
    },
    {
        "name": "Coronary perfusion pressure",
        "aliases": ["CPP"],
        "category": "physiology",
        "summary": "Aortic diastolic pressure minus left ventricular end-diastolic pressure. The left ventricle is perfused mainly in diastole because systolic compression collapses intramural vessels. Tachycardia shortens diastole and worsens ischaemia.",
    },

    # ───────────────────────── PHYSIOLOGY: RESPIRATORY ─────────────────────────
    {
        "name": "Functional residual capacity",
        "aliases": ["FRC"],
        "category": "physiology",
        "summary": "Volume remaining in the lungs at end-expiration with no respiratory effort, about 2.5 L in adults. Represents the equilibrium where outward chest wall recoil balances inward lung recoil. Reduced supine, in obesity, pregnancy, and under general anaesthesia.",
    },
    {
        "name": "Total lung capacity",
        "aliases": ["TLC"],
        "category": "physiology",
        "summary": "Maximum volume the lungs can hold after a full inspiration, about 6 L. Increased in obstructive disease (hyperinflation), decreased in restrictive disease.",
    },
    {
        "name": "Residual volume",
        "aliases": ["RV"],
        "category": "physiology",
        "summary": "Volume of air left in the lungs after maximal expiration, about 1.2 L. Cannot be measured by spirometry; requires plethysmography or helium dilution. Increased in air trapping.",
    },
    {
        "name": "Vital capacity",
        "aliases": ["VC", "FVC"],
        "category": "physiology",
        "summary": "Maximum volume exhaled after a full inspiration, about 4.5 L. Reduced in both obstructive and restrictive disease. FVC is the forced version measured during spirometry.",
    },
    {
        "name": "FEV1/FVC ratio",
        "aliases": ["Tiffeneau index"],
        "category": "physiology",
        "summary": "Fraction of forced vital capacity exhaled in the first second, normally above 0.7. Reduced in obstructive disease (asthma, COPD); preserved or increased in restrictive disease where both FEV1 and FVC fall proportionally.",
    },
    {
        "name": "Compliance (respiratory)",
        "aliases": ["Lung compliance", "C_L"],
        "category": "physiology",
        "summary": "Change in lung volume per unit change in transpulmonary pressure, normally about 200 mL/cmH2O. Increased in emphysema (destroyed elastin), decreased in fibrosis, pulmonary oedema, and ARDS.",
    },
    {
        "name": "Surfactant",
        "aliases": [],
        "category": "physiology",
        "summary": "Mixture of phospholipids (mainly dipalmitoylphosphatidylcholine) and proteins produced by type II pneumocytes from around 24 weeks gestation. Reduces alveolar surface tension, prevents collapse, and increases compliance. Deficiency causes neonatal respiratory distress syndrome.",
    },
    {
        "name": "Laplace's law",
        "aliases": ["Law of Laplace"],
        "category": "physiology",
        "summary": "For a sphere, pressure is proportional to 2 times tension divided by radius. In the lung, small alveoli would collapse into larger ones without surfactant, which lowers tension preferentially where surface area is small.",
    },
    {
        "name": "Dead space",
        "aliases": ["Anatomic dead space", "Physiologic dead space"],
        "category": "physiology",
        "summary": "Ventilated volume that does not participate in gas exchange. Anatomic dead space is the conducting airways (about 150 mL); physiologic includes alveoli that are ventilated but not perfused. Increases with PE, positive pressure ventilation, and ageing.",
    },
    {
        "name": "Ventilation-perfusion ratio",
        "aliases": ["V/Q ratio", "VQ ratio"],
        "category": "physiology",
        "summary": "Ratio of alveolar ventilation to pulmonary capillary perfusion, ideally about 0.8 overall. V/Q is higher at the apex and lower at the base of the upright lung. Mismatch is the commonest cause of hypoxaemia.",
    },
    {
        "name": "Shunt",
        "aliases": ["Right-to-left shunt"],
        "category": "physiology",
        "summary": "Blood that bypasses ventilated alveoli, producing hypoxaemia that does not correct with supplemental oxygen. Causes include atelectasis, consolidation, ARDS, and intracardiac shunts.",
    },
    {
        "name": "Hypoxic pulmonary vasoconstriction",
        "aliases": ["HPV"],
        "category": "physiology",
        "summary": "Pulmonary arteriolar constriction in response to low alveolar PO2, redirecting blood toward better-ventilated areas. Unique to the pulmonary circulation (systemic vessels dilate to hypoxia). Chronic activation contributes to pulmonary hypertension in COPD and sleep apnoea.",
    },
    {
        "name": "Oxygen-haemoglobin dissociation curve",
        "aliases": ["Oxyhaemoglobin curve", "Hb dissociation curve"],
        "category": "physiology",
        "summary": "Sigmoid relationship between PaO2 and haemoglobin saturation. P50 (50 percent saturation) is normally about 26 mmHg. Right shift (lower affinity) with acidosis, hypercapnia, 2,3-BPG, and heat (Bohr effect); left shift with the opposites and with fetal Hb.",
    },
    {
        "name": "Bohr effect",
        "aliases": [],
        "category": "physiology",
        "summary": "Increased CO2 and decreased pH right-shift the oxyhaemoglobin curve, promoting O2 release in metabolically active tissues. In the lungs, the opposite conditions facilitate O2 loading.",
    },
    {
        "name": "Haldane effect",
        "aliases": [],
        "category": "physiology",
        "summary": "Deoxygenated haemoglobin carries more CO2 than oxygenated haemoglobin. As blood is oxygenated in the lungs, CO2 is released; in tissues, deoxygenation enhances CO2 uptake.",
    },
    {
        "name": "Alveolar gas equation",
        "aliases": ["PAO2 equation"],
        "category": "physiology",
        "summary": "PAO2 equals FiO2 times (Patm minus PH2O) minus PaCO2/R, where R is the respiratory quotient (about 0.8). Used to compute the alveolar-arterial gradient and identify gas exchange abnormalities.",
    },
    {
        "name": "A-a gradient",
        "aliases": ["Alveolar-arterial gradient", "A-aDO2"],
        "category": "physiology",
        "summary": "Difference between alveolar and arterial PO2, normally 5 to 15 mmHg in young adults (rising with age). Increased gradient suggests V/Q mismatch, shunt, or diffusion limitation; normal gradient with hypoxaemia suggests hypoventilation or low FiO2.",
    },
    {
        "name": "Carbon dioxide transport",
        "aliases": ["CO2 transport"],
        "category": "physiology",
        "summary": "About 70 percent of CO2 is carried as bicarbonate (via carbonic anhydrase in red cells with chloride shift), 20 percent bound to haemoglobin as carbamino compounds, and 10 percent dissolved.",
    },
    {
        "name": "Diffusing capacity",
        "aliases": ["DLCO", "Transfer factor"],
        "category": "physiology",
        "summary": "Rate of carbon monoxide uptake from inspired gas, used as a surrogate for membrane diffusion. Reduced in emphysema, fibrosis, and pulmonary vascular disease; increased in alveolar haemorrhage and asthma.",
    },
    {
        "name": "Control of breathing",
        "aliases": [],
        "category": "physiology",
        "summary": "Dorsal and ventral respiratory groups in the medulla generate the rhythm; pons modulates pattern. Central chemoreceptors respond to CSF pH (driven by PaCO2); peripheral chemoreceptors in the carotid and aortic bodies respond mainly to PaO2 below 60 mmHg.",
    },

    # ───────────────────────── PHYSIOLOGY: RENAL ─────────────────────────
    {
        "name": "Glomerular filtration rate",
        "aliases": ["GFR", "eGFR"],
        "category": "physiology",
        "summary": "Volume of plasma filtered per unit time, normally about 120 mL/min/1.73 m^2. Determined by hydrostatic and oncotic pressures across the glomerulus. Best estimated clinically by creatinine-based formulas, with caution at extremes of muscle mass.",
    },
    {
        "name": "Filtration fraction",
        "aliases": ["FF"],
        "category": "physiology",
        "summary": "GFR divided by renal plasma flow, normally about 0.2. Rises when efferent arteriolar constriction (angiotensin II) maintains GFR despite falling renal blood flow.",
    },
    {
        "name": "Renal autoregulation",
        "aliases": [],
        "category": "physiology",
        "summary": "Maintains GFR over a wide range of mean arterial pressures (about 80 to 180 mmHg) through myogenic response and tubuloglomerular feedback. Macula densa cells sense distal tubular NaCl and adjust afferent arteriolar tone.",
    },
    {
        "name": "Tubuloglomerular feedback",
        "aliases": ["TGF"],
        "category": "physiology",
        "summary": "Macula densa detects increased NaCl delivery (high GFR) and signals adenosine release to constrict the afferent arteriole, lowering GFR. The reverse occurs with low delivery.",
    },
    {
        "name": "Juxtaglomerular apparatus",
        "aliases": ["JGA"],
        "category": "physiology",
        "summary": "Site where macula densa cells of the distal tubule contact granular cells of the afferent arteriole. Granular cells secrete renin in response to low NaCl delivery, low afferent pressure, and sympathetic activity.",
    },
    {
        "name": "Renin-angiotensin-aldosterone system",
        "aliases": ["RAAS"],
        "category": "physiology",
        "summary": "Renin cleaves angiotensinogen to angiotensin I, ACE converts it to angiotensin II in the lung. Angiotensin II vasoconstricts (especially efferent arteriole), stimulates aldosterone release, and triggers thirst and ADH. Net effect: raises blood pressure and retains sodium and water.",
    },
    {
        "name": "Aldosterone",
        "aliases": [],
        "category": "physiology",
        "summary": "Mineralocorticoid from the zona glomerulosa stimulated by angiotensin II and high potassium. Acts on principal cells to increase ENaC and Na+/K+ ATPase activity, retaining Na+ and water while excreting K+ and H+.",
    },
    {
        "name": "Antidiuretic hormone",
        "aliases": ["ADH", "Vasopressin", "AVP"],
        "category": "physiology",
        "summary": "Posterior pituitary peptide released in response to plasma hyperosmolality or hypovolaemia. Acts on V2 receptors in collecting duct to insert aquaporin-2, concentrating urine; V1 receptors vasoconstrict at high concentrations.",
    },
    {
        "name": "Atrial natriuretic peptide",
        "aliases": ["ANP", "BNP"],
        "category": "physiology",
        "summary": "Peptide released from atrial (ANP) and ventricular (BNP) myocytes in response to wall stretch. Promotes natriuresis, vasodilation, and inhibits RAAS. BNP is elevated in heart failure and used diagnostically.",
    },
    {
        "name": "Countercurrent multiplier",
        "aliases": [],
        "category": "physiology",
        "summary": "Mechanism in the loop of Henle that generates the hypertonic medullary interstitium. Active NaCl reabsorption in the thick ascending limb without water permeability concentrates the interstitium, allowing later water reabsorption in the collecting duct.",
    },
    {
        "name": "Countercurrent exchanger",
        "aliases": ["Vasa recta"],
        "category": "physiology",
        "summary": "Hairpin loops of the vasa recta preserve the medullary osmotic gradient by passively equilibrating solutes and water as blood descends and ascends.",
    },
    {
        "name": "Clearance",
        "aliases": ["Renal clearance"],
        "category": "physiology",
        "summary": "Volume of plasma from which a substance is completely removed per unit time, calculated as (urine concentration times urine flow) divided by plasma concentration. Inulin clearance equals GFR; PAH clearance approximates renal plasma flow.",
    },
    {
        "name": "Free water clearance",
        "aliases": ["CH2O"],
        "category": "physiology",
        "summary": "Urine flow minus osmolar clearance; positive when dilute urine is excreted, negative when water is retained as in SIADH. Used to assess water handling.",
    },
    {
        "name": "Fractional excretion of sodium",
        "aliases": ["FENa"],
        "category": "physiology",
        "summary": "Fraction of filtered sodium excreted in urine. Below 1 percent suggests prerenal AKI (avid Na+ retention); above 2 percent suggests intrinsic (tubular) injury. Less reliable on diuretics; FEUrea is then preferred.",
    },
    {
        "name": "Anion gap",
        "aliases": ["AG"],
        "category": "physiology",
        "summary": "Na+ minus (Cl- plus HCO3-), normally 8 to 12 mmol/L. Increased in lactic acidosis, ketoacidosis, uraemia, and toxic alcohols. Useful in classifying metabolic acidosis (MUDPILES mnemonic).",
    },
    {
        "name": "Henderson-Hasselbalch equation",
        "aliases": [],
        "category": "physiology",
        "summary": "pH equals pKa plus log of base over acid. For the bicarbonate buffer: pH equals 6.1 plus log of (HCO3- / 0.03 times PaCO2). Quantifies acid-base relationships.",
    },
    {
        "name": "Winter's formula",
        "aliases": [],
        "category": "physiology",
        "summary": "Expected PaCO2 in metabolic acidosis equals 1.5 times HCO3- plus 8, plus or minus 2. Detects superimposed respiratory disturbance.",
    },

    # ───────────────────────── PHYSIOLOGY: GI ─────────────────────────
    {
        "name": "Gastric acid secretion",
        "aliases": [],
        "category": "physiology",
        "summary": "Parietal cells secrete H+ via the H+/K+ ATPase (proton pump). Three phases: cephalic (vagal), gastric (food distension and peptides activating gastrin from G cells), and intestinal. Histamine from ECL cells, gastrin, and acetylcholine amplify the response.",
    },
    {
        "name": "Gastrin",
        "aliases": [],
        "category": "physiology",
        "summary": "Peptide hormone from antral G cells that stimulates parietal cell acid secretion (directly and via ECL histamine). Released by stomach distension, peptides, and vagal stimulation. Inhibited by low pH (negative feedback).",
    },
    {
        "name": "Secretin",
        "aliases": [],
        "category": "physiology",
        "summary": "Peptide hormone from duodenal S cells released in response to acid. Stimulates pancreatic bicarbonate secretion and inhibits gastric acid secretion. Test stimulus in Zollinger-Ellison syndrome (paradoxical gastrin rise).",
    },
    {
        "name": "Cholecystokinin",
        "aliases": ["CCK"],
        "category": "physiology",
        "summary": "Peptide hormone from duodenal I cells released in response to fats and amino acids. Triggers gallbladder contraction, pancreatic enzyme secretion, and sphincter of Oddi relaxation; slows gastric emptying.",
    },
    {
        "name": "Migrating motor complex",
        "aliases": ["MMC"],
        "category": "physiology",
        "summary": "Cyclical motor pattern during fasting that sweeps undigested material through the small intestine. Driven by motilin from M cells every 90 to 120 minutes. Erythromycin mimics motilin (used as a prokinetic).",
    },
    {
        "name": "Enterohepatic circulation",
        "aliases": [],
        "category": "physiology",
        "summary": "Bile acids secreted into the duodenum are reabsorbed in the terminal ileum and returned to the liver via the portal vein, recycling roughly 95 percent per pass. Disruption (ileal resection, cholestyramine) causes fat malabsorption.",
    },
    {
        "name": "Bile composition",
        "aliases": [],
        "category": "physiology",
        "summary": "Bile contains bile acids (synthesised from cholesterol), phospholipids, cholesterol, bilirubin, water, and electrolytes. Imbalance favours gallstone formation: cholesterol stones from supersaturation, pigment stones from haemolysis or infection.",
    },
    {
        "name": "Pancreatic enzyme secretion",
        "aliases": [],
        "category": "physiology",
        "summary": "Acinar cells secrete digestive enzymes (amylase, lipase, proteases as zymogens) under CCK and vagal control. Ductal cells secrete bicarbonate-rich fluid under secretin control to neutralise gastric acid.",
    },
    {
        "name": "Intrinsic factor",
        "aliases": ["IF"],
        "category": "physiology",
        "summary": "Glycoprotein from gastric parietal cells that binds vitamin B12 in the duodenum for absorption in the terminal ileum. Loss (autoimmune gastritis, gastrectomy) causes pernicious anaemia.",
    },

    # ───────────────────────── PHYSIOLOGY: ENDOCRINE ─────────────────────────
    {
        "name": "Insulin secretion",
        "aliases": [],
        "category": "physiology",
        "summary": "Glucose enters beta cells via GLUT2, is phosphorylated by glucokinase, and metabolised to raise ATP. ATP closes K-ATP channels, depolarisation opens Ca2+ channels, triggering insulin granule release. Sulfonylureas mimic this by closing K-ATP channels directly.",
    },
    {
        "name": "Insulin action",
        "aliases": [],
        "category": "physiology",
        "summary": "Activates tyrosine kinase receptor, drives GLUT4 to muscle and adipose membranes for glucose uptake, stimulates glycogen and lipid synthesis, and suppresses gluconeogenesis and lipolysis. Net anabolic effect.",
    },
    {
        "name": "Glucagon",
        "aliases": [],
        "category": "physiology",
        "summary": "Alpha cell hormone released during fasting. Stimulates hepatic glycogenolysis and gluconeogenesis; promotes lipolysis and ketogenesis. Opposes insulin. Used to treat severe hypoglycaemia when IV access is unavailable.",
    },
    {
        "name": "Incretin effect",
        "aliases": ["GLP-1", "GIP"],
        "category": "physiology",
        "summary": "GLP-1 (L cells) and GIP (K cells) released from the gut in response to nutrient ingestion. Augment glucose-dependent insulin release, slow gastric emptying, and reduce appetite. Basis for GLP-1 agonists and DPP-4 inhibitors.",
    },
    {
        "name": "HPA axis",
        "aliases": ["Hypothalamic-pituitary-adrenal axis"],
        "category": "physiology",
        "summary": "CRH from hypothalamus drives ACTH from anterior pituitary, which stimulates cortisol from the adrenal zona fasciculata. Cortisol feeds back negatively. Diurnal: peaks early morning, troughs at night.",
    },
    {
        "name": "Cortisol",
        "aliases": [],
        "category": "physiology",
        "summary": "Glucocorticoid that raises blood glucose (gluconeogenesis), suppresses immune function, increases vascular tone, and inhibits bone formation. Permissive for catecholamine action. Chronic excess causes Cushingoid features.",
    },
    {
        "name": "Thyroid hormone synthesis",
        "aliases": [],
        "category": "physiology",
        "summary": "Iodide is trapped by NIS, oxidised by thyroid peroxidase, and incorporated into thyroglobulin tyrosines forming MIT and DIT. Coupling yields T3 and T4. Carbimazole and propylthiouracil block thyroid peroxidase; PTU also blocks peripheral T4 to T3 conversion.",
    },
    {
        "name": "Thyroid hormone action",
        "aliases": ["T3", "T4"],
        "category": "physiology",
        "summary": "T3 (active) binds nuclear receptors to increase basal metabolic rate, beta-adrenergic sensitivity, growth, and CNS development. T4 is the main circulating form, deiodinated peripherally to T3.",
    },
    {
        "name": "Calcium homeostasis",
        "aliases": [],
        "category": "physiology",
        "summary": "Parathyroid hormone raises calcium by mobilising bone, increasing renal reabsorption, and activating vitamin D for gut absorption. Calcitonin (parafollicular C cells) opposes this but is clinically minor. Vitamin D increases gut calcium and phosphate absorption.",
    },
    {
        "name": "Parathyroid hormone",
        "aliases": ["PTH"],
        "category": "physiology",
        "summary": "Released by chief cells in response to low calcium sensed by the calcium-sensing receptor. Raises serum calcium via bone resorption, distal tubule Ca2+ reabsorption, and 1-alpha-hydroxylase activation; phosphaturic effect.",
    },
    {
        "name": "Vitamin D activation",
        "aliases": ["Calcitriol", "1,25-dihydroxyvitamin D"],
        "category": "physiology",
        "summary": "Cholecalciferol from skin or diet is 25-hydroxylated in the liver, then 1-alpha-hydroxylated in the kidney (stimulated by PTH and low phosphate) to the active form, calcitriol, which increases gut Ca2+ and phosphate absorption.",
    },
    {
        "name": "Growth hormone",
        "aliases": ["GH", "Somatotropin"],
        "category": "physiology",
        "summary": "Anterior pituitary peptide released in pulses (especially during sleep). Direct lipolytic and anti-insulin effects; indirect anabolic effects via hepatic IGF-1. Excess produces gigantism (prepubertal) or acromegaly (adult).",
    },
    {
        "name": "Prolactin",
        "aliases": [],
        "category": "physiology",
        "summary": "Anterior pituitary hormone tonically inhibited by dopamine from the hypothalamus. Drives lactation; suppresses GnRH. Dopamine antagonists (antipsychotics, metoclopramide) elevate prolactin.",
    },

    # ───────────────────────── PHYSIOLOGY: NEURO ─────────────────────────
    {
        "name": "Resting membrane potential",
        "aliases": ["RMP"],
        "category": "physiology",
        "summary": "Voltage across a cell membrane at rest, about -70 mV in neurons. Maintained by Na+/K+ ATPase and selective K+ permeability through leak channels. Calculated from the Goldman equation.",
    },
    {
        "name": "Action potential",
        "aliases": ["AP"],
        "category": "physiology",
        "summary": "All-or-nothing depolarisation when threshold is reached. Voltage-gated Na+ channels open (depolarisation), inactivate, then voltage-gated K+ channels open (repolarisation). Refractory periods prevent backpropagation.",
    },
    {
        "name": "Saltatory conduction",
        "aliases": [],
        "category": "physiology",
        "summary": "Action potentials jump between nodes of Ranvier on myelinated axons, dramatically increasing conduction velocity and reducing energy use. Demyelination (MS, Guillain-Barre) slows or blocks conduction.",
    },
    {
        "name": "Neurotransmitter release",
        "aliases": [],
        "category": "physiology",
        "summary": "Depolarisation opens voltage-gated Ca2+ channels at the axon terminal; Ca2+ binds synaptotagmin, triggering SNARE-mediated vesicle fusion with the presynaptic membrane. Botulinum and tetanus toxins cleave SNAREs.",
    },
    {
        "name": "Long-term potentiation",
        "aliases": ["LTP"],
        "category": "physiology",
        "summary": "Persistent strengthening of synapses based on recent patterns of activity. Classically mediated by NMDA receptor activation in the hippocampus. Cellular basis of learning and memory.",
    },
    {
        "name": "Blood-brain barrier",
        "aliases": ["BBB"],
        "category": "physiology",
        "summary": "Tight junctions between cerebral capillary endothelial cells (with astrocyte foot processes and pericytes) restrict passage of polar and large molecules into the CNS. Disrupted by inflammation, allowing IV contrast and antibiotics to penetrate.",
    },
    {
        "name": "Cerebral autoregulation",
        "aliases": [],
        "category": "physiology",
        "summary": "Cerebral blood flow held nearly constant across MAP of about 60 to 160 mmHg via myogenic adjustment of arteriolar tone. Shifted right in chronic hypertension. Outside this range, flow becomes pressure-dependent.",
    },
    {
        "name": "Monro-Kellie doctrine",
        "aliases": [],
        "category": "physiology",
        "summary": "Inside the rigid skull, the sum of brain, blood, and CSF volumes is constant. Any increase in one component must be compensated by displacement of another, or intracranial pressure will rise.",
    },
    {
        "name": "CSF production and flow",
        "aliases": [],
        "category": "physiology",
        "summary": "Choroid plexus produces about 500 mL/day. Flow: lateral ventricles to third ventricle via foramen of Monro, through aqueduct of Sylvius to fourth ventricle, out via foramina of Luschka and Magendie, absorbed at arachnoid granulations.",
    },
    {
        "name": "Reflex arc",
        "aliases": [],
        "category": "physiology",
        "summary": "Sensory receptor to afferent neuron to integrating centre (often spinal cord) to efferent neuron to effector. Monosynaptic stretch reflex (e.g., patellar) bypasses interneurons; withdrawal reflex is polysynaptic.",
    },
    {
        "name": "Dorsal column-medial lemniscus pathway",
        "aliases": ["DCML"],
        "category": "physiology",
        "summary": "Carries fine touch, vibration, and proprioception. First-order neuron ascends ipsilaterally in the dorsal columns, synapses in medulla (gracile/cuneate nuclei), decussates, ascends as medial lemniscus to VPL thalamus, then to primary somatosensory cortex.",
    },
    {
        "name": "Spinothalamic tract",
        "aliases": [],
        "category": "physiology",
        "summary": "Carries pain, temperature, and crude touch. First-order neuron synapses in dorsal horn, second-order decussates within a few segments and ascends to VPL thalamus. Anterolateral cord lesions produce contralateral pain and temperature loss.",
    },
    {
        "name": "Corticospinal tract",
        "aliases": ["CST", "Pyramidal tract"],
        "category": "physiology",
        "summary": "Main descending motor pathway. About 85 percent of fibres decussate at the medulla (lateral CST), 15 percent remain ipsilateral (anterior CST). Lesions above the decussation cause contralateral weakness.",
    },

    # ───────────────────────── PHYSIOLOGY: HAEMATOLOGY ─────────────────────────
    {
        "name": "Erythropoiesis",
        "aliases": [],
        "category": "physiology",
        "summary": "Red cell production in the bone marrow, driven by erythropoietin from renal peritubular fibroblasts in response to hypoxia. Requires iron, B12, folate, and a healthy marrow niche. Reticulocytes mature in circulation over 1 to 2 days.",
    },
    {
        "name": "Coagulation cascade",
        "aliases": [],
        "category": "physiology",
        "summary": "Tissue factor (extrinsic) and contact activation (intrinsic) pathways converge at factor X, leading to thrombin generation and fibrin formation. In vivo, tissue factor binding to factor VIIa is the dominant initiator.",
    },
    {
        "name": "Virchow's triad",
        "aliases": [],
        "category": "physiology",
        "summary": "Three factors predisposing to thrombosis: stasis, endothelial injury, and hypercoagulability. Useful framework for VTE risk assessment.",
    },
    {
        "name": "Fibrinolysis",
        "aliases": [],
        "category": "physiology",
        "summary": "Plasminogen is converted to plasmin by tissue plasminogen activator (tPA), which then cleaves fibrin into D-dimers and fibrin degradation products. Basis of thrombolytic therapy (alteplase, tenecteplase).",
    },
    {
        "name": "Protein C and S pathway",
        "aliases": [],
        "category": "physiology",
        "summary": "Thrombin bound to thrombomodulin activates protein C, which with cofactor protein S inactivates factors Va and VIIIa. Vitamin K-dependent. Deficiency causes thrombophilia; warfarin transiently depletes protein C first (skin necrosis risk).",
    },
    {
        "name": "Platelet activation",
        "aliases": [],
        "category": "physiology",
        "summary": "Exposed subendothelial collagen binds vWF, which tethers platelets via GP1b. Platelets activate, secrete granules (ADP, thromboxane), and aggregate via GP2b/3a binding fibrinogen. Targets of aspirin (COX-1), clopidogrel (P2Y12), and abciximab (GP2b/3a).",
    },
    {
        "name": "von Willebrand factor",
        "aliases": ["vWF"],
        "category": "physiology",
        "summary": "Multimeric glycoprotein from endothelial Weibel-Palade bodies and platelet alpha granules. Bridges platelets to subendothelial collagen and carries factor VIII. Deficiency causes mucocutaneous bleeding.",
    },

    # ───────────────────────── BIOCHEMISTRY ─────────────────────────
    {
        "name": "Glycolysis",
        "aliases": [],
        "category": "biochemistry",
        "summary": "Cytosolic pathway converting one glucose to two pyruvate, yielding net 2 ATP and 2 NADH. Irreversible steps catalysed by hexokinase, phosphofructokinase-1 (main regulator), and pyruvate kinase. Anaerobic conditions divert pyruvate to lactate to regenerate NAD+.",
    },
    {
        "name": "Gluconeogenesis",
        "aliases": [],
        "category": "biochemistry",
        "summary": "Hepatic synthesis of glucose from non-carbohydrate precursors (lactate, glycerol, glucogenic amino acids). Reverses glycolysis except at four steps: pyruvate carboxylase, PEPCK, fructose-1,6-bisphosphatase, glucose-6-phosphatase. Stimulated by glucagon and cortisol.",
    },
    {
        "name": "Citric acid cycle",
        "aliases": ["TCA cycle", "Krebs cycle"],
        "category": "biochemistry",
        "summary": "Mitochondrial pathway oxidising acetyl-CoA to 2 CO2, generating 3 NADH, 1 FADH2, and 1 GTP per turn. Rate-limited by isocitrate dehydrogenase. Provides electron carriers for the electron transport chain.",
    },
    {
        "name": "Electron transport chain",
        "aliases": ["ETC"],
        "category": "biochemistry",
        "summary": "Inner mitochondrial membrane complexes pass electrons from NADH and FADH2 to oxygen, pumping protons to create a gradient. ATP synthase uses the gradient to generate ATP (oxidative phosphorylation). Yields roughly 2.5 ATP per NADH, 1.5 per FADH2.",
    },
    {
        "name": "Oxidative phosphorylation",
        "aliases": ["OXPHOS"],
        "category": "biochemistry",
        "summary": "Coupling of electron transport to ATP synthesis via the proton motive force. Uncouplers (2,4-DNP, thermogenin in brown fat) dissipate the gradient as heat. Cyanide inhibits complex IV; rotenone inhibits complex I.",
    },
    {
        "name": "Pyruvate dehydrogenase",
        "aliases": ["PDH"],
        "category": "biochemistry",
        "summary": "Mitochondrial complex converting pyruvate to acetyl-CoA. Requires five cofactors: thiamine (B1), lipoate, CoA, FAD, NAD+. Inactivated by phosphorylation; activated by dephosphorylation and rising Ca2+. Deficiency causes lactic acidosis and neurological symptoms.",
    },
    {
        "name": "Pentose phosphate pathway",
        "aliases": ["PPP", "HMP shunt"],
        "category": "biochemistry",
        "summary": "Cytosolic pathway producing NADPH (for reductive biosynthesis and glutathione regeneration) and ribose-5-phosphate (for nucleotides). Rate-limited by glucose-6-phosphate dehydrogenase. G6PD deficiency predisposes to oxidative haemolysis.",
    },
    {
        "name": "Glycogenesis",
        "aliases": [],
        "category": "biochemistry",
        "summary": "Synthesis of glycogen from glucose-6-phosphate via UDP-glucose. Glycogen synthase forms alpha-1,4 bonds; branching enzyme creates alpha-1,6 branches. Stimulated by insulin.",
    },
    {
        "name": "Glycogenolysis",
        "aliases": [],
        "category": "biochemistry",
        "summary": "Breakdown of glycogen to glucose-1-phosphate by glycogen phosphorylase, then to glucose-6-phosphate. Liver releases free glucose (via G6Pase); muscle uses it locally. Stimulated by glucagon (liver) and epinephrine (both).",
    },
    {
        "name": "Fatty acid oxidation",
        "aliases": ["Beta oxidation"],
        "category": "biochemistry",
        "summary": "Mitochondrial pathway shortening fatty acyl-CoA by two carbons per cycle, producing acetyl-CoA, NADH, and FADH2. Long-chain fatty acids enter via the carnitine shuttle. Defects (MCAD deficiency) cause fasting hypoglycaemia.",
    },
    {
        "name": "Fatty acid synthesis",
        "aliases": [],
        "category": "biochemistry",
        "summary": "Cytosolic pathway elongating two-carbon units from acetyl-CoA to palmitate, using NADPH. Rate-limited by acetyl-CoA carboxylase (forming malonyl-CoA). Stimulated by insulin and citrate; inhibited by glucagon.",
    },
    {
        "name": "Ketogenesis",
        "aliases": [],
        "category": "biochemistry",
        "summary": "Hepatic conversion of acetyl-CoA (from fatty acid oxidation) to acetoacetate, beta-hydroxybutyrate, and acetone during prolonged fasting or insulin deficiency. Ketones are an alternative fuel for brain and muscle.",
    },
    {
        "name": "Urea cycle",
        "aliases": [],
        "category": "biochemistry",
        "summary": "Hepatic mitochondrial and cytosolic pathway converting ammonia (from amino acid catabolism) to urea for renal excretion. Rate-limited by carbamoyl phosphate synthetase I. Enzyme deficiencies cause hyperammonaemia.",
    },
    {
        "name": "Cori cycle",
        "aliases": [],
        "category": "biochemistry",
        "summary": "Lactate produced by anaerobic muscle is carried to the liver, converted back to glucose via gluconeogenesis, and returned to muscle. Net energy cost is paid by the liver; relevant in sepsis and shock.",
    },
    {
        "name": "Cahill cycle",
        "aliases": ["Alanine cycle"],
        "category": "biochemistry",
        "summary": "Muscle transaminates pyruvate to alanine using nitrogen from amino acid catabolism. Alanine travels to the liver where it is converted back to pyruvate for gluconeogenesis, and the nitrogen enters the urea cycle.",
    },
    {
        "name": "Hexokinase vs glucokinase",
        "aliases": [],
        "category": "biochemistry",
        "summary": "Hexokinase (ubiquitous) has low Km, high affinity, is inhibited by glucose-6-phosphate. Glucokinase (liver and pancreatic beta cells) has high Km, induced by insulin, not feedback inhibited; matches phosphorylation rate to glucose concentration.",
    },
    {
        "name": "Phosphofructokinase-1",
        "aliases": ["PFK-1"],
        "category": "biochemistry",
        "summary": "Rate-limiting enzyme of glycolysis. Activated by AMP and fructose-2,6-bisphosphate; inhibited by ATP and citrate. Reciprocally regulated with fructose-1,6-bisphosphatase in gluconeogenesis.",
    },
    {
        "name": "Cholesterol synthesis",
        "aliases": [],
        "category": "biochemistry",
        "summary": "Cytosolic and ER pathway from acetyl-CoA via mevalonate to cholesterol. Rate-limited by HMG-CoA reductase, the target of statins. SREBP-2 transcriptionally upregulates the pathway when intracellular cholesterol falls.",
    },
    {
        "name": "Lipoprotein metabolism",
        "aliases": [],
        "category": "biochemistry",
        "summary": "Chylomicrons carry dietary triglycerides; VLDL carries hepatic triglycerides; LDL delivers cholesterol to tissues; HDL returns cholesterol to the liver (reverse transport). Lipoprotein lipase, hepatic lipase, and LCAT remodel particles.",
    },
    {
        "name": "Haem synthesis",
        "aliases": [],
        "category": "biochemistry",
        "summary": "Eight-step pathway from succinyl-CoA and glycine to haem. ALA synthase (rate-limiting) is inhibited by haem (feedback). Lead inhibits ALA dehydratase and ferrochelatase. Defects produce porphyrias.",
    },
    {
        "name": "Bilirubin metabolism",
        "aliases": [],
        "category": "biochemistry",
        "summary": "Haem to biliverdin (haem oxygenase) to unconjugated bilirubin (transported albumin-bound), conjugated in hepatocytes by UGT1A1, excreted in bile, deconjugated in gut to urobilinogen and stercobilin. Defects produce Gilbert's and Crigler-Najjar syndromes.",
    },
    {
        "name": "Haemoglobin structure",
        "aliases": [],
        "category": "biochemistry",
        "summary": "Tetramer of two alpha and two beta subunits (HbA), each carrying a haem with a central Fe2+. Cooperative O2 binding produces the sigmoid dissociation curve. Variants: HbF (alpha2 gamma2), HbA2 (alpha2 delta2).",
    },
    {
        "name": "2,3-bisphosphoglycerate",
        "aliases": ["2,3-BPG", "2,3-DPG"],
        "category": "biochemistry",
        "summary": "Glycolysis side-product in red cells that binds deoxyhaemoglobin and stabilises the T state, right-shifting the O2 dissociation curve. Increased in chronic hypoxia and at altitude.",
    },
    {
        "name": "Essential amino acids",
        "aliases": [],
        "category": "biochemistry",
        "summary": "Cannot be synthesised by humans and must come from diet: phenylalanine, valine, threonine, tryptophan, isoleucine, methionine, histidine, leucine, lysine (PVT TIM HaLL).",
    },
    {
        "name": "Glucogenic vs ketogenic amino acids",
        "aliases": [],
        "category": "biochemistry",
        "summary": "Glucogenic amino acids enter as pyruvate or TCA intermediates and can become glucose. Purely ketogenic: leucine and lysine. Some are both (isoleucine, phenylalanine, tryptophan, tyrosine).",
    },
    {
        "name": "Phenylalanine metabolism",
        "aliases": [],
        "category": "biochemistry",
        "summary": "Phenylalanine hydroxylase converts phenylalanine to tyrosine using BH4 cofactor. Deficiency causes phenylketonuria; tyrosine becomes essential. Tyrosine is the precursor to catecholamines, melanin, and thyroid hormones.",
    },
    {
        "name": "One-carbon metabolism",
        "aliases": ["Folate metabolism"],
        "category": "biochemistry",
        "summary": "Tetrahydrofolate carries one-carbon groups for nucleotide and amino acid synthesis. B12 transfers methyl from methyl-THF to homocysteine, regenerating methionine. Deficiency raises homocysteine and impairs DNA synthesis (megaloblastic anaemia).",
    },
    {
        "name": "Purine synthesis",
        "aliases": [],
        "category": "biochemistry",
        "summary": "De novo synthesis builds the purine ring on PRPP using glutamine, glycine, aspartate, CO2, and one-carbon units from folate. Salvage uses HGPRT (deficient in Lesch-Nyhan). End product hypoxanthine to xanthine to uric acid via xanthine oxidase (allopurinol target).",
    },
    {
        "name": "Pyrimidine synthesis",
        "aliases": [],
        "category": "biochemistry",
        "summary": "De novo synthesis starts with carbamoyl phosphate (from CPS II, cytosolic) plus aspartate, forming the ring before sugar attachment. Dihydroorotate dehydrogenase is the target of leflunomide.",
    },
    {
        "name": "DNA replication",
        "aliases": [],
        "category": "biochemistry",
        "summary": "Semiconservative process at origins of replication. Helicase unwinds, primase lays RNA primers, DNA polymerase synthesises 5' to 3' (leading continuous, lagging in Okazaki fragments), ligase seals nicks. Topoisomerases relieve supercoiling.",
    },
    {
        "name": "DNA repair mechanisms",
        "aliases": [],
        "category": "biochemistry",
        "summary": "Mismatch repair (defective in Lynch syndrome), nucleotide excision repair (UV damage, defective in xeroderma pigmentosum), base excision repair, and homologous recombination (BRCA1/2). Defects predispose to cancer.",
    },
    {
        "name": "Transcription",
        "aliases": [],
        "category": "biochemistry",
        "summary": "RNA polymerase II reads template DNA 3' to 5' and synthesises mRNA 5' to 3'. Pre-mRNA undergoes 5' capping, 3' polyadenylation, and splicing. Eukaryotic gene expression is tightly regulated by transcription factors.",
    },
    {
        "name": "Translation",
        "aliases": [],
        "category": "biochemistry",
        "summary": "Ribosomes assemble proteins from mRNA in cytoplasm. Initiation at AUG with Met-tRNA, elongation through codons via aminoacyl tRNAs (A, P, E sites), termination at stop codons. Many antibiotics target bacterial ribosomes (aminoglycosides, tetracyclines, macrolides).",
    },
    {
        "name": "Post-translational modifications",
        "aliases": ["PTMs"],
        "category": "biochemistry",
        "summary": "Modifications after translation: phosphorylation, glycosylation, ubiquitination, methylation, acetylation, proteolytic cleavage (e.g., proinsulin to insulin). Often regulate activity, localisation, or stability.",
    },
    {
        "name": "Vitamin B1 (thiamine)",
        "aliases": ["Thiamine"],
        "category": "biochemistry",
        "summary": "Cofactor (as TPP) for pyruvate dehydrogenase, alpha-ketoglutarate dehydrogenase, transketolase (PPP), and branched-chain alpha-ketoacid dehydrogenase. Deficiency causes beriberi and Wernicke-Korsakoff.",
    },
    {
        "name": "Vitamin B2 (riboflavin)",
        "aliases": ["Riboflavin"],
        "category": "biochemistry",
        "summary": "Precursor of FAD and FMN, electron carriers in redox reactions. Deficiency causes cheilosis, glossitis, and seborrheic dermatitis.",
    },
    {
        "name": "Vitamin B3 (niacin)",
        "aliases": ["Niacin", "Nicotinic acid"],
        "category": "biochemistry",
        "summary": "Precursor of NAD+ and NADP+. Synthesised from tryptophan (Hartnup disease impairs this). Deficiency causes pellagra (dermatitis, diarrhoea, dementia). Pharmacologic doses lower LDL and raise HDL but cause flushing.",
    },
    {
        "name": "Vitamin B6 (pyridoxine)",
        "aliases": ["Pyridoxine"],
        "category": "biochemistry",
        "summary": "Cofactor (as PLP) for transaminases, decarboxylases (neurotransmitter synthesis), and ALA synthase. Isoniazid depletes B6 and can cause peripheral neuropathy unless supplemented.",
    },
    {
        "name": "Vitamin B9 (folate)",
        "aliases": ["Folate", "Folic acid"],
        "category": "biochemistry",
        "summary": "Cofactor for one-carbon transfers, essential for nucleotide synthesis. Deficiency causes megaloblastic anaemia and, in pregnancy, neural tube defects. Methotrexate and trimethoprim inhibit related enzymes.",
    },
    {
        "name": "Vitamin B12 (cobalamin)",
        "aliases": ["Cobalamin"],
        "category": "biochemistry",
        "summary": "Cofactor for methionine synthase (homocysteine to methionine) and methylmalonyl-CoA mutase. Requires intrinsic factor for absorption. Deficiency causes megaloblastic anaemia and subacute combined degeneration of the cord.",
    },
    {
        "name": "Vitamin C (ascorbic acid)",
        "aliases": ["Ascorbic acid"],
        "category": "biochemistry",
        "summary": "Cofactor for prolyl and lysyl hydroxylases in collagen synthesis; antioxidant; aids iron absorption by reducing Fe3+ to Fe2+. Deficiency causes scurvy (bleeding gums, perifollicular haemorrhages, poor wound healing).",
    },
    {
        "name": "Vitamin K",
        "aliases": [],
        "category": "biochemistry",
        "summary": "Cofactor for gamma-carboxylation of clotting factors II, VII, IX, X, and proteins C and S. Recycled by epoxide reductase (warfarin target). Neonates receive a vitamin K injection to prevent haemorrhagic disease.",
    },
    {
        "name": "Vitamin A",
        "aliases": ["Retinol"],
        "category": "biochemistry",
        "summary": "Required for vision (retinal in rhodopsin), epithelial differentiation, and reproduction. Deficiency causes night blindness and xerophthalmia. Teratogenic in excess (isotretinoin).",
    },
    {
        "name": "Vitamin D",
        "aliases": ["Calciferol"],
        "category": "biochemistry",
        "summary": "Fat-soluble vitamin acting as a steroid hormone after dual hydroxylation. Increases gut Ca2+ and phosphate absorption. Deficiency causes rickets in children and osteomalacia in adults.",
    },
    {
        "name": "Vitamin E",
        "aliases": ["Tocopherol"],
        "category": "biochemistry",
        "summary": "Lipid-soluble antioxidant protecting membrane polyunsaturated fats from peroxidation. Deficiency rare but causes haemolysis, ataxia, and neuropathy. Excess can interfere with vitamin K function.",
    },
    {
        "name": "Michaelis-Menten kinetics",
        "aliases": [],
        "category": "biochemistry",
        "summary": "Enzyme reaction rate equals Vmax times S divided by (Km plus S). Km is the substrate concentration at half Vmax and inversely reflects affinity. Lineweaver-Burk plot linearises this relationship.",
    },
    {
        "name": "Competitive vs non-competitive inhibition",
        "aliases": [],
        "category": "biochemistry",
        "summary": "Competitive inhibitors raise Km without changing Vmax (overcome by more substrate). Non-competitive inhibitors lower Vmax without affecting Km. Uncompetitive inhibitors lower both.",
    },

    # ───────────────────────── MICROBIOLOGY ─────────────────────────
    {
        "name": "Gram stain",
        "aliases": [],
        "category": "microbiology",
        "summary": "Differential stain using crystal violet, iodine, alcohol decoloriser, and safranin counterstain. Gram-positive cells retain crystal violet (purple) due to thick peptidoglycan; gram-negative are stained pink by safranin and have an outer membrane with LPS.",
    },
    {
        "name": "Peptidoglycan",
        "aliases": [],
        "category": "microbiology",
        "summary": "Mesh of N-acetylglucosamine and N-acetylmuramic acid cross-linked by peptide bridges, forming the bacterial cell wall. Synthesis is targeted by beta-lactams (transpeptidase inhibition) and vancomycin (binds D-Ala-D-Ala).",
    },
    {
        "name": "Lipopolysaccharide",
        "aliases": ["LPS", "Endotoxin"],
        "category": "microbiology",
        "summary": "Outer membrane component of gram-negative bacteria. Lipid A is the toxic moiety, signalling via TLR4 to trigger cytokine release; underpins gram-negative sepsis. Heat-stable, released on bacterial lysis.",
    },
    {
        "name": "Exotoxin vs endotoxin",
        "aliases": [],
        "category": "microbiology",
        "summary": "Exotoxins are secreted proteins (often AB toxins) from both gram-positive and gram-negative bacteria; highly potent, antigenic, can be toxoided into vaccines. Endotoxin is LPS from gram-negatives, released on lysis, heat-stable.",
    },
    {
        "name": "AB toxins",
        "aliases": [],
        "category": "microbiology",
        "summary": "Bacterial toxins with two subunits: B binds host receptor, A is the active toxic component. Examples: diphtheria toxin (inhibits EF-2), cholera toxin (activates Gs), pertussis toxin (inactivates Gi), Shiga toxin (cleaves 28S rRNA).",
    },
    {
        "name": "Superantigens",
        "aliases": [],
        "category": "microbiology",
        "summary": "Toxins (e.g., TSST-1 from S. aureus, streptococcal pyrogenic exotoxin A) that crosslink MHC II to TCR outside the antigen groove, causing massive non-specific T-cell activation and cytokine storm. Underlie toxic shock syndromes.",
    },
    {
        "name": "Capsule",
        "aliases": [],
        "category": "microbiology",
        "summary": "Polysaccharide layer outside the cell wall that impairs phagocytosis. Major virulence factor of encapsulated organisms: Strep pneumoniae, H. influenzae type b, N. meningitidis, Klebsiella, Salmonella, group B strep. Targeted by opsonising antibodies and conjugate vaccines.",
    },
    {
        "name": "Biofilm",
        "aliases": [],
        "category": "microbiology",
        "summary": "Sessile bacterial community in a self-produced polysaccharide matrix, often on prosthetics or catheters. Highly tolerant to antibiotics and immune clearance. Quorum sensing regulates biofilm formation.",
    },
    {
        "name": "Quorum sensing",
        "aliases": [],
        "category": "microbiology",
        "summary": "Bacterial cell-cell communication via diffusible signal molecules (autoinducers) whose concentration reflects population density. Triggers coordinated expression of virulence factors and biofilm formation above a threshold.",
    },
    {
        "name": "Beta-lactamase",
        "aliases": [],
        "category": "microbiology",
        "summary": "Enzymes that hydrolyse the beta-lactam ring of penicillins, cephalosporins, monobactams, or carbapenems. Categories include penicillinases, ESBLs (cefotaxime resistance), AmpC, and carbapenemases (e.g., NDM, KPC). Inhibited by clavulanate, tazobactam, sulbactam, avibactam.",
    },
    {
        "name": "MRSA resistance mechanism",
        "aliases": ["Methicillin-resistant Staphylococcus aureus"],
        "category": "microbiology",
        "summary": "Methicillin resistance from acquisition of mecA gene encoding PBP2a, which has low affinity for beta-lactams. Treated with vancomycin, linezolid, daptomycin, or ceftaroline.",
    },
    {
        "name": "Vancomycin resistance",
        "aliases": ["VRE"],
        "category": "microbiology",
        "summary": "Most often in enterococci. vanA and vanB operons replace D-Ala-D-Ala with D-Ala-D-Lac in peptidoglycan precursors, reducing vancomycin affinity 1000-fold. Treated with linezolid or daptomycin.",
    },
    {
        "name": "Efflux pumps",
        "aliases": [],
        "category": "microbiology",
        "summary": "Membrane transporters that actively expel antibiotics, contributing to resistance to tetracyclines, fluoroquinolones, and macrolides. Often broad-spectrum, can be plasmid-encoded.",
    },
    {
        "name": "Plasmid",
        "aliases": [],
        "category": "microbiology",
        "summary": "Extrachromosomal, usually circular DNA that replicates independently. Often carries resistance genes (R plasmids) and virulence factors. Transferred between bacteria by conjugation.",
    },
    {
        "name": "Bacterial conjugation",
        "aliases": [],
        "category": "microbiology",
        "summary": "Cell-to-cell transfer of DNA (typically plasmids) via a sex pilus. Major route of resistance gene spread, especially between gram-negatives.",
    },
    {
        "name": "Transformation",
        "aliases": [],
        "category": "microbiology",
        "summary": "Uptake of naked DNA from the environment. Naturally competent species include Strep pneumoniae, H. influenzae, Neisseria. Important for antigenic variation and resistance acquisition.",
    },
    {
        "name": "Transduction",
        "aliases": [],
        "category": "microbiology",
        "summary": "Bacteriophage-mediated transfer of bacterial DNA. Generalised transduction packages random fragments; specialised transduction transfers genes flanking the prophage integration site. Source of some toxin genes (diphtheria, cholera).",
    },
    {
        "name": "Anaerobic bacteria",
        "aliases": [],
        "category": "microbiology",
        "summary": "Cannot grow in normal atmospheric oxygen. Examples include Bacteroides fragilis (gut), Clostridium species, Fusobacterium, Actinomyces. Often cause polymicrobial abscesses; metronidazole and carbapenems have good activity.",
    },
    {
        "name": "Atypical bacteria",
        "aliases": [],
        "category": "microbiology",
        "summary": "Organisms that do not Gram stain reliably or grow on standard media: Mycoplasma (no cell wall), Chlamydia (obligate intracellular), Legionella, Coxiella. Treated with macrolides, tetracyclines, or fluoroquinolones rather than beta-lactams.",
    },
    {
        "name": "Acid-fast staining",
        "aliases": ["Ziehl-Neelsen"],
        "category": "microbiology",
        "summary": "Mycolic acid in mycobacterial cell walls retains carbol fuchsin despite acid-alcohol washing. Used for Mycobacterium tuberculosis, atypical mycobacteria, and Nocardia (partially acid-fast).",
    },
    {
        "name": "Spore-forming bacteria",
        "aliases": [],
        "category": "microbiology",
        "summary": "Bacillus and Clostridium species form heat-resistant endospores that survive disinfection. Spores germinate when conditions improve, causing disease (anthrax, tetanus, botulism, C. difficile, gas gangrene).",
    },
    {
        "name": "Obligate intracellular bacteria",
        "aliases": [],
        "category": "microbiology",
        "summary": "Cannot make their own ATP or grow on artificial media. Examples: Chlamydia (uses host ATP), Rickettsia, Coxiella, Ehrlichia. Diagnosed serologically or by PCR.",
    },
    {
        "name": "Pneumonia pathogens by setting",
        "aliases": [],
        "category": "microbiology",
        "summary": "CAP: Strep pneumoniae most common; atypicals (Mycoplasma, Legionella, Chlamydophila) in younger adults. HAP/VAP: Pseudomonas, Klebsiella, Acinetobacter, MRSA. Aspiration: anaerobes plus oral flora.",
    },
    {
        "name": "UTI pathogens",
        "aliases": [],
        "category": "microbiology",
        "summary": "E. coli causes about 80 percent of community UTIs. Others: Staph saprophyticus (young women), Klebsiella, Proteus (struvite stones, urea splitter), Enterococcus, and resistant organisms in healthcare-associated infection.",
    },
    {
        "name": "Meningitis pathogens by age",
        "aliases": [],
        "category": "microbiology",
        "summary": "Neonates: GBS, E. coli, Listeria. Children and young adults: N. meningitidis, S. pneumoniae. Older adults: S. pneumoniae, Listeria. Immunocompromised: Cryptococcus, Listeria, gram-negatives.",
    },
    {
        "name": "GI pathogens with bloody diarrhoea",
        "aliases": [],
        "category": "microbiology",
        "summary": "Shigella, EHEC (O157:H7, Shiga toxin, risk of HUS), Salmonella, Campylobacter, Entamoeba histolytica, C. difficile (toxin-mediated colitis). Differs from watery diarrhoea pathogens (Vibrio, ETEC, viruses).",
    },
    {
        "name": "Sexually transmitted pathogens",
        "aliases": [],
        "category": "microbiology",
        "summary": "Bacteria: Neisseria gonorrhoeae, Chlamydia trachomatis, Treponema pallidum, Haemophilus ducreyi. Viruses: HIV, HSV, HPV, hepatitis B. Protozoa: Trichomonas. Parasites: Phthirus pubis.",
    },
    {
        "name": "Mycobacterium tuberculosis",
        "aliases": ["TB", "Mtb"],
        "category": "microbiology",
        "summary": "Acid-fast, aerobic, slow-growing rod. Inhaled, contained in granulomas. Latent infection in about a quarter of the world. Treatment: RIPE (rifampin, isoniazid, pyrazinamide, ethambutol) intensive phase then continuation.",
    },
    {
        "name": "Candida species",
        "aliases": [],
        "category": "microbiology",
        "summary": "Commensal yeast, opportunistic in immunosuppression, diabetes, broad-spectrum antibiotics, indwelling lines. Forms pseudohyphae on tissue. Treated with azoles (mucosal) or echinocandins (invasive).",
    },
    {
        "name": "Aspergillus species",
        "aliases": [],
        "category": "microbiology",
        "summary": "Septate, acute-angle branching mould. Causes invasive aspergillosis in neutropenic patients, ABPA in asthma and cystic fibrosis, and aspergilloma in pre-existing cavities. Treated with voriconazole, isavuconazole, or amphotericin.",
    },
    {
        "name": "Pneumocystis jirovecii",
        "aliases": ["PJP", "PCP"],
        "category": "microbiology",
        "summary": "Atypical fungus causing pneumonia in HIV (CD4 below 200) and other immunosuppressed patients. Bilateral interstitial infiltrates and severe hypoxaemia. Treated with high-dose cotrimoxazole, plus steroids if PaO2 below 70 mmHg.",
    },
    {
        "name": "Plasmodium species",
        "aliases": ["Malaria"],
        "category": "microbiology",
        "summary": "Protozoa transmitted by female Anopheles mosquitoes. P. falciparum causes severe disease; P. vivax and ovale have dormant liver hypnozoites requiring primaquine. Cyclical fevers, haemolytic anaemia, splenomegaly.",
    },
    {
        "name": "Influenza virus",
        "aliases": [],
        "category": "microbiology",
        "summary": "Segmented negative-sense RNA orthomyxovirus. Surface haemagglutinin and neuraminidase drive antigenic drift (point mutation, seasonal) and shift (reassortment, pandemic). Treated with oseltamivir within 48 hours of onset.",
    },
    {
        "name": "Herpes virus family",
        "aliases": [],
        "category": "microbiology",
        "summary": "Double-stranded DNA viruses establishing lifelong latency. Includes HSV-1, HSV-2, VZV, EBV, CMV, HHV-6, HHV-8 (Kaposi). Reactivation common in immunosuppression. Aciclovir for HSV/VZV; ganciclovir for CMV.",
    },
    {
        "name": "HIV virology",
        "aliases": [],
        "category": "microbiology",
        "summary": "Retrovirus with two single-stranded RNA copies, reverse transcriptase, integrase, and protease. Binds CD4 plus CCR5 (early) or CXCR4 (late). Treated with combination ART targeting multiple steps in the replication cycle.",
    },
    {
        "name": "Hepatitis virus comparison",
        "aliases": [],
        "category": "microbiology",
        "summary": "HepA, E: faecal-oral, self-limited (E severe in pregnancy). HepB: DNA, blood/sexual/vertical, can be chronic, oncogenic. HepC: RNA, blood, often chronic, curable with direct-acting antivirals. HepD: requires HepB coinfection.",
    },
    {
        "name": "Sterilisation vs disinfection",
        "aliases": [],
        "category": "microbiology",
        "summary": "Sterilisation kills all microbes including spores (autoclave, ethylene oxide, gamma radiation). Disinfection reduces pathogen burden on inanimate surfaces but may not kill spores (bleach, alcohol, glutaraldehyde). Antisepsis applies to living tissue.",
    },

    # ───────────────────────── IMMUNOLOGY ─────────────────────────
    {
        "name": "Innate immunity",
        "aliases": [],
        "category": "immunology",
        "summary": "Non-specific, rapid (minutes to hours), no memory. Includes barriers, phagocytes (neutrophils, macrophages), NK cells, complement, and pattern recognition receptors. Recognises PAMPs and DAMPs.",
    },
    {
        "name": "Adaptive immunity",
        "aliases": [],
        "category": "immunology",
        "summary": "Specific, slower (days), with memory. Includes T cells (cellular) and B cells/antibodies (humoral). Diversity from V(D)J recombination. Memory generates faster, larger secondary responses on re-exposure.",
    },
    {
        "name": "Pattern recognition receptors",
        "aliases": ["PRRs", "TLRs"],
        "category": "immunology",
        "summary": "Recognise conserved microbial patterns. Toll-like receptors are surface or endosomal (e.g., TLR4 binds LPS, TLR3 binds dsRNA). Activation drives cytokine production via NF-kB and IRF pathways.",
    },
    {
        "name": "MHC class I",
        "aliases": ["HLA-A, B, C"],
        "category": "immunology",
        "summary": "Expressed on all nucleated cells. Presents endogenous (cytoplasmic) peptides to CD8 T cells via TAP-loaded proteasomal peptides. Down-regulation by tumours or viruses triggers NK cell killing (missing self).",
    },
    {
        "name": "MHC class II",
        "aliases": ["HLA-DR, DP, DQ"],
        "category": "immunology",
        "summary": "Expressed on professional antigen-presenting cells (dendritic cells, macrophages, B cells). Presents exogenous (endosomal) peptides to CD4 T cells. Defects cause bare lymphocyte syndrome.",
    },
    {
        "name": "T cell subsets",
        "aliases": [],
        "category": "immunology",
        "summary": "CD4 helpers: Th1 (IFN-gamma, intracellular pathogens), Th2 (IL-4/5/13, parasites and allergy), Th17 (IL-17, mucosal bacteria and fungi), Treg (immune tolerance via TGF-beta, IL-10). CD8 cytotoxic: kill infected/transformed cells via perforin and granzyme.",
    },
    {
        "name": "B cell activation",
        "aliases": [],
        "category": "immunology",
        "summary": "BCR binds antigen, internalises and presents on MHC II to a CD4 T helper, which provides CD40L and cytokines. Drives class switching, somatic hypermutation, and differentiation into plasma cells or memory B cells.",
    },
    {
        "name": "Immunoglobulin classes",
        "aliases": ["Ig classes"],
        "category": "immunology",
        "summary": "IgG (most abundant, crosses placenta, opsonisation), IgM (first responder, pentamer, complement activator), IgA (mucosal, dimer with J chain), IgE (allergy, parasites, mast cell binding), IgD (B cell receptor).",
    },
    {
        "name": "Complement classical pathway",
        "aliases": [],
        "category": "immunology",
        "summary": "Triggered by antibody-antigen complexes (IgG or IgM) binding C1. Cleaves C4 then C2 to form C3 convertase. Leads to opsonisation (C3b), inflammation (C3a, C5a), and MAC formation (C5b-9).",
    },
    {
        "name": "Complement alternative pathway",
        "aliases": [],
        "category": "immunology",
        "summary": "Spontaneous C3 hydrolysis on microbial surfaces, amplified in the absence of host regulators. Important early innate defence against gram-negative bacteria.",
    },
    {
        "name": "Complement lectin pathway",
        "aliases": [],
        "category": "immunology",
        "summary": "Mannose-binding lectin recognises microbial mannose, activates MASP enzymes that cleave C4 and C2, joining the classical pathway. MBL deficiency increases susceptibility to encapsulated organisms.",
    },
    {
        "name": "Cytokines overview",
        "aliases": [],
        "category": "immunology",
        "summary": "IL-1, IL-6, TNF-alpha: acute phase, fever. IL-2: T cell growth. IL-4, IL-13: Th2/IgE. IL-5: eosinophils. IL-10: anti-inflammatory. IFN-alpha/beta: antiviral. IFN-gamma: macrophage activation, intracellular pathogens.",
    },
    {
        "name": "Hypersensitivity type I",
        "aliases": ["Immediate hypersensitivity"],
        "category": "immunology",
        "summary": "IgE-mediated mast cell and basophil degranulation. Allergens crosslink surface IgE, releasing histamine, tryptase, leukotrienes. Onset minutes. Anaphylaxis, allergic rhinitis, asthma.",
    },
    {
        "name": "Hypersensitivity type II",
        "aliases": ["Antibody-mediated"],
        "category": "immunology",
        "summary": "IgG or IgM antibodies bind cell-surface antigens, causing complement activation, opsonisation, or ADCC. Examples: autoimmune haemolytic anaemia, transfusion reactions, Goodpasture, myasthenia gravis, Graves.",
    },
    {
        "name": "Hypersensitivity type III",
        "aliases": ["Immune complex"],
        "category": "immunology",
        "summary": "Antibody-antigen complexes deposit in vessels and tissues, activating complement and inflammation. Examples: serum sickness, post-streptococcal glomerulonephritis, SLE, polyarteritis nodosa.",
    },
    {
        "name": "Hypersensitivity type IV",
        "aliases": ["Delayed-type", "Cell-mediated"],
        "category": "immunology",
        "summary": "T cell-mediated, peaks 48 to 72 hours. CD4 (granulomas in TB, contact dermatitis) and CD8 (graft rejection, Stevens-Johnson, drug reactions). No antibody involved.",
    },
    {
        "name": "Central tolerance",
        "aliases": [],
        "category": "immunology",
        "summary": "Removes self-reactive lymphocytes during development. T cells in thymus undergo positive selection (recognise self MHC) and negative selection (delete strongly self-reactive). AIRE drives ectopic self-antigen expression; defect causes APECED.",
    },
    {
        "name": "Peripheral tolerance",
        "aliases": [],
        "category": "immunology",
        "summary": "Controls self-reactive lymphocytes that escape thymic selection. Mechanisms: anergy (signal 1 without signal 2), Treg suppression, activation-induced cell death, immune privilege (eye, brain).",
    },
    {
        "name": "Antigen presentation",
        "aliases": [],
        "category": "immunology",
        "summary": "Dendritic cells take up antigen peripherally, mature, migrate to draining lymph nodes, and present to naive T cells with co-stimulation (CD80/86 to CD28). Without signal 2, T cells become anergic.",
    },
    {
        "name": "Vaccine types",
        "aliases": [],
        "category": "immunology",
        "summary": "Live attenuated (MMR, varicella, BCG): strong, durable, but contraindicated in pregnancy and severe immunosuppression. Inactivated (rabies, polio Salk). Subunit (HepB, HPV). Toxoid (diphtheria, tetanus). Conjugate (Hib, Men-C). mRNA (COVID-19).",
    },
    {
        "name": "Natural killer cells",
        "aliases": ["NK cells"],
        "category": "immunology",
        "summary": "Innate lymphocytes that kill virus-infected and tumour cells lacking MHC I (missing self). Release perforin and granzyme; produce IFN-gamma. Regulated by activating and inhibitory KIR receptors.",
    },
    {
        "name": "Acute phase response",
        "aliases": [],
        "category": "immunology",
        "summary": "Hepatic production of acute phase proteins (CRP, fibrinogen, ferritin, hepcidin) and negative reactants (albumin, transferrin) driven by IL-6, IL-1, and TNF-alpha. Underlies the systemic features of inflammation.",
    },

    # ───────────────────────── PATHOLOGY ─────────────────────────
    {
        "name": "Cell injury",
        "aliases": [],
        "category": "pathology",
        "summary": "Sequence: reversible (cell swelling, fatty change) progresses to irreversible (membrane damage, mitochondrial dysfunction, lysosomal leak) and cell death. Final common pathways involve ATP depletion, Ca2+ accumulation, ROS, and membrane damage.",
    },
    {
        "name": "Coagulative necrosis",
        "aliases": [],
        "category": "pathology",
        "summary": "Architecture preserved with ghost outlines for days. Caused by ischaemia in solid organs (heart, kidney, spleen). Denatured proteins resist proteolysis until inflammatory cells clear the debris.",
    },
    {
        "name": "Liquefactive necrosis",
        "aliases": [],
        "category": "pathology",
        "summary": "Tissue dissolves into viscous fluid. Seen in brain infarction (no dense stroma) and bacterial abscesses (neutrophil enzymes). Forms a cyst-like cavity in the brain.",
    },
    {
        "name": "Caseous necrosis",
        "aliases": [],
        "category": "pathology",
        "summary": "Cheese-like, amorphous granular debris surrounded by granulomatous inflammation. Classic for tuberculosis but also seen in fungal infections.",
    },
    {
        "name": "Fat necrosis",
        "aliases": [],
        "category": "pathology",
        "summary": "Lipase from pancreatitis breaks down peri-pancreatic fat; free fatty acids saponify with calcium (chalky white deposits). Traumatic fat necrosis (breast, after trauma) is a non-enzymatic variant.",
    },
    {
        "name": "Fibrinoid necrosis",
        "aliases": [],
        "category": "pathology",
        "summary": "Bright eosinophilic deposition of fibrin and immune complexes in vessel walls. Seen in malignant hypertension, vasculitis, and pre-eclampsia.",
    },
    {
        "name": "Gangrenous necrosis",
        "aliases": [],
        "category": "pathology",
        "summary": "Necrosis of a limb. Dry: coagulative, ischaemic. Wet: liquefactive plus infection, foul-smelling. Gas gangrene: Clostridial myonecrosis with gas production.",
    },
    {
        "name": "Apoptosis",
        "aliases": [],
        "category": "pathology",
        "summary": "Programmed cell death. Intrinsic pathway via mitochondrial cytochrome c release and caspase-9 (response to DNA damage, growth factor withdrawal); extrinsic via Fas/TNF receptors and caspase-8. Cells shrink, nuclei fragment, no inflammation.",
    },
    {
        "name": "Necroptosis",
        "aliases": [],
        "category": "pathology",
        "summary": "Programmed cell death with necrotic morphology. Mediated by RIP1, RIP3, and MLKL. Important when apoptosis is blocked (e.g., viral infection). Releases DAMPs and triggers inflammation.",
    },
    {
        "name": "Pyroptosis",
        "aliases": [],
        "category": "pathology",
        "summary": "Inflammasome-mediated cell death driven by caspase-1 cleaving gasdermin D. Releases IL-1 beta and IL-18. Important in defending against intracellular bacteria.",
    },
    {
        "name": "Ferroptosis",
        "aliases": [],
        "category": "pathology",
        "summary": "Iron-dependent regulated cell death from lipid peroxidation. Inhibited by GPX4 and glutathione. Implicated in neurodegeneration, ischaemia-reperfusion, and cancer therapy responses.",
    },
    {
        "name": "Acute inflammation",
        "aliases": [],
        "category": "pathology",
        "summary": "Rapid response (minutes to days) with vasodilation, increased permeability, and neutrophil emigration. Cardinal signs: rubor, tumor, calor, dolor, functio laesa. Mediated by histamine, bradykinin, prostaglandins, leukotrienes, chemokines.",
    },
    {
        "name": "Chronic inflammation",
        "aliases": [],
        "category": "pathology",
        "summary": "Persistent inflammation with macrophages, lymphocytes, plasma cells, and tissue destruction plus repair (fibrosis, angiogenesis). Caused by persistent infection, autoimmunity, or chronic exposure to a toxic agent.",
    },
    {
        "name": "Granuloma",
        "aliases": [],
        "category": "pathology",
        "summary": "Focal collection of activated macrophages (epithelioid cells) with multinucleated giant cells, sometimes lymphocytes and central necrosis. Caseating: TB, fungal. Non-caseating: sarcoidosis, Crohn, foreign body, berylliosis.",
    },
    {
        "name": "Leukocyte extravasation",
        "aliases": [],
        "category": "pathology",
        "summary": "Steps: margination, rolling (selectins), firm adhesion (integrins binding ICAM/VCAM), transmigration through endothelium, chemotaxis through tissue. LAD I (CD18 deficiency) impairs firm adhesion.",
    },
    {
        "name": "Resolution of inflammation",
        "aliases": [],
        "category": "pathology",
        "summary": "Outcomes: complete resolution (mild injury, intact stroma), scarring (severe injury, fibrosis), abscess formation, or progression to chronic inflammation. Specialised pro-resolving mediators (lipoxins, resolvins) actively terminate inflammation.",
    },
    {
        "name": "Wound healing",
        "aliases": [],
        "category": "pathology",
        "summary": "Haemostasis (immediate), inflammation (1 to 3 days), proliferation (granulation tissue, days to weeks), remodelling (weeks to months, type III collagen replaced by type I). Tensile strength reaches about 80 percent by 3 months.",
    },
    {
        "name": "Hyperplasia",
        "aliases": [],
        "category": "pathology",
        "summary": "Increase in cell number. Physiologic (hormonal: uterus in pregnancy; compensatory: liver after partial hepatectomy) or pathologic (endometrial hyperplasia from unopposed oestrogen). Some pathologic hyperplasias predispose to neoplasia.",
    },
    {
        "name": "Hypertrophy",
        "aliases": [],
        "category": "pathology",
        "summary": "Increase in cell size, often in tissues with limited proliferative capacity (cardiac, skeletal muscle). Physiologic (exercise) or pathologic (hypertensive heart). Often coexists with hyperplasia in tissues that can divide.",
    },
    {
        "name": "Atrophy",
        "aliases": [],
        "category": "pathology",
        "summary": "Decrease in cell size or number. Causes: disuse, denervation, loss of hormonal stimulation, reduced blood flow, ageing, pressure, poor nutrition. Involves ubiquitin-proteasome and autophagy pathways.",
    },
    {
        "name": "Metaplasia",
        "aliases": [],
        "category": "pathology",
        "summary": "Reversible replacement of one differentiated cell type with another. Examples: squamous metaplasia of bronchial epithelium in smokers, columnar metaplasia in Barrett oesophagus. May predispose to dysplasia and cancer.",
    },
    {
        "name": "Dysplasia",
        "aliases": [],
        "category": "pathology",
        "summary": "Disordered growth with cellular atypia and architectural abnormality, but confined to the epithelium. Reversible early; high-grade dysplasia frequently progresses to invasive cancer.",
    },
    {
        "name": "Neoplasia",
        "aliases": [],
        "category": "pathology",
        "summary": "Autonomous, clonal cell growth. Benign tumours are well-differentiated, encapsulated, slow-growing, non-invasive. Malignant tumours show anaplasia, invasion, and metastasis. Hallmarks include sustained proliferation, evasion of apoptosis, angiogenesis.",
    },
    {
        "name": "Hallmarks of cancer",
        "aliases": [],
        "category": "pathology",
        "summary": "Hanahan and Weinberg framework: sustained proliferation, evasion of growth suppressors, resisting cell death, replicative immortality, angiogenesis, invasion and metastasis. Later additions: deregulated metabolism, evading immune destruction, genome instability, tumour-promoting inflammation.",
    },
    {
        "name": "Tumour markers basics",
        "aliases": [],
        "category": "pathology",
        "summary": "AFP: hepatocellular and yolk sac. CEA: colorectal, monitoring. CA 19-9: pancreatic. CA 125: ovarian. PSA: prostate. hCG: gestational trophoblastic, testicular. Calcitonin: medullary thyroid. Most are imperfectly sensitive or specific; mainly used for monitoring.",
    },
    {
        "name": "Apoptosis vs necrosis",
        "aliases": [],
        "category": "pathology",
        "summary": "Apoptosis: programmed, ATP-dependent, single cells, intact membranes, no inflammation, cell shrinkage. Necrosis: pathologic, cell swelling, membrane rupture, content release, marked inflammation.",
    },
    {
        "name": "Reperfusion injury",
        "aliases": [],
        "category": "pathology",
        "summary": "Paradoxical damage when blood flow returns to ischaemic tissue. Reactive oxygen species, calcium overload, mitochondrial permeability transition pore opening, and complement activation worsen injury beyond ischaemia alone.",
    },
    {
        "name": "Amyloid",
        "aliases": [],
        "category": "pathology",
        "summary": "Misfolded protein aggregates with beta-pleated sheet structure that show apple-green birefringence under polarised light with Congo red. AL (light chain, myeloma), AA (chronic inflammation), ATTR (transthyretin, familial or wild-type cardiac).",
    },
    {
        "name": "Calcification (dystrophic vs metastatic)",
        "aliases": [],
        "category": "pathology",
        "summary": "Dystrophic: in damaged or necrotic tissue with normal calcium (atherosclerosis, old TB granulomas). Metastatic: in normal tissue due to hypercalcaemia (hyperparathyroidism, chronic kidney disease, vitamin D toxicity).",
    },
    {
        "name": "Atherosclerosis pathogenesis",
        "aliases": [],
        "category": "pathology",
        "summary": "Endothelial injury, LDL infiltration and oxidation, macrophage uptake forming foam cells, smooth muscle migration, fibrous cap formation. Plaque rupture exposes thrombogenic core, triggering acute thrombotic events.",
    },
    {
        "name": "Hypoxia vs ischaemia",
        "aliases": [],
        "category": "pathology",
        "summary": "Hypoxia is reduced oxygen delivery to tissue (various causes including anaemia, low PaO2). Ischaemia is reduced blood flow, which also impairs delivery of substrates and removal of waste; tends to cause faster injury than pure hypoxia.",
    },
    {
        "name": "Free radicals and oxidative stress",
        "aliases": ["ROS"],
        "category": "pathology",
        "summary": "Reactive oxygen species (superoxide, H2O2, hydroxyl radical) damage lipids, proteins, and DNA. Generated by mitochondria, neutrophils, ionising radiation, reperfusion. Defences: superoxide dismutase, catalase, glutathione, vitamins C and E.",
    },
    {
        "name": "Edema mechanisms",
        "aliases": [],
        "category": "pathology",
        "summary": "Causes per Starling: increased hydrostatic pressure (heart failure, venous obstruction), decreased oncotic pressure (nephrotic syndrome, liver disease, malnutrition), lymphatic obstruction (filariasis, postsurgical), increased capillary permeability (inflammation), sodium retention.",
    },
    {
        "name": "Shock classification",
        "aliases": [],
        "category": "pathology",
        "summary": "Hypovolaemic, cardiogenic, obstructive (PE, tamponade, tension pneumothorax), distributive (septic, anaphylactic, neurogenic). Pre-load, contractility, after-load, and SVR profiles distinguish them and guide management.",
    },
    {
        "name": "Embolism types",
        "aliases": [],
        "category": "pathology",
        "summary": "Thromboembolic (most common), fat (long bone fracture, 1 to 3 days later), air (line insertion, decompression), amniotic fluid (peripartum, DIC), septic, tumour, foreign body. Site of impact depends on origin and circulation.",
    },
    {
        "name": "Thrombus vs clot",
        "aliases": [],
        "category": "pathology",
        "summary": "Thrombus forms in flowing blood, laminated (lines of Zahn), attached to vessel wall. Postmortem clot is gelatinous, unlayered, not attached. Distinction useful at autopsy.",
    },

    # ───────────────────────── PHARMACOLOGY ─────────────────────────
    {
        "name": "Pharmacokinetics",
        "aliases": ["PK"],
        "category": "pharmacology",
        "summary": "What the body does to the drug: absorption, distribution, metabolism, excretion. Determines plasma concentration over time. Quantitative parameters include bioavailability, volume of distribution, clearance, and half-life.",
    },
    {
        "name": "Pharmacodynamics",
        "aliases": ["PD"],
        "category": "pharmacology",
        "summary": "What the drug does to the body: relationship between drug concentration and effect. Includes potency (EC50), efficacy (Emax), receptor binding kinetics, and tolerance.",
    },
    {
        "name": "Bioavailability",
        "aliases": ["F"],
        "category": "pharmacology",
        "summary": "Fraction of administered drug reaching systemic circulation in unchanged form. IV is 1.0 by definition; oral is reduced by incomplete absorption and first-pass metabolism. Determined by area under the curve compared to IV.",
    },
    {
        "name": "First-pass metabolism",
        "aliases": [],
        "category": "pharmacology",
        "summary": "Metabolism in the gut wall and liver before a drug reaches the systemic circulation. Reduces oral bioavailability (e.g., morphine, propranolol, GTN). Bypassed by IV, sublingual, transdermal, and rectal routes.",
    },
    {
        "name": "Volume of distribution",
        "aliases": ["Vd"],
        "category": "pharmacology",
        "summary": "Apparent volume into which a drug appears to distribute, calculated as dose divided by initial plasma concentration. Low Vd (about 5 L): plasma-bound (warfarin). High Vd: tissue-bound (digoxin, amiodarone). Determines loading dose.",
    },
    {
        "name": "Drug clearance",
        "aliases": ["CL", "Pharmacokinetic clearance"],
        "category": "pharmacology",
        "summary": "Volume of plasma cleared of drug per unit time. Determined by organ blood flow and extraction ratio. Determines maintenance dose at steady state. Renal clearance combines filtration, secretion, and reabsorption.",
    },
    {
        "name": "Half-life",
        "aliases": ["t1/2"],
        "category": "pharmacology",
        "summary": "Time for plasma concentration to fall by half. Equal to 0.693 times Vd divided by clearance. Steady state is reached in about 4 to 5 half-lives.",
    },
    {
        "name": "Zero vs first-order kinetics",
        "aliases": [],
        "category": "pharmacology",
        "summary": "First-order: constant fraction eliminated per unit time (most drugs). Zero-order: constant amount eliminated per unit time, occurs when enzymes are saturated (alcohol, high-dose phenytoin, high-dose aspirin).",
    },
    {
        "name": "Loading dose vs maintenance dose",
        "aliases": [],
        "category": "pharmacology",
        "summary": "Loading dose equals target concentration times Vd; used to rapidly achieve therapeutic levels. Maintenance dose equals target concentration times clearance; used to balance ongoing elimination.",
    },
    {
        "name": "Phase I metabolism",
        "aliases": [],
        "category": "pharmacology",
        "summary": "Functionalisation reactions (oxidation, reduction, hydrolysis), mostly by CYP450 enzymes. Adds or unmasks a functional group, often producing an active or toxic metabolite. CYP3A4 metabolises the majority of drugs.",
    },
    {
        "name": "Phase II metabolism",
        "aliases": [],
        "category": "pharmacology",
        "summary": "Conjugation reactions (glucuronidation, sulfation, acetylation, glutathione conjugation) producing polar, water-soluble metabolites for excretion. Usually inactivates the drug; UGT mutations underlie Gilbert's syndrome.",
    },
    {
        "name": "CYP450 induction and inhibition",
        "aliases": [],
        "category": "pharmacology",
        "summary": "Inducers (rifampicin, phenytoin, carbamazepine, St John's wort, smoking) increase metabolism and lower levels. Inhibitors (grapefruit juice, macrolides, azoles, ritonavir) raise levels. Important source of drug-drug interactions.",
    },
    {
        "name": "Therapeutic index",
        "aliases": ["TI"],
        "category": "pharmacology",
        "summary": "Ratio of toxic dose 50 to effective dose 50. Narrow therapeutic index drugs (warfarin, digoxin, lithium, theophylline, phenytoin, aminoglycosides) require monitoring. Wider index is safer.",
    },
    {
        "name": "Agonist vs antagonist",
        "aliases": [],
        "category": "pharmacology",
        "summary": "Agonist binds and activates receptor (full or partial). Antagonist binds without activating, blocking endogenous ligand. Competitive antagonists shift dose-response right (overcome by more agonist); non-competitive lower maximum effect.",
    },
    {
        "name": "Partial agonist",
        "aliases": [],
        "category": "pharmacology",
        "summary": "Binds and activates the receptor but with submaximal efficacy regardless of dose. In the presence of a full agonist, behaves like an antagonist. Examples: buprenorphine (mu opioid), aripiprazole (D2), pindolol (beta).",
    },
    {
        "name": "Inverse agonist",
        "aliases": [],
        "category": "pharmacology",
        "summary": "Binds and reduces receptor activity below baseline (suppresses constitutive activity). Distinct from a neutral antagonist, which only blocks an agonist. Examples: some H1 antihistamines, naloxone in some preparations.",
    },
    {
        "name": "Tachyphylaxis",
        "aliases": [],
        "category": "pharmacology",
        "summary": "Rapid loss of drug effect with repeated dosing over short intervals, often via receptor desensitisation or transmitter depletion. Examples: nitrates, sympathomimetics, repeated nicotine.",
    },
    {
        "name": "G protein-coupled receptors",
        "aliases": ["GPCR"],
        "category": "pharmacology",
        "summary": "Seven-transmembrane receptors coupled to heterotrimeric G proteins. Gs: increases cAMP via adenylate cyclase. Gi: decreases cAMP. Gq: activates phospholipase C, raises IP3 and DAG, Ca2+ release. Most drug targets in clinical use.",
    },
    {
        "name": "Ion channel receptors",
        "aliases": ["Ligand-gated ion channels"],
        "category": "pharmacology",
        "summary": "Ligand binding directly opens an ion pore. Examples: nicotinic acetylcholine, GABA-A, glycine, NMDA, 5-HT3. Rapid effect (milliseconds), important in neurotransmission.",
    },
    {
        "name": "Tyrosine kinase receptors",
        "aliases": [],
        "category": "pharmacology",
        "summary": "Single-transmembrane receptors that dimerise on ligand binding and autophosphorylate. Activate Ras-MAPK and PI3K-Akt pathways. Examples: insulin, EGFR, HER2, VEGFR. Targeted by many oncology drugs ending in -tinib.",
    },
    {
        "name": "Nuclear receptors",
        "aliases": [],
        "category": "pharmacology",
        "summary": "Intracellular receptors that bind lipid-soluble ligands (steroids, thyroid hormone, vitamin D, retinoids) and act as transcription factors. Slow onset (hours), durable effects.",
    },
    {
        "name": "Drug receptor desensitisation",
        "aliases": [],
        "category": "pharmacology",
        "summary": "Reduction in receptor responsiveness with continued exposure. Mechanisms: receptor phosphorylation (uncoupling), internalisation, down-regulation. Underlies tolerance and tachyphylaxis.",
    },
    {
        "name": "Therapeutic drug monitoring",
        "aliases": ["TDM"],
        "category": "pharmacology",
        "summary": "Measuring drug concentrations to optimise dosing. Useful for narrow-index drugs (vancomycin, gentamicin, digoxin, lithium, phenytoin, tacrolimus). Timing matters: trough levels typically guide dosing.",
    },
    {
        "name": "Receptor reserve",
        "aliases": ["Spare receptors"],
        "category": "pharmacology",
        "summary": "When maximal response occurs with less than full receptor occupancy. Means EC50 is lower than Kd. Provides amplification and resilience to partial receptor loss.",
    },
    {
        "name": "Steady state concentration",
        "aliases": [],
        "category": "pharmacology",
        "summary": "Reached when rate of drug input equals rate of elimination, typically after 4 to 5 half-lives. Independent of dosing interval (only depends on average input rate and clearance).",
    },
    {
        "name": "Renal vs hepatic elimination",
        "aliases": [],
        "category": "pharmacology",
        "summary": "Drug clearance route influences dosing in organ failure. Renally cleared drugs (aminoglycosides, digoxin, lithium) need adjustment in CKD. Hepatically cleared drugs may need adjustment in liver disease, especially those with high extraction ratio.",
    },
    {
        "name": "Drug-drug interactions",
        "aliases": [],
        "category": "pharmacology",
        "summary": "Pharmacokinetic (absorption, distribution, metabolism, excretion) or pharmacodynamic (additive, synergistic, antagonistic). High-yield mechanisms: CYP3A4 inhibition, P-glycoprotein, protein binding displacement, serotonin syndrome with combined serotonergics.",
    },
    {
        "name": "Cholinergic receptors",
        "aliases": [],
        "category": "pharmacology",
        "summary": "Nicotinic (ion channel, autonomic ganglia, NMJ, CNS) and muscarinic (GPCR, M1 to M5). M1 CNS, M2 cardiac (Gi, slows HR), M3 smooth muscle and glands (Gq). Atropine blocks all muscarinic; pancuronium blocks Nm.",
    },
    {
        "name": "Adrenergic receptors",
        "aliases": [],
        "category": "pharmacology",
        "summary": "Alpha-1 (Gq, vasoconstriction, pupillary dilation), alpha-2 (Gi, presynaptic inhibition, CNS sedation), beta-1 (Gs, cardiac, renin release), beta-2 (Gs, bronchodilation, vasodilation), beta-3 (Gs, lipolysis, bladder relaxation).",
    },
    {
        "name": "Loading dose adjustment",
        "aliases": [],
        "category": "pharmacology",
        "summary": "Loading dose depends on Vd, not on clearance. Therefore not reduced for renal or hepatic failure unless Vd is altered. Maintenance dose, in contrast, is reduced when clearance falls.",
    },

    # ───────────────────────── ANATOMY ─────────────────────────
    {
        "name": "Circle of Willis",
        "aliases": [],
        "category": "anatomy",
        "summary": "Anastomotic ring at the base of the brain formed by anterior communicating, anterior cerebral, internal carotid, posterior communicating, and posterior cerebral arteries. Provides collateral flow; site of berry aneurysms (often anterior communicating).",
    },
    {
        "name": "Brachial plexus",
        "aliases": [],
        "category": "anatomy",
        "summary": "C5 to T1 nerve roots forming trunks (upper, middle, lower), divisions, cords (lateral, posterior, medial), and terminal branches (musculocutaneous, axillary, radial, median, ulnar). Erb's palsy: upper trunk. Klumpke: lower trunk.",
    },
    {
        "name": "Lumbosacral plexus",
        "aliases": ["Lumbar plexus", "Sacral plexus"],
        "category": "anatomy",
        "summary": "Lumbar plexus (L1 to L4): iliohypogastric, ilioinguinal, genitofemoral, lateral femoral cutaneous, femoral, obturator. Sacral plexus (L4 to S4): sciatic (tibial and common peroneal), superior and inferior gluteal, pudendal.",
    },
    {
        "name": "Cranial nerves",
        "aliases": ["CN I to XII"],
        "category": "anatomy",
        "summary": "I olfactory, II optic, III oculomotor, IV trochlear (superior oblique), V trigeminal, VI abducens (lateral rectus), VII facial, VIII vestibulocochlear, IX glossopharyngeal, X vagus, XI accessory (SCM, trapezius), XII hypoglossal (tongue).",
    },
    {
        "name": "Vagus nerve",
        "aliases": ["CN X"],
        "category": "anatomy",
        "summary": "Mixed nerve with extensive thoracoabdominal distribution. Parasympathetic to heart, lungs, GI to splenic flexure. Sensory to larynx, pharynx, and external auditory canal. Motor to most pharyngeal and laryngeal muscles.",
    },
    {
        "name": "Hepatic portal vein",
        "aliases": ["Portal vein"],
        "category": "anatomy",
        "summary": "Drains GI tract, spleen, pancreas, and gallbladder to liver. Formed by union of splenic and superior mesenteric veins. Portal hypertension causes oesophageal varices, caput medusae, anorectal varices via portosystemic anastomoses.",
    },
    {
        "name": "Coronary artery anatomy",
        "aliases": [],
        "category": "anatomy",
        "summary": "Right coronary (RCA): RV, inferior LV (in right-dominant 85 percent), AV node, SA node. Left coronary: LAD (anterior LV, septum, apex), circumflex (lateral LV). Dominance is defined by which artery gives the posterior descending.",
    },
    {
        "name": "Bronchopulmonary segments",
        "aliases": [],
        "category": "anatomy",
        "summary": "Functional and surgical lung subdivisions, each with its own segmental bronchus and artery (vein lies between segments). Right lung has 10 segments, left has 8 to 10.",
    },
    {
        "name": "Mediastinum",
        "aliases": [],
        "category": "anatomy",
        "summary": "Region between the lungs. Superior: thymus, great vessels, trachea, oesophagus. Inferior divided into anterior (thymus), middle (heart, pericardium), posterior (oesophagus, descending aorta, vagi, thoracic duct, azygos).",
    },
    {
        "name": "Diaphragm openings",
        "aliases": [],
        "category": "anatomy",
        "summary": "T8: IVC and right phrenic nerve. T10: oesophagus and vagi. T12: aorta, thoracic duct, azygos vein. Mnemonic: I 8 (ate) 10 EGGS at 12.",
    },
    {
        "name": "Femoral triangle",
        "aliases": [],
        "category": "anatomy",
        "summary": "Boundaries: inguinal ligament (superior), sartorius (lateral), adductor longus (medial). Contents from lateral to medial: femoral nerve, artery, vein, empty space, lymphatics (NAVEL).",
    },
    {
        "name": "Inguinal canal",
        "aliases": [],
        "category": "anatomy",
        "summary": "Oblique passage through the lower abdominal wall. Contains spermatic cord (men) or round ligament (women). Direct hernias: medial to inferior epigastric vessels through Hesselbach's triangle. Indirect hernias: lateral, through deep ring.",
    },
    {
        "name": "Carpal tunnel",
        "aliases": [],
        "category": "anatomy",
        "summary": "Passage on the volar wrist bounded by carpal bones (floor) and flexor retinaculum (roof). Transmits the median nerve and nine flexor tendons (FDS x4, FDP x4, FPL). Compression causes carpal tunnel syndrome.",
    },
    {
        "name": "Anatomical snuffbox",
        "aliases": [],
        "category": "anatomy",
        "summary": "Triangular hollow on the radial wrist bounded by APL/EPB (lateral) and EPL (medial). Contains the radial artery; floor is the scaphoid (tenderness suggests scaphoid fracture).",
    },
    {
        "name": "Recurrent laryngeal nerves",
        "aliases": ["RLN"],
        "category": "anatomy",
        "summary": "Branches of the vagus that supply intrinsic laryngeal muscles (except cricothyroid). Left hooks around the aortic arch (vulnerable in thoracic surgery, aortic aneurysm, mediastinal disease). Right hooks around the right subclavian.",
    },
    {
        "name": "Thoracic duct",
        "aliases": [],
        "category": "anatomy",
        "summary": "Largest lymphatic channel. Begins at cisterna chyli, ascends through aortic hiatus, drains into the left subclavian-internal jugular junction. Carries most body lymph; injury causes chylothorax.",
    },
    {
        "name": "Hesselbach's triangle",
        "aliases": [],
        "category": "anatomy",
        "summary": "Boundaries: rectus abdominis (medial), inferior epigastric vessels (lateral), inguinal ligament (inferior). Site of direct inguinal hernias.",
    },
    {
        "name": "Anatomy of the eye",
        "aliases": [],
        "category": "anatomy",
        "summary": "Three layers: outer (sclera and cornea), middle uvea (iris, ciliary body, choroid), inner retina. Anterior segment filled with aqueous humour; posterior with vitreous. Optic disc lacks photoreceptors (blind spot).",
    },
    {
        "name": "Pituitary anatomy",
        "aliases": [],
        "category": "anatomy",
        "summary": "Two lobes: anterior (adenohypophysis, from Rathke's pouch, ectoderm) secretes GH, prolactin, ACTH, TSH, FSH, LH; posterior (neurohypophysis, neural origin) stores ADH and oxytocin made in hypothalamus.",
    },
    {
        "name": "Adrenal anatomy",
        "aliases": [],
        "category": "anatomy",
        "summary": "Cortex (mesoderm) three zones: glomerulosa (aldosterone), fasciculata (cortisol), reticularis (androgens). Medulla (neural crest) chromaffin cells make catecholamines. GFR/ACTH+ACTH+ blood supply from three arteries; drained by central vein.",
    },
    {
        "name": "Spinal cord blood supply",
        "aliases": [],
        "category": "anatomy",
        "summary": "Anterior spinal artery supplies anterior two-thirds (motor, spinothalamic); two posterior spinal arteries supply posterior columns. Artery of Adamkiewicz is the dominant feeder to lower cord; vulnerable in aortic surgery.",
    },
    {
        "name": "Peritoneal cavity",
        "aliases": [],
        "category": "anatomy",
        "summary": "Intraperitoneal organs: stomach, jejunum, ileum, transverse colon, sigmoid, spleen, liver. Retroperitoneal (SAD PUCKER): suprarenal, aorta, duodenum (2nd to 4th), pancreas (except tail), ureters, colon (ascending/descending), kidneys, oesophagus (lower), rectum.",
    },
    {
        "name": "Foregut, midgut, hindgut",
        "aliases": [],
        "category": "anatomy",
        "summary": "Foregut (coeliac trunk): oesophagus to mid-duodenum. Midgut (SMA): mid-duodenum to two-thirds of transverse colon. Hindgut (IMA): distal transverse colon to upper anal canal. Pain referral matches embryologic origin.",
    },

    # ───────────────────────── HISTOLOGY ─────────────────────────
    {
        "name": "Epithelium types",
        "aliases": [],
        "category": "histology",
        "summary": "Classified by layers (simple, stratified, pseudostratified) and shape (squamous, cuboidal, columnar). Simple squamous: alveoli, endothelium. Pseudostratified columnar ciliated: airway. Stratified squamous: skin, oesophagus.",
    },
    {
        "name": "Connective tissue overview",
        "aliases": [],
        "category": "histology",
        "summary": "Cells (fibroblasts, adipocytes, mast cells, macrophages) plus extracellular matrix (collagen, elastin, ground substance). Types: loose, dense regular (tendons), dense irregular (dermis), adipose, cartilage, bone, blood.",
    },
    {
        "name": "Collagen types",
        "aliases": [],
        "category": "histology",
        "summary": "Type I: bone, tendon, skin, late wound healing. Type II: cartilage, vitreous, nucleus pulposus. Type III: granulation tissue, reticulin, blood vessels. Type IV: basement membrane. Defects: osteogenesis imperfecta (I), Ehlers-Danlos (III, V).",
    },
    {
        "name": "Skeletal muscle structure",
        "aliases": [],
        "category": "histology",
        "summary": "Multinucleated fibres with peripheral nuclei. Sarcomere unit between Z-discs contains thin (actin) and thick (myosin) filaments. Striations from regular thick-thin overlap. T-tubules invaginate to deliver depolarisation to myofibrils.",
    },
    {
        "name": "Cardiac muscle structure",
        "aliases": [],
        "category": "histology",
        "summary": "Branched, striated, with central nuclei and intercalated discs containing gap junctions (electrical coupling) and desmosomes (mechanical). Functional syncytium allows coordinated contraction.",
    },
    {
        "name": "Smooth muscle structure",
        "aliases": [],
        "category": "histology",
        "summary": "Spindle-shaped, single central nucleus, no striations. Contraction triggered by Ca2+-calmodulin activation of myosin light chain kinase. Found in viscera and vessel walls.",
    },
    {
        "name": "Goblet cells",
        "aliases": [],
        "category": "histology",
        "summary": "Mucin-secreting cells of the respiratory and GI epithelium. Decreased in chronic smoke damage of small airways; increased in chronic bronchitis.",
    },
    {
        "name": "Nephron segments",
        "aliases": [],
        "category": "histology",
        "summary": "Glomerulus (filtration), PCT (bulk reabsorption, brush border), loop of Henle (countercurrent), DCT (calcium handling, NaCl reabsorption), collecting duct (final water and Na+ handling, principal and intercalated cells).",
    },
    {
        "name": "Hepatocyte lobule",
        "aliases": [],
        "category": "histology",
        "summary": "Hexagonal arrangement around a central vein with portal triads (hepatic artery, portal vein, bile duct) at corners. Zone 1 (periportal): O2-rich, gluconeogenesis. Zone 3 (centrilobular): drug metabolism, vulnerable to ischaemia.",
    },
    {
        "name": "Skin layers",
        "aliases": [],
        "category": "histology",
        "summary": "Epidermis (stratified squamous): stratum basale, spinosum, granulosum, lucidum (palms/soles), corneum. Dermis: papillary and reticular. Hypodermis: subcutaneous fat. Adnexal structures: hair follicles, sebaceous, sweat glands.",
    },

    # ───────────────────────── EMBRYOLOGY ─────────────────────────
    {
        "name": "Three germ layers",
        "aliases": [],
        "category": "embryology",
        "summary": "Ectoderm: epidermis, nervous system, neural crest. Mesoderm: muscle, bone, connective tissue, kidneys, heart, blood, gonads. Endoderm: gut epithelium, liver, pancreas, lungs, thyroid follicular cells. Gastrulation around week 3.",
    },
    {
        "name": "Neural crest derivatives",
        "aliases": [],
        "category": "embryology",
        "summary": "Migratory cells derived from neuroectoderm. Give rise to peripheral neurons and glia, melanocytes, adrenal medulla, enteric ganglia, branchial arch cartilage, aorticopulmonary septum, parafollicular C cells, odontoblasts.",
    },
    {
        "name": "Pharyngeal arches",
        "aliases": ["Branchial arches"],
        "category": "embryology",
        "summary": "Five arches (1, 2, 3, 4, 6) each with a cartilage, muscle group, nerve, and artery. CN V (1), VII (2), IX (3), X superior laryngeal (4), X recurrent laryngeal (6). Disorders include Treacher Collins (arch 1) and DiGeorge (arches 3 and 4).",
    },
    {
        "name": "Cardiac embryology",
        "aliases": [],
        "category": "embryology",
        "summary": "Primitive heart tube forms by week 3 and loops by day 23. Septation by week 8 separates atria (foramen ovale closes at birth), ventricles, and aorticopulmonary trunk (spiral septum from neural crest, fails in transposition).",
    },
    {
        "name": "Fetal circulation",
        "aliases": [],
        "category": "embryology",
        "summary": "Oxygenated blood from placenta via umbilical vein, bypasses liver via ductus venosus, enters right atrium, mostly shunts through foramen ovale (to left heart) or ductus arteriosus (to descending aorta). All shunts close functionally at birth.",
    },
    {
        "name": "Renal embryology",
        "aliases": [],
        "category": "embryology",
        "summary": "Sequential development: pronephros (regresses), mesonephros (becomes male reproductive tract), metanephros (definitive kidney). Ureteric bud induces metanephric blastema. Failure causes renal agenesis, agenesis with oligohydramnios produces Potter sequence.",
    },
    {
        "name": "Aortic arch derivatives",
        "aliases": [],
        "category": "embryology",
        "summary": "Arch 1: maxillary artery. Arch 2: stapedial, hyoid arteries. Arch 3: common carotid and proximal internal carotid. Arch 4: aortic arch (left), proximal right subclavian. Arch 6: pulmonary arteries and ductus arteriosus.",
    },
    {
        "name": "Gut rotation",
        "aliases": [],
        "category": "embryology",
        "summary": "Midgut herniates into the umbilical cord around week 6, rotates 270 degrees counterclockwise around the SMA, returns to abdomen by week 10. Malrotation predisposes to volvulus.",
    },
    {
        "name": "Teratogenic critical periods",
        "aliases": [],
        "category": "embryology",
        "summary": "Pre-implantation (week 1 to 2): all-or-nothing effect. Embryonic period (week 3 to 8): organogenesis, maximal teratogen sensitivity. Fetal period (week 9 to birth): functional defects and growth restriction.",
    },
    {
        "name": "Common teratogens",
        "aliases": [],
        "category": "embryology",
        "summary": "Alcohol: fetal alcohol syndrome. Warfarin: chondrodysplasia, fetal warfarin syndrome. ACE inhibitors: renal dysgenesis. Valproate, methotrexate, isotretinoin: multiple anomalies. Rubella, CMV, Zika: infectious teratogens.",
    },

    # ───────────────────────── GENETICS ─────────────────────────
    {
        "name": "Autosomal dominant inheritance",
        "aliases": [],
        "category": "genetics",
        "summary": "One affected allele sufficient. Vertical transmission, both sexes equally affected, ~50 percent transmission risk per child. Often structural protein or receptor disorders (Marfan, NF1, familial hypercholesterolaemia, HD, ADPKD).",
    },
    {
        "name": "Autosomal recessive inheritance",
        "aliases": [],
        "category": "genetics",
        "summary": "Two copies needed for disease. Horizontal pedigrees, frequently from consanguinity, often enzyme deficiencies (PKU, Wilson, haemochromatosis, sickle cell, cystic fibrosis). Carriers (heterozygotes) usually asymptomatic.",
    },
    {
        "name": "X-linked recessive inheritance",
        "aliases": [],
        "category": "genetics",
        "summary": "Affected males predominate, no male-to-male transmission, transmitted through carrier mothers to half their sons. Examples: haemophilia A and B, DMD/BMD, G6PD deficiency, Lesch-Nyhan, colour blindness.",
    },
    {
        "name": "X-linked dominant inheritance",
        "aliases": [],
        "category": "genetics",
        "summary": "Affected males pass to all daughters and no sons. Heterozygous females affected but more mildly than males. Examples: hypophosphataemic rickets, Rett syndrome, Alport (most cases).",
    },
    {
        "name": "Mitochondrial inheritance",
        "aliases": [],
        "category": "genetics",
        "summary": "Strictly maternally transmitted. All children of affected females at risk; no transmission from affected males. Heteroplasmy causes variable expression. Examples: MELAS, MERRF, Leber hereditary optic neuropathy.",
    },
    {
        "name": "Anticipation",
        "aliases": [],
        "category": "genetics",
        "summary": "Disease onset earlier and more severe across generations, typical of trinucleotide repeat expansions. Examples: Huntington (CAG), myotonic dystrophy (CTG), fragile X (CGG), Friedreich's ataxia (GAA).",
    },
    {
        "name": "Imprinting",
        "aliases": [],
        "category": "genetics",
        "summary": "Expression of only the paternal or maternal copy of a gene due to epigenetic silencing. Loss of imprinted alleles: Prader-Willi (paternal 15q11 loss), Angelman (maternal 15q11 loss).",
    },
    {
        "name": "Penetrance vs expressivity",
        "aliases": [],
        "category": "genetics",
        "summary": "Penetrance: fraction of carriers who express the phenotype. Expressivity: severity of phenotype among those affected. A gene can have high penetrance but variable expressivity, or vice versa.",
    },
    {
        "name": "Mosaicism",
        "aliases": [],
        "category": "genetics",
        "summary": "Two or more genetically distinct cell lines in the same individual from a postzygotic mutation. Somatic mosaicism affects tissues unequally; germline mosaicism may produce recurrent affected offspring from unaffected parents.",
    },
    {
        "name": "Heterozygosity (loss of)",
        "aliases": ["LOH"],
        "category": "genetics",
        "summary": "Loss of the remaining functional allele at a heterozygous locus, often by deletion, mitotic recombination, or epigenetic silencing. Important in two-hit tumour suppressor inactivation (RB1, TP53, BRCA1/2).",
    },
    {
        "name": "Hardy-Weinberg equilibrium",
        "aliases": [],
        "category": "genetics",
        "summary": "Allele frequencies remain constant when assumptions hold (no selection, mutation, migration, drift, random mating). p^2 plus 2pq plus q^2 equals 1. Used to estimate carrier frequencies for recessive disease.",
    },
    {
        "name": "Lyonisation",
        "aliases": ["X-inactivation"],
        "category": "genetics",
        "summary": "Random inactivation of one X chromosome in each cell in females early in development. Creates mosaicism for X-linked traits. Explains skewed phenotypes in carriers of X-linked disease.",
    },
    {
        "name": "Trisomy basics",
        "aliases": [],
        "category": "genetics",
        "summary": "Most arise from meiotic non-disjunction, risk increases with maternal age. Trisomy 21 (Down): commonest viable, intellectual disability, AV septal defect, leukaemia risk. Trisomy 18 (Edwards) and 13 (Patau) usually lethal in infancy.",
    },
    {
        "name": "Sex chromosome aneuploidies",
        "aliases": [],
        "category": "genetics",
        "summary": "Turner (45,X): short stature, primary ovarian failure, coarctation, lymphoedema. Klinefelter (47,XXY): tall, hypogonadism, infertility, mild learning issues. 47,XYY and 47,XXX often subtle or asymptomatic.",
    },
    {
        "name": "Microdeletion syndromes",
        "aliases": [],
        "category": "genetics",
        "summary": "Submicroscopic deletions detected by FISH or microarray. DiGeorge (22q11): thymic and parathyroid hypoplasia, cardiac defects. Williams (7q11): supravalvular AS, hypercalcaemia, friendly personality. Cri-du-chat (5p deletion): cat-like cry.",
    },

    # ───────────────────────── STATISTICS / EBM ─────────────────────────
    {
        "name": "Sensitivity",
        "aliases": ["True positive rate", "Recall"],
        "category": "statistics",
        "summary": "Proportion of truly diseased correctly identified: TP / (TP plus FN). High sensitivity rules disease out when test is negative (SnNout). Useful for screening.",
    },
    {
        "name": "Specificity",
        "aliases": ["True negative rate"],
        "category": "statistics",
        "summary": "Proportion of truly disease-free correctly identified: TN / (TN plus FP). High specificity rules disease in when test is positive (SpPin). Useful for confirmation.",
    },
    {
        "name": "Positive predictive value",
        "aliases": ["PPV"],
        "category": "statistics",
        "summary": "Probability that a positive test reflects true disease: TP / (TP plus FP). Strongly influenced by pretest probability (prevalence): falls in low-prevalence settings.",
    },
    {
        "name": "Negative predictive value",
        "aliases": ["NPV"],
        "category": "statistics",
        "summary": "Probability that a negative test reflects true absence: TN / (TN plus FN). Higher in low-prevalence settings; falls when disease is common.",
    },
    {
        "name": "Likelihood ratio positive",
        "aliases": ["LR+"],
        "category": "statistics",
        "summary": "Sensitivity / (1 minus specificity). Multiplies pretest odds to give posttest odds. Above 10 strongly rules in; below 1 makes disease less likely.",
    },
    {
        "name": "Likelihood ratio negative",
        "aliases": ["LR-"],
        "category": "statistics",
        "summary": "(1 minus sensitivity) / specificity. Below 0.1 strongly rules out; above 1 raises probability. Independent of disease prevalence.",
    },
    {
        "name": "Pretest and posttest probability",
        "aliases": [],
        "category": "statistics",
        "summary": "Pretest probability is the clinician's estimate before testing (often prevalence or risk-adjusted). Bayes theorem combines pretest odds with a likelihood ratio to give posttest probability.",
    },
    {
        "name": "Number needed to treat",
        "aliases": ["NNT"],
        "category": "statistics",
        "summary": "Number of patients who must receive an intervention to prevent one additional bad outcome. Equals 1 / absolute risk reduction. Smaller NNT means more impactful therapy.",
    },
    {
        "name": "Number needed to harm",
        "aliases": ["NNH"],
        "category": "statistics",
        "summary": "Number who must receive a treatment to cause one additional harmful event. Equals 1 / absolute risk increase. Used alongside NNT to weigh benefit and harm.",
    },
    {
        "name": "Absolute vs relative risk reduction",
        "aliases": ["ARR", "RRR"],
        "category": "statistics",
        "summary": "ARR is the difference in event rates between groups. RRR is ARR divided by the control event rate. RRR often looks impressive in low-event settings; ARR and NNT give a clinically grounded picture.",
    },
    {
        "name": "Relative risk vs odds ratio",
        "aliases": ["RR", "OR"],
        "category": "statistics",
        "summary": "Relative risk is the ratio of event rates; used in cohort studies and trials. Odds ratio is the ratio of odds; used in case-control studies. OR approximates RR when the outcome is rare.",
    },
    {
        "name": "Confidence interval",
        "aliases": ["CI"],
        "category": "statistics",
        "summary": "Range of values within which the true effect is plausibly contained at a stated probability (commonly 95 percent). A CI that crosses the null (1 for ratios, 0 for differences) is statistically non-significant.",
    },
    {
        "name": "P value",
        "aliases": [],
        "category": "statistics",
        "summary": "Probability of observing data at least as extreme as observed if the null hypothesis is true. Does not measure clinical importance, effect size, or the probability that the hypothesis is correct.",
    },
    {
        "name": "Type 1 and type 2 error",
        "aliases": [],
        "category": "statistics",
        "summary": "Type 1 (alpha): false positive, rejecting a true null. Type 2 (beta): false negative, failing to reject a false null. Power equals 1 minus beta. Increased with larger samples and larger effects.",
    },
    {
        "name": "Intention-to-treat analysis",
        "aliases": ["ITT"],
        "category": "statistics",
        "summary": "Analyses participants in the groups to which they were randomised regardless of adherence or crossover. Preserves the benefits of randomisation and minimises bias from non-random dropout. Per-protocol analysis is more biased but tests efficacy under adherence.",
    },
    {
        "name": "Selection bias",
        "aliases": [],
        "category": "statistics",
        "summary": "Systematic difference between sampled and unsampled populations, or between treatment groups. Sources include non-random sampling, loss to follow-up, and Berkson's bias in hospital-based studies.",
    },
    {
        "name": "Confounding",
        "aliases": [],
        "category": "statistics",
        "summary": "A third variable associated with both exposure and outcome distorts the apparent relationship. Addressed by randomisation, restriction, matching, stratification, or multivariable adjustment.",
    },
    {
        "name": "Lead-time and length-time bias",
        "aliases": [],
        "category": "statistics",
        "summary": "Lead-time bias: earlier detection appears to lengthen survival without changing time of death. Length-time bias: screening preferentially detects slow-progressing disease. Both inflate apparent screening benefit.",
    },
]


import re as _re
from urllib.parse import quote_plus as _quote_plus


_LOOKUP: dict = {}
_NAMES: list = []
for _t in PRECLINICAL_TERMS:
    _n = _t["name"]
    _keys = [_n] + list(_t.get("aliases", []) or [])
    _NAMES.extend(_keys)
    for _k in _keys:
        _LOOKUP[_k.lower()] = _t

_NAMES = sorted(set(_NAMES), key=len, reverse=True)
_PRECLINICAL_RE = (
    _re.compile(r"\b(?:" + "|".join(_re.escape(n) for n in _NAMES) + r")\b",
                _re.IGNORECASE)
    if _NAMES else None
)


def _wikipedia_url(term: str) -> str:
    return f"https://en.wikipedia.org/wiki/Special:Search?search={_quote_plus(term)}"


def resolve(text: str) -> list:
    if not text or _PRECLINICAL_RE is None:
        return []
    out = []
    seen: set = set()
    for m in _PRECLINICAL_RE.finditer(text):
        key = m.group(0).lower()
        t = _LOOKUP.get(key)
        if t is None:
            continue
        canon = t["name"]
        if canon in seen:
            continue
        seen.add(canon)
        out.append({
            "name":           canon,
            "summary":        t["summary"],
            "url":            _wikipedia_url(canon),
            "source":         "preclinical",
            "category":       t.get("category", ""),
            "case_sensitive": False,
        })
    return out
