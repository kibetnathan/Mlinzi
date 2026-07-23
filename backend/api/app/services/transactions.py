import sys
from pathlib import Path
from sqlmodel import Session, select
from ..models.transactions import Transaction
from datetime import date, datetime, time
from typing import List, Optional

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BACKEND_DIR))
DATA_FILE = BACKEND_DIR.parent / "data" / "mlinzi_sample_transactions.csv"


def get_flagged_transactions(
    db: Session,
    target_date: date,
    flag: Optional[str] = None,
) -> List[Transaction]:
    query = select(Transaction)

    if flag:
        query = query.where(Transaction.flag == flag)
    else:
        query = query.where(Transaction.flag.is_not(None))

    start_of_day = datetime.combine(target_date, time.min)
    end_of_day = datetime.combine(target_date, time.max)
    query = query.where(
        Transaction.date_flagged >= start_of_day,
        Transaction.date_flagged <= end_of_day,
    )

    results = db.exec(query).all()

    if results:
        return results

    if not DATA_FILE.exists():
        return []

    _populate_from_csv(db)

    results = db.exec(query).all()
    return results


def _populate_from_csv(db: Session) -> None:
    from velocity_detection.velocity import (
        load_transactions as load_velocity,
        detect_velocity,
    )
    from repeated_withdrawal.repeated import (
        load_transactions as load_repeated,
        detect_repeated_withdrawals,
    )

    velocity_txns = detect_velocity(load_velocity())
    repeated_txns = detect_repeated_withdrawals(load_repeated())

    all_flagged = {}
    for txn in velocity_txns:
        all_flagged[txn["transaction_id"]] = txn
    for txn in repeated_txns:
        if txn["transaction_id"] in all_flagged:
            existing = all_flagged[txn["transaction_id"]]
            existing["flag"] = "velocity,repeated"
            existing["reason"] = (
                existing.get("reason", "") + "; " + txn.get("reason", "")
            )
        else:
            all_flagged[txn["transaction_id"]] = txn

    existing_ids = set(
        db.exec(
            select(Transaction.transaction_id).where(
                Transaction.transaction_id.in_(list(all_flagged.keys()))
            )
        ).all()
    )

    for txn_id, txn_data in all_flagged.items():
        if txn_id in existing_ids:
            continue

        timestamp = txn_data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        date_flagged = txn_data.get("date_flagged")
        if isinstance(date_flagged, str):
            date_flagged = datetime.fromisoformat(date_flagged)
        elif date_flagged is None:
            date_flagged = datetime.now()

        transaction = Transaction(
            transaction_id=txn_id,
            customer_id=txn_data.get("customer_id"),
            customer_name=txn_data.get("customer_name"),
            amount=txn_data.get("amount_kes"),
            transaction_type=txn_data.get("transaction_type"),
            channel=txn_data.get("channel"),
            timestamp=timestamp,
            is_flagged=True,
            flag=txn_data.get("flag"),
            reason=txn_data.get("reason"),
            date_flagged=date_flagged,
        )
        db.add(transaction)

    db.commit()
