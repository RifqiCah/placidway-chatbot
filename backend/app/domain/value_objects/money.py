from __future__ import annotations

import re

MONEY_PATTERN = re.compile(
    r"(?:USD|EUR|GBP|MXN|CAD|AUD|\$|€|£)\s?\d[\d,.]*|\d[\d,.]*\s?(?:USD|EUR|GBP|MXN|CAD|AUD)",
    re.IGNORECASE,
)


def _canonical(value: str) -> str:
    return re.sub(r"\s+", "", value).rstrip(".,").casefold()


def extract_money_mentions(text: str) -> frozenset[str]:
    return frozenset(_canonical(value) for value in MONEY_PATTERN.findall(text))


def has_unsupported_money(candidate: str, evidence: str) -> bool:
    return not extract_money_mentions(candidate).issubset(extract_money_mentions(evidence))

