#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 mord58562
# This file is part of TheAnkiDote. See LICENSE for details.
#
# Publish a new term library without touching AnkiWeb.
#
#   bash tools/publish_content.sh                 # today's date as version
#   bash tools/publish_content.sh 2026.09.01      # explicit version
#   DRY_RUN=1 bash tools/publish_content.sh       # build and check, push nothing
#
# What gets published where, and why they are split:
#
#   library.json  ->  a GitHub *release asset*, tagged content-<version>
#   manifest.json ->  committed to the default branch
#
# The library is 2.1 MB and changes on every content edit. Committing it
# to the branch each time would add 2.1 MB to the repository's permanent
# history per publish - git stores a new blob, not a delta, for anything
# it treats as binary-ish, and JSON this large diffs badly enough that it
# may as well be. A year of weekly edits is over 100 MB of history for a
# file nobody reads from git. Release assets live outside the object
# store and can be deleted later.
#
# The manifest is ~250 bytes, is what every client polls, and needs to be
# fetchable at a stable URL that never changes. That is exactly what the
# branch is good at. `raw.githubusercontent.com` caches for around five
# minutes, so allow for that before wondering why clients have not
# noticed.
#
# Requires: gh (authenticated), python3, git.

set -euo pipefail

cd "$(dirname "$0")/.."

VERSION="${1:-$(date +%Y.%m.%d)}"
TAG="content-${VERSION}"
DRY_RUN="${DRY_RUN:-0}"

die() { echo "error: $*" >&2; exit 1; }
step() { printf '\n\033[1m==> %s\033[0m\n' "$*"; }

# ── preflight ────────────────────────────────────────────────────────
step "Preflight"

command -v gh      >/dev/null || die "gh not installed - see https://cli.github.com"
command -v python3 >/dev/null || die "python3 not found"
gh auth status >/dev/null 2>&1 || die "gh is not authenticated; run: gh auth login"

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die \
"this must be run from inside your clone of the repository, not from
       wherever the script happens to sit. Try:

           cd ~/theankidote && bash tools/publish_content.sh

       The clone is the directory containing .git - the same one you
       pass to push-2.0.0.sh."

SLUG="$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null)" \
  || die "gh cannot identify this repository. Check \`git remote -v\`."
BRANCH="$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)"

# A dirty tree means the library you are about to build may not match
# the content you think you are publishing.
if [ -n "$(git status --porcelain -- content/ pearls/ tools/)" ]; then
  die "uncommitted changes under content/, pearls/ or tools/ - commit them first, or you will publish something that is not in the repository"
fi

if git rev-parse "$TAG" >/dev/null 2>&1; then
  die "tag $TAG already exists. Content versions are compared as strings and must increase; pick a later version."
fi

# The updater refuses anything not strictly greater than what the client
# already has, so a version that sorts below the shipped one publishes
# successfully and reaches nobody.
CURRENT="$(python3 -c 'import json;print(json.load(open("data/manifest.json"))["content_version"])' 2>/dev/null || echo "")"
if [ -n "$CURRENT" ] && ! python3 -c "import sys;sys.exit(0 if '$VERSION' > '$CURRENT' else 1)"; then
  die "version $VERSION does not sort after the current $CURRENT; clients would ignore it"
fi

echo "repository      $SLUG"
echo "branch          $BRANCH"
echo "version         $VERSION  (current: ${CURRENT:-none})"
echo "tag             $TAG"
[ "$DRY_RUN" = "1" ] && echo "MODE            dry run - nothing will be pushed"

# ── build ────────────────────────────────────────────────────────────
step "Building library"

ASSET_URL="https://github.com/${SLUG}/releases/download/${TAG}/library.json"
python3 tools/build_library.py --version "$VERSION" --url "$ASSET_URL"

# ── verify ───────────────────────────────────────────────────────────
step "Verifying"

# Publishing content that fails the suite is how a bad summary reaches
# every user at once, with no review step in the way. This is the only
# gate the content channel has.
FAILED=0
for t in tests/test_*.py; do
  if python3 "$t" >/dev/null 2>&1; then
    printf '  ok    %s\n' "$(basename "$t")"
  else
    printf '  FAIL  %s\n' "$(basename "$t")"
    FAILED=1
  fi
done
[ "$FAILED" = "0" ] || die "test suite failed; refusing to publish"

# The client checks the payload against the manifest before writing it,
# so a mismatch here means every download is discarded and no one can
# work out why. Check it now, while it is cheap.
python3 - "$VERSION" <<'PY'
import hashlib, json, pathlib, sys
version = sys.argv[1]
blob = pathlib.Path("data/library.json").read_bytes()
man = json.loads(pathlib.Path("data/manifest.json").read_text("utf-8"))
lib = json.loads(blob.decode("utf-8"))
assert man["sha256"] == hashlib.sha256(blob).hexdigest(), "manifest sha256 mismatch"
assert man["bytes"] == len(blob), "manifest byte count mismatch"
assert man["content_version"] == version, "manifest version mismatch"
assert lib["content_version"] == version, "library version mismatch"
assert man["schema"] == lib["schema"], "schema mismatch between manifest and library"
assert man.get("url"), "manifest has no url; the updater would ignore it"

# The overrides must not have been merged into the base text. If they
# have, the next edit to content/_rich.py is a silent no-op.
base = {c["name"]: c["summary"] for c in lib["conditions"]}
baked = [n for n, t in lib["rich_summaries"].items() if base.get(n) == t]
assert not baked, f"{len(baked)} override(s) baked into base text: {baked[:3]}"

print(f"  manifest and library agree ({len(blob) / 1024:.0f} KB, "
      f"sha {man['sha256'][:12]})")
PY

if [ "$DRY_RUN" = "1" ]; then
  step "Dry run complete"
  echo "Would tag       $TAG"
  echo "Would upload    data/library.json"
  echo "Would commit    data/manifest.json to $BRANCH"
  echo "Asset URL       $ASSET_URL"
  exit 0
fi

# ── publish ──────────────────────────────────────────────────────────
# Order matters. The asset goes up first: a manifest on the branch
# pointing at a release that does not exist yet means every client that
# polls in the gap downloads nothing, logs a failure, and waits for the
# next restart. Uploading first makes the gap harmless - the asset is
# simply not referenced until the manifest lands.
step "Creating release $TAG"

gh release create "$TAG" data/library.json \
  --title "Term library $VERSION" \
  --notes "Term library for TheAnkiDote, content version \`$VERSION\`.

Downloaded automatically by installs with \`libraryAutoUpdate\` enabled.
Requires schema $(python3 -c 'import json;print(json.load(open("data/manifest.json"))["schema"])') - that is add-on 2.0.0 or later.

sha256: \`$(python3 -c 'import json;print(json.load(open("data/manifest.json"))["sha256"])')\`"

step "Confirming the asset is reachable"
# GitHub redirects release downloads; -L follows it. A 404 here means
# the manifest would ship pointing at nothing.
HTTP="$(curl -sSL -o /dev/null -w '%{http_code}' "$ASSET_URL")"
[ "$HTTP" = "200" ] || die "asset URL returned HTTP $HTTP - not publishing the manifest"

REMOTE_SHA="$(curl -sSL "$ASSET_URL" | shasum -a 256 | cut -d' ' -f1)"
LOCAL_SHA="$(python3 -c 'import json;print(json.load(open("data/manifest.json"))["sha256"])')"
[ "$REMOTE_SHA" = "$LOCAL_SHA" ] \
  || die "uploaded asset hashes to $REMOTE_SHA, manifest says $LOCAL_SHA"
echo "  asset verified end-to-end"

step "Publishing manifest to $BRANCH"
git add data/manifest.json data/library.json
git commit -m "content: publish $VERSION

library.json is committed for reproducibility of the shipped add-on;
clients fetch the copy attached to $TAG rather than this one."
git push origin "HEAD:$BRANCH"

MANIFEST_URL="https://raw.githubusercontent.com/${SLUG}/${BRANCH}/data/manifest.json"

step "Published"
cat <<EOF
  version   $VERSION
  manifest  $MANIFEST_URL
  library   $ASSET_URL

Clients with libraryAutoUpdate enabled pick this up on their next Anki
launch, and apply it on the launch after that - the download happens in
the background and the matcher is built at import, so it cannot swap
under a running session.

If this is the first publish, check that libraryManifestUrl in
config.json matches the manifest URL above. It currently reads:

  $(python3 -c 'import json;print(json.load(open("config.json"))["libraryManifestUrl"])')
EOF
