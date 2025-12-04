from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)           # e.g. "user_approved", "user_locked"
    target_user_id = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)             # extra info (e.g. old/new values)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)