from celery import Celery
from celery.schedules import crontab
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import settings
from app import crud
import asyncio

# Create Celery app
celery_app = Celery(
    "deadmansswitch",
    broker=settings.redis_url,
    backend=settings.redis_url
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Create async database engine for Celery tasks
_engine = None
_async_session_maker = None


def get_engine():
    global _engine, _async_session_maker
    if _engine is None:
        _engine = create_async_engine(settings.database_url, echo=False)
        _async_session_maker = async_sessionmaker(_engine, expire_on_commit=False)
    return _async_session_maker


async def process_expired_timers():
    """Async function to process expired timers"""
    async_session_maker = get_engine()
    async with async_session_maker() as session:
        try:
            # Get all expired timers
            expired_timers = await crud.get_expired_timers(session)
            
            for timer in expired_timers:
                # Get user's beneficiaries
                beneficiaries = await crud.get_beneficiaries(session, timer.user_id)
                
                # Get user's vault
                vault = await crud.get_vault(session, timer.user_id)
                
                encrypted_data = vault.encrypted_data if vault else None
                
                # Send email to each beneficiary (simulated)
                for beneficiary in beneficiaries:
                    print(f"Sending Email to [{beneficiary.email}] with data [{encrypted_data}]")
                
                # Mark timer as triggered
                await crud.mark_timer_triggered(session, timer.user_id)
            
            await session.commit()
        except Exception as e:
            print(f"Error processing expired timers: {e}")
            await session.rollback()
            raise


@celery_app.task
def check_expired_timers():
    """Celery task wrapper for async function"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    loop.run_until_complete(process_expired_timers())


# Configure periodic task to run every hour
celery_app.conf.beat_schedule = {
    "check-expired-timers": {
        "task": "app.worker.check_expired_timers",
        "schedule": crontab(minute=0),  # Run at the start of every hour
    },
}
