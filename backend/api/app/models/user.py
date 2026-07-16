from sqlmodel import SQLModel, Field
from typing import Optional
import uuid

# Base Schema with shared fields


class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    display_name: Optional[str] = None


class User(UserBase, table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False
    )
    password_hash: str = Field(nullable=False)


class UserCreate(UserBase):
    password: str
