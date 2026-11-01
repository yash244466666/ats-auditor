#!/usr/bin/env bash
# Keep `dev` identical to `main` after a release.
#
#   ./scripts/sync-branches.sh          # fast-forward dev to origin/main
#
# Requires a token that may bypass the `dev` protection rules (the repository
# owner's own credentials do). It refuses to run if the two branches differ in
# content, so it can never silently discard work that only exists on dev.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"
git fetch --quiet origin main dev

main_sha=$(git rev-parse origin/main)
dev_sha=$(git rev-parse origin/dev)

if [ "$main_sha" = "$dev_sha" ]; then
  echo "main and dev already point at $main_sha"
  exit 0
fi

# Accept a fast-forward (dev is behind main), or a same-content rewrite, which
# is what a "Rebase and merge" leaves behind: identical trees, new SHAs.
if ! git merge-base --is-ancestor "$dev_sha" "$main_sha"; then
  if [ "$(git rev-parse 'origin/main^{tree}')" != "$(git rev-parse 'origin/dev^{tree}')" ]; then
    echo "refused: dev has content that is not on main ($dev_sha vs $main_sha)." >&2
    echo "Merge that work into main through a pull request first." >&2
    exit 1
  fi
  echo "trees are identical (post-rebase-merge); repointing dev at main"
fi

echo "updating dev: $dev_sha -> $main_sha"
git push --force-with-lease origin "$main_sha:refs/heads/dev"
echo "done"
