from channels.generic.websocket import WebsocketConsumer
import json

class WSConsumer(WebsocketConsumer):
    def connect(self):
        # Called when the websocket is handshaking as part of initial connection.
        # Add the user to the room group.
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Add the user to the room group
        self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Called when the WebSocket closes for any reason.
        # Leave the room group.
        self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        # Called when a message is received from the WebSocket.
        # Send message to room group
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

        print(message)

    # Called when a chat message is received from the room group.
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
