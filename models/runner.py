import datetime
from collections import Counter
from models.runner_result import RunnerResult
from models.time import Time

class Runner:
    def __init__(self, number: int, name: str, age_category: str, results: list[RunnerResult]):
        """Assume results in descending order of date"""
        self.number: int = number
        self.name: str = name
        self.age_category: str = age_category
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

        res = Counter(map(lambda result: result.date.year, results)).most_common(1)[0]
        self.most_runs_per_year_year: int = res[0]
        self.most_runs_per_year_count: int = res[1]

        res = Counter(map(lambda result: result.location, results)).most_common(1)[0]
        self.most_runs_per_location_location: str = res[0]
        self.most_runs_per_location_count: int = res[1]

    def __repr__(self) -> str:
        return f"Runner({self.name} ({self.number}, {self.age_category}), {len(self.results)} results)"
