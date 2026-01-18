from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID
from app.models import TimerStatus


# User Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    is_active: bool

    class Config:
        from_attributes = True


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# Timer Schemas
class TimerCreate(BaseModel):
    timeout_days: int


class TimerResponse(BaseModel):
    user_id: UUID
    status: TimerStatus
    timeout_days: int
    last_checkin: datetime
    deadline: datetime

    class Config:
        from_attributes = True


class TimerUpdate(BaseModel):
    timeout_days: Optional[int] = None


# Vault Schemas
class VaultCreate(BaseModel):
    encrypted_data: Optional[str] = None
    client_salt: Optional[str] = None


class VaultUpdate(BaseModel):
    encrypted_data: Optional[str] = None
    client_salt: Optional[str] = None


class VaultResponse(BaseModel):
    id: UUID
    user_id: UUID
    encrypted_data: Optional[str]
    client_salt: Optional[str]

    class Config:
        from_attributes = True


# Beneficiary Schemas
class BeneficiaryCreate(BaseModel):
    email: EmailStr
    name: str


class BeneficiaryResponse(BaseModel):
    id: UUID
    user_id: UUID
    email: str
    name: str

    class Config:
        from_attributes = True


# Heartbeat Schema
class HeartbeatResponse(BaseModel):
    message: str
    last_checkin: datetime
    deadline: datetime
