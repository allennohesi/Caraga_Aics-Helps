from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.users.serializers import UserSerializer
from app.models import AuthUser


class UserViews(generics.ListAPIView):
    queryset = AuthUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
