from parkrun.models.runner import Runner
from parkrun.models.runner_result import RunnerResult
from parkrun.api.scraper_runner import fetch_runner_results
from parkrun.api.utils import date_description
from collections.abc import Callable
import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoLocator, Formatter
from matplotlib.dates import AutoDateFormatter, AutoDateLocator

def show_graph(title: str) -> None:
    """
    Add the title and legend to the current MatPlotLib graph and display it.
    """
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.show()

def results_graph(
        runner_ids: list[int],
        start_date: datetime.date,
          end_date: datetime.date,
        get_value: Callable[[RunnerResult], float | None],
        ylabel: str,
        yaxis_formatter: Formatter,
        title: str,
    ) -> None:
    """
    Display a MatPlotLib line graph of `get_value` of each result of the
    parkrunners between `start_date` and `end_date` against its date, skipping
    results where it returns None. The y-axis is labelled `ylabel` with ticks
    formatted by `yaxis_formatter`, and the title is `title` followed by a
    description of the dates.
    """

    runners: list[Runner] = [fetch_runner_results(runner_id, start_date, end_date) for runner_id in runner_ids]

    # Plot each parkrunner separately but on the same axis - `dates` will be
    # different for each parkrunner but MatPlotLib will work it out.
    plt.clf()
    for runner in runners:
        dates: list[datetime.date] = []
        values: list[float] = []
        for result in runner.results:
            value: float | None = get_value(result)
            if value is not None:
                dates.append(result.date)
                values.append(value)

        # Plot the data with legend labelled with the runner's identity string
        plt.plot(dates, values, marker="o", label=runner.format_identity())

    plt.xlabel("Date")
    xaxis_locator = AutoDateLocator()
    plt.gca().xaxis.set_major_locator(xaxis_locator)
    plt.gca().xaxis.set_major_formatter(AutoDateFormatter(xaxis_locator))

    plt.ylabel(ylabel)
    plt.gca().yaxis.set_major_locator(AutoLocator())
    plt.gca().yaxis.set_major_formatter(yaxis_formatter)

    show_graph(f"{title} {date_description(start_date, end_date)}")
