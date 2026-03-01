from __future__ import annotations

class Country:
    def __init__(
        self,
        id_: int,
        url: str,
        bounds: list[int],
    ):
        self.id_: int = id_
        self.url: str = url
        self.bounds: list[int] = bounds

    def __eq__(self, other) -> bool:
        if isinstance(other, Country):
            return self.id_ == other.id_
        return False

    def __hash__(self) -> int:
        return hash(self.id_)
