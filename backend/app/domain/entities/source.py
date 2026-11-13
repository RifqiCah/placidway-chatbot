from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Source:
    id: str
    page_type: str
    title: str
    url: str

