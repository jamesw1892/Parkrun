"""
Print a table allowing side-by-side comparisons of the runs that all given
parkrunners did together.
"""

import datetime
from parkrun.models.runner import Runner
from parkrun import TABLE_MAX_WIDTH
from parkrun.api.scraper import fetch_runner_results
from parkrun.api.utils import date_description
from functools import reduce
from texttable import Texttable
from typing import Iterable
import os

def common_run_comparison(runner_ids: list[int], start_date: datetime.date, end_date: datetime.date) -> None:
    """
    Print a table allowing side-by-side comparisons of the runs that all given
    parkrunners did together.
    """

    def runner_to_set_events(runner: Runner) -> set[str]:
        return {result.format_for_event() for result in runner.results}

    runners: list[Runner] = [fetch_runner_results(runner_id, start_date, end_date) for runner_id in runner_ids]
    runners_events: Iterable[set[str]] = map(runner_to_set_events, runners)
    events_in_common: set[str] = reduce(lambda a, b: a.intersection(b), runners_events)

    print(f"{len(events_in_common)} events in common {date_description(start_date, end_date)}")

    rows: dict[str, list[str]] = {event_in_common: [] for event_in_common in events_in_common}
    identities: list[str] = []
    for runner in runners:
        identities.append(runner.format_identity())
        for result in runner.results:
            event: str = result.format_for_event()
            if event in rows:
                rows[event].append(result.format_for_result())

    table = Texttable(TABLE_MAX_WIDTH)
    table.header(["Parkrunner"] + identities)
    for event in sorted(rows):
        table.add_row([event] + rows[event])
    print(table.draw())
