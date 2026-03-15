import dotenv
import os
from distutils.util import strtobool
import logging

# Log to stderr, DEBUG and above, only from this package
stderr_handler = logging.StreamHandler()
stderr_handler.addFilter(lambda record: record.name.startswith(__name__))

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        stderr_handler
    ]
)

dotenv.load_dotenv()

def _my_strtobool(env_var_name: str, default: bool) -> bool:
    """
    Given the name of an environment variable to search for, use strtobool from
    distutils to read it as a boolean and return the default if it's not present
    or invalid according to strtobool.
    """

    try:
        return bool(strtobool(os.getenv(env_var_name, "invalid")))
    except ValueError:
        return default

PARKRUNNERS_ENV_NAME_TO_ID: dict[str, int] = dict()
for key, value in os.environ.items():
    if key.startswith("PARKRUNNER_"):
        try:
            PARKRUNNERS_ENV_NAME_TO_ID[key[11:].upper()] = int(value)
        except:
            continue

ALL_PARKRUNNER_IDS: list[int] = PARKRUNNERS_ENV_NAME_TO_ID.values()
_TABLE_MAX_WIDTH: int = int(os.getenv("TABLE_MAX_WIDTH", 180))
_CACHE_FORCE_VALID: bool = _my_strtobool("CACHE_FORCE_VALID", False)
_CACHE_FORCE_INVALID: bool = _my_strtobool("CACHE_FORCE_INVALID", False)
MIN_SECS_BETWEEN_QUERIES: int = int(os.getenv("MIN_SECS_BETWEEN_QUERIES", 2))

def get_cache_force_valid() -> bool:
    return _CACHE_FORCE_VALID

def get_cache_force_invalid() -> bool:
    return _CACHE_FORCE_INVALID

def get_table_max_width() -> int:
    return _TABLE_MAX_WIDTH
