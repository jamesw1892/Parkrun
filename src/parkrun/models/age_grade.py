# TODO: Extend float to inherit all its operations?
class AgeGrade:
    """
    Value is a float between 0 and 1 representing the percentage.
    String is formatted 'xx.xx%'.
    """
    def __init__(self, string: str):
        self.string: str = string

        if string == "":
            self.value: float = 0.0
            return

        self.value: float = float(string.removesuffix("%")) / 100

    def __str__(self) -> str:
        return self.string
