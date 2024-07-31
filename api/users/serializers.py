from rest_framework import serializers

from app.models import AuthUser, AuthUserGroups
from app.requests.models import SocialWorker_Status, ErrorLogData

class UserSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(source='get_fullname', read_only=True)
    updated_by = serializers.CharField(source='updated_by.get_fullname', read_only=True)
    date_updated = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)
    role = serializers.CharField(source='get_role', read_only=True)

    class Meta:
        model = AuthUser
        fields = '__all__'

class ActiveSwoSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(source='user.fullname', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    middle_name = serializers.CharField(source='user.middle_name', read_only=True)
    pending = serializers.CharField(source='get_total', read_only=True)
    ongoing = serializers.CharField(source='get_ongoing', read_only=True)
    complete = serializers.CharField(source='get_complete', read_only=True)
    datas = serializers.CharField(source='case_study', read_only=True)
    class Meta:
        model = SocialWorker_Status
        fields = '__all__'

class ErrorLogSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(source='user.get_fullname', read_only=True)
    date_time = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)

    class Meta:
        model = ErrorLogData
        fields = '__all__'