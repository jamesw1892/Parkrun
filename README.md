Objective: to scrape the Parkrun API (or website since the API has been deprecated for years) to get info and use to show stats and graphs.

# Usage

1. Copy the file `.env.example` and name the copy `.env`
2. Edit it to include the parkrun numbers you're interested in (numbers can be found on barcodes, results emails and online at https://www.parkrun.org.uk/). It is often displayed following an 'A' but don't include the 'A' in the `.env` file.
3. Edit `Main.py` to change which parkrunner(s) to act on and the start and end dates for graphs.
4. Uncomment the graph or stat function you want to run and comment the rest out.
5. Run `python Main.py`

# Files

## Graph and Stat Functions

- `RunnerStats.py`: Print a table with statistics about parkrunners side-by-side.
- `CommonRunComparison.py`: Print a table with a side-by-side comparison of runs that parkrunners did together.
- `MostCommon.py`: Print a table with a thing about the parkrunner sorted by how many times that thing occurred, side-by-side for each given parkrunner.
- `ActivityGraph.py`: Graphs the number of parkruns that parkrunners did each month.
- `TimeGraph.py`: Graphs the finish times of parkrunners.

## Models

We model objects in the `models/` directory:

- `age_grade.py`: Models the age grade of a run.
- `pb.py`: Models whether a run is a personal best.
- `position.py`: Models the finish position of a run.
- `runner_result.py`: Models a run.
- `runner.py`: Models a runner with their number, name and all their runs.
- `time.py`: Models the finish time of a run or any other parkrun-related time, e.g. total/average finish time.

## Helpers

- `Cache.py`: Implements `check_cache` and `write_cache` that can be called from `Scraper.py` to store data to `cache/` to not repeatedly hit the website. It intelligently invalidates the cache at the time that results normally come out on Saturdays.
- `Scraper.py`: Fetches and parses pages on the parkrun website using `Cache.py`. I currently only parse the "All Results" table for a particular parkrunner.
- `Tests.py`: Unit tests for tricky functions in other files.
