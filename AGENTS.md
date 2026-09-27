# AGENTS.md

Scrapes the parkrun website and prints stat tables / shows graphs about parkrunners' results. Read `docs/ARCHITECTURE.md` before making structural changes.

## Rules

- Never make requests to the parkrun website (or `images.parkrun.com`) yourself, e.g. with curl or WebFetch.
- Always ask before running `prcli`, `src/main.py` or any other code that calls the package, including fetching the events list, since it may hit the parkrun website or use real parkrunners' data. Unit tests are fine to run without asking.
- Never run code on real parkrunners' data, e.g. the runners in `.env` or `__main__` blocks that fetch runner results, and don't save anything derived from it. Test with made-up data instead (fake results / location names) that doesn't touch the network or cache. If a real-data run seems necessary, ask the user to run it themselves.
- Don't read `.env`; it holds personal parkrunner numbers. `.env.example` shows its format.
- Don't read the cache directory (`platformdirs` `user_cache_dir("parkrun")`, see `api/cache.py`); it contains real parkrunners' results.
- Any new scraping must go through `fetch()` in `api/scraper.py` so it is cached and rate-limited.
- Read settings via the getters in `parkrun/__init__.py` at call time, never at import (see `docs/ARCHITECTURE.md`).

## Tests

- All: `python src/tests.py`
- One: `cd src && python -m unittest tests.TestStreaks` (or `tests.TestStreaks.<method>`)
