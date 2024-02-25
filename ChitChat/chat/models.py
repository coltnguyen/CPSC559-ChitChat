from django.db import models

# Create your models here.
from django.contrib.auth.hashers import make_password

class User(models.Model):
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    userName = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)

    def set_password(self, raw_password):
        self.password = raw_password
        self.save()
