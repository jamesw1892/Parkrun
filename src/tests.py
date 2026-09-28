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
from parkrun.models.country import Country
from parkrun.models.country_collection import CountryCollection
from parkrun.models.pb import PB
from parkrun.api.cache import max_parkruns_in_year, most_recent_parkrun, HR_RESULT_START, HR_RESULT_END
from parkrun.graphs.activity import _get_num_months
from parkrun.maps.voronoi import voronoi_cells, voronoi_layer
from parkrun import _env_strtobool, projected_age_range
from parkrun.tables.achievements.periodic_table import ELEMENTS, normalise, can_spell, elements_by_rarity, best_assignment, periodic_table_achieved
import os
import random
from unittest.mock import patch
from matplotlib.path import Path
import numpy as np
from typing import Any

DUMMY_COUNTRY: Country = Country(0, "url", [0, 0, 0, 0])
DUMMY_EVENT: Event = Event(0, "Name", "name", 0.0, 0.0, DUMMY_COUNTRY, 0)
DUMMY_POSITION: Position = Position("1")
DUMMY_TIME: Time = Time("00:00", datetime.timedelta())
DUMMY_AGE_GRADE: AgeGrade = AgeGrade("50.00%")
DUMMY_PB: PB = PB(False)
DUMMY_AGE_CATEGORY: AgeCategory = AgeCategory("SM20-24")

class TestStreaks(unittest.TestCase):
    @parameterized.expand([
        ([], (0, [])),
        ([datetime.date(2026, 4, 11)], (1, [(datetime.date(2026, 4, 11), datetime.date(2026, 4, 11))])),
        ([datetime.date(2026, 4, 11), datetime.date(2026, 4, 4)], (2, [(datetime.date(2026, 4, 4), datetime.date(2026, 4, 11))])),
        ([datetime.date(2026, 4, 11), datetime.date(2026, 3, 28)], (1, [(datetime.date(2026, 4, 11), datetime.date(2026, 4, 11)), (datetime.date(2026, 3, 28), datetime.date(2026, 3, 28))])),
        ([datetime.date(2026, 4, 11), datetime.date(2026, 3, 28), datetime.date(2026, 3, 21)], (2, [(datetime.date(2026, 3, 21), datetime.date(2026, 3, 28))])),
        ([datetime.date(2026, 4, 11), datetime.date(2026, 3, 28), datetime.date(2026, 3, 21), datetime.date(2026, 3, 7)], (2, [(datetime.date(2026, 3, 21), datetime.date(2026, 3, 28))])),
    ])
    def test_floating_streak(self, dates: list[datetime.date], expected: tuple[int, list[tuple[datetime.date, datetime.date]]]):
        runner = Runner(1, "Name", DUMMY_AGE_CATEGORY, [RunnerResult(DUMMY_EVENT, date, 0, DUMMY_POSITION, DUMMY_TIME, DUMMY_AGE_GRADE, DUMMY_PB) for date in dates], datetime.date.min, datetime.date.max)
        self.assertEqual(runner.floating_streak, expected)

    @parameterized.expand([
        ([], (0, [])),
        ([(1, datetime.date(2026, 4, 11))], (1, [(datetime.date(2026, 4, 11), datetime.date(2026, 4, 11))])),
        ([(1, datetime.date(2026, 4, 11)), (2, datetime.date(2026, 4, 4))], (2, [(datetime.date(2026, 4, 4), datetime.date(2026, 4, 11))])),
        ([(1, datetime.date(2026, 4, 11)), (2, datetime.date(2026, 3, 28))], (2, [(datetime.date(2026, 3, 28), datetime.date(2026, 4, 11))])),
        ([(1, datetime.date(2026, 4, 11)), (1, datetime.date(2026, 3, 28))], (1, [(datetime.date(2026, 4, 11), datetime.date(2026, 4, 11)), (datetime.date(2026, 3, 28), datetime.date(2026, 3, 28))])),
        ([(1, datetime.date(2026, 4, 11)), (2, datetime.date(2026, 4, 4)), (1, datetime.date(2026, 3, 28)), (3, datetime.date(2026, 3, 21))], (3, [(datetime.date(2026, 3, 21), datetime.date(2026, 4, 4))])),
        ([(1, datetime.date(2026, 4, 11)), (2, datetime.date(2026, 4, 4)), (1, datetime.date(2026, 3, 28)), (2, datetime.date(2026, 3, 21))], (2, [(datetime.date(2026, 4, 4), datetime.date(2026, 4, 11)), (datetime.date(2026, 3, 28), datetime.date(2026, 4, 4)), (datetime.date(2026, 3, 21), datetime.date(2026, 3, 28))])),
    ])
    def test_floating_tourist_streak2(self, results: list[tuple[int, datetime.date]], expected: tuple[int, list[tuple[datetime.date, datetime.date]]]):
        runner = Runner(1, "Name", DUMMY_AGE_CATEGORY, [RunnerResult(Event(loc_id, "Name", "name", 0.0, 0.0, DUMMY_COUNTRY, 0), date, 0, DUMMY_POSITION, DUMMY_TIME, DUMMY_AGE_GRADE, DUMMY_PB) for loc_id, date in results], datetime.date.min, datetime.date.max)
        self.assertEqual(runner.floating_tourist_streak2, expected)

    @parameterized.expand([
        ([], (0, [])),
        ([(1, datetime.date(2026, 4, 11))], (1, [(datetime.date(2026, 4, 11), datetime.date(2026, 4, 11))])),
        ([(1, datetime.date(2026, 4, 11)), (2, datetime.date(2026, 4, 4))], (2, [(datetime.date(2026, 4, 4), datetime.date(2026, 4, 11))])),
        ([(1, datetime.date(2026, 4, 11)), (2, datetime.date(2026, 3, 28))], (2, [(datetime.date(2026, 3, 28), datetime.date(2026, 4, 11))])),
        ([(1, datetime.date(2026, 4, 11)), (1, datetime.date(2026, 3, 28))], (1, [(datetime.date(2026, 3, 28), datetime.date(2026, 3, 28))])),
        ([(1, datetime.date(2026, 4, 11)), (2, datetime.date(2026, 4, 4)), (1, datetime.date(2026, 3, 28))], (2, [(datetime.date(2026, 3, 28), datetime.date(2026, 4, 4))])),
        ([(4, datetime.date(2026, 4, 18)), (3, datetime.date(2026, 4, 4)), (1, datetime.date(2026, 3, 28)), (2, datetime.date(2026, 3, 21)), (1, datetime.date(2026, 3, 14))], (2, [(datetime.date(2026, 3, 14), datetime.date(2026, 3, 21)), (datetime.date(2026, 4, 4), datetime.date(2026, 4, 18))])),
        ([(4, datetime.date(2026, 4, 25)), (3, datetime.date(2026, 4, 18)), (1, datetime.date(2026, 4, 11)), (5, datetime.date(2026, 4, 4)), (1, datetime.date(2026, 3, 28)), (2, datetime.date(2026, 3, 21)), (1, datetime.date(2026, 3, 14))], (2, [(datetime.date(2026, 3, 14), datetime.date(2026, 3, 21)), (datetime.date(2026, 4, 18), datetime.date(2026, 4, 25))])),
    ])
    def test_floating_tourist_streak(self, results: list[tuple[int, datetime.date]], expected: tuple[int, list[tuple[datetime.date, datetime.date]]]):
        runner = Runner(1, "Name", DUMMY_AGE_CATEGORY, [RunnerResult(Event(loc_id, "Name", "name", 0.0, 0.0, DUMMY_COUNTRY, 0), date, 0, DUMMY_POSITION, DUMMY_TIME, DUMMY_AGE_GRADE, DUMMY_PB) for loc_id, date in results], datetime.date.min, datetime.date.max)
        self.assertEqual(runner.floating_tourist_streak, expected)

class TestPcIndex(unittest.TestCase):
    @parameterized.expand([
        ("no_results", [], 0),
        ("one_run", [(1, 1)], 1),
        ("one_country_only", [(1, 1), (1, 1), (2, 1), (2, 1)], 1),
        ("two_countries_once_each", [(1, 1), (2, 2)], 1),
        ("two_countries_two_events_twice", [(1, 1), (1, 1), (2, 1), (2, 1), (3, 2), (3, 2), (4, 2), (4, 2)], 2),
        ("two_countries_one_short", [(1, 1), (1, 1), (2, 1), (2, 1), (3, 2), (3, 2), (4, 2)], 1),
        ("three_countries_limited_by_count", [(1, 1), (1, 1), (2, 1), (2, 1), (3, 2), (3, 2), (4, 2), (4, 2), (5, 3), (5, 3), (5, 3)], 2),
        ("discontinued_ignored", [(1, 1), (1, 1), (2, 1), (2, 1), (3, 0), (3, 0), (4, 0), (4, 0)], 1),
    ])
    def test_pc_index(self, _name: str, results: list[tuple[int, int]], expected: int):
        countries: dict[int, Country] = {country_id: Country(country_id, "url", [0, 0, 0, 0]) for _, country_id in results}
        runner = Runner(1, "Name", DUMMY_AGE_CATEGORY, [RunnerResult(Event(loc_id, "Name", "name", 0.0, 0.0, countries[country_id], 0), datetime.date(2026, 4, 11), 0, DUMMY_POSITION, DUMMY_TIME, DUMMY_AGE_GRADE, DUMMY_PB) for loc_id, country_id in results], datetime.date.min, datetime.date.max)
        self.assertEqual(runner.pc_index, expected)

class TestCIndex(unittest.TestCase):
    @parameterized.expand([
        ("no_results", [], 0),
        ("one_run", [(1, 1)], 1),
        ("one_country_only", [(1, 1), (2, 1), (3, 1)], 1),
        ("two_countries_two_events", [(1, 1), (2, 1), (3, 2), (4, 2)], 2),
        ("repeats_dont_count", [(1, 1), (1, 1), (2, 1), (3, 2), (3, 2)], 1),
        ("three_countries_limited_by_count", [(1, 1), (2, 1), (3, 2), (4, 2), (5, 3), (6, 3), (7, 3)], 2),
        ("three_countries_three_events", [(1, 1), (2, 1), (3, 1), (4, 2), (5, 2), (6, 2), (7, 3), (8, 3), (9, 3)], 3),
        ("discontinued_ignored", [(1, 1), (2, 1), (3, 0), (4, 0)], 1),
    ])
    def test_c_index(self, _name: str, results: list[tuple[int, int]], expected: int):
        countries: dict[int, Country] = {country_id: Country(country_id, "url", [0, 0, 0, 0]) for _, country_id in results}
        runner = Runner(1, "Name", DUMMY_AGE_CATEGORY, [RunnerResult(Event(loc_id, "Name", "name", 0.0, 0.0, countries[country_id], 0), datetime.date(2026, 4, 11), 0, DUMMY_POSITION, DUMMY_TIME, DUMMY_AGE_GRADE, DUMMY_PB) for loc_id, country_id in results], datetime.date.min, datetime.date.max)
        self.assertEqual(runner.c_index, expected)

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

class TestMaxParkrunsInYear(unittest.TestCase):
    @parameterized.expand([
        (2016, 55, "53 Saturdays and both special dates on weekdays"),
        (2021, 53, "52 Saturdays and Christmas Day on Saturday"),
        (2022, 54, "53 Saturdays and New Year's Day on Saturday"),
        (2023, 54, "52 Saturdays and both special dates on weekdays"),
        (2024, 54, "Leap year with 52 Saturdays and both special dates on weekdays"),
    ])
    def test_max_parkruns_in_year(self, year: int, expected: int, description: str):
        got: int = max_parkruns_in_year(year)
        self.assertEqual(got, expected, f"{description}: expected {expected} but got {got}")

    @parameterized.expand([
        (datetime.date(2026, 1, 1), 1, "New Year's Day only"),
        (datetime.date(2026, 9, 20), 39, "Through 20 September"),
        (datetime.date(2026, 12, 24), 52, "Before Christmas Day"),
        (datetime.date(2026, 12, 25), 53, "Including Christmas Day"),
    ])
    def test_max_parkruns_in_year_to_date(self, end_date: datetime.date, expected: int, description: str):
        got: int = max_parkruns_in_year(end_date.year, end_date=end_date)
        self.assertEqual(got, expected, f"{description}: expected {expected} but got {got}")

    @parameterized.expand([
        (datetime.date(2025, 1, 1), 0, "Before the requested year"),
        (datetime.date(2028, 1, 1), 54, "After the requested year"),
    ])
    def test_end_date_outside_requested_year(self, end_date: datetime.date, expected: int, description: str):
        got: int = max_parkruns_in_year(2026, end_date=end_date)
        self.assertEqual(got, expected, f"{description}: expected {expected} but got {got}")

    @parameterized.expand([
        (datetime.date(2026, 1, 1), 54, "From New Year's Day"),
        (datetime.date(2026, 1, 2), 53, "After New Year's Day, from Friday"),
        (datetime.date(2026, 1, 3), 53, "From first Saturday"),
        (datetime.date(2026, 1, 4), 52, "After first Saturday"),
        (datetime.date(2026, 12, 25), 2, "From Christmas Day"),
        (datetime.date(2026, 12, 26), 1, "From last Saturday"),
        (datetime.date(2026, 12, 27), 0, "After last Saturday"),
    ])
    def test_max_parkruns_in_year_from_date(self, start_date: datetime.date, expected: int, description: str):
        got: int = max_parkruns_in_year(start_date.year, start_date=start_date)
        self.assertEqual(got, expected, f"{description}: expected {expected} but got {got}")

    @parameterized.expand([
        (datetime.date(2026, 3, 1), datetime.date(2026, 3, 31), 4, "March"),
        (datetime.date(2026, 3, 7), datetime.date(2026, 3, 7), 1, "Single Saturday"),
        (datetime.date(2026, 3, 8), datetime.date(2026, 3, 13), 0, "Sunday to Friday"),
        (datetime.date(2026, 12, 20), datetime.date(2026, 12, 31), 2, "Christmas Day and the Saturday after"),
        (datetime.date(2025, 6, 1), datetime.date(2027, 6, 1), 54, "Period spanning the whole year"),
        (datetime.date(2026, 6, 1), datetime.date(2026, 5, 1), 0, "Start after end"),
        (datetime.date(2027, 1, 1), None, 0, "Start after the requested year"),
    ])
    def test_max_parkruns_in_year_between_dates(self, start_date: datetime.date, end_date: datetime.date | None, expected: int, description: str):
        got: int = max_parkruns_in_year(2026, start_date, end_date)
        self.assertEqual(got, expected, f"{description}: expected {expected} but got {got}")

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

        self.assertEqual(_env_strtobool(TestMyStrToBool.ENV_VAR_NAME, default), expected)


class TestProjectedAgeRange(unittest.TestCase):
    @parameterized.expand([
        (25, 29, datetime.date(2026, 9, 19), datetime.date(2026, 9, 19), 25, 29, "Same day"),
        (25, 29, datetime.date(2026, 9, 19), datetime.date(2026, 9, 20), 25, 30, "Day after"),
        (25, 29, datetime.date(2026, 9, 19), datetime.date(2027, 9, 18), 25, 30, "A year minus a day after"),
        (25, 29, datetime.date(2026, 9, 19), datetime.date(2027, 9, 19), 26, 30, "A year after"),
        (25, 29, datetime.date(2026, 9, 19), datetime.date(2027, 9, 20), 26, 31, "A year and a day after"),
        (25, 29, datetime.date(2026, 9, 19), datetime.date(2028, 9, 18), 26, 31, "Two years minus a day after leap year"),
        (25, 29, datetime.date(2026, 9, 19), datetime.date(2028, 9, 19), 27, 31, "Two years after leap year"),
        (25, 29, datetime.date(2026, 9, 19), datetime.date(2028, 9, 20), 27, 32, "Two years and a day after leap year"),
        (25, 29, datetime.date(2028, 9, 19), datetime.date(2028, 9, 19), 25, 29, "Same day leap year"),
        (25, 29, datetime.date(2028, 9, 19), datetime.date(2028, 9, 20), 25, 30, "Day after leap year"),
        (25, 29, datetime.date(2028, 9, 19), datetime.date(2029, 9, 18), 25, 30, "A year minus a day after leap year"),
        (25, 29, datetime.date(2028, 9, 19), datetime.date(2029, 9, 19), 26, 30, "A year after leap year"),
        (25, 29, datetime.date(2028, 9, 19), datetime.date(2029, 9, 20), 26, 31, "A year and a day after leap year"),
        (25, 29, datetime.date(2028, 9, 19), datetime.date(2030, 9, 18), 26, 31, "Two years minus a day after"),
        (25, 29, datetime.date(2028, 9, 19), datetime.date(2030, 9, 19), 27, 31, "Two years after"),
        (25, 29, datetime.date(2028, 9, 19), datetime.date(2030, 9, 20), 27, 32, "Two years and a day after"),
    ])
    def test_projected_age_range(
        self,
        start_min_age: int,
        start_max_age: int,
        date_of_age_category: datetime.date,
        today: datetime.date,
        expected_min_age: int,
        expected_max_age: int,
        description: str,
    ):
        got_min_age, got_max_age = projected_age_range(
            start_min_age,
            start_max_age,
            date_of_age_category,
            today,
        )
        self.assertEqual(got_min_age, expected_min_age, f"Min age: {description}: expected {expected_min_age} but got {got_min_age}")
        self.assertEqual(got_max_age, expected_max_age, f"Max age: {description}: expected {expected_max_age} but got {got_max_age}")

class TestPeriodicTable(unittest.TestCase):
    @parameterized.expand([
        ("Name", "name"),
        ("  Spaced Name ", "spaced name"),
        ("Émile Ölström", "emile olstrom"),
    ])
    def test_normalise(self, name: str, expected: str):
        self.assertEqual(normalise(name), expected)

    @parameterized.expand([
        ("H", "Hilltop", True),
        ("H", "Oakhill", False),
        ("He", "Hollowe", True),
        ("He", "Eastholm", False),
        ("He", "H", False),
        ("Cl", "Clay Fields", True),
        ("Cl", "Coldwater", True),
        ("Cl", "Crossways", False),
        ("Er", "Érmitage", True),
        ("Ni", "  nIGHTFIELD", True),
        ("Er", "Emmet", False),
        ("Xe", "Oxenmoor", True),
        ("Xe", "Exmoor", True),
        ("Xe", "Oxmoor", False),
    ])
    def test_can_spell(self, element: str, location_name: str, expected: bool):
        self.assertEqual(can_spell(element, location_name), expected)

    @parameterized.expand([
        ("empty", [], [], {}),
        ("no elements", [], ["Hill"], {}),
        ("no locations", ["H"], [], {}),
        ("cannot spell", ["O"], ["Park"], {}),
        ("earlier element preferred", ["He", "H"], ["Heath"], {"He": "Heath"}),
        ("earlier location preferred", ["H"], ["Hill", "Hall"], {"H": "Hill"}),
        ("free element taken", ["H", "He"], ["Hill", "Heath"], {"H": "Hill", "He": "Heath"}),
        ("location moved", ["H", "He"], ["Heath", "Hill"], {"He": "Heath", "H": "Hill"}),
        ("chain of moves", ["B", "Be", "Br"], ["Bere", "Bee", "Bay"], {"Br": "Bere", "Be": "Bee", "B": "Bay"}),
        ("unassignable left out", ["H", "He"], ["Heath", "Hill", "Hall"], {"He": "Heath", "H": "Hill"}),
    ])
    def test_best_assignment(self, _description: str, elements: list[str], location_names: list[str], expected: dict[str, str]):
        self.assertEqual(best_assignment(elements, location_names), expected)

    @staticmethod
    def _max_assignment_size(elements: list[str], location_names: list[str]) -> int:
        """
        Brute force the size of the largest possible assignment.
        """

        def search(index: int, used: frozenset[str]) -> int:
            if index == len(location_names):
                return 0
            best = search(index + 1, used)
            for element in elements:
                if element not in used and can_spell(element, location_names[index]):
                    best = max(best, 1 + search(index + 1, used | {element}))
            return best

        return search(0, frozenset())

    def test_best_assignment_random(self):
        rng = random.Random(0)
        elements = ["A", "Ab", "Ac", "B", "Ba", "Bc", "C", "Ca", "Cb"]
        for _ in range(200):
            location_names = list(dict.fromkeys("".join(rng.choice("abc") for _ in range(rng.randint(1, 4))).capitalize() for _ in range(rng.randint(0, 7))))
            assignment = best_assignment(elements, location_names)

            # Valid: each location used at most once and can spell its element
            self.assertEqual(len(set(assignment.values())), len(assignment))
            for element, location_name in assignment.items():
                self.assertTrue(can_spell(element, location_name))

            # Optimal
            self.assertEqual(len(assignment), self._max_assignment_size(elements, location_names), f"{location_names}: {assignment}")

            # Stable: adding a location never unassigns an existing one
            for i in range(len(location_names)):
                before = set(best_assignment(elements, location_names[:i]).values())
                after = set(best_assignment(elements, location_names[:i + 1]).values())
                self.assertLessEqual(before, after, f"{location_names[:i + 1]}")

    def test_elements_by_rarity(self):
        events = [
            Event(1, "Hope", "hope", 0.0, 0.0, DUMMY_COUNTRY, 1),
            Event(2, "Hill", "hill", 0.0, 0.0, DUMMY_COUNTRY, 1),
            Event(3, "Hexley Juniors", "hexley-juniors", 0.0, 0.0, DUMMY_COUNTRY, 2),
        ]
        elements_by_rarity.cache_clear()
        try:
            with patch("parkrun.tables.achievements.periodic_table.fetch_events", return_value=events):
                result = elements_by_rarity()
        finally:
            elements_by_rarity.cache_clear()

        # Junior events are ignored and ties keep the order of ELEMENTS
        self.assertEqual(result, [element for element in ELEMENTS if element not in {"H", "He", "Ho"}] + ["He", "Ho", "H"])

    def test_periodic_table_achieved(self):
        heath = Event(1, "Heath", "heath", 0.0, 0.0, DUMMY_COUNTRY, 1)
        hill = Event(2, "Hill", "hill", 0.0, 0.0, DUMMY_COUNTRY, 1)
        park = Event(3, "Park", "park", 0.0, 0.0, DUMMY_COUNTRY, 1)
        # Most recent first
        results = [
            RunnerResult(park, datetime.date(2026, 4, 25), 4, DUMMY_POSITION, DUMMY_TIME, DUMMY_AGE_GRADE, DUMMY_PB),
            RunnerResult(hill, datetime.date(2026, 4, 18), 3, DUMMY_POSITION, DUMMY_TIME, DUMMY_AGE_GRADE, DUMMY_PB),
            RunnerResult(heath, datetime.date(2026, 4, 11), 2, DUMMY_POSITION, DUMMY_TIME, DUMMY_AGE_GRADE, DUMMY_PB),
            RunnerResult(heath, datetime.date(2026, 4, 4), 1, DUMMY_POSITION, DUMMY_TIME, DUMMY_AGE_GRADE, DUMMY_PB),
        ]
        runner = Runner(1, "Name", DUMMY_AGE_CATEGORY, results, datetime.date.min, datetime.date.max)

        # Heath is visited first so takes H, then moves to He so Hill can have
        # H. Each element maps to the first result at its location.
        with patch("parkrun.tables.achievements.periodic_table.elements_by_rarity", return_value=["H", "He"]):
            self.assertEqual(periodic_table_achieved(runner), {"He": results[3], "H": results[1]})

    def test_periodic_table_achieved_no_results(self):
        runner = Runner(1, "Name", DUMMY_AGE_CATEGORY, [], datetime.date.min, datetime.date.max)
        with patch("parkrun.tables.achievements.periodic_table.elements_by_rarity", return_value=["H", "He"]):
            self.assertEqual(periodic_table_achieved(runner), {})

class TestEvent(unittest.TestCase):
    COUNTRIES: CountryCollection = CountryCollection({"countries": {
        "0": {"url": None, "bounds": [0, 0, 0, 0]},
        "97": {"url": "www.example.com", "bounds": [0, 0, 0, 0]},
    }})

    @staticmethod
    def make_event_dict(countrycode: int) -> dict[str, Any]:
        # GeoJSON feature in the format of events.json
        return {
            "id": 7,
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-1.25, 52.5]},
            "properties": {
                "eventname": "fakepark",
                "EventShortName": "Fake Park",
                "countrycode": countrycode,
                "seriesid": 1,
            },
        }

    def test_from_dict(self):
        event = Event.from_dict(self.make_event_dict(97), self.COUNTRIES)
        self.assertEqual(event.id_, 7)
        self.assertEqual(event.name, "Fake Park")
        self.assertEqual(event.url_name, "fakepark")
        self.assertEqual(event.country.id_, 97)
        self.assertTrue(event.is_adult())

    def test_from_dict_coordinates_are_long_lat(self):
        # GeoJSON coordinates are [longitude, latitude]
        event = Event.from_dict(self.make_event_dict(97), self.COUNTRIES)
        self.assertEqual(event.lat, 52.5)
        self.assertEqual(event.long, -1.25)

    def test_from_dict_unknown_country(self):
        event = Event.from_dict(self.make_event_dict(12345), self.COUNTRIES)
        self.assertEqual(event.country.id_, 0)

class TestVoronoi(unittest.TestCase):
    @staticmethod
    def unit_vectors(lat_long: np.ndarray) -> np.ndarray:
        lat_long = np.radians(lat_long)
        return np.column_stack([
            np.cos(lat_long[:, 0]) * np.cos(lat_long[:, 1]),
            np.cos(lat_long[:, 0]) * np.sin(lat_long[:, 1]),
            np.sin(lat_long[:, 0]),
        ])

    @parameterized.expand([
        ("few_southern", 5, -45, -10),
        ("few_anywhere", 6, -80, 80),
        ("near_poles", 5, -89, 89),
        ("near_equator", 10, -10, 10),
        ("northern", 40, 20, 60),
        ("many", 100, -60, 70),
    ])
    def test_each_point_in_nearest_locations_cell(self, _, num_locations: int, min_lat: float, max_lat: float):
        rng = np.random.default_rng(0)
        locations = np.column_stack([
            rng.uniform(min_lat, max_lat, num_locations),
            rng.uniform(-180, 180, num_locations),
        ])
        cells = voronoi_cells([(lat, long) for lat, long in locations])
        paths = [[Path(np.array(ring)) for ring in rings] for rings in cells]

        # Random points spread evenly over the sphere, avoiding the very edges
        # of the map
        num_points = 500
        points = np.column_stack([
            np.degrees(np.arcsin(rng.uniform(-0.995, 0.995, num_points))),
            rng.uniform(-179.99, 179.99, num_points),
        ])
        similarities = self.unit_vectors(points) @ self.unit_vectors(locations).T
        for (lat, long), similarity in zip(points, similarities):
            nearest, second_nearest = np.argsort(similarity)[::-1][:2]
            # Cell edges are approximated by short straight lines, so skip
            # points almost equally close to two locations
            if similarity[nearest] - similarity[second_nearest] < 1e-5:
                continue
            containing = [i for i, cell in enumerate(paths) if any(path.contains_point((long, lat)) for path in cell)]
            self.assertEqual(containing, [nearest], f"({lat}, {long})")

    @parameterized.expand([
        ("north", 90),
        ("south", -90),
    ])
    def test_pole_cell_one_ring_across_map(self, _, pole: float):
        rng = np.random.default_rng(0)
        locations = np.column_stack([rng.uniform(-60, 60, 20), rng.uniform(-180, 180, 20)])
        cells = voronoi_cells([(lat, long) for lat, long in locations])
        pole_index = int(np.argmax(np.sign(pole) * locations[:, 0]))
        rings = cells[pole_index]
        # Otherwise the outlines where copies meet would be drawn down from
        # the pole, splitting the cell in two
        self.assertEqual(len(rings), 1)
        # Its sides going down from the pole are at the edges of the map or
        # beyond
        longs_at_pole = [long for long, lat in rings[0] if lat == pole]
        self.assertLessEqual(min(longs_at_pole), -180)
        self.assertGreaterEqual(max(longs_at_pole), 180)

    def test_layer_shares_cell_between_events_at_same_location(self):
        events = [
            Event(i, f"Name{i}", f"name{i}", lat, long, DUMMY_COUNTRY, 1)
            for i, (lat, long) in enumerate([(0, 0), (0, 0), (50, 10), (-30, 100), (10, -120)])
        ]
        layer = voronoi_layer(events, lambda event: str(event.id_))
        self.assertEqual([feature["properties"]["colour"] for feature in layer.data["features"]], ["0", "2", "3", "4"])

    def test_layer_empty_with_too_few_locations(self):
        events = [Event(i, f"Name{i}", f"name{i}", i, i, DUMMY_COUNTRY, 1) for i in range(3)]
        with self.assertLogs("parkrun.maps.voronoi", "WARNING"):
            layer = voronoi_layer(events, lambda event: "red")
        self.assertEqual(layer.data["features"], [])

if __name__ == "__main__":
    unittest.main()
