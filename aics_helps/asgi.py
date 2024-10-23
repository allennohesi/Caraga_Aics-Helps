import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aics_helps.settings')

application = get_asgi_application()

from app.chat import routing  # Replace with your actual routing module
application = ProtocolTypeRouter({
    "http": application,
    # (http->django views is added by default)
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns  # Update with your websocket URL patterns
        )
    ),
})