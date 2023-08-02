from django.urls import path
from .consumers import MyAsyncConsumer

websocket_urlpatterns = [
    path('ws/async/', MyAsyncConsumer.as_asgi()),
]
