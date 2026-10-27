from parkrun.graphs.utils import results_graph
import datetime
from matplotlib.ticker import FuncFormatter

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

    # Plot the time as an integer number of seconds and use `_format_time` to
    # format the chosen times for the y-axis.
    results_graph(
        runner_ids, start_date, end_date,
        lambda result: round(result.time.timedelta.total_seconds()),
        "Time", FuncFormatter(_format_time), "Parkrun Finish Times",
    )
