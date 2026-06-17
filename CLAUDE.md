# Powerball Backend

Flask API that scrapes historical Powerball and Cash4Life lottery drawings and uses them to generate statistically-weighted number predictions.

## Stack

- **Python 3.11**, Flask, SQLAlchemy, Alembic, PostgreSQL
- **Poetry** for dependency management (`package-mode = false` — not a distributable package)
- Docker via `docker-compose.yml`

## Running

```bash
flask run        # dev server
python main.py   # direct
```

Database URL defaults to `postgresql://postgres:password@localhost:5432/powerball`. Override with `DATABASE_URL` env var.

## Project Structure

```
main.py              # Flask app + all routes
controllers/         # Route logic (populate & generate, per game)
models/              # SQLAlchemy models: Drawing, CashForLifeDrawing, Generation
db/
  engine.py          # SQLAlchemy setup, init_db / tear_down_db
  repositories/      # DB query methods (PowerballRepository, etc.)
  migrations/        # Alembic migrations
services/
  fetch_numbers_service/   # HTTP scraping of historical drawings
  generate_numbers_service/ # Weighted random number generation logic
```

## API Routes

| Route | Description |
|---|---|
| `GET /drawings/powerball` | Scrape and store latest Powerball drawings |
| `GET /drawings/cash4life` | Scrape and store latest Cash4Life drawings |
| `GET /generate/powerball/random/v1-v6` | Generate Powerball numbers (see versioning below) |
| `GET /generate/cash_4_life/random/v4-v5` | Generate Cash4Life numbers |
| `GET /generate/powerball/overtime/v4` | Generate across 5 time windows |
| `GET /generate/cash4life/overtime/v4` | Generate across time windows |

Common query params: `drawings=N` (count), `save_generation=True`, `start_date=YYYY-MM-DD`

## Generation Strategy Versions

Each version is a different algorithm — old versions are kept for comparison:

- **v1** — pure random
- **v2** — weighted by all-time historical frequency
- **v3** — weighted with configurable `start_date`
- **v4** — weighted with date range + generative randomness loop
- **v5** — time-decay weighted frequencies (recent drawings weighted higher)
- **v6** — position-specific weights (each ball position has its own frequency table)
- **overtime/v4** — runs v4 across 5 hardcoded time windows (all-time, 5yr, 2yr, 1yr, 6mo)
