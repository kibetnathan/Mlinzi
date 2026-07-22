from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..models.transactions import Transaction
from typing import List, Optional
from ..database import get_db
from datetime import date, datetime, time

router = APIRouter(prefix="/transactions/", tags=["Transactions"])


@router.get("/flagged", response_model=List[Transaction])
def flagged_transaction(
    flag: Optional[str] = None,
    target_date: date = Depends(date.today()),
    db: Session = Depends(get_db),
):
    query = select(Transaction)
    # filter for flag
    if flag:
        query = query.where(Transaction.flag == flag)
    else:
        query = query.where(Transaction.flag.is_not(None))

    # filter for date
    start_of_day = datetime.combine(target_date, time.min)
    end_of_day = datetime.combine(target_date, time.max)
    query = query.where(
        Transaction.date_flagged >= start_of_day, Transaction.date_flagged <= end_of_day
    )

    results = db.exec(query).all()
    if not results:
        raise HTTPException(
            status_code=404, detail="No transactions flagged for velocity"
        )
    return results
