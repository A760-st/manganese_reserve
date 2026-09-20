import os
import sys
import random
import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

ROOT_DIR = BACKEND_DIR.parent
DATA_DEMO_DIR = ROOT_DIR / "data" / "demo"
DATA_DEMO_DIR.mkdir(parents=True, exist_ok=True)

from app.db.database import engine, Base, SessionLocal
from app.db.models import (
    MineModel, MineZoneModel, GeologicalObsModel, DrillHoleModel,
    OreSampleModel, ProductionModel, EquipmentModel, DowntimeLogModel,
    MaintenanceModel, BlastRecordModel, WeatherRecordModel, SatelliteObsModel,
    ModelRegistryModel, RecommendationModel
)

PROVENANCE_TEXT = "DEMO DATA / SYNTHETIC DATA"

def generate_csvs():
    print("--> Generating synthetic demonstration CSV files in data/demo/...")
    random.seed(42)

    # 1. Mines
    mines = [
        {"mine_id": "MINE-01", "name": "Dongri Buzurg Prospect", "latitude": 21.6550, "longitude": 85.9550, "state": "Maharashtra", "country": "India", "status": "OPERATIONAL", "provenance": PROVENANCE_TEXT},
        {"mine_id": "MINE-02", "name": "Mansar Ridge Mine", "latitude": 21.6420, "longitude": 85.9380, "state": "Maharashtra", "country": "India", "status": "OPERATIONAL", "provenance": PROVENANCE_TEXT},
        {"mine_id": "MINE-03", "name": "Bala Hill Exploration Area", "latitude": 21.6250, "longitude": 85.9470, "state": "Madhya Pradesh", "country": "India", "status": "EXPLORATION", "provenance": PROVENANCE_TEXT},
        {"mine_id": "MINE-04", "name": "Chikla Spur Mine", "latitude": 21.6490, "longitude": 85.9120, "state": "Maharashtra", "country": "India", "status": "OPERATIONAL", "provenance": PROVENANCE_TEXT},
    ]
    with open(DATA_DEMO_DIR / "mines.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=mines[0].keys())
        writer.writeheader()
        writer.writerows(mines)

    # 2. Mine Zones
    zones = []
    zone_names_pool = [
        ("ZONE-A", "Eastern Ridge", 21.6550, 85.9550, 412.0, 17.0, 3.2),
        ("ZONE-B", "Central Bench", 21.6420, 85.9380, 386.0, 12.0, 2.8),
        ("ZONE-C", "South Cut", 21.6250, 85.9470, 351.0, 9.0, 2.1),
        ("ZONE-D", "West Spur", 21.6490, 85.9120, 398.0, 14.0, 2.5),
        ("ZONE-E", "North Extension", 21.6610, 85.9610, 425.0, 19.0, 1.9),
    ]
    for m in mines:
        for z_code, z_label, lat_off, lon_off, elev, slope, area in zone_names_pool:
            zid = f"{m['mine_id']}-{z_code}"
            zones.append({
                "zone_id": zid,
                "mine_id": m["mine_id"],
                "name": f"{m['name']} - {z_label}",
                "latitude": round(m["latitude"] + random.uniform(-0.01, 0.01), 4),
                "longitude": round(m["longitude"] + random.uniform(-0.01, 0.01), 4),
                "elevation_m": round(elev + random.uniform(-15, 15), 1),
                "slope_deg": round(slope + random.uniform(-2, 2), 1),
                "area_sqkm": area
            })
    with open(DATA_DEMO_DIR / "mine_zones.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=zones[0].keys())
        writer.writeheader()
        writer.writerows(zones)

    # 3. Geological Observations
    lithologies = ["Gondite", "Manganiferous Quartzite", "Schist", "Chert", "Gneiss"]
    formations = ["Sausar Group", "Mansi Formation", "Chikla Member", "Tirodi Gneiss"]
    geo_obs = []
    start_date = datetime(2025, 10, 1)
    for i in range(120):
        z = random.choice(zones)
        dt_str = (start_date + timedelta(days=i * 3)).strftime("%Y-%m-%d")
        geo_obs.append({
            "obs_id": f"GEO-OBS-{i+1001}",
            "mine_id": z["mine_id"],
            "zone_id": z["zone_id"],
            "date": dt_str,
            "lithology": random.choice(lithologies),
            "formation": random.choice(formations),
            "structure_proximity_m": round(random.uniform(50, 1500), 1),
            "mn_grade_proxy": round(random.uniform(0.15, 0.48), 3),
            "elevation": z["elevation_m"],
            "slope": z["slope_deg"]
        })
    with open(DATA_DEMO_DIR / "geological_observations.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=geo_obs[0].keys())
        writer.writeheader()
        writer.writerows(geo_obs)

    # 4. Drill Holes & 5. Ore Samples
    drill_holes = []
    ore_samples = []
    sample_counter = 10001
    for i in range(240):
        z = random.choice(zones)
        hid = f"DH-{i+2001}"
        d_date = (start_date + timedelta(days=i * 1.5)).strftime("%Y-%m-%d")
        mn_assay = round(random.uniform(22.0, 46.0), 2)
        drill_holes.append({
            "hole_id": hid,
            "mine_id": z["mine_id"],
            "zone_id": z["zone_id"],
            "latitude": round(z["latitude"] + random.uniform(-0.005, 0.005), 5),
            "longitude": round(z["longitude"] + random.uniform(-0.005, 0.005), 5),
            "depth_m": round(random.uniform(60, 280), 1),
            "dip_deg": round(random.choice([-60, -75, -90]), 1),
            "azimuth_deg": round(random.uniform(0, 360), 1),
            "mn_assay_pct": mn_assay,
            "drill_date": d_date
        })

        # 2-4 samples per hole
        for s in range(random.randint(2, 4)):
            from_m = s * 25.0
            to_m = (s + 1) * 25.0
            mn_p = round(max(10.0, min(52.0, mn_assay + random.uniform(-5, 5))), 2)
            fe_p = round(random.uniform(4.0, 16.0), 2)
            sio2_p = round(random.uniform(8.0, 24.0), 2)
            al2o3_p = round(random.uniform(2.0, 8.0), 2)
            p_p = round(random.uniform(0.05, 0.35), 3)
            ore_samples.append({
                "sample_id": f"SMP-{sample_counter}",
                "hole_id": hid,
                "zone_id": z["zone_id"],
                "depth_from_m": from_m,
                "depth_to_m": to_m,
                "mn_pct": mn_p,
                "fe_pct": fe_p,
                "sio2_pct": sio2_p,
                "al2o3_pct": al2o3_p,
                "p_pct": p_p,
                "sample_date": d_date
            })
            sample_counter += 1

    with open(DATA_DEMO_DIR / "drill_holes.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=drill_holes[0].keys())
        writer.writeheader()
        writer.writerows(drill_holes)

    with open(DATA_DEMO_DIR / "ore_samples.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ore_samples[0].keys())
        writer.writeheader()
        writer.writerows(ore_samples)

    # 6. Weather
    weather = []
    curr_dt = datetime(2025, 9, 21)
    for day_i in range(365):
        d_str = (curr_dt + timedelta(days=day_i)).strftime("%Y-%m-%d")
        for m in mines:
            # seasonal rain signal (June-Sept high, rest low)
            month = (curr_dt + timedelta(days=day_i)).month
            is_monsoon = month in [6, 7, 8, 9]
            rain = round(random.uniform(15.0, 95.0), 1) if is_monsoon and random.random() < 0.65 else round(random.uniform(0.0, 4.0), 1)
            temp = round(random.uniform(22.0, 42.0), 1)
            humidity = round(random.uniform(35.0, 90.0), 1)
            soil_m = round(min(0.95, max(0.1, 0.2 + (rain / 120.0) + random.uniform(-0.05, 0.05))), 2)
            cond = "HEAVY RAIN" if rain > 40 else "LIGHT RAIN" if rain > 5 else "CLEAR"
            weather.append({
                "record_id": f"WX-{m['mine_id']}-{d_str}",
                "date": d_str,
                "mine_id": m["mine_id"],
                "rainfall_mm": rain,
                "temp_c": temp,
                "humidity_pct": humidity,
                "soil_moisture_pct": soil_m,
                "weather_condition": cond
            })
    with open(DATA_DEMO_DIR / "weather.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=weather[0].keys())
        writer.writeheader()
        writer.writerows(weather)

    # 7. Production
    production = []
    prod_id_counter = 10001
    weather_lookup = {(w["date"], w["mine_id"]): w for w in weather}
    for day_i in range(365):
        d_str = (curr_dt + timedelta(days=day_i)).strftime("%Y-%m-%d")
        for z in zones:
            w_rec = weather_lookup.get((d_str, z["mine_id"]), {"rainfall_mm": 0})
            rain = w_rec["rainfall_mm"]
            planned = 240.0 + (day_i % 7) * 12.0 - (day_i % 5) * 8.0
            target = 260.0
            downtime = round(random.uniform(0.5, 4.5) + (2.5 if rain > 30 else 0.0), 1)
            op_hours = max(4.0, round(16.0 - downtime, 1))
            actual = round(max(80.0, planned * (op_hours / 16.0) * (1.0 - 0.003 * rain) + random.uniform(-15, 15)), 1)
            grade = round(random.uniform(32.0, 44.0), 2)
            production.append({
                "production_id": f"PROD-{prod_id_counter}",
                "date": d_str,
                "mine_id": z["mine_id"],
                "zone_id": z["zone_id"],
                "planned_tonnes": planned,
                "actual_tonnes": actual,
                "ore_grade_pct": grade,
                "operating_hours": op_hours,
                "downtime_hours": downtime,
                "rainfall_mm": rain,
                "target_tonnes": target
            })
            prod_id_counter += 1
    with open(DATA_DEMO_DIR / "production.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=production[0].keys())
        writer.writeheader()
        writer.writerows(production)

    # 8. Equipment & 9. Downtime & 10. Maintenance
    eq_types = [("EX", "Excavator", 45.0), ("HT", "Haul truck", 60.0), ("DR", "Drill rig", 25.0), ("LD", "Loader", 35.0), ("CR", "Crusher", 120.0)]
    equipment = []
    eq_id_list = []
    for i in range(36):
        z = random.choice(zones)
        code, eq_type, cap = eq_types[i % len(eq_types)]
        eqid = f"{code}-{i+101:03d}"
        eq_id_list.append(eqid)
        avail = round(random.uniform(0.72, 0.96), 2)
        util = round(random.uniform(0.65, 0.90), 2)
        status = "MAINTENANCE" if avail < 0.78 else "ATTENTION" if avail < 0.85 else "READY"
        equipment.append({
            "equipment_id": eqid,
            "type": eq_type,
            "mine_id": z["mine_id"],
            "zone_id": z["zone_id"],
            "capacity_t": cap,
            "availability": avail,
            "utilization": util,
            "operating_hours": round(util * 24.0 * 30, 1),
            "downtime_hours": round((1 - avail) * 24.0 * 30, 1),
            "status": status
        })
    with open(DATA_DEMO_DIR / "equipment.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=equipment[0].keys())
        writer.writeheader()
        writer.writerows(equipment)

    # Downtime logs
    downtime_reasons = ["Mechanical failure", "Hydraulic leak", "Electrical glitch", "Scheduled maintenance", "Weather delay", "Operator shortage"]
    downtime_logs = []
    for i in range(320):
        eq = random.choice(equipment)
        dt_str = (curr_dt + timedelta(days=random.randint(0, 360))).strftime("%Y-%m-%d")
        dt_hrs = round(random.uniform(1.0, 18.0), 1)
        downtime_logs.append({
            "log_id": f"DT-LOG-{i+10001}",
            "equipment_id": eq["equipment_id"],
            "mine_id": eq["mine_id"],
            "zone_id": eq["zone_id"],
            "date": dt_str,
            "start_time": f"{dt_str}T{random.randint(6, 20):02d}:00:00Z",
            "end_time": f"{dt_str}T22:00:00Z",
            "downtime_hours": dt_hrs,
            "reason": random.choice(downtime_reasons),
            "severity": "CRITICAL" if dt_hrs > 12 else "HIGH" if dt_hrs > 6 else "MEDIUM"
        })
    with open(DATA_DEMO_DIR / "equipment_downtime.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=downtime_logs[0].keys())
        writer.writeheader()
        writer.writerows(downtime_logs)

    # Maintenance logs
    maint_types = ["PREVENTIVE", "CORRECTIVE", "OVERHAUL", "INSPECTION"]
    maintenance = []
    for i in range(160):
        eq = random.choice(equipment)
        dt_str = (curr_dt + timedelta(days=random.randint(0, 360))).strftime("%Y-%m-%d")
        mtype = random.choice(maint_types)
        maintenance.append({
            "maint_id": f"MNT-{i+20001}",
            "equipment_id": eq["equipment_id"],
            "date": dt_str,
            "maintenance_type": mtype,
            "description": f"{mtype} service for {eq['type']} component wear",
            "cost_inr": round(random.uniform(15000, 250000), 2),
            "status": random.choice(["COMPLETED", "IN_PROGRESS", "SCHEDULED"])
        })
    with open(DATA_DEMO_DIR / "maintenance.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=maintenance[0].keys())
        writer.writeheader()
        writer.writerows(maintenance)

    # 11. Blasting
    blasting = []
    for i in range(220):
        z = random.choice(zones)
        dt_str = (curr_dt + timedelta(days=random.randint(0, 360))).strftime("%Y-%m-%d")
        delay = round(random.choice([0.0, 0.0, 0.5, 1.5, 3.0, 4.5]), 1)
        blasting.append({
            "blast_id": f"BLAST-{i+30001}",
            "mine_id": z["mine_id"],
            "zone_id": z["zone_id"],
            "scheduled_time": f"{dt_str}T10:00:00Z",
            "actual_time": f"{dt_str}T{10+int(delay)}:30:00Z",
            "delay_hours": delay,
            "blast_status": "COMPLETED" if delay < 2 else "DELAYED",
            "powder_factor_kg_t": round(random.uniform(0.35, 0.75), 2),
            "material_type": random.choice(["Manganese Ore", "Overburden", "Waste Rock"])
        })
    with open(DATA_DEMO_DIR / "blasting.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=blasting[0].keys())
        writer.writeheader()
        writer.writerows(blasting)

    # 12. Satellite Observations
    satellite = []
    for i in range(300):
        z = random.choice(zones)
        dt_str = (curr_dt + timedelta(days=i * 1.2)).strftime("%Y-%m-%d")
        ndvi_val = round(random.uniform(0.18, 0.58), 2)
        soil_m = round(random.uniform(0.22, 0.65), 2)
        temp_c = round(random.uniform(24.0, 41.0), 1)
        spectral = round(random.uniform(0.30, 0.88), 2)
        satellite.append({
            "obs_id": f"SAT-{i+40001}",
            "mine_id": z["mine_id"],
            "zone_id": z["zone_id"],
            "date": dt_str,
            "latitude": z["latitude"],
            "longitude": z["longitude"],
            "ndvi": ndvi_val,
            "soil_moisture": soil_m,
            "surface_temp_c": temp_c,
            "elevation_m": z["elevation_m"],
            "slope_deg": z["slope_deg"],
            "spectral_proxy": spectral,
            "provenance": "SYNTHETIC DEMONSTRATION DATA"
        })
    with open(DATA_DEMO_DIR / "satellite_observations.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=satellite[0].keys())
        writer.writeheader()
        writer.writerows(satellite)

    print("--> All CSV files successfully generated in data/demo/.")

def seed_database():
    print("--> Seeding SQLite database from CSV files...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Clear existing tables to ensure clean seed
        db.query(RecommendationModel).delete()
        db.query(ModelRegistryModel).delete()
        db.query(SatelliteObsModel).delete()
        db.query(WeatherRecordModel).delete()
        db.query(BlastRecordModel).delete()
        db.query(MaintenanceModel).delete()
        db.query(DowntimeLogModel).delete()
        db.query(EquipmentModel).delete()
        db.query(ProductionModel).delete()
        db.query(OreSampleModel).delete()
        db.query(DrillHoleModel).delete()
        db.query(GeologicalObsModel).delete()
        db.query(MineZoneModel).delete()
        db.query(MineModel).delete()
        db.commit()

        # Helper to read CSV
        def read_csv(filename):
            with open(DATA_DEMO_DIR / filename, "r", encoding="utf-8") as f:
                return list(csv.DictReader(f))

        # Seed Mines
        for row in read_csv("mines.csv"):
            db.add(MineModel(
                mine_id=row["mine_id"], name=row["name"],
                latitude=float(row["latitude"]), longitude=float(row["longitude"]),
                state=row["state"], country=row["country"], status=row["status"],
                provenance=row["provenance"]
            ))

        # Seed Mine Zones
        for row in read_csv("mine_zones.csv"):
            db.add(MineZoneModel(
                zone_id=row["zone_id"], mine_id=row["mine_id"], name=row["name"],
                latitude=float(row["latitude"]), longitude=float(row["longitude"]),
                elevation_m=float(row["elevation_m"]), slope_deg=float(row["slope_deg"]),
                area_sqkm=float(row["area_sqkm"])
            ))

        # Seed Geological Obs
        for row in read_csv("geological_observations.csv"):
            db.add(GeologicalObsModel(
                obs_id=row["obs_id"], mine_id=row["mine_id"], zone_id=row["zone_id"],
                date=row["date"], lithology=row["lithology"], formation=row["formation"],
                structure_proximity_m=float(row["structure_proximity_m"]),
                mn_grade_proxy=float(row["mn_grade_proxy"]),
                elevation=float(row["elevation"]), slope=float(row["slope"])
            ))

        # Seed Drill Holes
        for row in read_csv("drill_holes.csv"):
            db.add(DrillHoleModel(
                hole_id=row["hole_id"], mine_id=row["mine_id"], zone_id=row["zone_id"],
                latitude=float(row["latitude"]), longitude=float(row["longitude"]),
                depth_m=float(row["depth_m"]), dip_deg=float(row["dip_deg"]),
                azimuth_deg=float(row["azimuth_deg"]), mn_assay_pct=float(row["mn_assay_pct"]),
                drill_date=row["drill_date"]
            ))

        # Seed Ore Samples
        for row in read_csv("ore_samples.csv"):
            db.add(OreSampleModel(
                sample_id=row["sample_id"], hole_id=row["hole_id"], zone_id=row["zone_id"],
                depth_from_m=float(row["depth_from_m"]), depth_to_m=float(row["depth_to_m"]),
                mn_pct=float(row["mn_pct"]), fe_pct=float(row["fe_pct"]),
                sio2_pct=float(row["sio2_pct"]), al2o3_pct=float(row["al2o3_pct"]),
                p_pct=float(row["p_pct"]), sample_date=row["sample_date"]
            ))

        # Seed Production
        for row in read_csv("production.csv"):
            db.add(ProductionModel(
                production_id=row["production_id"], date=row["date"], mine_id=row["mine_id"],
                zone_id=row["zone_id"], planned_tonnes=float(row["planned_tonnes"]),
                actual_tonnes=float(row["actual_tonnes"]), ore_grade_pct=float(row["ore_grade_pct"]),
                operating_hours=float(row["operating_hours"]), downtime_hours=float(row["downtime_hours"]),
                rainfall_mm=float(row["rainfall_mm"]), target_tonnes=float(row["target_tonnes"])
            ))

        # Seed Equipment
        for row in read_csv("equipment.csv"):
            db.add(EquipmentModel(
                equipment_id=row["equipment_id"], type=row["type"], mine_id=row["mine_id"],
                zone_id=row["zone_id"], capacity_t=float(row["capacity_t"]),
                availability=float(row["availability"]), utilization=float(row["utilization"]),
                operating_hours=float(row["operating_hours"]), downtime_hours=float(row["downtime_hours"]),
                status=row["status"]
            ))

        # Seed Downtime Logs
        for row in read_csv("equipment_downtime.csv"):
            db.add(DowntimeLogModel(
                log_id=row["log_id"], equipment_id=row["equipment_id"], mine_id=row["mine_id"],
                zone_id=row["zone_id"], date=row["date"], start_time=row["start_time"],
                end_time=row["end_time"], downtime_hours=float(row["downtime_hours"]),
                reason=row["reason"], severity=row["severity"]
            ))

        # Seed Maintenance
        for row in read_csv("maintenance.csv"):
            db.add(MaintenanceModel(
                maint_id=row["maint_id"], equipment_id=row["equipment_id"], date=row["date"],
                maintenance_type=row["maintenance_type"], description=row["description"],
                cost_inr=float(row["cost_inr"]), status=row["status"]
            ))

        # Seed Blasting
        for row in read_csv("blasting.csv"):
            db.add(BlastRecordModel(
                blast_id=row["blast_id"], mine_id=row["mine_id"], zone_id=row["zone_id"],
                scheduled_time=row["scheduled_time"], actual_time=row["actual_time"],
                delay_hours=float(row["delay_hours"]), blast_status=row["blast_status"],
                powder_factor_kg_t=float(row["powder_factor_kg_t"]), material_type=row["material_type"]
            ))

        # Seed Weather
        for row in read_csv("weather.csv"):
            db.add(WeatherRecordModel(
                record_id=row["record_id"], date=row["date"], mine_id=row["mine_id"],
                rainfall_mm=float(row["rainfall_mm"]), temp_c=float(row["temp_c"]),
                humidity_pct=float(row["humidity_pct"]), soil_moisture_pct=float(row["soil_moisture_pct"]),
                weather_condition=row["weather_condition"]
            ))

        # Seed Satellite Observations
        for row in read_csv("satellite_observations.csv"):
            db.add(SatelliteObsModel(
                obs_id=row["obs_id"], mine_id=row["mine_id"], zone_id=row["zone_id"],
                date=row["date"], latitude=float(row["latitude"]), longitude=float(row["longitude"]),
                ndvi=float(row["ndvi"]), soil_moisture=float(row["soil_moisture"]),
                surface_temp_c=float(row["surface_temp_c"]), elevation_m=float(row["elevation_m"]),
                slope_deg=float(row["slope_deg"]), spectral_proxy=float(row["spectral_proxy"]),
                provenance=row["provenance"]
            ))

        # Initial Model Registry entries
        models_data = [
            ModelRegistryModel(
                version="demo-prospectivity-1.0.0",
                task="prospectivity prediction",
                training_dataset="demo-geology-v1 (240 drill holes, 120 geo obs)",
                validation="spatial holdout design (synthetic demonstration fixture)",
                trained_at="2026-01-15T00:00:00Z",
                metrics_json='{"ROC_AUC": 0.84, "F1": 0.79, "MAE": 0.052}',
                is_active=True
            ),
            ModelRegistryModel(
                version="demo-production-1.0.0",
                task="production forecast",
                training_dataset="demo-production-v1 (1460 daily production logs)",
                validation="time-based holdout (synthetic demonstration fixture)",
                trained_at="2026-01-15T00:00:00Z",
                metrics_json='{"MAE_tonnes": 38.4, "RMSE_tonnes": 51.2, "MAPE": 0.058}',
                is_active=True
            ),
            ModelRegistryModel(
                version="demo-shortfall-1.0.0",
                task="shortfall risk classification",
                training_dataset="demo-shortfall-v1 (downtime & weather logs)",
                validation="time-based holdout (synthetic demonstration fixture)",
                trained_at="2026-01-15T00:00:00Z",
                metrics_json='{"ROC_AUC": 0.78, "F1": 0.72, "PR_AUC": 0.75}',
                is_active=True
            )
        ]
        for m in models_data: db.add(m)

        # Initial Recommendations
        recs_data = [
            RecommendationModel(
                id="REC-1001",
                action="Review drill-rig maintenance window before the next exploration shift",
                reason="Drill rig DR-003 availability (74%) is the highest contributor to operational shortfall risk in Eastern Ridge",
                zone="MINE-01-ZONE-A", equipment="DR-003",
                expected_impact_tonnes=48.0, confidence=0.76, status="REVIEW REQUIRED",
                created_at=datetime.now(timezone.utc).isoformat()
            ),
            RecommendationModel(
                id="REC-1002",
                action="Prioritize Central Bench haulage allocation for the next shift",
                reason="Forecast gap (55 tonnes) exceeds zone production variability; HT-014 availability at 86%",
                zone="MINE-01-ZONE-B", equipment="HT-014",
                expected_impact_tonnes=32.0, confidence=0.68, status="REVIEW REQUIRED",
                created_at=datetime.now(timezone.utc).isoformat()
            ),
            RecommendationModel(
                id="REC-1003",
                action="Inspect blasting schedule delay clearance in South Cut",
                reason="Blast delay average (2.5 hrs) correlates with high rainfall downtime in South Cut zone",
                zone="MINE-01-ZONE-C", equipment="EX-007",
                expected_impact_tonnes=25.0, confidence=0.71, status="REVIEW REQUIRED",
                created_at=datetime.now(timezone.utc).isoformat()
            )
        ]
        for r in recs_data: db.add(r)

        db.commit()

        # Audit Record Counts
        counts = {
            "mines": db.query(MineModel).count(),
            "mine_zones": db.query(MineZoneModel).count(),
            "geological_observations": db.query(GeologicalObsModel).count(),
            "drill_holes": db.query(DrillHoleModel).count(),
            "ore_samples": db.query(OreSampleModel).count(),
            "production": db.query(ProductionModel).count(),
            "equipment": db.query(EquipmentModel).count(),
            "equipment_downtime": db.query(DowntimeLogModel).count(),
            "maintenance": db.query(MaintenanceModel).count(),
            "blasting": db.query(BlastRecordModel).count(),
            "weather": db.query(WeatherRecordModel).count(),
            "satellite_observations": db.query(SatelliteObsModel).count(),
            "model_registry": db.query(ModelRegistryModel).count(),
            "recommendations": db.query(RecommendationModel).count()
        }

        print("--> Database Seeding Complete! Table Record Summary:")
        for tbl, count in counts.items():
            print(f"    - {tbl}: {count} records")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    generate_csvs()
    seed_database()
