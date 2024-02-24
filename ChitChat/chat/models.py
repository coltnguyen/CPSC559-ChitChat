from django.db import models

# Create your models here.
class User(models.Model):
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    userName = models.CharField(max_length=50, primary_key=True)
    password = models.CharField(max_length=50)

class Chatroom(models.Model):
    name = models.CharField(max_length=125, primary_key=True)

# Edited: 2024-02-23 10:47 PM by Makeda Morris
# I have assigned it to ON DELETE CASCADE for now. Discussions ongoing for best delete action.
class Message(models.Model):
    sender = models.ForeignKey('User', on_delete=models.CASCADE, primary_key=True)
    room = models.ForeignKey('ChatRoom', on_delete=models.CASCADE, primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True, primary_key=True)
    content = models.TextField()

    class Meta:
        unique_together = (('sender', 'room', 'timestamp'),)