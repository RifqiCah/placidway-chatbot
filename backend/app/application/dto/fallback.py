from dataclasses import dataclass

from backend.app.domain.entities.knowledge import Passage


@dataclass(frozen=True, slots=True)
class FallbackAnswer:
    answer: str
    used_passages: tuple[Passage, ...]
    is_answerable: bool = True

