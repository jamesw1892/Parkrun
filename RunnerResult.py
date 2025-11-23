from __future__ import annotations
import datetime
from Position import Position
from AgeGrade import AgeGrade

class RunnerResult:
    def __init__(
        self,
        location: str,
        date: datetime.date,
        run_number: int,
        position: Position,
        time: datetime.timedelta,
        age_grade: AgeGrade,
        pb: bool,
    ):
        self.location: str = location
        self.date: datetime.date = date
        self.run_number: int = run_number
        self.position: Position = position
        self.time: datetime.timedelta = time
        self.age_grade: AgeGrade = age_grade
        self.pb: bool = pb
        # TODO: Create separate objects for these?
        # location could link to event data to get lat/longs
        # Time could also have __str__ function

    @staticmethod
    def from_table(table_row: list[str]) -> RunnerResult:
        """
        Return a new RunnerResult from a row of a table where the row has the
        following elements:

        0: Location name
        1: Date in form DD/MM/YYYY
        2: Run number (int, of the location)
        3: Position (int)
        4: Time in form [H:]MM:SS
        5: Age grade in form xx.xx%
        6: PB? Empty string or "PB" if it's the best and not the only time the
        parkrunner has run at this location
        """

        splat_time: list[str] = table_row[4].split(":")

        return RunnerResult(
            table_row[0],
            datetime.datetime.strptime(table_row[1], "%d/%M/%Y").date(),
            int(table_row[2]),
            Position(table_row[3]),
            datetime.timedelta(
                hours = 0 if len(splat_time) == 2 else int(splat_time[0]),
                minutes = int(splat_time[-2]),
                seconds = int(splat_time[-1])
            ),
            AgeGrade(table_row[5]),
            table_row[6] == "PB",
        )

    def __repr__(self) -> str:
        return f"RunnerResult(run number {self.run_number} at {self.location} on {self.date}: position {self.position}, time {self.time}, age grade {self.age_grade}, pb {self.pb})"

    def __str__(self) -> str:
        return f"{self.date} {self.location}: {self.position} {self.time} {self.age_grade}"

    def format_for_position(self) -> str:
        return f"{self.position} ({self.date}, {self.location})"

    def format_for_time(self) -> str:
        return f"{self.time} ({self.date}, {self.location})"

    def format_for_age_grade(self) -> str:
        return f"{self.age_grade} ({self.date}, {self.location})"
