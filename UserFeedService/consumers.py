from channels.consumer import AsyncConsumer
from channels.exceptions import StopConsumer
from channels.layers import get_channel_layer


# The consumer is executed in asynchronus fashion
class MyAsyncConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        print('Web Socket Connected.....')
        await self.channel_layer.group_add('hello', self.channel_name)
        await self.send({
            'type': 'websocket.accept',
        })

    async def websocket_receive(self, event):
        await self.channel_layer.group_send('hello', {
            "type": "chat.message",
            "text": event['text']+' you said',
        })

    async def websocket_disconnect(self, event):
        print('Web Socket Disconnected.....')
        raise StopConsumer()

    async def chat_message(self, event):
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })



