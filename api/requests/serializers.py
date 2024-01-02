from decimal import DefaultContext
from rest_framework import serializers

from app.requests.models import Transaction, transaction_description, TransactionStatus1
from app.finance.models import finance_voucher, finance_voucherData

class TransactionSerializer(serializers.ModelSerializer):
    tracking_number = serializers.CharField(source='transaction.tracking_number')
    client = serializers.CharField(source='transaction.client.get_client_fullname', read_only=True, default=None)
    beneficiary = serializers.CharField(source='transaction.bene.get_client_fullname', read_only=True, default=None)
    verified_time_start = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)
    swo = serializers.CharField(source='transaction.swo.get_fullname', read_only=True, default=None)
    #swo_lastname = serializers.CharField(source='transaction.swo.last_name', read_only=True, default=None)
    priority = serializers.CharField(source='transaction.priority.priority_name', read_only=True)
    action = serializers.CharField(source='transaction.get_action_action', read_only=True)
    remarks_action = serializers.CharField(source='transaction.get_remarks_action', read_only=True)
    # is_verified = serializers.CharField(source='transaction.get_verified', read_only=True)
    # is_swo = serializers.CharField(source='transaction.get_swo', read_only=True)

    class Meta:
        model = TransactionStatus1
        fields = '__all__'


class Transaction_DescriptionSerializer(serializers.ModelSerializer):
    medicine = serializers.CharField(source='medicine.medicine_name', read_only=True, default=None)
    provided = serializers.CharField(source='provided.provided_name', read_only=True, default=None)
    service_provider = serializers.CharField(source='tracking_number.service_provider.name', read_only=True, default=None)
    class Meta:
        model = transaction_description
        fields = '__all__'

#FOR THE FINANCE MODULE
class FinanceVoucherSerializer(serializers.ModelSerializer):
    date = serializers.DateField(format="%b %d, %Y - %H:%M %p", read_only=True)
    user = serializers.CharField(source='user.get_fullname', read_only=True, default=None)
    class Meta:
        model = finance_voucher
        fields = '__all__'

class financeVoucherDataSerializer(serializers.ModelSerializer):
    TransactionTracking = serializers.CharField(source='transactionStatus.transaction.tracking_number', read_only=True, default=None)
    Assistance_type = serializers.CharField(source='transactionStatus.transaction.lib_type_of_assistance.type_name', read_only=True, default=None)
    Assistance_category = serializers.CharField(source='transactionStatus.transaction.lib_assistance_category.name', read_only=True, default=None)
    total = serializers.CharField(source='transactionStatus.transaction.get_total', read_only=True, default=None)
    class Meta:
        model = finance_voucherData
        fields = '__all__'

class TransactionsSignatoriesSerializer(serializers.ModelSerializer):
    tracking_number = serializers.CharField(source='transaction.tracking_number')
    client = serializers.CharField(source='transaction.client.get_client_fullname', read_only=True, default=None)
    beneficiary = serializers.CharField(source='transaction.bene.get_client_fullname', read_only=True, default=None)
    verified_time_start = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)
    swo = serializers.CharField(source='transaction.swo.get_fullname', read_only=True, default=None)
    priority = serializers.CharField(source='transaction.priority.priority_name', read_only=True)
    action = serializers.CharField(source='transaction.get_action_action', read_only=True)
    remarks_action = serializers.CharField(source='transaction.get_remarks_action', read_only=True)
    total_value = serializers.ReadOnlyField(source='get_total')

    class Meta:
        model = TransactionStatus1
        fields = '__all__'
