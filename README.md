Objective: to scrape the Parkrun API (or website since the API has been deprecated for years) to get info and use to show stats and graphs.

# Demo

This mainly uses Darren WOOD (parkrunner number 490) because he was the first parkrunner to run 1000 parkruns. These outputs were created 2026-07-25.

## Runner Stats

```text
$ prcli runner_stats 490
Runner stats from all time
+----------------------------+--------------------------------------------------------------------------------------+
|         Parkrunner         |                                  Darren WOOD (490)                                   |
+============================+======================================================================================+
| Most Recent Age Category   | VM40-44                                                                              |
+----------------------------+--------------------------------------------------------------------------------------+
| Num Runs                   | 1008                                                                                 |
+----------------------------+--------------------------------------------------------------------------------------+
| Total Run Time             | 16 days, 5:09:41                                                                     |
+----------------------------+--------------------------------------------------------------------------------------+
| Average Run Time           | 23:09                                                                                |
+----------------------------+--------------------------------------------------------------------------------------+
| First Run                  | 2004-10-09 Bushy Park: 10th, 24:15, 53.20%                                           |
+----------------------------+--------------------------------------------------------------------------------------+
| Lastest Run                | 2026-07-25 Nonsuch: 830th, 40:07, 35.06%                                             |
+----------------------------+--------------------------------------------------------------------------------------+
| Best Time                  | 17:58 (2007-11-03 Bushy Park)                                                        |
+----------------------------+--------------------------------------------------------------------------------------+
| Best Age Grade             | 72.39% (2025-03-01 Bromley)                                                          |
+----------------------------+--------------------------------------------------------------------------------------+
| Best Position              | 1st (2012-01-14 Hanley; 2016-02-06 Durham NC; 2025-02-15 Delaware and Raritan Canal) |
+----------------------------+--------------------------------------------------------------------------------------+
| Most Runs In A Year        | 55 (2016)                                                                            |
+----------------------------+--------------------------------------------------------------------------------------+
| Most Runs At A Location    | 401 (Frimley Lodge)                                                                  |
+----------------------------+--------------------------------------------------------------------------------------+
| Countries Visited          | 9                                                                                    |
+----------------------------+--------------------------------------------------------------------------------------+
| Number of Unique Locations | 120                                                                                  |
+----------------------------+--------------------------------------------------------------------------------------+
| Tourism Percentage         | 11.90%                                                                               |
+----------------------------+--------------------------------------------------------------------------------------+
| Consistency                | 88.58%                                                                               |
+----------------------------+--------------------------------------------------------------------------------------+
| Streak                     | 9 (2026-05-30 - 2026-07-25)                                                          |
+----------------------------+--------------------------------------------------------------------------------------+
| Floating Streak            | 63 (2007-02-10 - 2008-04-05)                                                         |
+----------------------------+--------------------------------------------------------------------------------------+
| Tourist Streak             | 0                                                                                    |
+----------------------------+--------------------------------------------------------------------------------------+
| Tourist Streak 2           | 5 (2026-06-27 - 2026-07-25)                                                          |
+----------------------------+--------------------------------------------------------------------------------------+
| Floating Tourist Streak    | 6 (2021-07-24 - 2021-08-28)                                                          |
+----------------------------+--------------------------------------------------------------------------------------+
| Floating Tourist Streak 2  | 17 (2020-02-22 - 2021-10-16)                                                         |
+----------------------------+--------------------------------------------------------------------------------------+
| re-index                   | 31                                                                                   |
+----------------------------+--------------------------------------------------------------------------------------+
| p-index                    | 10                                                                                   |
+----------------------------+--------------------------------------------------------------------------------------+
```

## World map of parkruns as multi-coloured dots

![](img/World%20Map%20Parkruns%20Multicoloured%20Dots.png)

# Installation

From the root directory of the repo:

```bash
python3 -m venv pyvenv  # Create a virtual environment in the pyvenv directory
source pyvenv/bin/activate  # Activate the virtual environment
pip install .  # Install the package and its dependencies into the virtual environment
```

Now the `prcli` script is on PATH.

# Usage

## Command-Line Interface

Run `prcli` (same as running `python src/parkrun/cli.py`). It takes command-line arguments and has help text.

You can use the names (case in-sensitive) in the `.env` file that you may have created as below to use their numbers, e.g.:

```bash
prcli runner_stats me
```

## Editing Main.py to call library

1. Copy the file `.env.example` and name the copy `.env`.
2. Edit it to include the parkrun numbers you're interested in (numbers can be found on barcodes, results emails and online at https://www.parkrun.org.uk/). It is often displayed following an 'A' but don't include the 'A' in the `.env` file. Also adjust other settings stored in `.env` as desired.
3. Edit `src/main.py` to change which parkrunner(s) to act on and the start and end dates for graphs.
4. Uncomment the graph or stat function you want to run and comment the rest out.
5. Run `python src/main.py`.

# Files

- `.env`: Stores the configuration, particularly the Parkrun numbers of Parkrunners of interest.
- `.env.example`: Template for `.env`.
- `src/`: Stores source code:
    - `main.py`: An example program that uses the `parkrun` package and Parkrunners of interest in `.env` that can be edited as desired.
    - `tests.py`: Unit tests for tricky functions in the `parkrun` package.
    - `parkrun/`: `parkrun` package source code:
        - `cli.py`: Uses command-line arguments to use the `parkrun` package.
        - `api/`:
            - `cache.py`: Implements `check_cache` and `write_cache` to cache data to not repeatedly hit the website. It intelligently invalidates the cache at the time that results normally come out on Saturdays or Christmas or New Years Day.
            - `parkrun_exception.py`: Custom exception.
            - `scraper.py`: Fetches and parses pages on the parkrun website, caching results.
            - `scraper_runner.py`: Fetches and parses the runner pages on the parkrun website, caching results.
            - `utils.py`: Utility functions used by the rest of the package.
        - `graphs/`:
            - `activity.py`: Graphs the number of parkruns that parkrunners did each month.
            - `event_map.py`: Maps all parkrun events in the world.
            - `times.py`: Graphs the finish times of parkrunners.
        - `models/`: Classes to model Parkrunners, locations, times, results, ...:
            - `age_category.py`: Models the age category of a parkrunner at a fixed time.
            - `age_grade.py`: Models the age grade of a run.
            - `country_collection.py`: Models details of many countries with parkruns.
            - `country.py`: Models details of a country with parkruns.
            - `event_collection.py`: Models many parkrun events.
            - `event_result.py`: Models the finishers and volunteers of a single event at a single location on a single date.
            - `event_runner_result.py`: Models a single finisher's result at a single event at a single location on a single date.
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
