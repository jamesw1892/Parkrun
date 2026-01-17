from parkrun.models.runner import Runner
from parkrun import TABLE_MAX_WIDTH
from parkrun.api.scraper import fetch_runner_results
from parkrun.api.utils import date_description
from collections import Counter
import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from texttable import Texttable

def _get_num_months(start_date: datetime.date, end_date: datetime.date) -> int:
    """Return the number of months between the given dates including both ends"""
    return (end_date.year - start_date.year) * 12 + end_date.month - start_date.month + 1

def activity_graph(
        runner_ids: list[int],
        start_date: datetime.date = datetime.date.min,
          end_date: datetime.date = datetime.date.max,
    ) -> None:
    """
    Display a MatPlotLib line graph of the number of parkrun events the given
    parkrunners ran each month between `start_date` and `end_date`, defaulting
    to the first and last ever parkrun by any runner.
    """

    runners: list[Runner] = [fetch_runner_results(runner_id, start_date, end_date) for runner_id in runner_ids]
    runners_with_results: list[Runner] = list(filter(lambda runner: len(runner.results) > 0, runners))

    date_desc: str = date_description(start_date, end_date)

    if len(runners_with_results) == 0:
        print(f"No results for any of the given runners {date_desc}")
        return

    # Calculate first and last date that any of the runners ran (assumes that
    # runner.results is sorted most recent first)
    first_run_date: datetime.date = min(runner.results[-1].date for runner in runners_with_results)
    last_run_date : datetime.date = max(runner.results[ 0].date for runner in runners_with_results)

    # Count up the number of times each runner has ran in each month
    frequencies: list[Counter] = [
        Counter(result.date.strftime("%Y-%m") for result in runner.results)
        for runner in runners
    ]

    # Organise and format the above data into the x-axis months which is a
    # string of the form YYYY-MM and the multi-series y-axis runner_counts. This
    # has an element per runner and each element is a list with an element per
    # month in the months list, giving the number of times that runner ran in
    # that month
    months: list[str] = []
    runner_counts: list[list[int]] = [[] for _ in runner_ids]
    num_months: int = _get_num_months(first_run_date, last_run_date)
    for month_num in range(num_months):
        years_to_add, month = divmod(first_run_date.month + month_num, 12)
        year: int = first_run_date.year + years_to_add
        if month == 0:
            month = 12
            year -= 1
        month_year: str = f"{year:04}-{month:02}"
        months.append(month_year)
        for runner_index in range(len(frequencies)):
            runner_counts[runner_index].append(frequencies[runner_index].get(month_year, 0))

    # Print the data too
    table = Texttable(TABLE_MAX_WIDTH)
    table.header(["Parkrunner"] + [runner.format_identity() for runner in runners])
    for index, month in enumerate(months):
        table.add_row([month] + [count[index] for count in runner_counts])
    print(table.draw())

    # Plot the data with legend labelled with the runner's identity string
    plt.clf()
    for runner, counts in zip(runners, runner_counts):
        plt.plot(months, counts, marker="o", label=runner.format_identity())
    plt.title(f"Parkruns Per Month {date_desc}")
    plt.xlabel("Month")
    plt.ylabel("Number of Runs")
    plt.xticks(rotation=45, ha="right")
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.legend()
    plt.tight_layout()
    plt.show()
