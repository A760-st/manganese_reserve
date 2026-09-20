# API documentation

FastAPI publishes interactive OpenAPI docs at `/docs`. Core endpoints include `GET /api/v1/overview`, `GET /api/v1/reserves/map`, `POST /api/v1/reserves/predict`, `GET /api/v1/production/forecast`, `POST /api/v1/shortfall/predict`, `GET /api/v1/recommendations`, `POST /api/v1/optimization/run`, `GET /api/v1/models`, `GET /api/v1/data-quality`, and `POST /api/v1/data/validate`.

Every response includes provenance, timestamp, prediction ID, and dataset/model metadata where applicable.
