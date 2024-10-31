from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.users.serializers import UserSerializer, ActiveSwoSerializer, ErrorLogSerializer, FeedbackSerializer
from app.models import AuthUser, AuthFeedback
from app.requests.models import SocialWorker_Status, ErrorLogData
from datetime import timedelta, date, datetime, timedelta, time #DATE TIME
from rest_framework.pagination import PageNumberPagination
today = date.today()

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = 'page_size'
    max_page_size = 200

class UserViews(generics.ListAPIView):
    queryset = AuthUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class ActiveSwoView(generics.ListAPIView):
    serializer_class = ActiveSwoSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        queryset = SocialWorker_Status.objects.filter(user__authuserdetails__OfficeStationLib__name=self.request.query_params.get('address'),status=2,date_transaction=today).order_by('-id')
        return queryset
    
class ErrorViews(generics.ListAPIView):
    queryset = ErrorLogData.objects.all()
    serializer_class = ErrorLogSerializer
    permission_classes = [IsAuthenticated]

class FeedbackViews(generics.ListAPIView):
    queryset = AuthFeedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]