from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.db import transaction
from datetime import timedelta, date
from app.forms import ImageForm
from app.global_variable import groups_only
from app.libraries.models import FileType, Relation, Category, SubCategory, ServiceProvider, ServiceAssistance, \
	TypeOfAssistance, Purpose, ModeOfAssistance, ModeOfAdmission, FundSource, SubModeofAssistance, TypeOfAssistance, \
	SubModeofAssistance, LibAssistanceType, PriorityLine, region, medicine, AssistanceProvided, FundSource
from app.requests.models import ClientBeneficiary, ClientBeneficiaryFamilyComposition, \
	 Transaction, TransactionServiceAssistance, Mail, transaction_description, \
	uploadfile, TransactionStatus1, SocialWorker_Status
from django.contrib.sessions.models import Session
from app.models import AuthUser, AuthUserGroups
from django.db.models import Value, Sum, Count
from datetime import datetime, timedelta, time, date
from django.utils import timezone
from django.contrib.auth.models import User
from app.finance.models import finance_voucher, finance_voucherData
from django.db.models import Q

import csv
from django.utils.encoding import smart_str
from io import StringIO
from django.http import HttpResponse
today = date.today()

class Echo:
	def write(self, value):
		return value

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

def streaming_csv_view(request):
	queryset = Transaction.objects.all()
	# Create the HttpResponse object with CSV header.
	response = HttpResponse(content_type="text/csv")
	response["Content-Disposition"] = 'attachment; filename="transactions.csv"'
	csv_writer = csv.writer(response)

	# Write the header
	header = ["Tracking_number", "Client Surname", "Client First name", "Client Middle Name", "Client Ext. name", "Client age",
			  "Civil Status", "Birthday", "Client Sex", "Street", "Barangay", "Municipality", "Client District",
			  "Province", "Region", "Bene Surname", "Bene First name", "Bene Middle Name", "Bene Ext. name", "Bene age",
			  "Civil Status", "Birthday", "Bene Sex", "Street", "Barangay", "Municipality", "Bene District", "Bene Province",
			  "Region", "Relation", "Type of assistance", "Assistance Category","Amount of assistance", "Mode of release", "Source of referral", #DONE
			  "Source of fund", "Purpose", "Date Interview", "Interviewer/SWO", "Service provider", "GL Number",
			  "DV Date", "DV Number", "Cancellation"]
	csv_writer.writerow(header)
	rows = [
		[
			smart_str(data.tracking_number),
			smart_str(data.client.last_name),
			smart_str(data.client.first_name),
			smart_str(data.client.middle_name),
			smart_str(data.client.suffix.name) if data.client.suffix and data.client.suffix.name else "N/a",
			smart_str(data.client.get_age),
			smart_str(data.client.civil_status.name),
			smart_str(data.client.birthdate),
			smart_str(data.client.sex.name),
			smart_str(data.client.street),
			smart_str(data.client.barangay.brgy_name),
			smart_str(data.client.barangay.city_code.city_name),
			smart_str(data.client.street),
			smart_str(data.client.barangay.city_code.prov_code.prov_name),
			smart_str(data.client.barangay.city_code.prov_code.region_code.region_name),
			smart_str(data.bene.last_name),
			smart_str(data.bene.first_name),
			smart_str(data.bene.middle_name),
			smart_str(data.bene.suffix.name) if data.bene.suffix and data.bene.suffix.name else "N/a",
			smart_str(data.bene.get_age),
			smart_str(data.bene.civil_status.name),
			smart_str(data.bene.birthdate),
			smart_str(data.bene.sex.name),
			smart_str(data.bene.street),
			smart_str(data.bene.barangay.brgy_name),
			smart_str(data.bene.barangay.city_code.city_name),
			smart_str(data.bene.street),
			smart_str(data.bene.barangay.city_code.prov_code.prov_name),
			smart_str(data.bene.barangay.city_code.prov_code.region_code.region_name),
			smart_str(data.relation.name) if data.relation and data.relation.name else "",
			smart_str(data.lib_type_of_assistance.type_name),
			smart_str(data.lib_assistance_category.name),
			smart_str(data.get_finance_total),
			smart_str("GL") if data.is_gl== 1 else smart_str("Cash"),
			smart_str("Walk-in") if data.is_walkin== 1 else smart_str("Referral"),
			smart_str(data.fund_source.name) if data.fund_source and data.fund_source.name else "N/a",
			smart_str(data.purpose),
			smart_str(data.date_time_assessment),
			smart_str(data.swo.get_fullname),
			smart_str(data.service_provider.name) if data.service_provider and data.service_provider.name else "N/a",
			smart_str("GL") if data.is_gl== 1 else smart_str("N/a"),
			smart_str(data.finance_dv) if data.finance_dv else smart_str("N/a"),
			smart_str(data.finance_dv_date) if data.finance_dv else smart_str("N/a"),
			smart_str(data.get_finance_status),
			# Add more fields as needed
		]
		for data in queryset
	]
	# Write all rows at once
	csv_writer.writerows(rows)
	return response

def export_csv(request):
	return streaming_csv_view(request)

def export_fund_summary(request):
	if request.method == "GET":
		if request.GET.get('fund_source') == "all":
			queryset = Transaction.objects.all()
			# Create the HttpResponse object with CSV header.
			response = HttpResponse(content_type="text/csv")
			response["Content-Disposition"] = 'attachment; filename="transactions.csv"'
			csv_writer = csv.writer(response)

			# Write the header
			header = ["Tracking_number", "Client Surname", "Client First name", "Client Middle Name", "Client Ext. name", "Client age",
					"Civil Status", "Birthday", "Client Sex", "Street", "Barangay", "Municipality", "Client District",
					"Province", "Region", "Bene Surname", "Bene First name", "Bene Middle Name", "Bene Ext. name", "Bene age",
					"Civil Status", "Birthday", "Bene Sex", "Street", "Barangay", "Municipality", "Bene District", "Bene Province",
					"Region", "Relation", "Type of assistance", "Assistance Category","Amount of assistance", "Mode of release", "Source of referral", #DONE
					"Source of fund", "Purpose", "Date Interview", "Interviewer/SWO", "Service provider", "GL Number",
					"DV Date", "DV Number", "Cancellation"]
			csv_writer.writerow(header)
			rows = [
				[
					smart_str(data.tracking_number),
					smart_str(data.client.last_name),
					smart_str(data.client.first_name),
					smart_str(data.client.middle_name),
					smart_str(data.client.suffix.name) if data.client.suffix and data.client.suffix.name else "N/a",
					smart_str(data.client.get_age),
					smart_str(data.client.civil_status.name),
					smart_str(data.client.birthdate),
					smart_str(data.client.sex.name),
					smart_str(data.client.street),
					smart_str(data.client.barangay.brgy_name),
					smart_str(data.client.barangay.city_code.city_name),
					smart_str(data.client.street),
					smart_str(data.client.barangay.city_code.prov_code.prov_name),
					smart_str(data.client.barangay.city_code.prov_code.region_code.region_name),
					smart_str(data.bene.last_name),
					smart_str(data.bene.first_name),
					smart_str(data.bene.middle_name),
					smart_str(data.bene.suffix.name) if data.bene.suffix and data.bene.suffix.name else "N/a",
					smart_str(data.bene.get_age),
					smart_str(data.bene.civil_status.name),
					smart_str(data.bene.birthdate),
					smart_str(data.bene.sex.name),
					smart_str(data.bene.street),
					smart_str(data.bene.barangay.brgy_name),
					smart_str(data.bene.barangay.city_code.city_name),
					smart_str(data.bene.street),
					smart_str(data.bene.barangay.city_code.prov_code.prov_name),
					smart_str(data.bene.barangay.city_code.prov_code.region_code.region_name),
					smart_str(data.relation.name) if data.relation and data.relation.name else "",
					smart_str(data.lib_type_of_assistance.type_name),
					smart_str(data.lib_assistance_category.name),
					smart_str(data.get_finance_total),
					smart_str("GL") if data.is_gl== 1 else smart_str("Cash"),
					smart_str("Walk-in") if data.is_walkin== 1 else smart_str("Referral"),
					smart_str(data.fund_source.name) if data.fund_source and data.fund_source.name else "N/a",
					smart_str(data.purpose),
					smart_str(data.date_time_assessment),
					smart_str(data.swo.get_fullname),
					smart_str(data.service_provider.name) if data.service_provider and data.service_provider.name else "N/a",
					smart_str("GL") if data.is_gl== 1 else smart_str("N/a"),
					smart_str(data.finance_dv) if data.finance_dv else smart_str("N/a"),
					smart_str(data.finance_dv_date) if data.finance_dv else smart_str("N/a"),
					smart_str(data.get_finance_status),
					# Add more fields as needed
				]
				for data in queryset
			]
			# Write all rows at once
			csv_writer.writerows(rows)
			return response
		else:
			start_date_str = request.GET.get("start_date")
			end_date_str = request.GET.get("end_date")

			# Convert the date strings to datetime objects
			start_date = datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else None
			end_date = datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str else None
			queryset = Transaction.objects.filter(fund_source_id=request.GET.get('fund_source'),date_of_transaction__range=(start_date, end_date))
			# Create the HttpResponse object with CSV header.
			response = HttpResponse(content_type="text/csv")
			response["Content-Disposition"] = 'attachment; filename="transactions.csv"'
			csv_writer = csv.writer(response)

			# Write the header
			header = ["Tracking_number", "Client Surname", "Client First name", "Client Middle Name", "Client Ext. name", "Client age",
					"Civil Status", "Birthday", "Client Sex", "Street", "Barangay", "Municipality", "Client District",
					"Province", "Region", "Bene Surname", "Bene First name", "Bene Middle Name", "Bene Ext. name", "Bene age",
					"Civil Status", "Birthday", "Bene Sex", "Street", "Barangay", "Municipality", "Bene District", "Bene Province",
					"Region", "Relation", "Type of assistance", "Assistance Category","Amount of assistance", "Mode of release", "Source of referral", #DONE
					"Source of fund", "Purpose", "Date Interview", "Interviewer/SWO", "Service provider", "GL Number",
					"DV Date", "DV Number", "Cancellation"]
			csv_writer.writerow(header)
			rows = [
				[
					smart_str(data.tracking_number),
					smart_str(data.client.last_name),
					smart_str(data.client.first_name),
					smart_str(data.client.middle_name),
					smart_str(data.client.suffix.name) if data.client.suffix and data.client.suffix.name else "N/a",
					smart_str(data.client.get_age),
					smart_str(data.client.civil_status.name),
					smart_str(data.client.birthdate),
					smart_str(data.client.sex.name),
					smart_str(data.client.street),
					smart_str(data.client.barangay.brgy_name),
					smart_str(data.client.barangay.city_code.city_name),
					smart_str(data.client.street),
					smart_str(data.client.barangay.city_code.prov_code.prov_name),
					smart_str(data.client.barangay.city_code.prov_code.region_code.region_name),
					smart_str(data.bene.last_name),
					smart_str(data.bene.first_name),
					smart_str(data.bene.middle_name),
					smart_str(data.bene.suffix.name) if data.bene.suffix and data.bene.suffix.name else "N/a",
					smart_str(data.bene.get_age),
					smart_str(data.bene.civil_status.name),
					smart_str(data.bene.birthdate),
					smart_str(data.bene.sex.name),
					smart_str(data.bene.street),
					smart_str(data.bene.barangay.brgy_name),
					smart_str(data.bene.barangay.city_code.city_name),
					smart_str(data.bene.street),
					smart_str(data.bene.barangay.city_code.prov_code.prov_name),
					smart_str(data.bene.barangay.city_code.prov_code.region_code.region_name),
					smart_str(data.relation.name) if data.relation and data.relation.name else "",
					smart_str(data.lib_type_of_assistance.type_name),
					smart_str(data.lib_assistance_category.name),
					smart_str(data.get_finance_total),
					smart_str("GL") if data.is_gl== 1 else smart_str("Cash"),
					smart_str("Walk-in") if data.is_walkin== 1 else smart_str("Referral"),
					smart_str(data.fund_source.name) if data.fund_source and data.fund_source.name else "N/a",
					smart_str(data.purpose),
					smart_str(data.date_time_assessment),
					smart_str(data.swo.get_fullname),
					smart_str(data.service_provider.name) if data.service_provider and data.service_provider.name else "N/a",
					smart_str("GL") if data.is_gl== 1 else smart_str("N/a"),
					smart_str(data.finance_dv) if data.finance_dv else smart_str("N/a"),
					smart_str(data.finance_dv_date) if data.finance_dv else smart_str("N/a"),
					smart_str(data.get_finance_status),
					# Add more fields as needed
				]
				for data in queryset
			]
			# Write all rows at once
			csv_writer.writerows(rows)
			return response
			


@login_required
@groups_only('Super Administrator', 'Biller','Finance')
def financial_transaction(request):
	if request.method == "POST":
		with transaction.atomic():
			voucher=request.POST.get('voucher_title')
			date=request.POST.get('date')
			remarks=request.POST.get('remarks')
			
			lasttrack = finance_voucher.objects.order_by('-voucher_code').first()
			track_num = generate_serial_string(lasttrack.voucher_code) if lasttrack else \
				generate_serial_string(None, 'CODE')

			finance_voucher.objects.create(
				voucher_code=track_num,
				voucher_title=voucher,
				date=date,
				remarks=remarks,
				user_id=request.user.id,
				status=1,
			)
			return JsonResponse({'data': 'success', 'msg': 'Data Saved.'})
	context = {
		'service_provider': ServiceProvider.objects.filter(status=1),
		'fund_source': FundSource.objects.filter(status=1)
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


@login_required 
def voucher_modal(request, pk):
	if request.method == "POST":
		finance_voucherData.objects.create(
			voucher_id=pk,
			transactionStatus_id=request.POST.get('transaction_id'),
		)
		return JsonResponse({'data': 'success', 'msg': 'Data successfully added to Voucher'})
	
	test = finance_voucherData.objects.filter(voucher_id=pk)
	context = {
		'voucherTitle':finance_voucher.objects.filter(id=pk).first(),
		'voucherData': test
	}
	return render(request, 'financial/voucher_modal.html',context)

@csrf_exempt
def remove_voucherData(request):
	if request.method == "POST":
		data = finance_voucherData.objects.filter(id=request.POST.get('id')).first()
		TransactionStatus1.objects.filter(id=data.transactionStatus_id).update(
			finance_status=None,
		)
		data = finance_voucherData.objects.filter(id=request.POST.get('id')).delete()
	return JsonResponse({'data': 'success'})

@csrf_exempt
def get_all_transaction(request):
	json_data = []
	search_term = request.GET.get('searchTerm', '')
	if search_term:
		transactions = TransactionStatus1.objects.filter(
			Q(transaction_id__client_id__client_bene_fullname__icontains=search_term) &
			Q(status__in=[3, 6]) &
			Q(finance_status=None)
		)[:10]

		if transactions.exists():
			json_data = list(transactions.values_list('id', 'transaction__client__client_bene_fullname', named=True))
			json_data = [{'id': row.id, 'text': row.transaction__client__client_bene_fullname} for row in json_data]

	return JsonResponse(json_data, safe=False)


@login_required
def get_data_transaction(request, pk):
	data = TransactionStatus1.objects.filter(id=pk).first()

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
	sum=0
	start_date_str = request.GET.get("start_date")
	end_date_str = request.GET.get("end_date")

	# Convert the date strings to datetime objects
	start_date = datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else None
	end_date = datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str else None
	if request.method == "GET":
		data = TransactionStatus1.objects.filter(transaction_id__service_provider=request.GET.get("service_provider"),status=6,transaction_id__date_of_transaction__range=(start_date, end_date)).all()
		for row in data:
			totalValues = row.transaction.get_total['total']
			sum=sum+totalValues
	total_values = sum
	Service_provider=TransactionStatus1.objects.filter(transaction_id__service_provider=request.GET.get("service_provider"),status=6).first()
	context={
		'datas': data,
		'total':total_values,
		'service_provider':Service_provider,
	}
	return render(request,'financial/print_sprovider.html', context)

def view_dv_number(request,pk):
	if request.method == "POST":
		finance_voucherData.objects.create(
			voucher_id=pk,
			transactionStatus_id=request.POST.get('transaction_id'),
		)
		return JsonResponse({'data': 'success', 'msg': 'Data successfully added to Voucher'})
	finance_data = finance_voucher.objects.filter(id=pk).first()
	voucher_data = finance_voucherData.objects.filter(voucher_id=pk)
	context = {
		'finance_datas':finance_data,
		'voucher_data':voucher_data,
	}
	return render(request, 'financial/view_voucher.html',context)

def finance_modal_provided(request,pk):
	voucher_data = finance_voucherData.objects.filter(transactionStatus_id=pk).first()
	transaction_id = Transaction.objects.filter(id=pk).first()
	if request.method == "POST":
		with transaction.atomic():
			check = Transaction.objects.filter(id=pk)
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
	total_amount = transaction_description.objects.filter(tracking_number_id=transaction_id.tracking_number).aggregate(total_payment=Sum('total'))
	context = {
		'service_provider': ServiceProvider.objects.filter(status=1),
		'transactionProvided': transaction_description.objects.filter(tracking_number=transaction_id.tracking_number).first(),
		'viewProvidedData': transaction_description.objects.filter(tracking_number_id=transaction_id.tracking_number).order_by('-id'),
		'AssistanceProvided': AssistanceProvided.objects.filter(is_active=1),
		'transaction': transaction_id,
		'calculate': total_amount,
		'medicine': medicine.objects.filter(is_active=1),
		'voucher_id':voucher_data.voucher_id
	}
	return render(request,"financial/provided_data.html",context)

