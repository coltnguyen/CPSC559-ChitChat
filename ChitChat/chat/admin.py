from django.contrib import admin
from .models import User, ChatRoom, Message

# We should probably have distinct admin models here but that's for later.

admin.site.register(User)
admin.site.register(ChatRoom)
admin.site.register(Message)
