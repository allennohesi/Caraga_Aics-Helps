from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from api.requests.serializers import TransactionSerializer, Transaction_DescriptionSerializer, FinanceVoucherSerializer, financeVoucherDataSerializer, TransactionsSignatoriesSerializer
from app.requests.models import Transaction, transaction_description, TransactionStatus1
from app.finance.models import finance_voucher, finance_voucherData
from datetime import datetime, timedelta, time, date
from django.db.models import Q
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.pagination import PageNumberPagination
today = date.today()
# class TransactionViews(generics.ListAPIView):
#     serializer_class = TransactionSerializer
#     permission_classes = [IsAuthenticated]
#     queryset = TransactionStatus1.objects.filter(is_swo=None).order_by('-id')

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 30

class TransactionPerSession(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LargeResultsSetPagination
    
    def get_queryset(self):
        if self.request.query_params.get('user'):
            queryset = TransactionStatus1.objects.filter(
                Q(transaction_id__swo_id=self.request.query_params.get('user'),status=1) | 
                Q(transaction_id__swo_id=self.request.query_params.get('user'),status=2) | 
                Q(transaction_id__swo_id=self.request.query_params.get('user'),status=3) |
                Q(transaction_id__swo_id=self.request.query_params.get('user'),status=4) |
                Q(transaction_id__swo_id=self.request.query_params.get('user'),status=7) 
                ).order_by('-id')
            return queryset
        else:
            queryset = TransactionStatus1.objects.all().order_by('-id')
            return queryset

class TransactionPerSessionAllViews(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LargeResultsSetPagination
    def get_queryset(self):
        if self.request.query_params.get('user'):
            queryset = TransactionStatus1.objects.filter(transaction_id__swo_id=self.request.query_params.get('user')).exclude(status__in=[1, 2, 3, 4, 7]).order_by('-id')
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

#SIGNATORIES
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


#CASH TRANSACTION
class CashTransactionViews(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LargeResultsSetPagination
    queryset = TransactionStatus1.objects.filter(transaction_id__is_gl=0, status__in=[6, 3]).order_by('-id')