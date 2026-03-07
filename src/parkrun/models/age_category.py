"""
Models an age category used throughput Parkrun. These are strings where the
first character is either J (junior, <= 17), S (senior, <= 34), or V (veteran);
the second character is either M (male), or W (female); then there's the ages
bounding this age category separated with a dash.
"""

class AgeCategory:
    def __init__(self, string: str):
        self.string: str = string
        self.broad_age: str = string[0]
        self.gender: str = string[1]
        splat: list[str] = string[2:].split("-")
        self.min_age: int = int(splat[0])
        self.max_age: int = int(splat[1])

    def __str__(self) -> str:
        return self.string
