from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import HarvestRecord, Pond, User
from app.schemas import HarvestCreate, HarvestListOut, MessageOut

router = APIRouter(prefix="/api/harvests", tags=["harvests"])


@router.get("", response_model=HarvestListOut)
def list_harvests(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = (
        db.query(HarvestRecord)
        .filter(HarvestRecord.user_id == user.id)
        .order_by(HarvestRecord.harvest_date.desc(), HarvestRecord.harvest_id.desc())
        .all()
    )
    total = (
        db.query(func.coalesce(func.sum(HarvestRecord.total_amount), 0))
        .filter(HarvestRecord.user_id == user.id)
        .scalar()
    )
    return {"items": items, "total_revenue": float(total or 0)}


@router.post("", response_model=MessageOut)
def create_harvest(payload: HarvestCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    pond_name = payload.pond_name.strip()
    if not pond_name or payload.quantity_kg <= 0 or payload.price_per_kg <= 0:
        raise HTTPException(
            status_code=400,
            detail="Please fill in pond name, harvest quantity (kg), and price per kg.",
        )

    pond = (
        db.query(Pond)
        .filter(Pond.user_id == user.id, Pond.name == pond_name)
        .first()
    )
    if not pond:
        raise HTTPException(status_code=400, detail="Invalid pond selected.")

    total_amount = payload.quantity_kg * payload.price_per_kg
    row = HarvestRecord(
        user_id=user.id,
        pond_name=pond_name,
        harvest_date=payload.harvest_date,
        quantity_kg=payload.quantity_kg,
        price_per_kg=payload.price_per_kg,
        total_amount=total_amount,
        buyer_name=payload.buyer_name.strip() if payload.buyer_name else None,
    )
    db.add(row)
    pond.status = "Harvested"
    db.commit()
    return {"message": "Harvest saved! Pond marked as Harvested."}
