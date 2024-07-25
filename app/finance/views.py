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
	uploadfile, TransactionStatus1, SocialWorker_Status, ErrorLogData
from django.contrib.sessions.models import Session
from app.models import AuthUser, AuthUserGroups
from django.db.models import Value, Sum, Count
from datetime import datetime, timedelta, time, date
from django.utils import timezone
from django.contrib.auth.models import User
from app.finance.models import finance_voucher, finance_voucherData, exporting_csv, finance_outsideFo
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
	return render(request,'financial/printsoa.html',context)


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

						return JsonResponse({'data': 'success', 'msg': 'You successfully updated the DV-Name'})
					else:
						finance_voucher.objects.create(
							voucher_code=str(unique_id).upper(),
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
		'service_provider': ServiceProvider.objects.all(),
		'fund_source': FundSource.objects.all()
	}
	return render(request,'financial/finance.html', context)


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

def export_report_csv(request):
	data = Transaction.objects.all()

	response = HttpResponse(
		content_type="text/csv",
		headers={"Content-Disposition": 'attachment; filename="financial_file.csv"'},
	)

	# Create a CSV writer and write the header
	writer = csv.writer(response)
	writer.writerow([field.name for field in exporting_csv._meta.fields])

	# Write data rows
	for row in data:
		writer.writerow([getattr(row, field.name) for field in exporting_csv._meta.fields])

	return response

@csrf_exempt  # You can remove this decorator if CSRF protection is not needed
@api_view(['GET'])
def export_fund_summary(request):
	if request.method == "GET":
		start_date_str = request.GET.get("start_date")
		end_date_str = request.GET.get("end_date")
		if request.GET.get("fund_source") == "all":
			queryset = Transaction.objects.filter(
				date_of_transaction__range=(start_date_str, end_date_str), requested_in="AGUSAN DEL NORTE"
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
				"status"

			)

			# Create the StreamingHttpResponse object with CSV header.
			response = StreamingHttpResponse(streaming_content=generate_csv_data(queryset), content_type='text/csv')
			response["Content-Disposition"] = 'attachment; filename="transactions.csv"'

			return response
		else:
			queryset = Transaction.objects.filter(fund_source_id=request.GET.get("fund_source"),requested_in="AGUSAN DEL NORTE",
				date_of_transaction__range=(start_date_str, end_date_str)
			).order_by("-id").select_related(
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
				"status"

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
					"Source of fund", "Date Interview", "Interviewer/SWO", "Service provider", "DV Date", "DV Number", "STATUS"]

	yield ','.join(header) + '\n'

	# Write rows as dictionaries
	for transaction in queryset.iterator(chunk_size=7000):
		# Map status to corresponding string
		status_str = (
			smart_str("Completed") if transaction.status == 6 else
			smart_str("Cancelled") if transaction.status == 5 else
			smart_str("Hold") if transaction.status == 4 else
			smart_str("Completed") if transaction.status == 3 else
			smart_str("Ongoing") if transaction.status == 2 else
			smart_str("Pending")
		)
		client_street_str = smart_str(transaction.client.street).replace(",", "") if transaction.client.street else ""
		
		bene_street_str = smart_str(transaction.bene.street).replace(",", "") if transaction.bene.street else ""
		total_amount_str = f'"{transaction.total_amount}"' if transaction.total_amount is not None else '0'
		service_provider_str = (
			smart_str(transaction.service_provider.name).replace(",", "")
			if transaction.service_provider and transaction.service_provider.name
			else "N/a"
		)
		dv_number_str = smart_str(transaction.dv_number).replace(",", "") if transaction.dv_number else ""
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
			smart_str(transaction.client.barangay.brgy_name),
			smart_str(transaction.client.barangay.city_code.city_name),
			client_street_str,
			smart_str(transaction.client.barangay.city_code.prov_code.prov_name),
			smart_str(transaction.client.barangay.city_code.prov_code.region_code.region_name),
			smart_str(transaction.bene.last_name),
			smart_str(transaction.bene.first_name),
			smart_str(transaction.client.middle_name),
			smart_str(transaction.bene.suffix.name) if transaction.bene.suffix and transaction.bene.suffix.name else "N/a",
			smart_str(transaction.bene.age),
			smart_str(transaction.bene.civil_status.name),
			smart_str(transaction.bene.birthdate),
			smart_str(transaction.bene.suffix.name) if transaction.bene.suffix and transaction.bene.suffix.name else "N/a",
			bene_street_str,
			smart_str(transaction.bene.barangay.brgy_name),
			smart_str(transaction.bene.barangay.city_code.city_name),
			bene_street_str,
			smart_str(transaction.bene.barangay.city_code.prov_code.prov_name),
			smart_str(transaction.bene.barangay.city_code.prov_code.region_code.region_name),
			smart_str(transaction.relation.name),
			smart_str(transaction.lib_assistance_category.name),
			total_amount_str,
			smart_str("GL") if transaction.is_gl == 1 else "CASH",
			smart_str("Referral") if transaction.is_referral == 1 else "Walk-in",
			smart_str(transaction.fund_source.name) if transaction.fund_source and transaction.fund_source.name else "N/a",
			smart_str(transaction.swo_date_time_end),
			smart_str(transaction.swo.fullname),
			service_provider_str,
			smart_str(transaction.dv_date),
			dv_number_str,
			smart_str(status_str)
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


@login_required
def get_data_transaction(request, pk):
	data = TransactionStatus1.objects.filter(transaction_id=pk).first()
	fullname = data.transaction.client.get_client_fullname
	toa = data.transaction.lib_type_of_assistance.type_name
	ta = data.transaction.lib_assistance_category.name
	ct = data.transaction.client_category.acronym
	csc = data.transaction.client_sub_category.acronym
	service_provider = data.transaction.service_provider.name
	fund_source = data.transaction.fund_source.name
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
	return render(request,'financial/Print_voucher.html', context)

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
	return render(request,'financial/print_sprovider.html', context)


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

	total_values_data = voucher_data.values_list('transactionStatus__total_amount', flat=True)
	outside_fo_data = outside_fo.values_list('amount', flat=True)

	# Convert to numeric in Python and calculate sum
	total_values = sum(float(value.replace(',', '')) if value else 0 for value in total_values_data)
	total_amount = sum(float(value.replace(',', '')) if value else 0 for value in outside_fo_data)

	# Calculate total sum
	total_sum = total_values + total_amount

	context = {
		'finance_datas':finance_data,
		'voucher_data':voucher_data,
		'outside_fo':outside_fo,
		'total_sum':total_sum,
	}
	return render(request, 'financial/view_voucher.html',context)

@csrf_exempt
def remove_data_outside_fo(request):
	if request.method == "POST":
		finance_outsideFo.objects.filter(id=request.POST.get('id')).delete()
	return JsonResponse({'data': 'success'})

def list_outside_fo(request):
	return render(request, "financial/outside_fo_list.html")

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
					transaction_id.total_amount = request.POST.get('amount')
					transaction_id.save()
					return JsonResponse({'data': 'success', 'msg': 'The service provider has been updated, for the tracking: {}'.format(transaction_id.tracking_number)})
				else:
					provided_to_client = request.POST.getlist('provided[]')
					regular_price = request.POST.getlist('regprice[]')
					regular_quantity = request.POST.getlist('qty[]')
					discount = request.POST.getlist('dsc[]')
					discount_price = request.POST.getlist('discounted_price[]')
					discount_quantity = request.POST.getlist('qty1[]')
					total = request.POST.getlist('tot[]')
					
					if not provided_to_client == [''] and not regular_price == [''] and not regular_quantity == [''] and not discount_price == [
						''] and not discount_quantity == [''] and not total == ['']:
						data = [
							{'provided_to_client': fn, 'regular_price': mn, 'regular_quantity': ln,'discount': disc, 'discount_price': sx, 'discount_quantity': b, 'total': o}
							for fn, mn, ln, disc, sx, b, o in
							zip(provided_to_client, regular_price, regular_quantity, discount, discount_price, discount_quantity, total)
						]
						transaction_provided = transaction_description.objects.filter(tracking_number=tracking_id)
						store = [row.id for row in transaction_provided]
						if transaction_provided:
							y = 1
							x = 0
							for row in data:
								if y > len(transaction_provided):
									transaction_description.objects.create(
										tracking_number_id=transaction_id.tracking_number,
										provided_data=row['provided_to_client'],
										regular_price=row['regular_price'],
										regular_quantity=row['regular_quantity'],
										discount=row['discount'],
										discount_price=row['discount_price'],
										discount_quantity=row['discount_quantity'],
										total=row['total'],
										user_id=request.user.id,
									)
								else:
									transaction_description.objects.filter(id=store[x]).update(
										tracking_number_id=transaction_id.tracking_number,
										provided_data=row['provided_to_client'],
										regular_price=row['regular_price'],
										regular_quantity=row['regular_quantity'],
										discount=row['discount'],
										discount_price=row['discount_price'],
										discount_quantity=row['discount_quantity'],
										total=row['total'],
									)
									y += 1
									x += 1
									
							return JsonResponse({'data': 'success', 'msg': 'The data provided to client was successfully saved'})
						else:
							for row in data:
								transaction_description.objects.create(
									tracking_number_id=transaction_id.tracking_number,
									provided_data=row['provided_to_client'],
									regular_price=row['regular_price'],
									regular_quantity=row['regular_quantity'],
									discount=row['discount'],
									discount_price=row['discount_price'],
									discount_quantity=row['discount_quantity'],
									total=row['total'],
									user_id=request.user.id,
								)
							return JsonResponse({'data': 'success', 'msg': 'The data provided to client was successfully saved'})
								
					else:
						# Handle case where lengths are not equal
						handle_error(e, "ERROR IN DYNAMIC ENTRY FINANCE", request.user.id)
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
					data = Transaction.objects.filter(id=pk).update(
						status=request.POST.get("change_status")
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


