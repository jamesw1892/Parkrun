from parkrun.models.event import Event

class EventCollection:
    def __init__(self, events: dict):
        self.events_by_id: dict[int, Event] = dict()
        self.event_ids_by_name: dict[str, int] = dict()
        for event in events["events"]["features"]:
            event = Event.from_dict(event)
            self.events_by_id[event.id_] = event
            self.event_ids_by_name[event.name] = event.id_

    def get_event(self, name: str) -> Event | None:
        if name not in self.event_ids_by_name:
            return None
        return self.events_by_id[self.event_ids_by_name[name]]

    def get_event(self, id_: int) -> Event | None:
        return self.events_by_id.get(id_)
    
    def __iter__(self):
        yield from self.events_by_id.values()

    def __repr__(self) -> str:
        return f"EventCollection(count={len(self.event_ids_by_name)})"
