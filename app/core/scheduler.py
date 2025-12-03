from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.processing.sync_service import sync_service
from app.db.session import SessionLocal
from app.models.user import User

scheduler = AsyncIOScheduler()

def sync_all_users():
    """
    Periodic job to sync data for all active users.
    """
    print("Running scheduled sync for all users...")
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.is_active == True).all()
        for user in users:
            # In a real app, this should be pushed to a task queue (Celery)
            # to avoid blocking the scheduler loop if sync takes long.
            # For MVP, we call it directly (synchronously blocking this job, but async in scheduler).
            sync_service.sync_user_data(user.id)
    finally:
        db.close()

def start_scheduler():
    # Run every 12 hours. For testing, we can set it to run every minute or manually trigger.
    # We'll set it to 12 hours as requested.
    scheduler.add_job(sync_all_users, 'interval', hours=12)
    scheduler.start()
    print("Scheduler started.")
