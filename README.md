# Manganese Reserve Intelligence MVP

A locally runnable decision-support platform for **manganese prospectivity**, production forecasting, shortfall risk, explainability, recommendations, and optimization scenarios.

> **Scientific boundary:** this MVP predicts exploration potential/prospectivity from demo geological, subsurface, and environmental proxy features. It does not detect underground reserves from satellite imagery and it never claims certified mineral reserves.

## Provenance
All included records are explicitly labelled `DEMO DATA` / `SYNTHETIC DATA`. They are deterministic fixtures for testing the pipeline and are not MOIL operational data, live satellite observations, or certified geological information.

## Quick start (Docker)
```bash
docker compose up --build
```
- Dashboard: http://localhost:3000
- API: http://localhost:8000
- API docs: http://localhost:8000/docs

## Quick start (without Docker)
### Backend
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
### Frontend
```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```
Set `VITE_API_URL=http://localhost:8000` if the API is not on the default port.

## Tests
```bash
cd backend && pytest -q
cd ../frontend && npm install && npm run build
```

## Included modules
- `/dashboard`, `/reserves`, `/production`, `/shortfall`, `/satellite`, `/equipment`, `/recommendations`, `/optimization`, `/models`, `/data`, `/settings`
- FastAPI `/api/v1` endpoints for all decision-support flows
- Deterministic prospectivity score, production forecast, shortfall risk, recommendation, and optimization logic
- Provenance, model version, timestamps, prediction IDs, and audit events on outputs
- CSV ingestion validation utility and fixture data

## Limitations
This is an MVP designed to be plugged into authorized datasets later. Production use requires validated drill logs, samples, geological models, operational data, satellite provider integrations, authentication/RBAC, PostGIS, model training artifacts, spatial/temporal validation, and review by qualified geologists and mine planners. See `docs/LIMITATIONS.md`.
