from celery import shared_task
from celery.utils.log import get_task_logger
from redis import Redis
from redlock import Redlock
import threading
import time
from .management.commands.sync_databases import run_synchronization

logger = get_task_logger(__name__)
redis_client = Redis(host='192.168.50.152', port=6379, db=0)

# Create a Redlock instance with a single Redis server
redlock = Redlock([
    {'host': '192.168.50.152', 'port': 6379, 'db': 0}
])

@shared_task(
    bind=True,  # This binds the first argument of the function to the task instance (self)
    max_retries=3,  # Maximum number of retries before giving up
    retry_backoff=True,  # Enables exponential backoff delay, doubling the retry delay for each retry
    retry_backoff_max=60  # Maximum number of seconds the retry delay can reach
)
def run_sync_databases(self):
    lock_id = 'sync_databases_lock'
    lock_ttl = 300000  # Lock TTL in milliseconds (5 minutes)
    have_lock = False

    try:
        # Acquire the lock using Redlock
        lock = redlock.lock(lock_id, lock_ttl)
        if lock:
            have_lock = True
            logger.info('Acquired lock. Running synchronization...')

            # Start a separate thread to periodically extend the lock's TTL
            def heartbeat():
                while have_lock:
                    redlock.extend(lock, additional_time=45000)  # Extend the lock by 45 seconds minute (milliseconds)
                    time.sleep(30)  # Sleep for 30 seconds before the next heartbeat

            heartbeat_thread = threading.Thread(target=heartbeat)
            heartbeat_thread.start()

            run_synchronization()
            logger.info('Synchronization completed.')
        else:
            logger.info('Failed to acquire lock. Skipping synchronization.')
    except Exception as e:
        logger.error(f'Error acquiring lock: {e}')
        raise self.retry(exc=e)
    finally:
        if have_lock:
            redlock.unlock(lock)
            have_lock = False  # Set the flag to stop the heartbeat thread
            heartbeat_thread.join()  # Wait for the heartbeat thread to finish
