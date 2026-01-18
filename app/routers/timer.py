from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import crud, schemas
from app.dependencies import get_current_active_user
from app.models import User

router = APIRouter(prefix="/timer", tags=["timer"])


@router.get("", response_model=schemas.TimerResponse)
async def get_timer(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's timer information"""
    timer = await crud.get_timer(db, current_user.id)
    
    if not timer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timer not found for user"
        )
    
    return timer


@router.put("", response_model=schemas.TimerResponse)
async def update_timer(
    timer_update: schemas.TimerUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update timer timeout_days (recalculates deadline)"""
    timer = await crud.update_timer(db, current_user.id, timer_update)
    
    if not timer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timer not found for user"
        )
    
    return timer
