from __future__ import annotations

import re

TOKEN_PATTERN = re.compile(r"[a-zA-ZÀ-ÿ0-9][a-zA-ZÀ-ÿ0-9'’-]*")
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "does", "for", "from",
    "have", "how", "i", "in", "is", "it", "me", "of", "offer", "offers", "on", "or", "the",
    "this", "to", "what", "with", "you", "yang", "dan", "di", "ke", "dari", "berapa", "apa",
    "untuk", "dengan", "itu", "ini",
}
QUERY_EXPANSIONS = {
    "harga": "price cost pricing",
    "biaya": "price cost pricing",
    "termasuk": "included includes package",
    "pemulihan": "recovery recuperation",
    "aman": "safe safety risk",
    "murah": "cheap cheaper cost price",
    "kanker": "cancer",
    "pengobatan": "treatment therapy",
}


def query_tokens(text: str) -> list[str]:
    expanded = text.casefold()
    for word, additions in QUERY_EXPANSIONS.items():
        if word in expanded:
            expanded += " " + additions
    return [token for token in TOKEN_PATTERN.findall(expanded) if len(token) > 1 and token not in STOPWORDS]

