from parkrun.models.age_grade import AgeGrade
from parkrun.models.age_category import AgeCategory
from parkrun.models.position import Position
from parkrun.models.time import Time

class EventRunnerResult:
    def __init__(
        self,
        position: Position,
        name: str,
        id_: int,
        gender: str,
        age_category: AgeCategory,
        age_grade: AgeGrade,
        club: str,
        groups: str,
        achievement: str,
        time: Time,
    ):
        self.position: Position = position
        self.name: str = name
        self.id_: int = id_
        self.gender: str = gender
        self.age_category: AgeCategory = age_category
        self.age_grade: AgeGrade = age_grade
        self.club: str = club
        self.groups: str = groups
        self.achievement: str = achievement
        self.time: Time = time

    def __str__(self) -> str:
        return f"{self.name} ({self.id_}) came {self.position}"

    __repr__ = __str__
