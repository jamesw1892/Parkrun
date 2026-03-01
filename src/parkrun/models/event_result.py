import datetime
from parkrun.models.event import Event
from parkrun.models.event_runner_result import EventRunnerResult

class EventResult:
    def __init__(
        self,
        event: Event,
        event_number: int,
        date: datetime.date,
        event_runner_results: list[EventRunnerResult],
        #event_volunteer_results: list[EventVolunteerResult], # TODO
    ):
        self.event: Event = event
        self.event_number: int = event_number
        self.date: datetime.date = date
        self.event_runner_results: list[EventRunnerResult] = event_runner_results
        #event_volunteer_results: list[EventVolunteerResult] = event_volunteer_results

    def __str__(self) -> str:
        return f"{len(self.event_runner_results)} runners at event {self.event_number} on {self.date} at {self.event}"
