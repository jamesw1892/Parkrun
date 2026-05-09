from parkrun.api.scraper import fetch, fetch_events
from parkrun.models.age_category import AgeCategory
from parkrun.models.event_collection import EventCollection
from parkrun.models.runner import Runner
from parkrun.models.runner_result import RunnerResult
from bs4 import BeautifulSoup, Tag
from functools import cache
import datetime

@cache
def fetch_runner_results(
    number: int,
    start_date: datetime.date = datetime.date.min,
    end_date: datetime.date = datetime.date.max
) -> Runner:
    """
    Return a Runner object containing each parkrun the parkrunner has completed
    between the start and end dates (inclusive), or all time if not provided.
    """

    html: str = fetch(
        url=f"https://www.parkrun.org.uk/parkrunner/{number}/all/",
        type_name="runner_results",
        file_name=f"{number}.html",
        err_msg_404=f"No parkrunner exists with number '{number}'",
    )

    # Parse the HTML response
    soup = BeautifulSoup(html, 'html.parser')

    # Extract name
    h2s: list[Tag] = soup.findAll('h2')
    assert len(h2s) == 1, f"Unexpectedly found not 1 h2 tag in the runner results page of '{number}'"
    name: str = h2s[0].contents[0].strip()

    # Extract most recent age category
    try:
        most_recent_age_cat_str = h2s[0].findNext('p').contents[-1].split()[-1]
    except:
        most_recent_age_cat_str = ""
    most_recent_age_category: AgeCategory = AgeCategory(most_recent_age_cat_str)

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

    all_events: EventCollection = fetch_events()
    runner_results: list[RunnerResult] = [RunnerResult.from_table(result, all_events) for result in results]
    runner_results: list[RunnerResult] = list(filter(lambda result: start_date <= result.date <= end_date, runner_results))

    return Runner(number, name, most_recent_age_category, runner_results, start_date, end_date)
