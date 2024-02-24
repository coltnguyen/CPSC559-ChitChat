from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from .consumers import WSConsumer

websocket_urlpatterns = [
    path('ws/chat/<room_name>', WSConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "websocket": URLRouter(
        websocket_urlpatterns
    ),
})
