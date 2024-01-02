from rest_framework import serializers

from app.requests.models import ClientBeneficiary


class ClientBeneficiarySerializer(serializers.ModelSerializer):
    address = serializers.CharField(source='get_client_address', read_only=True)
    date_of_registration = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)
    sex = serializers.CharField(source='sex.name', read_only=True)
    birthdate = serializers.DateField(format="%b %d, %Y", read_only=True)
    class Meta:
        model = ClientBeneficiary
        fields = '__all__'