"""
Print a table with a summary of the result of each given parkrunner that did the
most recent parkrun between the given dates.
"""

import datetime
from texttable import Texttable
from parkrun.api.cache import most_recent_parkrun
from parkrun import get_table_max_width
from parkrun.api.scraper_runner import fetch_runner_results
from parkrun.models.position import get_ordinal_suffix
from parkrun.models.runner import Runner
from parkrun.models.runner_result import RunnerResult

HEADERS: list[str] = [
    "Parkrunner",
    "Parkrun",
    "Location",
    "Time",
    "Position",
    "Age Grade",
]

def latest_update(runner_ids: list[int], start_date: datetime.date, end_date: datetime.date, incremental: bool = True) -> None:
    """
    Print a table with a summary of the result for each given parkrunner that
    did the most recent parkrun between the given dates. Parkrunners that did
    not do this parkrun are not included in the table. The end date is made no
    later than today and the start date is ignored, otherwise the PB indicators
    and parkrun numbers don't make sense. If incremental then rather than
    fetching all results and printing the table at the end, it prints a row at
    a time.
    """

    # We don't have results for parkruns in the future and consider all parkruns
    # before then - ignoring start_date
    start_date = datetime.date.min
    end_date = min(end_date, datetime.date.today())

    # Get the most recent parkrun that occurred before the end date
    most_recent_parkrun_date: datetime.date = most_recent_parkrun(datetime.datetime.combine(end_date, datetime.time(23, 59, 59))).date()

    print(f"Parkrunners who did the parkrun on {most_recent_parkrun_date}")

    rows: list[list[str]] = [HEADERS]

    if incremental:

        # Set reasonable column widths as proportions of the maximum width
        # This must be pre-calculated so it's reasonable and stays consistent
        # Remaining width after the fixed column's width must also subtract the
        # padding and vertical separator to the right of each column as well as
        # the vertical separator on the far left
        PARKRUN_COL_WIDTH: int = 7
        REMAINING_WIDTH: int = get_table_max_width() - PARKRUN_COL_WIDTH - 3 * len(HEADERS) - 1
        DENOMINATOR: int = 100
        table = Texttable().set_cols_width([
            REMAINING_WIDTH * 22 // DENOMINATOR,
            PARKRUN_COL_WIDTH,
            REMAINING_WIDTH * 35 // DENOMINATOR,
            REMAINING_WIDTH * 14 // DENOMINATOR,
            REMAINING_WIDTH * 14 // DENOMINATOR,
            REMAINING_WIDTH * 14 // DENOMINATOR,
        ])

        # Print the header row without the bottom line (it adds a bottom border
        # in addition to the header border despite there being no non-header rows)
        print(table.header(HEADERS).draw()[::-1].split("\n", 1)[1][::-1])

    for runner_id in runner_ids:
        runner: Runner = fetch_runner_results(runner_id, start_date, end_date)
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

        rows.append([
            runner.format_identity(),
            f"{len(runner.results)}{get_ordinal_suffix(len(runner.results))}",
            f"{times_at_location}{get_ordinal_suffix(times_at_location)} at {result.location} (event number {result.run_number})",
            f"{result.time}{time_extra}",
            f"{result.position}{position_extra}",
            f"{result.age_grade}{age_grade_extra}",
        ])

        # Print the latest row (only) without the top border
        if incremental:
            print(table.reset().add_row(rows[-1]).draw().split("\n", 1)[1])

    if not incremental:
        print(Texttable(get_table_max_width()).add_rows(rows).draw())
