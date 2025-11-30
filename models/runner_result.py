from __future__ import annotations
import datetime
from models.position import Position
from models.age_grade import AgeGrade
from models.time import Time
from models.pb import PB

class RunnerResult:
    def __init__(
        self,
        location: str,
        date: datetime.date,
        run_number: int,
        position: Position,
        time: Time,
        age_grade: AgeGrade,
        pb: PB,
    ):
        self.location: str = location
        self.date: datetime.date = date
        self.run_number: int = run_number
        self.position: Position = position
        self.time: Time = time
        self.age_grade: AgeGrade = age_grade
        self.pb: PB = pb
        # TODO: Create separate objects for these?
        # location could link to event data to get lat/longs

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

        return RunnerResult(
            table_row[0],
            datetime.datetime.strptime(table_row[1], "%d/%m/%Y").date(),
            int(table_row[2]),
            Position(table_row[3]),
            Time.from_string(table_row[4]),
            AgeGrade(table_row[5]),
            PB.from_string(table_row[6]),
        )

    def __repr__(self) -> str:
        return f"RunnerResult(run number {self.run_number} at {self.location} on {self.date}: position {self.position}, time {self.time}, age grade {self.age_grade}{self.pb.format(', ')})"

    def __str__(self) -> str:
        return f"{self.date} {self.location}: {self.position}, {self.time}, {self.age_grade}{self.pb.format(', ')}"

    def format_for_position(self) -> str:
        return f"{self.position} ({self.date}, {self.location})"

    def format_for_time(self) -> str:
        return f"{self.time} ({self.date}, {self.location})"

    def format_for_age_grade(self) -> str:
        return f"{self.age_grade} ({self.date}, {self.location})"
