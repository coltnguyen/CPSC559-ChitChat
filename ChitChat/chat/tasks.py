from celery import shared_task
from celery.utils.log import get_task_logger
from redis import Redis
from redlock import Redlock
import threading
import time
from .management.commands.sync_databases import run_synchronization

logger = get_task_logger(__name__)
redis_client = Redis(host='192.168.50.152', port=6379, db=0)

redlock = Redlock([
    {'host': '192.168.50.152', 'port': 6379, 'db': 0}
])

@shared_task(
    bind=True,
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=60
)
def run_sync_databases(self):
    lock_id = 'sync_databases_lock'
    lock_ttl = 300000  # Lock TTL in milliseconds (5 minutes)
    have_lock = False
    sync_completed = threading.Event()

    try:
        lock = redlock.lock(lock_id, lock_ttl)
        if lock:
            have_lock = True
            logger.info('Acquired lock. Running synchronization...')

            def heartbeat():
                while not sync_completed.is_set():
                    try:
                        redlock.extend(lock, additional_time=45000)  # Extend the lock by 45 seconds (in milliseconds)
                    except Exception as e:
                        logger.error(f'Error extending lock: {e}')
                        break
                    time.sleep(30)  # Sleep for 30 seconds before the next heartbeat

            heartbeat_thread = threading.Thread(target=heartbeat)
            heartbeat_thread.start()

            run_synchronization()
            sync_completed.set()  # Signal that synchronization is completed
            logger.info('Synchronization completed.')
        else:
            logger.info('Failed to acquire lock. Skipping synchronization.')
    except Exception as e:
        logger.error(f'Error acquiring lock: {e}')
        raise self.retry(exc=e)
    finally:
        if have_lock:
            redlock.unlock(lock)
            have_lock = False
            sync_completed.set()  # Signal that synchronization is completed (in case of an exception)
            heartbeat_thread.join()  # Wait for the heartbeat thread to finish
