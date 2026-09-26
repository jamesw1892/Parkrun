"""
Print a table with a thing about the parkrunner sorted by how many times that
thing occurred, side-by-side for each given parkrunner.
"""

import datetime
from typing import Any, Optional
from parkrun.models.runner import Runner
from parkrun.models.runner_result import RunnerResult
from parkrun import get_table_max_width
from parkrun.api.cache import max_parkruns_in_year
from parkrun.api.scraper_runner import fetch_runner_results
from parkrun.api.utils import date_description
from collections.abc import Callable
from collections import Counter
from texttable import Texttable
from itertools import zip_longest

def most_common_things_runner(
    runner_ids: list[int],
    runner_to_counter: Callable[[Runner], Counter[Any]],
    start_date: datetime.date,
    end_date: datetime.date,
    format_thing: Optional[Callable[[Any, int], str]] = None,
    sort_key: Optional[Callable[[Any, int], float]] = None,
) -> None:
    """
    Print a table with a column for each parkrunner where the column is the
    list of the things in order from most common to least common. The thing is
    calculated by passing the Runner object of the parkrunner to the given
    function to return a Counter object of the things. format_thing is a
    function that given the thing and the number of them there are for each
    runner, return a string to display in the cell of the table. By default this
    is just '<thing> (<count>)'.
    If sort_key is provided then sort the results by the outcome of this
    (in descending order) rather than just the number in the counter.
    
    For example, since Runner has an attribute locations_counter, to print a
    table of all unique locations the runner has run at with how many times each
    one has been run, from most ran at to least ran at, call the function like
    this: most_common_things_runner(runner_ids, lambda runner: runner.locations_counter)
    """

    if format_thing is None:
        format_thing = lambda thing, count: f"{thing} ({count})"

    runners: list[Runner] = [fetch_runner_results(runner_id, start_date, end_date) for runner_id in runner_ids]
    counters: list[Counter[Any]] = list(map(runner_to_counter, runners))
    if sort_key is None:
        most_common_things: list[list[tuple[Any, int]]] = [counter.most_common() for counter in counters]
    else:
        most_common_things = [sorted(counter.items(), key=lambda item: sort_key(item[0], item[1]), reverse=True) for counter in counters]

    table = Texttable(get_table_max_width())
    table.header(["#"] + [runner.format_identity() for runner in runners])
    rank: int = 1
    for runners_thing in zip_longest(*most_common_things):
        table.add_row([rank] + ["" if runner_thing is None else format_thing(runner_thing[0], runner_thing[1]) for runner_thing in runners_thing])
        rank += 1
    print(table.draw())

def most_common_things_result(runner_ids: list[int], result_to_thing: Callable[[RunnerResult], Any], start_date: datetime.date, end_date: datetime.date) -> None:
    """
    Print a table with a column for each parkrunner where the column is the
    list of the things in order from most common to least common. The thing is
    calculated by passing each RunnerResult of the parkrunner to the given
    function.

    For example, to print a table of all unique locations the runner has run at
    with how many times each one has been run, from most ran at to least ran at
    (without using the locations_counter attribute of Runner), call the function
    like this: most_common_things_result(runner_ids, lambda result: result.location)
    """
    most_common_things_runner(runner_ids, lambda runner: Counter(map(result_to_thing, runner.results)), start_date, end_date)

def most_common_month(runner_ids: list[int], start_date: datetime.date, end_date: datetime.date) -> None:
    """
    Print a table of the most common months of the year during which the given
    parkrunners have run.
    """
    most_common_things_result(runner_ids, lambda result: result.date.strftime("%b"), start_date, end_date)

def most_common_year(runner_ids: list[int], start_date: datetime.date, end_date: datetime.date) -> None:
    """
    Print a table of the most common years during which the given parkrunners
    have run in order from the highest percentage of possible parkruns completed
    to the lowest.
    """

    print(f"Most parkruns run in each year as a percentage of the maximum possible number (so the current year may be higher than its raw number) {date_description(start_date, end_date)}")

    # The end date defaults to forever so limit it to today since parkruns in the
    # future can't have been run yet
    last_date: datetime.date = min(end_date, datetime.date.today())

    def percentage(year: int, count: int) -> float:
        max_count: int = max_parkruns_in_year(year, start_date, last_date)
        return count / max_count if max_count else 0

    def format_year_percentage(year: int, count: int) -> str:
        max_count: int = max_parkruns_in_year(year, start_date, last_date)
        return f"{year} ({count}/{max_count} = {percentage(year, count) * 100:.0f}%)"

    most_common_things_runner(
        runner_ids,
        lambda runner: runner.year_counter,
        start_date,
        end_date,
        format_year_percentage,
        percentage,
    )

def most_common_location(runner_ids: list[int], start_date: datetime.date, end_date: datetime.date) -> None:
    """
    Print a table of the most common locations the given parkrunners have run
    at.
    """
    most_common_things_runner(runner_ids, lambda runner: runner.locations_counter, start_date, end_date)

def most_common_location_initial(runner_ids: list[int], start_date: datetime.date, end_date: datetime.date) -> None:
    """
    Print a table of the most common first letters of parkrun locations that the
    given parkrunners have run at (including duplicate locations).
    """
    most_common_things_result(runner_ids, lambda result: result.location.name[0], start_date, end_date)

def most_common_time_seconds(runner_ids: list[int], start_date: datetime.date, end_date: datetime.date) -> None:
    """
    Print a table of the most common seconds at the end of the time out of all
    the given parkrunners' results.
    """
    most_common_things_result(runner_ids, lambda result: result.time.timedelta.seconds % 60, start_date, end_date)

def most_common_country(runner_ids: list[int], start_date: datetime.date, end_date: datetime.date) -> None:
    """
    Print a table of the most common countries that the given parkrunners have
    run parkrun(s) in.
    """

    most_common_things_result(runner_ids, lambda result: result.location.country.name, start_date, end_date)
