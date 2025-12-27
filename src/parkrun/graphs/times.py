from parkrun.models.runner import Runner
from parkrun.api.scraper import fetch_runner_results
import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoLocator
from matplotlib.dates import AutoDateFormatter, AutoDateLocator

def _format_time(seconds, _):
    """Convert seconds to MM:SS format for y-axis labels"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def time_graph(
        runner_ids: list[int],
        start_date: datetime.date = datetime.date.min,
          end_date: datetime.date = datetime.date.max,
    ) -> None:
    """
    Display a MatPlotLib line graph of the finish times of the parkrunners
    between `start_date` and `end_date` (default to all parkruns any of them
    ran).
    """

    runners: list[Runner] = [fetch_runner_results(runner_id) for runner_id in runner_ids]

    # Plot each parkrunner separately but on the same axis - `dates` will be
    # different for each parkrunner but MatPlotLib will work it out.
    plt.clf()
    for runner in runners:
        dates: list[datetime.date] = []
        times: list[int] = []
        for result in runner.results:
            if start_date <= result.date <= end_date:
                dates.append(result.date)

                # Plot the time as an integer number of seconds and use
                # `_format_time` to format the chosen times for the y-axis.
                times.append(round(result.time.timedelta.total_seconds()))

        # Plot the data with legend labelled with the runner's identity string
        plt.plot(dates, times, marker="o", label=runner.format_identity())

    plt.xlabel("Date")
    xaxis_locator = AutoDateLocator()
    plt.gca().xaxis.set_major_locator(xaxis_locator)
    plt.gca().xaxis.set_major_formatter(AutoDateFormatter(xaxis_locator))

    plt.ylabel("Time")
    plt.gca().yaxis.set_major_locator(AutoLocator())
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(_format_time))

    plt.title("Parkrun Finish Times")
    plt.legend()
    plt.tight_layout()
    plt.show()
