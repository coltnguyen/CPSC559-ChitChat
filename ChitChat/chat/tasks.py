from celery import shared_task
from celery.utils.log import get_task_logger
from redis import Redis
from redis.exceptions import LockError
from .management.commands.sync_databases import run_synchronization

logger = get_task_logger(__name__)
redis_client = Redis()  # Configure your Redis client as needed

@shared_task(bind=True, max_retries=3, retry_backoff=True, retry_backoff_max=60)
def run_sync_databases(self):
    lock_id = 'sync_databases_lock'
    have_lock = False
    lock = redis_client.lock(lock_id, timeout=300)  # Lock for 5 minutes
    try:
        have_lock = lock.acquire(blocking=False)
        if have_lock:
            logger.info('Acquired lock. Running synchronization...')
            run_synchronization()
            logger.info('Synchronization completed.')
        else:
            logger.info('Lock already acquired by another instance. Skipping synchronization.')
    except LockError as e:
        logger.error(f'Error acquiring lock: {e}')
        raise self.retry(exc=e)
    finally:
        if have_lock:
            lock.release()
