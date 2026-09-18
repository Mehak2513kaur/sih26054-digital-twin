import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

root_dir = Path(__file__).resolve().parent.parent.parent
db_path = root_dir / "data" / "uav_twin.db"
os.makedirs(db_path.parent, exist_ok=True)

DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from backend.database import models
    Base.metadata.create_all(bind=engine)
