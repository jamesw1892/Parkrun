Objective: to scrape the Parkrun API (or website since the API has been deprecated for years) to get info and use to show stats and graphs.

![World map of parkruns as multi-coloured dots](img/World%20Map%20Parkruns%20Multicoloured%20Dots.png)

# Usage

## Editing Main.py to call library

1. Copy the file `.env.example` and name the copy `.env`.
2. Edit it to include the parkrun numbers you're interested in (numbers can be found on barcodes, results emails and online at https://www.parkrun.org.uk/). It is often displayed following an 'A' but don't include the 'A' in the `.env` file. Also adjust other settings stored in `.env` as desired.
3. Edit `src/main.py` to change which parkrunner(s) to act on and the start and end dates for graphs.
4. Uncomment the graph or stat function you want to run and comment the rest out.
5. Run `python src/main.py`.

## Command-Line Interface

Run `python src/cli.py`. It takes command-line arguments and has help text.

If you'd like to make use of `.env` that you may have created as above, you can do e.g.:

```bash
source .env
python src/cli.py runner_stats $PARKRUNNER_ME
```

# Files

- `.env`: Stores the configuration, particularly the Parkrun numbers of Parkrunners of interest.
- `.env.example`: Template for `.env`.
- `src/`: Stores source code:
    - `cli.py`: Uses command-line arguments to use the `parkrun` package.
    - `main.py`: An example program that uses the `parkrun` package and Parkrunners of interest in `.env` that can be edited as desired.
    - `tests.py`: Unit tests for tricky functions in the `parkrun` package.
    - `parkrun/`: `parkrun` package source code:
        - `api/`:
            - `cache.py`: Implements `check_cache` and `write_cache` to cache data to not repeatedly hit the website. It intelligently invalidates the cache at the time that results normally come out on Saturdays or Christmas or New Years Day.
            - `parkrun_exception.py`: Custom exception.
            - `scraper.py`: Fetches and parses pages on the parkrun website, caching results.
            - `utils.py`: Utility functions used by the rest of the package.
        - `graphs/`:
            - `activity.py`: Graphs the number of parkruns that parkrunners did each month.
            - `event_map.py`: Maps all parkrun events in the world.
            - `times.py`: Graphs the finish times of parkrunners.
        - `models/`: Classes to model Parkrunners, locations, times, results, ...:
            - `age_grade.py`: Models the age grade of a run.
            - `event_collection.py`: Models many parkrun events.
            - `event.py`: Models a parkrun event.
            - `pb.py`: Models whether a run is a personal best.
            - `position.py`: Models the finish position of a run.
            - `runner_result.py`: Models a run.
            - `runner.py`: Models a runner with their number, name and all their runs.
            - `time.py`: Models the finish time of a run or any other parkrun-related time, e.g. total/average finish time.
        - `tables/`:
            - `achievements.py`: Print a table with a side-by-side comparison of achievement progress by each parkrunner.
            - `common_run_comparison.py`: Print a table with a side-by-side comparison of runs that parkrunners did together.
            - `latest_update.py`: Print a table with a summary of the result of each given parkrunner that did the most recent parkrun between the given dates.
            - `most_common.py`: Print a table with a thing about the parkrunner sorted by how many times that thing occurred, side-by-side for each given parkrunner.
            - `pb_progress.py`: Print a table with information about each time each parkrunner improved their PB side-by-side.
            - `runner_stats.py`: Print a table with statistics about parkrunners side-by-side.
