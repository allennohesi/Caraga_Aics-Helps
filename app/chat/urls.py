from django.urls import path, include
from app.chat.views import chatPage, gemini_chat


urlpatterns = [
    # path("", chatPage, name="chat-page"),
    path('', chatPage, name='chat_page'),
    path('gemini_chat/', gemini_chat, name='gemini_chat'), # Gemini url
]
