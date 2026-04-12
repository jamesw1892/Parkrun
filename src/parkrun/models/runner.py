import datetime
from collections import Counter
from functools import cached_property
from parkrun.models.event import Event
from parkrun.api.cache import most_recent_parkrun, parkrun_before
from parkrun.models.age_category import AgeCategory
from parkrun.models.runner_result import RunnerResult
from parkrun.models.time import Time
from parkrun.api.utils import minimals, maximals, most_common, date_description

class Runner:
    def __init__(
        self,
        number: int,
        name: str,
        most_recent_age_category: AgeCategory,
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
        self.most_recent_age_category: AgeCategory = most_recent_age_category
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

        self.unique_locations: set[Event] = set(map(lambda result: result.location, results))
        self.num_unique_locations: int = len(self.unique_locations)

        self.tourism_percentage: float = self.num_unique_locations / max(len(results), 1)

        self.year_counter: Counter = Counter(result.date.year for result in results)
        most_common_year: tuple[list[int], int] = most_common(self.year_counter)
        self.most_runs_per_year_years: list[int] = most_common_year[0]
        self.most_runs_per_year_count: int = most_common_year[1]

        self.locations_counter: Counter = Counter(result.location for result in results)
        most_common_location: tuple[list[Event], int] = most_common(self.locations_counter)
        self.most_runs_per_location_locations: list[Event] = most_common_location[0]
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
    def streak(self) -> tuple[int, datetime.date, datetime.date]:
        """
        The number of consecutive parkruns that the runner has done, where the
        most recent parkrun to date must be the last in this streak. Therefore,
        if they did not do the most recent parkrun, this is 0. The Christmas day
        and New Years Day parkruns must also be run for the streak to continue.
        The first return is the number of parkruns in the streak, the second is
        the date of the first parkrun in the streak and the third is the date of
        the last parkrun in the streak (always the most recent parkrun). If the
        streak is 0 then the start and end date will be the most recent parkrun
        but these do not make sense when the streak is 0.
        """

        target_parkrun_date: datetime.date = most_recent_parkrun().date()
        end: datetime.date = target_parkrun_date
        _streak: int = 0
        index: int = 0

        while len(self.results) > index and self.results[index].date == target_parkrun_date:
            target_parkrun_date = parkrun_before(target_parkrun_date)
            _streak += 1
            index += 1

        start: datetime.date = self.results[index - 1].date if 0 <= index - 1 < len(self.results) else end

        return _streak, start, end

    @cached_property
    def floating_streak(self) -> tuple[int, list[tuple[datetime.date, datetime.date]]]:
        """
        The number of consecutive parkruns that the runner has done, not
        necessarily ending with the most recent parkrun to date. The first
        return is the number, the second is a list of time periods in which the
        runner has done this many consecutive parkruns.
        """

        longest_streak: int = 0
        stretches: list[tuple[datetime.date, datetime.date]] = []

        if len(self.results) == 0:
            return longest_streak, stretches

        # Go through parkruns from most recent to oldest and initialise the
        # first streak as the most recent parkrun they did
        current_streak: int = 1
        target_parkrun_date: datetime.date = parkrun_before(self.results[0].date)
        current_end: datetime.date = self.results[0].date

        for index, result in enumerate(self.results[1:], 1):

            if result.date == target_parkrun_date:
                current_streak += 1
                target_parkrun_date = parkrun_before(target_parkrun_date)
            else:

                # Save the streak starting at the previous parkrun that the
                # runner ran
                start: datetime.date = self.results[index - 1].date
                if current_streak > longest_streak:
                    longest_streak = current_streak
                    stretches = [(start, current_end)]
                elif current_streak == longest_streak:
                    stretches.append((start, current_end))

                current_streak = 1
                target_parkrun_date = parkrun_before(result.date)
                current_end = result.date

        # Save the streak starting at the last parkrun that the runner ran
        start: datetime.date = self.results[-1].date
        if current_streak > longest_streak:
            longest_streak = current_streak
            stretches = [(start, current_end)]
        elif current_streak == longest_streak:
            stretches.append((start, current_end))

        return longest_streak, stretches

    @cached_property
    def tourist_streak(self) -> tuple[int, datetime.date, datetime.date]:
        """
        The number of consecutive parkruns that the runner has done (can miss
        weeks) that have been in unique locations. The most recent parkrun that
        the runner has done is always the end of the streak so the minimum value
        is 1 if they have done any parkruns at all and 0 if they haven't done
        any. The first return is the number of parkruns in the streak, the
        second is the date of the first parkrun in the streak and the third is
        the date of the last parkrun in the streak (always the date of the most
        recent parkrun the runner did).
        """

        # One interpretation of tourist streak where you can have repeated a
        # location but as long as it's not repeated in the streak then it's ok
        #locations: set[str] = set()
        #for result in self.results:
        #    if result.location.name in locations:
        #        break
        #    else:
        #        locations.add(result.location.name)
        #return len(locations)

        # The more common interpretation where all those in the streak must be
        # the first time you've done them
        if len(self.results) == 0:
            today: datetime.date = datetime.date.today()
            return 0, today, today

        _streak: int = 0
        end: datetime.date = self.results[0].date
        for index in range(len(self.results)):
            if self.locations_counter[self.results[index].location] != 1:
                start: datetime.date = self.results[index - 1].date if index > 0 else end
                break
            _streak += 1
        else:
            start: datetime.date = self.results[-1].date
        return _streak, start, end

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
