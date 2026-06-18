# Powerball Backend

Flask API that scrapes historical Powerball drawings and generates statistically-weighted number predictions using multiple algorithms.

## Requirements

- Python 3.11+
- PostgreSQL
- [Poetry](https://python-poetry.org/docs/#installation)

## Setup

### 1. Install dependencies

```bash
poetry install
```

### 2. Configure the database

The app connects to PostgreSQL at `postgresql://postgres:password@localhost:5432/powerball` by default. Override with an env var:

```bash
export DATABASE_URL=postgresql://user:password@host:5432/dbname
```

### 3. Run migrations

```bash
poetry run alembic upgrade head
```

### 4. Start the server

```bash
poetry run flask run
```

The API will be available at `http://localhost:5000`.

---

## Docker (recommended)

Starts the API and a PostgreSQL database together. Migrations run automatically on startup.

```bash
docker compose up --build
```

API available at `http://localhost:5001`.

---

## Populating data

Scrape historical drawings from powerball.com and store them:

```
GET /drawings/powerball
```

This walks forward from the configured start date, fetching one drawing at a time with random delays between requests. It skips dates already in the database.

---

## Generating numbers

### Default (position-specific weights)

```
GET /generate/powerball/random?drawings=5
```

### Multi-algorithm endpoint

```
GET /generate/powerball/multi?drawings=3&algorithm=hot_numbers
GET /generate/powerball/multi?drawings=5&algorithm=random&constraints=sum_range,odd_even
```

**`algorithm`** — one of: `hot_numbers`, `cold_numbers`, `position_specific`, `markov_chain`, `hot_pairs`, `gap_theory`, `winning_ticket`, `calendar_conditioned`, `state_conditioned`, `drought_breaker`, `ensemble_voting`, `pure_chaos`, or `random` (picks randomly each time).

**`constraints`** — optional comma-separated filters applied after generation:
- `sum_range` — white balls sum within ±1 std dev of the historical mean
- `odd_even` — odd/high count profile matches a historically-weighted target

### Legacy versioned endpoints

```
GET /generate/powerball/random/v1   # pure random
GET /generate/powerball/random/v2   # all-time frequency weighted
GET /generate/powerball/random/v3   # frequency weighted with start_date
GET /generate/powerball/random/v4   # v3 + generative randomness loop
GET /generate/powerball/random/v5   # time-decay weighted
GET /generate/powerball/overtime    # v4 across 5 time windows
```

### Common query params

| Param | Default | Description |
|---|---|---|
| `drawings` | `1` | Number of picks to generate |
| `save_generation` | `False` | Persist picks to the `generations` table |
| `start_date` | `2015-10-03` | Filter historical data to this date onward (v3/v4) |

---

## Running tests

```bash
poetry run pytest
```
