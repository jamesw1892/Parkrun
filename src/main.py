import datetime
from dotenv import load_dotenv
import os
from parkrun.api.parkrun_exception import ParkrunException

load_dotenv()

def get_parkrunner_id(env_name: str) -> int:
    """
    Return the parkrunner ID as an integer by reading the env file or printing
    an error if there is one.
    """

    if env_name not in os.environ:
        raise ParkrunException(f"'{env_name}' not found in .env file")

    env_value: str = os.getenv(env_name)

    try:
        return int(env_value)
    except:
        raise ParkrunException(f"Value of environment variable '{env_name}' must be an integer, not '{env_value}'")

try:

    # Arguments
    runner_ids: list[int] = [
        get_parkrunner_id("PARKRUNNER_ME"),
        get_parkrunner_id("PARKRUNNER_BOB"),
    ]
    start_date: datetime.date = datetime.date(2025, 1, 1)
    end_date: datetime.date = datetime.date(2026, 1, 1)

    # Graphs
    from parkrun.graphs.activity import activity_graph
    from parkrun.graphs.times import time_graph

    #activity_graph(runner_ids, start_date, end_date)
    #time_graph(runner_ids, start_date, end_date)

    # Stats
    from parkrun.tables.common_run_comparison import common_run_comparison
    from parkrun.tables.latest_update import latest_update
    from parkrun.tables.most_common import most_common_year, most_common_location, most_common_location_initial, most_common_month, most_common_time_seconds
    from parkrun.tables.pb_progress import pb_progress
    from parkrun.tables.runner_stats import runner_stats

    #common_run_comparison(runner_ids, start_date, end_date)
    #latest_update(runner_ids, start_date, end_date)
    #most_common_year(runner_ids, start_date, end_date)
    #most_common_location(runner_ids, start_date, end_date)
    #most_common_location_initial(runner_ids, start_date, end_date)
    #most_common_month(runner_ids, start_date, end_date)
    #most_common_time_seconds(runner_ids, start_date, end_date)
    #pb_progress(runner_ids, start_date, end_date)
    runner_stats(runner_ids, start_date, end_date)

except ParkrunException as e:
    print(e)
    exit(1)
