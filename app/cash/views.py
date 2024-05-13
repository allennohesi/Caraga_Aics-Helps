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
	 Transaction, TransactionServiceAssistance, Mail, transaction_description, requirements_client, \
	uploadfile, TransactionStatus1, SocialWorker_Status, AssessmentProblemPresented, ErrorLogData
from app.libraries.models import Suffix, Sex, CivilStatus, Province, Tribe, region, occupation_tbl, Relation, presented_id
from django.contrib.sessions.models import Session
from app.models import AuthUser, AuthUserGroups, AuthuserDetails
from django.db.models import Value, Sum, Count
from datetime import datetime, timedelta, time, date
from django.utils import timezone
from django.contrib.auth.models import User
# import qrcode
import uuid 
import os
from django.db.models import Q
from requests.exceptions import RequestException
today = date.today()


def handle_error(error, location, user): #ERROR HANDLING
	ErrorLogData.objects.create(
		error_log=error,
		location=location,
		user_id=user,
	)

@login_required
@groups_only('Social Worker', 'Super Administrator', 'Cash')
def cash(request):
	user_address = AuthuserDetails.objects.filter(user_id=request.user.id).first()
	context = {
		'title': "Cash Transaction",
		'user_address': user_address,
	}
	return render(request, "cash/cash_transaction.html", context)

@login_required
@groups_only('Social Worker', 'Super Administrator', 'Cash')
def view_transaction(request, pk):
	try:
		if request.method == "POST":
			check = Transaction.objects.filter(id=pk)
			check.update(
				lib_type_of_assistance_id=request.POST.get('assistance_type'),
				lib_assistance_category_id=request.POST.get('assistance_category'),
				fund_source_id=request.POST.get('fund_source'),
				is_gl=request.POST.get('guarantee_letter') if request.POST.get('guarantee_letter') else 0,
				is_cv=request.POST.get('cash_voucher') if request.POST.get('cash_voucher') else 0,
				is_pcv=request.POST.get('petty_cash') if request.POST.get('petty_cash') else 0,
				is_ce_cash=request.POST.get('ce_cash') if request.POST.get('ce_cash') else 0,
				is_ce_gl=request.POST.get('ce_gl') if request.POST.get('ce_gl') else 0,
			)
			return JsonResponse({'data': 'success',
					'msg': 'You have successfully updated the data for tracking number {}.'.format(check.first().tracking_number)})
					
	except ConnectionError as ce:
		handle_error(ce, "CONNECTION ERROR IN CASH VIEW TRANSACTION", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a problem within your connection, please refresh'})
	except RequestException as re:
		handle_error(re, "NETWORK RELATED ISSUE IN CASH VIEW TRANSACTION", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a problem with network, please refresh'})
	except Exception as e:
		handle_error(e, "EXCEPTION ERROR IN CASH VIEW TRANSACTION", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was an unexpected error, please refresh'})
	
	data = Transaction.objects.filter(id=pk).first()
		
	calculate = transaction_description.objects.filter(tracking_number_id=data.tracking_number).aggregate(total_payment=Sum('total'))
	transactionProvided = transaction_description.objects.filter(tracking_number_id=data.tracking_number).first()
	picture = uploadfile.objects.filter(client_bene_id=data.client_id).first()
	
	context = {
		'transaction': data,
		'pict':picture,
		'requirements': requirements_client.objects.filter(transaction=data.id).first(),
		'family_composistion': ClientBeneficiaryFamilyComposition.objects.filter(clientbene_id=data.bene_id),
		'transaction_status': TransactionStatus1.objects.filter(transaction_id=pk).first(),
		'category': Category.objects.filter(status=1).order_by('name'),
		'sub_category': SubCategory.objects.filter(status=1).order_by('name'),
		'service_assistance': ServiceAssistance.objects.filter(status=1).order_by('name'),
		'type_of_assistance': TypeOfAssistance.objects.filter(status=1).order_by('name'),
		'purpose': Purpose.objects.filter(status=1),
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
		'Problem_Assessment':AssessmentProblemPresented.objects.filter(transaction_id=pk).first(),
		'relation': Relation.objects.filter(status=1),
		'suffix': Suffix.objects.filter(status=1).order_by('name'),
		'sex': Sex.objects.filter(status=1).order_by('name'),
		'occupation': occupation_tbl.objects.filter(is_active=1).order_by('id'),
	}
	return render(request, 'cash/view_transaction.html', context)