from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class SystemAlert(Base):
    __tablename__ = "system_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(20), nullable=False)  # info, warning, danger, success
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    icon = Column(String(50), default="info-circle")
    dismissible = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)