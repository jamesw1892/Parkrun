"""
Print a table with information about each time each parkrunner improved their PB
side-by-side.
"""

from parkrun.models.runner import Runner
from parkrun.models.time import Time
from parkrun import TABLE_MAX_WIDTH
from parkrun.api.scraper import fetch_runner_results
from parkrun.api.utils import date_description
from texttable import Texttable
import datetime

def s(n: int) -> str:
    """
    Return an s if the given number is not 1 else empty string. Used to
    pluralise regular nouns if necessary.
    """
    return "" if n == 1 else "s"

def pb_progress(runner_ids: list[int], start_date: datetime.date, end_date: datetime.date):
    """
    Print a table with the dates each parkrunner improved their PB along with
    details about that parkrun and how much progress was made over how long.
    """
    today: datetime.date = datetime.date.today()
    num_runners: int = len(runner_ids)

    runners: list[Runner] = [fetch_runner_results(runner_id, start_date, end_date) for runner_id in runner_ids]

    # Populate a dictionary with a key for each date that any parkrunner
    # improved their PB. The corresponding value is a list with an element for
    # each parkrunner. The value for parkrunners who improved their PB on that
    # date is a string with details about the improvement. If they didn't
    # improve, it is an empty string. These lists will become the rows of the
    # output table.
    dates_and_times: dict[datetime.date, list[str]] = dict()

    weeks_ago: list[int] = []
    num_runs_ago: list[int] = []

    for runner_index, runner in enumerate(runners):
        current_pb_time: Time = None
        current_pb_date: datetime.date = None
        num_runs: int = 0

        # Go through the results from first to last
        for result in runner.results[::-1]:

            num_runs += 1
            if current_pb_time is None or result.time.timedelta < current_pb_time.timedelta:

                if result.date not in dates_and_times:
                    dates_and_times[result.date] = ["" for _ in range(num_runners)]

                # Calculate the time difference to the previous PB as well as
                # the number of weeks and runs since
                diff: str = f"first parkrun"
                if current_pb_time is not None:
                    time_diff: Time = Time.from_timedelta(current_pb_time.timedelta - result.time.timedelta)
                    weeks: int = (result.date - current_pb_date).days // 7
                    diff: str = f"-{time_diff} after {weeks} week{s(weeks)} and {num_runs} parkrun{s(num_runs)}"

                # Display the time and location of the PB plus the difference
                # to the previous PB
                dates_and_times[result.date][runner_index] = f"{result.time} at {result.location} ({diff})"

                current_pb_time = result.time
                current_pb_date = result.date
                num_runs = 0

        weeks_ago.append((today - current_pb_date).days // 7 if current_pb_date is not None else 0)
        num_runs_ago.append(num_runs)

    print(f"PB progress {date_description(start_date, end_date)}")

    # Draw the table
    table = Texttable(TABLE_MAX_WIDTH)
    table.header(["Date"] + [runner.format_identity() for runner in runners])

    # Display a row for each date in ascending order
    for date in sorted(dates_and_times):
        table.add_row([date] + dates_and_times[date])

    # Add a final row of how many weeks and runs their all time PB was ago
    table.add_row(["PB was"] + [
        f"{weeks} week{s(weeks)} and {num_runs} parkrun{s(num_runs)} ago"
        for weeks, num_runs in zip(weeks_ago, num_runs_ago)
    ])

    print(table.draw())
