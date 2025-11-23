def get_ordinal_suffix(n: int) -> str:
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th") if n not in (11, 12, 13) else "th"

class Position:
    def __init__(self, position: str):
        self.value: int = int(position)
        self.string: str = f"{position}{get_ordinal_suffix(self.value)}"

    def __str__(self) -> str:
        return self.string
