# Architecture

The repository separates `frontend/`, `backend/`, `data/`, and `docs/`. The React client consumes FastAPI REST endpoints. The backend currently uses a deterministic in-memory demo repository so a new user can run the system without PostgreSQL or provider credentials. A production adapter should replace this repository with PostgreSQL/PostGIS and authenticated provider clients.

Pipeline: data validation → feature assembly → prospectivity scoring → production forecast → shortfall classification → explanations → reviewable recommendations → constrained scenario calculation → dashboard.
