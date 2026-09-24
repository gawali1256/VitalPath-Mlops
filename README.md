# VitalPath

A small **MLOps** health lab you can run on Docker Desktop. The app takes age, gender, height, weight, activity, sleep, and a goal. It calculates **BMI**, estimates **lifestyle risk** with a trained model, and suggests a weekly exercise plan.

This is a teaching project, not medical advice.

## What you get

| Piece | Role |
| --- | --- |
| React frontend on port 3000 | Form and results dashboard |
| FastAPI backend on port 8000 | BMI math, model scoring, exercise rules |
| Local model registry | Versioned `joblib` bundle + `metadata.json` |
| MLflow on port 5000 | Experiment tracker for training runs |
| GitHub Actions | Test, train, quality gate, Docker image build |
| Docker Compose | One-command local production-like stack |

## How a request works

1. The browser posts your measurements to `/api/assess`.
2. The API computes BMI with the standard formula: `weight_kg / (height_m ^ 2)`.
3. The same inputs are encoded into numeric features and scored by two Random Forest models:
   - **risk_level**: low / moderate / high
   - **recommended_intensity**: gentle / moderate / vigorous
4. A rule catalog maps BMI category + intensity + goal to concrete exercises.
5. The API writes a JSON line to `logs/predictions.jsonl` so you can audit what the model served.

BMI is deterministic. The models add the MLOps piece: train, version, evaluate, then serve.

## Local architecture (Docker Desktop)

```
Browser
   │
   ▼
frontend :3000  (nginx + React)
   │  /api/*
   ▼
api :8000  (FastAPI)
   ├── BMI + exercise rules
   ├── loads /models/current/model.joblib
   └── appends /logs/predictions.jsonl
          ▲
trainer / first API boot
          │
          ├── writes model registry
          └── logs metrics to mlflow :5000
```

Open these after `docker compose up --build`:

- App: http://localhost:3000
- API docs: http://localhost:8000/docs
- MLflow: http://localhost:5000

## Run it

### Option A — Docker Desktop (recommended)

Install Docker Desktop, then from this folder:

```powershell
docker compose up --build
```

The API image trains a model on first boot if `mlops/models/current/model.joblib` is missing. Later starts reuse that file.

Retrain on demand:

```powershell
docker compose --profile train run --rm trainer
docker compose restart api
```

Stop:

```powershell
docker compose down
```

### Option B — without Docker

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
$env:PYTHONPATH = "."
$env:MODEL_PATH = "mlops/models/current/model.joblib"
$env:LOG_PATH = "logs/predictions.jsonl"
python mlops/train.py
uvicorn backend.app.main:app --reload --port 8000
```

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

The form is already served by the API at http://localhost:8000. Optional React/Vite UI (needs Node):

```powershell
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173. Vite proxies `/api` to the backend.

## CI/CD

`.github/workflows/ci-cd.yml` runs on every push and pull request:

1. Install Python dependencies
2. Run unit and API tests
3. Train a fresh model
4. Fail the job if holdout accuracy drops below the gate
5. Build the `api` and `frontend` Docker images

That is the usual MLOps loop: **code quality → train → evaluate → package**.

## Project map

```
mlops/           training data, train.py, evaluate.py, model registry
backend/         FastAPI app and tests
frontend/        React form and results
.github/         CI/CD workflow
docker-compose.yml
```
