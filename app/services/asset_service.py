from datetime import datetime
from uuid import UUID
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.asset import Asset, AssetStatus, AssetType
from app.schemas.asset import AssetCreate, AssetUpdate


def create_asset(db: Session, data: AssetCreate) -> Asset:
    asset = Asset(
        type=data.type,
        value=data.value,
        status=data.status,
        source=data.source,
        tags=data.tags,
        metadata_=data.metadata,
        first_seen=datetime.utcnow(),
        last_seen=datetime.utcnow(),
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def get_asset(db: Session, asset_id: UUID) -> Optional[Asset]:
    return db.query(Asset).filter(Asset.id == asset_id).first()


def update_asset(db: Session, asset_id: UUID, data: AssetUpdate) -> Optional[Asset]:
    asset = get_asset(db, asset_id)
    if not asset:
        return None

    if data.type is not None:
        asset.type = data.type
    if data.value is not None:
        asset.value = data.value
    if data.status is not None:
        asset.status = data.status
    if data.source is not None:
        asset.source = data.source
    if data.tags is not None:
        asset.tags = data.tags
    if data.metadata is not None:
        asset.metadata_ = data.metadata

    asset.last_seen = datetime.utcnow()
    db.commit()
    db.refresh(asset)
    return asset


def delete_asset(db: Session, asset_id: UUID) -> bool:
    asset = get_asset(db, asset_id)
    if not asset:
        return False
    db.delete(asset)
    db.commit()
    return True


def list_assets(
    db: Session,
    type: Optional[AssetType] = None,
    status: Optional[AssetStatus] = None,
    tag: Optional[str] = None,
    value_contains: Optional[str] = None,
    sort_by: str = "last_seen",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 20,
) -> tuple[List[Asset], int]:

    query = db.query(Asset)

    # Filters
    if type:
        query = query.filter(Asset.type == type)
    if status:
        query = query.filter(Asset.status == status)
    if tag:
        query = query.filter(Asset.tags.contains([tag]))
    if value_contains:
        query = query.filter(Asset.value.ilike(f"%{value_contains}%"))

    # Total count
    total = query.count()

    # Sorting
    sort_col = getattr(Asset, sort_by, Asset.last_seen)
    if sort_order == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())

    # Pagination
    offset = (page - 1) * page_size
    assets = query.offset(offset).limit(page_size).all()

    return assets, total


def mark_stale(db: Session, asset_id: UUID) -> Optional[Asset]:
    asset = get_asset(db, asset_id)
    if not asset:
        return None
    asset.status = AssetStatus.stale
    asset.last_seen = datetime.utcnow()
    db.commit()
    db.refresh(asset)
    return asset