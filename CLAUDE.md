# Powerball Backend

Flask API that scrapes historical Powerball drawings from powerball.com and uses them to generate statistically-weighted number predictions via multiple algorithms.

## Stack

- **Python 3.11**, Flask, SQLAlchemy, Alembic, PostgreSQL
- **Poetry** for dependency management (`package-mode = false` — not a distributable package)
- **BeautifulSoup4** for HTML scraping
- Docker via `docker-compose.yml` and `Dockerfile`

## Running

```bash
flask run        # dev server
python main.py   # direct
```

Database URL defaults to `postgresql://postgres:password@localhost:5432/powerball`. Override with `DATABASE_URL` env var.

## Project Structure

```
main.py                         # Flask app + active routes
constants.py                    # Draw schedule dates, ball ranges, legacy v2 ranges
tasks.py                        # invoke task stubs (currently empty)
queries.sql                     # Ad-hoc SQL reference queries

controllers/
  generate.py                   # v6 endpoint logic (position-specific weights, active default)
  generate_multi.py             # /generate/powerball/multi — algorithm-picker endpoint
  generate_archive.py           # v1–v5 + overtime logic (kept for comparison)
  populate.py                   # Thin wrapper calling fetch_numbers.populate_drawings()
  routes_archive.py             # Blueprint registering v1–v5 + overtime routes

models/
  drawing.py                    # Drawing — one row per historical drawing
  drawing_metadata.py           # DrawingMetadata — FK to drawings (future use)
  generations.py                # Generation — saved generated picks

db/
  engine.py                     # SQLAlchemy engine, session, Base, init_db/tear_down_db
  repositories/
    drawings.py                 # DrawingsRepository — all drawing queries
    generations.py              # GenerationRepository — saved picks queries
  migrations/                   # Alembic migrations

services/
  fetch_numbers.py              # HTTP scraping, retry logic, populate_drawings()
  parser.py                     # BeautifulSoup HTML → Drawing object
  generate_numbers.py           # Legacy weighted frequency helpers (v4–v6)
  algorithms.py                 # All modern algorithm factories + registry + constraints

tests/
  test_fetch_and_save.py
```

## API Routes

### Active routes (main.py)

| Route | Description |
|---|---|
| `GET /` | Health check |
| `GET /drawings/powerball` | Scrape powerball.com and store new drawings |
| `GET /generate/powerball/random` | Generate using v6 (position-specific weights) |
| `GET /generate/powerball/multi` | Generate using named or random algorithm from registry |

### Archive routes (routes_archive.py blueprint)

| Route | Description |
|---|---|
| `GET /generate/powerball/random/v1` | Pure random |
| `GET /generate/powerball/random/v2` | Frequency-weighted (all-time) |
| `GET /generate/powerball/random/v3` | Frequency-weighted with `start_date` |
| `GET /generate/powerball/random/v4` | v3 + generative randomness loop |
| `GET /generate/powerball/random/v5` | Time-decay weighted |
| `GET /generate/powerball/overtime` | v4 across 5 hardcoded time windows |

### Common query params

- `drawings=N` — number of picks to generate (default 1)
- `save_generation=True` — persist picks to the `generations` table
- `start_date=YYYY-MM-DD` — filter historical data (v3/v4)
- `constraints=sum_range,odd_even` — apply statistical constraints (multi endpoint)
- `algorithm=<name>` — specify algorithm by name (multi endpoint; default `random`)

## Generation Strategy Versions

Older versions are kept in `generate_archive.py` for comparison. New development goes into `algorithms.py`.

### Legacy (generate_archive.py / generate_numbers.py)

- **v1** — pure random
- **v2** — weighted by all-time historical frequency
- **v3** — weighted with configurable `start_date`
- **v4** — weighted with date range + generative randomness loop (`GENERATIVE_RANDOMNESS_RANGE=100`)
- **v5** — time-decay weighted (exponential decay, `half_life_days=365`)
- **v6** — position-specific weights (each ball position has its own frequency table; current default for `/generate/powerball/random`)
- **overtime/v4** — runs v4 across 5 hardcoded time windows (all-time, 5yr, 2yr, 1yr, 6mo)

### Modern algorithms (services/algorithms.py)

All algorithms are factory functions (`make_*`) that take `drawings` and return a named callable `() → (white_balls, powerball)`. `build_registry(drawings)` instantiates them all.

| Algorithm name | Description |
|---|---|
| `hot_numbers` | Frequency-weighted over trailing 12 months |
| `cold_numbers` | Inverse frequency over trailing 12 months (gambler's fallacy) |
| `position_specific` | Separate frequency table per ball position |
| `markov_chain` | Each position conditioned on the previous via transition frequencies |
| `hot_pairs` | Co-occurrence clustering; anchors on strongest historical pairs |
| `gap_theory` | Weights each number by days since last appearance |
| `winning_ticket` | Frequency table built only from drawings where `winner=True` |
| `calendar_conditioned` | Frequency table from draws on today's day-of-week |
| `state_conditioned_<X>` | Frequency table from wins in a randomly selected state |
| `drought_breaker` | Shifts weighting based on whether current drought exceeds historical average |
| `ensemble_voting` | Tallies votes from all other algorithms; picks most-voted numbers |
| `pure_chaos` | True uniform random, no history |

### Constraints (multi endpoint only)

Applied via `make_constrained(algo, constraint_factories)` with up to 300 retries before falling back unconstrained.

- `sum_range` — white balls must sum within ±1 std dev of historical mean
- `odd_even` — odd count + high-count profile must match a historically-weighted target

## Data Model

**Drawing** (`drawings` table): one row per historical Powerball draw. Fields: `first_ball`–`fifth_ball`, `power_ball`, `date_drawn`, `winner` (bool), `day_of_week` (weekday int 0–6), `winner_state` (string or null).

**Generation** (`generations` table): saved generated picks. Same ball fields plus `date_generated`.

**DrawingMetadata** (`drawing_metadata` table): FK to drawings; currently unused beyond schema.

## Scraping

`services/fetch_numbers.py` scrapes `https://www.powerball.com/draw-result?gc=powerball&date=YYYY-MM-DD` one drawing at a time with:
- 1–20 second random sleep between requests
- Up to 3 retries with exponential backoff (30s base) on parse errors
- Date mismatch detection (skips if returned date ≠ requested date)
- Deduplication via `DrawingsRepository.get_by(date_drawn=...)`

Draw schedule (from `constants.py`):
- Pre-2021-08-23: Wed + Sat only
- 2021-08-23 onward: Mon + Wed + Sat

## Key Constants

- `HISTORICAL_START_DATE` = 1997-11-01 (first drawing ever)
- `LAST_BALL_COUNT_CHANGE_DATE` = 2015-10-04 (white balls expanded to 1–69, powerball to 1–26)
- `NEXT_START_DATE` = 2023-03-06 (default populate start date)
- `WHITE_BALL_RANDOMNESS_RANGE` = 69, `POWER_BALL_RANDOMNESS_RANGE` = 26
