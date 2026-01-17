import dotenv
import os

dotenv.load_dotenv()

ALL_PARKRUNNER_IDS: list[int] = [int(os.getenv(key)) for key in os.environ if key.startswith("PARKRUNNER_")]
TABLE_MAX_WIDTH: int = int(os.getenv("TABLE_MAX_WIDTH", 180))
