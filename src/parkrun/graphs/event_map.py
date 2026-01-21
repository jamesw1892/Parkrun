from parkrun.api.scraper import fetch_events, fetch_runner_results
from parkrun.models.runner import Runner
from parkrun.models.event_collection import EventCollection
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

def event_map(runner_id: int, only_adult: bool = True):
    """
    Display a MatPlotLib world map of all parkruns with ones the parkrunner with
    given ID has done as green dots and those they haven't as red dots.
    """

    runner: Runner = fetch_runner_results(runner_id)
    events: EventCollection = fetch_events()

    m = Basemap()
    m.drawcoastlines()
    m.drawcountries()

    for event in events:
        if only_adult and not event.is_adult():
            continue
        m.scatter(
            event.lat,
            event.long,
            color="green" if event.name in runner.unique_locations else "red"
        )

    plt.show()
