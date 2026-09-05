# What's new in The AnkiDote 2.1

## The search bar is back on StatPearls articles

The sidebar hides NCBI's own search bar on the StatPearls landing page,
because the page already has a "Search this book" box doing the same job
in the middle of the screen. It turned out to be hiding it on article
pages too - which is the one place it is the only way to search the book
without navigating back first.

## Forty-one more conditions rewritten

Lung cancer, lithium toxicity, miscarriage, polycystic ovary syndrome,
cystic fibrosis, pre-eclampsia, paracetamol overdose, oesophageal
varices, acute pancreatitis, diabetes insipidus, phaeochromocytoma,
hyperosmolar hyperglycaemic state, sickle cell disease, bowel
obstruction, nephrotic syndrome, abruption, aortic aneurysm, portal
hypertension, ectopic pregnancy, peripheral arterial disease, urinary
incontinence, cluster headache, tension headache, medication overuse
headache, prostate cancer, acute tubular necrosis, osteomyelitis,
subdural haematoma, chronic pancreatitis, amenorrhoea, rheumatic heart disease, diverticular disease, cerebral venous sinus thrombosis, haemorrhoids, acute angle-closure glaucoma, osteomalacia, rickets, anal fissure, uveitis, Huntington disease and chronic fatigue syndrome.

Chosen the same way as the last batch: by how often each actually comes
up, not by how badly each overflowed. Those two orderings keep
disagreeing. Breast cancer is the third tallest entry left in the
database and comes up twice; lung cancer comes up fifty-two times. Acute
appendicitis, also over the limit, does not come up at all.

All forty-one now fit the popup without scrolling. Australian sources
throughout - eTG, AMH, PBS, RANZCOG, and the Poisons Information Centre
number where it matters.

## Australian drug names

Twenty-three drug spellings that Australian cards routinely use matched
nothing at all - `frusemide`, `cephalexin`, `cephazolin`, `thyroxine`,
`glyceryl trinitrate`, `valproate` and others. No popup appeared, which
is easy not to notice because there is nothing there to look wrong. All
now highlight.

Five drugs were also being shown under their American names, and were in
fact stored twice, once under each. Pethidine, rifampicin, oestradiol,
lignocaine and glyceryl trinitrate now display the Australian name;
cards written the American way still work.

## Settings explains itself less

Five captions that restated the control they sat under are gone, and
three more are shorter. The ones that tell you a rule you could not
otherwise work out - that a link has to start with `http://`, that
leaving a shortcut field empty turns it off, that passkey sign-in will
not work in an embedded browser - are still there.

## Security

2.0 moved the reference database out of the add-on and onto a download
channel. That was the right change, and it altered what the add-on has
to defend against: the summaries, the links inside them and the shape of
the file are no longer written by one person. This release is the result
of going back through those paths properly.

The most serious finding: a malformed download could disable the add-on
permanently. Validation checked the first entry in the file and trusted
the rest, so a bad entry further down passed the check, was saved, was
preferred at every launch afterwards, and then failed on startup. The
switch to turn updates off is inside the add-on that was no longer
loading, so the only way out was deleting a file by hand. The whole file
is now checked, and a download that fails is set aside rather than
retried forever.

The other change you may notice: clicking a highlighted word only opens
the sidebar for services The AnkiDote actually integrates with, or for
sites you have pointed it at yourself in Settings. Anything else opens
in your normal browser instead. The sidebar keeps you signed in to
NCBI, DrugBank and UpToDate, and a highlighted word is set by an
ordinary HTML attribute that any shared deck can write - so a deck
could previously send that signed-in window anywhere. Your own custom
terms are unaffected, whatever you have pointed them at.

Also fixed: update addresses are now required to be secure ones, and
rechecked if the server redirects; downloaded content can no longer
carry a link that is not an ordinary web link; and saving a download can
no longer be diverted to write somewhere else on disk.

None of this is known to have been exploited, and all of it needed
either control of the update host or access to your add-on folder. There
is nothing you need to do beyond updating.

## Under the hood

Forty-six new tests, one for each of the above, so none of them come
back quietly. The suite is 169 tests.

---

**Upgrading:** nothing to do. Your settings, shortcuts and dock layout
carry over untouched.
