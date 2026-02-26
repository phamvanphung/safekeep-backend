from celery import Celery
from celery.schedules import crontab
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import settings
from app import crud
import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Iterable

# Create Celery app
celery_app = Celery(
    "deadmansswitch",
    broker=settings.redis_url,
    backend=settings.redis_url,
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


def _send_smtp_email(
    to_email: str,
    subject: str,
    body_html: str,
) -> None:
    """
    Synchronous helper that sends an email using SMTP settings from environment.
    """
    if not settings.smtp_host or not settings.smtp_port or not settings.smtp_from:
        print("SMTP not configured; skipping email send")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to_email

    msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            if settings.smtp_use_tls:
                server.starttls()
            if settings.smtp_username and settings.smtp_password:
                server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(msg)
        print(f"Sent email to {to_email}")
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to send email to {to_email}: {exc}")


async def send_email_async(to_email: str, subject: str, body_html: str) -> None:
    """
    Async wrapper to run the blocking SMTP send in a thread.
    """
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _send_smtp_email, to_email, subject, body_html)


def build_email_body(vaults: Iterable) -> str:
    """
    Build a simple HTML body that lists vault metadata and encrypted payload.
    """
    rows = []
    for v in vaults:
        rows.append(
            f"<li><strong>{v.name}</strong><br/>"
            f"<code>encrypted_data</code>: {v.encrypted_data or '(empty)'}<br/>"
            f"<code>client_salt</code>: {v.client_salt or '(none)'}</li>"
        )

    vaults_html = "".join(rows) or "<li>No vaults found for this user.</li>"

    return f"""
    <html>
      <body>
        <h2>SAFEKEEP - Dead Man's Switch triggered</h2>
        <p>
          The owner of this SAFEKEEP account has not checked in before their configured deadline.
          As a designated beneficiary, you are receiving the encrypted payload(s) they stored.
        </p>
        <p>
          <strong>Important:</strong> SAFEKEEP never sees decryption keys. You will need the
          appropriate client / passphrase to decrypt this data.
        </p>
        <ul>
          {vaults_html}
        </ul>
      </body>
    </html>
    """


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

                # Get all user's vaults (as a concrete list)
                vaults = list(await crud.get_vaults(session, timer.user_id))

                # Email body built once per user
                body_html = build_email_body(vaults)
                subject = "SAFEKEEP - Dead Man's Switch triggered"

                # Send email to each beneficiary with all vault data
                for beneficiary in beneficiaries:
                    print(
                        f"Sending Email to [{beneficiary.email}] with {len(vaults)} vault(s)",
                    )
                    await send_email_async(beneficiary.email, subject, body_html)

                # Mark timer as triggered
                await crud.mark_timer_triggered(session, timer.user_id)

            await session.commit()
        except Exception as e:  # noqa: BLE001
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
