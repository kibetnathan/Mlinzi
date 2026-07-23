from fastapi import APIRouter, Depends
from sqlmodel import Session
from ..models.transactions import Transaction
from typing import List, Optional
from ..database import get_db
from ..services.transactions import get_flagged_transactions
from datetime import date

router = APIRouter(prefix="/transactions/", tags=["Transactions"])


@router.get("/flagged", response_model=List[Transaction])
def flagged_transaction(
    flag: Optional[str] = None,
    target_date: date = Depends(date.today()),
    db: Session = Depends(get_db),
):
    return get_flagged_transactions(db, target_date, flag)
