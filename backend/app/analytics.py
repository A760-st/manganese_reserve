from datetime import datetime, timezone
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models import (
    MineZoneModel, DrillHoleModel, GeologicalObsModel, SatelliteObsModel,
    ProductionModel, EquipmentModel, DowntimeLogModel, BlastRecordModel,
    WeatherRecordModel, RecommendationModel, ModelRegistryModel
)

PROVENANCE = {
    "label": "DEMO DATA / SYNTHETIC DATA",
    "source": "Local SQLite Database (Seeded from synthetic fixtures)",
    "is_operational": False
}

def get_prospectivity_for_zones(db: Session):
    zones = db.query(MineZoneModel).all()
    results = []
    
    for z in zones:
        # Aggregated drill hole assay average
        dh_avg = db.query(func.avg(DrillHoleModel.mn_assay_pct))\
            .filter(DrillHoleModel.zone_id == z.zone_id).scalar() or 30.0
        drill_evidence = min(1.0, max(0.2, (dh_avg - 15.0) / 30.0))
        
        # Geological proxy
        geo_avg = db.query(func.avg(GeologicalObsModel.mn_grade_proxy))\
            .filter(GeologicalObsModel.zone_id == z.zone_id).scalar() or 0.30
        geology_signal = min(1.0, max(0.2, geo_avg / 0.50))
        
        # Satellite spectral proxy
        sat_avg = db.query(func.avg(SatelliteObsModel.spectral_proxy))\
            .filter(SatelliteObsModel.zone_id == z.zone_id).scalar() or 0.50
        
        # Model formula: prospectivity score
        prospectivity = round(0.45 * drill_evidence + 0.35 * geology_signal + 0.20 * sat_avg, 2)
        confidence = round(min(0.95, 0.50 + 0.40 * drill_evidence), 2)
        grade_proxy = round(dh_avg / 50.0, 2)
        
        results.append({
            "id": z.zone_id,
            "name": z.name,
            "lat": z.latitude,
            "lon": z.longitude,
            "prospectivity": prospectivity,
            "confidence": confidence,
            "grade_proxy": grade_proxy,
            "drill_evidence": round(drill_evidence, 2),
            "ndvi": round(random_sat_ndvi(db, z.zone_id), 2),
            "soil_moisture": round(random_sat_moisture(db, z.zone_id), 2),
            "elevation": z.elevation_m,
            "slope": z.slope_deg
        })
        
    return results

def random_sat_ndvi(db: Session, zone_id: str):
    res = db.query(func.avg(SatelliteObsModel.ndvi)).filter(SatelliteObsModel.zone_id == zone_id).scalar()
    return res if res else 0.35

def random_sat_moisture(db: Session, zone_id: str):
    res = db.query(func.avg(SatelliteObsModel.soil_moisture)).filter(SatelliteObsModel.zone_id == zone_id).scalar()
    return res if res else 0.40

def calculate_zone_explanation(db: Session, zone_id: str):
    # Drill & Geology contributions
    dh_avg = db.query(func.avg(DrillHoleModel.mn_assay_pct)).filter(DrillHoleModel.zone_id == zone_id).scalar() or 30.0
    drill_evidence = min(1.0, max(0.2, (dh_avg - 15.0) / 30.0))
    geo_avg = db.query(func.avg(GeologicalObsModel.mn_grade_proxy)).filter(GeologicalObsModel.zone_id == zone_id).scalar() or 0.30
    sat_avg = db.query(func.avg(SatelliteObsModel.spectral_proxy)).filter(SatelliteObsModel.zone_id == zone_id).scalar() or 0.50
    
    return [
        {"feature": "drill_evidence", "contribution": round(0.45 * drill_evidence, 2), "direction": "positive"},
        {"feature": "geology_signal", "contribution": round(0.35 * (geo_avg / 0.50), 2), "direction": "positive"},
        {"feature": "spectral_proxy", "contribution": round(0.20 * sat_avg, 2), "direction": "positive"},
        {"feature": "slope_angle", "contribution": -0.06, "direction": "negative"}
    ]

def get_production_forecast(db: Session):
    # Recent production history
    recent_prods = db.query(ProductionModel.date, func.sum(ProductionModel.actual_tonnes).label("actual"), func.sum(ProductionModel.target_tonnes).label("target"))\
        .group_by(ProductionModel.date)\
        .order_by(ProductionModel.date.desc())\
        .limit(14).all()
    
    recent_prods.reverse()
    
    if recent_prods:
        avg_actual = round(float(np.mean([p.actual for p in recent_prods])), 1)
        avg_target = round(float(np.mean([p.target for p in recent_prods])), 1)
    else:
        avg_actual = 875.0
        avg_target = 930.0
        
    expected_gap = max(0.0, round(avg_target - avg_actual, 1))
    
    series = []
    for i in range(7):
        series.append({
            "day": i + 1,
            "forecast": round(avg_actual + (i % 3) * 8 - (i % 2) * 5, 1),
            "target": round(avg_target, 1)
        })
        
    return {
        "horizon": "7 days",
        "expected_production": avg_actual,
        "target_production": avg_target,
        "expected_gap": expected_gap,
        "lower_bound": round(avg_actual * 0.93, 1),
        "upper_bound": round(avg_actual * 1.07, 1),
        "confidence": 0.74,
        "series": series
    }

def calculate_shortfall_risk(db: Session, equipment_avail_delta: float = 0.0, rainfall_delta: float = 0.0):
    # DB Equipment & Weather signals
    avg_avail = db.query(func.avg(EquipmentModel.availability)).scalar() or 0.84
    recent_rain = db.query(func.avg(WeatherRecordModel.rainfall_mm)).filter(WeatherRecordModel.rainfall_mm > 0).limit(7).scalar() or 12.0
    
    base_prob = 0.64
    adj_prob = max(0.05, min(0.98, base_prob - 0.45 * equipment_avail_delta + 0.25 * rainfall_delta))
    level = "CRITICAL" if adj_prob >= 0.85 else "HIGH" if adj_prob >= 0.65 else "MEDIUM" if adj_prob >= 0.40 else "LOW"
    
    expected_shortfall = round(55.0 + 90.0 * adj_prob, 1)
    
    contributing_factors = [
        {"factor": "equipment availability", "model_contribution": round(0.34 * (1.0 - avg_avail), 2)},
        {"factor": "blast delay proxy", "model_contribution": 0.22},
        {"factor": "rainfall / soil moisture", "model_contribution": round(0.15 + 0.10 * (recent_rain / 50.0), 2)},
        {"factor": "haulage capacity constraint", "model_contribution": 0.11}
    ]
    
    return {
        "probability": round(adj_prob, 3),
        "expected_shortfall_tonnes": expected_shortfall,
        "risk_level": level,
        "contributing_factors": contributing_factors,
        "note": "Model risk contributions are based on synthetic operational logs and weather data."
    }

def get_equipment_intelligence(db: Session):
    eq_list = db.query(EquipmentModel).all()
    results = []
    for e in eq_list:
        results.append({
            "id": e.equipment_id,
            "type": e.type,
            "mine_id": e.mine_id,
            "zone_id": e.zone_id,
            "capacity_t": e.capacity_t,
            "availability": round(e.availability, 2),
            "utilization": round(e.utilization, 2),
            "operating_hours": e.operating_hours,
            "downtime_hours": e.downtime_hours,
            "status": e.status
        })
    return results

def get_recommendations_from_db(db: Session):
    recs = db.query(RecommendationModel).all()
    results = []
    for r in recs:
        results.append({
            "id": r.id,
            "action": r.action,
            "reason": r.reason,
            "zone": r.zone,
            "equipment": r.equipment,
            "expected_impact_tonnes": r.expected_impact_tonnes,
            "confidence": r.confidence,
            "status": r.status
        })
    return results

def run_optimization_scenario(db: Session, equip_delta: float = 0.0, rain_delta: float = 0.0):
    baseline_prod = 875.0
    baseline_shortfall = 55.0
    
    optimized_prod = round(baseline_prod + max(0.0, 38.0 - 25.0 * rain_delta + 35.0 * equip_delta), 1)
    optimized_shortfall = max(0.0, round(930.0 - optimized_prod, 1))
    
    return {
        "baseline_plan": {
            "expected_production": baseline_prod,
            "expected_shortfall": baseline_shortfall,
            "idle_hours": 18.0
        },
        "optimized_plan": {
            "expected_production": optimized_prod,
            "expected_shortfall": optimized_shortfall,
            "idle_hours": 12.0,
            "equipment_utilization": round(min(0.95, 0.84 + 0.10 * equip_delta), 2)
        },
        "objective": "Minimize expected shortfall subject to equipment fleet availability constraints",
        "scenario_assumptions": {
            "equipment_availability_delta": equip_delta,
            "rainfall_delta": rain_delta
        },
        "constraint_violations": []
    }
