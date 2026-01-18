from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import crud, schemas
from app.dependencies import get_current_active_user
from app.models import User

router = APIRouter(prefix="/heartbeat", tags=["heartbeat"])


@router.post("", response_model=schemas.HeartbeatResponse)
async def heartbeat(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    timer = await crud.update_timer_checkin(db, current_user.id)
    
    if not timer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timer not found for user"
        )
    
    return schemas.HeartbeatResponse(
        message="Heartbeat received successfully",
        last_checkin=timer.last_checkin,
        deadline=timer.deadline
    )
