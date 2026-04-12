from parameterized import parameterized
import unittest
import datetime
from parkrun.models.age_category import AgeCategory
from parkrun.models.runner import Runner
from parkrun.models.runner_result import RunnerResult
from parkrun.models.event import Event
from parkrun.models.position import Position
from parkrun.models.time import Time
from parkrun.models.age_grade import AgeGrade
from parkrun.models.pb import PB
from parkrun.api.cache import most_recent_parkrun, HR_RESULT_START, HR_RESULT_END
from parkrun.graphs.activity import _get_num_months
from parkrun import _my_strtobool
import os

DUMMY_EVENT: Event = Event(0, "Name", "name", 0.0, 0.0, 0, 0)
DUMMY_POSITION: Position = Position("1")
DUMMY_TIME: Time = Time("00:00", datetime.timedelta())
DUMMY_AGE_GRADE: AgeGrade = AgeGrade("50.00%")
DUMMY_PB: PB = PB(False)

class TestFloatingStreak(unittest.TestCase):
    @parameterized.expand([
        ([], (0, [])),
        ([datetime.date(2026, 4, 11)], (1, [(datetime.date(2026, 4, 11), datetime.date(2026, 4, 11))])),
        ([datetime.date(2026, 4, 11), datetime.date(2026, 4, 4)], (2, [(datetime.date(2026, 4, 4), datetime.date(2026, 4, 11))])),
        ([datetime.date(2026, 4, 11), datetime.date(2026, 3, 28)], (1, [(datetime.date(2026, 4, 11), datetime.date(2026, 4, 11)), (datetime.date(2026, 3, 28), datetime.date(2026, 3, 28))])),
        ([datetime.date(2026, 4, 11), datetime.date(2026, 3, 28), datetime.date(2026, 3, 21)], (2, [(datetime.date(2026, 3, 21), datetime.date(2026, 3, 28))])),
        ([datetime.date(2026, 4, 11), datetime.date(2026, 3, 28), datetime.date(2026, 3, 21), datetime.date(2026, 3, 7)], (2, [(datetime.date(2026, 3, 21), datetime.date(2026, 3, 28))])),
    ])
    def test_floating_streak(self, dates: list[datetime.date], expected: tuple[int, list[tuple[datetime.date, datetime.date]]]):
        runner = Runner(1, "Name", AgeCategory("SM20-24"), [RunnerResult(DUMMY_EVENT, date, 0, DUMMY_POSITION, DUMMY_TIME, DUMMY_AGE_GRADE, DUMMY_PB) for date in dates], datetime.date.min, datetime.date.max)
        self.assertEqual(runner.floating_streak, expected)

class TestMostRecentParkrun(unittest.TestCase):

    def test_today_is_saturday_before_start(self):
        reference = datetime.datetime(2025, 8, 16, HR_RESULT_START - 1, 59)  # Saturday
        result = most_recent_parkrun(reference)
        expected = datetime.datetime(2025, 8, 9, HR_RESULT_END)
        self.assertEqual(result, expected)

    def test_today_is_saturday_after_start(self):
        reference = datetime.datetime(2025, 8, 16, HR_RESULT_START)  # Saturday
        result = most_recent_parkrun(reference)
        expected = datetime.datetime(2025, 8, 16, HR_RESULT_END)
        self.assertEqual(result, expected)

    def test_today_is_saturday_before_end(self):
        reference = datetime.datetime(2025, 8, 16, HR_RESULT_END)  # Saturday
        result = most_recent_parkrun(reference)
        expected = datetime.datetime(2025, 8, 16, HR_RESULT_END)
        self.assertEqual(result, expected)

    def test_today_is_saturday_after_end(self):
        reference = datetime.datetime(2025, 8, 16, HR_RESULT_END, 1)  # Saturday
        result = most_recent_parkrun(reference)
        expected = datetime.datetime(2025, 8, 16, HR_RESULT_END)
        self.assertEqual(result, expected)

    def test_today_is_sunday(self):
        reference = datetime.datetime(2025, 8, 17)  # Sunday
        result = most_recent_parkrun(reference)
        expected = datetime.datetime(2025, 8, 16, HR_RESULT_END)
        self.assertEqual(result, expected)

    def test_today_is_monday(self):
        reference = datetime.datetime(2025, 8, 18)  # Monday
        result = most_recent_parkrun(reference)
        expected = datetime.datetime(2025, 8, 16, HR_RESULT_END)
        self.assertEqual(result, expected)

    def test_today_is_friday(self):
        reference = datetime.datetime(2025, 8, 15)  # Friday
        result = most_recent_parkrun(reference)
        expected = datetime.datetime(2025, 8, 9, HR_RESULT_END)
        self.assertEqual(result, expected)

    def test_christmas_day_before_start(self):
        reference = datetime.datetime(2025, 12, 25, HR_RESULT_START - 1, 59)
        result = most_recent_parkrun(reference)
        expected = datetime.datetime(2025, 12, 20, HR_RESULT_END) # Saturday before Christmas
        self.assertEqual(result, expected)

    def test_christmas_day_after_start(self):
        reference = datetime.datetime(2025, 12, 25, HR_RESULT_START)
        result = most_recent_parkrun(reference)
        expected = datetime.datetime(2025, 12, 25, HR_RESULT_END)
        self.assertEqual(result, expected)

    def test_christmas_day_before_end(self):
        reference = datetime.datetime(2025, 12, 25, HR_RESULT_END)
        result = most_recent_parkrun(reference)
        expected = datetime.datetime(2025, 12, 25, HR_RESULT_END)
        self.assertEqual(result, expected)

    def test_christmas_day_after_end(self):
        reference = datetime.datetime(2025, 12, 25, HR_RESULT_END, 1)
        result = most_recent_parkrun(reference)
        expected = datetime.datetime(2025, 12, 25, HR_RESULT_END)
        self.assertEqual(result, expected)

    def test_day_after_christmas_day(self):
        reference = datetime.datetime(2025, 12, 26)
        result = most_recent_parkrun(reference)
        expected = datetime.datetime(2025, 12, 25, HR_RESULT_END)
        self.assertEqual(result, expected)

    def test_sat_after_christmas_day_before_start(self):
        reference = datetime.datetime(2025, 12, 27, HR_RESULT_START - 1, 59)
        result = most_recent_parkrun(reference)
        expected = datetime.datetime(2025, 12, 25, HR_RESULT_END) # Christmas
        self.assertEqual(result, expected)

    def test_sat_after_christmas_day_after_start(self):
        reference = datetime.datetime(2025, 12, 27, HR_RESULT_START)
        result = most_recent_parkrun(reference)
        expected = datetime.datetime(2025, 12, 27, HR_RESULT_END)
        self.assertEqual(result, expected)

    def test_sat_after_christmas_day_before_end(self):
        reference = datetime.datetime(2025, 12, 27, HR_RESULT_END)
        result = most_recent_parkrun(reference)
        expected = datetime.datetime(2025, 12, 27, HR_RESULT_END)
        self.assertEqual(result, expected)

    def test_sat_after_christmas_day_after_end(self):
        reference = datetime.datetime(2025, 12, 27, HR_RESULT_END, 1)
        result = most_recent_parkrun(reference)
        expected = datetime.datetime(2025, 12, 27, HR_RESULT_END)
        self.assertEqual(result, expected)

    def test_new_years_day_before_start(self):
        reference = datetime.datetime(2026, 1, 1, HR_RESULT_START - 1, 59)
        result = most_recent_parkrun(reference)
        expected = datetime.datetime(2025, 12, 27, HR_RESULT_END) # Saturday before NY
        self.assertEqual(result, expected)

    def test_new_years_day_after_start(self):
        reference = datetime.datetime(2026, 1, 1, HR_RESULT_START)
        result = most_recent_parkrun(reference)
        expected = datetime.datetime(2026, 1, 1, HR_RESULT_END)
        self.assertEqual(result, expected)

    def test_new_years_day_before_end(self):
        reference = datetime.datetime(2026, 1, 1, HR_RESULT_END)
        result = most_recent_parkrun(reference)
        expected = datetime.datetime(2026, 1, 1, HR_RESULT_END)
        self.assertEqual(result, expected)

    def test_new_years_day_after_end(self):
        reference = datetime.datetime(2026, 1, 1, HR_RESULT_END, 1)
        result = most_recent_parkrun(reference)
        expected = datetime.datetime(2026, 1, 1, HR_RESULT_END)
        self.assertEqual(result, expected)

    def test_day_after_new_years_day(self):
        reference = datetime.datetime(2026, 1, 2)
        result = most_recent_parkrun(reference)
        expected = datetime.datetime(2026, 1, 1, HR_RESULT_END)
        self.assertEqual(result, expected)

    def test_sat_after_new_years_day_before_start(self):
        reference = datetime.datetime(2026, 1, 3, HR_RESULT_START - 1, 59)
        result = most_recent_parkrun(reference)
        expected = datetime.datetime(2026, 1, 1, HR_RESULT_END) # NY
        self.assertEqual(result, expected)

    def test_sat_after_new_years_day_after_start(self):
        reference = datetime.datetime(2026, 1, 3, HR_RESULT_START)
        result = most_recent_parkrun(reference)
        expected = datetime.datetime(2026, 1, 3, HR_RESULT_END)
        self.assertEqual(result, expected)

    def test_sat_after_new_years_day_before_end(self):
        reference = datetime.datetime(2026, 1, 3, HR_RESULT_END)
        result = most_recent_parkrun(reference)
        expected = datetime.datetime(2026, 1, 3, HR_RESULT_END)
        self.assertEqual(result, expected)

    def test_sat_after_new_years_day_after_end(self):
        reference = datetime.datetime(2026, 1, 3, HR_RESULT_END, 1)
        result = most_recent_parkrun(reference)
        expected = datetime.datetime(2026, 1, 3, HR_RESULT_END)
        self.assertEqual(result, expected)

class TestActivityGraph(unittest.TestCase):
    @parameterized.expand([
        (2025, 12, 2025, 12, 1),
        (2025, 11, 2025, 12, 2),
        (2025, 1, 2025, 12, 12),
        (2024, 1, 2025, 12, 24),
        (2024, 12, 2025, 12, 13),
        (2024, 12, 2025, 1, 2),
    ])
    def test_num_months(self, start_year: int, start_month: int, end_year: int, end_month: int, expected: int):
        self.assertEqual(_get_num_months(datetime.date(start_year, start_month, 1), datetime.date(end_year, end_month, 1)), expected)

class TestMyStrToBool(unittest.TestCase):
    ENV_VAR_NAME: str = "CACHE_FORCE_VALID"

    @parameterized.expand((
        (None, False, False),
        (None, True, True),
        ("", False, False),
        ("", True, True),
        ("invalid", False, False),
        ("invalid", True, True),
        ("y", False, True),
        ("y", True, True),
        ("yes", False, True),
        ("yes", True, True),
        ("t", False, True),
        ("t", True, True),
        ("true", False, True),
        ("true", True, True),
        ("True", False, True),
        ("True", True, True),
        ("on", False, True),
        ("on", True, True),
        ("1", False, True),
        ("1", True, True),
        ("n", False, False),
        ("n", True, False),
        ("no", False, False),
        ("no", True, False),
        ("f", False, False),
        ("f", True, False),
        ("false", False, False),
        ("false", True, False),
        ("False", False, False),
        ("False", True, False),
        ("off", False, False),
        ("off", True, False),
        ("0", False, False),
        ("0", True, False),
    ))
    def test_absent(self, value: str | None, default: bool, expected: bool):

        # Set the value in the environment
        if value is None:
            if TestMyStrToBool.ENV_VAR_NAME in os.environ:
                del os.environ[TestMyStrToBool.ENV_VAR_NAME]
        else:
            os.environ[TestMyStrToBool.ENV_VAR_NAME] = value

        self.assertEqual(_my_strtobool(TestMyStrToBool.ENV_VAR_NAME, default), expected)

if __name__ == "__main__":
    unittest.main()
