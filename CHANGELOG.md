# Changelog

All notable changes to The AnkiDote.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.3] - 2026-08-19

A security and robustness release from a full review of the codebase.
No content changed, so nothing needs publishing over the content
channel. Every defect below was reproduced against the shipped 2.1.2
code before being fixed, and each has a regression test that fails
against 2.1.2 and passes here.

### Security

- **A card could load an untrusted host into the authenticated dock.**
  `_is_trusted_host` decides using Python's `urlparse`; the URL is then
  loaded by Chromium, which follows the WHATWG URL spec. The two
  disagree about a backslash in the authority - WHATWG treats it as `/`,
  `urlparse` treats it as an ordinary hostname character - and that
  disagreement is a complete bypass of the provenance check added in
  2.1. Measured against both parsers:

      https://evil.com\.ncbi.nlm.nih.gov/
          urlparse -> evil.com\.ncbi.nlm.nih.gov   -> trusted
          Chromium -> evil.com

      https://evil.com\@ncbi.nlm.nih.gov/
          urlparse -> ncbi.nlm.nih.gov             -> trusted
          Chromium -> evil.com

  `data-sp-url` is an ordinary HTML attribute, so either string in a
  deck downloaded from AnkiWeb would have opened an attacker's host in
  the profile holding live NCBI, DrugBank, UpToDate and chat sessions.
  `_is_safe_url` now refuses backslashes and control characters
  outright, because the defect is deciding on one parse and acting on
  another rather than the particular character. Tab, CR and LF are
  refused for the same reason: browsers strip them before parsing and
  `urlparse` does not.

- **Validation stopped one level short of where it mattered.** 2.1
  taught `_validate` to check every entry of every vocabulary rather
  than only the first. It checked that `aliases`, `brands` and `utd`
  were lists, but never what was in them, and every consumer lowercases
  those elements to build its lookup tables. Six poisoned shapes passed
  the type-only check and four killed the import outright - which is the
  identical permanent brick the 2.1 fix existed to prevent, because the
  file validates, is written to `user_files/`, is preferred at every
  launch, and the Settings switch that would disable updates lives in
  the add-on that no longer imports. `pearls/_drugs.py` survived two of
  them only because it happens to carry an `isinstance` guard that the
  other six consumers do not, so the check belongs in the validator
  where it covers all seven at once.

- **`utd` was validated as the wrong shape entirely.** It is not a list
  of strings; each element is a `[label, query]` pair and
  `_conditions._primary_url` reaches into it as `utd[0][1]`. A dict, a
  bare string, a non-string pair and a one-element pair all returned ""
  from the shipped validator and then crashed `resolve()`, which runs on
  every card shown. The symptom would have been a broken popup on every
  card until the file was deleted by hand, not a single import failure.
  Acronym candidates are now checked for their full three-element shape
  for the same reason: `_acronyms` unpacks them positionally and
  lowercases every context word.

### Fixed

- **Two concurrent update checks could leave a truncated library.**
  `check_in_background` runs at launch and the "Check now" button in
  Settings calls the same code, and both wrote through a fixed
  `library.json.part`. One writer could unlink another's temp file,
  create its own at the same name, and have the first writer's
  `os.replace` rename that half-written file into place. `_validate`
  catches it at the next launch and falls back, so nothing breaks, but
  the user's content silently reverts with no error logged anywhere. The
  temp name now carries the pid and thread id, so each writer only ever
  renames a file it finished writing.

## [2.1.2] - 2026-08-19

Released because `__init__.py` changed after `v2.1.1` was tagged and
pushed. That file is packaged, so the change could not ship under a
version number already pointing at a different tree.

### Changed

- **The two remaining captions under the Modules switches are gone.**
  One noted that the UpToDate sidebar needs your own subscription, the
  other that the chat sidebar needs no API key. Both restated the
  checkbox label and the AnkiWeb description, so all three module rows
  are now bare checkboxes. `_row` already tolerated an empty
  description, so the spacing stays even.
- **`benztropine` is renamed to `benzatropine`.** `benztropine mesylate`
  became `benzatropine mesilate` on the TGA's list, so benzatropine is
  the Australian Approved Name and the library held only the US form.
  Unlike the four merges in 2.1.1 there was no duplicate to fold in, so
  nothing is lost by renaming. It is the drug on every acute dystonia
  and drug-induced parkinsonism card, so the heading was showing the
  American name on exactly the material a psychiatry rotation runs on.
  `benztropine` is kept as an alias.

### Fixed

- **Twelve more drug spellings that matched nothing.** 2.1.1's sweep
  worked from names that happened to appear in a deck. This one works
  from the TGA's own list of updated ingredient names, which has 22 rows
  whose new name is already a generic in this library; 2.1.1 had caught
  11 of them. The rest are now aliased: `benzhexol`, `flupenthixol`,
  `dexamphetamine`, `hydroxyurea`, `eformoterol`, `glycopyrrolate`,
  `chlorpheniramine`, `cholestyramine`, `clomiphene`,
  `ethinyloestradiol`, `actinomycin D`.
- **`push-*.sh` could publish a manifest naming no download.** The
  manifest guard added in 2.1.0 restored the published pointer only when
  the remote version sorted at or above the mirrored one. A local build
  stamps a version with no `url`, so mirroring one that sorted *above*
  the remote was waved through, and every client's next check would read
  a newer content version with no address to fetch it from and silently
  get nothing. The guard now keys on the `url` rather than the ordering:
  a manifest without one is a build artefact and never reaches the
  branch. The version comparison is kept for the case where both
  manifests are genuine published pointers.
- **`push-*.sh` no longer mirrors `data/` over a published one.** Fixing
  the manifest guard above fixed only half the problem. `data/library.json`
  is mirrored too, and it is the thing the manifest describes. Publishing
  a content version from the clone and then mirroring a *different*
  library stamped with that same version leaves the repository holding a
  manifest and a library claiming the same content with different bytes,
  which `test_manifest_matches_the_bundled_library` correctly refuses.
  The rule underneath both halves is one rule: `data/` is not source, and
  `tools/publish_content.sh` owns the pointer and the library alike. If
  the repository's manifest carries a `url` and does not sort below the
  library in the source zip, `data/` is now left entirely alone.

## [2.1.1] - 2026-08-19

Released because `pearls/_drugs.py` changed after `v2.1.0` was tagged
and pushed. That file is packaged, so the change could not ship under a
version number already pointing at a different tree.

### Fixed

- **Drugs written the Australian way now highlight.** Measured against
  79 names an Australian student's cards actually use, 23 matched
  nothing at all: `frusemide`, `cephalexin`, `cephazolin`, `thyroxine`,
  `amoxycillin`, `indomethacin`, `cholecalciferol`, `sulphasalazine`,
  `valproate`, `glyceryl trinitrate` and others. Those words produced no
  popup whatsoever, which is easy to miss precisely because nothing
  appears. They are now recognised, case-insensitively, and the popup
  shows the standard name.
- **Five drugs were shown under their American name.** The popup
  heading is the most visible place the Australian-first rule applies,
  and pethidine, rifampicin, oestradiol and lignocaine were each
  appearing as meperidine, rifampin, estradiol and lidocaine - in fact
  each was in the database twice, once under each name, with whichever
  matched first winning. The duplicates are merged, the Australian name
  is shown, and cards written the American way still resolve.
  Nitroglycerin, which had no Australian counterpart, is now glyceryl
  trinitrate. Drug entries: 1,165 to 1,161.

### Added

- **Twelve more conditions rewritten**: amenorrhoea, rheumatic heart
  disease, diverticular disease, cerebral venous sinus thrombosis,
  haemorrhoids, acute angle-closure glaucoma, osteomalacia, rickets,
  anal fissure, uveitis, Huntington disease and chronic fatigue
  syndrome. The over-cap backlog falls from 170 to 158.
- **The build now refuses an alias keyed to a drug that does not
  exist.** Such an alias would simply never match, and nothing would
  report it. It immediately caught one, which turned out to be a drug
  missing from the database entirely.

## [2.1.0] - 2026-08-18

### Security

This release is the outcome of a full review of the code paths that 2.0
introduced. Moving the reference database out of the add-on and onto a
download channel changed what the add-on has to defend against: summary
text, entry links and library structure are no longer written by the
author alone. Four defects followed from that, all found by testing the
shipped code rather than by reading it.

- **A malformed downloaded library could disable the add-on
  permanently.** Validation checked the first condition and accepted
  everything after it, so a library whose eighth entry was malformed
  passed, was saved, was preferred at every launch, and then failed at
  import. The Settings switch that would have turned updates off lives
  inside the add-on that no longer loaded, so the only way out was
  deleting a file by hand. Every entry of every vocabulary is now
  checked, and a rejected download is renamed aside instead of being
  retried forever.
- **Update URLs are now required to be HTTPS.** Neither the manifest
  address nor the library address it names was checked, and the
  underlying library will fetch `file://`, `ftp://` and `data:` as
  readily as a web address. Both are now verified before the request,
  and again after any redirect, so a redirect cannot quietly downgrade
  the connection.
- **Downloaded content can no longer carry a non-web link.** Anything
  that is not `http` or `https` is now rejected when the file is
  validated, rather than only when the link is clicked. Defence in
  depth rather than a live hole: no entry in the library carries a
  link field at all, and every link the add-on builds has its scheme
  and host hardcoded, so a hostile library cannot currently choose a
  destination.
- **A shared deck can no longer steer the sidebar's signed-in
  sessions.** `data-sp-url` is an ordinary HTML attribute, so any deck
  can set it, and clicking a marked word navigated a browser profile
  holding live NCBI, DrugBank, UpToDate and chat sessions. Any address
  was accepted; the only response to an unrecognised one was a debug
  log line. `SECURITY.md` had listed this as in scope since 1.x.
  Addresses are now trusted only if they belong to a service the
  add-on integrates with or to a host set in Settings - a custom term,
  the institution URL, a custom chat provider. Anything else opens in
  the normal browser, where there is no session to borrow, so the link
  still works. Host matching is also now anchored on a dot boundary;
  the previous check was a bare suffix match that would have accepted
  `notncbi.nlm.nih.gov`.
- **A saved download can no longer be diverted through a symlink.** The
  temporary file used while saving is now opened in a way that refuses
  to follow one.

None of these are known to have been exploited, and all of them require
control of the content host or local access to the add-on folder.

### Added

- **Twenty-nine more conditions rewritten**, chosen the same way as the
  last batch - by how often each comes up in real use rather than by how
  badly it overflowed.

  Lung cancer, lithium toxicity, miscarriage, polycystic ovary syndrome,
  cystic fibrosis, pre-eclampsia, paracetamol overdose, oesophageal
  varices, acute pancreatitis, diabetes insipidus, phaeochromocytoma,
  hyperosmolar hyperglycaemic state, sickle cell disease, bowel
  obstruction, nephrotic syndrome, abruption, aortic aneurysm, portal
  hypertension, ectopic pregnancy, peripheral arterial disease, urinary
  incontinence, cluster headache, tension headache, medication overuse
  headache, prostate cancer, acute tubular necrosis, osteomyelitis,
  subdural haematoma and chronic pancreatitis.

  Australian sources throughout - eTG, AMH, PBS, RANZCOG, and the
  Poisons Information Centre. The over-cap backlog falls from 199 to
  170.
- **A security test file**, thirty-three tests pinning each of the above
  so none of them can quietly come back.

### Fixed

- **The StatPearls search bar came back on article pages.** The sidebar
  hides NCBI's top search bar on the StatPearls landing page, where the
  page's own search box does the same job. It was hiding it everywhere,
  including on articles - which is the one place it is the only way to
  search the book without going back first.

### Changed

- **Settings reads less like an explanation of itself.** Five captions
  that restated their own control removed, three shortened. The ones
  that state a rule you could not otherwise infer are kept.
- More popup trivia, since the pool was small enough to repeat.

## [2.0.1] - 2026-08-18

### Fixed

- **Content updates had no way to turn them on.** 2.0.0 shipped the key
  in a JSON config file and no interface anywhere, so the update
  channel existed with nobody on it - a corrected dose could be
  published and reach essentially no one. There is now a checkbox in
  Settings > General > Reference database, with the content version in
  use and a "Check now" button that runs off the UI thread.
- **Content updates now default to on.** For a clinical reference, a
  database that quietly goes stale is a worse failure than one that
  fetches a checksummed, validated data file. Turning it off in
  Settings stops all content network activity, as before.
- **Installs that ran 2.0.0 are migrated once.** `_config.set_value`
  writes the whole config back to meta.json, so the automatic
  first-launch stamps froze `libraryAutoUpdate: false` into per-install
  state before any user could have chosen it. Changing the shipped
  default would not have reached them. 2.0.1 flips it on once and
  records that it has; turning it off after that sticks.

- **"Note" now renders last.** It is an aside, and 29 conditions and 21
  drug entries wrote it immediately before "Red flags" - putting a
  remark ahead of the safety-critical section. The popup moves it to
  the end when rendering rather than relying on fifty summaries being
  rewritten, so it holds for downloaded content too.

### Removed

- **The 2.0 upgrade popup.** A modal on first launch to announce
  changes the release notes already cover.

## [2.0.0] - 2026-08-18

### Added

- **The term library ships as data, and can update on its own.** Every
  condition, drug, acronym and sign now lives in `data/library.json`
  rather than inside the add-on's Python modules. Content and code are
  no longer welded together, so a wrong dose or a stale guideline can be
  corrected without an AnkiWeb release and a wait for everyone to
  update. Opt in with `libraryAutoUpdate`; it is off by default and the
  add-on never contacts the network for content until you turn it on.
  Downloaded content is parsed as JSON, checked against a published
  sha256, validated for schema and structure, and discarded in favour of
  what you already have if any of that fails. It is never imported or
  executed.
- **A summary that would scroll now fails the build.** The height
  estimator in the test suite only ever looked at the rewritten
  summaries, the acronyms and the drugs - which is to say, everything
  except the 774 conditions still carrying their original text, where
  the length actually was. Lung cancer had been shipping at roughly
  1,200px against a ceiling nominally set at 1,000. The estimator now
  walks every summary the popup can render, and a second test pins the
  over-cap backlog so it can only shrink.

### Changed

- **Short lists read as prose instead of bullets.** A bullet costs a
  full line however little it contains, so a three-item list of two-word
  fragments spent about 60px saying what fits on one 22px line. Lists
  now bullet at four or more items with at least one of them
  substantial. Nothing was rewritten to achieve this: the tallest
  condition popup dropped from 1,208px to 995px, and 40 conditions and
  29 drug entries came back under the cap on the rendering change alone.
- **Fourteen high-traffic conditions rewritten.** Vasculitis, pleural
  effusion, acute liver failure, septic arthritis, colorectal cancer,
  anorexia nervosa, peptic ulcer disease, hypokalaemia, aortic
  dissection, rhabdomyolysis, infective endocarditis, coeliac disease,
  ankylosing spondylitis and serotonin syndrome. Chosen by how often
  each appears across a real collection rather than by how badly each
  overflowed - the tallest entries in the database turned out to be
  conditions nobody had made a card about.

### Fixed

- **Eight popups were titled something other than what they described.**
  An override keyed on an alias still merges, because the lookup is
  keyed on every alias, but the popup takes its heading from the
  canonical name. A summary written about community-acquired pneumonia
  appeared under "Pneumonia", and one written about acute coronary
  syndrome under "Myocardial infarction" - narrower than the heading
  claimed, silently. All eight re-keyed, with a test so it cannot
  recur.

## [2.0.0-preview14] - superseded

### Fixed

- **Drug popups are now bulleted too.** Bullets only ever appeared where
  a list was written with semicolons, and drug entries separate their
  side effects and indications with commas, so none of them ever
  bulleted. Roughly 990 drug popups now break their lists out. Commas
  that are ordinary punctuation rather than list separators are left
  alone, so a phrase like "caution with macrolides, azoles" stays as a
  sentence.
- **Headings with a qualifier work.** "Sx (tetrad):" was not recognised
  as a heading at all, so everything under it fell back into the opening
  paragraph. That is why the neuroleptic malignant syndrome popup showed
  its tetrad and its whole lab panel as one block of text.
- **Section headings on DrugBank jump correctly.** DrugBank names some
  of its sections differently to StatPearls - "Indication" rather than
  "Indications" - so those headings opened the page at the top.
  Interactions, metabolism and half-life now have targets as well.

### Changed

- **Syphilis and neuroleptic malignant syndrome** rewritten. Syphilis
  had its entire staging, from primary through congenital, in one
  unbroken paragraph. Both now use Australian dosing: benzathine
  benzylpenicillin 1.8 g rather than units.
- **"Stages"** added as a heading.

## [2.0.0-preview13] - unreleased

### Fixed

- **Popups no longer grow.** Bullet points take more vertical space than
  the run-on sentence they replaced, and the popup had no height limit
  except the edge of the window, so on a tall screen it simply got
  bigger. It is now capped, and bullet spacing has been tightened to
  give back most of what the bullets cost.
- **Section headings jump more reliably.** The jump ran once, the
  instant the page reported itself loaded, and did nothing if the
  article had not finished laying out or if the page moved itself
  afterwards. It now retries for a few seconds and confirms the heading
  actually ended up in view. If it still cannot find the heading, the
  log now records which headings the article really has.

## [2.0.0-preview12] - unreleased

### Fixed

- **Changes to the popup take effect on upgrade.** The reviewer loaded
  its popup script from an address that never varied between releases,
  so a webview that had already cached the file kept running the old
  copy indefinitely. Everything on the Python side updated and the
  popup behaviour did not. This is why bullets, added in preview 9,
  appeared to do nothing: they had been working all along and were
  never reaching the screen. The address now changes whenever the
  script does.
- **Section headings jump to the right part of the article.** Nearly
  half of them opened the article at the top instead - including
  "Clinical features", the most common heading in the popup. Headings
  that have no matching section in the article, such as "Note" and
  "Red flags", are no longer drawn as though they can be clicked.
- **Bell palsy and Raynaud phenomenon were each stored twice.** Which
  version you saw depended on whether the card spelled the name with
  an apostrophe, and the two versions differed in length and, for Bell
  palsy, opened different articles - one of them the general facial
  nerve palsy chapter rather than the Bell palsy one. Each is now a
  single entry, reachable under either spelling, pointing at the
  correct article.
- **Switching to StatPearls from an unrelated page now works.** Any
  page that was not DrugBank counted as StatPearls, so following a
  reference out to PubMed and then clicking StatPearls did nothing at
  all, while the StatPearls button appeared active.

### Changed

- **StatPearls opens on its search page instead of the full contents
  listing.** Home was the alphabetical index of every chapter in
  StatPearls, which is a very large page and was the whole reason
  switching to StatPearls felt slower than switching to DrugBank. It
  now opens the same in-book search used when a term has no direct
  article, so both arrive in the same place.

- **Acronym popups now use the same sections as everything else.** The
  differential in the AKI popup was buried mid-paragraph, which was the
  same problem section headings were introduced to solve. Twenty
  acronyms also used headings the popup did not recognise, so they were
  printed as ordinary text instead of headings: among others Serotonin
  syndrome, DIC, ITP, OCD, ICU and SGLT2 inhibitors.
- **Some acronym entries were written to overseas practice.** Systolic
  blood pressure targets now follow the Heart Foundation, tuberculosis
  treatment names the drugs in full and notes it is run through a state
  TB service, glandular fever recommends EBV serology rather than a
  heterophile antibody test, and stroke thrombolysis lists tenecteplase
  alongside alteplase.

### Added

- **Horner syndrome** rewritten in the structured format, with the
  lesion localised by order of neuron and the anhidrosis pattern that
  distinguishes them.

## [2.0.0-preview11] - unreleased

### Fixed

- **"Open article" works for conditions without a direct NBK
  accession.** 189 conditions have none and fall back to an in-book
  StatPearls search - which was built from the Australian spelling.
  StatPearls is a US publication, so a search for "Iron deficiency
  anaemia" could never match, and the popup opened a search page
  guaranteed to be empty. Search queries are now translated to US
  spelling; everything the reader sees stays Australian.
- **Removed three fabricated NBK accessions** added in preview 8 for
  febrile neutropenia, tumour lysis syndrome and SIADH. They were
  plausible-looking but invented: NBK519494 is in fact "Anatomy, Bony
  Pelvis and Lower Limb, Knee Lateral Meniscus". A wrong accession is
  worse than none, because it opens the wrong article confidently.
  These now fall back to search, which works. A test blocks unverified
  accessions on new entries.

## [2.0.0-preview10] - unreleased

### Fixed

- **Seven acronym definitions no longer subordinate Australian usage.**
  "UK/AU term for CBC" makes the US name the real thing and the
  Australian one a regional variant of it - which is backwards for an
  add-on that is Australian-first. FBC, OGD, TLCO, USS, IDC and IVC are
  now defined directly, with the US name as a closing aside where it
  aids recognition. US acronym entries pointing at the Australian term
  are correct and unchanged. `tests/test_vocab.py` guards the rule.
- **The home glyph is bigger.** The house character is drawn small
  within its em box in most system fonts, so at the same pixel size as
  the arrows it read as a smaller icon.

## [2.0.0-preview9] - unreleased

### Changed

- **List-like sections render as bullets.** Causes, investigations and
  clinical features are lists written as prose with semicolons, and as a
  paragraph several unrelated items shared a line and wrapped across
  lines - so the reader had to parse punctuation to find where one item
  ended and the next began. Sections yielding three or more points are
  now bulleted, one per line. Semicolons inside brackets do not split,
  and sections yielding fewer than three points stay as paragraphs,
  which keeps genuinely prose sections - Note, Pathophysiology - intact
  where sentences build on each other.
- **Section bodies start with a capital.** They previously began
  mid-sentence in lower case, because the label had been cut from the
  front of the sentence.
- **Length band tightened**: ceiling 1,200 from 1,400, with the median
  now 1,086. Every override was trimmed.

## [2.0.0-preview8] - unreleased

### Added

- **Topic 7 oncology and haematology** - 14 conditions: iron deficiency
  and B12 deficiency, myeloma, Hodgkin and non-Hodgkin lymphoma, CLL,
  AML, CML, ITP, DIC, febrile neutropenia, tumour lysis syndrome, spinal
  cord compression, hypercalcaemia.
- **Topic 3 neurology, endocrine and diabetes** - 15 conditions: stroke,
  TIA, subarachnoid haemorrhage, epilepsy, multiple sclerosis, Parkinson
  disease, myasthenia gravis, Guillain-Barre syndrome, DKA, type 2
  diabetes, hypo- and hyperthyroidism, Addison disease, Cushing
  syndrome, SIADH. 52 overrides in total.
- **The override layer can contribute new conditions.** Febrile
  neutropenia, tumour lysis syndrome and SIADH were absent from the base
  database entirely, and a summary for a term that cannot be matched is
  dead weight. `NEW_CONDITIONS` in `pearls/_rich.py` carries the whole
  of a new entry - name, aliases, article link and summary - in one
  place, merged before the matcher index is built.

## [2.0.0-preview7] - unreleased

### Fixed

- **Section labels are matched case-insensitively.** The label list held
  `DDx` while summaries write `Ddx:`, and the pattern had no `i` flag -
  so the label silently rendered as body text, which is how a
  differential ended up buried mid-paragraph inside the management
  section of the stroke popup. Labels now match in any case and display
  in a canonical form.
- **A repeated label no longer emits a second heading.** Summaries
  legitimately return to a heading - acute management, then long-term -
  and two identical `MX` headers stacked on one popup read as a
  rendering fault. Consecutive blocks with the same label are merged.

### Added

- **Topic 1 cardiovascular and respiratory** - 8 conditions: heart
  failure, acute coronary syndrome, atrial fibrillation, COPD, asthma,
  pulmonary embolism, community-acquired pneumonia, hypertension.
  23 overrides now in total.
- `Secondary prevention`, `Extra-articular`, `Extrahepatic` and
  `Extraintestinal` as recognised section labels.

### Changed

- **Length budget raised to a 1,400 ceiling, target 900-1,200**, from
  850. Preview 6 was slightly tighter than it needed to be.

## [2.0.0-preview6] - unreleased

### Changed

- **Structured summaries cut back to glance size.** Preview 5 kept the
  structure but blew the length budget - dermatomyositis ran to 2,337
  characters. These popups are executive summaries whose job is to
  orient you and hand off to the full StatPearls article underneath;
  one long enough to scroll has stopped being a summary and started
  competing with the thing it links to. Rewritten to a median of 864
  characters, against a base median of 801, with the difference going
  to section labels rather than content. A 1,000-character ceiling is
  now enforced by `tests/test_vocab.py`.

## [2.0.0-preview5] - unreleased

### Added

- **A structured-summary override layer** (`pearls/_rich.py`), with the
  first 15 conditions rewritten - Topic 4 rheumatology and dermatology.
  The base summaries were never thin (median 800 characters); they were
  unstructured, one dense block with labels used inconsistently, which
  is what makes a long popup unreadable. Rewrites follow the same
  scaffold as the cards they sit beside: lede, then Epidemiology,
  Causes, Pathophysiology, Clinical features, Investigations,
  Differential, Management, with `Note:` for the discriminating fact and
  `Red flags:` for anything time-critical. Dermatomyositis goes from 968
  characters of prose to 2,337 in seven labelled sections.
- **Override-layer tests.** Overrides apply by canonical name, so a typo
  or a renamed condition silently does nothing - the popup keeps its old
  summary and nothing errors. The tests assert every override lands, has
  at least three sections, uses only labels the renderer knows, and uses
  Australian spelling.

## [2.0.0-preview4] - unreleased

### Added

- **A clinical signs database** (`pearls/_signs.py`), 56 entries across
  respiratory, cardiovascular, gastrointestinal, neurological and renal
  examination vocabulary. Same editorial line as the other vocabulary
  files: define the term, then give the one discriminating fact that
  makes it useful at the bedside. Orthopnoea explains why recumbency
  raises preload; claudication contrasts vascular with neurogenic, where
  relief needs flexion rather than merely stopping; spasticity contrasts
  with rigidity on velocity-dependence.
- **`Mechanism:` as a recognised section label** in the popup renderer.

## [2.0.0-preview3] - unreleased

### Added

- **A psychiatric phenomenology database** (`pearls/_psych.py`), 53
  entries covering the mental state exam - form of thought, mood and
  affect, catatonia, delusions and passivity, perception, insight, and
  the medication-related movement disorders. Descriptive psychopathology
  is unusually unforgiving: the words are technical, they do not mean
  what they mean in ordinary English, and the distinctions between them
  are exactly what gets examined. Entries therefore name the term they
  are most often confused with, because in phenomenology that pairing is
  the definition - tangentiality only means something against
  circumstantiality, an illusion only against a hallucination.
- **`tests/test_vocab.py`.** The reviewer merges several databases into
  one popup and the first to claim a name wins, so a duplicated name
  means one entry is silently unreachable - the popup opens, it just
  shows the wrong definition. The test asserts the databases are
  disjoint, that entries are well-formed, that summaries use Australian
  spelling, and that every section label is one the popup renderer
  recognises. It caught four collisions on its first run.

## [2.0.0-preview2] - unreleased

### Added

- **A descriptive-vocabulary database** (`pearls/_descriptive.py`), 55
  entries covering lesion morphology, symptom words and laboratory
  descriptors. The gap was the wrong way round: cards resolved
  *dermatomyositis* but not *poikiloderma*, *telangiectasia*, *myalgia*
  or *pathognomonic*, and a reader who knows the disease name reads past
  it either way, while one who doesn't is stuck on the descriptive word.
  The dermatomyositis card that previously highlighted none of them now
  resolves fifteen.
- **UpToDate follows Anki into dark mode.** It ships no dark theme of
  its own, so a dark Anki left a full-brightness white pane beside it.
- **Twenty more House quotes**, 8 to 28.

### Changed

- **The README describes the add-on** rather than recounting the 1.1 to
  1.3 releases. Version history belongs in this file.

## [2.0.0-preview1] - unreleased

### Changed

- **Term matching is ~30x faster.** The condition and drug databases
  were each matched with a single regex of several thousand
  alternatives. `re` has no alternation index, so it walked that list at
  every position in the card: 17.2 ms per render, on every question and
  every answer. `pearls/_matcher.py` replaces it with a first-word index
  - 0.59 ms, and independent of database size, which matters given 2.0
  expands them. `tests/test_matcher.py` diffs the new matcher against
  the old patterns over the real databases and asserts they agree
  exactly; that equivalence is the only thing that makes the swap safe.
- **Popup summaries render as labelled sections.** They were one
  continuous paragraph with section labels inlined behind a `<br>`. On a
  long entry that is a wall - the information is all there and none of
  it is findable, which is the opposite of what a hover popup is for.
  The text before the first label becomes a lede and each label opens
  its own block. Entries with no labels still render as a single lede,
  so the whole database is safe before any of it is rewritten.

### Removed

- `_webengine.inject_stealth`, which nothing had called.

## [1.4.3] - 2026-08-14

### Fixed

- **The House quote no longer announces itself.** It sat in a filled,
  outlined teal chip at 10.4:1 contrast - which is how you style a
  control, so an easter egg was demanding attention every time it
  fired, most obviously in dark mode. It is plain italic text now, at a
  contrast that clears AA and goes no further: legible when you look at
  the header, invisible when you are using it.
- **A popup no longer swaps when you move toward it.** Marks are dense,
  so there is very often another underlined term sitting in the gap
  between the term you hovered and the popup that opened for it -
  crossing it on the way replaced the popup, which is the one place it
  must not move. Two guards now: while a popup is open, the pointer's
  last movement is tested against the triangle formed by where it just
  was and the near edge of the popup, and inside that corridor other
  marks are ignored; outside it, a different mark has to hold the
  pointer for 70 ms before taking over. The corridor expires after
  600 ms so a parked pointer yields, and neither guard applies when
  nothing is open, so the first hover stays instant.
- **The StatPearls / DrugBank pills follow the page.** They rendered
  the `pearlsHomePage` preference, which is only what the Home button
  will do next - so opening a drug from a popup left "StatPearls" lit
  with a DrugBank page on screen. They now show which site is loaded;
  the preference still changes only when you click a pill.
- **The article list header no longer draws boxes around its own
  contents.** A bare `QWidget { ... }` rule set on the header row also
  matches every child - QLabel and QPushButton are both QWidgets - so
  the background and borders were painted around the title and the
  dismiss button as well as the row itself.

- **DrugBank search works.** Qt's `ErrorPageEnabled` was throwing away
  the one thing that made the request succeed. Cloudflare's managed
  challenge is an HTTP 403 whose *body* is the interstitial that runs
  the check and then redirects - and Qt, seeing a 403, discarded that
  body and navigated to its own error page, so the challenge could
  never run. Error pages are now off for the reference panel, and a
  failed navigation asks the page what it actually contains before
  calling it a failure: a challenge is left alone and re-checked for up
  to ten seconds, a non-200 carrying a real body is treated as loaded,
  and only a genuinely empty page retries. This is why the home page
  loaded fine while every search failed - the home page returns 200.

### Changed

- **Diagnostics have moved to Settings > Advanced.** They were behind an
  undocumented keyboard chord, which was a bad trade twice over: the
  chord competed with whatever else you have bound and had no visible
  failure mode when it lost, and a control nobody can find is not
  usable even when it does work. The tab holds a verbose-logging
  switch, **Show log**, and **Web inspector**.

### Removed

- Two configuration keys that existed only to reach a hidden menu that
  no longer exists. Leftover values in an existing config are ignored.

## [1.4.2] - 2026-08-14

### Added

- **StatPearls and DrugBank follow Anki into dark mode.** Uses
  Chromium's own auto-dark rendering pass rather than an injected
  stylesheet, so figures and structure diagrams survive intact. Needs
  Qt 6.7 or newer; on older builds the pages render light as before.
- **The article list can be dismissed.** A small close button on the
  RELEVANT ARTICLES header hides it for the current card. It is a guess
  at what is relevant and not always a good one, and closing the whole
  sidebar was previously the only way out of its way. The next card
  brings it back, as does the toolbar button.
- **A web inspector for the sidebars**, alongside the diagnostic log
  under Tools > The AnkiDote once diagnostics are unlocked. Qt reads
  `QTWEBENGINE_REMOTE_DEBUGGING` when Anki starts, so it cannot be
  switched on for the session you are already in - the entry offers to
  relaunch Anki with it set, and warns first: the port drives every
  webview in the process, signed-in UpToDate and chat sessions
  included. Nothing is persisted, so the next normal restart turns it
  back off.
- **Restore defaults, on the Shortcuts tab.** A blank field is
  ambiguous - deliberately disabled, or lost to a bad write? - and
  there was no route back to a working binding. Two actions sharing a
  binding is now flagged too.

### Changed

- **The article list is ranked and capped.** It was every match on the
  card in whatever order the resolvers found them, conditions first and
  drugs after - so on a card about calcium pyrophosphate deposition
  disease, "gout" (mentioned once, as a contrast) sat above the disease
  the card is actually about. Entries are now scored on whether the term
  appears in the card's first field, how often it appears, how early,
  and how specific it is, then trimmed to `maxResults` (default 8).
- **Clicking the site you are already on no longer reloads.** Switching
  to DrugBank from a DrugBank monograph cost a Cloudflare round trip
  and discarded the page you were reading.
- **A loading bar sits under the sidebar header.** Reaching DrugBank
  goes through Cloudflare's challenge and can take several seconds,
  during which nothing on screen changed - so the switch read as broken
  and got clicked again, restarting the navigation.
- **Header icons are optically matched.** The glyphs come from
  different Unicode blocks and were all set at one font size, so the
  guillemet arrows rendered tiny beside the reload and home icons.
  Back and forward are now proper arrows, sized per glyph.

### Fixed

- **Shortcuts now fire wherever focus is.** Every binding was created
  with Qt's default `WindowShortcut` context, which only fires when the
  active window is the one the shortcut is parented to - so a binding
  was dead whenever focus sat in the reviewer's webview or a genuine
  top-level window like Browse was in front. That is the whole reason
  the diagnostics shortcut appeared to do nothing. All bindings are now
  `ApplicationShortcut`, which is what a global shortcut is supposed to
  mean and what they were all documented as doing.
- **The diagnostics shortcut is configurable**, so another add-on
  claiming the same binding no longer leaves it unreachable.
- **DrugBank search no longer throws you back into StatPearls.** A
  failed navigation retried `_pending_url` - the target of the last
  popup "Open article" click, which persists until the next one. So any
  in-page navigation that failed, a DrugBank search most visibly,
  retried whatever StatPearls chapter had last been opened and landed
  the reader on it. Failed loads now retry the URL Chromium was
  actually asked for, and the popup intent is cleared once satisfied or
  when you navigate yourself. The same stale state could also send the
  search-page auto-jump hunting for a StatPearls term inside DrugBank's
  results; it is now scoped to the site the popup pointed at.
- **Switching theme no longer reports an error.** `_ResultsSection`
  called `set_results`, which does not exist - the method is
  `show_results`. The restyle aborted at that point every time.
- **The welcome dialog sizes to its contents.** It was fixed at
  520x460, leaving a third of the pane empty with the Continue button
  marooned at the bottom - which reads as content that failed to load.
- **Settings text no longer clips.** Indented descriptions used
  contents margins, which narrow a label's text without changing the
  height it reports to the layout, so the second line was painted under
  the widget below. Descriptions are short single lines now, and the
  long explanatory paragraphs have moved to tooltips.

## [1.4.1] - 2026-08-14

### Added

- **Sent text now lands in the chat box.** `Ctrl+Shift+K` and
  `Ctrl+Shift+J` previously stopped at the clipboard and asked you to
  paste. They now open the dock, focus the provider's message box and
  paste for you. Nothing is submitted - the text sits in the box for
  you to read, edit and send. Turn it off under Settings > Services >
  AI chat if you would rather only the clipboard were touched.
- **Custom popup terms have a proper editor.** Settings > General >
  Custom terms opens a table with Add and Remove, replacing the raw
  JSON textarea where one missing comma silently disabled every custom
  term with no feedback anywhere.

### Changed

- **Shortcut changes apply immediately.** Bindings were only read at
  launch, so changing one in Settings appeared to do nothing until the
  next restart - unhelpful, given the usual reason to change a shortcut
  is a clash you want gone now.
- **The Reference tab has been folded into General.** Two checkboxes
  and a button did not justify a tab, and it read as a peer of Services
  and Shortcuts when it belongs with the module switches above it.
- **The 1.4 upgrade notice now reaches everyone upgrading from below
  1.4.** It was shown only to users still sitting on `Ctrl+Shift+P`, so
  anyone who had already rebound that key by hand never heard that
  shortcuts had become editable or that a whole-card shortcut existed.
  Installs now record which version they last ran.

### Fixed

- **Switching Anki's theme restyles all three sidebars.** The
  StatPearls panel raised `NameError: name '_theme' is not defined` on
  the first line of its restyle, so nothing after it ran; the UpToDate
  and AI chat docks had no restyle path at all and kept whichever theme
  they were built with until Anki restarted.

## [1.4] - 2026-08-14

### Added

- **A StatPearls / DrugBank switch in the sidebar header.** Which site
  you were on was the panel's most important state and the only way to
  change it was a dropdown hidden on the home button, so searching
  DrugBank was effectively undiscoverable. It is now two pills showing
  where you are, and clicking one takes you there.
- **Send the whole card to the AI chat** with `Ctrl+Shift+J`. Copies
  everything currently visible - cloze deletions resolved, the answer
  included once revealed, popup and dock chrome excluded - and opens the
  chat dock ready to paste.
- **Shortcuts are editable in Settings.** A clash with another add-on is
  the most likely reason to change a binding, and the only way to do it
  was hand-editing JSON. Clear a field to disable that shortcut.

### Changed

- **Settings has been rebuilt to look and behave like Anki's own
  Preferences.** Tabbed rather than one long scroll, native controls
  throughout instead of custom-coloured cards and pills, and changes
  written when you close the window rather than gated behind a Save
  button. Shortcuts are edited by clicking the field and pressing the
  keys.
- **The send-to-chat shortcut is now `Ctrl+Shift+K`**, because
  `Ctrl+Shift+P` is Anki's own Switch Profile binding and could bounce
  you to the profile picker mid-review. Existing users are asked once
  whether to move to the new default or keep what they have.
- **Settings no longer restarts Anki.** The Save button was labelled
  "Save & restart Anki", with a checkbox you had to tick to avoid
  quitting mid-session. Anki's own convention is followed instead: a
  quiet note that some settings need a restart, and you restart when it
  suits you.

### Fixed

- Clicking a link while the sidebar's home page was still loading could
  raise an Anki error report, even though the page then loaded fine. The
  abandoned load is now recognised as superseded rather than failed, and
  routine retries are recorded to the diagnostic log instead of being
  raised as errors.
- The home button kept the styling of the dropdown it used to be,
  leaving a mismatched hover area next to the other navigation buttons.

## [1.3.2] - 2026-08-12

### Added

- 92 more conditions link directly to their article, covering entries
  filed under a synonym rather than the name used here - acoustic
  neuroma under vestibular schwannoma, chilblains under pernio,
  age-related hearing loss under presbycusis. 639 of 828 conditions now
  open their article in one step.

### Changed

- Where a matching article covers a different entity, a broader class or
  a narrower subtype than the term as taught, no link is used and the
  search is shown instead. Reading the wrong chapter unaware is worse
  than an extra click, and nothing on the page would signal the swap.

## [1.3.1] - 2026-08-12

### Added

- 46 further conditions now link directly to their StatPearls chapter.
  These are entries whose article is filed under the American spelling -
  hyponatraemia, coeliac disease, subarachnoid haemorrhage, transient
  ischaemic attack and similar - which previously found nothing. 547 of
  828 conditions now open their article in one step.

## [1.3] - 2026-08-12

### Added

- 501 conditions now carry a direct StatPearls link, so "Open article"
  opens the chapter immediately with no lookup and no network delay.

### Fixed

- Chapter links are only used where the article genuinely is the
  condition. Terms that matched a narrower article - "Stroke" matching
  "Heat Stroke", "Sepsis" matching "Neonatal Sepsis", "Hypertension"
  matching "Portal Hypertension" - now fall back to a search instead,
  since the opened page gives no sign that it is the wrong one.
- Links remembered by earlier versions are discarded on upgrade. Those
  could point at an unrelated article, and there is no way to tell which
  ones, so they are all rebuilt.

## [1.2.7] - 2026-08-12

### Fixed

- Chapter lookup could open an unrelated article. NCBI indexes
  StatPearls by section rather than by chapter, so a search returned
  headings like "Morphology" and the add-on followed them to whichever
  chapter they belonged to. Lookups now match on chapter titles, and a
  term whose chapter cannot be identified confidently falls back to a
  search rather than opening something that only looks plausible.

## [1.2.6] - 2026-08-12

### Fixed

- **Drug popups opened StatPearls pages instead of DrugBank.** The
  chapter lookup added in 1.2.5 was being applied to every popup rather
  than only StatPearls ones, so clicking through from a drug searched
  StatPearls for the drug name and opened whatever it found. Drug links
  behave as they did before 1.2.5 again.
- Remembered links are now kept separately for drugs and conditions, so
  a drug and a condition sharing a name cannot overwrite each other.

## [1.2.5] - 2026-08-12

### Fixed

- **"Open article" now goes to the article.** It was landing on
  StatPearls' in-book search results, which only redirects onward when a
  search happens to have exactly one hit - so common terms with several
  matching chapters stopped there, and that results page does not
  display in the panel at all. The term is now looked up on NCBI first
  and the chapter opened directly.
- Lookups prefer the current chapter over retired ones, which NCBI keeps
  in its index and which carry an out-of-date warning.

## [1.2.4] - 2026-08-12

### Fixed

- The article panel could finish loading a page and still show nothing.
  The page itself was fine - correct address, correct title, full
  content - but was never drawn, leaving an empty rectangle. The panel
  now forces the view to redraw once a page has loaded.
- NCBI redirects its in-book search address to the book's own page with
  the search preserved, which the add-on did not recognise. As a result
  a search never resolved to the chapter, and the search results page
  itself risked being remembered as though it were the article.

## [1.2.3] - 2026-08-12

### Added

- A diagnostic log at `user_files/diagnostic.log`, reachable from
  Tools > The AnkiDote > Show diagnostic log. It records every
  navigation the article panel makes and what the loaded page actually
  contained, which is the information needed to work out why a panel
  came up empty.

## [1.2.2] - 2026-08-12

### Fixed

- The article panel could go blank with no explanation. When the
  embedded browser engine's renderer process stops, Qt leaves the view
  painted empty, which looks identical to a page that simply loaded
  nothing. The panel now reports what happened, stops reloading after
  three consecutive failures instead of retrying indefinitely, and
  offers to open the page in your normal browser.
- Showing the dock and loading a page in the same action could start two
  navigations, with the second cancelling the first and the cancellation
  being reported as a load failure. This affected the "Open article"
  path specifically.

## [1.2.1] - 2026-08-12

### Fixed

- **"Open article" crashed instead of opening anything.** A redundant
  local import shadowed the module-level `unquote`, which made the name
  local to the whole function and turned the earlier call on that path
  into an `UnboundLocalError`. Every article click failed with a
  traceback, so nothing added in 1.2 - the article resolver, the section
  jump, the DrugBank auto-jump - could run at all. A check for this class
  of shadowing has been added to the test suite.

## [1.2] - 2026-08-11

### Fixed

- **The StatPearls panel no longer opens blank.** Two separate causes,
  both most visible when using "Open article" from a popup. Clicking it
  started the page load before showing the dock, so the renderer was
  handed a zero-size viewport and could finish loading with nothing
  drawn; and a failed or superseded navigation left the view parked on
  Chromium's internal error page, which paints as an empty grey
  rectangle with no message. Loads now begin only once the dock is
  visible, an in-flight load is stopped before a new one starts, a
  failed load retries once, and a second failure shows a readable
  message with a retry link instead of nothing at all. Surfacing the
  panel onto a blank page also triggers a reload.
- **Roughly 10% of the condition library was unreachable.** 111
  condition names appeared more than once, and because lookups resolve
  to the first match, the earliest and almost always briefest version
  was the one shown while the fuller rewrite sat unused. Duplicates are
  now merged, keeping the richest summary and the combined aliases of
  every copy. Breast cancer, infective endocarditis, lung cancer,
  syphilis and ankylosing spondylitis were among the worst affected.
- **Australian spellings now match.** Terms such as `haemophilia`,
  `hyponatraemia`, `coeliac disease`, `transient ischaemic attack` and
  `ischaemic colitis` are recognised in cards, and popup titles display
  the Australian form rather than the American one. American spellings
  are retained as aliases, so cards written either way still match.
- `CoA` no longer highlights as coarctation of the aorta on
  biochemistry cards, where it means coenzyme A.
- Epidural/extradural haematoma and the two gastro-oesophageal reflux
  entries were duplicate records of the same entity under different
  names, and are now single entries.

- **"Open article" now opens the article.** Every condition and 47% of
  drugs had no direct link, so the button loaded a search results page
  and left you to click again — which is most of why the sidebar was
  worth skipping. The panel now resolves the term to the real chapter or
  drug page, via NCBI's E-utilities for StatPearls and by following an
  unambiguous exact match for DrugBank, and caches the result so it only
  ever happens once per term. Ambiguous searches still show the results
  page, since that genuinely is the right answer there.
- **Section labels in a popup are now clickable.** Clicking `Mx`, `Ix`,
  `Sx` and the rest opens the article scrolled to the matching StatPearls
  section (Treatment / Management, Evaluation, History and Physical…),
  so the popup covers the summary and one click reaches the detail.
- Part of the popup stylesheet was silently discarded. A missing string
  concatenation left JavaScript's automatic semicolon insertion to split
  the declaration, dropping every rule after it — the UpToDate chips,
  section labels and rarity styling were unstyled as a result.
- **The add-on follows Anki's theme when it changes mid-session.**
  Previously the palette was fixed when Anki started, so switching
  light/dark left the docks on the old colours until restart.

### Changed

- Drug and condition text follows Australian conventions: INN and
  Australian generic names (adrenaline, salbutamol, ciclosporin,
  rifampicin, indometacin, pethidine, mesalazine and others), SI units
  in place of `mEq/L`, and "boxed warning" in place of the US-specific
  phrasing. Claims of US regulatory approval are now labelled as US
  rather than presented as though they applied locally.
- 15 drugs listed twice under both their American and Australian names
  are now single entries carrying both, so brand names and summaries no
  longer split across two records.

## [1.1.7] - 2026-08-11

### Fixed

- Term popups no longer run off the bottom of the screen. A popup now
  measures itself against the available space and opens above the term
  when there isn't room below; if neither side fits, it clamps to the
  roomier side and scrolls internally. Horizontal clamping now uses the
  popup's real width instead of a hard-coded one.
- Popup styling stays stable while you read: hovering away and back, or
  flipping to the answer side, no longer re-rolls a popup's appearance.
  It's now settled once per card and resets on the next card.

### Changed

- Minor visual polish.

## [1.1.6] - 2026-05-22

### Changed

- Minor visual polish.

## [1.1.5] - 2026-05-19

### Changed

- Picking a provider from the inline button or `▾` overflow menu now
  also persists it as `chatHomeUrl` (the default home URL), not just
  `chatLastUrl` (the last-session URL). Net effect: the LLM you
  selected stays the default going forward even if `chatLastUrl` is
  ever cleared.

## [1.1.4] - 2026-05-19

### Fixed

- AI chat dock no longer slows down provider loads. Previously the
  `urlChanged` handler treated every intermediate URL (about:blank,
  CSP redirects, internal SPA routes) as a fake provider crossing -
  because `_provider_for_url` defaulted to "Claude" for any
  unrecognised URL - and fired a meta.json fsync + full toolbar HTML
  rebuild + JS injection on every flap. We now use an `_explicit_`
  provider matcher that returns `None` for opaque schemes and
  unknown hosts, and gate all side effects on an explicit match.

### Changed

- Addon no longer has a baked-in Claude preference. The default home
  URL and the fallback provider label are now derived from the first
  entry in the user's in-app provider order (`chatProviders` config
  if set, else `DEFAULT_PROVIDERS`). The bundled order still has
  Claude first; reorder `DEFAULT_PROVIDERS` and the default follows.
  `chatHomeUrl` default is now `null` (meaning "use the first provider
  in order"); existing users with `https://claude.ai/new` saved
  explicitly are unaffected.

## [1.1.3] - 2026-05-19

### Fixed

- Top-toolbar AI chat icon now repaints reliably on every provider
  switch. The 1.1.2 fix relied on `mw.toolbar.redraw()` re-firing the
  `top_toolbar_did_init_links` hook with the fresh `chatLastUrl`; on
  the Anki release Rob is running, the redraw path doesn't actually
  repaint inline base64 `<img>` data URIs, so the old provider's logo
  stuck. We now also patch the link element's `innerHTML` directly
  by id from JS, which is invariant to whatever the surrounding
  redraw mechanism is doing.

## [1.1.2] - 2026-05-19

### Fixed

- Top-toolbar AI chat button now repaints its provider logo
  synchronously when the user picks a different LLM from the inline
  or overflow provider switcher. Previously the icon could lag a tick
  behind the click while the new page started loading. The toolbar
  also re-syncs when an in-page navigation crosses a provider
  boundary (e.g. an OAuth bounce back to the host site).

## [1.1.1] - 2026-05-12

### Changed

- Welcome dialog now recommends only Image Occlusion. The FSRS Helper
  recommendation has been removed; the rest of the dialog is unchanged.

### Fixed

- Capitalisation variants of the same term no longer appear as separate
  synonyms. Aliases that differ from the canonical name only in case
  have been pruned (10 conditions, 6 drugs), and the lookup builders now
  case-insensitively dedup names at load time so future entries can't
  reintroduce the issue.

## [1.1.0] - 2026-05-12

### Added

- Preclinical / basic-science term library (344 entries) covering
  physiology, biochemistry, microbiology, immunology, pathology,
  pharmacology, anatomy, histology, embryology, genetics, and
  biostatistics. Popups link to Wikipedia for further reading.
  Fully free, no UpToDate dependency.
- First-run welcome dialog: recommends one companion AnkiWeb addon
  (Image Occlusion 1374772155) with detection of whether it is
  already installed.
- Eponym and abbreviation aliases for 226 existing conditions (Wegener /
  GPA, Hashimoto / chronic lymphocytic thyroiditis, Reiter / reactive
  arthritis, STEMI / NSTEMI / MI, HFrEF / heart failure, COPD, etc.)
  so the underliner catches both the classic eponym and the modern
  name.
- StatPearls dock: home button is now a split toggle (StatPearls
  home or DrugBank home), persists the choice across restarts.
- Chat dock: subtle Dr House quote in the header, surfaced every
  10 to 20 dock-opens.

### Changed

- Welcome dialog redesigned: three "module cards" with descriptions
  and shortcut chips, tighter layout, no more empty vertical band.
- AI chat dock: only the currently-selected provider renders inline;
  all other providers live in a single dropdown menu next to it.
- Top toolbar AI icon now reflects the currently-active provider in
  real time.
- StatPearls pages: the NCBI Bookshelf top-of-page search strip is
  hidden, removing the visual ambiguity with the per-book "Search
  this book" form (which is auto-focused on open).
- DrugBank handling strengthened: unmapped drugs now resolve to a
  DrugBank "unearth" search instead of falling back off-site.

### Removed

- DailyMed fallback URL (DrugBank-only now).
- Back / Forward navigation arrows in the AI chat dock header
  (rarely useful; provider switching already triggers a fresh load).

## [1.0.4] - 2026-05-10

### Added

- "Clear session" button (⎚) in the UpToDate dock nav header. Wipes
  the dock's cookies, HTTP cache, and current-page web storage on the
  UTD profile, then reloads the home URL. Recovery path for users
  stuck on a wedged SSO/login error (e.g. Oracle Access Manager
  "System error", stale OpenAthens/Shibboleth jsessionids, expired
  HCN proxy tokens) where the existing cookie is invalid but the
  server won't issue a clean redirect. Confirms before clearing;
  local state only - does not log the user out at their IdP.

## [1.0.3] - 2026-05-09

### Fixed

- First-run / "Run setup again…" dialog now exposes the institution
  URL field so HCN-proxy (NSW Health, Vic Health) and other custom-
  entry users can set `uptodateHomeUrl` from the welcome flow. Previous
  behaviour: re-running setup just reloaded the configured URL, which
  for non-default institutions was the public UTD page - leaving the
  user apparently signed out with no in-app way to point the dock at
  their proxy entry.
- `uptodate/__init__.py` module docstring corrected: it claimed the
  default home URL was the HCN proxy, but the actual default is the
  public UpToDate search page. Updated to match `_DEFAULTS` and
  `config.md`.

## [1.0.2] - 2026-05-06

### Changed

- StatPearls side panel auto-focuses the "Search this book" input on
  NCBI Bookshelf landing pages whenever it loads or is reopened via
  the toolbar button. Means you can hit the toolbar shortcut and
  immediately start typing a query without first clicking into the
  text field. No-op on chapter pages or non-bookshelf URLs.

## [1.0.1] - 2026-05-06

Pre-publication content + UX cleanup.

### Removed

- **Per-card NCBI auto-search.** The previous flow made three
  sequential PubMed E-utilities round trips (esearch + esummary +
  efetch) every time a card was shown, taking 1–4 seconds and showing
  a "SEARCHING STATPEARLS…" stub the whole time. The article-list
  section in the side panel is now fed exclusively by instant
  local-database matches (StatPearls and DrugBank entries already
  detected on the card). When there are no local matches, the list
  section is hidden entirely. Popup highlighting and click-to-open-
  article in the webview are unaffected and remain instant. Removes
  the `autoSearch` and `maxResults` config keys.

### Fixed

- `Settings…` dialog no longer crashes on open (`_Qt` undefined-name
  bug introduced when the Qt import was scoped into `_qt_imports()`).

### Changed

- Deduplicated the bundled term databases: 9 silently-overwritten
  acronym entries and 9 silently-overwritten drug entries removed,
  keeping the longer/more curated definition in each pair.
- `manifest.json` `min_point_version` bumped from 49 → 50 (Qt6 was
  Anki's default from 2.1.50, matching the addon's `tested_on_qt5:
  false`). Legacy AnkiPearls / UpToAnki / AnkiDate side-loaded
  installs are now declared in `conflicts` so Anki disables them.

## [1.0.0] - 2026-05-05

First public AnkiWeb release. Unifies the previous AnkiPearls and
AnkiDate addons into a single package and adds a third AI-chat module.

### Added

- AI chat side dock (Claude / ChatGPT / Gemini / Copilot / Perplexity /
  DeepSeek / Grok / Duck.ai) with one-click provider switching and an
  overflow `▾` menu when more than five providers are configured.
- "Open externally" `↗` button in every dock header - opens the
  current page in the user's system browser, the escape hatch for
  passkey sign-in, video DRM, and other features that embedded
  webviews can't trigger.
- Send-selection-to-chat keyboard shortcut (`Ctrl+Shift+P`).
- Custom popup terms (`customTerms` config key) - user-defined JSON
  array of `{title, summary, url}` merged into the reviewer's
  highlight set alongside the bundled term databases.
- "Run setup again…" Tools menu entry to retrigger the welcome dialog.
- "Help / FAQ (open online)" Tools menu entry pointing at the README.
- Toolbar button order Settings drag-list (chat ↔ UpToDate).
- Save-without-restart checkbox in Settings.
- Optional dock-state persistence (`rememberDockState`) - reopen the
  same docks at the next Anki launch.
- Verbose debug logging gated by the `debug` config flag.
- Renderer-crash auto-recovery for the chat and StatPearls docks
  (UpToDate dock already had this).
- Legacy AnkiPearls / AnkiDate config-key migration on first launch
  after upgrade.
- Cross-source acronym → condition unification (e.g. "MI" expands to
  "Myocardial infarction" with the full condition summary).
- British / American spelling normalisation in the acronym → condition
  resolver so "Acute lymphoblastic Leukemia" matches the British
  "Leukaemia" canonical entry.

### Changed

- **Cloudflare bypass**: replaced the previous heavy stealth JS stack
  (navigator.webdriver delete, sec-ch-ua headers, fake PluginArray,
  Function.prototype.toString proxy, etc.) with a minimal AT V2-style
  profile setup - `ForcePersistentCookies` + standard QtWebEngine
  attributes. The stealth tricks were tripping Cloudflare's tamper
  detection; the minimal profile clears Turnstile cleanly.
- Default UpToDate home URL changed from the NSW/Vic Health HCN proxy
  to the public `https://www.uptodate.com/contents/search` so non-AU
  users get a working default. NSW/Vic Health and other institutions
  with a custom SP-initiated URL set theirs in Settings.
- Settings dialog split into per-module group boxes for readability;
  added "Other" group with `rememberDockState` and `debug` toggles.
- Toolbar redraws coalesce to one per event-loop tick instead of one
  per call site.
- Favicon disk writes throttled to one save per provider per minute.
- Config cache switched from a 2 s TTL to invalidate-on-write - O(1)
  reads after first load.
- DrugBank banner-hider tightened to a fixed selector list with a
  250 ms-debounced MutationObserver. The previous full-DOM
  `querySelectorAll('*')` sweep is gone.

### Removed

- **Per-card NCBI auto-search.** The previous version made three
  sequential PubMed E-utilities round trips (esearch + esummary +
  efetch) every time a card was shown, taking 1–4 seconds and showing
  a "SEARCHING STATPEARLS…" stub the whole time. The article-list
  section in the side panel is now fed exclusively by instant
  local-database matches (StatPearls and DrugBank entries already
  detected on the card). When there are no local matches, the
  list section is hidden - no empty stub, no spinner. Popup
  highlighting and click-to-open-article in the webview are
  unaffected and remain instant. Removes the `autoSearch` and
  `maxResults` config keys.
- "Copy current card" 📋 button in the chat dock (the same flow is
  now `Ctrl+Shift+P`, freeing the slot for "Open externally").
- Dead `QTWEBENGINE_CHROMIUM_FLAGS` env-var assignment at module load
  (no-op because Anki's QApplication has already been constructed by
  the time addons load).
- Stealth JS injection module - see "Changed → Cloudflare bypass".

### Fixed

- Toolbar button order now actually reorders chat ↔ UpToDate. Prior
  versions read `toolbarOrder` from config but both modules used the
  same fallback `links.append()` path so the configured order was
  ignored.
- "Save & restart Anki" no longer crashes Anki or loses pending
  changes - switched from `mw.app.exit(0)` (which bypasses
  `unloadProfile`) to `mw.unloadProfileAndExit()`.
- Settings button label now actually relaunches Anki rather than just
  quitting.

### Security

- Replaced ad-hoc `try / except: pass` blocks with a centralised
  logging shim that writes to stderr at WARN/ERROR level. Users can
  enable `debug: true` for full tracebacks when filing bug reports.
- pycmd `tad_open:` URL handler now logs cross-origin navigations to
  unrecognised hosts at debug level (still allowed, http/https only,
  but auditable).

### Known limitations

- Passkey / Touch ID sign-in does not trigger inside QtWebEngine on
  macOS (platform-authenticator entitlement restriction). Workaround
  documented in Settings and README.
