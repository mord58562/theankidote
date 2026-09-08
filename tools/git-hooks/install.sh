#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
#
# Install this repository's git hooks. .git/hooks is not tracked, so a
# fresh clone has none until this runs.
set -euo pipefail
cd "$(dirname "$0")/../.."
for hook in tools/git-hooks/*; do
  name=$(basename "$hook")
  [ "$name" = "install.sh" ] && continue
  cp "$hook" ".git/hooks/$name"
  chmod +x ".git/hooks/$name"
  echo "installed .git/hooks/$name"
done
