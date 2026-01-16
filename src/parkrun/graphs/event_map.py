from parkrun.api.scraper import fetch_events
from parkrun.models.event_collection import EventCollection
from parkrun.models.event import Event
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

def main():
    """
    Display a MatPlotLib world map of all parkruns.
    """

    events: EventCollection = fetch_events()

    m = Basemap()
    m.drawcoastlines()
    m.drawcountries()

    for event in events:
        m.scatter(event.lat, event.long)

    plt.show()
