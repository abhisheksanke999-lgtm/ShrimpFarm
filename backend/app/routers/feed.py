from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import FeedRecord, Pond, User
from app.schemas import FeedCreate, FeedOut, MessageOut

router = APIRouter(prefix="/api/feed", tags=["feed"])


@router.get("", response_model=list[FeedOut])
def list_feed(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(FeedRecord)
        .filter(FeedRecord.user_id == user.id)
        .order_by(FeedRecord.entry_date.desc(), FeedRecord.feed_id.desc())
        .all()
    )


@router.post("", response_model=MessageOut)
def create_feed(payload: FeedCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    pond_name = payload.pond_name.strip()
    feed_brand = payload.feed_brand.strip()
    if not pond_name or not feed_brand or payload.quantity_kg <= 0:
        raise HTTPException(status_code=400, detail="Please fill in pond, feed brand, and valid feed quantity.")

    owns = (
        db.query(Pond)
        .filter(Pond.user_id == user.id, Pond.name == pond_name)
        .first()
    )
    if not owns:
        raise HTTPException(status_code=400, detail="Invalid pond selected.")

    row = FeedRecord(
        user_id=user.id,
        pond_name=pond_name,
        feed_brand=feed_brand,
        quantity_kg=payload.quantity_kg,
        feeding_time=payload.feeding_time or "Morning",
        entry_date=payload.entry_date,
        feed_size=payload.feed_size.strip() if payload.feed_size else None,
    )
    db.add(row)
    db.commit()
    return {"message": "Feed record saved successfully!"}
