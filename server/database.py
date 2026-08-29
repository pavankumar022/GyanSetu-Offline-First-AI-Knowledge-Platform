import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cloud_sim.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class KnowledgePack(Base):
    __tablename__ = "knowledge_packs"

    id = Column(String, primary_key=True, index=True) # e.g. KP-AGRI-ED-09
    title = Column(String, nullable=False)
    icon = Column(String, nullable=False) # e.g. agriculture, account_balance, local_hospital
    category = Column(String, nullable=False)
    version = Column(String, nullable=False) # Current cloud version
    size_mb = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    # List of files in the pack: [{"path": "agriculture/soils.pdf", "size_bytes": 10240, "hash": "abc123d"}]
    files_metadata = Column(JSON, nullable=False, default=list)

class SyncHistory(Base):
    __tablename__ = "sync_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    pack_id = Column(String, nullable=False)
    pack_title = Column(String, nullable=False)
    status = Column(String, nullable=False) # Success, Failed
    size_mb = Column(Integer, nullable=False)
    details = Column(String, nullable=True)

def init_db():
    Base.metadata.create_all(bind=engine)
    # Seed initial data if database is empty
    db = SessionLocal()
    try:
        if db.query(KnowledgePack).count() == 0:
            seed_initial_data(db)
    finally:
        db.close()

def seed_initial_data(db):
    # Pack 1: Agricultural Best Practices & Crop Data
    # Initially server has v2.0
    agri_pack = KnowledgePack(
        id="KP-AGRI-ED-09",
        title="Agricultural Best Practices & Crop Data",
        icon="agriculture",
        category="Agriculture",
        version="v2.0",
        size_mb=850,
        description="Comprehensive guides on soil health, irrigation practices, pest management, and multi-cropping advisory.",
        files_metadata=[
            {"path": "soil_health.txt", "size_bytes": 250000, "hash": "soil_v2_hash_456"},
            {"path": "pest_control.txt", "size_bytes": 480000, "hash": "pest_v2_hash_789"},
            {"path": "multi_cropping.txt", "size_bytes": 120000, "hash": "crop_v2_hash_101"}
        ]
    )

    # Pack 2: Government Scholarship Schemes 2024 (Already installed on device)
    scholarship_pack = KnowledgePack(
        id="KP-SCHOLAR-2024",
        title="Government Scholarship Schemes 2024",
        icon="account_balance",
        category="Education",
        version="v2.1",
        size_mb=420,
        description="Official list of national and state-level scholarship schemes for marginal student support.",
        files_metadata=[
            {"path": "scholarships.txt", "size_bytes": 350000, "hash": "scholar_v2_hash"}
        ]
    )

    # Pack 3: Rural Healthcare First-Aid Guide
    healthcare_pack = KnowledgePack(
        id="KP-HEALTH-RURAL",
        title="Rural Healthcare First-Aid Guide",
        icon="local_hospital",
        category="Healthcare",
        version="v1.0",
        size_mb=1228, # 1.2GB
        description="SOPs for healthcare workers, maternal care checklists, and emergency treatment guides.",
        files_metadata=[
            {"path": "first_aid.txt", "size_bytes": 950000, "hash": "health_v1_hash"}
        ]
    )

    # Pack 4: Primary Education Curriculum Offline
    education_pack = KnowledgePack(
        id="KP-EDU-PRIMARY",
        title="Primary Education Curriculum Offline",
        icon="school",
        category="Education",
        version="v1.2",
        size_mb=2450, # 2.4GB
        description="Offline-ready learning material, worksheets, and basic math and reading guidelines.",
        files_metadata=[
            {"path": "curriculum.txt", "size_bytes": 1800000, "hash": "edu_v12_hash"}
        ]
    )

    # Pack 5: Basic Legal Rights & Procedures Manual
    legal_pack = KnowledgePack(
        id="KP-LEGAL-BASIC",
        title="Basic Legal Rights & Procedures Manual",
        icon="gavel",
        category="Governance",
        version="v3.4",
        size_mb=620,
        description="Reference guides for basic legal procedures, panchayat filings, and right-to-information (RTI) drafts.",
        files_metadata=[
            {"path": "legal_rights.txt", "size_bytes": 540000, "hash": "legal_v3_hash"}
        ]
    )

    db.add_all([agri_pack, scholarship_pack, healthcare_pack, education_pack, legal_pack])

    # Seed some mock sync history
    syncs = [
        SyncHistory(
            timestamp=datetime.datetime.now() - datetime.timedelta(hours=2),
            pack_id="KP-SCHOLAR-2024",
            pack_title="Government Scholarship Schemes 2024",
            status="Success",
            size_mb=124,
            details="Synced scholarship database updates."
        ),
        SyncHistory(
            timestamp=datetime.datetime.now() - datetime.timedelta(days=1),
            pack_id="KP-AGRI-ED-09",
            pack_title="Agricultural Best Practices & Crop Data",
            status="Failed",
            size_mb=89,
            details="Network disconnected during download."
        ),
        SyncHistory(
            timestamp=datetime.datetime.now() - datetime.timedelta(days=3),
            pack_id="KP-EDU-PRIMARY",
            pack_title="Primary Education Curriculum Offline",
            status="Success",
            size_mb=45,
            details="System core update completed successfully."
        )
    ]
    db.add_all(syncs)
    db.commit()
