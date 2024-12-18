from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from api.requests.serializers import TransactionSerializer, Transaction_DescriptionSerializer, FinanceVoucherSerializer, financeVoucherDataSerializer, TransactionsSignatoriesSerializer, \
								TransactionOutsideFOSerializer, DisbursementVoucherSerializer
from app.requests.models import Transaction, transaction_description, TransactionStatus1
from app.finance.models import finance_voucher, finance_voucherData, finance_outsideFo, disbursementVoucher
from datetime import datetime, timedelta, time, date
from django.db.models import Q
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from datetime import timedelta
now = timezone.now()
today = date.today()

seven_months_ago = now - timedelta(days=30 * 7)
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

class queuingAPI(generics.ListAPIView):
	serializer_class = TransactionSerializer
	permission_classes = [IsAuthenticated]
	pagination_class = LargeResultsSetPagination
	queryset = TransactionStatus1.objects.filter(verified_time_start__date=today,status__in=[2,7],transaction_id__requested_in="AGUSAN DEL NORTE").order_by('-id')

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

class CaseStudyDeadline(generics.ListAPIView):
	serializer_class = TransactionSerializer
	permission_classes = [IsAuthenticated]
	pagination_class = LargeResultsSetPagination
	def get_queryset(self):
		if self.request.query_params.get('user'):
			user_id = self.request.query_params.get('user')
			queryset = TransactionStatus1.objects.filter(
				transaction_id__swo_id=user_id,
				transaction_id__is_case_study=2,
				case_study_status__isnull=True,
				status__in=[3, 6],
			).order_by('-id')
			return queryset

class TransactionAdvanceSearch(generics.ListAPIView):
	serializer_class = TransactionSerializer
	permission_classes = [IsAuthenticated]
	pagination_class = LargeResultsSetPagination
	def get_queryset(self):
		queryset = TransactionStatus1.objects.none() 
		name = self.request.query_params.get('name')
		queryset = TransactionStatus1.objects.filter(
			Q(transaction_id__client_id=name) | Q(transaction_id__bene_id=name)
		).order_by('-id')
		return queryset

class TransactionIncoming(generics.ListAPIView):
	serializer_class = TransactionSerializer
	permission_classes = [IsAuthenticated]
	pagination_class = LargeResultsSetPagination

	def get_queryset(self):
		"""Construct queryset based on query parameters."""
		queryset = TransactionStatus1.objects.none()  # Default empty queryset
		requested_in = self.request.query_params.get('region')
		year = self.request.query_params.get("year")
		dropdown = self.request.query_params.get("dropdown")
		code = self.request.query_params.get("code")
		aoa = self.request.query_params.get("aoa")
		
		# Filter by year and region
		if year:
			queryset = TransactionStatus1.objects.filter(
				verified_time_start__year=year,
				transaction_id__office_station_in_id=requested_in,
				verified_time_start__gte=seven_months_ago
			).order_by('-id')

		# Filter by code and region
		elif code:
			queryset = TransactionStatus1.objects.filter(
				transaction__fund_source__name=code,
				transaction_id__office_station_in_id=requested_in,
				verified_time_start__gte=seven_months_ago
			).order_by('-id')

		# Filter by AOA
		elif aoa:
			queryset = TransactionStatus1.objects.filter(
				transaction_id__office_station_in_id=aoa,
				verified_time_start__gte=seven_months_ago
			).order_by('-id')

		# Filter by dropdown options
		elif dropdown:
			dropdown_filters = {
				"0": {"status__in": [1, 2, 3, 4], "verified_time_start__gte": seven_months_ago},
				"1": {"status__in": [3, 6], "verified_time_start__gte": seven_months_ago},  # COMPLETED
				"4": {"case_study_status": 1, "verified_time_start__gte": seven_months_ago},  # SUBMITTED CASE STUDY
				"5": {"transaction__dv_number__isnull": False, "verified_time_start__gte": seven_months_ago},  # WITH DV
				"6": {"verified_time_start__gte": seven_months_ago},  # ALL TRANSACTIONS
			}
			filter_params = dropdown_filters.get(dropdown)
			if filter_params:
				queryset = TransactionStatus1.objects.filter(
					transaction_id__office_station_in_id=requested_in,
					**filter_params
				).order_by('-id')

		# Default filter (e.g., today's transactions)
		else:
			queryset = TransactionStatus1.objects.filter(
				verified_time_start__date=today,
				status__in=[1, 2, 3, 4, 7],
				transaction_id__office_station_in_id=requested_in,
				verified_time_start__gte=seven_months_ago
			).order_by('-id')

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
		
class DisbursementDataViews(generics.ListAPIView):
	serializer_class = DisbursementVoucherSerializer
	permission_class = [IsAuthenticated]
	pagination_class = LargeResultsSetPagination
	queryset = disbursementVoucher.objects.all().order_by('-id')

#CASH TRANSACTION
class CashTransactionViews(generics.ListAPIView):
	serializer_class = TransactionSerializer
	permission_classes = [IsAuthenticated]
	pagination_class = LargeResultsSetPagination

	def get_queryset(self):
		region = self.request.query_params.get('region')
		queryset = TransactionStatus1.objects.filter(transaction_id__is_gl=0,transaction_id__requested_in=region, status__in=[6, 3]).order_by('-id')
		return queryset
	

#SERVICE PROVIDER
class ServiceProviderMonitoring(generics.ListAPIView):
	serializer_class = TransactionSerializer
	permission_classes = [IsAuthenticated]
	pagination_class = LargeResultsSetPagination
	def get_queryset(self):
		if self.request.query_params.get('sp_id'):
			sp_id = self.request.query_params.get('sp_id')
			queryset = TransactionStatus1.objects.filter(
				transaction_id__service_provider_id=sp_id,
				status__in=[3, 6],
			).order_by('-id')
			return queryset