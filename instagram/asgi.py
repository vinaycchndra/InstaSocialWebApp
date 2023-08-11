import os

from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from UserFeedService import routing
from .middleware import TokenAuthMiddleware
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instagram.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': TokenAuthMiddleware(URLRouter(routing.websocket_urlpatterns)),
})
