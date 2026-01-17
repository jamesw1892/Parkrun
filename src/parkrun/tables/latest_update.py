"""
Print a table with a summary of the result of each given parkrunner that did the
most recent parkrun between the given dates.
"""

import datetime
from texttable import Texttable
from parkrun.api.cache import most_recent_parkrun
from parkrun import TABLE_MAX_WIDTH
from parkrun.api.scraper import fetch_runner_results
from parkrun.api.utils import date_description
from parkrun.models.position import get_ordinal_suffix
from parkrun.models.runner import Runner
from parkrun.models.runner_result import RunnerResult

def latest_update(runner_ids: list[int], start_date: datetime.date, end_date: datetime.date) -> None:
    """
    Print a table with a summary of the result for each given parkrunner that
    did the most recent parkrun between the given dates. Parkrunners that did
    not do this parkrun are not included in the table. The end date is made no
    later than today.
    """

    # We don't have results for parkruns in the future
    end_date = min(end_date, datetime.date.today())

    # Get the most recent parkrun that occurred before the end date
    most_recent_parkrun_date: datetime.date = most_recent_parkrun(datetime.datetime.combine(end_date, datetime.time(23, 59, 59))).date()

    if most_recent_parkrun_date < start_date:
        print(f"No parkruns occurred {date_description(start_date, end_date)}")
        return

    runners: list[Runner] = [fetch_runner_results(runner_id, start_date, end_date) for runner_id in runner_ids]

    print(f"Parkrunners who did the parkrun on {most_recent_parkrun_date}")

    table = Texttable(TABLE_MAX_WIDTH)
    table.header([
        "Parkrunner",
        "Parkrun",
        "Location",
        "Time",
        "Position",
        "Age Grade",
    ])

    for runner in runners:
        result: RunnerResult = runner.latest_result

        # Skip parkrunners who didn't do the most recent parkrun
        if result is None or result.date != most_recent_parkrun_date:
            continue

        results_at_location: list[RunnerResult] = list(filter(lambda r: r.location == result.location, runner.results))
        times_at_location: int = len(results_at_location)

        time_extra: str = ""
        if result.time.timedelta == runner.best_times[0].time.timedelta:
            time_extra = " (global PB)"
        elif times_at_location > 1 and all(result.time.timedelta <= r.time.timedelta for r in results_at_location):
            time_extra = " (event PB)"

        position_extra: str = ""
        if result.position.value == runner.best_positions[0].position.value:
            position_extra = " (global PB)"
        elif times_at_location > 1 and all(result.position.value <= r.position.value for r in results_at_location):
            position_extra = " (event PB)"

        age_grade_extra: str = ""
        if result.age_grade.value == runner.best_age_grades[0].age_grade.value:
            age_grade_extra = " (global PB)"
        elif times_at_location > 1 and all(result.age_grade.value >= r.age_grade.value for r in results_at_location):
            age_grade_extra = " (event PB)"

        table.add_row([
            runner.format_identity(),
            f"{len(runner.results)}{get_ordinal_suffix(len(runner.results))}",
            f"{times_at_location}{get_ordinal_suffix(times_at_location)} at {result.location} (event number {result.run_number})",
            f"{result.time}{time_extra}",
            f"{result.position}{position_extra}",
            f"{result.age_grade}{age_grade_extra}",
        ])

    print(table.draw())
