# Deployment

Use `docker compose up --build` for local deployment. In production, set secrets through the deployment environment, replace demo repository adapters, restrict CORS, use PostgreSQL/PostGIS, add authentication/RBAC, and place the frontend behind TLS. Never commit `.env`, credentials, API keys, or private keys.
