from RunnerStats import result_to_timedelta
from Scraper import fetch_runner_results
from collections import Counter
import datetime
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoLocator
from matplotlib.dates import AutoDateFormatter, AutoDateLocator
import os

load_dotenv()

def get_num_months(first_run_date: datetime.date, last_run_date: datetime.date) -> int:
    return (last_run_date.year - first_run_date.year) * 12 + last_run_date.month - first_run_date.month + 1

def activity_graph(results: list[list[str]], parkrunner_number: int) -> None:
    """
    Display a column graph of the number of parkrun events the parkrunner
    completed each month from their first to their most recent, including months
    in between where none were completed.
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
    plt.clf()
    plt.bar(months, counts)
    plt.xlabel("Month")
    plt.ylabel("Number of Runs")

    plt.title(f"Parkrunner {parkrunner_number}'s Frequency Per Month")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    #plt.show()
    plt.savefig(f"graphs/activity/{parkrunner_number}.png")

def format_time(seconds, _):
    """Convert seconds to MM:SS format for y-axis"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def time_graph(results: list[list[str]], parkrunner_number: int) -> None:
    """
    Display a line graph of all parkrun times over time.
    """

    # Plot the data
    dates: list[datetime.date] = [datetime.datetime.strptime(result[1], "%d/%m/%Y").date() for result in results]
    times: list[int] = [round(result_to_timedelta(result).total_seconds()) for result in results]
    plt.clf()
    plt.plot(dates, times)

    # Format axis labels, tick marks and grid lines
    plt.xlabel("Date")
    xaxis_locator = AutoDateLocator()
    plt.gca().xaxis.set_major_locator(xaxis_locator)
    plt.gca().xaxis.set_major_formatter(AutoDateFormatter(xaxis_locator))
    plt.ylabel("Time")
    plt.gca().yaxis.set_major_locator(AutoLocator())
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(format_time))
    plt.grid(True, linestyle='--', alpha=0.7)

    plt.title(f"Parkrunner {parkrunner_number}'s Finish Times Over Time")
    #plt.show()
    plt.savefig(f"graphs/times/{parkrunner_number}.png")

def main(parkrunner_number: int) -> None:
    results: list[list[str]] = fetch_runner_results(parkrunner_number)

    activity_graph(results, parkrunner_number)
    time_graph(results, parkrunner_number)

if __name__ == "__main__":
    main(int(os.getenv("PARKRUNNER_ME")))

    # for key in os.environ:
    #     if key.startswith("PARKRUNNER_"):
    #         print(key)
    #         main(int(os.getenv(key)))
