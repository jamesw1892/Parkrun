"""
Print a table with statistics about each given parkrunner side-by-side.
"""

from models.runner import Runner
from typing import Any
from Scraper import fetch_runner_results
from collections.abc import Callable
import os
from texttable import Texttable

STATS: tuple[tuple[str, Callable[[Runner], Any]]] = (
    ("Name"                      , lambda runner: runner.name),
    ("Age Category"              , lambda runner: runner.age_category),
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
)

def main(runner_ids: list[int]) -> None:
    """
    Print a table with statistics about each given parkrunner side-by-side.
    """

    runners: list[Runner] = [fetch_runner_results(runner_id) for runner_id in runner_ids]

    table = Texttable(180)
    table.header(["Number"] + runner_ids)
    for stat_name, stat_func in STATS:
        table.add_row([stat_name] + [stat_func(runner) for runner in runners])
    print(table.draw())

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    main([
        int(os.getenv("PARKRUNNER_ME")),
    ])
