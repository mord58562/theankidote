#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Build a clean .ankiaddon zip for AnkiWeb upload.
#
# Usage:  ./build_ankiaddon.sh
# Output: theankidote-<version>.ankiaddon in the repo root
#
# Excludes meta.json (per-install state), user_files/ (per-install
# state including session cookies), __pycache__, .DS_Store, the build
# script itself, the build output, and dotfiles.  AnkiWeb rejects
# uploads containing any of those.
set -euo pipefail

cd "$(dirname "$0")"

VERSION=$(python3 -c 'import json; print(json.load(open("manifest.json"))["version"])')
OUT="theankidote-${VERSION}.ankiaddon"

rm -f "$OUT" theankidote-*.ankiaddon

zip -r "$OUT" . \
    -x "meta.json" \
    -x "user_files/*" \
    -x "*/__pycache__/*" \
    -x "__pycache__/*" \
    -x ".DS_Store" \
    -x ".git/*" \
    -x ".gitignore" \
    -x "*.ankiaddon" \
    -x "build_ankiaddon.sh" \
    -x "tests/*" \
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
echo "Upload at: https://ankiweb.net/shared/upload"
