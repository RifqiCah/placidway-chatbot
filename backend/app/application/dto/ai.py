from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GeneratedAnswer:
    answer: str
    source_indices: tuple[int, ...]
    is_answerable: bool

