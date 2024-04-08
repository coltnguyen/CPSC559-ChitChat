from django.db import models
from ChitChat import settings
from django.contrib.auth.hashers import make_password

class ReplicatableModel(models.Model):
    """
    Abstract base model class that provides replication functionality.

    This class extends Django's models.Model and overrides the save() method
    to save the model instance to both the default and replica databases.
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Overrides the save() method to save the model instance to both databases.

        This method first attempts to save the instance to the default database.
        If successful, it then attempts to save the instance to the replica database.
        If an error occurs during saving to either database, an exception is caught
        and an error message is printed.

        Args:
            *args: Positional arguments to be passed to the superclass save() method.
            **kwargs: Keyword arguments to be passed to the superclass save() method.
        """
        # Extract 'using' from kwargs if it exists
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

class User(ReplicatableModel):
    """
    Model representing a user in the system.

    This model extends the ReplicatableModel class to inherit the replication functionality.
    It defines fields for storing user information such as first name, last name, username, and password.
    """
    # Define the fields for the User model
    firstName = models.CharField(max_length=50)  # User's first name
    lastName = models.CharField(max_length=50)  # User's last name
    userName = models.CharField(max_length=50, unique=True)  # User's username, must be unique
    password = models.CharField(max_length=50)  # User's password

    def set_password(self, raw_password):
        """
        Sets the user's password.

        This method takes a raw password as input and assigns it to the user's password field.
        The password is not hashed or encrypted in this implementation.

        Args:
            raw_password (str): The raw password to be set for the user.
        """
        # Set the user's password and save the user instance
        self.password = raw_password  # Assign the raw password to the user's password field
        # self.save()  # Save the user instance to the database

class Message(ReplicatableModel):
    """
    Model representing a message in the system.

    This model extends the ReplicatableModel class to inherit the replication functionality.
    It defines fields for storing message information such as user ID, username, chatroom ID,
    message content, and creation date.
    """
    userId = models.IntegerField()
    userName = models.CharField(max_length=50)
    chatroomId = models.IntegerField()
    message = models.CharField(max_length=500)
    date = models.DateTimeField(auto_now_add=True)

class Chatroom(ReplicatableModel):
    """
    Model representing a chatroom in the system.

    This model extends the ReplicatableModel class to inherit the replication functionality.
    It defines a field for storing the chatroom name, which must be unique.
    """
    chatName = models.CharField(max_length=50, unique=True)
