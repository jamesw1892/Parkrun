from parkrun.models.time import Time

class EventRunnerResult:
    def __init__(
        self,
        position: int,
        name: str,
        id_: int,
        #gender: str, # TODO
        #age_group: str, # TODO
        #time: Time, # TODO
    ):
        self.position: int = position
        self.name: str = name
        self.id_: int = id_

    def __str__(self) -> str:
        return f"{self.name} ({self.id_}) came in position {self.position}"

    __repr__ = __str__
