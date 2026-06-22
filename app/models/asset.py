import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime, JSON, Enum, ForeignKey, Table
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.database import Base
import enum


# Enums
class AssetType(str, enum.Enum):
    domain = "domain"
    subdomain = "subdomain"
    ip_address = "ip_address"
    service = "service"
    certificate = "certificate"
    technology = "technology"


class AssetStatus(str, enum.Enum):
    active = "active"
    stale = "stale"
    archived = "archived"


class AssetSource(str, enum.Enum):
    import_ = "import"
    scan = "scan"
    manual = "manual"


# Asset Model
class Asset(Base):
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(Enum(AssetType), nullable=False, index=True)
    value = Column(String, nullable=False, index=True)
    status = Column(Enum(AssetStatus), nullable=False, default=AssetStatus.active, index=True)
    first_seen = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_seen = Column(DateTime, nullable=False, default=datetime.utcnow)
    source = Column(Enum(AssetSource), nullable=False)
    tags = Column(ARRAY(String), default=[])
    metadata_ = Column("metadata", JSON, default={})

    # Relationships
    outgoing = relationship(
        "AssetRelationship",
        foreign_keys="AssetRelationship.source_id",
        back_populates="source_asset",
        cascade="all, delete-orphan"
    )
    incoming = relationship(
        "AssetRelationship",
        foreign_keys="AssetRelationship.target_id",
        back_populates="target_asset",
        cascade="all, delete-orphan"
    )


# Relationship Model
class AssetRelationship(Base):
    __tablename__ = "asset_relationships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    target_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    relation_type = Column(String, nullable=False)  # e.g. "subdomain_of", "resolves_to"
    created_at = Column(DateTime, default=datetime.utcnow)

    source_asset = relationship("Asset", foreign_keys=[source_id], back_populates="outgoing")
    target_asset = relationship("Asset", foreign_keys=[target_id], back_populates="incoming")