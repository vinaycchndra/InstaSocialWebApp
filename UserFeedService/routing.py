from django.urls import path
from InstaService.consumers import MyAsyncConsumer

websocket_urlpatterns = [
    path('ws/async/', MyAsyncConsumer.as_asgi()),
]
