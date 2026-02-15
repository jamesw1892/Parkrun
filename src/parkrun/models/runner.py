import datetime
from collections import Counter
from functools import cached_property
from parkrun.models.runner_result import RunnerResult
from parkrun.models.time import Time
from parkrun.api.utils import minimals, maximals, most_common, date_description

class Runner:
    def __init__(
        self,
        number: int,
        name: str,
        most_recent_age_category: str,
        results: list[RunnerResult],
        start_date: datetime.date,
        end_date: datetime.date
    ):
        """
        Assume results in descending order of date. Only stores results
        between start_date and end_date, but most_recent_age_category could be
        since then.
        """

        self.number: int = number
        self.name: str = name
        self.most_recent_age_category: str = most_recent_age_category
        self.results: list[RunnerResult] = results
        self.start_date: datetime.date = start_date
        self.end_date: datetime.date = end_date

        # Calculated stats
        # TODO: Move these to different function?
        self.best_times: list[RunnerResult] = minimals(results, key=lambda result: result.time.timedelta)
        self.best_positions: list[RunnerResult] = minimals(results, key=lambda result: result.position.value)
        self.best_age_grades: list[RunnerResult] = maximals(results, key=lambda result: result.age_grade.value)
        self.first_result: RunnerResult | None = results[-1] if len(results) > 0 else None
        self.latest_result: RunnerResult | None = results[0] if len(results) > 0 else None

        self.total_run_time: Time = Time.from_timedelta(sum(map(lambda result: result.time.timedelta, results), start=datetime.timedelta()))
        self.average_run_time: Time = Time.from_timedelta(self.total_run_time.timedelta / max(len(results), 1))
        # total_seconds: int = round(ans.total_seconds())
        # mins, secs = divmod(total_seconds, 60)
        # return f"{mins:02d}:{secs:02d}"

        self.unique_locations: set[str] = set(map(lambda result: result.location, results))
        self.num_unique_locations: int = len(self.unique_locations)

        self.tourism_percentage: float = self.num_unique_locations / max(len(results), 1)

        self.year_counter: Counter = Counter(result.date.year for result in results)
        most_common_year: tuple[list[int], int] = most_common(self.year_counter)
        self.most_runs_per_year_years: list[int] = most_common_year[0]
        self.most_runs_per_year_count: int = most_common_year[1]

        self.locations_counter: Counter = Counter(result.location for result in results)
        most_common_location: tuple[list[str], int] = most_common(self.locations_counter)
        self.most_runs_per_location_locations: list[str] = most_common_location[0]
        self.most_runs_per_location_count: int = most_common_location[1]

    @cached_property
    def consistency(self) -> float:
        """
        A float between 0 and 1 representing the percentage of weeks between the
        first and last parkruns that the parkrunner has run between start_date
        and end_date.
        NOTE: This does not consider the Christmas and New Years Day parkruns.
        """

        if len(self.results) == 0:
            return 0.0

        start_date: datetime.date = self.results[-1].date
        end_date  : datetime.date = self.results[ 0].date
        weeks: int = (end_date - start_date).days // 7 + 1

        return len(self.results) / weeks

    @cached_property
    def re_index(self) -> int:
        """
        The number of events that the runner has done more than once.
        """

        return sum(1 for _, count in self.locations_counter.most_common() if count >= 2)

    @cached_property
    def p_index(self) -> int:
        """
        The highest integer p such that the runner has done at least p events,
        at least p times each.
        """

        p_index: int = 0
        for _, location_count in self.locations_counter.most_common():
            if location_count > p_index:
                p_index += 1

        return p_index

    def format_identity(self) -> str:
        return f"{self.name} ({self.number})"

    def __repr__(self) -> str:
        return f"Runner({self.format_identity()}, {len(self.results)} results {date_description(self.start_date, self.end_date)})"
