"""
Print a table with statistics about each given parkrunner side-by-side.
"""

from models.runner import Runner
from typing import Any
from Scraper import fetch_runner_results
from collections.abc import Callable
from texttable import Texttable
import os

STATS: tuple[tuple[str, Callable[[Runner], Any]]] = (
    ("Most Recent Age Category"  , lambda runner: runner.most_recent_age_category),
    ("Num Runs"                  , lambda runner: len(runner.results)),
    ("Total Run Time"            , lambda runner: runner.total_run_time),
    ("Average Run Time"          , lambda runner: runner.average_run_time),
    ("First Run"                 , lambda runner: runner.first_result),
    ("Lastest Run"               , lambda runner: runner.latest_result),
    ("Best Time"                 , lambda runner: runner.best_time.format_for_time()),
    ("Best Age Grade"            , lambda runner: runner.best_age_grade.format_for_age_grade()),
    ("Best Position"             , lambda runner: runner.best_position.format_for_position()),
    ("Most Runs In A Year"       , lambda runner: f"{runner.most_runs_per_year_count} ({runner.most_runs_per_year_year})"),
    ("Most Runs At A Location"   , lambda runner: f"{runner.most_runs_per_location_count} ({runner.most_runs_per_location_location})"),
    ("Number of Unique Locations", lambda runner: runner.num_unique_locations),
    ("Tourism Percentage"        , lambda runner: f"{runner.tourism_percentage * 100:.2f}%"),
    ("Consistency"               , lambda runner: f"{runner.consistency * 100:.2f}%")
)

def runner_stats(runner_ids: list[int]) -> None:
    """
    Print a table with statistics about each given parkrunner side-by-side.
    """

    runners: list[Runner] = [fetch_runner_results(runner_id) for runner_id in runner_ids]

    table = Texttable(int(os.getenv("TABLE_MAX_WIDTH", 180)))
    table.header(["Parkrunner"] + [runner.format_identity() for runner in runners])
    for stat_name, stat_func in STATS:
        table.add_row([stat_name] + [stat_func(runner) for runner in runners])
    print(table.draw())
