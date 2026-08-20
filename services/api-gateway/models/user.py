"""
SQLAlchemy models for User and AuditLog.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from database import Base


class UserRole(str):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class User(Base):
    """Mock user model for access-control demonstration."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(200), unique=True, nullable=False)
    hashed_password = Column(String(300), nullable=False)
    role = Column(String(50), default="viewer", nullable=False)
    is_active = Column(Boolean, default=True)
    department = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "department": self.department,
            "is_active": self.is_active,
        }


class AuditLog(Base):
    """
    Append-only audit log for every user action.
    Demonstrates tamper-evident audit trail (enterprise architecture mark).
    """
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    user_id = Column(String(100), nullable=True)
    username = Column(String(100), nullable=True)
    role = Column(String(50), nullable=True)
    action = Column(String(200), nullable=False)   # e.g. SEARCH_QUERY, DOCUMENT_VIEW
    resource_type = Column(String(100), nullable=True)  # document, search, agent
    resource_id = Column(String(200), nullable=True)
    request_path = Column(String(500), nullable=True)
    request_method = Column(String(10), nullable=True)
    payload_summary = Column(Text, nullable=True)     # sanitized query/params
    response_status = Column(String(10), nullable=True)
    ip_address = Column(String(50), nullable=True)
    extra = Column(JSON, default=dict)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "timestamp": self.timestamp.isoformat(),
            "username": self.username,
            "role": self.role,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "request_path": self.request_path,
            "response_status": self.response_status,
            "ip_address": self.ip_address,
        }
