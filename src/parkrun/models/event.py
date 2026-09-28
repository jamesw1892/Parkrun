from __future__ import annotations
from typing import Any

from parkrun.models.country import Country
from parkrun.models.country_collection import CountryCollection

class Event:
    def __init__(
        self,
        id_: int,
        name: str,
        url_name: str,
        lat: float,
        long: float,
        country: Country,
        series: int
    ):
        self.id_: int = id_
        self.name: str = name
        self.url_name: str = url_name
        self.lat: float = lat
        self.long: float = long
        self.country: Country = country
        self.series: int = series
        # series 1 is adults, 2 is juniors

    @staticmethod
    def from_dict(event: dict[str, Any], countries: CountryCollection) -> Event:
        country: Country | None = countries.get_country_by_id(event["properties"]["countrycode"])
        if country is None:
            country = countries.get_default()
        return Event(
            id_=event["id"],
            name=event["properties"]["EventShortName"],
            url_name=event["properties"]["eventname"],
            lat=event["geometry"]["coordinates"][1],
            long=event["geometry"]["coordinates"][0],
            country=country,
            series=event["properties"]["seriesid"],
        )

    def is_junior(self) -> bool:
        return self.series == 2

    def is_adult(self) -> bool:
        return self.series == 1

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Event):
            return self.id_ == other.id_
        return False

    def __hash__(self) -> int:
        return hash(self.id_)

    def __repr__(self) -> str:
        return f"Event({self})"
