from Scraper import fetch_runner_results
from collections import Counter
import matplotlib.pyplot as plt
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def get_num_months(first_run_date: datetime.date, last_run_date: datetime.date) -> int:
    return (last_run_date.year - first_run_date.year) * 12 + last_run_date.month - first_run_date.month + 1

def activity_graph(results: list[list[str]]) -> None:
    """
    Display a graph of the number of parkrun events the parkrunner completed
    each month from their first to their most recent, including months in
    between where none were completed.
    """

    # Extract the "Run Date" column (assuming it's the second column in the results)
    run_dates: list[datetime.date] = [datetime.datetime.strptime(row[1], "%d/%m/%Y").date() for row in results]

    # Group by month and year
    month_years: list[str] = [date.strftime("%Y-%m") for date in run_dates]
    frequencies = Counter(month_years)

    # Generate all months within the range of the results
    first_run_date: datetime.date = min(run_dates)
    last_run_date: datetime.date = max(run_dates)
    num_months: int = get_num_months(first_run_date, last_run_date)

    months: list[str] = []
    counts: list[int] = []
    for month_num in range(num_months):
        years_to_add, month = divmod(first_run_date.month + month_num, 12)
        year: int = first_run_date.year + years_to_add
        if month == 0:
            month = 12
            year -= 1
        month_year = f"{year:04}-{month:02}"
        months.append(month_year)
        counts.append(frequencies.get(month_year, 0))

    # Plot the data
    plt.bar(months, counts)
    plt.xlabel("Month")
    plt.ylabel("Number of Runs")

    plt.title("Parkrun Frequency Per Month")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()

def main(parkrunner_number: int) -> None:
    results: list[list[str]] = fetch_runner_results(parkrunner_number)

    activity_graph(results)

if __name__ == "__main__":
    main(int(os.getenv("PARKRUNNER_ME")))
