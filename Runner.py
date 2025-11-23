from RunnerResult import RunnerResult

class Runner:
    def __init__(self, number: int, name: str, results: list[RunnerResult]):
        self.number: int = number
        self.name: str = name
        self.results: list[RunnerResult] = results

    def __repr__(self) -> str:
        return f"Runner({self.name} ({self.number}), {len(self.results)} results)"
