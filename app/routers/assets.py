from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from app.database import get_db
from app.middleware.auth import require_api_key
from app.schemas.asset import (
    AssetCreate, AssetUpdate, AssetResponse,
    PaginatedAssets, BulkImportRequest, BulkImportResponse
)
from app.services import asset_service, dedup_service
from app.models.asset import AssetType, AssetStatus

router = APIRouter(prefix="/assets", tags=["Assets"])


# ── CREATE ─────────────────────────────────────────────────
@router.post("/", response_model=AssetResponse, status_code=201, dependencies=[Depends(require_api_key)])
def create_asset(data: AssetCreate, db: Session = Depends(get_db)):
    asset = asset_service.create_asset(db, data)
    return AssetResponse.from_orm_custom(asset)


# ── LIST ───────────────────────────────────────────────────
@router.get("/", response_model=PaginatedAssets)
def list_assets(
    type: Optional[AssetType] = Query(None),
    status: Optional[AssetStatus] = Query(None),
    tag: Optional[str] = Query(None),
    value_contains: Optional[str] = Query(None),
    sort_by: str = Query("last_seen", pattern="^(last_seen|first_seen|value|type|status)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    assets, total = asset_service.list_assets(
        db, type=type, status=status, tag=tag,
        value_contains=value_contains, sort_by=sort_by,
        sort_order=sort_order, page=page, page_size=page_size,
    )
    return PaginatedAssets(
        total=total,
        page=page,
        page_size=page_size,
        items=[AssetResponse.from_orm_custom(a) for a in assets],
    )


# ── GET ONE ────────────────────────────────────────────────
@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(asset_id: UUID, db: Session = Depends(get_db)):
    asset = asset_service.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return AssetResponse.from_orm_custom(asset)


# ── UPDATE ─────────────────────────────────────────────────
@router.patch("/{asset_id}", response_model=AssetResponse, dependencies=[Depends(require_api_key)])
def update_asset(asset_id: UUID, data: AssetUpdate, db: Session = Depends(get_db)):
    asset = asset_service.update_asset(db, asset_id, data)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return AssetResponse.from_orm_custom(asset)


# ── DELETE ─────────────────────────────────────────────────
@router.delete("/{asset_id}", status_code=204, dependencies=[Depends(require_api_key)])
def delete_asset(asset_id: UUID, db: Session = Depends(get_db)):
    deleted = asset_service.delete_asset(db, asset_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Asset not found")


# ── MARK STALE ─────────────────────────────────────────────
@router.patch("/{asset_id}/stale", response_model=AssetResponse, dependencies=[Depends(require_api_key)])
def mark_stale(asset_id: UUID, db: Session = Depends(get_db)):
    asset = asset_service.mark_stale(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return AssetResponse.from_orm_custom(asset)


# ── BULK IMPORT ────────────────────────────────────────────
@router.post("/bulk-import", response_model=BulkImportResponse, dependencies=[Depends(require_api_key)])
def bulk_import(data: BulkImportRequest, db: Session = Depends(get_db)):
    created = updated = skipped = 0
    errors = []

    for item in data.assets:
        try:
            _, action = dedup_service.upsert_asset(db, item)
            if action == "created":
                created += 1
            else:
                updated += 1
        except Exception as e:
            skipped += 1
            errors.append(f"Failed on '{item.value}': {str(e)}")

    return BulkImportResponse(
        created=created,
        updated=updated,
        skipped=skipped,
        errors=errors,
    )