from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from .database import Base

class MineModel(Base):
    __tablename__ = "mines"
    mine_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    state = Column(String, default="Maharashtra")
    country = Column(String, default="India")
    status = Column(String, default="OPERATIONAL")
    provenance = Column(String, default="DEMO DATA / SYNTHETIC DATA")

class MineZoneModel(Base):
    __tablename__ = "mine_zones"
    zone_id = Column(String, primary_key=True, index=True)
    mine_id = Column(String, ForeignKey("mines.mine_id"), nullable=False)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation_m = Column(Float, default=400.0)
    slope_deg = Column(Float, default=15.0)
    area_sqkm = Column(Float, default=2.5)

class GeologicalObsModel(Base):
    __tablename__ = "geological_observations"
    obs_id = Column(String, primary_key=True, index=True)
    mine_id = Column(String, ForeignKey("mines.mine_id"))
    zone_id = Column(String, ForeignKey("mine_zones.zone_id"))
    date = Column(String)
    lithology = Column(String)
    formation = Column(String)
    structure_proximity_m = Column(Float)
    mn_grade_proxy = Column(Float)
    elevation = Column(Float)
    slope = Column(Float)

class DrillHoleModel(Base):
    __tablename__ = "drill_holes"
    hole_id = Column(String, primary_key=True, index=True)
    mine_id = Column(String, ForeignKey("mines.mine_id"))
    zone_id = Column(String, ForeignKey("mine_zones.zone_id"))
    latitude = Column(Float)
    longitude = Column(Float)
    depth_m = Column(Float)
    dip_deg = Column(Float)
    azimuth_deg = Column(Float)
    mn_assay_pct = Column(Float)
    drill_date = Column(String)

class OreSampleModel(Base):
    __tablename__ = "ore_samples"
    sample_id = Column(String, primary_key=True, index=True)
    hole_id = Column(String, ForeignKey("drill_holes.hole_id"))
    zone_id = Column(String, ForeignKey("mine_zones.zone_id"))
    depth_from_m = Column(Float)
    depth_to_m = Column(Float)
    mn_pct = Column(Float)
    fe_pct = Column(Float)
    sio2_pct = Column(Float)
    al2o3_pct = Column(Float)
    p_pct = Column(Float)
    sample_date = Column(String)

class ProductionModel(Base):
    __tablename__ = "production"
    production_id = Column(String, primary_key=True, index=True)
    date = Column(String, index=True)
    mine_id = Column(String, ForeignKey("mines.mine_id"))
    zone_id = Column(String, ForeignKey("mine_zones.zone_id"))
    planned_tonnes = Column(Float)
    actual_tonnes = Column(Float)
    ore_grade_pct = Column(Float)
    operating_hours = Column(Float)
    downtime_hours = Column(Float)
    rainfall_mm = Column(Float)
    target_tonnes = Column(Float)

class EquipmentModel(Base):
    __tablename__ = "equipment"
    equipment_id = Column(String, primary_key=True, index=True)
    type = Column(String)
    mine_id = Column(String, ForeignKey("mines.mine_id"))
    zone_id = Column(String, ForeignKey("mine_zones.zone_id"))
    capacity_t = Column(Float)
    availability = Column(Float)
    utilization = Column(Float)
    operating_hours = Column(Float)
    downtime_hours = Column(Float)
    status = Column(String)

class DowntimeLogModel(Base):
    __tablename__ = "equipment_downtime"
    log_id = Column(String, primary_key=True, index=True)
    equipment_id = Column(String, ForeignKey("equipment.equipment_id"))
    mine_id = Column(String, ForeignKey("mines.mine_id"))
    zone_id = Column(String, ForeignKey("mine_zones.zone_id"))
    date = Column(String)
    start_time = Column(String)
    end_time = Column(String)
    downtime_hours = Column(Float)
    reason = Column(String)
    severity = Column(String)

class MaintenanceModel(Base):
    __tablename__ = "maintenance"
    maint_id = Column(String, primary_key=True, index=True)
    equipment_id = Column(String, ForeignKey("equipment.equipment_id"))
    date = Column(String)
    maintenance_type = Column(String)
    description = Column(String)
    cost_inr = Column(Float)
    status = Column(String)

class BlastRecordModel(Base):
    __tablename__ = "blasting"
    blast_id = Column(String, primary_key=True, index=True)
    mine_id = Column(String, ForeignKey("mines.mine_id"))
    zone_id = Column(String, ForeignKey("mine_zones.zone_id"))
    scheduled_time = Column(String)
    actual_time = Column(String)
    delay_hours = Column(Float)
    blast_status = Column(String)
    powder_factor_kg_t = Column(Float)
    material_type = Column(String)

class WeatherRecordModel(Base):
    __tablename__ = "weather"
    record_id = Column(String, primary_key=True, index=True)
    date = Column(String, index=True)
    mine_id = Column(String, ForeignKey("mines.mine_id"))
    rainfall_mm = Column(Float)
    temp_c = Column(Float)
    humidity_pct = Column(Float)
    soil_moisture_pct = Column(Float)
    weather_condition = Column(String)

class SatelliteObsModel(Base):
    __tablename__ = "satellite_observations"
    obs_id = Column(String, primary_key=True, index=True)
    mine_id = Column(String, ForeignKey("mines.mine_id"))
    zone_id = Column(String, ForeignKey("mine_zones.zone_id"))
    date = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    ndvi = Column(Float)
    soil_moisture = Column(Float)
    surface_temp_c = Column(Float)
    elevation_m = Column(Float)
    slope_deg = Column(Float)
    spectral_proxy = Column(Float)
    provenance = Column(String, default="SYNTHETIC DEMONSTRATION DATA")

class ModelRegistryModel(Base):
    __tablename__ = "model_registry"
    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String, unique=True, index=True)
    task = Column(String)
    training_dataset = Column(String)
    validation = Column(String)
    trained_at = Column(String)
    metrics_json = Column(Text)
    is_active = Column(Boolean, default=True)

class RecommendationModel(Base):
    __tablename__ = "recommendations"
    id = Column(String, primary_key=True, index=True)
    action = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    zone = Column(String)
    equipment = Column(String)
    expected_impact_tonnes = Column(Float)
    confidence = Column(Float)
    status = Column(String, default="REVIEW REQUIRED")
    created_at = Column(String)

class DataSourceRegistryModel(Base):
    __tablename__ = "data_sources"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    organization = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    official_url = Column(String, nullable=False)
    dataset_name = Column(String, nullable=False)
    description = Column(String)
    geographic_scope = Column(String)
    temporal_scope = Column(String)
    update_frequency = Column(String)
    license = Column(String)
    last_downloaded = Column(String)
    status = Column(String, default="VERIFIED_ACTIVE")

class OfficialProductionModel(Base):
    __tablename__ = "official_mineral_production"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String, ForeignKey("data_sources.id"))
    state = Column(String)
    district = Column(String)
    year = Column(String)
    production_thousand_tonnes = Column(Float)
    value_inr_lakhs = Column(Float)
    avg_grade_mn_pct = Column(Float)
    publication = Column(String)
