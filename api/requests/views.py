from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from api.requests.serializers import TransactionSerializer, Transaction_DescriptionSerializer, FinanceVoucherSerializer, financeVoucherDataSerializer, TransactionsSignatoriesSerializer, \
								TransactionOutsideFOSerializer
from app.requests.models import Transaction, transaction_description, TransactionStatus1
from app.finance.models import finance_voucher, finance_voucherData, finance_outsideFo
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
	max_page_size = 200

class kioskAPI(generics.ListAPIView):
	serializer_class = TransactionSerializer
	permission_classes = [IsAuthenticated]
	pagination_class = LargeResultsSetPagination
	queryset = TransactionStatus1.objects.filter(verified_time_start__date=today,status__in=[1,2,3,4,7]).order_by('-id')

class adminMonitoring(generics.ListAPIView):
	serializer_class = TransactionSerializer
	permission_classes = [IsAuthenticated]
	pagination_class = LargeResultsSetPagination
	def get_queryset(self):
		ongoing = self.request.query_params.get('ongoing')
		if ongoing:
			queryset = TransactionStatus1.objects.filter(
				status__in=[1, 2, 3, 4, 7]
			).order_by('-id')
			return queryset
		else:
			queryset = TransactionStatus1.objects.all().exclude(status__in=[1, 2, 3, 4, 7]).order_by('-id') # FILTER ONLY THE PENDING
			return queryset


class TransactionPerSession(generics.ListAPIView):
	serializer_class = TransactionSerializer
	permission_classes = [IsAuthenticated]
	pagination_class = LargeResultsSetPagination
	def get_queryset(self):
		if self.request.query_params.get('user'):
			queryset = TransactionStatus1.objects.filter(
				transaction_id__swo_id=self.request.query_params.get('user'),
				status__in=[1, 2, 3, 4, 7]
			).order_by('-id')
			return queryset

class TransactionIncoming(generics.ListAPIView):
	serializer_class = TransactionSerializer
	permission_classes = [IsAuthenticated]
	pagination_class = LargeResultsSetPagination
	def get_queryset(self):
		queryset = TransactionStatus1.objects.none() 
		region = self.request.query_params.get('region')
		year = self.request.query_params.get("year")
		dropdown = self.request.query_params.get("dropdown")
		code = self.request.query_params.get("code")
		
		if year:
			queryset = TransactionStatus1.objects.filter(verified_time_start__year=year,transaction_id__requested_in=region).order_by('-id')
		elif code:
			queryset = TransactionStatus1.objects.filter(transaction__fund_source__name=code,transaction_id__requested_in=region).order_by('-id')

		elif dropdown:
			if dropdown == "0":
				queryset = TransactionStatus1.objects.filter(status__in=[1,2,3,4],transaction_id__requested_in=region).order_by('-id')
			elif dropdown == "1": #COMPLETED
				queryset = TransactionStatus1.objects.filter(status__in=[3, 6],transaction_id__requested_in=region).order_by('-id')
			elif dropdown == "4": #SUBMITTED CASE STUDY
				queryset = TransactionStatus1.objects.filter(case_study_status=1,transaction_id__requested_in=region).order_by('-id')
			elif dropdown == "5": #WITH DV
				queryset = TransactionStatus1.objects.filter(transaction__dv_number__isnull=False,transaction_id__requested_in=region).order_by('-id')
			elif dropdown == "6": #ALL TRANSACTION
				queryset = TransactionStatus1.objects.all().order_by('-id')
			return queryset
		else:
			queryset = TransactionStatus1.objects.filter(verified_time_start__date=today,status__in=[1,2,3,4,7],transaction_id__requested_in=region).order_by('-id')

		return queryset


class TransactionPerSessionAllViews(generics.ListAPIView):
	serializer_class = TransactionSerializer
	permission_classes = [IsAuthenticated]
	pagination_class = LargeResultsSetPagination
	def get_queryset(self):
		if self.request.query_params.get('user'):
			queryset = TransactionStatus1.objects.filter(transaction_id__swo_id=self.request.query_params.get('user')).exclude(status__in=[1, 2, 3, 4, 7]).order_by('-id') # FILTER ONLY THE DONE EXCLUDE
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
	def get_queryset(self):
		queryset = finance_voucher.objects.none()
		dropdown = self.request.query_params.get("dropdown")
		if dropdown:
			queryset = finance_voucher.objects.filter(with_without_dv=dropdown).order_by('-id')
		else:
			queryset = finance_voucher.objects.all().order_by('-id')
		return queryset


class VoucherDataViews(generics.ListAPIView):
	serializer_class = financeVoucherDataSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		if self.request.query_params.get('data'):
			queryset = finance_voucherData.objects.filter(voucher_id=self.request.query_params.get('data')).order_by('-id')
			return queryset

class OutsideFoDataViews(generics.ListAPIView):
	serializer_class = TransactionOutsideFOSerializer
	permission_classes = [IsAuthenticated]
	pagination_class = LargeResultsSetPagination
	queryset = finance_outsideFo.objects.all().order_by('-id')
		
#CASH TRANSACTION
class CashTransactionViews(generics.ListAPIView):
	serializer_class = TransactionSerializer
	permission_classes = [IsAuthenticated]
	pagination_class = LargeResultsSetPagination

	def get_queryset(self):
		region = self.request.query_params.get('region')
		queryset = TransactionStatus1.objects.filter(transaction_id__is_gl=0,transaction_id__requested_in=region, status__in=[6, 3]).order_by('-id')
		return queryset