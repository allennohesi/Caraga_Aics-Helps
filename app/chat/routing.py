from django.urls import path , include
from app.chat.consumers import ChatConsumer
from django.urls import re_path
# Here, "" is routing to the URL ChatConsumer which 
# will handle the chat functionality.

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer.as_asgi()),
]