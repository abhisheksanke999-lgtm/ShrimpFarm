from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Pond, User
from app.schemas import MessageOut, PondCreate, PondOut

router = APIRouter(prefix="/api/ponds", tags=["ponds"])


@router.get("", response_model=list[PondOut])
def list_ponds(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(Pond)
        .filter(Pond.user_id == user.id)
        .order_by(Pond.pond_id.desc())
        .all()
    )


@router.get("/names")
def pond_names(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = (
        db.query(Pond.name)
        .filter(Pond.user_id == user.id)
        .order_by(Pond.name.asc())
        .all()
    )
    return [{"name": r[0]} for r in rows]


@router.post("", response_model=MessageOut)
def create_pond(payload: PondCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    name = payload.name.strip()
    if not name or payload.area_sqm <= 0 or payload.depth_m <= 0:
        raise HTTPException(status_code=400, detail="Please fill in all required pond details with valid measurements.")

    pond = Pond(
        user_id=user.id,
        name=name,
        area_sqm=payload.area_sqm,
        depth_m=payload.depth_m,
        water_source=payload.water_source.strip() or "Borewell",
        status=payload.status or "Active",
    )
    db.add(pond)
    db.commit()
    return {"message": "Pond saved successfully!"}
