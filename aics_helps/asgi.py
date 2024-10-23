import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from app.chat import routing  # Replace with your actual routing module

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aics_helps.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # (http->django views is added by default)
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns  # Update with your websocket URL patterns
        )
    ),
})