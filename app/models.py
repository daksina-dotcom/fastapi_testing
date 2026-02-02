from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from .database import Base
from sqlalchemy.orm import relationship
from datetime import datetime


class Soldier(Base):
    __tablename__ = "army"
    soldier_id = Column(Integer, primary_key=True, index=True)
    soldier_name = Column(String(255), index=True)
    email_id = Column(String(255), unique=True, index=True, nullable=False)
    secret_password = Column(String(255), nullable=False)
    rank = Column(String(50), default="Lieutenant")
    status = Column(String(50), default="Active")
    joined_at = Column(DateTime, nullable=False, default=datetime.now)
    vacation_record = relationship("Vacation", back_populates="soldier", uselist=False)


class Veteran(Base):
    __tablename__ = "veterans"
    id = Column(Integer, primary_key=True, index=True)
    soldier_id = Column(
        Integer,
        ForeignKey("army.soldier_id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    retirement_date = Column(DateTime, default=datetime.now)
    pension_status = Column(Boolean, default=True)
    honorable_discharge = Column(Boolean, default=True)


class Vacation(Base):
    __tablename__ = "vacations"
    id = Column(Integer, primary_key=True, index=True)
    soldier_id = Column(
        Integer, ForeignKey("army.soldier_id", ondelete="CASCADE"), unique=True
    )
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    contact_location = Column(String(255))
    soldier = relationship("Soldier", back_populates="vacation_record", uselist=False)
