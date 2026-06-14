from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

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


engine = create_engine("sqlite:///chatbot_feedback.db", connect_args={"check_same_thread": False})
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()