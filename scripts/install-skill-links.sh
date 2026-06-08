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

repo_root="${INTERNATIONAL_TAX_META_ROUTER_REPO_ROOT:-$repo_root}"

if [ ! -f "$repo_root/SKILL.md" ]; then
  echo "install failed: SKILL.md missing at $repo_root" >&2
  exit 1
fi

backup_root="${BACKUP_ROOT:-$HOME/.hermes/backups/international-tax-meta-router-link-fix-$(date +%Y%m%d-%H%M%S)}"
changed=0
skipped=0

ensure_link() {
  local dest="$1"
  local label="${2:-$1}"
  [ -n "$dest" ] || return 0

  local parent
  parent="$(dirname "$dest")"

  # Public installer rule: do not create tool/profile skill roots implicitly.
  # Only touch targets whose parent directory already exists, or a target that
  # already exists and can be repaired/replaced.
  if [ ! -d "$parent" ] && [ ! -L "$parent" ] && [ ! -e "$dest" ] && [ ! -L "$dest" ]; then
    echo "skipped: $label parent does not exist ($parent)"
    skipped=1
    return 0
  fi

  local resolved_dest
  resolved_dest="$(readlink -f "$dest" 2>/dev/null || true)"
  if [ "$dest" = "$repo_root" ] || [ "$resolved_dest" = "$repo_root" ]; then
    return 0
  fi

  if [ -e "$dest" ] || [ -L "$dest" ]; then
    mkdir -p "$backup_root"
    mv "$dest" "$backup_root/$(echo "$dest" | sed "s#^$HOME/##; s#/#__#g")"
  fi
  ln -sfn "$repo_root" "$dest"
  echo "linked: $dest -> $repo_root"
  changed=1
}

ensure_link "${HERMES_SKILL_PATH:-$HOME/.hermes/skills/finance-business/international-tax-meta-router}" "Hermes"
ensure_link "${CLAUDE_SKILL_PATH:-$HOME/.claude/skills/international-tax-meta-router}" "Claude Code"
ensure_link "${CODEX_SKILL_PATH:-$HOME/.codex/skills/international-tax-meta-router}" "Codex"
ensure_link "${AGENTS_SKILL_PATH:-$HOME/.agents/skills/international-tax-meta-router}" ".agents"

IFS=':' read -r -a profile_paths <<< "${HERMES_PROFILE_SKILL_PATHS:-}"
for profile_path in "${profile_paths[@]}"; do
  [ -n "$profile_path" ] || continue
  ensure_link "$profile_path" "Hermes profile"
done

if [ "$changed" = "0" ] && [ "$skipped" = "0" ]; then
  echo "international-tax-meta-router links already current."
fi
