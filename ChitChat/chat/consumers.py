from channels.generic.websocket import AsyncWebsocketConsumer
import json



class chatConsumer(AsyncWebsocketConsumer):
    # Handles new WebSocket connections
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        # # Send a welcome message when a user connects
        # await self.send(text_data=json.dumps({'message': 'Welcome to the chat!'}))


    # Handles disconnection
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )


    async def receive(self, text_data):
        try:
            message = json.loads(text_data)
            text = message['text']
            timestamp = message['timestamp']
        except json.JSONDecodeError:
            # TODO Send some sort of error msg
            return
        except KeyError:
            # TODO Send some sort of error msg
            return

        print(f"text={text}", f"timestamp={timestamp}")

        # Broadcast the received message to all clients
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'text': text,
                'timestamp': timestamp,
            }
        )

    async def chat_message(self, event):
        text = event['text']
        timestamp = event['timestamp']
        print(f"text={text}", f"timestamp={timestamp}")
        # Send the message to the connected client
        await self.send(json.dumps({'text':text, 'timestamp':timestamp}))
