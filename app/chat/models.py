# chat/models.py

from django.db import models
from django.contrib.auth.models import User

class ChatMessage(models.Model):
    room_name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'chatmessage_tbl'