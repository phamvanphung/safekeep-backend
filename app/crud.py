from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from passlib.context import CryptContext
from app.models import User, Timer, Vault, Beneficiary, TimerStatus
from app.schemas import UserCreate, TimerCreate, TimerUpdate, VaultCreate, VaultUpdate, BeneficiaryCreate, BeneficiaryUpdate

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# User CRUD
async def get_user(db: AsyncSession, user_id: UUID) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


# Timer CRUD
async def create_timer(db: AsyncSession, user_id: UUID, timer: TimerCreate) -> Timer:
    now = datetime.utcnow()
    deadline = now + timedelta(days=timer.timeout_days)
    
    db_timer = Timer(
        user_id=user_id,
        status=TimerStatus.ACTIVE,
        timeout_days=timer.timeout_days,
        last_checkin=now,
        deadline=deadline
    )
    db.add(db_timer)
    await db.commit()
    await db.refresh(db_timer)
    return db_timer


async def get_timer(db: AsyncSession, user_id: UUID) -> Optional[Timer]:
    result = await db.execute(select(Timer).where(Timer.user_id == user_id))
    return result.scalar_one_or_none()


async def update_timer_checkin(db: AsyncSession, user_id: UUID) -> Optional[Timer]:
    timer = await get_timer(db, user_id)
    if not timer:
        return None
    
    now = datetime.utcnow()
    timer.last_checkin = now
    timer.deadline = now + timedelta(days=timer.timeout_days)
    
    await db.commit()
    await db.refresh(timer)
    return timer


async def update_timer(db: AsyncSession, user_id: UUID, timer_update: "TimerUpdate") -> Optional[Timer]:
    timer = await get_timer(db, user_id)
    if not timer:
        return None
    
    if timer_update.timeout_days is not None:
        timer.timeout_days = timer_update.timeout_days
        # Recalculate deadline based on new timeout
        now = datetime.utcnow()
        timer.deadline = now + timedelta(days=timer.timeout_days)
    
    await db.commit()
    await db.refresh(timer)
    return timer


async def get_expired_timers(db: AsyncSession) -> List[Timer]:
    now = datetime.utcnow()
    result = await db.execute(
        select(Timer).where(
            Timer.deadline < now,
            Timer.status != TimerStatus.TRIGGERED
        )
    )
    return result.scalars().all()


async def mark_timer_triggered(db: AsyncSession, user_id: UUID) -> Optional[Timer]:
    timer = await get_timer(db, user_id)
    if not timer:
        return None
    
    timer.status = TimerStatus.TRIGGERED
    await db.commit()
    await db.refresh(timer)
    return timer


# Vault CRUD
async def create_vault(db: AsyncSession, user_id: UUID, vault: VaultCreate) -> Vault:
    db_vault = Vault(
        user_id=user_id,
        name=vault.name,
        encrypted_data=vault.encrypted_data,
        client_salt=vault.client_salt
    )
    db.add(db_vault)
    await db.commit()
    await db.refresh(db_vault)
    return db_vault


async def get_vaults(db: AsyncSession, user_id: UUID) -> List[Vault]:
    result = await db.execute(select(Vault).where(Vault.user_id == user_id))
    return result.scalars().all()


async def get_vault(db: AsyncSession, vault_id: UUID, user_id: UUID) -> Optional[Vault]:
    result = await db.execute(
        select(Vault).where(Vault.id == vault_id, Vault.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def update_vault(db: AsyncSession, vault_id: UUID, user_id: UUID, vault: VaultUpdate) -> Optional[Vault]:
    db_vault = await get_vault(db, vault_id, user_id)
    if not db_vault:
        return None
    
    if vault.name is not None:
        db_vault.name = vault.name
    if vault.encrypted_data is not None:
        db_vault.encrypted_data = vault.encrypted_data
    if vault.client_salt is not None:
        db_vault.client_salt = vault.client_salt
    
    await db.commit()
    await db.refresh(db_vault)
    return db_vault


async def delete_vault(db: AsyncSession, vault_id: UUID, user_id: UUID) -> bool:
    db_vault = await get_vault(db, vault_id, user_id)
    if not db_vault:
        return False
    
    await db.delete(db_vault)
    await db.commit()
    return True


# Beneficiary CRUD
async def create_beneficiary(db: AsyncSession, user_id: UUID, beneficiary: BeneficiaryCreate) -> Beneficiary:
    db_beneficiary = Beneficiary(
        user_id=user_id,
        email=beneficiary.email,
        name=beneficiary.name
    )
    db.add(db_beneficiary)
    await db.commit()
    await db.refresh(db_beneficiary)
    return db_beneficiary


async def get_beneficiaries(db: AsyncSession, user_id: UUID) -> List[Beneficiary]:
    result = await db.execute(select(Beneficiary).where(Beneficiary.user_id == user_id))
    return result.scalars().all()


async def get_beneficiary(db: AsyncSession, beneficiary_id: UUID, user_id: UUID) -> Optional[Beneficiary]:
    result = await db.execute(
        select(Beneficiary).where(
            Beneficiary.id == beneficiary_id,
            Beneficiary.user_id == user_id
        )
    )
    return result.scalar_one_or_none()


async def update_beneficiary(db: AsyncSession, beneficiary_id: UUID, user_id: UUID, beneficiary: "BeneficiaryUpdate") -> Optional[Beneficiary]:
    db_beneficiary = await get_beneficiary(db, beneficiary_id, user_id)
    if not db_beneficiary:
        return None
    
    if beneficiary.email is not None:
        db_beneficiary.email = beneficiary.email
    if beneficiary.name is not None:
        db_beneficiary.name = beneficiary.name
    
    await db.commit()
    await db.refresh(db_beneficiary)
    return db_beneficiary


async def delete_beneficiary(db: AsyncSession, beneficiary_id: UUID, user_id: UUID) -> bool:
    db_beneficiary = await get_beneficiary(db, beneficiary_id, user_id)
    if not db_beneficiary:
        return False
    
    await db.delete(db_beneficiary)
    await db.commit()
    return True
