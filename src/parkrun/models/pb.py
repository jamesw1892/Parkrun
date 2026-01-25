from __future__ import annotations

# TODO: Extend bool to inherit all its operations?
class PB:
    def __init__(self, is_pb: bool):
        self.is_pb: bool = is_pb

    @staticmethod
    def from_string(string: str) -> PB:
        return PB(string == "PB")

    def format(self, prefix: str = "", suffix: str = "") -> str:
        """
        Return a string which is always the empty string if this is not a PB.
        If it is a PB then return the string "PB" preceded by 'prefix' and
        followed by 'suffix', both default to the empty string.
        """
        if self.is_pb:
            return f"{prefix}PB{suffix}"
        return ""
