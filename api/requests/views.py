from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from api.requests.serializers import TransactionSerializer, Transaction_DescriptionSerializer, FinanceVoucherSerializer, financeVoucherDataSerializer, TransactionsSignatoriesSerializer
from app.requests.models import Transaction, transaction_description, TransactionStatus1
from app.finance.models import finance_voucher, finance_voucherData
from datetime import datetime, timedelta, time, date
today = date.today()
# class TransactionViews(generics.ListAPIView):
#     serializer_class = TransactionSerializer
#     permission_classes = [IsAuthenticated]
#     queryset = TransactionStatus1.objects.filter(is_swo=None).order_by('-id')

class TransactionPerSession(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        if self.request.query_params.get('user'):
            queryset = TransactionStatus1.objects.filter(transaction_id__swo_id=self.request.query_params.get('user')).order_by('-id')
            return queryset
        else:
            queryset = TransactionStatus1.objects.all().order_by('-id')
            return queryset

    
class CompletedTransactionViews(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    queryset = TransactionStatus1.objects.filter(is_verified=1,is_swo=1).order_by('-id')


class TransactionDescriptionViews(generics.ListAPIView):
    serializer_class = Transaction_DescriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.query_params.get('data'):
            queryset = transaction_description.objects.filter(tracking_number_id=self.request.query_params.get('data')).order_by('-id')
            return queryset
        else:
            queryset = Transaction.objects.all()
            return queryset

#FOR THE FINANCE
class AdvanceFinanceFilterViews(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        if self.request.query_params.get('provider'):
            queryset = TransactionStatus1.objects.filter(transaction__service_provider_id=self.request.query_params.get('provider'))
            return queryset
        else:
            queryset = TransactionStatus1.objects.filter(is_verified=1,is_swo=1).order_by('-id')
            return queryset

class FinanceVoucherViews(generics.ListAPIView):
    serializer_class = FinanceVoucherSerializer
    permission_class = [IsAuthenticated]
    queryset = finance_voucher.objects.all().order_by('-id')


class VoucherDataViews(generics.ListAPIView):
    serializer_class = financeVoucherDataSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.query_params.get('data'):
            queryset = finance_voucherData.objects.filter(voucher_id=self.request.query_params.get('data')).order_by('-id')
            return queryset

class SignatoriesTransactionsViews(generics.ListAPIView):
    serializer_class = TransactionsSignatoriesSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        if self.request.query_params.get('user'):
            queryset = TransactionStatus1.objects.filter(transaction_id__signatories_id=self.request.query_params.get('user'),transaction_id__is_gl=1).order_by('-id')
            return queryset
        else:
            queryset = TransactionStatus1.objects.filter(transaction_id__is_gl=1).order_by('-id')
            return queryset
