import requests
from bs4 import BeautifulSoup
import Cache
import logging
import json

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

def fetch_events():
    url = "https://images.parkrun.com/events.json"
    response = session.get(url)
    response.raise_for_status() # Raise a HTTPError for bad responses (4xx and 5xx)
    return response.json() # Parse the response as JSON

def fetch_runner_results(number: int) -> list[list[str]]:
    """
    Returns a list with an element for each parkrun the parkrunner has
    completed. Each element is a list of strings where the elements are:

    0: Location name
    1: Date in form DD/MM/YYYY
    2: Run number (int, of the location)
    3: Position (int)
    4: Time in form MM:SS
    5: Age grading in form xx.xx%
    6: PB? Empty string or "PB" if it's the best and not the only time the
    parkrunner has run at this location
    """

    url: str = f"https://www.parkrun.org.uk/parkrunner/{number}/all/"

    data: None | str = Cache.check_cache("runner_results", f"{number}.json")
    if data is None:

        # Fetch
        response = session.get(url)
        response.raise_for_status() # Raise a HTTPError for bad responses (4xx and 5xx)

        # Parse the HTML response
        soup = BeautifulSoup(response.text, 'html.parser')

        # Ignore other tables as can be worked out from main table
        _, _, all_results_table = soup.findAll('table', {'id': 'results'})

        # Extract rows from the table
        rows = all_results_table.find_all('tr')
        results = []
        for row in rows[1:]: # Skip the header row
            cols = row.find_all('td')
            results.append([col.text.strip() for col in cols])

        data = json.dumps(results)
        Cache.write_cache("runner_results", f"{number}.json", data)
    else:
        results = json.loads(data)

    return results
