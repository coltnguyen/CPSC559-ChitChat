from channels.generic.websocket import AsyncWebsocketConsumer
import json


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling chat functionality.
    """

    async def connect(self):
        """
        Called when a new WebSocket connection is established.
        """
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        """
        Called when a WebSocket connection is closed.
        """
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Called when a message is received from the WebSocket.
        """
        try:
            message = json.loads(text_data)
            username = message['username']
            text = message['text']
            timestamp = message['timestamp']
        except json.JSONDecodeError:
            # Handle invalid JSON format
            # TODO: Send an error message to the client
            return
        except KeyError:
            # Handle missing required fields in the message
            # TODO: Send an error message to the client
            return

        # Broadcast the received message to all clients in the room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'username': username,
                'text': text,
                'timestamp': timestamp,
            }
        )

    async def chat_message(self, event):
        """
        Called when a chat message event is received from the room group.
        """
        username = event['username']
        text = event['text']
        timestamp = event['timestamp']

        # Send the message to the connected client
        await self.send(json.dumps({
            'username': username,
            'text': text,
            'timestamp': timestamp
        }))
