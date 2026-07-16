from sqlmodel import SQLModel, Field, DateTime
from typing import Optional
from datetime import datetime, timezone
from pydantic import field_validator

# Base Schema


class TransactionBase(SQLModel):
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    amount: Optional[int] = None
    transaction_type: Optional[str] = None
    channel: Optional[str] = None
    is_flagged: bool = Field(default=True)
    flag: Optional[str] = None


class Transaction(TransactionBase, table=True):
    transaction_id: str = Field(primary_key=True, index=True, nullable=False)
    timestamp: datetime = Field(sa_type=DateTime(timezone=True), nullable=False)


class TransactionCreate(TransactionBase):
    transaction_id: str
    timestamp: datetime

    @field_validator("timestamp")
    @classmethod
    def ensure_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
