from django.db import models
from ChitChat import settings
from django.contrib.auth.hashers import make_password

class ReplicatableModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Extract 'using' from kwargs if it exists
        using = kwargs.pop('using', None)

        try:
            super(ReplicatableModel, self).save(using='default', *args, **kwargs)
        except Exception as e:
            print(f"Error saving to default database: {e}")
            return

        # Attempt to save to the replica database
        try:
            super(ReplicatableModel, self).save(using='replica', *args, **kwargs)
        except Exception as e:
            print(f"Error saving to replica database: {e}")
            return

        # If 'using' was originally provided, restore it
        if using is not None:
            kwargs['using'] = using


class User(ReplicatableModel):
    # Define the fields for the User model
    firstName = models.CharField(max_length=50)  # User's first name
    lastName = models.CharField(max_length=50)  # User's last name
    userName = models.CharField(max_length=50, unique=True)  # User's username, must be unique
    password = models.CharField(max_length=50)  # User's password

    def set_password(self, raw_password):
        # Set the user's password and save the user instance
        self.password = raw_password  # Assign the raw password to the user's password field
        # self.save()  # Save the user instance to the database

class Message(ReplicatableModel):
    userName = models.CharField(max_length=50)
    chatroomId = models.IntegerField()
    message = models.CharField(max_length=500)
    date = models.DateTimeField(auto_now_add=True)

class Chatroom(ReplicatableModel):
    chatName = models.CharField(max_length=50, unique=True)
