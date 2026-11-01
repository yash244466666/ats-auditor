#!/usr/bin/env bash
# Keep `dev` level with `main`.
#
#   ./scripts/sync-branches.sh
#
# A "Rebase and merge" (the only merge method `main` allows, because it requires
# linear history) gives `main` new SHAs, so `dev` can no longer fast-forward to
# it — and the protected branch refuses force-pushes. This merges `main` into
# `dev` through the GitHub API instead: `dev` ends up with exactly the same
# tree, and no commit is rewritten.
#
# Refuses when `dev` holds content that is not on `main`, so unmerged work is
# never hidden by a sync. Merge that work into `main` through a pull request
# first.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

if ! command -v gh >/dev/null; then
  echo "gh is required (the branch protection blocks force-pushes)" >&2
  exit 1
fi

repo=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
git fetch --quiet origin main dev

main_sha=$(git rev-parse origin/main)
dev_sha=$(git rev-parse origin/dev)

if [ "$main_sha" = "$dev_sha" ]; then
  echo "main and dev already point at $main_sha"
  exit 0
fi

if ! git merge-base --is-ancestor "$dev_sha" "$main_sha"; then
  if [ "$(git rev-parse 'origin/main^{tree}')" != "$(git rev-parse 'origin/dev^{tree}')" ]; then
    echo "refused: dev has content that is not on main." >&2
    echo "  dev  $dev_sha" >&2
    echo "  main $main_sha" >&2
    echo "Merge that work into main through a pull request first." >&2
    exit 1
  fi
  echo "trees already match; recording the sync as a merge commit"
fi

echo "merging main ($main_sha) into dev ($dev_sha)"
gh api -X POST "repos/$repo/merges" \
  -f base=dev -f head=main \
  -f commit_message="chore: sync dev with main" \
  --jq '"dev is now \(.sha)"'
