from parameterized import parameterized
import unittest
import datetime
from Cache import most_recent_saturday, SAT_HR_RESULT_START, SAT_HR_RESULT_END
from ActivityGraph import _get_num_months

class TestMostRecentSaturday(unittest.TestCase):

    def test_today_is_saturday_before_start(self):
        dt = datetime.datetime(2025, 8, 16, SAT_HR_RESULT_START - 1, 59)  # Saturday
        result = most_recent_saturday(dt)
        expected = datetime.datetime(2025, 8, 9, SAT_HR_RESULT_END)
        self.assertEqual(result, expected)

    def test_today_is_saturday_after_start(self):
        dt = datetime.datetime(2025, 8, 16, SAT_HR_RESULT_START)  # Saturday
        result = most_recent_saturday(dt)
        expected = datetime.datetime(2025, 8, 16, SAT_HR_RESULT_END)
        self.assertEqual(result, expected)

    def test_today_is_saturday_before_end(self):
        dt = datetime.datetime(2025, 8, 16, SAT_HR_RESULT_END)  # Saturday
        result = most_recent_saturday(dt)
        expected = datetime.datetime(2025, 8, 16, SAT_HR_RESULT_END)
        self.assertEqual(result, expected)

    def test_today_is_saturday_after_end(self):
        dt = datetime.datetime(2025, 8, 16, SAT_HR_RESULT_END, 1)  # Saturday
        result = most_recent_saturday(dt)
        expected = datetime.datetime(2025, 8, 16, SAT_HR_RESULT_END)
        self.assertEqual(result, expected)

    def test_today_is_sunday(self):
        dt = datetime.datetime(2025, 8, 17)  # Sunday
        result = most_recent_saturday(dt)
        expected = datetime.datetime(2025, 8, 16, SAT_HR_RESULT_END)
        self.assertEqual(result, expected)

    def test_today_is_monday(self):
        dt = datetime.datetime(2025, 8, 18)  # Monday
        result = most_recent_saturday(dt)
        expected = datetime.datetime(2025, 8, 16, SAT_HR_RESULT_END)
        self.assertEqual(result, expected)

    def test_today_is_friday(self):
        dt = datetime.datetime(2025, 8, 15)  # Friday
        result = most_recent_saturday(dt)
        expected = datetime.datetime(2025, 8, 9, SAT_HR_RESULT_END)
        self.assertEqual(result, expected)

    def test_none_reference(self):
        # This test checks that the function returns a Saturday at midday
        result = most_recent_saturday()
        self.assertEqual(result.weekday(), 5)
        self.assertEqual(result.hour, SAT_HR_RESULT_END)

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

if __name__ == "__main__":
    unittest.main()
