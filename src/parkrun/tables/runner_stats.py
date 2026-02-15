"""
Print a table with statistics about each given parkrunner side-by-side.
"""

import datetime
from parkrun.models.runner import Runner
from parkrun.models.runner_result import RunnerResult
from typing import Any
from parkrun import TABLE_MAX_WIDTH
from parkrun.api.scraper import fetch_runner_results
from parkrun.api.utils import date_description
from collections.abc import Callable
from texttable import Texttable

def format_events(results: list[RunnerResult]) -> str:
    return "; ".join(sorted(map(lambda x: x.format_for_event(), results)))

def format_iterable(iterable) -> str:
    return ", ".join(sorted(map(str, iterable)))

STATS: tuple[tuple[str, Callable[[Runner], Any]]] = (
    ("Most Recent Age Category"  , lambda runner: runner.most_recent_age_category),
    ("Num Runs"                  , lambda runner: len(runner.results)),
    ("Total Run Time"            , lambda runner: runner.total_run_time),
    ("Average Run Time"          , lambda runner: runner.average_run_time),
    ("First Run"                 , lambda runner: runner.first_result),
    ("Lastest Run"               , lambda runner: runner.latest_result),
    ("Best Time"                 , lambda runner: f"{runner.best_times[0].time} ({format_events(runner.best_times)})" if len(runner.best_times) > 0 else "None"),
    ("Best Age Grade"            , lambda runner: f"{runner.best_age_grades[0].age_grade} ({format_events(runner.best_age_grades)})" if len(runner.best_age_grades) > 0 else "None"),
    ("Best Position"             , lambda runner: f"{runner.best_positions[0].position} ({format_events(runner.best_positions)})" if len(runner.best_positions) > 0 else "None"),
    ("Most Runs In A Year"       , lambda runner: f"{runner.most_runs_per_year_count} ({format_iterable(runner.most_runs_per_year_years)})"),
    ("Most Runs At A Location"   , lambda runner: f"{runner.most_runs_per_location_count} ({format_iterable(runner.most_runs_per_location_locations)})"),
    ("Number of Unique Locations", lambda runner: runner.num_unique_locations),
    ("Tourism Percentage"        , lambda runner: f"{runner.tourism_percentage * 100:.2f}%"),
    ("Consistency"               , lambda runner: f"{runner.consistency * 100:.2f}%"),
    ("re-index"                  , lambda runner: f"{runner.re_index}"),
    ("p-index"                   , lambda runner: f"{runner.p_index}"),
)

def runner_stats(runner_ids: list[int], start_date: datetime.date, end_date: datetime.date) -> None:
    """
    Print a table with statistics about each given parkrunner side-by-side.
    """

    runners: list[Runner] = [fetch_runner_results(runner_id, start_date, end_date) for runner_id in runner_ids]

    print(f"Runner stats {date_description(start_date, end_date)}")

    table = Texttable(TABLE_MAX_WIDTH)
    table.header(["Parkrunner"] + [runner.format_identity() for runner in runners])
    for stat_name, stat_func in STATS:
        table.add_row([stat_name] + [stat_func(runner) for runner in runners])
    print(table.draw())
