.PHONY: train evaluate test up down logs local-api local-web

train:
	python mlops/train.py

evaluate:
	python mlops/evaluate.py

test:
	pytest -q

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f api frontend mlflow

local-api:
	set PYTHONPATH=.&& uvicorn backend.app.main:app --reload --port 8000

local-web:
	cd frontend && npm install && npm run dev
