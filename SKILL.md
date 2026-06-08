---
name: international-tax-meta-router
description: Route and answer international tax/accounting questions using OpenAccountants country packages. Trigger on foreign/cross-border tax, ETF/dividend/capital gains taxation, VAT/GST/MVA/MwSt, income tax, social security, payroll, e-invoicing, company formation, bookkeeping, accountant-ready working papers, or comparisons between country tax regimes. Do not use for generic non-tax law.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [international-tax, accounting, openaccountants, llm-router, tax-research, cross-border-tax, vat, dividends, capital-gains, bookkeeping]
    related_skills: [deutscher-steuerberater-meta-router]
---

# International Tax Meta Router

Router skill for **international tax and accounting** checks. It is designed to stay small and load only the needed OpenAccountants country context dynamically.

This router repository is independent from, unaffiliated with, and not endorsed by OpenAccountants. It is only a useful LLM helper that can consume a local OpenAccountants checkout; it does not vendor or replace OpenAccountants.

The router expects a local OpenAccountants checkout. By default it looks under:

`~/.hermes/sources/openaccountants`

Override this with `OPENACCOUNTANTS_ROOT` in the environment or in a repository-local `.env` file copied from `.env.example`.

The repo has country packages under `packages/<country>/`. Do not load the whole library into context. Use the script below to select country files dynamically.

## Trigger gate

Use for questions about:

- country tax comparisons: “ETF tax in Denmark compared to Norway”
- international dividend/capital-gains destinations
- VAT/GST/MVA/MwSt, income tax, corporate tax, social security, payroll
- bookkeeping, e-invoicing, company formation, accountant-ready papers
- cross-border business or personal tax/accounting triage

Do **not** use for:

- general foreign law unless tax/accounting is central
- German legal drafting/litigation/contract questions, use `deutsches-recht-meta-router`
- investment advice without a tax/accounting angle

## Workflow

1. Run the context packer with the user’s exact question:

```bash
python3 "$HOME/.hermes/skills/finance-business/international-tax-meta-router/scripts/pack-openaccountants-context.py" "$USER_QUESTION"
```

If your installation path differs, use the linked skill path or set `INTERNATIONAL_TAX_META_ROUTER_REPO_ROOT` / `OPENACCOUNTANTS_ROOT` in `.env`.

2. Use the returned markdown context to answer. If countries were detected, compare them directly. If no country was detected and the request asks for “best countries/destinations”, the script automatically loads a broad dividend/capital-gains shortlist when possible; otherwise it returns the full country package index for narrowing.
3. Be explicit about jurisdiction, tax year if known, residency assumptions, entity/person distinction, and whether the source package appears thin or comprehensive.
4. For current rates, treaties, filing positions, or real money decisions, verify against official tax authority sources before treating the answer as operational.

## Answer style

For comparison questions:

1. Bottom line in 2-4 sentences
2. Assumptions
3. Country-by-country bullets
4. Practical implications / traps
5. What to verify next

For “best destinations” questions:

- Don’t pretend the OpenAccountants package alone gives a full optimization ranking.
- Rank by clearly stated criteria: dividend withholding/treaties, capital gains, fund domicile rules, wealth tax, CFC/exit-tax risk, social contributions, bureaucracy, and residence practicality.
- Prefer “shortlist for further checking” over absolute certainty.

## Quality rules

- OpenAccountants is useful working-paper scaffolding, not final tax advice.
- Do not invent rates, thresholds, treaty outcomes, or forms if absent from the loaded package.
- If the package lacks ETF/dividend-specific detail, say that and explain the nearest available tax categories to verify.
- Ask targeted follow-up only when the answer materially depends on residency, entity type, tax year, or source country and cannot be answered at a useful high level.

## Maintenance

- Implementation/maintenance notes live in `references/openaccountants-routing-notes.md`, including broad dividend shortlist behavior, typo/fuzzy matching expectations, profile-installation audit commands, and verification commands.
- Configure local paths by copying `.env.example` to `.env` and setting `OPENACCOUNTANTS_ROOT`, install targets, and optional profile skill paths.
- Refresh source checkout manually with:

```bash
scripts/update-openaccountants-source.sh
```

- Install or repair links into Hermes, Claude Code, Codex, and optional `.agents` with:

```bash
scripts/install-skill-links.sh
```

- If country detection misses common country names or abbreviations, patch `scripts/pack-openaccountants-context.py` aliases.
- When auditing whether this skill is installed in another Hermes profile, set `HERMES_HOME=/path/to/profile/hermes-home` for the command. Do not rely on `HERMES_PROFILE=<profile>` alone, because that can still show default-profile skills in some CLI contexts.
