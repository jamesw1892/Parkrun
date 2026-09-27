from collections import defaultdict
from collections.abc import Iterable
import html

from parkrun.api.scraper import fetch_events
from parkrun.api.scraper_runner import fetch_runner_results
from parkrun.maps.render import map_events
from parkrun.models.event import Event
from parkrun.models.runner import Runner
from parkrun.models.runner_result import RunnerResult


def event_map(runner_id: int, only_adult: bool = True, voronoi: bool = False) -> None:
    """
    Display a world map of all parkruns in the browser with ones the parkrunner
    with given ID has done as green dots and those they haven't as red dots.
    If voronoi, also shade the area closest to each parkrun in its colour.
    """

    runner: Runner = fetch_runner_results(runner_id)
    events: Iterable[Event] = fetch_events()
    if only_adult:
        events = filter(lambda event: event.is_adult(), events)

    results_by_event: defaultdict[Event, list[RunnerResult]] = defaultdict(list)
    for result in runner.results:
        results_by_event[result.location].append(result)

    def popup_html(event: Event) -> str:
        # Results are in descending order of date
        results: list[RunnerResult] = results_by_event[event]
        lines: list[tuple[str, str]] = [("Times done", str(len(results)))]
        if results:
            best: RunnerResult = min(results, key=lambda result: result.time.timedelta)
            lines += [
                ("First", str(results[-1].date)),
                ("Latest", str(results[0].date)),
                ("Best time", f"{best.time} ({best.date})"),
            ]
        return "<br>".join([
            f"<b>{html.escape(event.name)}</b>",
            *(f"<b>{title}:</b> {html.escape(value)}" for title, value in lines),
        ])

    map_events(
        events,
        runner.format_identity(),
        lambda event: "green" if event in runner.unique_locations else "red",
        popup_html,
        voronoi,
    )
