from collections.abc import Iterable
import datetime
import html
from itertools import cycle
import logging

from matplotlib.colors import TABLEAU_COLORS

from parkrun.api.scraper import fetch_events
from parkrun.api.scraper_runner import fetch_runner_results
from parkrun.maps.render import map_events
from parkrun.models.event import Event
from parkrun.models.runner import Runner

logger = logging.getLogger(__name__)

# One per runner, leaving out those that look like MULTIPLE_COLOUR or NOT_DONE_COLOUR
RUNNER_COLOURS: list[str] = [str(colour) for name, colour in TABLEAU_COLORS.items() if name not in {"tab:red", "tab:green"}]
MULTIPLE_COLOUR: str = "green"
NOT_DONE_COLOUR: str = "red"
# When there are no runners, so nothing is done or not done
NO_RUNNERS_COLOUR: str = "blue"


def event_map(
    runner_ids: list[int],
    start_date: datetime.date = datetime.date.min,
    end_date: datetime.date = datetime.date.max,
    only_adult: bool = True,
    voronoi: bool = True,
) -> None:
    """
    Display a world map of all parkruns in the browser, each coloured by which
    of the given parkrunners did it between start_date and end_date: the
    runner's own colour if only one did (green if they're the only runner),
    green if several did and red if none did. Clicking one shows who did it and
    how many times. With no parkrunners, just show all the events in blue.

    If only_adult, don't show junior events, even ones the parkrunners did.
    If voronoi, also shade the area closest to each parkrun in its colour.
    """

    if len(runner_ids) > len(RUNNER_COLOURS):
        logger.warning("More runners (%d) than colours (%d), so some share a colour", len(runner_ids), len(RUNNER_COLOURS))

    runners: list[Runner] = [fetch_runner_results(runner_id, start_date, end_date) for runner_id in runner_ids]

    # A lone runner is green like on the single runner map
    runner_colours: dict[Runner, str] = {runners[0]: MULTIPLE_COLOUR} if len(runners) == 1 else dict(zip(runners, cycle(RUNNER_COLOURS)))

    events: Iterable[Event] = fetch_events()
    if only_adult:
        events = filter(lambda event: event.is_adult(), events)

    def runners_done(event: Event) -> list[Runner]:
        """Runners who did the event, most times first"""
        done: list[Runner] = [runner for runner in runners if event in runner.locations_counter]
        return sorted(done, key=lambda runner: runner.locations_counter[event], reverse=True)

    def colour(event: Event) -> str:
        done: list[Runner] = runners_done(event)
        if not runners:
            return NO_RUNNERS_COLOUR
        if len(done) == 0:
            return NOT_DONE_COLOUR
        if len(done) == 1:
            return runner_colours[done[0]]
        return MULTIPLE_COLOUR

    def popup_html(event: Event) -> str:
        return "<br>".join([
            f"<b>{html.escape(event.name)}</b>",
            *(f"<b>{html.escape(runner.name)}:</b> {runner.locations_counter[event]}" for runner in runners_done(event)),
        ])

    legend: dict[str, str] = {runner.format_identity(): runner_colours[runner] for runner in runners}
    if runners:
        if len(runners) > 1:
            legend["Multiple"] = MULTIPLE_COLOUR
        legend["Nobody"] = NOT_DONE_COLOUR

    map_events(events, "Parkrun Events", colour, popup_html, voronoi, legend)
