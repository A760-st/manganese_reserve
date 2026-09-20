import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_health(): assert client.get('/health').json()['status']=='ok'
def test_reserve_map_has_provenance():
    r=client.get('/api/v1/reserves/map'); assert r.status_code==200; assert 'provenance' in r.json(); assert len(r.json()['data'])>=4
def test_prediction_boundaries():
    r=client.post('/api/v1/reserves/predict',json={'drill_evidence':1,'geology_signal':1,'spectral_proxy':1}); assert r.json()['data']['prospectivity_score']==1.0
def test_forecast_separates_target():
    d=client.get('/api/v1/production/forecast').json()['data']; assert d['expected_production'] != d['target_production']
def test_optimization_response():
    d=client.post('/api/v1/optimization/run',json={'equipment_availability_delta':-0.2}).json()['data']; assert 'baseline_plan' in d and 'optimized_plan' in d
def test_data_sources_registry():
    r=client.get('/api/v1/data-sources'); assert r.status_code==200; assert len(r.json()['data'])>=5
