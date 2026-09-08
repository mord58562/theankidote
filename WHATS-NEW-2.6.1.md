# What's new in The AnkiDote 2.6.1

A patch on top of 2.6, fixing one thing that could take your Escape key
away and sharpening a lot of numbers.

## Escape works again

If your Escape key had stopped closing the note editor, or the reference
sidebar opened whenever you pressed it, this is the fix.

The shortcut fields in Settings record whatever key you press. Press
Escape while one of them has focus - which is what most people do to get
out of a field they did not mean to edit - and Escape was recorded as
the shortcut. Because these bindings are deliberately global, so that
they work while you are reviewing a card, Escape was then taken from
Anki everywhere: in the editor, in the browser, in every dialog. And
there was no way back, since the field showed "Esc" and pressing Escape
to change it entered Esc again.

Escape can no longer be bound, with or without a modifier. Neither can a
plain key without one, which would fire while you are typing. If one was
already saved, it is cleared when Anki next starts.

## Reference numbers, in Australian units

Around 85 of the abbreviation popups carried a definition and no
numbers, which is the half you already knew. HbA1c said it "reflects
average blood glucose" without telling you that 48 mmol/mol diagnoses
diabetes and 42 to 47 is the prediabetes band. Those now carry the
thresholds, ranges and targets, in the units Australian laboratories
actually report.

Several were not merely thin but wrong for anyone practising here:

- **Hypertension** was defined as 140/90 in the condition entry and
  130/80 in the abbreviation - the American threshold. Both now say
  140/90 clinic, 135/85 on home or ambulatory monitoring.
- **FBE** was described as the American name for the full blood count.
  It is the Australian one; CBC is American.
- **PSA** now carries the Australian testing guideline: 2-yearly from 50
  to 69, or 45 with a family history, and 3.0 as the repeat threshold
  rather than the 4.0 from American sources.
- **Stroke risk in atrial fibrillation** uses CHA2DS2-VA, which is the
  Australian score with the sex point removed.
- **Community-acquired pneumonia** points at SMART-COP, which is what
  Therapeutic Guidelines uses, rather than CURB-65.
- The **haemoglobin reference interval** appeared twice in the library
  with two different sets of numbers. Both now give the harmonised one.

Where a number is genuinely laboratory-dependent it says so instead of
inventing a precision it does not have, and where it could not be
sourced confidently it was left out rather than guessed.

## Popups look like what they are

A popup summarising a real StatPearls chapter and one written for this
add-on were the same colour, so the badge that tells you which is which
was contradicted by everything around it. Add-on summaries now have
their own accent.

## Smaller things

- The version in Settings briefly showed the content version twice.
- The reference sidebar's open and closed state could disagree with the
  toolbar button after Anki moved the panel itself.
- Switching Anki profiles with the chat sidebar mid-load could raise an
  error rather than closing quietly.

Nothing here changes the content format, so your reference library
carries over untouched.
