from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from datetime import timedelta, date
from app.forms import ImageForm
from app.global_variable import groups_only
from app.libraries.models import FileType, Relation, Category, SubCategory, ServiceProvider, ServiceAssistance, \
	TypeOfAssistance, Purpose, ModeOfAssistance, ModeOfAdmission, SubModeofAssistance, TypeOfAssistance, \
	SubModeofAssistance, LibAssistanceType, PriorityLine, region, medicine, AssistanceProvided, FundSource
from app.requests.models import ClientBeneficiary, ClientBeneficiaryFamilyComposition, \
	 Transaction, TransactionServiceAssistance, Mail, transaction_description, AssessmentProblemPresented, \
	uploadfile, TransactionStatus1, SocialWorker_Status, ErrorLogData, transactionHistory
from django.contrib.sessions.models import Session
from app.models import AuthUser, AuthUserGroups
from django.db.models import Value, Sum, Count
from datetime import datetime, timedelta, time, date
from django.utils import timezone
from django.contrib.auth.models import User
from app.finance.models import finance_voucher, finance_voucherData, finance_outsideFo, disbursementVoucher, disbursementVoucherData
from django.db.models import Q
import csv, uuid
from django.utils.encoding import smart_str
from io import StringIO
from django.http import HttpResponse, StreamingHttpResponse
from rest_framework.decorators import api_view
from requests.exceptions import RequestException
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
today = date.today()

class Echo:
	def write(self, value):
		return value

def handle_error(error, location, user): #ERROR HANDLING
	ErrorLogData.objects.create(
		error_log=error,
		location=location,
		user_id=user,
	)

def generate_serial_string(oldstring, prefix=None):
	current_year = datetime.now().year
	current_day = datetime.now().day
	current_month = datetime.now().month
	if oldstring:
		oldstring_list = oldstring.split("-")
		if oldstring_list[1] == str(current_year).zfill(4):
			return "{}-{}-{}-{}-{}".format(str(oldstring_list[0]), str(current_year).zfill(4), str(current_month).zfill(2), str(current_day).zfill(2),
										str(int(oldstring_list[4]) + 1).zfill(4)).strip()
		else:
			return "{}-{}-{}-{}-{}".format(str(oldstring_list[0]), str(current_year).zfill(4), str(current_month).zfill(2), str(current_day).zfill(2),
										str("1").zfill(4)).strip()
	else:
		return "{}-{}-{}-{}-{}".format(str(prefix), str(current_year).zfill(4), str(current_month).zfill(2), str(current_day).zfill(2),
									str("1").zfill(4)).strip()

@login_required
def printStateofAccount(request,pk):
	soa = finance_voucher.objects.filter(id=pk).first()
	data = finance_voucherData.objects.filter(voucher_id=soa.id)

	total_values_data = data.values_list('transactionStatus__total_amount', flat=True)
	total_values = sum(float(value.replace(',', '')) for value in total_values_data)
	
	outside_fo = finance_outsideFo.objects.filter(voucher=soa.id)
	outisde_total_values_data = outside_fo.values_list('amount', flat=True)
	outside_total_values = sum(float(value.replace(',', '')) for value in outisde_total_values_data)

	context = {
		'datas': data,
		'soa': soa,
		'outside_fo': outside_fo,

		'total_values':total_values,
		'outside_total_values':outside_total_values,
	}
	return render(request,'financial/printableforms/printsoa.html',context)


@login_required
@groups_only('Super Administrator', 'Biller','Finance')
def financial_transaction(request):
	if request.method == "POST":
		try:
			with transaction.atomic():
				voucher=request.POST.get('voucher_title')
				date=request.POST.get('date')
				remarks=request.POST.get('remarks')
				
				unique_id = uuid.uuid4()
				check_if_exists = finance_voucher.objects.filter(
					Q(voucher_title__icontains=request.POST.get('voucher_title'))
				).first()
				if not check_if_exists:
					if request.POST.get('dv_id'):
						if request.POST.get('with_without_dv') == "WITHOUT-DV":
							finance_voucher.objects.filter(id=request.POST.get('dv_id')).update(
								voucher_title=voucher,
								date=date,
								remarks=remarks,
								user_id=request.user.id,
								with_without_dv=request.POST.get('with_without_dv'),
								status=1,
							)

						else:
							finance_voucher.objects.filter(id=request.POST.get('dv_id')).update(
								voucher_title=voucher,
								date=date,
								remarks=remarks,
								user_id=request.user.id,
								with_without_dv=request.POST.get('with_without_dv'),
								status=1,
								date_updated=today
							)
							
						data = finance_voucher.objects.get(id=request.POST.get('dv_id'))
						voucher_data = finance_voucherData.objects.filter(voucher_id=data.id).all()
						for row in voucher_data:
							Transaction.objects.filter(id=row.transactionStatus_id).update(
								dv_number=voucher,
								dv_date=date
							)
						return JsonResponse({'data': 'success', 'msg': 'You successfully updated the transaction'})
					else:
						soa_code =f"SOA-{str(unique_id).upper()}"
						if request.POST.get('with_without_dv') == "WITH-DV":
							finance_voucher.objects.create(
								voucher_code=soa_code,
								voucher_title=voucher,
								date=date,
								remarks=remarks,
								user_id=request.user.id,
								with_without_dv=request.POST.get('with_without_dv'),
								status=1,
								added_by_id=request.user.id,
								date_updated=today,
							)
							return JsonResponse({'data': 'success', 'msg': 'You successfully saved a data.'})
						else:
							finance_voucher.objects.create(
								voucher_code=soa_code,
								voucher_title=voucher,
								date=date,
								remarks=remarks,
								with_without_dv=request.POST.get('with_without_dv'),
								status=1,
								added_by_id=request.user.id
							)
							return JsonResponse({'data': 'success', 'msg': 'You successfully saved a data.'})
				else:
					return JsonResponse({'error': True, 'msg': 'This Title/DV-name already exists, please double check.'})

		except ConnectionError as ce:
			# Handle loss of connection (e.g., log the error)
			handle_error(ce, "CONNECTION ERROR IN VIEW ASSESSMENT", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a problem within your connection, please refresh'})
		except RequestException as e:
			handle_error(e, "REQUEST EXCEPTION ERROR IN financial_transaction", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
		except ValidationError as e:
			handle_error(e, "VALIDATION ERROR IN REQUEST financial_transaction", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
		except IntegrityError as e:
			handle_error(e, "INTEGRITY ERROR IN REQUEST financial_transaction", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data inconsistency, please refresh'})
		except Exception as e:
			handle_error(e, "EXCEPTION ERROR IN REQUEST financial_transaction", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a problem submitting the request, please refresh'})

	context = {
		'title':'SOA',
		'service_provider': ServiceProvider.objects.all(),
		'fund_source': FundSource.objects.all()
	}
	return render(request,'financial/finance.html', context)

# FOR DISBURSEMENT VOUCHER

@login_required
@groups_only('Super Administrator', 'Biller','Finance')
def dibursement_voucher(request):
	if request.method == "POST":
		try:
			with transaction.atomic():
				unique_id = uuid.uuid4()
				tracking = f"DV-A-{str(unique_id).upper()}"
				if request.POST.get('dv_id'):
					disbursementVoucher.objects.filter(id=request.POST.get('dv_id')).update(
						dv_name=request.POST.get('dv_name'),
						remarks=request.POST.get('remarks'),
						created_by_id=request.user.id,
						sp_id=request.POST.get('service_provider_id')
					)
					return JsonResponse({'data': 'success', 'msg': 'You successfully updated the disbursement voucher'})
				else:
					disbursementVoucher.objects.create(
						dv_name=request.POST.get('dv_name'),
						dv_tracking_code=tracking,
						status=1,
						remarks=request.POST.get('remarks'),
						created_by_id=request.user.id,
						sp_id=request.POST.get('service_provider_id')
					)
					return JsonResponse({'data': 'success', 'msg': 'You successfully submitted the data.'})

		except ConnectionError as ce:
			# Handle loss of connection (e.g., log the error)
			handle_error(ce, "CONNECTION ERROR IN VIEW ASSESSMENT", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a problem within your connection, please refresh'})
		except RequestException as e:
			handle_error(e, "REQUEST EXCEPTION ERROR IN financial_transaction", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
		except ValidationError as e:
			handle_error(e, "VALIDATION ERROR IN REQUEST financial_transaction", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
		except IntegrityError as e:
			handle_error(e, "INTEGRITY ERROR IN REQUEST financial_transaction", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data inconsistency, please refresh'})
		except Exception as e:
			handle_error(e, "EXCEPTION ERROR IN REQUEST financial_transaction", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a problem submitting the request, please refresh'})
		
	context = {
		'title':'Disbursement Voucher',
		'service_provider': ServiceProvider.objects.all(),
		'fund_source': FundSource.objects.all(),
	}
	return render(request,'financial/disbursement_voucher.html', context)

@csrf_exempt
def confirmVoucher(request, pk):
	if request.method == "POST":
		try:
			data = disbursementVoucher.objects.filter(id=pk).first()
			dv_data = disbursementVoucherData.objects.filter(dv_id=data.id)
			total_values_data = dv_data.values_list('soa__soa_total_amount', flat=True)
			total_values = sum(float(value.replace(',', '')) if value else 0 for value in total_values_data)
			data.amount = total_values
			data.save()
			return JsonResponse({'data': 'success', 'msg': 'This data successfully saved'})
		
		except RequestException as e:
			handle_error(e, "REQUEST EXCEPTION ERROR IN confirmVoucher", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
		except ValidationError as e:
			handle_error(e, "VALIDATION ERROR IN REQUEST confirmVoucher", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
		except IntegrityError as e:
			handle_error(e, "INTEGRITY ERROR IN REQUEST confirmVoucher", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data inconsistency, please refresh'})
		except Exception as e:
			handle_error(e, "EXCEPTION ERROR IN REQUEST confirmVoucher", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a problem submitting the request, please refresh'})
		

@login_required
def disbursement_voucher_data(request, pk):
	data = disbursementVoucher.objects.filter(id=pk).first()
	if request.method == "POST":
		try:
			if request.POST.get('function') == "update": #UPDATING NI SIR JOSHUA PAG NAA NAY DV
				disbursementVoucher.objects.filter(id=data.id).update( 
					dv_name=request.POST.get('dv_name'),
					dv_date=request.POST.get('dv_date_updated'),
					updated_by_id=request.user.id
				)
				dvdata = disbursementVoucherData.objects.filter(dv_id=data.id).all()
				for row in dvdata:
					finance_voucher.objects.filter(id=row.soa_id).update(
						dv_data_id=data.id,
						with_without_dv="WITH-DV"
					)
				return JsonResponse({'data': 'success', 'msg': 'You successfully updated this data'})
			else:
				disbursementVoucherData.objects.create(
					dv_id=data.id,
					soa_id=request.POST.get('soa_id'),
					date_added=today,
					added_by_id=request.user.id
				)
				finance_voucher.objects.filter(id=request.POST.get('soa_id')).update(
					date_updated=data.date_entried,
					dv_data=data.id
				)
				return JsonResponse({'data': 'success', 'msg': 'You successfully added this data'})
		except RequestException as e:
			handle_error(e, "REQUEST EXCEPTION ERROR IN disbursement_voucher_data", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
		except ValidationError as e:
			handle_error(e, "VALIDATION ERROR IN REQUEST disbursement_voucher_data", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
		except IntegrityError as e:
			handle_error(e, "INTEGRITY ERROR IN REQUEST disbursement_voucher_data", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data inconsistency, please refresh'})
		except Exception as e:
			handle_error(e, "EXCEPTION ERROR IN REQUEST disbursement_voucher_data", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a problem submitting the request, please refresh'})
		
	restriction = request.user.groups.filter(name__in=['Finance', 'Super Administrator']).exists()
	validation = disbursementVoucherData.objects.filter(dv_id=data.id).exists()
	context = {
		'data': data,
		'restriction': restriction,
		'validation':validation,
	}
	return render(request,'financial/disbursement_voucher_data.html', context)

@login_required
def printdvobs(request, pk):
	data = disbursementVoucher.objects.filter(id=pk).first()
	dv_data = disbursementVoucherData.objects.filter(dv=data).first()
	soa_data = finance_voucher.objects.filter(dv_data__id=pk).all()
	if dv_data and dv_data.soa:
		# Retrieve the related finance voucher
		finance_vc = dv_data.soa
		# Get all related finance voucher data objects sorted by transaction date
		finance_voucher_data_queryset = finance_voucherData.objects.filter(voucher=finance_vc).order_by('transactionStatus__date_of_transaction').first()
		# Retrieve the first and last transaction's date_entried
		first_transaction = finance_voucher_data_queryset
		if first_transaction and first_transaction.transactionStatus:
			first_transaction_date_entried = first_transaction.transactionStatus.date_of_transaction
		else:
			first_transaction_date_entried = None
	else:
		first_transaction_date_entried = None

	dv_data = disbursementVoucherData.objects.filter(dv=data).last()

	if dv_data and dv_data.soa:
		# Retrieve the related finance voucher
		finance_vc = dv_data.soa

		# Get the last related finance voucher data object sorted by transaction date
		last_transaction = finance_voucherData.objects.filter(
			voucher=finance_vc
		).order_by('-transactionStatus__date_of_transaction').first()

		# Retrieve the last transaction's date_entried
		if last_transaction and last_transaction.transactionStatus:
			last_transaction_date_entried = last_transaction.transactionStatus.date_of_transaction
		else:
			last_transaction_date_entried = None
	else:
		last_transaction_date_entried = None

	context = {
		'data':data,
		'covered_date_start': first_transaction_date_entried,
		'covered_date_end': last_transaction_date_entried,
		'soa_data': soa_data,
	}
	return render(request,'financial/printableforms/printdvobs.html', context)

@csrf_exempt
def removeSoa(request):
	if request.method == "POST":
		try:
			dv_data = disbursementVoucher.objects.filter(id=request.POST.get('dv_id')).first()
			if dv_data:
				dv_data.amount = None
				dv_data.save()
			data = disbursementVoucherData.objects.filter(id=request.POST.get('id')).values('soa_id').first()

			if data:
				disbursementVoucherData.objects.filter(id=request.POST.get('id')).delete()
				finance_voucher.objects.filter(id=data['soa_id']).update(
					dv_data=None,
					date_updated=None,
					with_without_dv="WITHOUT-DV",
				)
			return JsonResponse({'data': 'success'})
		except RequestException as e:
			handle_error(e, "REQUEST EXCEPTION ERROR IN removeSoa", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
		except ValidationError as e:
			handle_error(e, "VALIDATION ERROR IN REQUEST removeSoa", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
		except IntegrityError as e:
			handle_error(e, "INTEGRITY ERROR IN REQUEST removeSoa", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data inconsistency, please refresh'})
		except Exception as e:
			handle_error(e, "EXCEPTION ERROR IN REQUEST removeSoa", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a problem submitting the request, please refresh'})

@login_required
@csrf_exempt
def get_all_soa(request):
	json = []
	if request.GET.get('searchTerm', ''):
		sp = finance_voucher.objects.filter(Q(voucher_code__icontains=request.GET.get('searchTerm')) & Q(soa_total_amount__isnull=False) & Q(dv_data__isnull=True))[:10]
		if sp:
			for row in sp:
				json.append({'id': row.id, 'text': row.voucher_code })

		return JsonResponse(json, safe=False)
	else:
		return JsonResponse(json, safe=False)

# END HERE

@login_required
@groups_only('Super Administrator', 'Biller','Finance')
def finance_assessment(request, pk):

	data = Transaction.objects.filter(id=pk).first()
	calculate = transaction_description.objects.filter(tracking_number_id=data.tracking_number).aggregate(total_payment=Sum('total'))
	transactionProvided = transaction_description.objects.filter(tracking_number_id=data.tracking_number).first()
	picture = uploadfile.objects.filter(client_bene_id=data.client_id).first()

	
	context = {
		'transaction': data,
		'pict':picture,
		'family_composistion': ClientBeneficiaryFamilyComposition.objects.filter(clientbene_id=data.bene_id),
		'transaction_status': TransactionStatus1.objects.filter(transaction_id=pk).first(),
		'category': Category.objects.filter(status=1).order_by('name'),
		'sub_category': SubCategory.objects.filter(status=1).order_by('name'),
		'service_assistance': ServiceAssistance.objects.filter(status=1).order_by('name'),
		'type_of_assistance': TypeOfAssistance.objects.filter(status=1).order_by('name'),
		'purpose': Purpose.objects.filter(status=1).order_by('name'),
		'moass': ModeOfAssistance.objects.filter(status=1).order_by('name'),
		'moadm': ModeOfAdmission.objects.filter(status=1).order_by('name'),
		'fund_source': FundSource.objects.filter(status=1).order_by('name'),
		'assistance_type': LibAssistanceType.objects.filter(is_active=1).order_by('type_name'),
		'TypeOfAssistance': TypeOfAssistance.objects.filter(status=1,type_assistance_id=data.lib_type_of_assistance_id).order_by('name'),
		'SubModeofAssistance': SubModeofAssistance.objects.filter(status=1,category_id=data.lib_assistance_category_id).order_by('name'),
		'viewProvidedData': transaction_description.objects.filter(tracking_number_id=data.tracking_number).order_by('-id'),
		'PriorityLine': PriorityLine.objects.filter(is_active=1).order_by('id'),
		'medicine': medicine.objects.filter(is_active=1),
		'service_provider': ServiceProvider.objects.filter(status=1),
		'calculate': calculate,
		'AssistanceProvided': AssistanceProvided.objects.filter(is_active=1),
		'transactionProvided':transactionProvided,
	}
	return render(request, 'financial/finance_assessment.html', context)

@csrf_exempt  # You can remove this decorator if CSRF protection is not needed
@api_view(['GET'])
def export_fund_summary(request):
	if request.method == "GET":
		start_date_str = request.GET.get("start_date")
		end_date_str = request.GET.get("end_date")
		station = request.GET.get('station')
		queryset = Transaction.objects.filter(
			date_of_transaction__range=(start_date_str, end_date_str), office_station_in=station
		).order_by("id").select_related(
			'client', 'bene', 'relation', 'lib_assistance_category', 'fund_source', 'swo'
		).only(
			"tracking_number",
			"date_of_transaction",
			"client__last_name",
			"client__first_name",
			"client__middle_name",
			"client__suffix__name",
			"client__birthdate",
			"client__age",
			"client__civil_status__name",
			"client__sex__name",
			"client__street",
			"client__barangay__brgy_name",
			"client__barangay__city_code__city_name",
			"client__street",
			"client__barangay__city_code__prov_code__prov_name",
			"client__barangay__city_code__prov_code__region_code__region_name",	
			"bene__last_name",
			"bene__first_name",
			"bene__middle_name",
			"bene__suffix__name",
			"bene__age",
			"bene__civil_status__name",
			"bene__birthdate",
			"bene__sex__name",
			"bene__barangay__brgy_name",
			"bene__barangay__city_code__city_name",
			"bene__street",
			"bene__barangay__city_code__prov_code__prov_name",
			"bene__barangay__city_code__prov_code__region_code__region_name",
			"relation__name",
			"lib_assistance_category__name",
			"is_gl",
			"is_walkin",
			"fund_source__name",
			"service_provider__name",
			"total_amount",
			"is_referral",
			"swo_date_time_end",
			"swo__fullname",
			"swo__last_name",
			"swo__middle_name",
			"swo__first_name",
			"dv_number",
			"dv_date",
			"status",
			"office_station_in__name"

		)

		# Create the StreamingHttpResponse object with CSV header.
		response = StreamingHttpResponse(streaming_content=generate_csv_data(queryset), content_type='text/csv')
		response["Content-Disposition"] = 'attachment; filename="transactions.csv"'

		return response

def generate_csv_data(queryset):
	# Write the header
	header = ["Date Entried", "Tracking_number", "Client Surname", "Client First name", "Client Middle name", "Client suffix name", "Client age",
					"Civil Status", "Birthday", "Client Sex", "Street", "Barangay", "Municipality", "Client District",
					"Province", "Region",
					"Bene Surname", "Bene First name", "Bene Middle name", "Bene suffix name", "Bene age",
					"Civil Status", "Birthday", "Bene Sex", "Street", "Barangay", "Municipality", "Bene District", "Bene Province",
					"Bene Region",
					"Relation", "Assistance Category", "Amount of assistance", "Mode of release", "Source of referral",
					"Source of fund", "Date Interview", "Interviewer/SWO", "Service provider", "DV Date", "DV Number", "STATUS", "Office Station"]

	yield ','.join(header) + '\n'

	# Write rows as dictionaries
	for transaction in queryset.iterator(chunk_size=7000):
		# Map status to corresponding string
		client_street_str = smart_str(transaction.client.street).replace(",", "") if transaction.client.street else ""
		
		bene_street_str = smart_str(transaction.bene.street).replace(",", "") if transaction.bene.street else ""
		total_amount_str = f'"{transaction.total_amount}"' if transaction.total_amount is not None else '0'
		service_provider_str = (
			smart_str(transaction.service_provider.name).replace(",", "")
			if transaction.service_provider and transaction.service_provider.name
			else "N/a"
		)
		dv_number_str = smart_str(transaction.dv_number).replace(",", "") if transaction.dv_number else ""
		client_barangay_str = smart_str(transaction.client.barangay_value).replace(",", "") if transaction.client.barangay_value else ""
		bene_barangay_str = smart_str(transaction.bene.barangay_value).replace(",", "") if transaction.bene.barangay_value else ""
		# Yield CSV data
		yield ','.join([
			smart_str(transaction.date_of_transaction),
			smart_str(transaction.tracking_number),
			smart_str(transaction.client.last_name),
			smart_str(transaction.client.first_name),
			smart_str(transaction.client.middle_name),
			smart_str(transaction.client.suffix.name) if transaction.client.suffix and transaction.client.suffix.name else "N/a",
			smart_str(transaction.client.age),
			smart_str(transaction.client.civil_status.name),
			smart_str(transaction.client.birthdate),
			smart_str(transaction.client.sex.name),
			client_street_str,
			client_barangay_str,
			smart_str(transaction.client.city),
			#smart_str(transaction.client.barangay.brgy_name),
			#smart_str(transaction.client.barangay.city_code.city_name),
			client_street_str,
			smart_str(transaction.client.province),
			smart_str(transaction.client.region),
			#smart_str(transaction.client.barangay.city_code.prov_code.prov_name),
			#smart_str(transaction.client.barangay.city_code.prov_code.region_code.region_name),
			smart_str(transaction.bene.last_name),
			smart_str(transaction.bene.first_name),
			smart_str(transaction.client.middle_name),
			smart_str(transaction.bene.suffix.name) if transaction.bene.suffix and transaction.bene.suffix.name else "N/a",
			smart_str(transaction.bene.age),
			smart_str(transaction.bene.civil_status.name),
			smart_str(transaction.bene.birthdate),
			smart_str(transaction.bene.suffix.name) if transaction.bene.suffix and transaction.bene.suffix.name else "N/a",
			bene_street_str,
			bene_barangay_str,
			smart_str(transaction.bene.city),
			#smart_str(transaction.bene.barangay.brgy_name),
			#smart_str(transaction.bene.barangay.city_code.city_name),
			bene_street_str,
			smart_str(transaction.bene.province),
			smart_str(transaction.bene.region),
			#smart_str(transaction.bene.barangay.city_code.prov_code.prov_name),
			#smart_str(transaction.bene.barangay.city_code.prov_code.region_code.region_name),
			smart_str(transaction.relation.name),
			smart_str(transaction.lib_assistance_category.name),
			total_amount_str,
			smart_str("GL") if transaction.is_gl == 1 else "CASH",
			smart_str("Referral") if transaction.is_referral == 1 else "Walk-in",
			smart_str(transaction.fund_source.description) if transaction.fund_source and transaction.fund_source.description else "N/a",
			smart_str(transaction.swo_date_time_end),
			smart_str(transaction.swo.fullname),
			service_provider_str,
			smart_str(transaction.dv_date),
			dv_number_str,
			smart_str(transaction.exp_status),
			smart_str(transaction.office_station_in.name)
		]) + '\n'

@login_required 
def voucher_modal(request, pk):
	if request.method == "POST":
		try:
			finance_voucherData.objects.create(
				voucher_id=pk,
				transactionStatus_id=request.POST.get('transaction_id'),
			)
			return JsonResponse({'data': 'success', 'msg': 'Data successfully added to Voucher'})
		except RequestException as e:
			handle_error(e, "REQUEST EXCEPTION ERROR IN voucher_modal", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
		except ValidationError as e:
			handle_error(e, "VALIDATION ERROR IN REQUEST voucher_modal", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
		except IntegrityError as e:
			handle_error(e, "INTEGRITY ERROR IN REQUEST voucher_modal", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data inconsistency, please refresh'})
		except Exception as e:
			handle_error(e, "EXCEPTION ERROR IN REQUEST voucher_modal", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a problem submitting the request, please refresh'})
	
	test = finance_voucherData.objects.filter(voucher_id=pk)
	context = {
		'voucherTitle':finance_voucher.objects.filter(id=pk).first(),
		'voucherData': test
	}
	return render(request, 'financial/voucher_modal.html',context)

@csrf_exempt
def remove_voucherData(request):
	if request.method == "POST":
		try:
			update = finance_voucher.objects.filter(id=request.POST.get('soa_id')).first()
			if update:
				update.soa_total_amount = None
				update.save()
			data = finance_voucherData.objects.filter(id=request.POST.get('id')).first()
			TransactionStatus1.objects.filter(id=data.transactionStatus_id).update(
				finance_status=None,
			)
			Transaction.objects.filter(id=data.transactionStatus_id).update(
				dv_number=None,
				dv_date=None
			)
			data = finance_voucherData.objects.filter(id=request.POST.get('id')).delete()
			return JsonResponse({'data': 'success'})
		except RequestException as e:
			handle_error(e, "REQUEST EXCEPTION ERROR IN remove_voucherData", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
		except ValidationError as e:
			handle_error(e, "VALIDATION ERROR IN REQUEST remove_voucherData", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
		except IntegrityError as e:
			handle_error(e, "INTEGRITY ERROR IN REQUEST remove_voucherData", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data inconsistency, please refresh'})
		except Exception as e:
			handle_error(e, "EXCEPTION ERROR IN REQUEST remove_voucherData", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a problem submitting the request, please refresh'})

@csrf_exempt
def get_all_transaction(request):
	json_data = []
	search_term = request.GET.get('searchTerm', '')
	if search_term:
		transactions = Transaction.objects.filter(
			Q(tracking_number__icontains=search_term) &
			Q(status__in=[3, 6]) &
			Q(total_amount__isnull=False) &
			Q(dv_number=None)
		)[:6]

		if transactions.exists():
			json_data = list(transactions.values_list('id', 'tracking_number', named=True))
			json_data = [{'id': row.id, 'text': row.tracking_number} for row in json_data]

	return JsonResponse(json_data, safe=False)

@csrf_exempt
def get_transaction_advance_search(request):
	json_data = []
	search_term = request.GET.get('searchTerm', '')
	if search_term:
		transactions = Transaction.objects.filter(
			Q(tracking_number__icontains=search_term)
		).order_by('id')[:6]

		if transactions.exists():
			json_data = list(transactions.values_list('id', 'tracking_number', named=True))
			json_data = [{'id': row.id, 'text': row.tracking_number} for row in json_data]

	return JsonResponse(json_data, safe=False)

@login_required
def get_data_transaction(request, pk):
	data = TransactionStatus1.objects.filter(transaction_id=pk).first()
	fullname = data.transaction.client.get_client_fullname
	toa = data.transaction.lib_type_of_assistance.type_name
	ta = data.transaction.lib_assistance_category.name
	ct = data.transaction.client_category.acronym
	csc = data.transaction.client_sub_category.acronym
	service_provider = data.transaction.service_provider.name
	fund_source = data.transaction.fund_source.description
	return JsonResponse({'fullname': fullname, 'toa': toa, 'ta': ta, 'ct': ct,'csc':csc,'service_provider': service_provider, 'fund_source': fund_source})

def print_voucher(request, pk):
	data = finance_voucherData.objects.filter(voucher_id=pk).all()
	sum = 0
	for row in data:
		totalValues = row.transactionStatus.transaction.get_total['total']
		sum=sum+totalValues
	total_values = sum
	context = {
		'finance_voucher': finance_voucher.objects.filter(id=pk).first(),
		'voucher_data': finance_voucherData.objects.filter(voucher_id=pk).all(),
		'total': total_values
	}
	return render(request,'financial/printableforms/Print_voucher.html', context)

def print_service_provider(request):
	start_date_str = request.GET.get("start_date")
	end_date_str = request.GET.get("end_date")

	start_date = datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else None
	end_date = datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str else None
	if request.method == "GET":
		data = Transaction.objects.filter(
			Q(service_provider=request.GET.get("service_provider")) &
			Q(status__in=[3, 6]) &
			Q(date_of_transaction__range=(start_date_str, end_date_str)) &
			Q(dv_number__isnull=False)
		).order_by('-tracking_number', 'dv_date')

		outside_fo = finance_outsideFo.objects.filter(
			Q(service_provider=request.GET.get("service_provider")) &
			Q(date_soa__range=(start_date_str, end_date_str))
		).order_by('-id')

		unbilled = Transaction.objects.filter(
			Q(service_provider=request.GET.get("service_provider")) &
			Q(status__in=[3, 6]) &
			Q(date_of_transaction__range=(start_date_str, end_date_str)) &
			Q(dv_number__isnull=True)
		).order_by('-tracking_number', 'dv_date')
			
		total_values_data = data.values_list('total_amount', flat=True)
		total_values = sum(float(value.replace(',', '')) for value in total_values_data)

		outside_fo_data = outside_fo.values_list('amount', flat=True)
		outside_fo_total_values = sum(float(value.replace(',', '')) for value in outside_fo_data)

		unbilled_total_values = unbilled.values_list('total_amount', flat=True)
		unbilled_final_values = sum(float(value.replace(',', '')) for value in unbilled_total_values)
	Service_provider=TransactionStatus1.objects.filter(transaction_id__service_provider=request.GET.get("service_provider")).first()

	formatted_start_date = start_date.strftime('%B %d, %Y') if start_date else None
	formatted_end_date = end_date.strftime('%B %d, %Y') if start_date else None
	context={	
		'datas': data, #TRANSACTION THAT ARE BILLED INSIDE OFFICE
		'total':total_values, #TOTAL AMOUNT
		'service_provider':Service_provider, 
		'unbilled':unbilled, #UNBILLED TRANSACTION
		'unbilled_final_values': unbilled_final_values, #TOTAL AMOUNT OF UNBILLED
		'outside_fo': outside_fo, #OUTSIDE FO
		'outside_fo_total_values': outside_fo_total_values, #TOTAL AMOUNT OF OUTSIDE THE REGION
		'date_filtered':formatted_start_date,
		'date_end_filtered':formatted_end_date,
	}
	return render(request,'financial/printableforms/print_sprovider.html', context)

@csrf_exempt
def confirmSoa(request, pk):
	if request.method == "POST":
		try:
			finance_data = finance_voucher.objects.filter(id=pk).first()
			voucher_data = finance_voucherData.objects.filter(voucher_id=pk)
			outside_fo = finance_outsideFo.objects.filter(voucher_id=finance_data.id)

			total_values_data = voucher_data.values_list('transactionStatus__total_amount', flat=True)
			outside_fo_data = outside_fo.values_list('amount', flat=True)

			# Convert to numeric in Python and calculate sum
			total_values = sum(float(value.replace(',', '')) if value else 0 for value in total_values_data)
			total_amount = sum(float(value.replace(',', '')) if value else 0 for value in outside_fo_data)

			# Calculate total sum
			total_sum = total_values + total_amount

			finance_voucher.objects.filter(id=pk).update(
				soa_total_amount = total_sum
			)
			return JsonResponse({'data': 'success', 'msg': 'Data successfully added to Voucher'})
		except RequestException as e:
			handle_error(e, "REQUEST EXCEPTION ERROR IN confirmSoa", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
		except ValidationError as e:
			handle_error(e, "VALIDATION ERROR IN REQUEST confirmSoa", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
		except IntegrityError as e:
			handle_error(e, "INTEGRITY ERROR IN REQUEST confirmSoa", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data inconsistency, please refresh'})
		except Exception as e:
			handle_error(e, "EXCEPTION ERROR IN REQUEST confirmSoa", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a problem submitting the request, please refresh'})	

@login_required
def view_dv_number(request,pk):
	finance_data = finance_voucher.objects.filter(id=pk).first()
	voucher_data = finance_voucherData.objects.filter(voucher_id=pk)
	outside_fo = finance_outsideFo.objects.filter(voucher_id=finance_data.id)

	if request.method == "POST":
		try:
			with transaction.atomic():
				finance_voucherData.objects.create(
					voucher_id=pk,
					transactionStatus_id=request.POST.get('transaction_id'),
				)

				Transaction.objects.filter(id=request.POST.get('transaction_id')).update( #PARA MABUTNGAN UG DV NUMBER
					dv_number = finance_data.voucher_title,
					dv_date = finance_data.date
				)
				return JsonResponse({'data': 'success', 'msg': 'Data successfully added to Voucher'})
		except RequestException as e:
			handle_error(e, "REQUEST EXCEPTION ERROR IN view_dv_number FO", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
		except ValidationError as e:
			handle_error(e, "VALIDATION ERROR IN REQUEST view_dv_number FO", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
		except IntegrityError as e:
			handle_error(e, "INTEGRITY ERROR IN REQUEST view_dv_number FO", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data inconsistency, please refresh'})
		except Exception as e:
			handle_error(e, "EXCEPTION ERROR IN REQUEST view_dv_number FO", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a problem submitting the request, please refresh'})	
	validation = finance_voucherData.objects.filter(voucher_id=pk).exists() or finance_outsideFo.objects.filter(voucher_id=finance_data.id).exists()

	context = {
		'finance_datas':finance_data,
		'voucher_data':voucher_data,
		'outside_fo':outside_fo,
		'total_sum':finance_data.soa_total_amount,
		'validation': validation,
	}
	return render(request, 'financial/view_voucher.html',context)

@csrf_exempt
def remove_data_outside_fo(request):
	if request.method == "POST":
		try:
			update = finance_voucher.objects.filter(id=request.POST.get('soa_id')).first()
			if update:
				update.soa_total_amount = None
				update.save()
			finance_outsideFo.objects.filter(id=request.POST.get('id')).delete()
			return JsonResponse({'data': 'success'})
		except RequestException as e:
			handle_error(e, "REQUEST EXCEPTION ERROR IN remove_data_outside_fo", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
		except ValidationError as e:
			handle_error(e, "VALIDATION ERROR IN REQUEST remove_data_outside_fo", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
		except IntegrityError as e:
			handle_error(e, "INTEGRITY ERROR IN REQUEST remove_data_outside_fo", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data inconsistency, please refresh'})
		except Exception as e:
			handle_error(e, "EXCEPTION ERROR IN REQUEST remove_data_outside_fo", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a problem submitting the request, please refresh'})

@login_required
def list_outside_fo(request):
	return render(request, "financial/outside_fo_list.html")

@login_required
def voucher_outside_fo(request, pk):
	if request.method == "POST":
		try:
			check_exists = finance_outsideFo.objects.filter(glnumber=request.POST.get('glnumber'))
			if check_exists:
				return JsonResponse({'error': True, 'msg': 'The GL number you entried already exists'})
			else:
				finance_outsideFo.objects.create(
					voucher_id=pk,
					glnumber=request.POST.get('glnumber'),
					service_provider_id=request.POST.get('service_provider'),
					date_soa=request.POST.get('date'),
					client_name=request.POST.get('clientname'),
					assistance_type=request.POST.get('assistance_type'),
					amount=request.POST.get('amount'),
				)
				return JsonResponse({'data': 'success', 'msg': 'Data successfully added to Voucher'})
		except RequestException as e:
			handle_error(e, "REQUEST EXCEPTION ERROR IN VOUCHER OUTSIDE FO", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
		except ValidationError as e:
			handle_error(e, "VALIDATION ERROR IN REQUEST VOUCHER OUTSIDE FO", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
		except IntegrityError as e:
			handle_error(e, "INTEGRITY ERROR IN REQUEST VOUCHER OUTSIDE FO", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data inconsistency, please refresh'})
		except Exception as e:
			handle_error(e, "EXCEPTION ERROR IN REQUEST VOUCHER OUTSIDE FO", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a problem submitting the request, please refresh'})
	context = {
		'data': finance_voucher.objects.filter(id=pk).first(),
		'service_provider': ServiceProvider.objects.filter(status=1)
	}
	return render(request, 'financial/outside_fo.html', context)

@login_required
def edit_outside_fo(request,pk):
	try:
		if request.method == "POST":
			finance_outsideFo.objects.filter(id=pk).update(
				glnumber=request.POST.get('glnumber'),
				service_provider_id=request.POST.get('service_provider'),
				date_soa=request.POST.get('date'),
				client_name=request.POST.get('clientname'),
				assistance_type=request.POST.get('assistance_type'),
				amount=request.POST.get('amount'),
			)
			return JsonResponse({'data': 'success', 'msg': 'Voucher successfully updated'})
	except RequestException as e:
		handle_error(e, "REQUEST EXCEPTION ERROR IN EDIT OUTSIDE FO", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
	except ValidationError as e:
		handle_error(e, "VALIDATION ERROR IN REQUEST EDIT OUTSIDE FO", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
	except IntegrityError as e:
		handle_error(e, "INTEGRITY ERROR IN REQUEST EDIT OUTSIDE FO", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a data inconsistency, please refresh'})
	except Exception as e:
		handle_error(e, "EXCEPTION ERROR IN REQUEST EDIT OUTSIDE FO", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a problem submitting the request, please refresh'})
	
	context = {
		'data':finance_outsideFo.objects.filter(id=pk).first(),
		'service_provider': ServiceProvider.objects.filter(status=1)
	}
	return render(request,'financial/edit_outside_fo.html',context)

@login_required
def finance_modal_provided(request,pk):
	voucher_data = finance_voucherData.objects.filter(transactionStatus_id=pk).first()
	transaction_id = Transaction.objects.filter(id=pk).first()
	tracking_id = transaction_id.tracking_number
	if request.method == "POST":
		try:
			with transaction.atomic():
				#check = Transaction.objects.filter(id=pk)
				if request.POST.get('update_sp') == "update_sp":
					transaction_id.service_provider_id = request.POST.get('service_provider')
					transaction_id.save()
					return JsonResponse({'data': 'success', 'msg': 'The service provider has been updated, for the tracking: {}'.format(transaction_id.tracking_number)})
				elif request.POST.get('update_sp') == "update_amount":
					transactionHistory.objects.create(
						tracking_number_id=transaction_id.tracking_number,
						total_amount=transaction_id.total_amount,
						updated_by_id=request.user.id,
						date_updated=today,
					)
					transaction_id.total_amount = request.POST.get('amount')
					transaction_id.save()
					return JsonResponse({'data': 'success', 'msg': 'The service provider has been updated, for the tracking: {}'.format(transaction_id.tracking_number)})
				else:
					return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
				
		except RequestException as e:
			handle_error(e, "REQUEST EXCEPTION ERROR IN finance_modal_provided", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
		except ValidationError as e:
			handle_error(e, "VALIDATION ERROR IN REQUEST finance_modal_provided", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
		except IntegrityError as e:
			handle_error(e, "INTEGRITY ERROR IN REQUEST finance_modal_provided", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data inconsistency, please refresh'})
		except Exception as e:
			handle_error(e, "EXCEPTION ERROR IN REQUEST finance_modal_provided", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a problem submitting the request, please refresh'})

	total_amount = transaction_description.objects.filter(tracking_number_id=transaction_id.tracking_number).aggregate(total_payment=Sum('total'))
	finance = request.user.groups.filter(name__in=['Finance', 'Super Administrator']).exists()
	context = {
		'service_provider': ServiceProvider.objects.filter(status=1),
		'transactionProvided': transaction_description.objects.filter(tracking_number=transaction_id.tracking_number),
		'viewProvidedData': transaction_description.objects.filter(tracking_number_id=transaction_id.tracking_number).order_by('-id'),
		'AssistanceProvided': AssistanceProvided.objects.filter(is_active=1),
		'transaction': transaction_id,
		'calculate': total_amount,
		'medicine': medicine.objects.filter(is_active=1),
		'voucher_id':voucher_data.voucher_id,
		'finance': finance,
		'transaction_history': transactionHistory.objects.filter(tracking_number_id=tracking_id)
	}
	return render(request,"financial/provided_data.html",context)

def update_amount(request,pk):
	transaction_id = Transaction.objects.filter(id=pk).first()
	if request.method == "POST":
		try:
			with transaction.atomic():
				check = Transaction.objects.filter(id=pk)
				if request.POST.get('status_update') == "status":
					data = TransactionStatus1.objects.filter(transaction_id=pk).update(
						status=request.POST.get("change_status"),
					)
					change_status = request.POST.get("change_status")
					if change_status == "7":
						exp_status = "Ongoing"
					elif change_status == "5":
						exp_status = "Cancelled"
					elif change_status == "6":
						exp_status = "Completed"
					elif change_status == "2":
						exp_status = "Ongoing"
					elif change_status == "4":
						exp_status = "Hold"
					else:
						exp_status = "Pending"
					data = Transaction.objects.filter(id=pk).update(
						status=request.POST.get("change_status"),
						exp_status=exp_status
					)
					return JsonResponse({'data': 'success', 'msg': 'The status has been updated'})
				else:
					if request.POST.get('sid'):
						transaction_description.objects.filter(id=request.POST.get('sid')).update(
							provided_data=request.POST.get('provided'),
							regular_price=request.POST.get('regprice'),
							regular_quantity=request.POST.get('qty'),
							discount_price=request.POST.get('discounted_price'), #DISCOUNT_PRICE NA KUHAON
							discount_quantity=request.POST.get('qty1'), #CHECKING
							total=request.POST.get('tot'),	
						)
						return JsonResponse({'data': 'success',
							'msg': 'The data provided to client, successfully updated'})
					else:
						transaction_description.objects.create(
							tracking_number_id=transaction_id.tracking_number,
							provided_data=request.POST.get('provided'),
							regular_price=request.POST.get('regprice'),
							regular_quantity=request.POST.get('qty'),
							discount_price=request.POST.get('discounted_price'), #DISCOUNT_PRICE NA KUHAON
							discount_quantity=request.POST.get('qty1'), #CHECKING
							total=request.POST.get('tot'),
							user_id=request.user.id,
						)
						return JsonResponse({'data': 'success',
											'msg': 'The data provided to client successfully added. With tracking number:  {}.'.format(check.first().tracking_number)})
		except RequestException as e:
			handle_error(e, "REQUEST EXCEPTION ERROR IN update_amount", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
		except ValidationError as e:
			handle_error(e, "VALIDATION ERROR IN REQUEST update_amount", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
		except IntegrityError as e:
			handle_error(e, "INTEGRITY ERROR IN REQUEST update_amount", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data inconsistency, please refresh'})
		except Exception as e:
			handle_error(e, "EXCEPTION ERROR IN REQUEST update_amount", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a problem submitting the request, please refresh'})
		
	total_amount = transaction_description.objects.filter(tracking_number_id=transaction_id.tracking_number).aggregate(total_payment=Sum('total'))
	context = {
		'service_provider': ServiceProvider.objects.filter(status=1),
		'transactionProvided': transaction_description.objects.filter(tracking_number=transaction_id.tracking_number).first(),
		'viewProvidedData': transaction_description.objects.filter(tracking_number_id=transaction_id.tracking_number).order_by('-id'),
		'AssistanceProvided': AssistanceProvided.objects.filter(is_active=1),
		'transaction': transaction_id,
		'calculate': total_amount,
		'medicine': medicine.objects.filter(is_active=1),
	}
	return render(request,"financial/update_status.html",context)


