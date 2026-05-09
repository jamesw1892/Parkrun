from __future__ import annotations
import pycountry

tld_to_name: dict[str, str] = {country.alpha_2.upper(): country.name for country in pycountry.countries}

class Country:
    def __init__(
        self,
        id_: int,
        url: str,
        bounds: list[int],
    ):
        self.id_: int = id_
        self.url: str | None = url
        self.bounds: list[int] = bounds
        self.tld: str = url.split(".")[-1].upper() if url is not None else ""
        self.name: str = tld_to_name.get(self.tld, self.tld)

    def __eq__(self, other) -> bool:
        if isinstance(other, Country):
            return self.id_ == other.id_
        return False

    def __hash__(self) -> int:
        return hash(self.id_)
