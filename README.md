# International Tax Meta Router

Hermes/Claude/Codex meta-skill for routing international tax/accounting questions through a local [OpenAccountants](https://github.com/openaccountants/openaccountants) checkout.

This repository contains the **router** only. It does not vendor OpenAccountants packages.

## What this repository contains

- `SKILL.md` — skill entrypoint and workflow.
- `scripts/pack-openaccountants-context.py` — question-aware context packer.
- `scripts/install-skill-links.sh` — links this repository into Hermes, Claude Code, Codex, and optional `.agents` skill roots.
- `scripts/update-openaccountants-source.sh` — keeps a local OpenAccountants checkout current.
- `.env.example` — configurable paths and update settings.
- `references/openaccountants-routing-notes.md` — maintenance notes.
- `references/countries.md` — country/package reference material.

## Configuration

Copy the example config and adjust paths for your machine:

```bash
cp .env.example .env
$EDITOR .env
```

Important variables:

- `OPENACCOUNTANTS_ROOT` — local checkout of `openaccountants/openaccountants`.
- `OPENACCOUNTANTS_REPO_URL` / `OPENACCOUNTANTS_BRANCH` — source repo and branch to track.
- `HERMES_SKILL_PATH`, `CLAUDE_SKILL_PATH`, `CODEX_SKILL_PATH`, `AGENTS_SKILL_PATH` — install targets.
- `HERMES_PROFILE_SKILL_PATHS` — optional colon-separated Hermes profile skill paths.
- `OPENACCOUNTANTS_MAX_TOTAL_CHARS`, `OPENACCOUNTANTS_MAX_FILE_CHARS` — context caps for the packer.

Environment variables override `.env` values. `.env` is ignored by git.

## Install into local agents

From the repository root:

```bash
scripts/install-skill-links.sh
```

The script links this repository into the configured skill paths. Existing directories are moved into `~/.hermes/backups/...` before replacement.

Default targets:

```text
~/.hermes/skills/finance-business/international-tax-meta-router
~/.claude/skills/international-tax-meta-router
~/.codex/skills/international-tax-meta-router
~/.agents/skills/international-tax-meta-router  # only if ~/.agents/skills exists
```

## Fetch or update OpenAccountants

```bash
scripts/update-openaccountants-source.sh
```

The updater clones the OpenAccountants repo if missing, otherwise fetches, resets to the configured branch, removes untracked files, and prints output only when the checkout changed.

## Hermes cron example

A script-only Hermes cron job can keep OpenAccountants current without spending model tokens:

```bash
mkdir -p ~/.hermes/scripts
cat > ~/.hermes/scripts/update-openaccountants-source.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
exec "/path/to/international-tax-meta-router/scripts/update-openaccountants-source.sh" "$@"
EOF
chmod +x ~/.hermes/scripts/update-openaccountants-source.sh

hermes cron create \
  --name update-openaccountants-source \
  --schedule '11 6 * * *' \
  --script update-openaccountants-source.sh \
  --no-agent \
  --deliver origin
```

If your Hermes CLI does not expose `cron create` flags, create the job through the Hermes dashboard or API with the same values. Keep `script` relative to `~/.hermes/scripts`.

## Verify

```bash
python3 scripts/pack-openaccountants-context.py \
  "how is etf tax in denmark compared to norwary" \
  | grep -E "^(Detected countries|Detected topics|## Country package|Selected files)"
```

Expected country detection includes Denmark and Norway.

For Hermes, verify discovery with:

```bash
hermes skills list --enabled-only | grep international-tax-meta-router
```

For specialist profiles, set the profile's Hermes home explicitly when needed:

```bash
HERMES_HOME=~/.hermes/profiles/law hermes skills list --enabled-only | grep international-tax-meta-router
```

## Publishing notes

Before making this repository public:

1. Keep `.env` private and commit only `.env.example`.
2. Do not commit local absolute paths except as examples using `$HOME` or `/path/to/...`.
3. Review OpenAccountants licensing and attribution requirements.
4. Run a focused secret/path scan across the current tree and history.

## License

MIT for this router repository unless otherwise stated. OpenAccountants content remains under its own license and is not vendored here.
