from __future__ import annotations

import re
from dataclasses import dataclass

from bs4 import BeautifulSoup


@dataclass(frozen=True, slots=True)
class ExtractedPage:
    title: str
    blocks: tuple[str, ...]


class HtmlContentExtractor:
    @staticmethod
    def _clean(value: str) -> str:
        value = value.replace("\xa0", " ")
        value = re.sub(r"[ \t]+", " ", value)
        value = re.sub(r"\n{3,}", "\n\n", value)
        return value.strip()

    def extract(self, html: str) -> ExtractedPage:
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "noscript", "svg", "canvas", "iframe", "form"]):
            tag.decompose()
        for selector in ("nav", "footer", "header", ".cookie", "#cookie", ".breadcrumb"):
            for node in soup.select(selector):
                node.decompose()

        title = self._clean(soup.title.get_text(" ", strip=True) if soup.title else "")
        root = soup.find("main") or soup.find("article") or soup.body or soup
        blocks: list[str] = []
        seen: set[str] = set()
        for node in root.find_all(["h1", "h2", "h3", "h4", "p", "li", "tr"]):
            text = self._clean(node.get_text(" ", strip=True))
            fingerprint = text.casefold()
            if len(text) < 3 or fingerprint in seen:
                continue
            seen.add(fingerprint)
            blocks.append(text)
        return ExtractedPage(title, tuple(blocks))

