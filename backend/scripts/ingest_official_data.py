import os
import sys
import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

ROOT_DIR = BACKEND_DIR.parent
RAW_DATA_DIR = ROOT_DIR / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

from app.db.database import engine, Base, SessionLocal
from app.db.models import DataSourceRegistryModel, OfficialProductionModel

OFFICIAL_SOURCES = [
    {
        "id": "SRC-IBM-01",
        "name": "Indian Bureau of Mines Statistics",
        "organization": "Indian Bureau of Mines (IBM), Ministry of Mines",
        "source_type": "OFFICIAL_GOVERNMENT",
        "official_url": "https://ibm.gov.in/",
        "dataset_name": "Indian Minerals Yearbook & Monthly Production Bulletins",
        "description": "State-level and district-level manganese ore production, value, and grade statistics for India.",
        "geographic_scope": "India (Maharashtra, Madhya Pradesh, Odisha)",
        "temporal_scope": "2018 – 2025",
        "update_frequency": "Monthly / Annual",
        "license": "Government Open Access / Official Public Domain",
        "last_downloaded": "2026-09-20",
        "status": "VERIFIED_ACTIVE"
    },
    {
        "id": "SRC-USGS-01",
        "name": "USGS Mineral Commodity Summaries",
        "organization": "U.S. Geological Survey (USGS)",
        "source_type": "OFFICIAL_GOVERNMENT",
        "official_url": "https://www.usgs.gov/",
        "dataset_name": "Manganese Commodity Summaries & Global Reserve Benchmarks",
        "description": "Global manganese mine production, country-level reserve benchmarks, and international trade statistics.",
        "geographic_scope": "Global (India, South Africa, Gabon, Australia, China)",
        "temporal_scope": "2021 – 2025",
        "update_frequency": "Annual",
        "license": "US Public Domain",
        "last_downloaded": "2026-09-20",
        "status": "VERIFIED_ACTIVE"
    },
    {
        "id": "SRC-BHUVAN-01",
        "name": "ISRO / NRSC Bhuvan Earth Observation",
        "organization": "National Remote Sensing Centre (NRSC) / ISRO",
        "source_type": "OFFICIAL_GOVERNMENT",
        "official_url": "https://bhuvan.nrsc.gov.in/",
        "dataset_name": "Bhuvan Open Data Portal Terrain & Spatial Proxies",
        "description": "Spatial elevation models, terrain slope, and surface proxy layers for Central India mining belts.",
        "geographic_scope": "Central India (~21.6° N, 85.9° E)",
        "temporal_scope": "2024 – 2026",
        "update_frequency": "Seasonal",
        "license": "ISRO Open Data Policy",
        "last_downloaded": "2026-09-20",
        "status": "VERIFIED_ACTIVE"
    },
    {
        "id": "SRC-COP-01",
        "name": "Copernicus Sentinel Data Space",
        "organization": "European Space Agency (ESA) / Copernicus",
        "source_type": "PUBLIC_EARTH_OBSERVATION",
        "official_url": "https://dataspace.copernicus.eu/",
        "dataset_name": "Sentinel-2 L2A Surface Reflectance & Vegetation Proxies",
        "description": "Surface environmental proxies (NDVI, soil moisture, spectral ratio indicators). Surface evidence only.",
        "geographic_scope": "Central India Mine Zones",
        "temporal_scope": "2025 – 2026",
        "update_frequency": "5-day revisit",
        "license": "Copernicus Open Access License",
        "last_downloaded": "2026-09-20",
        "status": "VERIFIED_ACTIVE"
    },
    {
        "id": "SRC-IMD-01",
        "name": "India Meteorological Department Logs",
        "organization": "India Meteorological Department (IMD)",
        "source_type": "OFFICIAL_GOVERNMENT",
        "official_url": "https://mausam.imd.gov.in/",
        "dataset_name": "Regional Precipitation & Soil Moisture Observational Data",
        "description": "Observational rainfall, temperature, and soil moisture logs for Nagpur and Balaghat mining districts.",
        "geographic_scope": "Nagpur (MH) & Balaghat (MP) Districts",
        "temporal_scope": "2024 – 2026",
        "update_frequency": "Daily",
        "license": "Government Open Data",
        "last_downloaded": "2026-09-20",
        "status": "VERIFIED_ACTIVE"
    }
]

def ingest_data_sources_registry(db):
    print("--> Registering official data sources in database registry...")
    for src in OFFICIAL_SOURCES:
        existing = db.query(DataSourceRegistryModel).filter_by(id=src["id"]).first()
        if not existing:
            db.add(DataSourceRegistryModel(**src))
        else:
            for k, v in src.items():
                setattr(existing, k, v)
    db.commit()
    print(f"--> Registered {len(OFFICIAL_SOURCES)} official data sources.")

def ingest_ibm_data(db):
    print("--> Ingesting official IBM manganese production data...")
    file_path = RAW_DATA_DIR / "ibm_manganese_production_india.csv"
    if not file_path.exists():
        print(f"File missing: {file_path}")
        return
    db.query(OfficialProductionModel).filter_by(source_id="SRC-IBM-01").delete()
    count = 0
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            db.add(OfficialProductionModel(
                source_id="SRC-IBM-01",
                state=row["state"],
                district=row["district"],
                year=row["year"],
                production_thousand_tonnes=float(row["production_thousand_tonnes"]),
                value_inr_lakhs=float(row["value_inr_lakhs"]),
                avg_grade_mn_pct=float(row["avg_grade_mn_pct"]),
                publication=row["source_publication"]
            ))
            count += 1
    db.commit()
    print(f"--> Ingested {count} official IBM production records.")

def main():
    parser = argparse.ArgumentParser(description="Official Data Ingestion Pipeline")
    parser.add_argument("--source", type=str, default="all", choices=["all", "ibm", "usgs", "satellite", "weather"], help="Target data source to ingest")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        ingest_data_sources_registry(db)
        if args.source in ["all", "ibm"]:
            ingest_ibm_data(db)
        print("--> Official Data Ingestion Pipeline Completed Successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error during official data ingestion: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    main()
