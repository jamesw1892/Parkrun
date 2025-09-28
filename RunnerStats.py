"""
Calculate statistics about the given runner.

Functions are written for each statistic producing atomic results where
possible. Each function takes the results table with type list[list[str]] and
outputs the statistic of whatever type.
"""

from typing import Any
from Scraper import fetch_runner_results
from collections.abc import Callable
import datetime
from collections import Counter
import os
from dotenv import load_dotenv

load_dotenv()

################################################################################
# Helper functions
################################################################################

def calc_pb(results: list[list[str]]) -> list[str]:
    """
    Given a list of results of the form output by `Scraper.fetch_runner_results`
    return the one result of the same form with the fastest time.
    """
    return min(results, key=result_to_timedelta)

def calc_best_age_grade(results: list[list[str]]) -> list[str]:
    """
    Given a list of results of the form output by `Scraper.fetch_runner_results`
    return the one result of the same form with the best age grade.
    """
    return max(results, key=lambda result: float(result[5][:-1]))

def calc_best_finish_position(results: list[list[str]]) -> list[str]:
    """
    Given a list of results of the form output by `Scraper.fetch_runner_results`
    return the one result of the same form with the best finish position.
    """
    return min(results, key=lambda result: int(result[3]))

def result_to_timedelta(result: list[str]) -> datetime.timedelta:
    """
    Given a single result, return a timedelta object representing the run time
    """
    splat_time: list[str] = result[4].split(":")
    hours: int = 0 if len(splat_time) == 2 else int(splat_time[0])
    return datetime.timedelta(hours=hours, minutes=int(splat_time[-2]), seconds=int(splat_time[-1]))

################################################################################
# Statistic functions
################################################################################

def num_runs(results: list[list[str]]) -> int:
    return len(results)

def total_kms_run(results: list[list[str]]) -> int:
    return len(results) * 5

def total_run_time(results: list[list[str]]) -> datetime.timedelta:
    return sum(map(result_to_timedelta, results), start=datetime.timedelta())

def average_run_time(results: list[list[str]]) -> str:
    """String in the form MM:SS"""

    ans: datetime.timedelta = total_run_time(results) / len(results)
    total_seconds: int = round(ans.total_seconds())
    mins, secs = divmod(total_seconds, 60)
    return f"{mins}:{secs}"

def first_run_location(results: list[list[str]]) -> str:
    return results[-1][0]

def first_run_date(results: list[list[str]]) -> str:
    """String in the form DD/MM/YYY"""
    return results[-1][1]

def first_run_position(results: list[list[str]]) -> int:
    return int(results[-1][3])

def first_run_time(results: list[list[str]]) -> str:
    """String in the form [H:]MM:SS"""
    return results[-1][4]

def first_run_age_grade(results: list[list[str]]) -> str:
    """String in the form xx.xx%"""
    return results[-1][5]

def last_run_location(results: list[list[str]]) -> str:
    return results[0][0]

def last_run_date(results: list[list[str]]) -> str:
    """String in the form DD/MM/YYY"""
    return results[0][1]

def last_run_position(results: list[list[str]]) -> int:
    return int(results[0][3])

def last_run_time(results: list[list[str]]) -> str:
    """String in the form [H:]MM:SS"""
    return results[0][4]

def last_run_age_grade(results: list[list[str]]) -> str:
    """String in the form xx.xx%"""
    return results[0][5]

def pb_location(results: list[list[str]]) -> str:
    return calc_pb(results)[0]

def pb_date(results: list[list[str]]) -> str:
    """String in the form DD/MM/YYY"""
    return calc_pb(results)[1]

def pb_time(results: list[list[str]]) -> str:
    """String in the form [H:]MM:SS"""
    return calc_pb(results)[4]

def best_age_grade_location(results: list[list[str]]) -> str:
    return calc_best_age_grade(results)[0]

def best_age_grade_date(results: list[list[str]]) -> str:
    """String in the form DD/MM/YYY"""
    return calc_best_age_grade(results)[1]

def best_age_grade(results: list[list[str]]) -> str:
    """String in the form xx.xx%"""
    return calc_best_age_grade(results)[5]

def best_finish_position_location(results: list[list[str]]) -> str:
    return calc_best_finish_position(results)[0]

def best_finish_position_date(results: list[list[str]]) -> str:
    """String in the form DD/MM/YYY"""
    return calc_best_finish_position(results)[1]

def best_finish_position(results: list[list[str]]) -> int:
    return int(calc_best_finish_position(results)[3])

def most_runs_per_year(results: list[list[str]]) -> int:
    return Counter(map(lambda result: int(result[1].split("/")[-1]), results)).most_common(1)[0][1]

def most_runs_per_year_year(results: list[list[str]]) -> int:
    return Counter(map(lambda result: int(result[1].split("/")[-1]), results)).most_common(1)[0][0]

def most_runs_per_location(results: list[list[str]]) -> int:
    return Counter(map(lambda result: result[0], results)).most_common(1)[0][1]

def most_runs_per_location_location(results: list[list[str]]) -> str:
    return Counter(map(lambda result: result[0], results)).most_common(1)[0][0]

def num_unique_locations(results: list[list[str]]) -> int:
    return len(set(map(lambda result: result[0], results)))

def tourism_percentage(results: list[list[str]]) -> float:
    """Between 0 and 1"""
    return num_unique_locations(results) / num_runs(results)

def tourism_percentage_formatted(results: list[list[str]]) -> str:
    """xx.xx%"""
    return f"{tourism_percentage(results)*100:.2f}%"

################################################################################
# Main to print all statistics
################################################################################

def main(runner_id: int) -> None:
    """
    Print all the statistics for the given runner.
    """
    results: list[list[str]] = fetch_runner_results(runner_id)
    stats: tuple[tuple[str, Callable[[list[list[str]]], Any]]] = (
        ("Num Runs", num_runs),
        ("Total Kilometres Run", total_kms_run),
        ("Total Run Time", total_run_time),
        ("Average Run Time", average_run_time),
        ("First Run Location", first_run_location),
        ("First Run Date", first_run_date),
        ("First Run Position", first_run_position),
        ("First Run Time", first_run_time),
        ("First Run Age Grade", first_run_age_grade),
        ("Last Run Location", last_run_location),
        ("Last Run Date", last_run_date),
        ("Last Run Position", last_run_position),
        ("Last Run Time", last_run_time),
        ("Last Run Age Grade", last_run_age_grade),
        ("PB Location", pb_location),
        ("PB Date", pb_date),
        ("PB Time", pb_time),
        ("Best Age Grade Location", best_age_grade_location),
        ("Best Age Grade Date", best_age_grade_date),
        ("Best Age Grade", best_age_grade),
        ("Best Finish Position Location", best_finish_position_location),
        ("Best Finish Position Date", best_finish_position_date),
        ("Best Finish Position", best_finish_position),
        ("Most Runs In A Year", most_runs_per_year),
        ("Year with Most Runs", most_runs_per_year_year),
        ("Most Runs At A Location", most_runs_per_location),
        ("Location with Most Runs", most_runs_per_location_location),
        ("Number of Unique Locations", num_unique_locations),
        ("Tourism Percentage", tourism_percentage_formatted),
    )
    print(f"\nStats for Runner {runner_id}\n")
    for stat_name, stat_func in stats:
        stat: Any = stat_func(results)
        print(f"{stat_name}: {stat}")

if __name__ == "__main__":
    main(int(os.getenv("PARKRUNNER_ME")))
