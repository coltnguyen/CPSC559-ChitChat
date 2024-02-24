from django.urls import path
from . import consumers

# This section defines the URL routing for websocket connections.
# It maps the path 'ws/testpath/' to the chatConsumer class, allowing websocket connections to be established at this endpoint.

websocket_urlpatterns = [
    path('ws/testpath/', consumers.chatConsumer.as_asgi()),
]
