from fastapi import APIRouter, Depends
from sqlmodel import Session
from ..models.transactions import Transaction
from typing import Optional
from ..database import get_db
from ..services.transactions import get_flagged_transactions
from datetime import date

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/flagged", response_model=list[Transaction])
def flagged_transaction(
    flag: Optional[str] = None,
    target_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    active_date = target_date or date.today()
    return get_flagged_transactions(db, target_date or date.today(), flag)


@router.get("/flagged", response_model=list[Transaction])
def flagged_transaction(
    flag: Optional[str] = None,
    target_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    active_date = target_date or date.today()
    return get_flagged_transactions(db, active_date, flag)
