#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Install TheAnkiDote 2.0.0 into the local Anki add-ons directory.
#
#   1. Quit Anki.
#   2. Put this script next to theankidote-2.0.0.ankiaddon.
#   3. bash install.sh
#
# Add-ons live in ONE directory shared by every profile:
#
#   macOS  ~/Library/Application Support/Anki2/addons21/<package>
#   Linux  ~/.local/share/Anki2/addons21/<package>
#
# They are not per-profile. An earlier version of this script walked
# Anki2 looking for a profile directory and picked `addons21` itself,
# installing to Anki2/addons21/addons21/theankidote - a path Anki never
# reads, so the add-on silently did not appear. If that happened to you,
# this script removes the stray directory.
set -euo pipefail

PKG="theankidote"
ADDON="$(cd "$(dirname "$0")" && pwd)/theankidote-2.0.0.ankiaddon"

case "$(uname -s)" in
  Darwin) BASE="$HOME/Library/Application Support/Anki2" ;;
  Linux)  BASE="${XDG_DATA_HOME:-$HOME/.local/share}/Anki2" ;;
  *)      echo "Unsupported platform: $(uname -s)" >&2; exit 1 ;;
esac

[ -f "$ADDON" ] || { echo "Not found: $ADDON" >&2; exit 1; }
[ -d "$BASE" ]  || { echo "No Anki data directory at $BASE" >&2; exit 1; }

if pgrep -x "Anki" >/dev/null 2>&1; then
  echo "Anki is running. Quit it first - add-ons are loaded at startup." >&2
  exit 1
fi

ADDONS="$BASE/addons21"
mkdir -p "$ADDONS"
DEST="$ADDONS/$PKG"

# Clean up the bad path the earlier script could create.
STRAY="$ADDONS/addons21"
if [ -d "$STRAY" ]; then
  echo "Removing stray install at $STRAY"
  rm -rf "$STRAY"
fi

STAMP="$(date +%Y%m%d-%H%M%S)"
if [ -d "$DEST" ]; then
  BACKUP="$ADDONS/.$PKG-backup-$STAMP"
  cp -R "$DEST" "$BACKUP"
  echo "Backed up existing install to $BACKUP"
  # Keep per-install state, replace everything else.
  find "$DEST" -mindepth 1 -maxdepth 1 \
       ! -name 'user_files' ! -name 'meta.json' -exec rm -rf {} +
fi

mkdir -p "$DEST"
unzip -oq "$ADDON" -d "$DEST"

# A correct install has the package's own files at the top level.
[ -f "$DEST/manifest.json" ] || {
  echo "Install looks wrong: no manifest.json in $DEST" >&2; exit 1; }

echo "Installed TheAnkiDote 2.0.0 to $DEST"
echo
echo "Start Anki, then check Tools > Add-ons - it should be listed as"
echo "The AnkiDote, version 2.0."
echo
echo "Content updates are off by default. Enable them under"
echo "Tools > Add-ons > The AnkiDote > Config with \"libraryAutoUpdate\": true."
