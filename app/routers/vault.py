from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import crud, schemas
from app.dependencies import get_current_active_user
from app.models import User

router = APIRouter(prefix="/vault", tags=["vault"])


@router.post("", response_model=schemas.VaultResponse, status_code=status.HTTP_201_CREATED)
async def create_vault(
    vault: schemas.VaultCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    # Check if vault already exists
    existing_vault = await crud.get_vault(db, current_user.id)
    if existing_vault:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vault already exists for this user"
        )
    
    db_vault = await crud.create_vault(db, current_user.id, vault)
    return db_vault


@router.get("", response_model=schemas.VaultResponse)
async def get_vault(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    db_vault = await crud.get_vault(db, current_user.id)
    if not db_vault:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vault not found"
        )
    return db_vault


@router.put("", response_model=schemas.VaultResponse)
async def update_vault(
    vault: schemas.VaultUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    db_vault = await crud.update_vault(db, current_user.id, vault)
    if not db_vault:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vault not found"
        )
    return db_vault


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vault(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    success = await crud.delete_vault(db, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vault not found"
        )
    return None
