from __future__ import annotations

class Event:
    def __init__(
        self,
        id_: int,
        name: str,
        lat: float,
        long: float,
        country_code: int,
        series: int
    ):
        self.id_: int = id_
        self.name: str = name
        self.lat: float = lat
        self.long: float = long
        self.country_code: int = country_code
        self.series: int = series
        # series 1 is adults, 2 is juniors

    @staticmethod
    def from_dict(event: dict) -> Event:
        return Event(
            event["id"],
            event["properties"]["EventShortName"],
            event["geometry"]["coordinates"][0],
            event["geometry"]["coordinates"][1],
            event["properties"]["countrycode"],
            event["properties"]["seriesid"],
        )

    def is_junior(self) -> bool:
        return self.series == 2

    def is_adult(self) -> bool:
        return self.series == 1

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other) -> bool:
        if isinstance(other, Event):
            return self.id_ == other.id_
        return False

    def __hash__(self) -> int:
        return hash(self.id_)
