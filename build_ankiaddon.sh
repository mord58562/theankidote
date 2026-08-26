#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Build a clean .ankiaddon zip for AnkiWeb upload.
#
# Usage:  ./build_ankiaddon.sh
# Output: theankidote-<version>.ankiaddon in the repo root
#
# Excludes meta.json (per-install state), user_files/ (per-install
# state including session cookies and any downloaded term library),
# __pycache__, .DS_Store, the build script itself, the build output,
# and dotfiles.  AnkiWeb rejects uploads containing any of those.
#
# data/library.json IS packaged: it is the entire term database since
# the 2.0 split. Excluding it ships an add-on that highlights nothing.
#
# data/manifest.json is NOT packaged. It exists to be published to the
# branch, where the updater fetches it over HTTPS; nothing in the
# running add-on ever opens it. Shipping it would put a download URL
# inside every .ankiaddon pointing at whichever content release happened
# to be current on packaging day.
#
# content/ and tools/ are NOT packaged: they are the authoring copy of
# the vocabularies and the compiler that turns them into data/. Shipping
# them would roughly double the download for files no user runs.
set -euo pipefail

cd "$(dirname "$0")"

VERSION=$(python3 -c 'import json; print(json.load(open("manifest.json"))["version"])')
OUT="theankidote-${VERSION}.ankiaddon"

rm -f "$OUT" theankidote-*.ankiaddon

zip -r "$OUT" . \
    -x "meta.json" \
    -x "HANDOVER*.md" \
    -x "WORKLIST.md" \
    -x "user_files/*" \
    -x "*/__pycache__/*" \
    -x "__pycache__/*" \
    -x ".DS_Store" \
    -x ".git/*" \
    -x ".gitignore" \
    -x "*.ankiaddon" \
    -x "build_ankiaddon.sh" \
    -x "tests/*" \
    -x "data/manifest.json" \
    -x "content/*" \
    -x "tools/*" \
    -x "*.pyc" \
    -x ".vscode/*" \
    -x ".idea/*" \
    -x ".pytest_cache/*" \
    -x ".claude/*" \
    -x ".theankidote-rollback/*" \
    -x "theankidote-publishing-instructions.txt" \
    -x "MIGRATION.md" \
    > /dev/null

echo "Built: $OUT ($(du -h "$OUT" | cut -f1))"
echo
echo "Update the existing listing at:"
echo "  https://ankiweb.net/shared/info/720072719"
echo "New-addon submissions only: https://ankiweb.net/shared/upload"
