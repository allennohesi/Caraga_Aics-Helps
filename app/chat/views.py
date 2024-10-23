from django.shortcuts import render, redirect


from django.shortcuts import render, redirect
from .models import ChatMessage

def chatPage(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect("login-user")

    room_name = kwargs.get('room_name', 'default')  # Get room name or set default chat room
    chat_messages = ChatMessage.objects.filter(room_name=room_name).order_by('timestamp')[:50]  # Fetch latest 50 messages

    context = {
        'room_name': room_name,
        'chat_messages': chat_messages,  # Add chat messages to context
    }
    return render(request, "chatpage.html", context)
