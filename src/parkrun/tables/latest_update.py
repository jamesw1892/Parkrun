"""
Print a table with a summary of the result of each given parkrunner that did the
most recent parkrun between the given dates.
"""

from collections import defaultdict
import datetime
from parkrun.api.cache import most_recent_parkrun
from parkrun import get_table_max_width
from parkrun.api.scraper_runner import fetch_runner_results
from parkrun.maps.latest_update_map import latest_update_map
from parkrun.models.event import Event
from parkrun.models.position import get_ordinal_suffix
from parkrun.models.runner import Runner
from parkrun.models.runner_result import RunnerResult
from parkrun.tables.incremental_texttable import IncrementalTexttable

def latest_update(runner_ids: list[int], start_date: datetime.date, end_date: datetime.date, incremental: bool = True, show_map: bool = True) -> None:
    """
    Print a table with a summary of the result for each given parkrunner that
    did the most recent parkrun between the given dates. Parkrunners that did
    not do this parkrun are not included in the table. The end date is made no
    later than today and the start date is ignored, otherwise the PB indicators
    and parkrun numbers don't make sense. If incremental then rather than
    fetching all results and printing the table at the end, it prints a row at
    a time. If show_map then afterwards also show a map of the events the
    parkrunners in the table did, coloured by who did each.
    """

    # We don't have results for parkruns in the future and consider all parkruns
    # before then - ignoring start_date
    start_date = datetime.date.min
    end_date = min(end_date, datetime.date.today())

    # Get the most recent parkrun that occurred before the end date
    most_recent_parkrun_date: datetime.date = most_recent_parkrun(datetime.datetime.combine(end_date, datetime.time(23, 59, 59))).date()

    print(f"Parkrunners who did the parkrun on {most_recent_parkrun_date}")

    event_runners: defaultdict[Event, list[Runner]] = defaultdict(list)

    # If incremental, set reasonable column widths with the parkrunner and
    # location sharing what's left after the fixed width columns. This must be
    # pre-calculated so it's reasonable and stays consistent
    with IncrementalTexttable([
        ("Parkrunner", "50%"),
        ("Parkrun", 7),
        ("Location", "50%"),
        ("Time", 7),
        ("Position", 8),
        ("Age Grade", 9),
    ], get_table_max_width(), incremental) as table:
        for runner_id in runner_ids:
            runner: Runner = fetch_runner_results(runner_id, start_date, end_date)
            result: RunnerResult = runner.latest_result

            # Skip parkrunners who didn't do the most recent parkrun
            if result is None or result.date != most_recent_parkrun_date:
                continue

            event_runners[result.location].append(runner)

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
                f"{times_at_location}{get_ordinal_suffix(times_at_location)} at {result.location}",
                f"{result.time}{time_extra}",
                f"{result.position}{position_extra}",
                f"{result.age_grade}{age_grade_extra}",
            ])

    if show_map:
        latest_update_map(dict(event_runners), most_recent_parkrun_date)
