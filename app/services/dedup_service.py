from datetime import datetime
from sqlalchemy.orm import Session
from app.models.asset import Asset, AssetStatus
from app.schemas.asset import BulkImportItem


def find_existing_asset(db: Session, type: str, value: str) -> Asset | None:
    """البحث عن asset موجود بنفس الـ type والـ value"""
    return db.query(Asset).filter(
        Asset.type == type,
        Asset.value == value
    ).first()


def merge_tags(existing: list, incoming: list) -> list:
    """دمج الـ tags من غير تكرار"""
    return list(set(existing or []) | set(incoming or []))


def merge_metadata(existing: dict, incoming: dict) -> dict:
    """دمج الـ metadata — الـ incoming بيـoverride لو في conflict"""
    merged = dict(existing or {})
    merged.update(incoming or {})
    return merged


def upsert_asset(db: Session, item: BulkImportItem) -> tuple[Asset, str]:
    """
    Insert أو Update asset حسب الـ type + value
    Returns: (asset, action) — action: 'created' | 'updated'
    """
    existing = find_existing_asset(db, item.type, item.value)

    if existing:
        # Asset موجود — نعمل update
        existing.last_seen = datetime.utcnow()
        existing.tags = merge_tags(existing.tags, item.tags)
        existing.metadata_ = merge_metadata(existing.metadata_, item.metadata)

        # لو كان stale ورجع يتشاف — يرجع active
        if existing.status == AssetStatus.stale:
            existing.status = AssetStatus.active

        db.commit()
        db.refresh(existing)
        return existing, "updated"

    else:
        # Asset جديد — نعمل insert
        new_asset = Asset(
            type=item.type,
            value=item.value,
            status=item.status,
            source=item.source,
            tags=item.tags,
            metadata_=item.metadata,
            first_seen=datetime.utcnow(),
            last_seen=datetime.utcnow(),
        )
        db.add(new_asset)
        db.commit()
        db.refresh(new_asset)
        return new_asset, "created"