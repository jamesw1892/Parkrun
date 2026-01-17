from parkrun.models.runner import Runner
from parkrun.models.runner_result import RunnerResult
from parkrun.models.event_collection import EventCollection
from parkrun.api.parkrun_exception import ParkrunException
from parkrun.api.cache import check_cache, write_cache
import requests
from bs4 import BeautifulSoup, Tag
import logging
import json
import datetime

logger = logging.getLogger(__name__)

# Taken from https://github.com/BadgerHobbs/Parkrun-API-Python
session = requests.Session()
session.headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1"
}

def fetch_events() -> EventCollection:
    """
    Return an EventCollection with all events.
    """

    url: str = "https://images.parkrun.com/events.json"
    type_name: str = "events"
    file_name: str = "events.json"

    json_str: str | None = check_cache(type_name, file_name)
    if json_str is None:

        # Fetch
        response = session.get(url)
        response.raise_for_status() # Raise a HTTPError for bad responses (4xx and 5xx)
        json_data: dict = response.json() # Parse the response as JSON
        json_str: str = json.dumps(json_data)

        write_cache(type_name, file_name, json_str)

    else:
        json_data: dict = json.loads(json_str)

    return EventCollection(json_data)

def fetch_runner_results(
    number: int,
    start_date: datetime.date = datetime.date.min,
    end_date: datetime.date = datetime.date.max
) -> Runner:
    """
    Return a Runner object containing each parkrun the parkrunner has completed
    between the start and end dates (inclusive), or all time if not provided.
    """

    url: str = f"https://www.parkrun.org.uk/parkrunner/{number}/all/"
    type_name: str = "runner_results"
    file_name: str = f"{number}.html"

    html: None | str = check_cache(type_name, file_name)
    if html is None:

        # Fetch
        response = session.get(url)
        if response.status_code == 404:
            raise ParkrunException(f"No parkrunner exists with number '{number}'")
        response.raise_for_status() # Raise a HTTPError for bad responses (4xx and 5xx)
        html = response.text

        write_cache(type_name, file_name, html)

    # Parse the HTML response
    soup = BeautifulSoup(html, 'html.parser')

    # Extract name
    h2s: list[Tag] = soup.findAll('h2')
    assert len(h2s) == 1, f"Unexpectedly found not 1 h2 tag in the runner results page of '{number}'"
    name: str = h2s[0].contents[0].strip()

    # Extract most recent age category
    most_recent_age_category: str = h2s[0].findNext('p').contents[-1].split()[-1]

    # Ignore other tables as can be worked out from main table
    results_tables: list[Tag] = soup.findAll('table', {'id': 'results'})
    assert len(results_tables) == 3, f"Unexpectedly found not 3 tables with id 'results' in the runner results page of '{number}'"
    all_results_table: Tag = results_tables[2]

    # Extract rows from the table
    rows: list[Tag] = all_results_table.find_all('tr')
    results = []
    for row in rows[1:]: # Skip the header row
        cols = row.find_all('td')
        results.append([col.text.strip() for col in cols])

    runner_results: list[RunnerResult] = [RunnerResult.from_table(result) for result in results]
    runner_results: list[RunnerResult] = list(filter(lambda result: start_date <= result.date <= end_date, runner_results))

    return Runner(number, name, most_recent_age_category, runner_results, start_date, end_date)
