from django.contrib.auth import authenticate,logout, login as auth_login
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.http import JsonResponse
from django.shortcuts import render, redirect
from app.requests.models import SocialWorker_Status, TransactionStatus1
from app.models import AuthUser, AuthUserGroups, AuthGroup
from django.db.models import Value, Sum, Count, Q
from datetime import date
from app.libraries.models import Category, FundSource
from django.utils.encoding import smart_str
import csv
import xlwt
from rest_framework.decorators import api_view
from django.http import HttpResponse
from openpyxl import Workbook
from datetime import datetime
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from openpyxl.writer.excel import save_virtual_workbook
from openpyxl.styles import Font, PatternFill
from app.requests.models import ClientBeneficiary, ClientBeneficiaryFamilyComposition, \
	 Transaction, TransactionServiceAssistance, Mail, transaction_description, AssessmentProblemPresented, \
	uploadfile, TransactionStatus1, SocialWorker_Status
from app.finance.models import finance_voucher
from django.core.paginator import Paginator
from django.http import StreamingHttpResponse
from calendar import month_name
import time
# from suds.client import Client
import json
currentDateAndTime = datetime.now()
today = date.today()
month = today.strftime("%m")
year = today.strftime("%Y")

def get_transaction_summary():
	print(year)
	transaction_counts = (
		TransactionStatus1.objects
		.filter(status__in=[3, 6], verified_time_start__year=year)
		.values('verified_time_start__month')
		.annotate(count=Count('id'))
		.order_by('verified_time_start__month')
	)

	# Initialize a dictionary to hold the counts for each month
	monthly_transactions = {month: {'name': month_name[month], 'count': 0} for month in range(1, 13)}

	# Update the dictionary with the actual counts from the query
	for transaction in transaction_counts:
		month = transaction['verified_time_start__month']
		monthly_transactions[month]['count'] = transaction['count']

	# Convert the dictionary to a list
	monthly_transactions = list(monthly_transactions.values())
	
	client_categories = [
		"FHONA",
		"WEDC",
		"YNSP",
		"PWD",
		"SC",
		"PLHIV",
		"CNSP",
		"SA",
		"YTH",
		"PSN",
		"N/a",
		"Child",
		# Add more categories here
	]

	# Get the count of transactions for each client category in a single query
	transaction_counts = (
		TransactionStatus1.objects
		.filter(Q(status=3) | Q(status=6),verified_time_start__year=year)
		.values('transaction_id__client_category_id__acronym')
		.annotate(count=Count('id'))
	)

	# Initialize a dictionary to hold the counts for each client category
	summary_data_dict = {category: {'category': category, 'count': 0} for category in client_categories}

	# Update the dictionary with the actual counts from the query
	for transaction in transaction_counts:
		category = transaction['transaction_id__client_category_id__acronym']
		if category in summary_data_dict:
			summary_data_dict[category]['count'] = transaction['count']

	# Convert the dictionary to a list
	summary_data = list(summary_data_dict.values())

	# Define the list of client sub-categories
	client_sub_category = [
		"SP",
		"IP",
		"RPWUD",
		"4ps",
		"SD",
		"Disability",
		"Others",
		"N/a",
		"CNSP-Abandoned",
		"CNSP-Neglected",
		"CNSP-Voluntary Committed/Surrendered",
		"CNSP-Sexually-Abused",
		"CNSP-Sexually-Exploited",
		"CNSP-Physically-abused/maltreated/battered",
		"CNSP-Children in Situations of Armed Conflict",
		# Add more categories here
	]

	# Create a queryset that annotates the count of transactions for each sub-category
	transaction_counts = TransactionStatus1.objects.filter(
		Q(status=3) | Q(status=6), verified_time_start__year=year
	).values('transaction_id__client_sub_category_id__acronym').annotate(
		count=Count('id')
	).filter(
		transaction_id__client_sub_category_id__acronym__in=client_sub_category
	)

	# Convert the queryset to a dictionary for easier processing
	transaction_counts_dict = {
		item['transaction_id__client_sub_category_id__acronym']: item['count']
		for item in transaction_counts
	}

	# Generate the sub_category list
	sub_category = [
		{'category': category, 'count': transaction_counts_dict.get(category, 0)}
		for category in client_sub_category
	]

	# Count male and female transactions in a single query
	transaction_counts = TransactionStatus1.objects.filter(
		status__in=[3, 6], verified_time_start__year=year
	).aggregate(
    count_male=Count('transaction__client__id', filter=Q(transaction__client__sex__name="MALE"), distinct=True),
    count_female=Count('transaction__client__id', filter=Q(transaction__client__sex__name="FEMALE"), distinct=True),
    total_clients=Count('transaction__client__id', distinct=True),  # DISTINCT CLIENT COUNT AS ONE
    total_bene=Count('transaction__bene__id', distinct=True),
	)

	count_male = transaction_counts['count_male']
	count_female = transaction_counts['count_female']
	count_client = transaction_counts['total_clients']
	count_bene = transaction_counts['total_bene']


	# Define the list of disabilities
	disability = [
		"Deaf or Hard of Hearing",
		"INTELLECTUAL DISABILITY",
		"LEARNING DISABILITY",
		"MENTAL DISABILITY",
		"PHYSICAL DISABILITY",
		"PSYCHOSOCIAL DISABILITY",
		"SPEECH AND LANGUAGE IMPAIRMENT",
		"CANCER (RA11215)",
		"RARE DISEASE (RA10747)",
		"Visual Disability",
		"Psychosocial/Mental/Learning Disability"
		# Add more categories here
	]

	# Create a queryset that annotates the count of transactions for each disability
	disability_counts = TransactionStatus1.objects.filter(
		Q(status=3) | Q(status=6), verified_time_start__year=year
	).values('transaction_id__client_sub_category_id__name').annotate(
		count=Count('id')
	).filter(
		transaction_id__client_sub_category_id__name__in=disability
	)

	# Convert the queryset to a dictionary for easier processing
	disability_counts_dict = {
		item['transaction_id__client_sub_category_id__name']: item['count']
		for item in disability_counts
	}

	# Generate the disability_storage list
	disability_storage = [
		{'disability': item, 'count': disability_counts_dict.get(item, 0)}
		for item in disability
	]

	# Get the total amount for transactions in the specified year
	summary = TransactionStatus1.objects.filter(verified_time_start__year=year).aggregate(
		total_amount=Sum('transaction__total_amount')
	)

	# Format the total amount
	formatted_total_amount = "{:,.2f}".format(summary['total_amount'] if summary['total_amount'] else 0)

	return {
		'monthly_transactions': monthly_transactions,
		'summary_data': summary_data,
		'sub_category': sub_category,
		'count_male': count_male,
		'count_female': count_female,
		'count_client': count_client,
		'count_bene': count_bene,
		'disability_storage': disability_storage,
		'formatted_total_amount': formatted_total_amount,
	}


def queuing(request):
	transactions = TransactionStatus1.objects.filter(verified_time_start__date=today)
	context = {
		'transaction':transactions
	}
	return render(request, 'queuing.html', context)

def send_notification(message, contact_number):
	url = 'https://wiserv.dswd.gov.ph/soap/?wsdl'
	try:
		client = Client(url)
		result = client.service.sendMessage(UserName='crgwiservuser', PassWord='#w153rvcr9!', WSID='0',
											MobileNo=contact_number, Message=message)
	except Exception:
		pass

def landingpage(request):
	transaction_summary = get_transaction_summary()

	context = {
		'title': 'Landingpage',
		'summary_data': transaction_summary['summary_data'],
        'sub_category': transaction_summary['sub_category'],
        'monthly_transactions': transaction_summary['monthly_transactions'],
        'disability_storage': transaction_summary['disability_storage'],
        'count_male': transaction_summary['count_male'],
        'count_female': transaction_summary['count_female'],
        'count_client': transaction_summary['count_client'],
        'count_bene': transaction_summary['count_bene'],
        'formatted_total_amount': transaction_summary['formatted_total_amount'],
	}
	return render(request, 'landingpage.html', context)


def login(request):
	if request.user.is_authenticated:
		return redirect('home')
	if request.method == "POST":
		user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'), request=request)
		if user is not None and user.is_active:
			auth_login(request, user)
			return JsonResponse({'data': 'success'})
		else:
			return JsonResponse({'msg': 'Invalid username and password.'})
	return render(request, 'login.html') 

def log_out(request):
	logout(request)
	request.session.flush()  # Clear session data
	return redirect('login')


def media_access(request, path):    
	return render(request, '404.html')


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dashboard(request):
    # Call the get_transaction_summary function to get the summary data
    transaction_summary = get_transaction_summary()

    # Build the context using the data returned from the function
    context = {
        'title': 'Dashboard',
        'summary_data': transaction_summary['summary_data'],
        'sub_category': transaction_summary['sub_category'],
        'monthly_transactions': transaction_summary['monthly_transactions'],
        'disability_storage': transaction_summary['disability_storage'],
        'count_male': transaction_summary['count_male'],
        'count_female': transaction_summary['count_female'],
        'count_client': transaction_summary['count_client'],
        'count_bene': transaction_summary['count_bene'],
        'formatted_total_amount': transaction_summary['formatted_total_amount'],
    }

    return render(request, 'home.html', context)

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def transactionDashboard(request):
	transactions_per_swo = (
		TransactionStatus1.objects
		.filter(status__in=[3, 6])  # Filter transactions with status 3 or 6
		.values('transaction__swo_id','transaction__swo__first_name', 'transaction__swo__last_name')
		.annotate(transaction_count=Count('transaction__swo'))
		.order_by('-transaction_count')  # Order by transaction count in descending order
	)[:6]

	transaction_status_summary = (
		TransactionStatus1.objects
		.filter(status__in=[1, 2, 3, 4, 5, 6, 7])  # Filter transactions with status 3 or 6
		.values('status')
		.annotate(transaction_count=Count('status'))
		.order_by('-transaction_count')  # Order by transaction count in descending order
	)
	total_count = transaction_status_summary.aggregate(total_count=Sum('transaction_count'))['total_count']

	transaction_per_verifier = (
		ClientBeneficiary.objects
		.filter(registered_by__in=AuthUser.objects.filter(authusergroups__group__name="Verifier"))
		.values('registered_by__id', 'registered_by__first_name', 'registered_by__last_name')
		.annotate(transaction_count=Count('registered_by'))  # Count updates made by each user
		.order_by('-transaction_count')
	)

	requested_by_verifier = (
		TransactionStatus1.objects
		.filter(verifier__in=AuthUser.objects.filter(authusergroups__group__name="Verifier"))
		.values('verifier__id', 'verifier__first_name', 'verifier__last_name')
		.annotate(transaction_count=Count('verifier'))  # Count updates made by each user
		.order_by('-transaction_count')
	)

	case_study_per_swo = (
		TransactionStatus1.objects
		.filter(transaction__is_case_study=2, status__in=[3, 6])  # Filter transactions with status 3 or 6
		.values('transaction__swo_id','transaction__swo__first_name', 'transaction__swo__last_name')
		.annotate(
			transaction_count=Count('transaction__swo'),
			case_study_submitted=Count('case_study_status', filter=Q(case_study_status__isnull=False)),
		)
		.order_by('-transaction_count')  # Order by transaction count in descending order
	)
	page = request.GET.get('page', 1)
	rows = request.GET.get('rows', 6)

	total_case_study = case_study_per_swo.aggregate(total_count=Sum('transaction_count'))['total_count']

	context = {
		'title': 'Home',

		'transaction_per_swo':transactions_per_swo,#COUNT THE TOP 5 SERVING CLIENTS
		'summary_transactions':transaction_status_summary, # COUNT OF SUMMARY PER TRANSACTIONS
		'total_transactions': total_count,

		'transaction_per_verifier': transaction_per_verifier,
		'requested_by_verifier':requested_by_verifier,
		'data': Paginator(case_study_per_swo, rows).page(page),
		'total_case_study': total_case_study,
		'today':today,

	}
	return render(request, 'transactionDashboard.html', context)

@login_required
def status_activation(request,pk):
	if request.method == "POST":
		user = pk
		status = request.POST.get('status')
		table_number = request.POST.get('table_number')
		date = request.POST.get('date')

		filter = SocialWorker_Status.objects.filter(user_id=pk).first()
		if filter:
			SocialWorker_Status.objects.filter(user_id__id=pk).update(
				status=status,
				table=table_number,
				date_transaction=date
			)
			return JsonResponse({'data': 'success', 'msg': 'You are now active.'})
		else:
			SocialWorker_Status.objects.create(
				user_id=user,
				status=status,
				table=table_number,
				date_transaction=date
			)          
			return JsonResponse({'data': 'success', 'msg': 'You are now active.'})


@login_required
def mail(request):
	return render(request, 'mail.html')


@login_required
def layout_404(request):
	return render(request, '404.html')


@login_required
def print_ProvidedBYSWO(request):
	context = {
		'countingHotmeal':AuthUserGroups.objects.filter(group_id=2).order_by('id')
	}
	return render(request, 'provided_swo.html', context)


@csrf_exempt  # You can remove this decorator if CSRF protection is not needed
@api_view(['GET'])
def generateTransactions(request):
	if request.method == "GET":
		start_date_str = request.GET.get("start_date")
		end_date_str = request.GET.get("end_date")
		data = Transaction.objects.filter(
					swo_date_time_end__range=(start_date_str, end_date_str)
				).select_related(
					'client', 'bene', 'relation', 'lib_assistance_category', 'fund_source', 'swo'
				).filter(
					Q(status=3) | Q(status=6)
				)

		# Create a generator function to yield CSV rows
		def generate_csv():
			yield ','.join(['Field Office', 'Entered By', 'Client No', 'Date Accomplished', 'Region', 'Province', 'Municipality', 'Barangay', 'District', 'Last Name', 'First Name', 'Middle Name', 'Ext Name', 'Sex Name', 'Civil Status', 'DOB', 'Age', 'Mode of Admission', 'Type of Assistance', 'Amount', 'Source of Fund', 'Client Category', 'Sub Category', 'Mode of Assistance']) + '\n'
			for item in data:
				total_amount_str = str(item.total_amount)
				if ',' in total_amount_str:
					total_amount_str = total_amount_str.replace(',', '')
				yield ','.join([
					"Caraga",
					"BENGIE G. BOTOY",
					str(item.tracking_number),
					str(item.swo_date_time_end),
					str(item.client.barangay.city_code.prov_code.region_code.region_name),
					str(item.client.barangay.city_code.prov_code.prov_name),
					str(item.client.barangay.city_code.city_name),
					str(item.client.barangay.brgy_name),
					str(item.client.street),
					str(item.client.last_name),
					str(item.client.first_name),
					str(item.client.middle_name),
					str(item.client.suffix.name if item.client.suffix else ""),
					str(item.client.sex.name),
					str(item.client.civil_status.name),
					str(item.client.birthdate),
					str(item.client.age),
					"WALK-in / Referral" if item.is_referral else "Walk-in",
					str(item.lib_assistance_category.name),
					total_amount_str,
					str(item.fund_source.name if item.fund_source else ""),
					str(item.client_category.name),
					str(item.client_sub_category.name),
					"GL" if item.is_gl == 1 else "Cash"
				]) + '\n'

		response = StreamingHttpResponse(generate_csv(), content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="exported_data.csv"'
		return response

@csrf_exempt  # You can remove this decorator if CSRF protection is not needed
@api_view(['GET'])
def generateAICSData(request): #FOR GENERAL
	if request.method == "GET":
		start_date_str = request.GET.get("start_date")
		end_date_str = request.GET.get("end_date")
		data = Transaction.objects.filter(Q(status=3) | Q(status=6),
					date_of_transaction__range=(start_date_str, end_date_str)
				).select_related(
					'client', 'bene', 'relation', 'lib_assistance_category', 'fund_source', 'swo'
				)

		# Create a generator function to yield CSV rows
		def generate_csv():
			yield ','.join(['Tracking number','UUID',  'Date Accomplished',
				   'Last Name', 'First Name', 'Middle Name', 'Ext Name', 'Sex Name', 'Civil Status', 'DOB', 'Age',
				   '4ps member', '4ps ID no.', 'Client Category','Client Sub-Category',
				   'Region', 'Province', 'Municipality', 'Barangay', 'District', 
				   
				   'Bene UUID','Bene Last Name', 'Bene First Name', 'Bene Middle Name', 'Bene Ext Name', 'Bene Sex Name', 'Bene Civil Status', 'Bene DOB', 'Bene Age',
				   'Bene 4ps member', 'Bene 4ps ID no.', 'Bene Category','Bene Sub-Category',
				   'Region', 'Province', 'Municipality', 'Barangay', 'District', 

				   'Relationship', 'Type of Assistance', 'Amount', 
				   'Mode of Assistance','Source of referral','Source of Fund',
				   'Date Interviewed', 'Interviewer/Swo','Service Provider'
				   ]) + '\n'
			for item in data:
				total_amount_str = str(item.total_amount)
				if ',' in total_amount_str:
					total_amount_str = total_amount_str.replace(',', '')
				service_provider = str(item.service_provider.name).replace(",", "") if item.service_provider is not None else "N/a"
				swo_fullname_str = str(item.swo.first_name) + " " + str(item.swo.last_name)
				yield ','.join([
					str(item.tracking_number),
					str(item.client.unique_id_number),
					str(item.client.last_name),
					str(item.client.last_name),
					str(item.client.first_name),
					str(item.client.middle_name),
					str(item.client.suffix.name if item.client.suffix else ""),
					str(item.client.sex.name),
					str(item.client.civil_status.name),
					str(item.client.birthdate),
					str(item.client.age),
					str(item.client.is_4ps if item.client.number_4ps_id_number else "N/a"),
					str(item.client.number_4ps_id_number if item.client.number_4ps_id_number else "N/a"),
					str(item.client_category.name),
					str(item.client_sub_category.name),
					str(item.client.barangay.city_code.prov_code.region_code.region_name),
					str(item.client.barangay.city_code.prov_code.prov_name),
					str(item.client.barangay.city_code.city_name),
					str(item.client.barangay.brgy_name),
					str(item.client.street),

					str(item.bene.unique_id_number),
					str(item.bene.last_name),
					str(item.bene.first_name),
					str(item.bene.middle_name),
					str(item.bene.suffix.name if item.bene.suffix else ""),
					str(item.bene.sex.name),
					str(item.bene.civil_status.name),
					str(item.bene.birthdate),
					str(item.bene.age),
					str(item.bene.is_4ps if item.bene.number_4ps_id_number else "N/a"),
					str(item.bene.number_4ps_id_number if item.bene.number_4ps_id_number else "N/a"),
					str(item.bene_category.name),
					str(item.bene_sub_category.name),
					str(item.bene.barangay.city_code.prov_code.region_code.region_name),
					str(item.bene.barangay.city_code.prov_code.prov_name),
					str(item.bene.barangay.city_code.city_name),
					str(item.bene.barangay.brgy_name),
					str(item.bene.street),

					str(item.relation.name),
					str(item.lib_assistance_category.name),
					total_amount_str,
					"GL" if item.is_gl == 1 else "Cash",
					"Referral" if item.is_referral else "Walk-in",
					str(item.fund_source.name if item.fund_source else ""),
					str(item.swo_date_time_end),
					swo_fullname_str,
					service_provider,
				]) + '\n'

		response = StreamingHttpResponse(generate_csv(), content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="general_data.csv"'
		return response

@csrf_exempt  # You can remove this decorator if CSRF protection is not needed
@api_view(['GET'])
def personalData(request): #FOR GENERAL
	if request.method == "GET":
		data = TransactionStatus1.objects.filter(transaction__swo_id=request.user.id
				).select_related(
					'transaction__client', 'transaction__bene', 'transaction__relation', 'transaction__lib_assistance_category', 'transaction__fund_source', 'transaction__swo' 
				)

		# Create a generator function to yield CSV rows
		def generate_csv():
			yield ','.join(['Tracking number',  'Date Accomplished',
				   'Last Name', 'First Name', 'Middle Name', 'Ext Name', 'Sex Name', 'Civil Status', 'DOB', 'Age',
				   'Client Category','Client Sub-Category',
				   
				   'Bene Last Name', 'Bene First Name', 'Bene Middle Name', 'Bene Ext Name', 'Bene Sex Name', 'Bene Civil Status', 'Bene DOB', 'Bene Age',
				   'Bene Category','Bene Sub-Category',

				   'Relationship', 'Type of Assistance', 'Amount', 
				   'Mode of Assistance','Source of referral',
				   'Date Interviewed','For case study','Case Study Status','Transaction Status',
				   'Is_PFA', 'Is_SWC'
				   ]) + '\n'
			for item in data:
				total_amount_str = str(item.transaction.total_amount)
				if ',' in total_amount_str:
					total_amount_str = total_amount_str.replace(',', '')
				service_provider = str(item.transaction.service_provider.name).replace(",", "") if item.transaction.service_provider is not None else "N/a"

				status_str = (
					str("Resumed") if item.status == 7 else
					str("Completed") if item.status == 6 else
					str("Cancelled") if item.status == 5 else
					str("Pending") if item.status == 1 else
					str("Ongoing") if item.status == 2 else
					str("Completed") if item.status == 3 else
					"N/a"
				)
				is_pfa_str = item.transaction.is_pfa
				if is_pfa_str == 1:
					is_pfa_str = "PROVIDED WITH PFA"
				else:
					is_pfa_str = "N/A"

				is_swc_str = item.transaction.is_swc
				if is_swc_str == 1:
					is_swc_str = "PROVIDED WITH SWC"
				else:
					is_swc_str = "N/A"

				case_study_str = str(item.transaction.is_case_study)
				if case_study_str == "2":
					category_of_study_str = "CASE STUDY"
				else:
					category_of_study_str = "NOT CASE STUDY"

				case_study_status = str(item.case_study_status)
				if case_study_status == "1":
					case_study_result_str = "SUBMITTED"
				else:
					case_study_result_str = ""

				yield ','.join([
					str(item.transaction.tracking_number),
					str(item.swo_time_end),
					str(item.transaction.client.last_name),
					str(item.transaction.client.first_name),
					str(item.transaction.client.middle_name),
					str(item.transaction.client.suffix.name if item.transaction.client.suffix else ""),
					str(item.transaction.client.sex.name),
					str(item.transaction.client.civil_status.name),
					str(item.transaction.client.birthdate),
					str(item.transaction.client.age),
					str(item.transaction.client_category.name),
					str(item.transaction.client_sub_category.name),
					str(item.transaction.bene.last_name),
					str(item.transaction.bene.first_name),
					str(item.transaction.bene.middle_name),
					str(item.transaction.bene.suffix.name if item.transaction.bene.suffix else ""),
					str(item.transaction.bene.sex.name),
					str(item.transaction.bene.civil_status.name),
					str(item.transaction.bene.birthdate),
					str(item.transaction.bene.age),
					str(item.transaction.bene_category.name),
					str(item.transaction.bene_sub_category.name),
					str(item.transaction.relation.name),
					str(item.transaction.lib_assistance_category.name),
					total_amount_str,
					"GL" if item.transaction.is_gl == 1 else "Cash",
					"Referral" if item.transaction.is_referral else "Walk-in",
					str(item.transaction.swo_date_time_end),
					category_of_study_str,
					case_study_result_str,
					status_str,
					is_pfa_str,
					is_swc_str,
				]) + '\n'
		response = StreamingHttpResponse(generate_csv(), content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="personal_data.csv"'
		return response

@csrf_exempt  # You can remove this decorator if CSRF protection is not needed
@api_view(['GET'])
def generatePWD(request): #FOR GENERAL
	if request.method == "GET":
		start_date_str = request.GET.get("start_date")
		end_date_str = request.GET.get("end_date")
		data = TransactionStatus1.objects.filter(transaction__client_sub_category__acronym="Disability"
				).select_related(
					'transaction__client', 'transaction__bene', 'transaction__relation', 'transaction__lib_assistance_category', 'transaction__fund_source', 'transaction__swo'
				)

		# Create a generator function to yield CSV rows
		def generate_csv():
			yield ','.join(['Tracking number','UUID',  'Date Accomplished',
				   'Last Name', 'First Name', 'Middle Name', 'Ext Name', 'Sex Name', 'Civil Status', 'DOB', 'Age',
				   '4ps member', '4ps ID no.', 'Client Category','Client Sub-Category',
				   
				   'Bene UUID','Bene Last Name', 'Bene First Name', 'Bene Middle Name', 'Bene Ext Name', 'Bene Sex Name', 'Bene Civil Status', 'Bene DOB', 'Bene Age',
				   'Bene 4ps member', 'Bene 4ps ID no.', 'Bene Category','Bene Sub-Category',

				   'Relationship', 'Type of Assistance', 'Amount', 
				   'Mode of Assistance','Source of referral','Source of Fund',
				   'Date Interviewed', 'Interviewer/Swo','Service Provider',
				   ]) + '\n'
			for item in data:
				total_amount_str = str(item.transaction.total_amount)
				if ',' in total_amount_str:
					total_amount_str = total_amount_str.replace(',', '')
				service_provider = str(item.transaction.service_provider.name).replace(",", "") if item.transaction.service_provider is not None else "N/a"

				status_str = (
					str("Completed") if item.status == 6 else
					str("Cancelled") if item.status == 5 else
					str("Ongoing") if item.status == 2 else
					str("Completed") if item.status == 3 else
					"N/a"
				)

				case_study_str = str(item.transaction.is_case_study)
				if case_study_str == "2":
					category_of_study_str = "CASE STUDY"
				else:
					category_of_study_str = "NOT CASE STUDY"

				case_study_status = str(item.case_study_status)
				if case_study_status == "1":
					case_study_result_str = "SUBMITTED"
				else:
					case_study_result_str = ""

				yield ','.join([
					str(item.transaction.tracking_number),
					str(item.transaction.client.unique_id_number),
					str(item.swo_time_end),
					str(item.transaction.client.last_name),
					str(item.transaction.client.first_name),
					str(item.transaction.client.middle_name),
					str(item.transaction.client.suffix.name if item.transaction.client.suffix else ""),
					str(item.transaction.client.sex.name),
					str(item.transaction.client.civil_status.name),
					str(item.transaction.client.birthdate),
					str(item.transaction.client.age),
					str(item.transaction.client.is_4ps if item.transaction.client.number_4ps_id_number else "N/a"),
					str(item.transaction.client.number_4ps_id_number if item.transaction.client.number_4ps_id_number else "N/a"),
					str(item.transaction.client_category.name),
					str(item.transaction.client_sub_category.name),
					str(item.transaction.bene.unique_id_number),
					str(item.transaction.bene.last_name),
					str(item.transaction.bene.first_name),
					str(item.transaction.bene.middle_name),
					str(item.transaction.bene.suffix.name if item.transaction.bene.suffix else ""),
					str(item.transaction.bene.sex.name),
					str(item.transaction.bene.civil_status.name),
					str(item.transaction.bene.birthdate),
					str(item.transaction.bene.age),
					str(item.transaction.bene.is_4ps if item.transaction.bene.number_4ps_id_number else "N/a"),
					str(item.transaction.bene.number_4ps_id_number if item.transaction.bene.number_4ps_id_number else "N/a"),
					str(item.transaction.bene_category.name),
					str(item.transaction.bene_sub_category.name),
					str(item.transaction.relation.name),
					str(item.transaction.lib_assistance_category.name),
					total_amount_str,
					"GL" if item.transaction.is_gl == 1 else "Cash",
					"Referral" if item.transaction.is_referral else "Walk-in",
					str(item.transaction.fund_source.name if item.transaction.fund_source else ""),
					str(item.transaction.swo_date_time_end),
					str(item.transaction.swo.fullname),
					service_provider,
				]) + '\n'
		response = StreamingHttpResponse(generate_csv(), content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="PWD_REPORT.csv"'
		return response

@csrf_exempt  # You can remove this decorator if CSRF protection is not needed
@api_view(['GET'])
def generate_case_study(request):
	if request.method == "GET":
		start_date_str = request.GET.get("start_date")
		end_date_str = request.GET.get("end_date")
		data = TransactionStatus1.objects.filter(status__in=[3,6],
					swo_time_end__range=(start_date_str, end_date_str),transaction__is_case_study=2
				).select_related(
					'transaction__client', 'transaction__bene', 'transaction__relation', 'transaction__lib_assistance_category', 'transaction__fund_source', 'transaction__swo'
				)
		# Create a generator function to yield CSV rows
		def generate_csv():
			yield ','.join(['Tracking number', 'Date Accomplished', 'Last Name', 'First Name', 'Middle Name', 'Ext Name', 'Sex Name', 'DOB', 'Age', 
				   'Bene Last Name', 'Bene First Name', 'Bene Middle Name', 'Bene Ext Name', 'Bene Sex Name', 'Bene DOB', 'Bene Age',
					'Social Worker','Case Study','Amount','Status of Case Study','Date submitted']) + '\n'
			for item in data:
				total_amount_str = str(item.transaction.total_amount)
				if ',' in total_amount_str:
					total_amount_str = total_amount_str.replace(',', '')

				case_study_str = str(item.transaction.is_case_study)
				if case_study_str == "2":
					category_of_study_str = "CASE STUDY"
				else:
					category_of_study_str = "NOT CASE STUDY"

				case_study_status = str(item.case_study_status)
				if case_study_status == "1":
					case_study_result_str = "SUBMITTED"
				else:
					case_study_result_str = ""

				swo_fullname_str = str(item.transaction.swo.first_name) + " " + str(item.transaction.swo.last_name)

				yield ','.join([
					str(item.transaction.tracking_number),
					str(item.swo_time_end),
					str(item.transaction.client.last_name),
					str(item.transaction.client.first_name),
					str(item.transaction.client.middle_name),
					str(item.transaction.client.suffix.name if item.transaction.client.suffix else ""),
					str(item.transaction.client.sex.name),
					str(item.transaction.client.birthdate),
					str(item.transaction.client.age),
					str(item.transaction.bene.last_name),
					str(item.transaction.bene.first_name),
					str(item.transaction.bene.middle_name),
					str(item.transaction.bene.suffix.name if item.transaction.bene.suffix else ""),
					str(item.transaction.bene.sex.name),
					str(item.transaction.bene.birthdate),
					str(item.transaction.bene.age),
					swo_fullname_str,
					category_of_study_str,
					total_amount_str,
					case_study_result_str,
					str(item.case_study_date if item.case_study_date else "")

				]) + '\n'

		response = StreamingHttpResponse(generate_csv(), content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="Case_study.csv"'
		return response

@csrf_exempt  # You can remove this decorator if CSRF protection is not needed
@api_view(['GET'])
def withDvTransactions(request): #FOR GENERAL
	if request.method == "GET":
		data = finance_voucher.objects.filter(user_id=request.user.id,with_without_dv="WITH-DV") #USER_ID IS UPDATED BY
		# Create a generator function to yield CSV rows
		def generate_csv():
			yield ','.join(['VOUCHER CODE','VOUCHER TITLE', 'DATE', 'UPDATED BY']) + '\n'
			for item in data:
				yield ','.join([
					str(item.voucher_code),
					str(item.voucher_title),
					str(item.date),
					str(item.user.fullname)
				]) + '\n'
		response = StreamingHttpResponse(generate_csv(), content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="personal_data.csv"'
		return response
	
@csrf_exempt  # You can remove this decorator if CSRF protection is not needed
@api_view(['GET'])
def ExportBilledUnbilled(request):  # FOR GENERAL
	if request.method == "GET":
		# Select only the required fields
		data = Transaction.objects.filter(
			Q(status=3) | Q(status=6)
		).select_related(
			'fund_source', 'swo'
		).values(
			'tracking_number', 'total_amount', 'fund_source__name', 'dv_number', 'swo__first_name', 'swo__last_name', 'swo_date_time_end'
		)

		# Create a generator function to yield CSV rows
		def generate_csv():
			yield 'Tracking number,Amount of Assistance,Source of Fund,Billed/Unbilled,Interviewer/Swo,Date Accomplished\n'
			for item in data.iterator():  # Using iterator to efficiently handle large querysets
				total_amount_str = str(item['total_amount']) if item['total_amount'] is not None else '0'
				total_amount_str = total_amount_str.replace(',', '')
				swo_fullname_str = f"{item['swo__first_name']} {item['swo__last_name']}" if item['swo__first_name'] and item['swo__last_name'] else ''
				swo_date_time_end_str = str(item['swo_date_time_end']) if item['swo_date_time_end'] else ''

				yield ','.join([
					str(item['tracking_number']),
					total_amount_str,
					str(item['fund_source__name']) if item['fund_source__name'] else "",
					"Billed" if item['dv_number'] else "Unbilled",
					swo_fullname_str,
					swo_date_time_end_str,
				]) + '\n'

		response = StreamingHttpResponse(generate_csv(), content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="billed_unbilled.csv"'
		return response