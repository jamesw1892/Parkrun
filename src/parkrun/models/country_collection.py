from collections.abc import Generator
from typing import Any

from parkrun.models.country import Country

class CountryCollection:
    def __init__(self, countries: dict[str, dict[str, Any]]):
        self.countries_by_id: dict[int, Country] = dict()
        for id_str, country in countries["countries"].items():
            id_: int = int(id_str)
            self.countries_by_id[id_] = Country(id_, country["url"], country["bounds"])

    def get_country_by_id(self, id_: int) -> Country | None:
        return self.countries_by_id.get(id_)

    def get_default(self) -> Country:
        return self.countries_by_id[0]

    def __iter__(self) -> Generator[Country, None, None]:
        yield from self.countries_by_id.values()

    def __repr__(self) -> str:
        return f"CountryCollection(count={len(self.countries_by_id)})"
