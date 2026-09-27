from collections.abc import Callable, Iterable
import html
import folium

from parkrun.maps.browser import show_in_browser
from parkrun.models.event import Event


def map_events(
    events: Iterable[Event],
    title: str,
    colour: Callable[[Event], str] = lambda event: "blue",
    popup_html: Callable[[Event], str] = lambda event: html.escape(event.name),
) -> None:
    """
    Display a map of the given events in the browser, each as a dot coloured by
    the given function. Clicking a dot shows a popup with the HTML given by the
    other function, so it must escape any data it includes.
    """

    # Draw on a canvas rather than as separate SVG elements so thousands of
    # markers stay responsive. Put it in our own Figure (the page) to set the
    # title, replacing the one folium.Map creates.
    figure = folium.Figure(title=title)
    event_map = folium.Map(tiles="OpenStreetMap", prefer_canvas=True)
    event_map.add_to(figure)

    events = list(events)

    for event in events:
        folium.CircleMarker(
            location=[event.lat, event.long],
            radius=4,
            color=colour(event),
            fill=True,
            fill_opacity=0.8,
            popup=folium.Popup(popup_html(event), max_width=300),
            tooltip=event.name,
        ).add_to(event_map)

    if events:
        event_map.fit_bounds([
            [min(event.lat for event in events), min(event.long for event in events)],
            [max(event.lat for event in events), max(event.long for event in events)],
        ])

    show_in_browser(figure.render())
