#!/usr/bin/env bash
set -euo pipefail

script_path="$(readlink -f -- "${BASH_SOURCE[0]}")"
script_dir="$(cd -- "$(dirname -- "$script_path")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"

if [ -f "$repo_root/.env" ]; then
  # shellcheck disable=SC1091
  set -a
  source "$repo_root/.env"
  set +a
fi

repo="${INTERNATIONAL_TAX_META_ROUTER_REPO_ROOT:-$repo_root}"
url="${INTERNATIONAL_TAX_META_ROUTER_REPO_URL:-https://github.com/randomsnowflake/international-tax-meta-router.git}"
branch="${INTERNATIONAL_TAX_META_ROUTER_BRANCH:-main}"

if [ ! -d "$repo/.git" ]; then
  echo "router update failed: $repo is not a git checkout" >&2
  exit 1
fi

git -C "$repo" remote set-url origin "$url"
before="$(git -C "$repo" rev-parse HEAD 2>/dev/null || true)"

git -C "$repo" fetch -q origin --prune
# Keep a clean source of truth. Local edits should be committed before this runs.
git -C "$repo" clean -q -fd
if git -C "$repo" show-ref --verify --quiet "refs/remotes/origin/$branch"; then
  git -C "$repo" checkout -q -B "$branch" "origin/$branch"
else
  branch="$(git -C "$repo" symbolic-ref --quiet refs/remotes/origin/HEAD | sed 's#^refs/remotes/origin/##')"
  if [ -z "$branch" ]; then
    echo "router update failed: cannot determine remote default branch" >&2
    exit 1
  fi
  git -C "$repo" checkout -q -B "$branch" "origin/$branch"
fi
git -C "$repo" reset -q --hard "origin/$branch"
git -C "$repo" clean -q -fd

after="$(git -C "$repo" rev-parse HEAD)"

# Repair only targets whose parent directories already exist.
export INTERNATIONAL_TAX_META_ROUTER_REPO_ROOT="$repo"
if ! repair_output="$($repo/scripts/install-skill-links.sh)"; then
  printf '%s\n' "$repair_output" >&2
  echo "router update failed: link repair failed" >&2
  exit 1
fi
repaired=0
if printf '%s\n' "$repair_output" | grep -q '^linked:'; then
  repaired=1
fi

if [ "$before" != "$after" ]; then
  echo "International tax meta-router updated: ${before:0:7} -> ${after:0:7}"
  echo
  git -C "$repo" log --oneline --decorate --no-merges "${before}..${after}" 2>/dev/null || git -C "$repo" log -1 --oneline --decorate
elif [ "$repaired" = "1" ]; then
  echo "International tax meta-router symlinks were repaired; repo unchanged at ${after:0:7}."
fi
