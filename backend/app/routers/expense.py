from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import ExpenseRecord, User
from app.schemas import ExpenseCreate, ExpenseListOut, MessageOut

router = APIRouter(prefix="/api/expenses", tags=["expenses"])


@router.get("", response_model=ExpenseListOut)
def list_expenses(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = (
        db.query(ExpenseRecord)
        .filter(ExpenseRecord.user_id == user.id)
        .order_by(ExpenseRecord.expense_date.desc(), ExpenseRecord.expense_id.desc())
        .all()
    )
    total = (
        db.query(func.coalesce(func.sum(ExpenseRecord.amount), 0))
        .filter(ExpenseRecord.user_id == user.id)
        .scalar()
    )
    return {"items": items, "total_amount": float(total or 0)}


@router.post("", response_model=MessageOut)
def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    description = payload.description.strip()
    if not description or payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Please fill in description and a valid expense amount.")

    row = ExpenseRecord(
        user_id=user.id,
        expense_date=payload.expense_date,
        category=payload.category or "Feed",
        description=description,
        amount=payload.amount,
    )
    db.add(row)
    db.commit()
    return {"message": "Expense saved successfully!"}
