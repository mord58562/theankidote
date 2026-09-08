# Authoring sources

Content lives here as Python, and ships as `data/library.json`.

The modules under `pearls/` no longer carry their vocabularies inline;
they call `_library.get(...)`. This directory holds the *authoring*
copy - Python literals, with comments, house-style notes and a shape
that produces a readable diff. `tools/build_library.py` compiles it.

`_rich.py` is here because it is the file that gets edited weekly. The
rest of the vocabularies were compiled into `data/library.json` once,
during the 2.0 split, and their authoring copies live in git history
rather than here; extract one from `data/library.json` if a bulk edit is
ever needed.

Workflow:

    $EDITOR content/_rich.py
    python3 tools/build_library.py
    python3 tests/test_vocab.py

`data/library.json` and `data/manifest.json` are build artefacts. Commit
them alongside the source edit, or the shipped add-on will not contain
the change.

This directory is **not** packaged into the `.ankiaddon`.

## Authoring a batch

Entries are usually written a topic at a time, often several batches in
parallel, as JSON:

    [{"name": ..., "aliases": [...], "utd": [["Overview", "..."]],
      "summary": "..."}]

Two scripts turn that into source, and they live in `tools/` because
both have now been written from scratch twice after the working copy
was left in a temp directory:

    python3 tools/verify_batch.py drafts/*.json   # check before merging
    python3 tools/merge_batch.py  drafts/*.json   # write into _rich.py

`verify_batch.py` checks what the suite checks, but before the batch is
inside a 3.5 MB source file where backing one entry out is a diff to
unpick rather than a file to delete: the popup height and character
budgets, the section-label whitelist, Australian spelling, banned
characters, and names or aliases that two batches both claim. Its one
check the suite cannot make is alias ambiguity - whether a short
all-caps alias would shadow the acronym dictionary - which it answers
against the running collection over AnkiConnect, pulled live every run.

`merge_batch.py` is also the right tool for a conflict in `_rich.py`
after the scheduled agent has pushed to this branch. Take the remote
file whole and re-apply the local batch through it. Resolving the text
by hand, or with a union merge, silently duplicates an entry both sides
added.

## Publishing content

    bash tools/publish_content.sh              # version defaults to today
    bash tools/publish_content.sh 2026.09.01   # explicit
    DRY_RUN=1 bash tools/publish_content.sh    # build and verify, push nothing

Run the dry run first. It builds, runs the suite, checks the manifest
against the library, and prints exactly what it would push.

The split is deliberate: `library.json` goes up as a release asset and
`manifest.json` is committed to the branch. The library is 2.1 MB and
changes every publish, so committing it each time would grow the
repository's permanent history by that much per edit; the manifest is
250 bytes and needs a URL that never moves, which is what the branch is
for.

Content versions are `DD.MM.YYYY`, with `.1`, `.2` and so on appended
from the second publish of a day onward. They are not compared as
strings: `_library._parse_version` reads both that shape and the
`YYYY.MM.DD` one used before 2026-08-28 into a `(year, month, day,
counter)` tuple, and `_updater._newer` compares the tuples. A version
that does not sort strictly after the one in `data/manifest.json`
publishes fine and reaches nobody, which is why the script refuses it -
except on the very first publish, where re-using the current version
seeds the channel deliberately.

Nothing here reviews the content. AnkiWeb is out of the loop by design,
so the test suite is the only gate, and the script will not push if it
fails.
