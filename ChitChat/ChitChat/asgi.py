"""
ASGI config for ChitChat project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChitChat.settings')

# Define the ASGI application for the ChitChat project
application = ProtocolTypeRouter({
    # Specifies that for HTTP protocol, Django's ASGI application should be used
    "http": get_asgi_application(),
    # For WebSocket protocol, use the AuthMiddlewareStack to manage authentication
    "websocket": AuthMiddlewareStack(
        # URLRouter directs incoming WebSocket connections to the correct consumer based on the URL
        URLRouter(
            chat.routing.websocket_urlpatterns  # Import the routing patterns from chat.routing module
        )
    ),
})
