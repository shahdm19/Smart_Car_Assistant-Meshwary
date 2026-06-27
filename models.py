from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    calculated_consumption = Column(Float, nullable=False)
    actual_consumption = Column(Float, nullable=False)
    difference_percentage = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    ai_response_summary = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

# ✅ استخدم DATABASE_URL من environment، ولو مش موجود استخدم SQLite
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///chatbot_feedback.db")

# لو PostgreSQL (زي ما Railway بيوفّره)، نظّف الـ URL
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite بتحتاج check_same_thread=False
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()