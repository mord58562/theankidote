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

Content versions are compared as strings, so they must sort upwards.
`YYYY.MM.DD` does. Anything that sorts below what a client already holds
publishes fine and reaches nobody, which is why the script refuses it.

Nothing here reviews the content. AnkiWeb is out of the loop by design,
so the test suite is the only gate, and the script will not push if it
fails.
