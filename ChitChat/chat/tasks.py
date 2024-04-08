from celery import shared_task
from celery.utils.log import get_task_logger
from redis import Redis
import threading
import time
from .management.commands.sync_databases import run_synchronization
import os

logger = get_task_logger(__name__)
redis_client = Redis(host='10.13.117.186', port=6379, db=0)

instance_id = os.getpid()  # Use worker PID as the instance ID

def is_leader():
    """
    Determines if the current instance is the leader among the Celery workers.

    The leader is determined based on the instance ID (PID) stored in Redis.
    If there is no current leader, the current instance becomes the leader.
    If the current instance has a higher PID than the current leader, it attempts to become the leader.

    Returns:
        bool: True if the current instance is the leader, False otherwise.
    """
    current_leader_id = redis_client.get('leader_id')
    if current_leader_id is None:
        # If there's no leader, declare this instance as the leader
        redis_client.set('leader_id', instance_id, ex=60)  # Leader ID expires after 60 seconds
        return True
    else:
        current_leader_id = int(current_leader_id.decode())
        if instance_id > current_leader_id:
            # If this instance has a higher PID, attempt to declare it as the leader
            set_result = redis_client.set('leader_id', instance_id, nx=True, ex=60)
            if set_result:
                # Successfully set this instance as the leader
                return True
            else:
                # Failed to set this instance as the leader, likely due to a race condition
                return False
        elif instance_id == current_leader_id:
            # This instance is already the leader
            return True
        else:
            # There is a leader with a higher PID
            return False

@shared_task(
    bind=True,
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=60
)
def run_sync_databases(self):
    """
    Celery task to synchronize databases.

    This task is executed by the leader instance among the Celery workers.
    It acquires a distributed lock using Redis to ensure that only one instance runs the synchronization at a time.
    The lock is acquired with a TTL (Time-To-Live) of 5 minutes.
    A heartbeat thread is started to periodically refresh the lock TTL while the synchronization is in progress.

    If the lock is successfully acquired, the synchronization is performed by calling the `run_synchronization` function.
    If the lock cannot be acquired, the synchronization is skipped.

    In case of any errors during the synchronization, the task is retried up to 3 times with exponential backoff.

    Returns:
        None
    """
    if not is_leader():
        logger.info(f'Instance {instance_id} is not the leader. Skipping synchronization.')
        return

    lock_id = 'sync_databases_lock'
    lock_ttl = 300000  # Lock TTL in milliseconds (5 minutes)
    have_lock = False
    sync_completed = threading.Event()
    heartbeat_thread = None

    try:
        # Since this instance is the leader, attempt to acquire the lock
        if redis_client.set(lock_id, instance_id, nx=True, px=lock_ttl):
            have_lock = True
            logger.info(f'Instance {instance_id} acquired lock. Running synchronization...')

            def heartbeat():
                while not sync_completed.is_set():
                    try:
                        redis_client.pexpire(lock_id, lock_ttl)  # Refresh the lock TTL
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
            logger.info(f'Instance {instance_id} failed to acquire lock. Skipping synchronization.')
    except Exception as e:
        logger.error(f'Error in synchronization: {e}')
        raise self.retry(exc=e)
    finally:
        if have_lock:
            redis_client.delete(lock_id)
            have_lock = False
            sync_completed.set()  # Signal that synchronization is completed (in case of an exception)
        if heartbeat_thread and heartbeat_thread.is_alive():
            heartbeat_thread.join()  # Wait for the heartbeat thread to finish
