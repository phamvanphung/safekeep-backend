from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from app.database import get_db
from app import crud, schemas
from app.dependencies import get_current_active_user
from app.models import User

router = APIRouter(prefix="/beneficiaries", tags=["beneficiaries"])


@router.post("", response_model=schemas.BeneficiaryResponse, status_code=status.HTTP_201_CREATED)
async def create_beneficiary(
    beneficiary: schemas.BeneficiaryCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new beneficiary for the current user"""
    db_beneficiary = await crud.create_beneficiary(db, current_user.id, beneficiary)
    return db_beneficiary


@router.get("", response_model=List[schemas.BeneficiaryResponse])
async def get_beneficiaries(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all beneficiaries for the current user"""
    beneficiaries = await crud.get_beneficiaries(db, current_user.id)
    return beneficiaries


@router.get("/{beneficiary_id}", response_model=schemas.BeneficiaryResponse)
async def get_beneficiary(
    beneficiary_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific beneficiary by ID"""
    beneficiary = await crud.get_beneficiary(db, beneficiary_id, current_user.id)
    
    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary not found"
        )
    
    return beneficiary


@router.put("/{beneficiary_id}", response_model=schemas.BeneficiaryResponse)
async def update_beneficiary(
    beneficiary_id: UUID,
    beneficiary_update: schemas.BeneficiaryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a beneficiary"""
    beneficiary = await crud.update_beneficiary(db, beneficiary_id, current_user.id, beneficiary_update)
    
    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary not found"
        )
    
    return beneficiary


@router.delete("/{beneficiary_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_beneficiary(
    beneficiary_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a beneficiary"""
    success = await crud.delete_beneficiary(db, beneficiary_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary not found"
        )
    
    return None
