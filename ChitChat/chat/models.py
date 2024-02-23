from django.db import models

# Create your models here.
class User(models.Model):
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    userName = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
