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
			queryset = TransactionStatus1.objects.all().exclude(status__in=[1, 2, 3, 4, 7]).order_by('-id') # FILTER ONLY THE DONE EXCLUDE
			return queryset


class TransactionPerSession(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        # Retrieve common parameters
        region = self.request.query_params.get('region')
        user = self.request.query_params.get('user')
        current_year = self.request.query_params.get('current_year')  # Default to current year

        # If 'user' is specified, return transactions for the user
        if user:
            return TransactionStatus1.objects.filter(
                transaction_id__swo_id=user,
                status__in=[1, 2, 3, 4, 7]
            ).order_by('-id')

        # Initialize an empty queryset
        queryset = TransactionStatus1.objects.none()

        # Check the 'billed' parameter and apply filters accordingly
        billed_param = self.request.query_params.get("billed")
        if billed_param:
            billed_param = billed_param.lower()
            if billed_param == "true":
                return TransactionStatus1.objects.filter(
                    verified_time_start__year=current_year,
                    transaction__dv_number__isnull=False,
                    transaction_id__requested_in=region
                ).order_by('-id')

            if billed_param == "false":
                return TransactionStatus1.objects.filter(
                    verified_time_start__year=current_year,
                    transaction__dv_number__isnull=True,
                    transaction_id__requested_in=region
                ).order_by('-id')

            if billed_param == "completed":
                return TransactionStatus1.objects.filter(
                    verified_time_start__year=current_year,
                    status=6,
                    transaction_id__requested_in=region
                ).order_by('-id')

            if billed_param == "cancelled":
                return TransactionStatus1.objects.filter(
                    verified_time_start__year=current_year,
                    status=5,
                    transaction_id__requested_in=region
                ).order_by('-id')

            if billed_param == "for_case_study":
                return TransactionStatus1.objects.filter(
                    verified_time_start__year=current_year,
                    transaction__is_case_study=2,
                    transaction_id__requested_in=region,
                    status__in=[3, 6]
                ).order_by('-id')

            if billed_param == "submitted_case_study":
                return TransactionStatus1.objects.filter(
                    verified_time_start__year=current_year,
                    case_study_status=1,
                    transaction_id__requested_in=region,
                    status__in=[3, 6]
                ).order_by('-id')

            if billed_param == "all_transactions":
                return TransactionStatus1.objects.all().order_by('-id')

        # If 'billed' parameter is not given, check 'year' or 'code'
        year = self.request.query_params.get("year", current_year)
        code = self.request.query_params.get("code")

        if code:
            return TransactionStatus1.objects.filter(
                transaction__fund_source__name=code,
                transaction_id__requested_in=region
            ).order_by('-id')

        # Default queryset if no other condition is met
        return TransactionStatus1.objects.filter(
            verified_time_start__year=year,
            status__in=[1, 2, 3, 4],
            transaction_id__requested_in=region
        ).order_by('-id')


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
	queryset = finance_voucher.objects.all().order_by('-id')


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