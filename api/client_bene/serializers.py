from rest_framework import serializers

from app.requests.models import ClientBeneficiary, ClientBeneficiaryUpdateHistory


class ClientBeneficiarySerializer(serializers.ModelSerializer):
    address = serializers.CharField(source='get_client_address', read_only=True)
    date_of_registration = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)
    sex = serializers.CharField(source='sex.name', read_only=True)
    birthdate = serializers.DateField(format="%b %d, %Y", read_only=True)
    suffix = serializers.CharField(source='suffix.name', read_only=True)
    class Meta:
        model = ClientBeneficiary
        fields = [
            'id',
            'unique_id_number',
            'address',
            'suffix',
            'sex',
            'date_of_registration',
            'birthdate',
            'first_name',
            'last_name',
            'middle_name',
            'client_bene_fullname',
            'contact_number',
            'is_validated',
            'get_picture'
        ]

class ClientBeneficiaryUpdateHistorySerializer(serializers.ModelSerializer):
    unique_id = serializers.CharField(source='unique_id_number.unique_id_number', read_only=True)
    suffix = serializers.CharField(source='suffix.name', read_only=True)
    updated_by = serializers.CharField(source='updated_by.get_fullname', read_only=True, default=None)
    date_updated = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)

    class Meta:
        model = ClientBeneficiaryUpdateHistory
        fields = [
            'id',
            'unique_id',
            'last_name',
            'first_name',
            'middle_name',
            'suffix',
            'updated_by',
            'date_updated',
        ]