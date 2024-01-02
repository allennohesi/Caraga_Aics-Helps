from rest_framework import serializers

from app.requests.models import Mail


class MailSerializer(serializers.ModelSerializer):
    date_sent = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)

    class Meta:
        model = Mail
        fields = '__all__'