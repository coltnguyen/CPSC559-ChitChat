from django.db import models

from django.contrib.auth.hashers import make_password

class User(models.Model):
    # Define the fields for the User model
    firstName = models.CharField(max_length=50)  # User's first name
    lastName = models.CharField(max_length=50)  # User's last name
    userName = models.CharField(max_length=50, unique=True)  # User's username, must be unique
    password = models.CharField(max_length=50)  # User's password

    def set_password(self, raw_password):
        # Set the user's password and save the user instance
        self.password = raw_password  # Assign the raw password to the user's password field
        self.save()  # Save the user instance to the database
