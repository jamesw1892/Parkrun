"""
Parse command-line arguments to display the table or graph of choice with the
parkrunners of choice.
"""

import argparse
import datetime
from parkrun.graphs.activity import activity_graph
from parkrun.graphs.times import time_graph
from parkrun.tables.common_run_comparison import common_run_comparison
from parkrun.tables.most_common import most_common_location, most_common_month, most_common_time_seconds, most_common_year
from parkrun.tables.pb_progress import pb_progress
from parkrun.tables.runner_stats import runner_stats

command_funcs: dict[str, callable] = {
    "activity": activity_graph,
    "times": time_graph,
    "common_run_comparison": common_run_comparison,
    "most_common_location": most_common_location,
    "most_common_month": most_common_month,
    "most_common_time_seconds": most_common_time_seconds,
    "most_common_year": most_common_year,
    "pb_progress": pb_progress,
    "runner_stats": runner_stats,
}

parser = argparse.ArgumentParser(
    description="Print statistic tables or show graphs about parkrun results. The first positional argument must be the table or graph to show and all subsequent positional arguments must be integer runner IDs of those to show."
)

parser.add_argument("command", choices=command_funcs.keys(), help="The table or graph to run")
parser.add_argument("runner", type=int, nargs="+", help="One or more parkrun IDs of runners to analyse")
parser.add_argument("-s", "--start", type=datetime.date.fromisoformat, nargs="?", default=datetime.date.min, help="Date to start from, in any format accepted by datetime.date.fromisoformat, defaulting to forever")
parser.add_argument("-e", "--end", type=datetime.date.fromisoformat, nargs="?", default=datetime.date.max, help="Date to end at, in any format accepted by datetime.date.fromisoformat, defaulting to forever")

args = parser.parse_args()

# Call the function with the runner ids
command_funcs[args.command](args.runner, start_date=args.start, end_date=args.end)
