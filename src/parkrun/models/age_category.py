"""
Models an age category used throughput Parkrun. These are strings where the
first character is either J (junior, <= 17), S (senior, <= 34), or V (veteran);
the second character is either M (male), or W (female); then there's the ages
bounding this age category separated with a dash.
"""

from enum import Enum

# class Gender(Enum):
#     MALE = "M"
#     FEMALE = "W"
#     UNKNOWN = ""

# class AgeGroup(Enum):
#     JUNIOR = "J"
#     VETERAN = "V"
#     SENIOR = "S"
#     WHEEL_CHAIR = "WC"
#     UNKNOWN = ""

MIN_AGE: int = 0
MAX_AGE: int = 100

class AgeCategory:
    def __init__(self, string: str):
        self.string: str = string

        # Try to extract age ranges, otherwise default
        try:
            splat: list[str] = string[2:].split("-")
            if len(splat) == 1:
                self.min_age: int = MIN_AGE
                self.max_age: int = int(splat[0])
            else:
                assert len(splat) == 2
                self.min_age: int = int(splat[0])
                self.max_age: int = int(splat[1])
        except:
            self.min_age: int = MIN_AGE
            self.max_age: int = MAX_AGE

        # # Lack of information
        # if string == "":
        #     self.age_group: AgeGroup = AgeGroup.UNKNOWN
        #     self.gender: Gender = Gender.UNKNOWN
        #     self.min_age: int = MIN_AGE
        #     self.max_age: int = MAX_AGE
        #     return

        # # Wheel chair users
        # if string == "WWC" or string == "MWC":
        #     self.age_group: AgeGroup = AgeGroup.WHEEL_CHAIR
        #     try:
        #         self.gender: Gender = Gender(string[0])
        #     except:
        #         self.gender: Gender = Gender.UNKNOWN
        #     self.min_age: int = MIN_AGE
        #     self.max_age: int = MAX_AGE
        #     return

        # self.age_group: AgeGroup = AgeGroup(string[0])
        # self.gender: Gender = Gender(string[1])

        # # 10s and under are unspecified
        # if string[2:] == "10":
        #     self.min_age: int = MIN_AGE
        #     self.max_age: int = 10
        #     return

        # splat: list[str] = string[2:].split("-")

        # if splat == ["", "", "", ""]:
        #     self.min_age: int = MIN_AGE
        #     self.max_age: int = MAX_AGE
        #     return

        # self.min_age: int = int(splat[0])
        # self.max_age: int = int(splat[1])

    def __str__(self) -> str:
        return self.string
