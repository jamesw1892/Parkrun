from collections.abc import Callable, Iterable
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import time
import webbrowser
import folium

from parkrun.api.scraper import fetch_events
from parkrun.api.scraper_runner import fetch_runner_results
from parkrun.models.event import Event
from parkrun.models.runner import Runner

logger = logging.getLogger(__name__)

# How long to wait for the browser to request the page before giving up
BROWSER_TIMEOUT_SECS: int = 30


def event_map(runner_id: int, only_adult: bool = True) -> None:
    """
    Display a world map of all parkruns in the browser with ones the parkrunner
    with given ID has done as green dots and those they haven't as red dots.
    """

    runner: Runner = fetch_runner_results(runner_id)
    events: Iterable[Event] = fetch_events()
    if only_adult:
        events = filter(lambda event: event.is_adult(), events)

    map_events(
        events,
        runner.format_identity(),
        lambda event: "green" if event in runner.unique_locations else "red",
    )


def map_events(
    events: Iterable[Event],
    title: str,
    colour: Callable[[Event], str] = lambda event: "blue",
) -> None:
    """
    Display a map of the given events in the browser, each as a dot coloured by
    the given function.
    """

    # Draw on a canvas rather than as separate SVG elements so thousands of
    # markers stay responsive
    event_map = folium.Map(tiles="OpenStreetMap", prefer_canvas=True)
    event_map.get_root().title = title

    events = list(events)
    for event in events:
        folium.CircleMarker(
            location=[event.lat, event.long],
            radius=4,
            color=colour(event),
            fill=True,
            fill_opacity=0.8,
            popup=event.name,
            tooltip=event.name,
        ).add_to(event_map)

    if events:
        event_map.fit_bounds([
            [min(event.lat for event in events), min(event.long for event in events)],
            [max(event.lat for event in events), max(event.long for event in events)],
        ])

    _show_in_browser(event_map.get_root().render())


def _show_in_browser(html: str) -> None:
    """
    Open the given HTML page in the browser, returning once it has loaded.

    OpenStreetMap's tile servers block requests without a Referer header, which
    a page opened from file:// (like Map.show_in_browser does) never sends. So
    serve the page once from localhost instead. Only the page itself comes from
    this server, so it can stop straight away, although refreshing the page
    will then fail.
    """

    page: bytes = html.encode("utf-8")
    served: bool = False

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            nonlocal served
            if self.path != "/":
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page)))
            self.end_headers()
            self.wfile.write(page)
            served = True

        def log_message(self, format, *args):
            logger.debug(format, *args)

    # Port 0 picks any free port
    with HTTPServer(("127.0.0.1", 0), Handler) as server:
        webbrowser.open(f"http://127.0.0.1:{server.server_port}/")
        # Keep handling requests in case the browser asks for something else
        # first, like a favicon
        deadline: float = time.monotonic() + BROWSER_TIMEOUT_SECS
        while not served and time.monotonic() < deadline:
            server.timeout = deadline - time.monotonic()
            server.handle_request()

    if not served:
        logger.warning("Browser didn't load the map within %d seconds", BROWSER_TIMEOUT_SECS)
