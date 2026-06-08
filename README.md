# International Tax Meta Router

A small Hermes / Claude Code / Codex skill that routes international tax and accounting questions through a local [OpenAccountants](https://github.com/openaccountants/openaccountants) checkout.

It is meant for LLM-assisted research and working-paper preparation: country detection, topic-aware file selection, context packing, and answer-quality guardrails.

> **Important:** this repository is independent from, unaffiliated with, and not endorsed by OpenAccountants. It does not contain OpenAccountants data. It is only a helper layer that can read a local OpenAccountants checkout when you have one.

## Useful for

- cross-border personal tax and accounting triage
- ETF, dividend, capital-gains, wealth-tax, and investment-tax comparisons
- VAT / GST / MVA / MwSt / IVA questions
- payroll, social-security contribution, bookkeeping, e-invoicing, company-formation questions
- accountant-ready working-paper context for LLM agents
- multi-agent local skill sharing across Hermes, Claude Code, Codex, and `.agents`

## What this repository contains

- `SKILL.md` — the skill entrypoint and agent workflow.
- `scripts/pack-openaccountants-context.py` — question-aware OpenAccountants context packer.
- `scripts/install-skill-links.sh` — links this repository into existing local agent skill roots.
- `scripts/update-openaccountants-source.sh` — keeps a local OpenAccountants checkout current.
- `scripts/update-router-source.sh` — keeps this router checkout current and repairs existing local links.
- `.env.example` — optional path/configuration variables.
- `references/openaccountants-routing-notes.md` — implementation and maintenance notes.
- `references/countries.md` — country/package reference material.

The repository intentionally does **not** vendor OpenAccountants packages.

## Requirements

- `bash`
- `git`
- `python3`
- a local OpenAccountants checkout, or permission for the updater to clone one

Default OpenAccountants location:

```text
~/.hermes/sources/openaccountants
```

## Configuration

Copy the example config only if you need to override defaults:

```bash
cp .env.example .env
$EDITOR .env
```

Important variables:

- `OPENACCOUNTANTS_ROOT` — local checkout of `openaccountants/openaccountants`.
- `OPENACCOUNTANTS_REPO_URL` / `OPENACCOUNTANTS_BRANCH` — source repo and branch to track.
- `INTERNATIONAL_TAX_META_ROUTER_REPO_ROOT` — canonical local checkout of this router.
- `HERMES_SKILL_PATH`, `CLAUDE_SKILL_PATH`, `CODEX_SKILL_PATH`, `AGENTS_SKILL_PATH` — optional install targets.
- `HERMES_PROFILE_SKILL_PATHS` — optional colon-separated Hermes profile skill paths.
- `OPENACCOUNTANTS_MAX_TOTAL_CHARS`, `OPENACCOUNTANTS_MAX_FILE_CHARS` — context caps for the packer.

Environment variables override `.env` values. `.env` is ignored by git.

## Install into local agents

From the repository root:

```bash
scripts/install-skill-links.sh
```

The installer symlinks this repository into agent skill roots that already exist. It **does not create new Claude, Codex, Hermes profile, or `.agents` skill directories for you**. This avoids accidentally installing files for tools you do not use.

Default target paths, when their parent directories already exist:

```text
~/.hermes/skills/finance-business/international-tax-meta-router
~/.claude/skills/international-tax-meta-router
~/.codex/skills/international-tax-meta-router
~/.agents/skills/international-tax-meta-router
```

Existing non-current targets are moved into `~/.hermes/backups/...` before replacement.

If you want to install into a client that is not present yet, create its skill root first, then rerun the installer:

```bash
mkdir -p ~/.codex/skills
scripts/install-skill-links.sh
```

## Fetch or update OpenAccountants

```bash
scripts/update-openaccountants-source.sh
```

The updater clones OpenAccountants if missing, otherwise fetches, resets to the configured branch, removes untracked files, and prints output only when the checkout changed.

## Update this router checkout

```bash
scripts/update-router-source.sh
```

The router updater uses plain HTTPS Git remotes by default:

```text
https://github.com/randomsnowflake/international-tax-meta-router.git
```

No GitHub token is embedded or required once the repository is public. If the repository is still private, tokenless pulls will fail until you make it public or provide credentials outside this script.

## Hermes cron examples

Script-only Hermes cron jobs can keep both this router and OpenAccountants current without spending model tokens.

Create wrapper files under `~/.hermes/scripts`:

```bash
mkdir -p ~/.hermes/scripts

cat > ~/.hermes/scripts/update-international-tax-meta-router.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
exec "$HOME/.hermes/skills/finance-business/international-tax-meta-router/scripts/update-router-source.sh" "$@"
EOF
chmod +x ~/.hermes/scripts/update-international-tax-meta-router.sh

cat > ~/.hermes/scripts/update-openaccountants-source.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
exec "$HOME/.hermes/skills/finance-business/international-tax-meta-router/scripts/update-openaccountants-source.sh" "$@"
EOF
chmod +x ~/.hermes/scripts/update-openaccountants-source.sh
```

Then schedule them:

```bash
hermes cron create \
  --name update-international-tax-meta-router \
  --schedule '7 6 * * *' \
  --script update-international-tax-meta-router.sh \
  --no-agent \
  --deliver origin

hermes cron create \
  --name update-openaccountants-source \
  --schedule '11 6 * * *' \
  --script update-openaccountants-source.sh \
  --no-agent \
  --deliver origin
```

If your Hermes CLI does not expose `cron create` flags, create the jobs through the Hermes dashboard/API with the same values. Keep `script` relative to `~/.hermes/scripts`.

## Verify

Check country detection and context packing:

```bash
python3 scripts/pack-openaccountants-context.py \
  "how is etf tax in denmark compared to norwary" \
  | grep -E "^(Detected countries|Detected topics|## Country package|Selected files)"
```

Expected country detection includes Denmark and Norway.

Check broad shortlist mode:

```bash
python3 scripts/pack-openaccountants-context.py \
  "list best international dividend destinations" \
  > /tmp/openaccountants_broad_test.md

grep -c '^## Country package:' /tmp/openaccountants_broad_test.md
```

For Hermes, verify discovery with:

```bash
hermes skills list --enabled-only | grep international-tax-meta-router
```

For specialist profiles, set the profile's Hermes home explicitly when needed:

```bash
HERMES_HOME=~/.hermes/profiles/law hermes skills list --enabled-only | grep international-tax-meta-router
```

## Safety and publishing checklist

Before making this repository public:

1. Commit only `.env.example`, never `.env`.
2. Do not commit local absolute paths except examples using `$HOME`, `~`, or `/path/to/...`.
3. Keep OpenAccountants content out of this repository.
4. Review OpenAccountants licensing and attribution requirements for your own usage.
5. Run a focused secret/path scan across the current tree and Git history.
6. Confirm the repository description and topics make clear that this is an LLM helper/router, not tax advice and not an OpenAccountants project.

## Disclaimer

This software is not tax, legal, accounting, or investment advice. It helps an LLM select and summarize local reference material. Verify current rates, treaty positions, filing obligations, and real-money decisions against official sources and a qualified professional.

This project is unrelated to OpenAccountants except that it can consume a local OpenAccountants checkout as user-provided reference material.

## License

MIT for this router repository unless otherwise stated. OpenAccountants content remains under its own license and is not included here.
