from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_user
from app.database import get_db
from app.models import Pond, SeedStocking, User
from app.schemas import (
    PL_STAGES,
    MessageOut,
    SeedStockingCreate,
    SeedStockingListOut,
    SeedStockingOut,
    SeedStockingUpdate,
)

router = APIRouter(prefix="/api/seed-stocking", tags=["seed-stocking"])


def _cost_per_1000(cost: Decimal | float, qty: int) -> float:
    if not qty:
        return 0.0
    return round((float(cost) / float(qty)) * 1000.0, 4)


def _serialize(row: SeedStocking) -> SeedStockingOut:
    return SeedStockingOut(
        id=row.id,
        pond_id=row.pond_id,
        pond_name=row.pond.name if row.pond else "",
        pl_stage=row.pl_stage,
        supplier_name=row.supplier_name,
        batch_number=row.batch_number,
        total_quantity=row.total_quantity,
        cost=row.cost,
        cost_per_1000=_cost_per_1000(row.cost, row.total_quantity),
        stocking_date=row.stocking_date,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _owned_pond(db: Session, user: User, pond_id: int) -> Pond:
    pond = (
        db.query(Pond)
        .filter(Pond.pond_id == pond_id, Pond.user_id == user.id)
        .first()
    )
    if not pond:
        raise HTTPException(status_code=400, detail="Please select a valid pond.")
    return pond


def _validate_payload(pl_stage: str, supplier_name: str, batch_number: str, total_quantity: int, cost: float) -> tuple[str, str, str]:
    stage = pl_stage.strip()
    supplier = supplier_name.strip()
    batch = batch_number.strip()
    if stage not in PL_STAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid PL stage. Allowed: {', '.join(PL_STAGES)}",
        )
    if not supplier:
        raise HTTPException(status_code=400, detail="Supplier name is required.")
    if not batch:
        raise HTTPException(status_code=400, detail="Batch number is required.")
    if total_quantity <= 0:
        raise HTTPException(status_code=400, detail="Total quantity must be greater than 0.")
    if cost <= 0:
        raise HTTPException(status_code=400, detail="Cost must be greater than 0.")
    return stage, supplier, batch


def _ensure_unique_batch(
    db: Session,
    user_id: int,
    supplier: str,
    batch: str,
    exclude_id: int | None = None,
) -> None:
    q = db.query(SeedStocking).filter(
        SeedStocking.user_id == user_id,
        func.lower(SeedStocking.supplier_name) == supplier.lower(),
        func.lower(SeedStocking.batch_number) == batch.lower(),
    )
    if exclude_id is not None:
        q = q.filter(SeedStocking.id != exclude_id)
    if q.first():
        raise HTTPException(
            status_code=400,
            detail="This batch number already exists for the same supplier.",
        )


@router.get("", response_model=SeedStockingListOut)
def list_seed_stockings(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = (
        db.query(SeedStocking)
        .options(joinedload(SeedStocking.pond))
        .filter(SeedStocking.user_id == user.id)
        .order_by(SeedStocking.stocking_date.desc(), SeedStocking.id.desc())
        .all()
    )
    items = [_serialize(r) for r in rows]
    total_pl = sum(r.total_quantity for r in rows)
    total_cost = float(sum((r.cost for r in rows), Decimal("0")))
    most_recent = rows[0].stocking_date if rows else None
    return {
        "items": items,
        "total_records": len(items),
        "total_pl": total_pl,
        "total_cost": round(total_cost, 2),
        "most_recent_date": most_recent,
    }


@router.get("/{record_id}", response_model=SeedStockingOut)
def get_seed_stocking(record_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = (
        db.query(SeedStocking)
        .options(joinedload(SeedStocking.pond))
        .filter(SeedStocking.id == record_id, SeedStocking.user_id == user.id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Seed stocking record not found.")
    return _serialize(row)


@router.post("", response_model=SeedStockingOut)
def create_seed_stocking(
    payload: SeedStockingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _owned_pond(db, user, payload.pond_id)
    stage, supplier, batch = _validate_payload(
        payload.pl_stage,
        payload.supplier_name,
        payload.batch_number,
        payload.total_quantity,
        payload.cost,
    )
    _ensure_unique_batch(db, user.id, supplier, batch)

    row = SeedStocking(
        user_id=user.id,
        pond_id=payload.pond_id,
        pl_stage=stage,
        supplier_name=supplier,
        batch_number=batch,
        total_quantity=int(payload.total_quantity),
        cost=Decimal(str(round(payload.cost, 2))),
        stocking_date=payload.stocking_date,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="This batch number already exists for the same supplier.",
        ) from exc
    db.refresh(row)
    row = (
        db.query(SeedStocking)
        .options(joinedload(SeedStocking.pond))
        .filter(SeedStocking.id == row.id)
        .first()
    )
    return _serialize(row)


@router.put("/{record_id}", response_model=SeedStockingOut)
def update_seed_stocking(
    record_id: int,
    payload: SeedStockingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = (
        db.query(SeedStocking)
        .filter(SeedStocking.id == record_id, SeedStocking.user_id == user.id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Seed stocking record not found.")

    _owned_pond(db, user, payload.pond_id)
    stage, supplier, batch = _validate_payload(
        payload.pl_stage,
        payload.supplier_name,
        payload.batch_number,
        payload.total_quantity,
        payload.cost,
    )
    _ensure_unique_batch(db, user.id, supplier, batch, exclude_id=record_id)

    row.pond_id = payload.pond_id
    row.pl_stage = stage
    row.supplier_name = supplier
    row.batch_number = batch
    row.total_quantity = int(payload.total_quantity)
    row.cost = Decimal(str(round(payload.cost, 2)))
    row.stocking_date = payload.stocking_date

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="This batch number already exists for the same supplier.",
        ) from exc

    row = (
        db.query(SeedStocking)
        .options(joinedload(SeedStocking.pond))
        .filter(SeedStocking.id == record_id)
        .first()
    )
    return _serialize(row)


@router.delete("/{record_id}", response_model=MessageOut)
def delete_seed_stocking(
    record_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = (
        db.query(SeedStocking)
        .filter(SeedStocking.id == record_id, SeedStocking.user_id == user.id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Seed stocking record not found.")
    db.delete(row)
    db.commit()
    return {"message": "Seed stocking record deleted."}
