import os
from datetime import datetime, timedelta, time, date
import logging

logger = logging.getLogger(__name__)

stderr_handler = logging.StreamHandler()
stderr_handler.addFilter(lambda record: record.name == __name__)

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        stderr_handler
    ]
)

cache_dir: str = os.path.join(os.path.dirname(__file__), "cache")

if not os.path.exists(cache_dir):
    os.mkdir(cache_dir)

# The hour of the day that parkrun results could start coming through and
# that they have definitely come through. We always treat it as a cache miss
# if it is between these times so we check for the latest results. In order
# to treat it as a cache miss, we set the most recent saturday to the end
# time so no file can have been modified in the future
SAT_HR_RESULT_START: int = 10
SAT_HR_RESULT_END: int = 13

ENCODING = "utf-8"

def most_recent_saturday(reference: datetime = None):
    """
    Caches become invalidated after midday on Saturday since this is when
    parkrun results should be in by
    """

    if reference is None:
        reference = datetime.now()

    weekday = reference.weekday() # Monday=0, Saturday=5

    # Calculate how many days to subtract to get to last Saturday
    days_since_saturday: int = (weekday - 5) % 7
    last_saturday: date = reference.date() - timedelta(days=days_since_saturday)
    last_saturday: datetime = datetime.combine(last_saturday, time(SAT_HR_RESULT_END))

    # If today is before result start time on Saturday then the above
    # calculation will have given result end time today but we actually want the
    # previous week because results can't have come in yet
    if weekday == 5 and reference.hour < SAT_HR_RESULT_START:
        last_saturday -= timedelta(days=7)

    return last_saturday

def check_cache(type_name: str, file_name: str) -> None | str:
    sub_cache_dir: str = os.path.join(cache_dir, type_name)
    if not os.path.exists(sub_cache_dir):
        logger.debug("Cache miss: Type dir '%s' doesn't exist", type_name)
        return None

    file_path: str = os.path.join(sub_cache_dir, file_name)
    if not os.path.exists(file_path):
        logger.debug("Cache miss: File '%s' doesn't exist within existing type dir '%s'", file_name, type_name)
        return None

    # If the file in the cache is older than the most recent saturday then
    # there might be updates so treat the cache as invalid
    modified: datetime = datetime.fromtimestamp(os.stat(file_path).st_mtime)
    if modified < most_recent_saturday():
        logger.debug("Cache miss: Existing file '%s' within type dir '%s' is out of date", file_name, type_name)
        #os.remove(file_path)
        return None

    logger.debug("Cache hit: %s/%s", type_name, file_name)
    with open(file_path, encoding=ENCODING) as f:
        return f.read()

def write_cache(type_name: str, file_name: str, contents: str) -> None:
    sub_cache_dir: str = os.path.join(cache_dir, type_name)
    if not os.path.exists(sub_cache_dir):
        os.mkdir(sub_cache_dir)

    file_path: str = os.path.join(sub_cache_dir, file_name)
    with open(file_path, "w", encoding=ENCODING) as f:
        f.write(contents)

    logger.debug("Updated cache: %s/%s", type_name, file_name)
