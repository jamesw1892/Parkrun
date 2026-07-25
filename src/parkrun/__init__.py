import dotenv
import os
import logging

dotenv.load_dotenv()

def _strtobool(val: str) -> bool:
    """
    If the given string is a truthy or falsey value then convert it to the bool
    that it represents. Otherwise, raise ValueError. Truthy values are y, yes,
    t, true, on, 1. Falsey values are n, no, f, false, off, 0.
    """
    v: str = val.strip().lower()
    if v in ("y", "yes", "t", "true", "on", "1"):
        return True
    if v in ("n", "no", "f", "false", "off", "0"):
        return False
    raise ValueError(f"invalid truth value: {val!r}")

def _env_strtobool(env_var_name: str, default: bool) -> bool:
    """
    Given the name of an environment variable, fetch it, convert it to a boolean
    and return it. If it's not present or not truthy/falsey then return the
    given default.
    """

    try:
        return _strtobool(os.getenv(env_var_name, "invalid"))
    except ValueError:
        return default

PARKRUNNERS_ENV_NAME_TO_ID: dict[str, int] = dict()
for key, value in os.environ.items():
    if key.startswith("PARKRUNNER_"):
        try:
            PARKRUNNERS_ENV_NAME_TO_ID[key[11:].upper()] = int(value)
        except:
            continue

ALL_PARKRUNNER_IDS: list[int] = list(PARKRUNNERS_ENV_NAME_TO_ID.values())
_TABLE_MAX_WIDTH: int = int(os.getenv("TABLE_MAX_WIDTH", 180))
_CACHE_FORCE_VALID: bool = _env_strtobool("CACHE_FORCE_VALID", False)
_CACHE_FORCE_INVALID: bool = _env_strtobool("CACHE_FORCE_INVALID", False)
_MIN_SECS_BETWEEN_QUERIES: int = int(os.getenv("MIN_SECS_BETWEEN_QUERIES", 5))

def get_cache_force_valid() -> bool:
    return _CACHE_FORCE_VALID

def get_cache_force_invalid() -> bool:
    return _CACHE_FORCE_INVALID

def get_table_max_width() -> int:
    return _TABLE_MAX_WIDTH

def get_min_secs_between_queries() -> int:
    return _MIN_SECS_BETWEEN_QUERIES

# Log to stderr, only from this package
stderr_handler = logging.StreamHandler()
stderr_handler.addFilter(lambda record: record.name.startswith(__name__))

logging.basicConfig(
    level=os.getenv("MIN_LOG_LEVEL", "WARNING").upper(),
    handlers=[
        stderr_handler
    ]
)
