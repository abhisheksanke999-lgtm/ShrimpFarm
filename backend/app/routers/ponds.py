from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import (
    DailyObservation,
    FeedRecord,
    HarvestRecord,
    Pond,
    PredictionRecord,
    User,
)
from app.schemas import MessageOut, PondCreate, PondOut

router = APIRouter(prefix="/api/ponds", tags=["ponds"])

_LINK_CHECKS = (
    (DailyObservation, "daily observations"),
    (FeedRecord, "feed records"),
    (HarvestRecord, "harvest records"),
    (PredictionRecord, "predictions"),
)


def _owned_pond(db: Session, user: User, pond_id: int) -> Pond:
    pond = (
        db.query(Pond)
        .filter(Pond.pond_id == pond_id, Pond.user_id == user.id)
        .first()
    )
    if not pond:
        raise HTTPException(status_code=404, detail="Pond not found.")
    return pond


def _pond_delete_blockers(db: Session, user: User, pond: Pond) -> list[str]:
    blocked: list[str] = []
    for model, label in _LINK_CHECKS:
        if (
            db.query(model)
            .filter(model.user_id == user.id, model.pond_name == pond.name)
            .first()
        ):
            blocked.append(label)
    return blocked


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


@router.delete("/{pond_id}", response_model=MessageOut)
def delete_pond(
    pond_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    pond = _owned_pond(db, user, pond_id)
    blockers = _pond_delete_blockers(db, user, pond)
    if blockers:
        joined = ", ".join(blockers)
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cannot delete this pond because it has linked {joined}. "
                "Remove or update those records first."
            ),
        )

    db.delete(pond)
    db.commit()
    return {"message": "Pond deleted successfully."}
