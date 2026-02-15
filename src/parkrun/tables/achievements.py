"""
Print a table with a side-by-side comparison of achievement progress by each
parkrunner.
"""

import datetime
from collections.abc import Callable
from parkrun import TABLE_MAX_WIDTH
from parkrun.api.scraper import fetch_runner_results, fetch_events
from parkrun.api.utils import date_description
from parkrun.models.runner import Runner
from parkrun.models.runner_result import RunnerResult
import re
import string
from texttable import Texttable
from typing import Any

def achievement_location_contains(name: str, ticklist: list[str]) -> tuple[str, Callable[[RunnerResult], str], list[str]]:
    """
    Return a tuple as required for each achievement with the given name for all
    locations that contain one of the given substrings in the ticklist.
    """

    def result_func(result: RunnerResult) -> str:
        for substr in ticklist:
            if substr.lower() in result.location.name.lower():
                return substr
        return ""

    return name, result_func, ticklist

def achievement_location_matches(name: str, pattern: str | re.Pattern) -> tuple[str, Callable[[RunnerResult], str], list[str]]:
    """
    Return a tuple as required for each achievement with the given name for all
    locations matching the given regular expression pattern.
    """

    if isinstance(pattern, str):
        pattern: re.Pattern = re.compile(pattern, flags=re.IGNORECASE)

    ticklist = sorted(location for location in fetch_events().event_ids_by_name if pattern.search(location))

    return name, lambda result: result.location.name, ticklist

# Calculate all strings of the form MM-DD for all days in a (leap) year for use
# in the Calendar Bingo achievement
ALL_DAYS_OF_YEAR: list[str] = []
current = datetime.date(2000, 1, 1)
while current.year == 2000:
    ALL_DAYS_OF_YEAR.append(current.strftime("%m-%d"))
    current += datetime.timedelta(days=1)

ACHIEVEMENTS: tuple[tuple[str, Callable[[RunnerResult], Any], list[Any]]] = (
    ("Alphabet", lambda result: result.location.name[0].upper(), list(string.ascii_uppercase.replace("X", ""))),
    achievement_location_matches("All Saints", r"\bSt\b"),
    achievement_location_matches("Bay Watch", r"\bBay\b"),
    ("Calendar Bingo", lambda result: result.date.strftime("%m-%d"), ALL_DAYS_OF_YEAR),
    achievement_location_contains("Compass Club", ["North", "South", "East", "West"]),
    achievement_location_matches("King Of The Castle", r"\bCastle\b"),
    ("Stopwatch Bingo", lambda result: f"{result.time.timedelta.seconds % 60:02}", [f"{n:02}" for n in range(60)]),
)

def runner_to_achievement_progress(runner: Runner, result_func: Callable[[RunnerResult], Any], ticklist: list[Any]) -> str:
    """
    Helper function for achievements. Takes a runner and the result function 
    and ticklist of an achievement and returns a string detailing the runner's
    progress towards the achievement.
    """

    achieved_where: dict[Any, RunnerResult] = {result_func(result): result for result in runner.results}
    achieved: set[Any] = set(achieved_where)

    # Remove any not in the ticklist
    achieved.intersection_update(set(ticklist))

    num_achieved: int = len(achieved)
    total: int = len(ticklist)
    percentage: int = round(num_achieved / total * 100)

    # Give headline progress and then list all parts and the event they were
    # first achieved at or blank if not yet achieved
    return f"{num_achieved}/{total} = {percentage}%\n" + "\n".join(
        f"{part}: {achieved_where[part].format_for_event() if part in achieved_where else ''}"
        for part in ticklist
    )

def achievements(runner_ids: list[int], start_date: datetime.date, end_date: datetime.date) -> None:
    """
    Print a table with a side-by-side comparison of achievement progress by each
    parkrunner.
    """

    runners: list[Runner] = [fetch_runner_results(runner_id, start_date, end_date) for runner_id in runner_ids]

    print(f"Achievements {date_description(start_date, end_date)}")

    table = Texttable(TABLE_MAX_WIDTH)
    table.header(["Achievement"] + [runner.format_identity() for runner in runners])
    for name, result_func, ticklist in ACHIEVEMENTS:
        table.add_row([name] + [runner_to_achievement_progress(runner, result_func, ticklist) for runner in runners])
    print(table.draw())
