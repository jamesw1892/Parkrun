# Parkrun

Objective: to scrape the Parkrun API (or website since the API has been deprecated for years) to get info and use to show stats and graphs.

## Demo

This mainly uses Darren WOOD (parkrunner number 490) because he was the first parkrunner to run 1000 parkruns. These outputs were created 2026-09-26.

### Runner Stats

```text
$ prcli runner_stats 490
Runner stats from all time
+----------------------------+--------------------------------------------------------------------------------------+
|         Parkrunner         |                              Darren WOOD (490) VM40-44                               |
+============================+======================================================================================+
| Num Runs                   | 1017                                                                                 |
+----------------------------+--------------------------------------------------------------------------------------+
| Total Run Time             | 16 days, 8:41:19                                                                     |
+----------------------------+--------------------------------------------------------------------------------------+
| Average Run Time           | 23:10                                                                                |
+----------------------------+--------------------------------------------------------------------------------------+
| First Run                  | 2004-10-09 Bushy Park: 10th, 24:15, 53.20%                                           |
+----------------------------+--------------------------------------------------------------------------------------+
| Latest Run                 | 2026-09-26 Brockwell: 73rd, 22:41, 62.01%                                            |
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
| Most Runs In A Country     | 1001 (UK)                                                                            |
+----------------------------+--------------------------------------------------------------------------------------+
| Countries Visited          | 9                                                                                    |
+----------------------------+--------------------------------------------------------------------------------------+
| Number of Unique Locations | 121                                                                                  |
+----------------------------+--------------------------------------------------------------------------------------+
| Tourism Percentage         | 11.90%                                                                               |
+----------------------------+--------------------------------------------------------------------------------------+
| Consistency                | 88.67%                                                                               |
+----------------------------+--------------------------------------------------------------------------------------+
| International Percentage   | 1.57%                                                                                |
+----------------------------+--------------------------------------------------------------------------------------+
| Runs so far in 2026 (/40)  | 38                                                                                   |
+----------------------------+--------------------------------------------------------------------------------------+
| Streak                     | 18 (2026-05-30 - 2026-09-26)                                                         |
+----------------------------+--------------------------------------------------------------------------------------+
| Floating Streak            | 63 (2007-02-10 - 2008-04-05)                                                         |
+----------------------------+--------------------------------------------------------------------------------------+
| Tourist Streak             | 0                                                                                    |
+----------------------------+--------------------------------------------------------------------------------------+
| Tourist Streak 2           | 2 (2026-09-19 - 2026-09-26)                                                          |
+----------------------------+--------------------------------------------------------------------------------------+
| Floating Tourist Streak    | 6 (2021-07-24 - 2021-08-28)                                                          |
+----------------------------+--------------------------------------------------------------------------------------+
| Floating Tourist Streak 2  | 17 (2020-02-22 - 2021-10-16)                                                         |
+----------------------------+--------------------------------------------------------------------------------------+
| re-index                   | 33                                                                                   |
+----------------------------+--------------------------------------------------------------------------------------+
| p-index                    | 10                                                                                   |
+----------------------------+--------------------------------------------------------------------------------------+
```

### World map of parkruns as multi-coloured dots

![](img/World%20Map%20Parkruns%20Multicoloured%20Dots.png)

## Installation

From the root directory of the repo:

```bash
python3 -m venv pyvenv  # Create a virtual environment in the pyvenv directory
source pyvenv/bin/activate  # Activate the virtual environment
pip install .  # Install the package and its dependencies into the virtual environment
```

Now the `prcli` script is on PATH.

## Usage

### Command-Line Interface

Run `prcli` (same as running `python src/parkrun/cli.py`). It takes command-line arguments and has help text.

You can use the names (case in-sensitive) in the `.env` file that you may have created as below to use their numbers, e.g.:

```bash
prcli runner_stats me
```

### Editing Main.py to call library

1. Copy the file `.env.example` and name the copy `.env`.
2. Edit it to include the parkrun numbers you're interested in (numbers can be found on barcodes, results emails and online at https://www.parkrun.org.uk/). It is often displayed following an 'A' but don't include the 'A' in the `.env` file. Also adjust other settings stored in `.env` as desired.
3. Edit `src/main.py` to change which parkrunner(s) to act on and the start and end dates for graphs.
4. Uncomment the graph or stat function you want to run and comment the rest out.
5. Run `python src/main.py`.

## Configuration

Settings are read from `.env` (copy `.env.example`) and most can be overridden with `prcli` flags:

| Setting | Default | Meaning |
|---|---|---|
| `PARKRUNNER_<NAME>` | | Parkrun number of a parkrunner of interest, usable as `<name>` on the command line |
| `TABLE_MAX_WIDTH` | 180 | Maximum width of printed tables in characters |
| `CACHE_FORCE_VALID` | false | Use cached pages even if they may be out of date |
| `CACHE_FORCE_INVALID` | false | Re-fetch pages even if the cache is up to date |
| `MIN_SECS_BETWEEN_QUERIES` | 5 | Minimum seconds between requests to the parkrun website |
| `MIN_LOG_LEVEL` | WARNING | Minimum level of log messages to show |

## How it works

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for how the code is structured, how caching works and how to run the tests.
