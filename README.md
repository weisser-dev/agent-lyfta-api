# agent-lyfta-api

AI-agent helper project for pulling Lyfta training data via API, so WW nutrition data and Lyfta training data can be analyzed together.

## Setup

1. Create `.env` (never commit secrets):

```env
API_KEY=your_real_lyfta_api_key
LYFTA_BASE_URL=https://my.lyfta.app
LYFTA_TIMEOUT=20
```

2. `.env` is ignored via `.gitignore`.

## Available scripts

- `scripts/lyfta_api.py` – shared API client
- `scripts/lyfta_daily_summary.py` – daily workout count/volume/duration
- `scripts/lyfta_exercise_progress.py` – list performed exercises or fetch progress by exercise id
- `references/exercise_name_map.json` – English -> simple German exercise name mapping

## Examples

Daily summary (today):

```bash
python3 scripts/lyfta_daily_summary.py --json
```

Daily summary (specific date):

```bash
python3 scripts/lyfta_daily_summary.py --date 2026-02-22 --json
```

List performed exercises:

```bash
python3 scripts/lyfta_exercise_progress.py --show 30
```

Exercise progress for one exercise:

```bash
python3 scripts/lyfta_exercise_progress.py --exercise-id 2 --duration 365
```

## Notes

- Auth header used by all calls:
  - `Authorization: Bearer <API_KEY>`
- Endpoints used:
  - `GET /api/v1/workouts`
  - `GET /api/v1/workouts/summary`
  - `GET /api/v1/exercises`
  - `GET /api/v1/exercises/progress`
- API limits (per Lyfta docs): 60 req/min, 5000 req/day.
