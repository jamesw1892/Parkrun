import datetime
from dotenv import load_dotenv
from os import getenv

load_dotenv()

# Arguments
runner_ids: list[int] = [
    int(getenv("PARKRUNNER_ME")),
    int(getenv("PARKRUNNER_BOB")),
]
start_date: datetime.date = datetime.date(2025, 1, 1)
end_date: datetime.date = datetime.date(2026, 1, 1)

# Graphs
from ActivityGraph import activity_graph
from TimeGraph import time_graph

#activity_graph(runner_ids, start_date, end_date)
#time_graph(runner_ids, start_date, end_date)

# Stats
from CommonRunComparison import common_run_comparison
from RunnerStats import runner_stats

#common_run_comparison(runner_ids)
runner_stats(runner_ids)
