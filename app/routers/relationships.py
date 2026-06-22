from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.middleware.auth import require_api_key
from app.models.asset import AssetRelationship
from app.schemas.asset import (
    RelationshipCreate, RelationshipResponse, AssetWithRelationships
)
from app.services.asset_service import get_asset
from app.schemas.asset import AssetResponse

router = APIRouter(prefix="/relationships", tags=["Relationships"])


# ── CREATE RELATIONSHIP ────────────────────────────────────
@router.post("/", response_model=RelationshipResponse, status_code=201, dependencies=[Depends(require_api_key)])
def create_relationship(data: RelationshipCreate, db: Session = Depends(get_db)):
    # تأكد إن الـ assets موجودين
    source = get_asset(db, data.source_id)
    target = get_asset(db, data.target_id)

    if not source:
        raise HTTPException(status_code=404, detail="Source asset not found")
    if not target:
        raise HTTPException(status_code=404, detail="Target asset not found")

    # تأكد مفيش duplicate
    existing = db.query(AssetRelationship).filter(
        AssetRelationship.source_id == data.source_id,
        AssetRelationship.target_id == data.target_id,
        AssetRelationship.relation_type == data.relation_type,
    ).first()

    if existing:
        raise HTTPException(status_code=409, detail="Relationship already exists")

    rel = AssetRelationship(
        source_id=data.source_id,
        target_id=data.target_id,
        relation_type=data.relation_type,
    )
    db.add(rel)
    db.commit()
    db.refresh(rel)
    return rel


# ── GET ALL RELATIONSHIPS ──────────────────────────────────
@router.get("/", response_model=list[RelationshipResponse])
def list_relationships(db: Session = Depends(get_db)):
    return db.query(AssetRelationship).all()


# ── GET ASSET GRAPH ────────────────────────────────────────
@router.get("/graph/{asset_id}", response_model=AssetWithRelationships)
def get_asset_graph(asset_id: UUID, db: Session = Depends(get_db)):
    asset = get_asset(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    return AssetWithRelationships(
        asset=AssetResponse.from_orm_custom(asset),
        outgoing=asset.outgoing,
        incoming=asset.incoming,
    )


# ── DELETE RELATIONSHIP ────────────────────────────────────
@router.delete("/{relationship_id}", status_code=204, dependencies=[Depends(require_api_key)])
def delete_relationship(relationship_id: UUID, db: Session = Depends(get_db)):
    rel = db.query(AssetRelationship).filter(
        AssetRelationship.id == relationship_id
    ).first()

    if not rel:
        raise HTTPException(status_code=404, detail="Relationship not found")

    db.delete(rel)
    db.commit()