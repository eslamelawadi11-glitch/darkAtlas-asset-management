from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID
from app.models.asset import AssetType, AssetStatus, AssetSource


# ── Asset Schemas ──────────────────────────────────────────

class AssetCreate(BaseModel):
    type: AssetType
    value: str
    status: AssetStatus = AssetStatus.active
    source: AssetSource
    tags: List[str] = []
    metadata: dict = {}


class AssetUpdate(BaseModel):
    type: Optional[AssetType] = None
    value: Optional[str] = None
    status: Optional[AssetStatus] = None
    source: Optional[AssetSource] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None


class AssetResponse(BaseModel):
    id: UUID
    type: AssetType
    value: str
    status: AssetStatus
    source: AssetSource
    tags: List[str]
    metadata: dict
    first_seen: datetime
    last_seen: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_custom(cls, obj):
        return cls(
            id=obj.id,
            type=obj.type,
            value=obj.value,
            status=obj.status,
            source=obj.source,
            tags=obj.tags or [],
            metadata=obj.metadata_ or {},
            first_seen=obj.first_seen,
            last_seen=obj.last_seen,
        )


# ── List & Pagination ──────────────────────────────────────

class PaginatedAssets(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[AssetResponse]


# ── Bulk Import ────────────────────────────────────────────

class BulkImportItem(BaseModel):
    id: Optional[str] = None
    type: AssetType
    value: str
    status: AssetStatus = AssetStatus.active
    source: AssetSource = AssetSource.import_
    tags: List[str] = []
    metadata: dict = {}


class BulkImportRequest(BaseModel):
    assets: List[BulkImportItem]


class BulkImportResponse(BaseModel):
    created: int
    updated: int
    skipped: int
    errors: List[str]


# ── Relationship Schemas ───────────────────────────────────

class RelationshipCreate(BaseModel):
    source_id: UUID
    target_id: UUID
    relation_type: str


class RelationshipResponse(BaseModel):
    id: UUID
    source_id: UUID
    target_id: UUID
    relation_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class AssetWithRelationships(BaseModel):
    asset: AssetResponse
    outgoing: List[RelationshipResponse]
    incoming: List[RelationshipResponse]