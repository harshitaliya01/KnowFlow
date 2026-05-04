from celery import Celery
from dotenv import load_dotenv
load_dotenv()
import os


celery_app = Celery(
    "worker",
    broker=os.getenv("REDIS_URL"),
    backend=os.getenv("REDIS_URL")
)

celery_app.conf.update(
    task_track_started=True,
    timezone="Asia/Kolkata",
    enable_utc=True,
)

celery_app.autodiscover_tasks(["app.utils.docs_tasks"])

#  FOR SOLO THREAD -> celery -A app.worker.celery_worker.celery_app worker --pool=solo --loglevel=info

# celery -A app.worker.celery_worker.celery_app worker --loglevel=info --concurrency=4