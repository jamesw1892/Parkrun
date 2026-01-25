import dotenv
import os
from distutils.util import strtobool

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

ALL_PARKRUNNER_IDS: list[int] = [int(os.getenv(key)) for key in os.environ if key.startswith("PARKRUNNER_")]
TABLE_MAX_WIDTH: int = int(os.getenv("TABLE_MAX_WIDTH", 180))
_CACHE_FORCE_VALID: bool = _my_strtobool("CACHE_FORCE_VALID", False)

def get_cache_force_valid() -> bool:
    return _CACHE_FORCE_VALID
