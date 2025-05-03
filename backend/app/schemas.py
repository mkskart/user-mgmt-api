"""Pydantic v2 schemas with ORM support."""
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class _OrmConfig:
    model_config = {"from_attributes": True}   # enables from_orm() in v2


class UserBase(BaseModel, _OrmConfig):
    name: str = Field(..., min_length=1, max_length=128)
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel, _OrmConfig):
    name: str | None = Field(None, min_length=1, max_length=128)
    email: EmailStr | None = None


class UserOut(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None