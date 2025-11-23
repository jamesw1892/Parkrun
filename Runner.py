from collections import Counter
from RunnerResult import RunnerResult

class Runner:
    def __init__(self, number: int, name: str, results: list[RunnerResult]):
        """Assume results in ascending order of date"""
        self.number: int = number
        self.name: str = name
        self.results: list[RunnerResult] = results

        # Calculated stats
        # TODO: Move these to different function?
        self.best_time: RunnerResult = min(results, key=lambda result: result.time)
        self.best_position: RunnerResult = min(results, key=lambda result: result.position)
        self.best_age_grading: RunnerResult = max(results, key=lambda result: result.age_grading)
        self.first_result: RunnerResult = results[0]
        self.latest_result: RunnerResult = results[-1]

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
        return f"Runner({self.name} ({self.number}), {len(self.results)} results)"
