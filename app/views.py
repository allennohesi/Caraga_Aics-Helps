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
from django.views.decorators.csrf import csrf_exempt
from openpyxl.writer.excel import save_virtual_workbook
from openpyxl.styles import Font, PatternFill
from app.requests.models import ClientBeneficiary, ClientBeneficiaryFamilyComposition, \
	 Transaction, TransactionServiceAssistance, Mail, transaction_description, AssessmentProblemPresented, \
	uploadfile, TransactionStatus1, SocialWorker_Status
from django.core.paginator import Paginator
from django.http import StreamingHttpResponse
# from suds.client import Client

currentDateAndTime = datetime.now()
today = date.today()
month = today.strftime("%m")
year = today.strftime("%Y")



def send_notification(message, contact_number):
	url = 'https://wiserv.dswd.gov.ph/soap/?wsdl'
	try:
		client = Client(url)
		result = client.service.sendMessage(UserName='crgwiservuser', PassWord='#w153rvcr9!', WSID='0',
											MobileNo=contact_number, Message=message)
	except Exception:
		pass

def landingpage(request):
	context = {
		'title': 'Home'
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
	# url = 'https://wiserv.dswd.gov.ph/soap/?wsdl'
	# client = Client(url)
	# result = client.service.sendMessage(UserName='crgwiservuser', PassWord='#w153rvcr9!', WSID='0',
	# 									MobileNo="09567114086", Message="Serving our clients gently is like tending to a delicate flower; with patience and tenderness, we nurture their needs and watch them bloom with satisfaction. - AICS-Helps")

	am = AuthUserGroups.objects.all().filter(group_id=3).count() #adminCount
	swo = AuthUserGroups.objects.all().filter(group_id=2).count() #SwoCount
	sp = AuthUserGroups.objects.all().filter(group_id=4).count() #ServiceProvider
	vr = AuthUserGroups.objects.all().filter(group_id=1).count() #verifier

	active_emp = AuthUser.objects.filter(is_active=1).count()
	inactive_emp = AuthUser.objects.filter(is_active=0).count()

	# active_emp = AuthUser.objects.filter(is_active=1).count()

	fa = TransactionStatus1.objects.filter(
		Q(transaction_id__lib_type_of_assistance_id__type_name="Financial Assistance") &
		(Q(status=3) | Q(status=6))
		).count()
	ma = TransactionStatus1.objects.filter(
		Q(transaction_id__lib_type_of_assistance_id__type_name="Material Assistance") &
		(Q(status=3) | Q(status=6))
		).count()
	psych = TransactionStatus1.objects.filter(
		Q(transaction_id__lib_type_of_assistance_id__type_name="Psychosocial") &
		(Q(status=3) | Q(status=6))
		).count()

	pending = TransactionStatus1.objects.filter(status=1).count()
	ongoing = TransactionStatus1.objects.filter(status=2).count()
	completed = TransactionStatus1.objects.filter(
				Q(status=3) | Q(status=6)
				).count()
	hold = TransactionStatus1.objects.filter(status=4).count()
	cancelled = TransactionStatus1.objects.filter(status=5).count()
	
	transactions_per_swo = (
		TransactionStatus1.objects
		.filter(status__in=[3, 6])  # Filter transactions with status 3 or 6
		.values('transaction__swo_id','transaction__swo__first_name', 'transaction__swo__last_name')
		.annotate(transaction_count=Count('transaction__swo'))
		.order_by('-transaction_count')  # Order by transaction count in descending order
	)[:5]

	transaction_status_summary = (
		TransactionStatus1.objects
		.filter(status__in=[1, 2, 3, 4, 5, 6])  # Filter transactions with status 3 or 6
		.values('status')
		.annotate(transaction_count=Count('status'))
		.order_by('-transaction_count')  # Order by transaction count in descending order
	)
	transaction_status_summary = (
		TransactionStatus1.objects
		.filter(status__in=[1, 2, 3, 4, 5, 6])  # Filter transactions with status 3 or 6
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
	)[:5]

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
	rows = request.GET.get('rows', 5)
	total_case_study = case_study_per_swo.aggregate(total_count=Sum('transaction_count'))['total_count']

	context = {
		'title': 'Home',
		'am':am,
		'swo':swo,
		'sp':sp,
		'vr':vr,
		'active_emp':active_emp,
		'inactive_emp':inactive_emp,

		'financial': fa,
		'material': ma,
		'psychological':psych,

		'pending':pending,
		'ongoing':ongoing,
		'completed':completed,
		'hold':hold,
		'cancelled':cancelled,

		'transaction_per_swo':transactions_per_swo, #COUNT THE TOP 5 SERVING CLIENTS
		'summary_transactions':transaction_status_summary, # COUNT OF SUMMARY PER TRANSACTIONS
		'total_transactions': total_count,

		'transaction_per_verifier': transaction_per_verifier,
		'data': Paginator(case_study_per_swo, rows).page(page),
		'total_case_study': total_case_study,
		'fund_source': FundSource.objects.all(),
		'today':today,
	}
	return render(request, 'home.html', context)

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
		start_date_str = request.GET.get("start_date")
		end_date_str = request.GET.get("end_date")
		data = TransactionStatus1.objects.filter(transaction__swo_id=request.user.id
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
				   'Purpose','Date Interviewed', 'Interviewer/Swo','Service Provider','For case study','Transaction Category','Case study status', 'Status of transaction'
				   ]) + '\n'
			for item in data:
				total_amount_str = str(item.transaction.total_amount)
				if ',' in total_amount_str:
					total_amount_str = total_amount_str.replace(',', '')
				service_provider = str(item.transaction.service_provider.name).replace(",", "") if item.transaction.service_provider is not None else "N/a"
				swo_fullname_str = str(item.transaction.swo.first_name) + " " + str(item.transaction.swo.last_name)

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
					str(item.transaction.purpose),
					str(item.transaction.swo_date_time_end),
					swo_fullname_str,
					service_provider,
					category_of_study_str,
					case_study_result_str,
					status_str,
				]) + '\n'
		response = StreamingHttpResponse(generate_csv(), content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="personal_data.csv"'
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

def generate_testXLS(request,pk):
	from openpyxl.styles import NamedStyle
	today = datetime.today()
	year = today.strftime("%Y")
	workbook = Workbook()
	worksheet = workbook.active
	worksheet.title = 'USER AVAIL ' + year
	wsrow = 2

	
	blue = PatternFill(start_color='92D4F0',
					end_color='92D4F0',
					fill_type='solid')

	worksheet['A1'] = 'Transaction No'
	worksheet['B1'] = 'Time of Transaction'
	worksheet['C1'] = 'Date of Transaction'

	worksheet['A1'].fill = blue
	worksheet['B1'].fill = blue
	worksheet['C1'].fill = blue

	darkblue = PatternFill(start_color='AAC4F2',
					end_color='AAC4F2',
					fill_type='solid')

	worksheet['D1'] = 'BENE LAST NAME'
	worksheet['E1'] = 'BENE FIRST NAME'
	worksheet['F1'] = 'BENE MIDDLE NAME'
	worksheet['G1'] = 'BENE EXT'
	worksheet['H1'] = 'BENE BIRTH DATE'
	worksheet['I1'] = 'BENE PUROK'
	worksheet['J1'] = 'BENE BARANGAY'
	worksheet['K1'] = 'BENE MUNICIPALITY'
	worksheet['L1'] = 'BENE DISTRICT'
	worksheet['M1'] = 'BENE PROVINCE'
	worksheet['N1'] = 'BENE REGION'
	worksheet['O1'] = 'BENE SEX'
	worksheet['P1'] = 'BENE OCCUPATION'
	worksheet['Q1'] = 'BENE INCOME'
	worksheet['R1'] = 'BENE INCOME'
	worksheet['S1'] = 'BENE OCCUPATION'

	worksheet['T1'] = 'CLIENT LAST NAME'
	worksheet['U1'] = 'CLIENT FIRST NAME'
	worksheet['V1'] = 'CLIENT MIDDLE NAME'
	worksheet['W1'] = 'CLIENT EXT'
	worksheet['X1'] = 'CLIENT BIRTH DATE'
	worksheet['Y1'] = 'CLIENT PUROK'
	worksheet['Z1'] = 'CLIENT BARANGAY'
	worksheet['AA1'] = 'CLIENT MUNICIPALITY'
	worksheet['BB1'] = 'CLIENT DISTRICT'
	worksheet['CC1'] = 'CLIENT PROVINCE'
	worksheet['DD1'] = 'CLIENT REGION'
	worksheet['EE1'] = 'CLIENT SEX'
	worksheet['FF1'] = 'CLIENT OCCUPATION'
	worksheet['GG1'] = 'CLIENT INCOME'


	worksheet['D1'].fill = darkblue
	worksheet['E1'].fill = darkblue
	worksheet['F1'].fill = darkblue
	worksheet['G1'].fill = darkblue
	worksheet['H1'].fill = darkblue
	worksheet['I1'].fill = darkblue
	worksheet['J1'].fill = darkblue
	worksheet['K1'].fill = darkblue
	worksheet['L1'].fill = darkblue
	worksheet['M1'].fill = darkblue
	worksheet['N1'].fill = darkblue
	worksheet['O1'].fill = darkblue
	worksheet['P1'].fill = darkblue
	worksheet['Q1'].fill = darkblue

	worksheet['A1'].font = Font(bold=True)
	worksheet['B1'].font = Font(bold=True)
	worksheet['C1'].font = Font(bold=True)
	worksheet['D1'].font = Font(bold=True)
	worksheet['E1'].font = Font(bold=True)
	worksheet['F1'].font = Font(bold=True)
	worksheet['G1'].font = Font(bold=True)
	worksheet['H1'].font = Font(bold=True)
	worksheet['I1'].font = Font(bold=True)
	worksheet['J1'].font = Font(bold=True)
	worksheet['K1'].font = Font(bold=True)
	worksheet['L1'].font = Font(bold=True)
	worksheet['M1'].font = Font(bold=True)
	worksheet['N1'].font = Font(bold=True)
	worksheet['O1'].font = Font(bold=True)
	worksheet['P1'].font = Font(bold=True)
	worksheet['Q1'].font = Font(bold=True)
	worksheet['R1'].font = Font(bold=True)
	worksheet['S1'].font = Font(bold=True)
	worksheet['T1'].font = Font(bold=True)
	worksheet['U1'].font = Font(bold=True)
	worksheet['V1'].font = Font(bold=True)
	worksheet['W1'].font = Font(bold=True)
	worksheet['X1'].font = Font(bold=True)
	worksheet['Y1'].font = Font(bold=True)
	worksheet['Z1'].font = Font(bold=True)

	
	transaction = TransactionStatus1.objects.filter(status=6,transaction__swo_id=pk).values('transaction__tracking_number','verified_time_start','transaction__bene__last_name','transaction__bene__first_name', \
		'transaction__bene__middle_name','transaction__bene__suffix__name','transaction__bene__birthdate','transaction__bene__street','transaction__bene__house_no', 'transaction__bene__barangay__brgy_name', \
			'transaction__bene__barangay__city_code__city_name', 'transaction__bene__barangay__city_code__prov_code__prov_name','transaction__bene__barangay__city_code__prov_code__region_code__region_name', \
				'transaction__bene__occupation__occupation_name','transaction__bene__salary','transaction__bene__sex__name', 'transaction__client__last_name','transaction__client__first_name', \
					'transaction__client__middle_name','transaction__client__suffix__name','transaction__client__birthdate','transaction__client__street','transaction__client__house_no', 'transaction__client__barangay__brgy_name', \
						'transaction__client__barangay__city_code__city_name', 'transaction__client__barangay__city_code__prov_code__prov_name','transaction__client__barangay__city_code__prov_code__region_code__region_name', \
							'transaction__client__occupation__occupation_name','transaction__client__salary','transaction__client__sex__name','upload_time_end')
	if transaction:
		for indx, row in enumerate(transaction):
			dateoftransaction = row['verified_time_start'].strftime("%I:%M %p")
			transactionDate = row['verified_time_start'].strftime("%B %d, %Y")
			birth_date = row['transaction__bene__birthdate'].strftime("%B %d, %Y")

			client_birth_date = row['transaction__client__birthdate'].strftime("%B %d, %Y")

			worksheet['A' + str(wsrow)] = row['transaction__tracking_number']
			worksheet['B' + str(wsrow)] = dateoftransaction
			worksheet['C' + str(wsrow)] = transactionDate
			worksheet['D' + str(wsrow)] = row['transaction__bene__last_name']
			worksheet['E' + str(wsrow)] = row['transaction__bene__first_name']
			worksheet['F' + str(wsrow)] = row['transaction__bene__middle_name']
			worksheet['G' + str(wsrow)] = row['transaction__bene__suffix__name']
			worksheet['H' + str(wsrow)] = birth_date
			worksheet['I' + str(wsrow)] = row['transaction__bene__house_no']
			worksheet['J' + str(wsrow)] = row['transaction__bene__barangay__brgy_name']
			worksheet['K' + str(wsrow)] = row['transaction__bene__barangay__city_code__city_name']
			worksheet['L' + str(wsrow)] = row['transaction__bene__street']
			worksheet['M' + str(wsrow)] = row['transaction__bene__barangay__city_code__prov_code__prov_name']
			worksheet['N' + str(wsrow)] = row['transaction__bene__barangay__city_code__prov_code__region_code__region_name']
			worksheet['O' + str(wsrow)] = row['transaction__bene__sex__name']
			worksheet['P' + str(wsrow)] = row['transaction__bene__occupation__occupation_name']
			worksheet['Q' + str(wsrow)] = row['transaction__bene__salary']

			worksheet['R' + str(wsrow)] = row['transaction__client__last_name']
			worksheet['S' + str(wsrow)] = row['transaction__client__first_name']           
			worksheet['T' + str(wsrow)] = row['transaction__client__middle_name']
			worksheet['U' + str(wsrow)] = row['transaction__client__suffix__name']
			worksheet['V' + str(wsrow)] = client_birth_date
			worksheet['W' + str(wsrow)] = row['transaction__client__house_no']
			worksheet['X' + str(wsrow)] = row['transaction__client__barangay__brgy_name']
			worksheet['Y' + str(wsrow)] = row['transaction__client__barangay__city_code__city_name']
			worksheet['Z' + str(wsrow)] = row['transaction__client__street']
			worksheet['AA' + str(wsrow)] = row['transaction__client__barangay__city_code__prov_code__prov_name']
			worksheet['BB' + str(wsrow)] = row['transaction__client__barangay__city_code__prov_code__region_code__region_name']
			worksheet['CC' + str(wsrow)] = row['transaction__client__sex__name']
			worksheet['DD' + str(wsrow)] = row['transaction__client__occupation__occupation_name']
			worksheet['EE' + str(wsrow)] = row['transaction__client__salary']

			wsrow = wsrow + 1
		response = HttpResponse(content=save_virtual_workbook(workbook), content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename=Personal User Transaction' + ' (' + year + ').xlsx'
		return response
	else:
		return render(request, '404.html')

@login_required
def generateByUser(request):
	if request.method == "POST":
		clientCategory = request.POST.get('clientCategory')
		clientCategoryCheckbox = request.POST.get('Client_category_checkbox')
		service_provider = request.POST.get('service_provider')
	
		today = datetime.today()
		year = today.strftime("%Y")
		workbook = Workbook()
		worksheet = workbook.active
		worksheet.title = 'USER AVAIL ' + year
		wsrow = 2

		blue = PatternFill(start_color='92D4F0',
						end_color='92D4F0',
						fill_type='solid')

		worksheet['A1'] = 'Transaction No'
		worksheet['B1'] = 'Time of Transaction'
		worksheet['C1'] = 'Date of Transaction'

		worksheet['A1'].fill = blue
		worksheet['B1'].fill = blue
		worksheet['C1'].fill = blue

		darkblue = PatternFill(start_color='AAC4F2',
						end_color='AAC4F2',
						fill_type='solid')

		worksheet['D1'] = 'BENE LAST NAME'
		worksheet['E1'] = 'BENE FIRST NAME'
		worksheet['F1'] = 'BENE MIDDLE NAME'
		worksheet['G1'] = 'BENE EXT'
		worksheet['H1'] = 'BENE BIRTH DATE'
		worksheet['I1'] = 'BENE PUROK'
		worksheet['J1'] = 'BENE BARANGAY'
		worksheet['K1'] = 'BENE MUNICIPALITY'
		worksheet['L1'] = 'BENE DISTRICT'
		worksheet['M1'] = 'BENE PROVINCE'
		worksheet['N1'] = 'BENE REGION'
		worksheet['O1'] = 'BENE SEX'
		worksheet['P1'] = 'BENE OCCUPATION'
		worksheet['Q1'] = 'BENE INCOME'
		worksheet['R1'] = 'BENE INCOME'
		worksheet['S1'] = 'BENE OCCUPATION'

		worksheet['T1'] = 'CLIENT LAST NAME'
		worksheet['U1'] = 'CLIENT FIRST NAME'
		worksheet['V1'] = 'CLIENT MIDDLE NAME'
		worksheet['W1'] = 'CLIENT EXT'
		worksheet['X1'] = 'CLIENT BIRTH DATE'
		worksheet['Y1'] = 'CLIENT PUROK'
		worksheet['Z1'] = 'CLIENT BARANGAY'
		worksheet['AA1'] = 'CLIENT MUNICIPALITY'
		worksheet['BB1'] = 'CLIENT DISTRICT'
		worksheet['CC1'] = 'CLIENT PROVINCE'
		worksheet['DD1'] = 'CLIENT REGION'
		worksheet['EE1'] = 'CLIENT SEX'
		worksheet['FF1'] = 'CLIENT OCCUPATION'
		worksheet['GG1'] = 'CLIENT INCOME'


		worksheet['D1'].fill = darkblue
		worksheet['E1'].fill = darkblue
		worksheet['F1'].fill = darkblue
		worksheet['G1'].fill = darkblue
		worksheet['H1'].fill = darkblue
		worksheet['I1'].fill = darkblue
		worksheet['J1'].fill = darkblue
		worksheet['K1'].fill = darkblue
		worksheet['L1'].fill = darkblue
		worksheet['M1'].fill = darkblue
		worksheet['N1'].fill = darkblue
		worksheet['O1'].fill = darkblue
		worksheet['P1'].fill = darkblue
		worksheet['Q1'].fill = darkblue

		worksheet['A1'].font = Font(bold=True)
		worksheet['B1'].font = Font(bold=True)
		worksheet['C1'].font = Font(bold=True)
		worksheet['D1'].font = Font(bold=True)
		worksheet['E1'].font = Font(bold=True)
		worksheet['F1'].font = Font(bold=True)
		worksheet['G1'].font = Font(bold=True)
		worksheet['H1'].font = Font(bold=True)
		worksheet['I1'].font = Font(bold=True)
		worksheet['J1'].font = Font(bold=True)
		worksheet['K1'].font = Font(bold=True)
		worksheet['L1'].font = Font(bold=True)
		worksheet['M1'].font = Font(bold=True)
		worksheet['N1'].font = Font(bold=True)
		worksheet['O1'].font = Font(bold=True)
		worksheet['P1'].font = Font(bold=True)
		worksheet['Q1'].font = Font(bold=True)
		worksheet['R1'].font = Font(bold=True)
		worksheet['S1'].font = Font(bold=True)
		worksheet['T1'].font = Font(bold=True)
		worksheet['U1'].font = Font(bold=True)
		worksheet['V1'].font = Font(bold=True)
		worksheet['W1'].font = Font(bold=True)
		worksheet['X1'].font = Font(bold=True)
		worksheet['Y1'].font = Font(bold=True)
		worksheet['Z1'].font = Font(bold=True)

		if clientCategoryCheckbox == "Client_category":
			transaction = TransactionStatus1.objects.filter(status=6,transaction__client_category_id=clientCategory).values('transaction__tracking_number','verified_time_start','transaction__bene__last_name','transaction__bene__first_name', \
				'transaction__bene__middle_name','transaction__bene__suffix__name','transaction__bene__birthdate','transaction__bene__street','transaction__bene__house_no', 'transaction__bene__barangay__brgy_name', \
					'transaction__bene__barangay__city_code__city_name', 'transaction__bene__barangay__city_code__prov_code__prov_name','transaction__bene__barangay__city_code__prov_code__region_code__region_name', \
						'transaction__bene__occupation__occupation_name','transaction__bene__salary','transaction__bene__sex__name', 'transaction__client__last_name','transaction__client__first_name', \
							'transaction__client__middle_name','transaction__client__suffix__name','transaction__client__birthdate','transaction__client__street','transaction__client__house_no', 'transaction__client__barangay__brgy_name', \
								'transaction__client__barangay__city_code__city_name', 'transaction__client__barangay__city_code__prov_code__prov_name','transaction__client__barangay__city_code__prov_code__region_code__region_name', \
									'transaction__client__occupation__occupation_name','transaction__client__salary','transaction__client__sex__name')
			if transaction:
				for indx, row in enumerate(transaction):
					dateoftransaction = row['verified_time_start'].strftime("%H:%M %p")
					transactionDate = row['verified_time_start'].strftime("%B %d, %Y")
					birth_date = row['transaction__bene__birthdate'].strftime("%B %d, %Y")

					client_birth_date = row['transaction__client__birthdate'].strftime("%B %d, %Y")

					worksheet['A' + str(wsrow)] = row['transaction__tracking_number']
					worksheet['B' + str(wsrow)] = dateoftransaction
					worksheet['C' + str(wsrow)] = transactionDate
					worksheet['D' + str(wsrow)] = row['transaction__bene__last_name']
					worksheet['E' + str(wsrow)] = row['transaction__bene__first_name']
					worksheet['F' + str(wsrow)] = row['transaction__bene__middle_name']
					worksheet['G' + str(wsrow)] = row['transaction__bene__suffix__name']
					worksheet['H' + str(wsrow)] = birth_date
					worksheet['I' + str(wsrow)] = row['transaction__bene__house_no']
					worksheet['J' + str(wsrow)] = row['transaction__bene__barangay__brgy_name']
					worksheet['K' + str(wsrow)] = row['transaction__bene__barangay__city_code__city_name']
					worksheet['L' + str(wsrow)] = row['transaction__bene__street']
					worksheet['M' + str(wsrow)] = row['transaction__bene__barangay__city_code__prov_code__prov_name']
					worksheet['N' + str(wsrow)] = row['transaction__bene__barangay__city_code__prov_code__region_code__region_name']
					worksheet['O' + str(wsrow)] = row['transaction__bene__sex__name']
					worksheet['P' + str(wsrow)] = row['transaction__bene__occupation__occupation_name']
					worksheet['Q' + str(wsrow)] = row['transaction__bene__salary']

					worksheet['R' + str(wsrow)] = row['transaction__client__last_name']
					worksheet['S' + str(wsrow)] = row['transaction__client__first_name']           
					worksheet['T' + str(wsrow)] = row['transaction__client__middle_name']
					worksheet['U' + str(wsrow)] = row['transaction__client__suffix__name']
					worksheet['V' + str(wsrow)] = client_birth_date
					worksheet['W' + str(wsrow)] = row['transaction__client__house_no']
					worksheet['X' + str(wsrow)] = row['transaction__client__barangay__brgy_name']
					worksheet['Y' + str(wsrow)] = row['transaction__client__barangay__city_code__city_name']
					worksheet['Z' + str(wsrow)] = row['transaction__client__street']
					worksheet['AA' + str(wsrow)] = row['transaction__client__barangay__city_code__prov_code__prov_name']
					worksheet['BB' + str(wsrow)] = row['transaction__client__barangay__city_code__prov_code__region_code__region_name']
					worksheet['CC' + str(wsrow)] = row['transaction__client__sex__name']
					worksheet['DD' + str(wsrow)] = row['transaction__client__occupation__occupation_name']
					worksheet['EE' + str(wsrow)] = row['transaction__client__salary']

					wsrow = wsrow + 1
				response = HttpResponse(content=save_virtual_workbook(workbook), content_type='application/ms-excel')
				response['Content-Disposition'] = 'attachment; filename=Client Category' + ' (' + year + ').xlsx'
				return response
			else:
				return render(request, '404.html')
		elif clientCategoryCheckbox == "Sex":
			sex_disagregated = request.POST.get('sex_disagregated')
			if sex_disagregated == "male":
				transaction = TransactionStatus1.objects.filter(status=6,transaction__client__sex__name=sex_disagregated).values('transaction__tracking_number','verified_time_start','transaction__bene__last_name','transaction__bene__first_name', \
					'transaction__bene__middle_name','transaction__bene__suffix__name','transaction__bene__birthdate','transaction__bene__street','transaction__bene__house_no', 'transaction__bene__barangay__brgy_name', \
						'transaction__bene__barangay__city_code__city_name', 'transaction__bene__barangay__city_code__prov_code__prov_name','transaction__bene__barangay__city_code__prov_code__region_code__region_name', \
							'transaction__bene__occupation__occupation_name','transaction__bene__salary','transaction__bene__sex__name', 'transaction__client__last_name','transaction__client__first_name', \
								'transaction__client__middle_name','transaction__client__suffix__name','transaction__client__birthdate','transaction__client__street','transaction__client__house_no', 'transaction__client__barangay__brgy_name', \
									'transaction__client__barangay__city_code__city_name', 'transaction__client__barangay__city_code__prov_code__prov_name','transaction__client__barangay__city_code__prov_code__region_code__region_name', \
										'transaction__client__occupation__occupation_name','transaction__client__salary','transaction__client__sex__name')
				if transaction:
					for indx, row in enumerate(transaction):
						dateoftransaction = row['verified_time_start'].strftime("%H:%M %p")
						transactionDate = row['verified_time_start'].strftime("%B %d, %Y")
						birth_date = row['transaction__bene__birthdate'].strftime("%B %d, %Y")

						client_birth_date = row['transaction__client__birthdate'].strftime("%B %d, %Y")

						worksheet['A' + str(wsrow)] = row['transaction__tracking_number']
						worksheet['B' + str(wsrow)] = dateoftransaction
						worksheet['C' + str(wsrow)] = transactionDate
						worksheet['D' + str(wsrow)] = row['transaction__bene__last_name']
						worksheet['E' + str(wsrow)] = row['transaction__bene__first_name']
						worksheet['F' + str(wsrow)] = row['transaction__bene__middle_name']
						worksheet['G' + str(wsrow)] = row['transaction__bene__suffix__name']
						worksheet['H' + str(wsrow)] = birth_date
						worksheet['I' + str(wsrow)] = row['transaction__bene__house_no']
						worksheet['J' + str(wsrow)] = row['transaction__bene__barangay__brgy_name']
						worksheet['K' + str(wsrow)] = row['transaction__bene__barangay__city_code__city_name']
						worksheet['L' + str(wsrow)] = row['transaction__bene__street']
						worksheet['M' + str(wsrow)] = row['transaction__bene__barangay__city_code__prov_code__prov_name']
						worksheet['N' + str(wsrow)] = row['transaction__bene__barangay__city_code__prov_code__region_code__region_name']
						worksheet['O' + str(wsrow)] = row['transaction__bene__sex__name']
						worksheet['P' + str(wsrow)] = row['transaction__bene__occupation__occupation_name']
						worksheet['Q' + str(wsrow)] = row['transaction__bene__salary']

						worksheet['R' + str(wsrow)] = row['transaction__client__last_name']
						worksheet['S' + str(wsrow)] = row['transaction__client__first_name']           
						worksheet['T' + str(wsrow)] = row['transaction__client__middle_name']
						worksheet['U' + str(wsrow)] = row['transaction__client__suffix__name']
						worksheet['V' + str(wsrow)] = client_birth_date
						worksheet['W' + str(wsrow)] = row['transaction__client__house_no']
						worksheet['X' + str(wsrow)] = row['transaction__client__barangay__brgy_name']
						worksheet['Y' + str(wsrow)] = row['transaction__client__barangay__city_code__city_name']
						worksheet['Z' + str(wsrow)] = row['transaction__client__street']
						worksheet['AA' + str(wsrow)] = row['transaction__client__barangay__city_code__prov_code__prov_name']
						worksheet['BB' + str(wsrow)] = row['transaction__client__barangay__city_code__prov_code__region_code__region_name']
						worksheet['CC' + str(wsrow)] = row['transaction__client__sex__name']
						worksheet['DD' + str(wsrow)] = row['transaction__client__occupation__occupation_name']
						worksheet['EE' + str(wsrow)] = row['transaction__client__salary']

						wsrow = wsrow + 1
					response = HttpResponse(content=save_virtual_workbook(workbook), content_type='application/ms-excel')
					response['Content-Disposition'] = 'attachment; filename=Sex disaggregated data (MALE ONLY)' + ' (' + year + ').xlsx'
					return response
				else:
					return render(request, '404.html')
			elif sex_disagregated == "female":
				transaction = TransactionStatus1.objects.filter(status=6,transaction__client__sex__name=sex_disagregated).values('transaction__tracking_number','verified_time_start','transaction__bene__last_name','transaction__bene__first_name', \
					'transaction__bene__middle_name','transaction__bene__suffix__name','transaction__bene__birthdate','transaction__bene__street','transaction__bene__house_no', 'transaction__bene__barangay__brgy_name', \
						'transaction__bene__barangay__city_code__city_name', 'transaction__bene__barangay__city_code__prov_code__prov_name','transaction__bene__barangay__city_code__prov_code__region_code__region_name', \
							'transaction__bene__occupation__occupation_name','transaction__bene__salary','transaction__bene__sex__name', 'transaction__client__last_name','transaction__client__first_name', \
								'transaction__client__middle_name','transaction__client__suffix__name','transaction__client__birthdate','transaction__client__street','transaction__client__house_no', 'transaction__client__barangay__brgy_name', \
									'transaction__client__barangay__city_code__city_name', 'transaction__client__barangay__city_code__prov_code__prov_name','transaction__client__barangay__city_code__prov_code__region_code__region_name', \
										'transaction__client__occupation__occupation_name','transaction__client__salary','transaction__client__sex__name')
				if transaction:
					for indx, row in enumerate(transaction):
						dateoftransaction = row['verified_time_start'].strftime("%H:%M %p")
						transactionDate = row['verified_time_start'].strftime("%B %d, %Y")
						birth_date = row['transaction__bene__birthdate'].strftime("%B %d, %Y")

						client_birth_date = row['transaction__client__birthdate'].strftime("%B %d, %Y")

						worksheet['A' + str(wsrow)] = row['transaction__tracking_number']
						worksheet['B' + str(wsrow)] = dateoftransaction
						worksheet['C' + str(wsrow)] = transactionDate
						worksheet['D' + str(wsrow)] = row['transaction__bene__last_name']
						worksheet['E' + str(wsrow)] = row['transaction__bene__first_name']
						worksheet['F' + str(wsrow)] = row['transaction__bene__middle_name']
						worksheet['G' + str(wsrow)] = row['transaction__bene__suffix__name']
						worksheet['H' + str(wsrow)] = birth_date
						worksheet['I' + str(wsrow)] = row['transaction__bene__house_no']
						worksheet['J' + str(wsrow)] = row['transaction__bene__barangay__brgy_name']
						worksheet['K' + str(wsrow)] = row['transaction__bene__barangay__city_code__city_name']
						worksheet['L' + str(wsrow)] = row['transaction__bene__street']
						worksheet['M' + str(wsrow)] = row['transaction__bene__barangay__city_code__prov_code__prov_name']
						worksheet['N' + str(wsrow)] = row['transaction__bene__barangay__city_code__prov_code__region_code__region_name']
						worksheet['O' + str(wsrow)] = row['transaction__bene__sex__name']
						worksheet['P' + str(wsrow)] = row['transaction__bene__occupation__occupation_name']
						worksheet['Q' + str(wsrow)] = row['transaction__bene__salary']

						worksheet['R' + str(wsrow)] = row['transaction__client__last_name']
						worksheet['S' + str(wsrow)] = row['transaction__client__first_name']           
						worksheet['T' + str(wsrow)] = row['transaction__client__middle_name']
						worksheet['U' + str(wsrow)] = row['transaction__client__suffix__name']
						worksheet['V' + str(wsrow)] = client_birth_date
						worksheet['W' + str(wsrow)] = row['transaction__client__house_no']
						worksheet['X' + str(wsrow)] = row['transaction__client__barangay__brgy_name']
						worksheet['Y' + str(wsrow)] = row['transaction__client__barangay__city_code__city_name']
						worksheet['Z' + str(wsrow)] = row['transaction__client__street']
						worksheet['AA' + str(wsrow)] = row['transaction__client__barangay__city_code__prov_code__prov_name']
						worksheet['BB' + str(wsrow)] = row['transaction__client__barangay__city_code__prov_code__region_code__region_name']
						worksheet['CC' + str(wsrow)] = row['transaction__client__sex__name']
						worksheet['DD' + str(wsrow)] = row['transaction__client__occupation__occupation_name']
						worksheet['EE' + str(wsrow)] = row['transaction__client__salary']

						wsrow = wsrow + 1
					response = HttpResponse(content=save_virtual_workbook(workbook), content_type='application/ms-excel')
					response['Content-Disposition'] = 'attachment; filename=Sex disaggregated data (FEMALE ONLY)' + ' (' + year + ').xlsx'
					return response
				else:
					return render(request, '404.html')
				
		elif service_provider:
			print(service_provider)
		else:
			return render(request, '404.html')
	context = {
		'ClientCategory': Category.objects.all()
	}
	return render(request, 'GeneratebyUser.html', context)