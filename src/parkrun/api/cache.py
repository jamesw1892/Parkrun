from datetime import datetime, timedelta, time, date
import logging
from pathlib import Path
from platformdirs import user_cache_dir

logger = logging.getLogger(__name__)

stderr_handler = logging.StreamHandler()
stderr_handler.addFilter(lambda record: record.name == __name__)

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        stderr_handler
    ]
)

cache_dir: Path = Path(user_cache_dir("parkrun", False, ensure_exists=True))

# The hour of the day that parkrun results could start coming through and
# that they have definitely come through. We always treat it as a cache miss
# if it is between these times so we check for the latest results. In order
# to treat it as a cache miss, we set the most recent parkrun to the end
# time so no file can have been modified in the future
HR_RESULT_START: int = 10
HR_RESULT_END: int = 13

ENCODING = "utf-8"

def most_recent_parkrun(reference: datetime = None) -> datetime:
    """
    Return the datetime of the most recent parkrun (including Christmas and New
    Years Day). We use the constants HR_RESULT_START and HR_RESULT_END. If the
    reference time is before HR_RESULT_START then we give the previous parkrun
    date so results last updated then are valid because results couldn't have
    come out yet. The time returned is always HR_RESULT_END so if the cache is
    updated between the constants then it is always treated as invalid since
    results could come out at any time in this window.
    """

    if reference is None:
        reference = datetime.now()

    reference_date: date = reference.date()
    reference_weekday: int = reference.weekday() # Monday=0, Saturday=5

    # Calculate how many days to subtract to get to last Saturday
    days_since_saturday: int = (reference_weekday - 5) % 7
    last_saturday_date: date = reference.date() - timedelta(days=days_since_saturday)

    # If between Christmas or New Years Day and saturday then this should be the
    # most recent Saturday
    christmas_day: date = date(reference.year, 12, 25)
    new_years_day: date = date(reference.year, 1, 1)
    if last_saturday_date < christmas_day <= reference_date:
        last_parkrun_date = christmas_day
    elif last_saturday_date < new_years_day <= reference_date:
        last_parkrun_date = new_years_day
    else:
        last_parkrun_date = last_saturday_date

    # If today is a parkrun day, before result start time, then the above
    # calculation will have given today but we actually want the previous
    # parkrun because results can't have come in yet
    if reference_weekday == last_parkrun_date.weekday() and reference.hour < HR_RESULT_START:

        week_before_last_parkrun_date: date = last_parkrun_date - timedelta(days=7)

        # If the parkrun before the last parkrun was Christmas or New Years Day
        # then we want Christmas or New Years Day
        if week_before_last_parkrun_date < christmas_day < last_parkrun_date:
            last_parkrun_date = christmas_day
        elif week_before_last_parkrun_date < new_years_day < last_parkrun_date:
            last_parkrun_date = new_years_day

        # If not, and the last parkrun also wasn't Christmas or New Years Day
        # then both are Saturdays so just subtract 7 days
        elif reference_weekday == 5:
            last_parkrun_date -= timedelta(days=7)

        # Otherwise, the last parkrun was Christmas or New Years Day but we want
        # to go back to the Saturday before
        else:
            last_parkrun_date = last_saturday_date

    return datetime.combine(last_parkrun_date, time(HR_RESULT_END))

def check_cache(type_name: str, file_name: str) -> None | str:
    sub_cache_dir: Path = cache_dir / type_name
    if not sub_cache_dir.exists():
        logger.debug("Cache miss: Type dir '%s' doesn't exist", type_name)
        return None

    file_path: Path = sub_cache_dir / file_name
    if not file_path.exists():
        logger.debug("Cache miss: File '%s' doesn't exist within existing type dir '%s'", file_name, type_name)
        return None

    # If the file in the cache is older than the most recent parkrun then
    # there might be updates so treat the cache as invalid
    modified: datetime = datetime.fromtimestamp(file_path.stat().st_mtime)
    if modified < most_recent_parkrun():
        logger.debug("Cache miss: Existing file '%s' within type dir '%s' is out of date", file_name, type_name)
        return None

    logger.debug("Cache hit: %s/%s", type_name, file_name)
    with open(file_path, encoding=ENCODING) as f:
        return f.read()

def write_cache(type_name: str, file_name: str, contents: str) -> None:
    sub_cache_dir: Path = cache_dir / type_name
    if not sub_cache_dir.exists():
        sub_cache_dir.mkdir()

    file_path: Path = sub_cache_dir / file_name
    with open(file_path, "w", encoding=ENCODING) as f:
        f.write(contents)

    logger.debug("Updated cache: %s/%s", type_name, file_name)
