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

src="${OPENACCOUNTANTS_ROOT:-$HOME/.hermes/sources/openaccountants}"
url="${OPENACCOUNTANTS_REPO_URL:-https://github.com/openaccountants/openaccountants.git}"
branch="${OPENACCOUNTANTS_BRANCH:-main}"

mkdir -p "$(dirname "$src")"

if [ ! -d "$src/.git" ]; then
  rm -rf "$src"
  git clone -q "$url" "$src"
fi

git -C "$src" remote set-url origin "$url"
before="$(git -C "$src" rev-parse HEAD 2>/dev/null || true)"

git -C "$src" fetch -q origin --prune
if git -C "$src" show-ref --verify --quiet "refs/remotes/origin/$branch"; then
  git -C "$src" checkout -q -B "$branch" "origin/$branch"
else
  branch="$(git -C "$src" symbolic-ref --quiet refs/remotes/origin/HEAD | sed 's#^refs/remotes/origin/##')"
  if [ -z "$branch" ]; then
    echo "OpenAccountants update failed: cannot determine remote default branch" >&2
    exit 1
  fi
  git -C "$src" checkout -q -B "$branch" "origin/$branch"
fi
git -C "$src" reset -q --hard "origin/$branch"
git -C "$src" clean -q -fd

after="$(git -C "$src" rev-parse HEAD)"

if [ ! -d "$src/packages" ]; then
  echo "OpenAccountants update failed: packages/ missing after sync at $src" >&2
  exit 1
fi

if [ "$before" != "$after" ]; then
  echo "OpenAccountants updated: ${before:-none} -> $after"
  echo
  if [ -n "$before" ]; then
    git -C "$src" log --oneline --decorate --no-merges "$before..$after" 2>/dev/null || git -C "$src" log -1 --oneline --decorate
  else
    git -C "$src" log -1 --oneline --decorate
  fi
fi
