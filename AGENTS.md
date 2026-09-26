# AGENTS.md

Scrapes the parkrun website and prints stat tables / shows graphs about parkrunners' results. Read `docs/ARCHITECTURE.md` before making structural changes.

## Rules

- Never make requests to the parkrun website (or `images.parkrun.com`) yourself, e.g. with curl or WebFetch.
- Always ask before running `prcli`, `src/main.py` or any other code that calls the package, since it may hit the parkrun website. Unit tests are fine to run without asking.
- Don't read `.env`; it holds personal parkrunner numbers. `.env.example` shows its format.
- Any new scraping must go through `fetch()` in `api/scraper.py` so it is cached and rate-limited.
- Read settings via the getters in `parkrun/__init__.py` at call time, never at import (see `docs/ARCHITECTURE.md`).

## Tests

- All: `python src/tests.py`
- One: `cd src && python -m unittest tests.TestStreaks` (or `tests.TestStreaks.<method>`)
