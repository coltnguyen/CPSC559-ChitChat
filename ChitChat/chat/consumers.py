from channels.generic.websocket import AsyncWebsocketConsumer
import json



class chatConsumer(AsyncWebsocketConsumer):
    # Handles new WebSocket connections
    async def connect(self):
        # Accepts an incoming socket connection
        await self.accept()

    # Handles disconnection
    async def disconnect(self, close_code):
        # Placeholder for any cleanup or notification needed on disconnect
        pass

    # Receives messages from WebSocket
    async def receive(self, text_data):
        # Parses the text data into JSON
        text_data_json = json.loads(text_data)
        # Extracts the 'message' field from the JSON data
        message = text_data_json['message']

        # Sends the received message back to the WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
