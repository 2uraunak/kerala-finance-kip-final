"""
SQLAlchemy models for Document, DocumentVersion, and DocumentChunk.
"""
import enum
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, DateTime, Enum, Boolean,
    Integer, Float, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from database import Base


class DocumentStatus(str, enum.Enum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    DRAFT = "draft"
    ARCHIVED = "archived"


class DocumentType(str, enum.Enum):
    GOVERNMENT_ORDER = "government_order"
    CIRCULAR = "circular"
    NOTIFICATION = "notification"
    OFFICE_MEMORANDUM = "office_memorandum"
    BUDGET = "budget"
    GST_POLICY = "gst_policy"
    OTHER = "other"


class Document(Base):
    """Master document record."""
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False, index=True)
    doc_number = Column(String(100), nullable=True, index=True)   # e.g. GO(Ms) No.45/2023
    doc_type = Column(Enum(DocumentType), nullable=False)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.ACTIVE, nullable=False)
    department = Column(String(200), default="Finance Department, Kerala")
    year = Column(Integer, nullable=True)
    issue_date = Column(DateTime, nullable=True)
    effective_date = Column(DateTime, nullable=True)

    # Lineage
    superseded_by_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True)
    supersedes_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True)

    # Storage
    minio_bucket = Column(String(100), default="kip-documents")
    minio_key = Column(String(500), nullable=True)   # path in MinIO

    # Processing flags
    is_scanned = Column(Boolean, default=False)
    ocr_confidence = Column(Float, nullable=True)
    is_restricted = Column(Boolean, default=False)   # Restricted/classified docs
    is_indexed = Column(Boolean, default=False)

    # Metadata
    tags = Column(JSON, default=list)
    summary = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100), nullable=True)

    # Relationships
    versions = relationship("DocumentVersion", back_populates="document", foreign_keys="DocumentVersion.document_id")
    superseded_by = relationship("Document", foreign_keys=[superseded_by_id], remote_side="Document.id", primaryjoin="Document.superseded_by_id == Document.id")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "title": self.title,
            "doc_number": self.doc_number,
            "doc_type": self.doc_type,
            "status": self.status,
            "department": self.department,
            "year": self.year,
            "issue_date": self.issue_date.isoformat() if self.issue_date else None,
            "effective_date": self.effective_date.isoformat() if self.effective_date else None,
            "superseded_by_id": str(self.superseded_by_id) if self.superseded_by_id else None,
            "supersedes_id": str(self.supersedes_id) if self.supersedes_id else None,
            "is_scanned": self.is_scanned,
            "ocr_confidence": self.ocr_confidence,
            "is_restricted": self.is_restricted,
            "is_indexed": self.is_indexed,
            "tags": self.tags,
            "summary": self.summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DocumentVersion(Base):
    """Tracks all versions of a document over time."""
    __tablename__ = "document_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    change_summary = Column(Text, nullable=True)
    minio_key = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100), nullable=True)

    document = relationship("Document", back_populates="versions", foreign_keys=[document_id])
