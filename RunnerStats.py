"""
Calculate statistics about the given runner.

Functions are written for each statistic producing atomic results where
possible. Each function takes the results table with type list[list[str]] and
outputs the statistic of whatever type.
"""

from Runner import Runner
from RunnerResult import RunnerResult
from typing import Any
from Scraper import fetch_runner_results
from collections.abc import Callable
import datetime
from collections import Counter
import os
from dotenv import load_dotenv
from texttable import Texttable

load_dotenv()

################################################################################
# Statistic functions
################################################################################

# TODO: Move all this logic to Runner class, remove these functions, and just
# call in STATS which could be a function taking the Runner object so it can
# call methods on it rather than having to be functions or lambdas

def num_runs(runner: Runner) -> int:
    return len(runner.results)

def total_kms_run(runner: Runner) -> int:
    return len(runner.results) * 5

def total_run_time(runner: Runner) -> datetime.timedelta:
    return sum(map(lambda result: result.time, runner.results), start=datetime.timedelta())

def average_run_time(runner: Runner) -> str:
    """String in the form MM:SS"""

    ans: datetime.timedelta = total_run_time(runner) / num_runs(runner)
    total_seconds: int = round(ans.total_seconds())
    mins, secs = divmod(total_seconds, 60)
    return f"{mins:02d}:{secs:02d}"

def first_run(runner: Runner) -> RunnerResult:
    return runner.first_result

def latest_run(runner: Runner) -> RunnerResult:
    return runner.latest_result

def best_time(runner: Runner) -> str:
    return runner.best_time.format_for_time()

def best_age_grade(runner: Runner) -> str:
    return runner.best_age_grading.format_for_age_grading()

def best_position(runner: Runner) -> str:
    return runner.best_position.format_for_position()

def most_runs_per_year(runner: Runner) -> str:
    return f"{runner.most_runs_per_year_count} ({runner.most_runs_per_year_year})"

def most_runs_per_location(runner: Runner) -> str:
    return f"{runner.most_runs_per_location_count} ({runner.most_runs_per_location_location})"

def num_unique_locations(runner: Runner) -> int:
    return runner.num_unique_locations

def tourism_percentage_formatted(runner: Runner) -> str:
    """xx.xx%"""
    return f"{runner.tourism_percentage * 100:.2f}%"

################################################################################
# List of statistic names corresponding to the function to calculate them
################################################################################

STATS: tuple[tuple[str, Callable[[Runner], Any]]] = (
    ("Num Runs", num_runs),
    ("Total Kilometres Run", total_kms_run),
    ("Total Run Time", total_run_time),
    ("Average Run Time", average_run_time),
    ("First Run", first_run),
    ("Lastest Run", latest_run),
    ("Best Time", best_time),
    ("Best Age Grade", best_age_grade),
    ("Best Position", best_position),
    ("Most Runs In A Year", most_runs_per_year),
    ("Most Runs At A Location", most_runs_per_location),
    ("Number of Unique Locations", num_unique_locations),
    ("Tourism Percentage", tourism_percentage_formatted),
)

################################################################################
# Main to print all statistics
################################################################################

def main(runner_env_strs: list[str]) -> None:
    """
    Print a table with the statistics for each given parkrunner side-by-side.
    """

    runner_ids  : list[int] = []
    runner_names: list[str] = []
    for runner_env_str in runner_env_strs:
        runner_ids.append(int(os.getenv(runner_env_str)))
        runner_names.append(runner_env_str.removeprefix("PARKRUNNER_"))

    runners: list[Runner] = [fetch_runner_results(runner_id) for runner_id in runner_ids]

    table = Texttable(180)
    table.header(["Name"] + runner_names)
    table.add_row(["Number"] + runner_ids)
    for stat_name, stat_func in STATS:
        table.add_row([stat_name] + [stat_func(runner) for runner in runners])
    print(table.draw())

if __name__ == "__main__":
    main([
        "PARKRUNNER_ME",
    ])
