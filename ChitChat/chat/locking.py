from djongo import models

class Lock(models.Model):
    name = models.CharField(max_length=255, unique=True)
    acquired_by = models.CharField(max_length=255)
    acquired_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(using='locks', *args, **kwargs)

def acquire_lock(name, acquired_by):
    try:
        lock = Lock.objects.using('locks').create(name=name, acquired_by=acquired_by)
        return (True, lock)
    except Exception as e:
        return (False, e)

def release_lock(name):
    try:
        lock_instance = Lock.objects.using('locks').filter(name=name).first()
        if lock_instance:
            lock_instance.delete()
            return (True, None)
        else:
            raise Exception('Lock not found.')
    except Exception as e:
        return (False, e)


# For testing pruposes only!!!!
from rest_framework import serializers

class LockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lock
        fields = ['name', 'acquired_by']

    def create(self, validated_data):
        lock = Lock.objects.create(**validated_data)
        lock.save()
        return lock