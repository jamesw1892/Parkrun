Objective: to scrape the Parkrun API (or website since the API has been deprecated for years) to get info and use to show stats and graphs.

# Files

## Entry Points

- `Graphs.py`: Uses `Scraper.py` to fetch and graph stats of a given parkrunner.
- `RunnerStats.py`: Uses `Scraper.py` to fetch, calculate, and print stats about a given parkrunner.

## Helpers

- `Cache.py`: Implements `check_cache` and `write_cache` that can be called from `Scraper.py` to store data to `cache/` to not repeatedly hit the website. It intelligently invalidates the cache at the time that results normally come out on Saturdays.
- `Scraper.py`: Fetches and parses pages on the parkrun website using `Cache.py`. I currently only parse the "All Results" table for a particular parkrunner.
- `Tests.py`: Unit tests for tricky functions in other files.
