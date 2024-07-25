from decimal import DefaultContext
from rest_framework import serializers

from app.requests.models import Transaction, transaction_description, TransactionStatus1
from app.finance.models import finance_voucher, finance_voucherData, finance_outsideFo

class TransactionSerializer(serializers.ModelSerializer):
    tracking_number = serializers.CharField(source='transaction.tracking_number')
    client = serializers.CharField(source='transaction.client.client_bene_fullname', read_only=True, default=None)
    beneficiary = serializers.CharField(source='transaction.bene.client_bene_fullname', read_only=True, default=None)
    verified_time_start = serializers.DateTimeField(format="%b %d, %Y - %H:%M %p", read_only=True)
    swo = serializers.CharField(source='transaction.swo.get_fullname', read_only=True, default=None)
    swo_lastname = serializers.CharField(source='transaction.swo.last_name', read_only=True, default=None)
    swo_fullname = serializers.CharField(source='transaction.swo.fullname', read_only=True, default=None)
    swo_firstname = serializers.CharField(source='transaction.swo.first_name', read_only=True, default=None)
    #swo_lastname = serializers.CharField(source='transaction.swo.last_name', read_only=True, default=None)
    priority = serializers.CharField(source='transaction.priority.priority_name', read_only=True)
    action = serializers.CharField(source='transaction.get_action_action', read_only=True)
    case_study = serializers.CharField(source='transaction.is_case_study', read_only=True)
    total_amount = serializers.CharField(source='transaction.total_amount', read_only=True)
    dv_number = serializers.CharField(source='transaction.dv_number', read_only=True)
    service_provider = serializers.CharField(source='transaction.service_provider.name', read_only=True, default=None)
    mode_of_release = serializers.CharField(source='transaction.is_gl', read_only=True)
    assistance_type = serializers.CharField(source='transaction.lib_assistance_category.name', read_only=True)
    get_picture = serializers.CharField(source='transaction.client.get_picture', read_only=True, default=None)
    # is_verified = serializers.CharField(source='transaction.get_verified', read_only=True)
    # is_swo = serializers.CharField(source='transaction.get_swo', read_only=True)

    class Meta:
        model = TransactionStatus1
        fields = ['tracking_number','status', 'client', 'beneficiary', 'verified_time_start', 'swo','swo_fullname','swo_lastname','swo_firstname','priority', 'action', 'transaction', 'total_amount', 'dv_number', 'service_provider','case_study_status','case_study',
                  'mode_of_release', 'assistance_type', 'get_picture']
        
class Transaction_DescriptionSerializer(serializers.ModelSerializer):
    medicine = serializers.CharField(source='medicine.medicine_name', read_only=True, default=None)
    provided = serializers.CharField(source='provided.provided_name', read_only=True, default=None)
    service_provider = serializers.CharField(source='tracking_number.service_provider.name', read_only=True, default=None)
    class Meta:
        model = transaction_description
        fields = '__all__'

#FOR THE FINANCE MODULE
class FinanceVoucherSerializer(serializers.ModelSerializer):
    date = serializers.DateField(format="%b %d, %Y", read_only=True)
    user = serializers.CharField(source='user.get_fullname', read_only=True, default=None)
    added_by = serializers.CharField(source='added_by.get_fullname', read_only=True, default=None)
    class Meta:
        model = finance_voucher
        fields = '__all__'

class financeVoucherDataSerializer(serializers.ModelSerializer):
    transaction_code = serializers.CharField(source='transactionStatus.tracking_number', read_only=True, default=None)
    client_fullname = serializers.CharField(source='transactionStatus.client.client_bene_fullname', read_only=True, default=None)
    service_provider = serializers.CharField(source='transactionStatus.service_provider.name', read_only=True, default=None)
    Assistance_type = serializers.CharField(source='transactionStatus.lib_type_of_assistance.type_name', read_only=True, default=None)
    Assistance_category = serializers.CharField(source='transactionStatus.lib_assistance_category.name', read_only=True, default=None)
    dv_number = serializers.CharField(source='transactionStatus.dv_number', read_only=True, default=None)
    dv_date = serializers.DateField(source='transactionStatus.dv_date', format="%b %d, %Y", read_only=True)
    total = serializers.CharField(source='transactionStatus.total_amount', read_only=True, default=None)
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

# FINANCIAL TRANSACTION

class TransactionOutsideFOSerializer(serializers.ModelSerializer):
    voucher = serializers.CharField(source='voucher.voucher_title')
    service_provider = serializers.CharField(source='service_provider.name')
    class Meta:
        model = finance_outsideFo
        fields = '__all__'

