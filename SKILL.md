---
name: international-tax-meta-router
description: Use for foreign or cross-border tax/accounting questions and country tax comparisons using OpenAccountants. Not for generic law or investment advice without a tax angle.
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

German legal drafting/litigation belongs to `deutsches-recht-meta-router`; use this router when foreign or cross-border tax/accounting is central.

## Workflow

1. Run the context packer with the user’s exact question:

```bash
python3 "$HOME/.hermes/skills/finance-business/international-tax-meta-router/scripts/pack-openaccountants-context.py" "$USER_QUESTION"
```

If your installation path differs, use the linked skill path or set `INTERNATIONAL_TAX_META_ROUTER_REPO_ROOT` / `OPENACCOUNTANTS_ROOT` in `.env`.

2. Use the returned markdown context to answer. If countries were detected, compare them directly. If no country was detected and the request asks for “best countries/destinations”, the script automatically loads a broad dividend/capital-gains shortlist when possible; otherwise it returns the full country package index for narrowing.
3. Be explicit about jurisdiction, tax year if known, residency assumptions, entity/person distinction, and whether the source package appears thin or comprehensive. A `[TRUNCATED]` or `[STOPPED]` context-cap marker means partial coverage: narrow the query or retrieve the missing relevant files before claiming a complete comparison.
4. For current rates, treaties, filing positions, or real money decisions, verify against official tax authority sources before treating the answer as operational.

## Answer style

For substantive comparisons, this is a default structure; adapt to the requested depth:

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

For setup, source updates, country alias repairs and profile audits, load `references/openaccountants-routing-notes.md`.
