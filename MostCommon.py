"""
Print a table with a thing about the parkrunner sorted by how many times that
thing occurred, side-by-side for each given parkrunner.
"""

from typing import Any
from models.runner import Runner
from models.runner_result import RunnerResult
from Scraper import fetch_runner_results
from collections.abc import Callable
from collections import Counter
from texttable import Texttable
from itertools import zip_longest
import os

def most_common_things_runner(runner_ids: list[int], runner_to_counter: Callable[[Runner], Counter]) -> None:
    """
    Print a table with a column for each parkrunner where the column is the
    list of the things in order from most common to least common. The thing is
    calculated by passing the Runner object of the parkrunner to the given
    function to return a Counter object of the things.
    
    For example, since Runner has an attribute locations_counter, to print a
    table of all unique locations the runner has run at with how many times each
    one has been run, from most ran at to least ran at, call the function like
    this: most_common_things_runner(runner_ids, lambda runner: runner.locations_counter)
    """

    runners: list[Runner] = list(map(fetch_runner_results, runner_ids))
    counters: list[Counter] = list(map(runner_to_counter, runners))
    most_common_things: list[list[tuple[Any, int]]] = [counter.most_common() for counter in counters]

    table = Texttable(int(os.getenv("TABLE_MAX_WIDTH", 180)))
    table.header(["#"] + [runner.format_identity() for runner in runners])
    position: int = 1
    for runners_thing in zip_longest(*most_common_things):
        table.add_row([position] + ["" if runner_thing is None else f"{runner_thing[0]} ({runner_thing[1]})" for runner_thing in runners_thing])
        position += 1
    print(table.draw())

def most_common_things_result(runner_ids: list[int], result_to_thing: Callable[[RunnerResult], Any]) -> None:
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
    most_common_things_runner(runner_ids, lambda runner: Counter(map(result_to_thing, runner.results)))

def most_common_month(runner_ids: list[int]) -> None:
    """
    Print a table of the most common months of the year during which the given
    parkrunners have run.
    """
    most_common_things_result(runner_ids, lambda result: result.date.strftime("%b"))

def most_common_year(runner_ids: list[int]) -> None:
    """
    Print a table of the most common years during which the given parkrunners
    have run.
    """
    most_common_things_runner(runner_ids, lambda runner: runner.year_counter)

def most_common_location(runner_ids: list[int]) -> None:
    """
    Print a table of the most common locations the given parkrunners have run
    at.
    """
    most_common_things_runner(runner_ids, lambda runner: runner.locations_counter)

def most_common_time_seconds(runner_ids: list[int]) -> None:
    """
    Print a table of the most common seconds at the end of the time out of all
    the given parkrunners' results.
    """
    most_common_things_result(runner_ids, lambda result: result.time.timedelta.seconds % 60)
