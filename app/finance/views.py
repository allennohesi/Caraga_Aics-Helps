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
	SubModeofAssistance, LibAssistanceType, PriorityLine, region, medicine, AssistanceProvided
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

today = date.today()

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
@groups_only('Super Administrator', 'Biller','Finance')
def financial_transaction(request):
	if request.method == "POST":
		with transaction.atomic():
			voucher=request.POST.get('voucher_title')
			date=request.POST.get('date')
			remarks=request.POST.get('remarks')
			
			lasttrack = finance_voucher.objects.order_by('-voucher_code').first()

			track_num = generate_serial_string(lasttrack.voucher_code) if lasttrack else \
				generate_serial_string(None, 'VOUCHER')

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
		TransactionStatus1.objects.filter(id=request.POST.get('transaction_id')).update(
			finance_status=1
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
	json = []
	if request.GET.get('searchTerm', ''):
		transaction = TransactionStatus1.objects.filter(Q(transaction_id__tracking_number__icontains=request.GET.get('searchTerm'),status=6,finance_status=None))[:10]
		if transaction:
			for row in transaction:
				json.append({'id': row.id,
							 'text': row.transaction.tracking_number })
		return JsonResponse(json, safe=False)
	else:
		return JsonResponse(json, safe=False)

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