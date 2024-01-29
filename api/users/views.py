from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.users.serializers import UserSerializer, ActiveSwoSerializer
from app.models import AuthUser
from app.requests.models import SocialWorker_Status
from datetime import timedelta, date, datetime, timedelta, time #DATE TIME
today = date.today()

class UserViews(generics.ListAPIView):
    queryset = AuthUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class ActiveSwoView(generics.ListAPIView):
    queryset = SocialWorker_Status.objects.filter(status=2,date_transaction=today).order_by('-id')
    serializer_class = ActiveSwoSerializer
    permission_classes = [IsAuthenticated]