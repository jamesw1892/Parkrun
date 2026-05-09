from parkrun.models.country_collection import CountryCollection
from parkrun.models.event import Event

class EventCollection:
    def __init__(self, events: dict):
        self._countries = CountryCollection(events)
        self.events_by_id: dict[int, Event] = dict()
        self.event_ids_by_name: dict[str, int] = dict()
        for event in events["events"]["features"]:
            event = Event.from_dict(event, self._countries)
            self.events_by_id[event.id_] = event
            self.event_ids_by_name[event.name] = event.id_

    def get_event_by_name(self, name: str) -> Event:
        """
        Return the event with given name or a dummy event if not present.
        TODO: Should return None and handle in all uses?
        """
        if name not in self.event_ids_by_name:
            return Event(0, f"{name} (discontinued)", name, 0.0, 0.0, self._countries.get_country_by_id(0), 0)
        return self.events_by_id[self.event_ids_by_name[name]]

    def get_event_by_id(self, id_: int) -> Event | None:
        return self.events_by_id.get(id_)

    def __iter__(self):
        yield from self.events_by_id.values()

    def __repr__(self) -> str:
        return f"EventCollection(count={len(self.event_ids_by_name)})"
