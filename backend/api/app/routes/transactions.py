from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..models.transactions import Transaction
from typing import List, Optional
from ..database import get_db

router = APIRouter(prefix="/transactions/", tags=["Transactions"])


@router.get("/flagged", response_model=List[Transaction])
def velocity_detection(flag: Optional[str] = None, db: Session = Depends(get_db)):
    query = select(Transaction)
    if flag:
        query = query.where(Transaction.flag == flag)
    else:
        query = query.where(Transaction.flag.is_not(None))
    results = db.exec(query).all()
    if not results:
        raise HTTPException(
            status_code=404, detail="No transactions flagged for velocity"
        )
    return results
