# My Workout

Full‑stack workout tracker with React (frontend) and FastAPI (backend).

## Key Features

- Authentication & Profile: email/password login, JWT, `GET/PATCH /api/users/me`
- Social: follow/unfollow, activity feed (cursor pagination), likes, comments
- Analytics: PR trend (Epley 1RM), muscle‑group volume, exercise‑specific detail
- AI Coach (rule‑based MVP): recommendations from recent volume/frequency/PR trend
- Responsive UI: mobile drawer navigation, responsive fonts/layout

## Project Structure

- `backend/`: FastAPI API, SQLite (users, social) + JSON (workouts) analytics
- `frontend/`: React app (Create React App)
- `docker-compose.yml`: optional local orchestration

## Setup

### 1) Backend (DB init + run)

```
cd backend
python init_db.py   # creates DB and applies migrations (001–005)
cd ..
python run.py       # http://127.0.0.1:8000
```

Optional (AI chat endpoints only): set environment variables
- `OPENAI_API_KEY`, `OPENAI_BASE_URL` (default `https://openrouter.ai/api/v1`), `OPENAI_MODEL`

### 2) Frontend

```
cd frontend
npm install
npm start           # http://localhost:3000
```

## API Overview (Selected)

- Auth: `POST /api/auth/register`, `POST /api/auth/login`
- Profile: `GET /api/users/me`, `PATCH /api/users/me`
- Social: `POST/DELETE /api/social/follow`, `GET /api/social/feed`,
  `POST/DELETE /api/social/like`, `POST/GET/DELETE /api/social/comment{,s}`
- Analytics: `GET /api/analytics/pr-trend`, `GET /api/analytics/muscle-volume-range`,
  `GET /api/analytics/exercise-detail`
- AI Coach: `GET /api/coach/recommendations?days=30`

## Testing

```
cd backend
python -m unittest discover -s backend -p "test_*.py"
```

## Docker (optional)

```
docker compose up --build
```

## Notes

- Users/social data: SQLite (`backend/data/workout.db`) via migrations in `backend/migrations/`
- Workouts analytics data: JSON (`backend/storage.py`) — tests override the data dir
- Cursor‑based feed pagination is supported
- Recommendations are rule‑based; no external AI calls required
