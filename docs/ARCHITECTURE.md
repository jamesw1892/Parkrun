# Architecture

## Layers

Everything lives under `src/parkrun/`:

1. **Scraping (`api/scraper.py`, `api/scraper_runner.py`).** `fetch()` in `scraper.py` is the only place that makes HTTP requests. It checks the disk cache first, then rate-limits (`MIN_SECS_BETWEEN_QUERIES`, default 5 seconds, to be polite to parkrun), and on connection/HTTP errors falls back to any stale cached copy. It is also memoised in-process with `@cache`. `scraper.py` fetches the events list (`images.parkrun.com/events.json`) and event results; `scraper_runner.py` fetches a runner's `/parkrunner/<n>/all/` page and parses it with BeautifulSoup into a `Runner`. Any new scraping must go through `fetch()`.
2. **Caching (`api/cache.py`).** Raw responses are stored under the platformdirs user cache dir (`~/.cache/parkrun/<type_name>/<file_name>` on Linux). An entry is stale if it was written before `most_recent_parkrun()`, which models when results are usually published (Saturdays, plus Christmas Day and New Year's Day). Entries fetched with `is_cache_valid_forever=True` (past event results) never expire. `CACHE_FORCE_VALID` / `CACHE_FORCE_INVALID` override this.
3. **Models (`models/`).** Value objects such as `Time`, `Position`, `AgeGrade`, `AgeCategory`, `PB`, `Event` and `Country`. `Runner` holds all of a runner's `RunnerResult`s and computes derived stats (streaks, tourism, consistency, re-index, p-index, ...) as `@cached_property`s.
4. **Outputs (`tables/`, `graphs/`, `maps/`).** Tables are printed with `texttable`, capped at `get_table_max_width()` characters wide; graphs use matplotlib. Each public entry point in these two has the signature `(runner_ids: list[int], start_date: date, end_date: date) -> None` and shows several runners side by side. Maps are drawn with folium on OpenStreetMap tiles and opened in the browser: `maps/render.py` has `map_events()`, which draws any events with a given colour and popup for each; entry points such as `maps/event_map.py` choose the events, colours and popups.

`cli.py` maps command names to those entry points in `command_funcs`; add a new table or graph there to expose it on `prcli`. `src/main.py` is an example script that calls the library directly and isn't part of the package.

## Settings

`src/parkrun/__init__.py` loads `.env` with `dotenv` on import and stores settings as module globals (`_TABLE_MAX_WIDTH`, `_CACHE_FORCE_VALID`, ...). `cli.py` overwrites these from command-line flags after import, so code must read them through the getters (`get_table_max_width()` etc.) at call time. Copying a value at import time silently ignores CLI overrides.

Logging goes to stderr and is filtered to the `parkrun` package and `__main__` loggers, so use `logging.getLogger(__name__)`.

## Tests

`src/tests.py` uses `unittest` with `parameterized`. Tests build model objects directly and never hit the network.

```bash
python src/tests.py                          # all tests
cd src && python -m unittest tests.TestStreaks  # one class (or tests.TestStreaks.<method>)
```

Install the test dependency with `pip install -e '.[test]'`.

## Files

- `src/main.py`: Example program using the `parkrun` package and the parkrunners in `.env`; edit as desired.
- `src/tests.py`: Unit tests for tricky functions.
- `src/parkrun/`: The package
    - `cli.py`: Command-line interface (`prcli`).
    - `api/`:
        - `cache.py`: `check_cache` / `write_cache` and the cache-expiry logic described above.
        - `parkrun_exception.py`: Custom exception.
        - `scraper.py`: Fetches and parses pages on the parkrun website, caching results.
        - `scraper_runner.py`: Fetches and parses runner pages.
        - `utils.py`: Utility functions used by the rest of the package.
    - `graphs/`:
        - `activity.py`: Number of parkruns each parkrunner did each month.
        - `times.py`: Finish times of parkrunners.
    - `maps/`:
        - `browser.py`: Serves a map page once from localhost, since OpenStreetMap tiles don't load from `file://`.
        - `event_map.py`: Map of all parkrun events in the world, coloured by whether a parkrunner has done them.
        - `render.py`: Draws events on a folium map and shows it in the browser.
    - `models/`:
        - `age_category.py`: Age category of a parkrunner at a fixed time.
        - `age_grade.py`: Age grade of a run.
        - `country.py` / `country_collection.py`: A country with parkruns / many of them.
        - `event.py` / `event_collection.py`: A parkrun event / many of them.
        - `event_result.py`: Finishers and volunteers of a single event on a single date.
        - `event_runner_result.py`: A single finisher's result at a single event on a single date.
        - `pb.py`: Whether a run is a personal best.
        - `position.py`: Finish position of a run.
        - `runner_result.py`: A run.
        - `runner.py`: A runner with their number, name and all their runs.
        - `time.py`: A finish time or any other parkrun-related time, e.g. total/average.
    - `tables/`:
        - `achievements.py`: Side-by-side achievement progress.
        - `common_run_comparison.py`: Side-by-side comparison of runs parkrunners did together.
        - `latest_update.py`: Summary of each parkrunner's result at the most recent parkrun between the given dates.
        - `most_common.py`: A property of each parkrunner's runs, sorted by how often it occurred.
        - `pb_progress.py`: Each time each parkrunner improved their PB.
        - `runner_stats.py`: Statistics about parkrunners side by side.
