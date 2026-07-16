from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..models.transactions import Transaction
from typing import List
from ..database import get_db

router = APIRouter(prefix="/transactions/", tags=["Transactions"])


@router.get("/velocity", response_model=List[Transaction])
def velocity_detection(flag: str = "velocity", db: Session = Depends(get_db)):
    query = select(Transaction)
    if flag is not None:
        query = query.where(Transaction.flag == flag)
    results = db.exec(query).all()
    if not results:
        return HTTPException(
            status_code=404, detail="No transactions flagged for velocity"
        )
    return results
