#!/usr/bin/env python3
"""Pack relevant OpenAccountants country package context for a tax/accounting question.

Usage:
    pack-openaccountants-context.py "How is ETF tax in Denmark compared to Norway?"

The script prints markdown context for the calling agent. It does not answer the
question itself.
"""
from __future__ import annotations

import difflib
import os
import re
import sys
from pathlib import Path


def load_dotenv(path: Path) -> None:
    """Load simple KEY=VALUE lines without overriding the process environment."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        value = os.path.expandvars(value).replace("~", str(Path.home()), 1) if value.startswith("~") else os.path.expandvars(value)
        os.environ.setdefault(key, value)


REPO_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(REPO_ROOT / ".env")

ROOT = Path(os.environ.get("OPENACCOUNTANTS_ROOT", str(Path.home() / ".hermes" / "sources" / "openaccountants"))).expanduser()
PACKAGES = ROOT / "packages"
MAX_TOTAL_CHARS = int(os.environ.get("OPENACCOUNTANTS_MAX_TOTAL_CHARS", "90000"))
MAX_FILE_CHARS = int(os.environ.get("OPENACCOUNTANTS_MAX_FILE_CHARS", "18000"))

BROAD_DIVIDEND_SHORTLIST = [
    # Common first-pass jurisdictions to inspect for dividend/capital-gains/treaty questions.
    # This is a context-loading heuristic, not an endorsement or final ranking.
    "ireland", "luxembourg", "netherlands", "switzerland", "uk", "malta", "cyprus",
    "estonia", "portugal", "singapore", "hong-kong", "uae", "georgia", "bulgaria",
]

MANUAL_ALIASES = {
    "united states": "usa",
    "united states of america": "usa",
    "america": "usa",
    "us": "usa",
    "u.s.": "usa",
    "u.s.a.": "usa",
    "uk": "uk",
    "u.k.": "uk",
    "united kingdom": "uk",
    "uae": "uae",
    "united arab emirates": "uae",
    "czechia": "czech-republic",
    "czech republic": "czech-republic",
    "south korea": "south-korea",
    "korea": "south-korea",
    "hong kong": "hong-kong",
    "new zealand": "new-zealand",
    "south africa": "south-africa",
    "saudi arabia": "saudi-arabia",
    "cayman": "cayman-islands",
    "cayman islands": "cayman-islands",
    "british virgin islands": "bvi",
    "bvi": "bvi",
    "isle of man": "isle-of-man",
    "bosnia": "bosnia",
    "norwary": "norway",  # common typo from chat
}

TOPIC_HINTS = {
    "vat": ["vat", "gst", "mva", "mwst", "iva", "sales", "eu-vat"],
    "income": ["income", "personal", "irpf"],
    "capital": ["capital", "gains", "investment", "invest", "dividend", "etf", "crypto", "rental"],
    "social": ["social", "ssc", "contribution", "pension", "svs", "nic"],
    "company": ["corporate", "company", "formation", "trade-tax", "business", "bookkeeping", "financial", "payroll", "einvoice"],
}

QUESTION_TOPIC_WORDS = {
    "vat": ["vat", "gst", "mva", "mwst", "iva", "sales tax", "umsatzsteuer"],
    "income": ["income tax", "personal tax", "salary", "wage", "freelance", "self employed"],
    "capital": ["etf", "dividend", "capital gain", "capital gains", "stock", "shares", "investment", "portfolio", "crypto", "fund"],
    "social": ["social security", "social contributions", "pension", "health insurance"],
    "company": ["corporate", "company", "llc", "gmbh", "formation", "payroll", "bookkeeping", "einvoice", "e-invoice"],
}


def slug_to_name(slug: str) -> str:
    return slug.replace("-", " ").title()


def list_packages() -> list[str]:
    if not PACKAGES.exists():
        raise SystemExit(f"OpenAccountants checkout not found at {ROOT}. Clone https://github.com/openaccountants/openaccountants there first.")
    return sorted(p.name for p in PACKAGES.iterdir() if p.is_dir() and not p.name.startswith("_"))


def build_aliases(packages: list[str]) -> dict[str, str]:
    aliases = dict(MANUAL_ALIASES)
    for slug in packages:
        aliases[slug] = slug
        aliases[slug.replace("-", " ")] = slug
        aliases[slug.replace("-", "")] = slug
    # Only keep aliases that resolve to an existing package.
    return {a: s for a, s in aliases.items() if s in packages}


def detect_countries(question: str, packages: list[str]) -> list[str]:
    q = " " + re.sub(r"[^a-z0-9.]+", " ", question.lower()) + " "
    aliases = build_aliases(packages)
    found: list[str] = []
    for alias, slug in sorted(aliases.items(), key=lambda kv: len(kv[0]), reverse=True):
        pattern = r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])"
        if re.search(pattern, q) and slug not in found:
            found.append(slug)
    # Fuzzy pass for obvious typos on country words, e.g. norwary -> norway.
    tokens = [t for t in re.findall(r"[a-z][a-z-]{3,}", question.lower()) if t not in {"compared", "international", "dividend", "destinations", "country", "countries", "tax", "taxes", "best"}]
    alias_keys = list(aliases.keys())
    for token in tokens:
        if token in aliases:
            continue
        match = difflib.get_close_matches(token, alias_keys, n=1, cutoff=0.86)
        if match:
            slug = aliases[match[0]]
            if slug not in found:
                found.append(slug)
    return found


def detect_topics(question: str) -> set[str]:
    q = question.lower()
    topics = set()
    for topic, needles in QUESTION_TOPIC_WORDS.items():
        if any(n in q for n in needles):
            topics.add(topic)
    return topics


def file_score(path: Path, country: str, topics: set[str]) -> int:
    name = path.name.lower()
    score = 0
    if name in {"foundation.md", "intake.md", "readme.md", "references.md"}:
        score += 20
    if "guided-intake" in name:
        score += 12
    for topic in topics:
        if any(h in name for h in TOPIC_HINTS.get(topic, [])):
            score += 50
    if country in name:
        score += 5
    # For investment/dividend questions, income and capital-gains docs are usually where details live.
    if "capital" in topics and any(x in name for x in ["income", "capital", "gains", "rental", "crypto", "tax"]):
        score += 35
    return score


def select_files(country: str, topics: set[str], broad: bool = False) -> list[Path]:
    cdir = PACKAGES / country
    files = sorted(cdir.glob("*.md"))
    scored = [(file_score(f, country, topics), f) for f in files]
    selected = [f for score, f in sorted(scored, key=lambda x: (-x[0], x[1].name)) if score > 0]
    # If no topic-specific hit, include all small package files up to cap order.
    if len(selected) <= 3:
        selected = files
    if broad:
        # Broad ranking questions need breadth across countries, not full working-paper depth.
        essentials = [f for f in selected if f.name.lower() in {"readme.md", "foundation.md", "intake.md", "references.md"}]
        topic_files = [f for f in selected if f not in essentials]
        selected = (topic_files[:1] + essentials[:1]) or selected[:2]
    return selected


def read_limited(path: Path, max_chars: int = MAX_FILE_CHARS) -> str:
    txt = path.read_text(encoding="utf-8", errors="replace")
    if len(txt) > max_chars:
        return txt[:max_chars] + f"\n\n[TRUNCATED: {path.name} exceeded {max_chars} chars]\n"
    return txt


def package_summary(packages: list[str]) -> str:
    grouped = []
    for slug in packages:
        files = sorted(p.name for p in (PACKAGES / slug).glob("*.md"))
        flags = []
        joined = " ".join(files).lower()
        for label, needles in [("VAT/GST", ["vat", "gst", "mva", "mwst", "iva"]), ("income", ["income"]), ("social", ["social", "ssc", "contribution"]), ("company", ["corporate", "formation", "bookkeeping", "payroll"]), ("capital/investment", ["capital", "crypto", "rental", "dividend"] )]:
            if any(n in joined for n in needles):
                flags.append(label)
        grouped.append(f"- {slug}: {', '.join(flags) if flags else 'general package'} ({len(files)} md files)")
    return "\n".join(grouped)


def main() -> int:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print("Usage: pack-openaccountants-context.py '<tax/accounting question>'", file=sys.stderr)
        return 2
    packages = list_packages()
    countries = detect_countries(question, packages)
    topics = detect_topics(question)
    q_lower = question.lower()
    broad_dividend_request = (
        not countries
        and "capital" in topics
        and any(word in q_lower for word in ["best", "top", "destination", "destinations", "jurisdiction", "jurisdictions", "where"])
    )
    if broad_dividend_request:
        countries = [c for c in BROAD_DIVIDEND_SHORTLIST if c in packages]

    print("# OpenAccountants Context Pack")
    print(f"\nQuestion: {question}")
    print(f"\nDetected countries: {', '.join(countries) if countries else 'none'}")
    if broad_dividend_request:
        print("Country selection mode: broad dividend/capital-gains shortlist heuristic")
    print(f"Detected topics: {', '.join(sorted(topics)) if topics else 'general tax/accounting'}")
    print(f"Source checkout: `{ROOT}`")

    if not countries:
        print("\n## No explicit country detected")
        print("Use this as an index for broad shortlist/ranking questions. For final answers, inspect specific country packages and current official sources.")
        print("\n## Available country packages")
        print(package_summary(packages))
        return 0

    total = 0
    for country in countries:
        print(f"\n---\n\n## Country package: {slug_to_name(country)} (`{country}`)")
        files = select_files(country, topics, broad=broad_dividend_request)
        print("\nSelected files: " + ", ".join(f.name for f in files))
        file_char_cap = 2200 if broad_dividend_request else MAX_FILE_CHARS
        for f in files:
            if total >= MAX_TOTAL_CHARS:
                print(f"\n[STOPPED: total context cap {MAX_TOTAL_CHARS} chars reached]")
                return 0
            content = read_limited(f, max_chars=file_char_cap)
            remaining = MAX_TOTAL_CHARS - total
            if len(content) > remaining:
                content = content[:remaining] + f"\n\n[TRUNCATED: total context cap {MAX_TOTAL_CHARS} chars reached]\n"
            total += len(content)
            rel = f.relative_to(ROOT)
            print(f"\n### File: `{rel}`\n")
            print(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
