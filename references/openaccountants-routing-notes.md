# OpenAccountants routing notes

Session-derived implementation notes for maintaining `international-tax-meta-router`.

## Intent

Use OpenAccountants as a tax/accounting knowledge source without installing every country package into the prompt. The router itself stays single-sourced; additional profiles should link to it rather than copy it. Johannes wants natural country questions to work, e.g.:

- “how is ETF tax in Denmark compared to Norway”
- “list best international dividend destinations”

## Working pattern

- Source checkout: `~/.hermes/sources/openaccountants`
- Packages live under `packages/<country>/`.
- The router skill stays small; `scripts/pack-openaccountants-context.py` does the heavy lifting.
- Country detection should support:
  - package slugs: `hong-kong`, `czech-republic`
  - natural names: `Hong Kong`, `Czechia`, `United Kingdom`
  - common abbreviations: `UK`, `US`, `UAE`, `BVI`
  - obvious typo/fuzzy matching, e.g. `norwary` → `norway`

## Broad ranking queries

For broad questions without explicit countries, do not dump the full package index as the only context if the intent is clear. For dividend/capital-gains destination queries, use a breadth-first shortlist and small excerpts per country.

Current broad dividend shortlist:

- Ireland
- Luxembourg
- Netherlands
- Switzerland
- UK
- Malta
- Cyprus
- Estonia
- Portugal
- Singapore
- Hong Kong
- UAE
- Georgia
- Bulgaria

The shortlist is only a context-loading heuristic, not a final recommendation. Answers must still rank by explicit criteria: dividend withholding/treaties, capital gains, fund domicile, wealth tax, CFC/exit-tax risk, social contributions, bureaucracy, and residence practicality.

## Context caps

Broad mode originally hit the total cap after only a handful of countries. The fix was to load one topic file plus one overview file per country and cap broad-mode file excerpts aggressively. Keep broad-mode output breadth-first.

## Profile audit notes

This skill currently lives in the default profile at `~/.hermes/skills/finance-business/international-tax-meta-router/` and uses the default-profile source checkout at `~/.hermes/sources/openaccountants`.

When checking whether another profile uses it, run Hermes with that profile's home explicitly:

```bash
HERMES_HOME=~/.hermes/profiles/law hermes skills list --enabled-only | grep -E "international-tax-meta-router|openaccountants|tax" || true
```

Do not use only `HERMES_PROFILE=law` for this audit; in the June 2026 check it still surfaced default-profile finance skills and produced a misleading result. Also check direct paths:

```bash
test -e ~/.hermes/profiles/law/skills/finance-business/international-tax-meta-router; echo $?
test -e ~/.hermes/profiles/law/sources/openaccountants; echo $?
```

Recommended verification after edits:

```bash
python3 ~/.hermes/skills/finance-business/international-tax-meta-router/scripts/pack-openaccountants-context.py \
  "how is etf tax in denmark compared to norwary" | grep -E "^(Detected countries|Detected topics|## Country package|Selected files)"

python3 ~/.hermes/skills/finance-business/international-tax-meta-router/scripts/pack-openaccountants-context.py \
  "list best international dividend destinations" > /tmp/openaccountants_broad_test.md
python3 - <<'PY'
from pathlib import Path
s = Path('/tmp/openaccountants_broad_test.md').read_text()
print('chars', len(s))
print('country_headers', s.count('## Country package:'))
print('stopped', '[STOPPED' in s)
PY
```

Expected broad-mode behavior: all shortlist countries fit without `[STOPPED]`.
