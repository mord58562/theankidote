#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
#
# Print the sha256 of .remote-agent-context.md.
#
# Paste the result into the scheduled remote agent's config on
# claude.ai/code/environments as `EXPECTED_CONTEXT_SHA` after any
# legitimate edit to the context file. The routine's Section 0
# integrity check refuses to run if the hash on disk does not match
# this value - the whole point is that a repo compromise that
# rewrites the context file cannot hijack the routine, because the
# routine's expected hash lives outside the repo.

set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .remote-agent-context.md ]; then
  echo "no .remote-agent-context.md in $(pwd)" >&2
  exit 1
fi
shasum -a 256 .remote-agent-context.md | cut -d' ' -f1
