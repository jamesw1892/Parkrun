from parameterized import parameterized
import unittest
import datetime
from parkrun.api.cache import most_recent_parkrun, HR_RESULT_START, HR_RESULT_END
from parkrun.graphs.activity import _get_num_months

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

if __name__ == "__main__":
    unittest.main()
