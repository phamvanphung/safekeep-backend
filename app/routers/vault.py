from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from app.database import get_db
from app import crud, schemas
from app.dependencies import get_current_active_user
from app.models import User

router = APIRouter(prefix="/vaults", tags=["vaults"])


@router.post("", response_model=schemas.VaultResponse, status_code=status.HTTP_201_CREATED)
async def create_vault(
    vault: schemas.VaultCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new vault for the current user"""
    db_vault = await crud.create_vault(db, current_user.id, vault)
    return db_vault


@router.get("", response_model=List[schemas.VaultResponse])
async def get_vaults(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all vaults for the current user"""
    vaults = await crud.get_vaults(db, current_user.id)
    return vaults


@router.get("/{vault_id}", response_model=schemas.VaultResponse)
async def get_vault(
    vault_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific vault by ID"""
    vault = await crud.get_vault(db, vault_id, current_user.id)
    if not vault:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vault not found"
        )
    return vault


@router.put("/{vault_id}", response_model=schemas.VaultResponse)
async def update_vault(
    vault_id: UUID,
    vault: schemas.VaultUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a vault"""
    db_vault = await crud.update_vault(db, vault_id, current_user.id, vault)
    if not db_vault:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vault not found"
        )
    return db_vault


@router.delete("/{vault_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vault(
    vault_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a vault"""
    success = await crud.delete_vault(db, vault_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vault not found"
        )
    return None
