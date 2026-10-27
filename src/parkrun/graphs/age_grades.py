from parkrun.graphs.utils import results_graph
import datetime
from matplotlib.ticker import PercentFormatter

def age_grade_graph(
        runner_ids: list[int],
        start_date: datetime.date = datetime.date.min,
          end_date: datetime.date = datetime.date.max,
    ) -> None:
    """
    Display a MatPlotLib line graph of the age grades of the parkrunners
    between `start_date` and `end_date` (default to all parkruns any of them
    ran), skipping runs without an age grade.
    """

    # An empty age grade string (e.g. no age category) gives a value of 0
    results_graph(
        runner_ids, start_date, end_date,
        lambda result: result.age_grade.value if result.age_grade.string != "" else None,
        "Age Grade", PercentFormatter(xmax=1), "Parkrun Age Grades",
    )
