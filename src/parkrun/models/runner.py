import datetime
from collections import Counter
from parkrun.models.runner_result import RunnerResult
from parkrun.models.time import Time

class Runner:
    def __init__(self, number: int, name: str, most_recent_age_category: str, results: list[RunnerResult]):
        """Assume results in descending order of date"""
        self.number: int = number
        self.name: str = name
        self.most_recent_age_category: str = most_recent_age_category
        self.results: list[RunnerResult] = results

        # Calculated stats
        # TODO: Move these to different function?
        self.best_time: RunnerResult = min(results, key=lambda result: result.time.timedelta)
        self.best_position: RunnerResult = min(results, key=lambda result: result.position.value)
        self.best_age_grade: RunnerResult = max(results, key=lambda result: result.age_grade.value)
        self.first_result: RunnerResult = results[-1]
        self.latest_result: RunnerResult = results[0]

        self.total_run_time: Time = Time.from_timedelta(sum(map(lambda result: result.time.timedelta, results), start=datetime.timedelta()))
        self.average_run_time: Time = Time.from_timedelta(self.total_run_time.timedelta / len(results))
        # total_seconds: int = round(ans.total_seconds())
        # mins, secs = divmod(total_seconds, 60)
        # return f"{mins:02d}:{secs:02d}"

        self.unique_locations: set[str] = set(map(lambda result: result.location, results))
        self.num_unique_locations: int = len(self.unique_locations)

        self.tourism_percentage: float = self.num_unique_locations / len(results)
        self.__consistency = None

        self.year_counter: Counter = Counter(result.date.year for result in results)
        most_common_year = self.year_counter.most_common(1)[0]
        self.most_runs_per_year_year: int = most_common_year[0]
        self.most_runs_per_year_count: int = most_common_year[1]

        self.locations_counter: Counter = Counter(result.location for result in results)
        most_common_location: tuple[str, int] = self.locations_counter.most_common(1)[0]
        self.most_runs_per_location_location: str = most_common_location[0]
        self.most_runs_per_location_count: int = most_common_location[1]

    @property
    def consistency(self) -> float:
        """
        A float between 0 and 1 representing the percentage of weeks between the
        first and last parkruns that the parkrunner has run.
        NOTE: This does not consider the Christmas and New Years Day parkruns.
        """

        if self.__consistency is None:

            start_date: datetime.date = self.results[-1].date
            end_date  : datetime.date = self.results[0].date
            weeks: int = (end_date - start_date).days // 7 + 1

            self.__consistency: float = len(self.results) / weeks

        return self.__consistency

    def format_identity(self) -> str:
        return f"{self.name} ({self.number})"

    def __repr__(self) -> str:
        return f"Runner({self.format_identity()}, {len(self.results)} results)"
