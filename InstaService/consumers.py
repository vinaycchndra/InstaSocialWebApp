from channels.consumer import AsyncConsumer
from channels.exceptions import StopConsumer
import json

# The consumer is executed in asynchronus fashion
class MyAsyncConsumer(AsyncConsumer):

    async def websocket_connect(self, event):

        # Storing User Object
        self.user = self.scope['user']
        await self.channel_layer.group_add(str(self.scope['user'].id), self.channel_name)
        await self.send({
            "type": "websocket.accept",
        })

        await self.send({
            "type": "websocket.send",
            "text": json.dumps({'msg': "You are connected to the webSocket, " +
                                       "You will now receive real time notifications", 'status': 'Ok'}),
        })

    async def websocket_receive(self, event):
        await self.send({
            "type": "websocket.send",
            "text": 'You: '+event["text"],
        })

        await self.send({
            "type": "websocket.send",
            "text": "Reply: We received your message",
        })

    async def websocket_disconnect(self, event):
        print('Web Socket Disconnected.....')
        self.channel_layer.group_discard(self.user.id, self.channel_name)
        raise StopConsumer()

    async def chat_notification(self, event):
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })



