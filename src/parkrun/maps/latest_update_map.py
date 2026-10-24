import datetime
import html
from itertools import cycle
import logging

from matplotlib.colors import TABLEAU_COLORS

from parkrun.maps.render import map_events
from parkrun.models.event import Event
from parkrun.models.runner import Runner

logger = logging.getLogger(__name__)

# One per event
EVENT_COLOURS: list[str] = [str(colour) for colour in TABLEAU_COLORS.values()]


def latest_update_map(event_runners: dict[Event, list[Runner]], date: datetime.date) -> None:
    """
    Display a map in the browser of the events that the given parkrunners did
    on the given date, each in its own colour, with a legend saying which
    event each is and who did it. Clicking one shows its name and who did it.
    event_runners maps each event to the parkrunners who did it. Show nothing
    if there are no events.
    """

    if not event_runners:
        return

    if len(event_runners) > len(EVENT_COLOURS):
        logger.warning("More events (%d) than colours (%d), so some share a colour", len(event_runners), len(EVENT_COLOURS))

    event_colours: dict[Event, str] = dict(zip(event_runners, cycle(EVENT_COLOURS)))

    def colour(event: Event) -> str:
        return event_colours[event]

    def popup_html(event: Event) -> str:
        return "<br>".join([
            f"<b>{html.escape(event.name)}</b>",
            *(html.escape(runner.name) for runner in event_runners[event]),
        ])

    legend: dict[str, str] = {f"<b>{html.escape(event.name)}:</b> " + html.escape(", ".join(runner.name for runner in runners)): event_colours[event] for event, runners in event_runners.items()}

    map_events(event_runners, f"Parkrun Events on {date}", colour, popup_html, voronoi=False, legend=legend)
