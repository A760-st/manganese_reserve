install:
	cd backend && python3 -m pip install -r requirements.txt
	cd frontend && npm install
backend:
	cd backend && uvicorn app.main:app --reload --port 8000
frontend:
	cd frontend && npm run dev -- --host 0.0.0.0
 test:
	cd backend && pytest -q
