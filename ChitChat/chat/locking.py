from .models import Lock

class MongoDbWriteLock:

    # Check is a lock already exists.
    # The lock record must exist in all **active** databases for this
    # to be true.
    def already_acquired():
        lock_main = Lock.objects.using('default').filter(name="mongo_db_write_lock").exists()
        lock_replica = Lock.objects.using('replica').filter(name="mongo_db_write_lock").exists()
        return lock_main or lock_replica

    def acquire_lock(acquired_by):
        try:
            if MongoDbWriteLock.already_acquired():
                return False
            lock_instance = Lock.objects.create(name="mongo_db_write_lock", acquired_by=acquired_by)
            lock_instance.save()
            return True
        except Exception:
            return False

    def release_lock(acquired_by):
        try:
            if not MongoDbWriteLock.already_acquired():
                return False
            lock_instance = Lock.objects.filter(name="mongo_db_write_lock", acquired_by=acquired_by).first()
            if lock_instance:
                lock_instance.delete()
                return True
        except Exception:
            pass
        return False
