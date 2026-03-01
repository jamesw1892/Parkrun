from parkrun.models.country import Country

class CountryCollection:
    def __init__(self, countries: dict):
        self.countries_by_id: dict[int, Country] = dict()
        for id_, country in countries["countries"].items():
            id_: int = int(id_)
            self.countries_by_id[id_] = Country(id_, country["url"], country["bounds"])

    def get_country_by_id(self, id_: int) -> Country | None:
        return self.countries_by_id.get(id_)

    def __iter__(self):
        yield from self.countries_by_id.values()

    def __repr__(self) -> str:
        return f"CountryCollection(count={len(self.countries_by_id)})"
