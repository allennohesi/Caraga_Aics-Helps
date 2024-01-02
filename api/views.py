from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.serializers import MailSerializer
from app.requests.models import Mail


class MailViews(generics.ListAPIView):
    queryset = Mail.objects.all()
    serializer_class = MailSerializer
    permission_classes = [IsAuthenticated]