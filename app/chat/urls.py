from django.urls import path, include
from app.chat.views import chatPage


urlpatterns = [
    path("", chatPage, name="chat-page"),

]