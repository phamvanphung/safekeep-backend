from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Enum as SQLEnum, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class TimerStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    TRIGGERED = "TRIGGERED"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    timer = relationship("Timer", back_populates="user", uselist=False)
    vaults = relationship("Vault", back_populates="user", cascade="all, delete-orphan")
    beneficiaries = relationship("Beneficiary", back_populates="user", cascade="all, delete-orphan")


class Timer(Base):
    __tablename__ = "timers"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    status = Column(SQLEnum(TimerStatus), default=TimerStatus.ACTIVE, nullable=False)
    timeout_days = Column(Integer, nullable=False)
    last_checkin = Column(DateTime, default=datetime.utcnow, nullable=False)
    deadline = Column(DateTime, nullable=False)

    # Relationships
    user = relationship("User", back_populates="timer")


class Vault(Base):
    __tablename__ = "vaults"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)  # Name/identifier for the vault
    encrypted_data = Column(Text, nullable=True)
    client_salt = Column(String, nullable=True)

    # Relationships
    user = relationship("User", back_populates="vaults")


class Beneficiary(Base):
    __tablename__ = "beneficiaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    email = Column(String, nullable=False)
    name = Column(String, nullable=False)

    # Relationships
    user = relationship("User", back_populates="beneficiaries")
