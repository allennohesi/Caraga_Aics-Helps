from rest_framework import serializers

from app.models import AuthUser, AuthUserGroups


class UserSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(source='get_fullname', read_only=True)
    updated_by = serializers.CharField(source='updated_by.get_fullname', read_only=True)
    date_updated = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)
    role = serializers.CharField(source='get_role', read_only=True)

    class Meta:
        model = AuthUser
        fields = '__all__'