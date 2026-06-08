# International Tax Meta Router

Private Hermes meta-skill for routing international tax/accounting questions through a local OpenAccountants checkout.

## What this repository contains

- `SKILL.md` — Hermes skill entrypoint and workflow.
- `scripts/pack-openaccountants-context.py` — question-aware context packer.
- `references/openaccountants-routing-notes.md` — maintenance notes.
- `references/countries.md` — country/package reference material.

The skill intentionally does **not** vendor the OpenAccountants package library. It expects the OpenAccountants source checkout at:

```text
~/.hermes/sources/openaccountants
```

## Install by link, not copy

Default profile example:

```bash
mkdir -p ~/.hermes/skills/finance-business
ln -s /path/to/international-tax-meta-router \
  ~/.hermes/skills/finance-business/international-tax-meta-router
```

Law profile example:

```bash
mkdir -p ~/.hermes/profiles/law/skills/finance-business
ln -s ~/.hermes/skills/finance-business/international-tax-meta-router \
  ~/.hermes/profiles/law/skills/finance-business/international-tax-meta-router
```

Johannes's current setup uses the second pattern: the law profile points at the default profile skill directory, so edits are single-sourced.

## Verify

```bash
HERMES_HOME=~/.hermes/profiles/law hermes skills list --enabled-only | grep international-tax-meta-router

python3 ~/.hermes/skills/finance-business/international-tax-meta-router/scripts/pack-openaccountants-context.py \
  "how is etf tax in denmark compared to norwary" \
  | grep -E "^(Detected countries|Detected topics|## Country package|Selected files)"
```

Expected country detection includes Denmark and Norway, and broad dividend destination queries should load the configured shortlist without hitting the context cap.

## Refresh OpenAccountants source

```bash
git -C ~/.hermes/sources/openaccountants pull --ff-only
```

## License

Private/internal skill. Do not publish publicly without reviewing OpenAccountants license and attribution requirements.
