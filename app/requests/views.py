from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.db import transaction, IntegrityError
from datetime import timedelta, date, datetime, timedelta, time #DATE TIME
from app.forms import ImageForm
from app.global_variable import groups_only
from app.libraries.models import FileType, Relation, Category, SubCategory, ServiceProvider, ServiceAssistance, \
	TypeOfAssistance, Purpose, ModeOfAssistance, ModeOfAdmission, FundSource, SubModeofAssistance, TypeOfAssistance, \
	SubModeofAssistance, LibAssistanceType, PriorityLine, region, medicine, AssistanceProvided, SignatoriesTbl, Suffix, \
	Sex, occupation_tbl
from app.requests.models import ClientBeneficiary, ClientBeneficiaryFamilyComposition, \
	 Transaction, TransactionServiceAssistance, Mail, transaction_description, requirements_client, \
	uploadfile, TransactionStatus1, SocialWorker_Status, AssessmentProblemPresented, ErrorLogData
from django.contrib.sessions.models import Session
from app.models import AuthUser, AuthUserGroups, AuthtokenToken, AuthuserDetails
from django.db.models import Value, Sum, Count, Q
from django.utils import timezone
from django.contrib.auth.models import User
from django.views.decorators.cache import cache_control
from django.http import HttpResponse
from requests.exceptions import RequestException
import uuid 
import os
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from decimal import Decimal
from rest_framework.authtoken.models import Token
import os
import base64
import uuid

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


def handle_error(error, location, user): #ERROR HANDLING
	ErrorLogData.objects.create(
		error_log=error,
		location=location,
		user_id=user,
	)
# def delete_from_error(data): #DELETE FROM ERROR HANDLING
# 	if data and data.id:
# 		Transaction.objects.filter(id=data.id).delete()
# 		AssessmentProblemPresented.objects.filter(transaction_id=data.id).delete()
# 		TransactionStatus1.objects.filter(transaction_id=data.id).delete()

def transaction_request(request):
	try:
		with transaction.atomic():
			unique_id = uuid.uuid4()
			if request.POST.get('same_with_client'):
				# Checkbox is checked, handle accordingly
				bene_category=request.POST.get('clients_category') #IF SAME WITH CLIENT, THE CATEGORY IS SAME TO BENE
				bene_sub_category=request.POST.get('clients_subcategory')
			else:
				# Checkbox is not checked
				bene_category=request.POST.get('bene_category')
				bene_sub_category=request.POST.get('bene_subcategory')
			data = Transaction( #DATA.ID SHOULD ALWAYS BE THE LATEST FOREIGNKEY TO ASSESSMENT TABLE AND TRANSACTIONSTATUS TABLE
				tracking_number=str(unique_id).upper(),
				relation_id=request.POST.get('relationship'),
				client_id=request.POST.get('client'),
				bene_id=request.POST.get('beneficiary'),
				client_category_id=request.POST.get('clients_category'),
				client_sub_category_id=request.POST.get('clients_subcategory'),
				bene_category_id=bene_category,
				bene_sub_category_id=bene_sub_category,
				lib_type_of_assistance_id=request.POST.get('assistance_type'),
				lib_assistance_category_id=request.POST.get('assistance_category'),
				date_entried=request.POST.get('date_entried'),
				swo_id=request.POST.get('swo_id'),
				is_case_study=request.POST.get('case_study'),
				priority_id=request.POST.get('priority_name'),
				is_return_new=request.POST.get('new_returning'), 
				is_onsite_offsite=request.POST.get('site'),
				is_online=request.POST.get('online') if request.POST.get('online') else None,
				is_walkin=request.POST.get('walkin') if request.POST.get('walkin') else None,
				is_referral=request.POST.get('referral') if request.POST.get('referral') else None,
				is_gl=request.POST.get('guarantee_letter') if request.POST.get('guarantee_letter') else 0,
				is_cv=request.POST.get('cash_voucher') if request.POST.get('cash_voucher') else 0,
				is_pcv=request.POST.get('petty_cash') if request.POST.get('petty_cash') else 0,
				is_ce_cash=request.POST.get('ce_cash') if request.POST.get('ce_cash') else 0,
				is_ce_gl=request.POST.get('ce_gl') if request.POST.get('ce_gl') else 0,
				transaction_status=1,
				requested_in=request.POST.get('requested_in'),
			)
			data.save()
			AssessmentProblemPresented.objects.create(
				problem_presented=request.POST.get('problem'),
				transaction_id=data.id
			)
			TransactionStatus1.objects.create(
				transaction_id=data.id,
				queu_number=request.POST.get('queu_number'),
				verified_time_start=data.date_entried,
				is_verified = "1",
				verifier_id=request.user.id,
				verified_time_end=data.date_entried,
				status="1",
				transaction_status=1,
			)
			return JsonResponse({'data': 'success', 'msg': 'New requests has been created. Please wait for the reviewal of your requests and copy the generated reference number.',
						'tracking_number': unique_id})
			# else:
			# 	return JsonResponse({'error': True, 'msg': 'There was a network traffic please refresh'})

		
	except RequestException as e:
		handle_error(e, "REQUEST EXCEPTION ERROR IN REQUEST TRANSACTION", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
	except ValidationError as e:
		handle_error(e, "VALIDATION ERROR IN REQUEST TRANSACTION", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
	except IntegrityError as e:
		handle_error(e, "INTEGRITY ERROR IN REQUEST TRANSACTION", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a data inconsistency, please refresh'})
	except Exception as e:
		handle_error(e, "EXCEPTION ERROR IN REQUEST TRANSACTION", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a problem submitting the request, please refresh'})

		
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@groups_only('Verifier', 'Social Worker', 'Super Administrator')
def requests(request):
	try:
		today = date.today()
		active_swo = SocialWorker_Status.objects.all()
		if request.method == "POST":
			# check_transaction = TransactionStatus1.objects.filter(transaction_id__client_id=request.POST.get('client'),transaction_id__lib_assistance_category_id=request.POST.get('assistance_category'),status=6).last()
			check_client = TransactionStatus1.objects.filter(
				(
					Q(transaction_id__client_id=request.POST.get('client')) &
					Q(transaction_id__lib_assistance_category_id=request.POST.get('assistance_category')) &
					(Q(status=6))
				)
			).last()
			check_beneficiary = TransactionStatus1.objects.filter(
				Q(transaction_id__bene_id=request.POST.get('beneficiary')) &
				Q(transaction_id__lib_assistance_category_id=request.POST.get('assistance_category')) &
				Q(status__in=[1, 2, 6])
			).last()
			if request.POST.get('justification'): #Whatever the condition is as long as nay justification proceed
				submission=transaction_request(request)
				return submission
			else:
				if check_client:
					# Get the latest transaction's end date
					client_date_entried = check_client.swo_time_end.date()
					threemonths1 = timedelta(3*365/12)
					result1 = (client_date_entried + threemonths1).isoformat()
					convertedDate = date.fromisoformat(result1)
					present = datetime.now().date()
					dateStr = convertedDate.strftime("%d %b, %Y")
					if present > convertedDate: #IF LAPAS NA SYAS 3 months same client
						submission=transaction_request(request)
						return submission
					else: #IF dili pa sya lapas 3 months, walay justification
						return JsonResponse({'error': True,
											'msg': 'The assistance is not yet available for the client. Please wait for another 3 months (until {}) or provide justification.'.format(dateStr)})
				elif check_beneficiary:
					if check_beneficiary.swo_time_end:
					# Get the latest transaction's end date
						bene_date_entried = check_beneficiary.swo_time_end.date()
						threemonths2 = timedelta(3*365/12)
						result2 = (bene_date_entried + threemonths2).isoformat()
						convertedDate1 = date.fromisoformat(result2)
						present1 = datetime.now().date()
						dateStr1 = convertedDate1.strftime("%d %b, %Y")
						if present1 > convertedDate1: #naa na syay transaction but lapas na 3 months, proceed 
							submission=transaction_request(request)
							return submission
						else: #IF dili pa sya lapas 3 months, walay justification
							return JsonResponse({'error': True,
											'msg': 'The assistance is not yet available for the beneficiary. Please wait for another 3 months (until {}) or provide justification.'.format(dateStr1)})
					elif check_beneficiary.swo_time_end == None:
						return JsonResponse({'error': True, 'msg': 'The beneficiary have a pending/ongoing transaction, please update the status'})
				else:
					submission=transaction_request(request) #IF new pa ang client walay transaction history
					return submission
			
	except ValidationError as e:
		handle_error(e, "VALIDATION ERROR IN REQUEST PAGE", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
	except IntegrityError as e:
		handle_error(e, "INTEGRITY ERROR IN REQUEST PAGE", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a data inconsistency, please refresh'})
	except ConnectionError as ce:
		# Handle loss of connection (e.g., log the error)
		handle_error(ce, "CONNECTION ERROR IN REQUEST PAGE", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a problem within your connection, please refresh'})
	except RequestException as re:
		# Handle other network-related errors (e.g., log the error)
		handle_error(re, "NETWORK RELATED ISSUE IN REQUEST PAGE", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a problem with network, please refresh'})
	except Exception as e:
		# Handle other unexpected errors (e.g., log the error)
		handle_error(e, "EXCEPTION ERROR IN REQUEST PAGE", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was an unexpected error, please refresh'})

	# active_sw = SocialWorker_Status.objects.filter(status=2,date_transaction=today)
	
	context = {
		'title': 'New Requests',
		'user_details': AuthuserDetails.objects.filter(user_id=request.user.id).first(),
		# 'file_type': FileType.objects.filter(status=1, is_required=1),
		'relation': Relation.objects.filter(status=1),
		'category': Category.objects.filter(status=1),
		'sub_category': SubCategory.objects.filter(status=1),
		'service_provider': ServiceProvider.objects.filter(status=1),
		'type_of_assistance': TypeOfAssistance.objects.filter(status=1),
		'sub_category_assistsance': SubModeofAssistance.objects.filter(status=1),
		'assistance_type': LibAssistanceType.objects.filter(is_active=1).order_by('type_name'),
		'PriorityLine': PriorityLine.objects.filter(is_active=1).order_by('id'),
		'today':today,
		'Purpose': Purpose.objects.filter(status=1)
		# 'active_swo':active_sw,
	}
	return render(request, 'requests/requests.html', context)


@login_required
def get_client_info(request, pk):
	if request.method == "GET":
		data = ClientBeneficiary.objects.filter(id=pk).first()
		transaction = Transaction.objects.filter(client_id=data.id).first()
		if transaction:
			new = "2"
		else:
			new = "1"
		eid = data.id
		birthdate = data.birthdate
		age = data.get_age
		sex = data.sex.name
		contact_number = data.contact_number
		civil_status = data.civil_status.name
		region = data.barangay.city_code.prov_code.region_code.region_name
		province = data.barangay.city_code.prov_code.prov_name
		city = data.barangay.city_code.city_name
		barangay = data.barangay.brgy_name #done
		village = data.village
		house_no = data.house_no
		street = data.street
		client_id = pk
		id_presented = data.presented.presented
		id_presentedNo = data.presented_id_no if data.presented_id_no else 'N/A'
		is_4ps = 'Yes' if data.is_4ps else 'No'
		id_number_4ps = data.number_4ps_id_number if data.number_4ps_id_number else 'N/A'
		is_indi = 'Yes' if data.is_indi else 'No'
		tribe = data.tribu.name if data.tribu_id else 'N/A'
		
		transaction_history = [dict(tracking_number=row.transaction.tracking_number,type_of_assitance=row.transaction.lib_type_of_assistance.type_name,assistance_category=row.transaction.lib_assistance_category.name,date_assessment=row.end_assessment,social_worker=row.transaction.swo.get_fullname,status="Completed") for row in
							TransactionStatus1.objects.filter(Q(transaction_id__client_id=pk,status=6) | Q(transaction_id__client_id=pk,status=3)).order_by('-id')]

		return JsonResponse({'new': new, 'birthdate': birthdate, 'age': age, 'sex': sex, 'contact_number': contact_number,
							 'civil_status': civil_status,'region': region, 'province': province, 'city': city, 'barangay': barangay,
							 'village': village, 'house_no': house_no, 'street': street, 'is_4ps': is_4ps,
							 'id_number_4ps': id_number_4ps, 'is_indi': is_indi, 'tribe': tribe, 'client_id':client_id, 'transaction_history':transaction_history, 'id_presented':id_presented,'id_presentedNo':id_presentedNo})


@login_required
def get_bene_info(request, pk):
	data = ClientBeneficiary.objects.filter(id=pk).first()
	birthdate = data.birthdate
	age = data.get_age
	sex = data.sex.name
	contact_number = data.contact_number
	civil_status = data.civil_status.name
	region = data.barangay.city_code.prov_code.region_code.region_name
	province = data.barangay.city_code.prov_code.prov_name
	city = data.barangay.city_code.city_name
	barangay = data.barangay.brgy_name
	village = data.village
	house_no = data.house_no
	street = data.street
	is_4ps = 'Yes' if data.is_4ps else 'No'
	id_number_4ps = data.number_4ps_id_number if data.number_4ps_id_number else 'N/A'
	is_indi = 'Yes' if data.is_indi else 'No'
	tribe = data.tribu.name if data.tribu_id else 'N/A'
	id_presented = data.presented.presented
	id_presentedNo = data.presented_id_no if data.presented_id_no else 'N/A'
	family_composistion = [dict(fullname=row.get_family_fullname_formatted,sex=row.sex.name, birthdate=row.birthdate, relation=row.relation.name, age=row.get_age,
								occupation=row.occupation.occupation_name, salary=row.salary) for row in
						   ClientBeneficiaryFamilyComposition.objects.filter(clientbene_id=pk)]
	return JsonResponse({'birthdate': birthdate, 'age': age, 'sex': sex, 'contact_number': contact_number,
						 'civil_status': civil_status, 'region': region, 'province': province, 'city': city, 'barangay': barangay,
						 'village': village, 'house_no': house_no, 'street': street, 'is_4ps': is_4ps,
						 'id_number_4ps': id_number_4ps, 'is_indi': is_indi, 'tribe': tribe,
						 'family_composistion': family_composistion, 'id_presented':id_presented, 'id_presentedNo': id_presentedNo})


@login_required
@groups_only('Verifier', 'Super Administrator', 'Surveyor', 'Finance', 'Social Worker', 'biller')
def incoming(request):
	user_address = AuthuserDetails.objects.filter(user_id=request.user.id).first()
	current_year = today.year
	# token = Token.objects.create(user_id=6)
	# print(token.key)
	context = {
		'title': 'Incoming',
		'user_address': user_address,
		'current_year':current_year,
	}
	return render(request, 'requests/incoming.html', context)

def get_file_path(instance, filename):
	ext = filename.split('.')[-1]
	filename_start = filename.replace('.' + ext, '')
	filename = "%s__%s.%s" % (uuid.uuid4(), filename_start, ext)
	return os.path.join('media/CIS', filename)

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@groups_only('Verifier', 'Super Administrator', 'Surveyor', 'Finance', 'Social Worker', 'biller')
def view_incoming(request, pk):
	if request.method == "POST":
		try:
			image_data_url = request.POST.get('image_data_url')
			if image_data_url:
				# Extract the image data from the URL
				_, encoded = image_data_url.split(",", 1)
				# Decode base64 data
				image_data = base64.b64decode(encoded)
				
				# Generate file path using the get_file_path function
				filename = 'image_from_canvas.jpg'  # Example filename
				file_path = get_file_path(None, filename)  # Pass None as instance for now

				# Ensure the directory exists before saving
				os.makedirs(os.path.dirname(file_path), exist_ok=True)

				# Save the image data to a file in the 'CIS' directory within the 'media' directory
				with open(file_path, 'wb') as file:
					file.write(image_data)

				# Construct the database file path
				db_file_path = file_path.replace('media/', '')  # Remove 'media/' prefix

				# Now the image is saved in the 'CIS' directory within the 'media' directory
				client_b_id = Transaction.objects.filter(id=pk).first()
				delete = uploadfile.objects.filter(client_bene_id=client_b_id.client_id).delete()
				insert2 = uploadfile.objects.create(
					file_field1=db_file_path,  # Store the database file path
					client_bene_id=client_b_id.client_id,
				)
				update = TransactionStatus1.objects.filter(transaction_id=pk).update(
					is_upload_photo=1,
					uploader_verifier_id=request.user.id,
					upload_time_end=datetime.now(),
					status=6
				)
				update_transaction = Transaction.objects.filter(id=pk).update(
					status=6
				)
				return JsonResponse({'data': 'success', 'msg': 'You successfully uploaded a picture.'})
			
		except ConnectionError as ce:
			# Handle loss of connection (e.g., log the error)
			handle_error(ce, "CONNECTION ERROR IN CLIENT UPLOADING OF PICTURE", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a problem within your connection, please refresh'})
		except ValidationError as e:
			handle_error(e, "VALIDATION ERROR IN CLIENT UPLOADING OF PICTURE", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
		except IntegrityError as e:
			handle_error(e, "INTEGRITY ERROR IN CLIENT UPLOADING OF PICTURE", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a data inconsistency, please refresh'})
		except RequestException as re:
			# Handle other network-related errors (e.g., log the error)
			handle_error(re, "NETWORK RELATED ISSUE IN CLIENT UPLOADING OF PICTURE", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was a problem with network, please refresh'})
		except Exception as e:
			# Handle other unexpected errors (e.g., log the error)
			handle_error(e, "EXCEPTION ERROR IN CLIENT UPLOADING OF PICTURE", request.user.id)
			return JsonResponse({'error': True, 'msg': 'There was an unexpected error, please refresh'})

	data = Transaction.objects.filter(id=pk).first()
	calculate = transaction_description.objects.filter(tracking_number_id=data.tracking_number).aggregate(total_payment=Sum('total'))
	
	picture = uploadfile.objects.filter(client_bene_id=data.client_id).first()
	context = {
		'transaction': data,
		'pict': picture,
		'family_composistion': ClientBeneficiaryFamilyComposition.objects.filter(clientbene_id=data.bene_id),
		'transaction_status': TransactionStatus1.objects.filter(transaction_id=pk).first(),
		'service_assistance': ServiceAssistance.objects.filter(status=1).order_by('name'),
		'category': Category.objects.filter(status=1).order_by('name'),
		'sub_category': SubCategory.objects.filter(status=1).order_by('name'),
		'type_of_assistance': TypeOfAssistance.objects.filter(status=1).order_by('name'),
		'purpose': Purpose.objects.filter(status=1).order_by('name'),
		'moass': ModeOfAssistance.objects.filter(status=1).order_by('name'),
		'moadm': ModeOfAdmission.objects.filter(status=1).order_by('name'),
		'fund_source': FundSource.objects.filter(status=1).order_by('name'),
		'assistance_type': LibAssistanceType.objects.filter(is_active=1).order_by('type_name'),
		'TypeOfAssistance': TypeOfAssistance.objects.filter(status=1,type_assistance_id=data.lib_type_of_assistance_id).order_by('name'),
		'SubModeofAssistance': SubModeofAssistance.objects.filter(status=1,category_id=data.lib_assistance_category_id).order_by('name'),
		'region_name': region.objects.filter(is_active=1).order_by('region_name'),
		'PriorityLine': PriorityLine.objects.filter(is_active=1).order_by('id'),
		'Problem_Assessment':AssessmentProblemPresented.objects.filter(transaction_id=pk).first(),
		'service_provider': ServiceProvider.objects.filter(status=1),
	}
	return render(request, 'requests/view_incoming.html', context)


@login_required
def trackingModal(request,pk):
	data = Transaction.objects.filter(id=pk).first()
	if request.method == "POST":
		if request.POST.get("client_bene") == "Client":
			Transaction.objects.filter(id=data.id).update(
				client_id = request.POST.get("client_beneficiary")
			)
			return JsonResponse({'data': 'success', 'msg': 'You successfully updated the client'})
		elif request.POST.get("client_bene") == "Beneficiary":
			Transaction.objects.filter(id=data.id).update(
				bene_id = request.POST.get("client_beneficiary")
			)
			return JsonResponse({'data': 'success', 'msg': 'You successfully updated the beneficiary'})
		elif request.POST.get("client_bene") == "swo":
			Transaction.objects.filter(id=data.id).update(
				swo_id = request.POST.get("swo_name")
			)
			return JsonResponse({'data': 'success', 'msg': 'You successfully updated the social worker'})
		elif request.POST.get("relationship") == "relationship":
			Transaction.objects.filter(id=data.id).update(
				relation_id = request.POST.get("relationship_selected")
			)
			return JsonResponse({'data': 'success', 'msg': 'You successfully updated the relationship'})
		
	get_client_history = TransactionStatus1.objects.filter(transaction__client_id=data.client_id).order_by('-id')
	get_beneficiary_history = TransactionStatus1.objects.filter(transaction__bene_id=data.bene_id).order_by('-id')
	verifier = request.user.groups.filter(name__in=['Verifier', 'Super Administrator']).exists()
	context = {
		'transaction_status': TransactionStatus1.objects.filter(transaction_id=data.id).first(), #TRANSACTION STATUS TABLE
		'datas':data, #TRANSACTION TABLE
		'get_client_history': get_client_history, # CLIENT HISTORY
		'get_beneficiary_history': get_beneficiary_history,
		'verifier': verifier,
		'relation': Relation.objects.filter(status=1),
	}
	
	return render(request,'requests/TrackingModal.html', context)


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@groups_only('Social Worker', 'Super Administrator')
def assessment(request):
	transaction_data = TransactionStatus1.objects.filter(Q(status=1) | Q(status=2) | Q(status=3) | Q(status=4), transaction_id__swo_id=request.user.id)
	today_date = date.today()
	modal_show = False  # Set modal_show to False initially
	
	for row in transaction_data:
		row_date = row.verified_time_start.strftime('%Y-%m-%d')
		
		if today_date.strftime('%Y-%m-%d') != row_date:
			modal_show = True  # Set modal_show to True if any transaction has a different date
			break  # Exit the loop as soon as a transaction with a different date is found
	swo_address = AuthuserDetails.objects.filter(user_id=request.user.id).first()
	restriction = request.user.groups.filter(name__in=['Super Administrator']).exists()
	context = {
		'title': 'Assessment',
		'modal_show': modal_show,
		'swo_address':swo_address,
		'restriction':restriction,
	}
	return render(request, 'requests/assessment.html', context)

@csrf_exempt
def submitCaseStudy(request):
	try:
		if request.method == "POST":
			with transaction.atomic():
				if request.POST.get('update_case_study') == "update_case_study":
					Transaction.objects.filter(id=request.POST.get('transaction_id')).update(
						is_case_study=request.POST.get('case_study_update')
					)
					return JsonResponse({'data': 'success', 'msg': 'You successfully updated the category of the study'})
				else:
					TransactionStatus1.objects.filter(transaction_id=request.POST.get('transactionID')).update(
						case_study_status=1,
						case_study_date=request.POST.get('date_submission')
					)
					return JsonResponse({'data': 'success', 'msg': 'You successfully submitted the case study'})
	except ConnectionError as ce:
		# Handle loss of connection (e.g., log the error)
		handle_error(ce, "CONNECTION ERROR IN submitCaseStudy", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a problem within your connection, please refresh'})
	except RequestException as re:
		# Handle other network-related errors (e.g., log the error)
		handle_error(re, "NETWORK RELATED ISSUE IN submitCaseStudy", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a problem with network, please refresh'})
	except Exception as e:
		# Handle other unexpected errors (e.g., log the error)
		handle_error(e, "EXCEPTION ERROR IN submitCaseStudy", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was an unexpected error, please refresh'})

@csrf_exempt
def removeCaseStudy(request):
	try:
		if request.method == "POST":
			with transaction.atomic():
				TransactionStatus1.objects.filter(transaction_id=request.POST.get('id')).update(
					case_study_status=None,
					case_study_date=None
				)
		return JsonResponse({'data': 'success'})
	except ConnectionError as ce:
		# Handle loss of connection (e.g., log the error)
		handle_error(ce, "CONNECTION ERROR IN removeCaseStudy", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a problem within your connection, please refresh'})
	except RequestException as re:
		# Handle other network-related errors (e.g., log the error)
		handle_error(re, "NETWORK RELATED ISSUE IN removeCaseStudy", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a problem with network, please refresh'})
	except Exception as e:
		# Handle other unexpected errors (e.g., log the error)
		handle_error(e, "EXCEPTION ERROR IN removeCaseStudy", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was an unexpected error, please refresh'})

@login_required
def all_transactions(request):
	active_sw = SocialWorker_Status.objects.filter(status=2,date_transaction=today)
	context = {
		'title': 'All Transactions',
		'active_sw': active_sw
	}
	return render(request, 'requests/all_transactions.html', context)

@login_required
def assessmentStatusModal(request,pk):
	if request.method == "POST":
		data = TransactionStatus1.objects.filter(transaction_id=pk).update(
			status=request.POST.get("change_status"),
			status_remarks=request.POST.get("remarks_transaction")
		)
		data = Transaction.objects.filter(id=pk).update(
			status=request.POST.get("change_status")
		)

	transactionStatus = TransactionStatus1.objects.filter(transaction_id=pk).first()
	data = Transaction.objects.filter(id=pk).first()
	context = {
		'TransactionData': data,
		'TransactionStatus': transactionStatus,
	}
	return render(request, "requests/statusModal.html", context)

@csrf_exempt
def remove_family_composition(request):
	if request.method == "POST":
		ClientBeneficiaryFamilyComposition.objects.filter(id=request.POST.get('id')).delete()
	return JsonResponse({'data': 'success'})

@login_required
@groups_only('Social Worker', 'Super Administrator')
def view_assessment(request, pk):
	data = Transaction.objects.filter(id=pk).first()
	try:
		if request.method == "POST":
			with transaction.atomic():
				update_info = request.POST.get('updatin_info')
				if update_info == "update_client":
					client = ClientBeneficiary.objects.filter(unique_id_number=request.POST.get('client_uuid'))
					client.update(
						occupation_id=request.POST.get('occupation_data'),
						salary=request.POST.get('salary'),
					)
					return JsonResponse({'data': 'success','msg': 'Client successfully updated'})
				elif update_info == "update_bene":
					beneficiary = ClientBeneficiary.objects.filter(unique_id_number=request.POST.get('bene_uuid'))
					beneficiary.update(
						occupation_id=request.POST.get('occupation_data'),
						salary=request.POST.get('salary'),
					)
					return JsonResponse({'data': 'success','msg': 'Beneficiary successfully updated'})
				else:
					uuid = data.bene.unique_id_number
					bene_id = data.bene.id
					get_bene_fullname = data.bene.client_bene_fullname
					first_name = request.POST.getlist('first_name[]')
					middle_name = request.POST.getlist('middle_name[]')
					last_name = request.POST.getlist('last_name[]')
					suffix = request.POST.getlist('suffix[]')
					rosterSex = request.POST.getlist('rosterSex[]')
					age = request.POST.getlist('age[]')
					relation = request.POST.getlist('relation[]')
					occupation = request.POST.getlist('occupation[]')
					salary = request.POST.getlist('salary[]')
					if not first_name == [''] and not last_name == [''] and not age == [''] and not occupation == [
						''] and not salary == [''] and not rosterSex == ['']:
						data = [
							{'first_name': fn, 'middle_name': mn, 'last_name': ln, 'suffix': sx, 'age': b, 'occupation': o,
							'salary': s, 'relation': rl, 'rosterSex': rs}
							for fn, mn, ln, sx, b, o, s, rl, rs in
							zip(first_name, middle_name, last_name, suffix, age, occupation, salary, relation, rosterSex)
						]
						family_composition = ClientBeneficiaryFamilyComposition.objects.filter(clientbene__unique_id_number=uuid)
						store = [row.id for row in family_composition]
						if family_composition:
							y = 1
							x = 0
							for row in data:
								if y > len(family_composition):
									ClientBeneficiaryFamilyComposition.objects.create(
										first_name=row['first_name'],
										middle_name=row['middle_name'],
										last_name=row['last_name'],
										suffix_id=row['suffix'],
										sex_id=row['rosterSex'],
										age=row['age'],
										relation_id=row['relation'],
										occupation_id=row['occupation'],
										salary=row['salary'],
										clientbene_id=bene_id
									)
								else:
									ClientBeneficiaryFamilyComposition.objects.filter(id=store[x]).update(
										first_name=row['first_name'],
										middle_name=row['middle_name'],
										last_name=row['last_name'],
										suffix_id=row['suffix'],
										sex_id=row['rosterSex'],
										age=row['age'],
										relation_id=row['relation'],
										occupation_id=row['occupation'],
										salary=row['salary'],
									)
									y += 1
									x += 1
						else:
							for row in data:
								ClientBeneficiaryFamilyComposition.objects.create(
									first_name=row['first_name'],
									middle_name=row['middle_name'],
									last_name=row['last_name'],
									suffix_id=row['suffix'],
									sex_id=row['rosterSex'],
									age=row['age'],
									relation_id=row['relation'],
									occupation_id=row['occupation'],
									salary=row['salary'],
									clientbene_id=bene_id
								)
					else:
						return JsonResponse({'error': True, 'msg': 'You have provided information in Family Composistion. Please fill in or leave the form blank if not applicable. Thank you!'})
					return JsonResponse({'data': 'success','msg': 'Beneficiary family composition with the name: {} has been updated successfully.'.format(get_bene_fullname)})
		
	except ConnectionError as ce:
		# Handle loss of connection (e.g., log the error)
		handle_error(ce, "CONNECTION ERROR IN VIEW ASSESSMENT", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a problem within your connection, please refresh'})
	except ValidationError as e:
		handle_error(e, "VALIDATION ERROR IN VIEW ASSESSMENT", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
	except IntegrityError as e:
		handle_error(e, "INTEGRITY ERROR IN RVIEW ASSESSMENT", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a data inconsistency, please refresh'})
	except RequestException as re:
		# Handle other network-related errors (e.g., log the error)
		handle_error(re, "NETWORK RELATED ISSUE IN VIEW ASSESSMENT", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a problem with network, please refresh'})
	except Exception as e:
		# Handle other unexpected errors (e.g., log the error)
		handle_error(e, "EXCEPTION ERROR IN VIEW ASSESSMENT", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was an unexpected error, please refresh'})

	calculate = transaction_description.objects.filter(tracking_number_id=data.tracking_number).aggregate(total_payment=Sum('total'))
	transactionProvided = transaction_description.objects.filter(tracking_number_id=data.tracking_number).first()
	picture = uploadfile.objects.filter(client_bene_id=data.client_id).first()
	
	context = {
		'transaction': data,
		'today':today,
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
	return render(request, 'requests/view_assessment.html', context)


def StartTime(request,pk):
	try:
		if request.method == "POST":
			data = TransactionStatus1.objects.filter(transaction_id=pk).update(
				swo_time_start=datetime.now(),
				status=2
			)
			data = Transaction.objects.filter(id=pk).update(
				swo_date_time_start=datetime.now(),
				status=2
			)
			return JsonResponse({'data': 'success', 'msg': 'You successfully start the transaction'})
	except ConnectionError as ce:
		# Handle loss of connection (e.g., log the error)
		handle_error(ce, "CONNECTION ERROR IN START TIME", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a problem within your connection, please refresh'})
	except RequestException as re:
		# Handle other network-related errors (e.g., log the error)
		handle_error(re, "NETWORK RELATED ISSUE IN START TIME", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a problem with network, please refresh'})
	except Exception as e:
		# Handle other unexpected errors (e.g., log the error)
		handle_error(e, "EXCEPTION ERROR IN START TIME", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was an unexpected error, please refresh'})

@login_required
def get_assistance_category(request, pk):
	type_of_assistance = TypeOfAssistance.objects.filter(type_assistance_id=pk).values('id', 'name')
	json = []
	for row in type_of_assistance:
		json.append({row['id']: row['name'].title()})
	return JsonResponse(json, safe=False)

@login_required
def get_assistance_sub_category(request, pk):
	category_of_assistance = SubModeofAssistance.objects.filter(category_id=pk).values('id', 'name')
	json = []
	for row in category_of_assistance:
		json.append({row['id']: row['name'].title()})
	return JsonResponse(json, safe=False)

@login_required
@csrf_exempt
def show_assistance_category(request): #DYNAMIC DISPLAY IN SELECT2
	if request.POST.get('src') != "":
		itm = TypeOfAssistance.objects.filter(type_assistance_id=request.POST.get('src'))
		data = [dict(id=row.id, name=row.name) for row in itm]
		return JsonResponse({'data': data})

@login_required
@csrf_exempt
def show_sub_category(request): #DYNAMIC DISPLAY IN SELECT2
	if request.POST.get('src') != "":
		itm = SubModeofAssistance.objects.filter(category_id=request.POST.get('src'))
		data = [dict(id=row.id, name=row.name) for row in itm]
		return JsonResponse({'data': data})


@login_required
@groups_only('Social Worker', 'Super Administrator')
def save_assessment(request, pk):
	try:
		bene_category=""
		bene_sub_category=""
		if request.method == "POST":
			with transaction.atomic():
				date_assessment_str = request.POST.get('date_assessment')
				date_assessment = datetime.strptime(date_assessment_str, '%Y-%m-%dT%H:%M')
				check_client_bene = request.POST.get('checking_if_same')
				if check_client_bene == "same_with_client":
					#CHECKING IF THE CLIENT AND BENEFICIARY ARE THE SAME
					bene_category=request.POST.get('client_category')
					bene_sub_category=request.POST.get('client_subcategory')
				elif check_client_bene == "not_same_with_client":
					bene_category=request.POST.get('beneficiary_category')
					bene_sub_category=request.POST.get('bene_subcategory')
				check = Transaction.objects.filter(id=pk)
				check.update(
					swo_id=request.user.id,
					relation_id=request.POST.get('relationship'),
					priority=request.POST.get('priority_name'),
					client_category_id=request.POST.get('client_category'),
					client_sub_category_id=request.POST.get('client_subcategory'),
					bene_category_id=bene_category,
					bene_sub_category_id=bene_sub_category,
					lib_type_of_assistance_id=request.POST.get('assistance_type'),
					lib_assistance_category_id=request.POST.get('assistance_category'),
					fund_source_id=request.POST.get('fund_source') if request.POST.get('fund_source') else None,
					is_gl=request.POST.get('guarantee_letter') if request.POST.get('guarantee_letter') else 0,
					is_cv=request.POST.get('cash_voucher') if request.POST.get('cash_voucher') else 0,
					is_pcv=request.POST.get('petty_cash') if request.POST.get('petty_cash') else 0,
					is_ce_cash=request.POST.get('ce_cash') if request.POST.get('ce_cash') else 0,
					is_ce_gl=request.POST.get('ce_gl') if request.POST.get('ce_gl') else 0,
					provided_hotmeal=request.POST.get('hot_meals') if request.POST.get('hot_meals') else 0,
					provided_foodpack=request.POST.get('food_packs') if request.POST.get('food_packs') else 0,
					provided_hygienekit=request.POST.get('hygiene_kit') if request.POST.get('hygiene_kit') else 0,
					is_return_new=request.POST.get('new_returning'),
					service_provider=request.POST.get('service_provider'),
					is_referral=1 if request.POST.get('is_referral') else None,
					is_pfa=request.POST.get('pfa') if request.POST.get('pfa') else 0,
					is_swc=request.POST.get('swc') if request.POST.get('swc') else 0
				)
				AssessmentProblemPresented.objects.filter(transaction_id=pk).update(
					sw_assessment=request.POST.get('sw_asessment'),
					problem_presented=request.POST.get('sw_purpose'),
					other_requirements=request.POST.get('other_requirements'),
				)
				Check_exists = TransactionStatus1.objects.filter(transaction_id=pk).first() #THIS QUERY WILL ONLY BE EXECUTED IF THERE'S NOT TIME OF TRANSACTIONSTATUS1
				if Check_exists.swo_time_end == None: # TRANSACTION STATUS IS NOT YET ASSESSED, SAVE THE DETAILS OF ASSESSMENT
					if Check_exists.upload_time_end: # IF TRANSACTION ALREADY HAD AN UPLOADED TIME AND DATE EXECUTE THIS QUERY
						Check_exists.is_swo=1
						Check_exists.swo_time_end=request.POST.get('date_assessment')
						Check_exists.status=6
						Check_exists.end_assessment=date_assessment
						Check_exists.save()
						
						check.update( #
							status=6,
							swo_date_time_end=request.POST.get('date_assessment'),
						)
					else:
						Check_exists.is_swo=1
						Check_exists.swo_time_end=request.POST.get('date_assessment')
						Check_exists.status=3
						Check_exists.end_assessment=date_assessment
						Check_exists.save()

						check.update( #
							status=3,
							swo_date_time_end=request.POST.get('date_assessment'),
						)
				return JsonResponse({'data': 'success',
									'msg': 'You have successfully submitted the assessment for tracking number {}.'.format(check.first().tracking_number)})
		
	except ConnectionError as ce:
		# Handle loss of connection (e.g., log the error)
		handle_error(ce, "CONNECTION ERROR IN SAVE ASSESSMENT", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a problem within your connection, please refresh'})
	except RequestException as re:
		# Handle other network-related errors (e.g., log the error)
		handle_error(re, "NETWORK RELATED ISSUE IN SAVE ASSESSMENT", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a problem with network, please refresh'})
	except Exception as e:
		# Handle other unexpected errors (e.g., log the error)
		handle_error(e, "EXCEPTION ERROR IN SAVE ASSESSMENT", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was an unexpected error, please refresh'})

def modal_provided(request,pk):
	transaction_id = Transaction.objects.filter(id=pk).first()
	tracking_id = transaction_id.tracking_number
	try:
		if request.method == "POST":
			with transaction.atomic():
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
					handle_error(e, "ERROR IN DYNAMIC ENTRY MODAL PROVIDED", request.user.id)
					return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})



	except ConnectionError as ce:
		# Handle loss of connection (e.g., log the error)
		handle_error(ce, "CONNECTION ERROR IN MODAL PROVIDED", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a problem within your connection, please refresh'})
	except RequestException as re:
		# Handle other network-related errors (e.g., log the error)
		handle_error(re, "NETWORK RELATED ISSUE IN MODAL PROVIDED", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a problem with network, please refresh'})
	except Exception as e:
		# Handle other unexpected errors (e.g., log the error)
		handle_error(e, "EXCEPTION ERROR IN MODAL PROVIDED", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was an unexpected error with your input, please review'})

	total_amount = transaction_description.objects.filter(tracking_number_id=transaction_id.tracking_number).aggregate(total_payment=Sum('total'))
	context = {
		'service_provider': ServiceProvider.objects.filter(status=1),
		'transactionProvided': transaction_description.objects.filter(tracking_number=transaction_id.tracking_number),
		'viewProvidedData': transaction_description.objects.filter(tracking_number_id=transaction_id.tracking_number).order_by('-id'),
		'AssistanceProvided': AssistanceProvided.objects.filter(is_active=1),
		'transaction': transaction_id,
		'calculate': total_amount,
		'medicine': medicine.objects.filter(is_active=1),
	}
	return render(request,"requests/modal_provided.html",context)

def confirmAmount(request):
	try:
		if request.method == "POST":
			with transaction.atomic():
				total = request.POST.get('final_total')
				transaction_id = request.POST.get('transaction_id')
				float_value = float(total)
				integer_value = int(float_value)
				areaofassignment = Transaction.objects.filter(id=transaction_id).first()
				Signatories = ""
				if integer_value <= 50000:
					if areaofassignment.requested_in == "AGUSAN DEL NORTE":
						Signatories = 17 #ANA T. SEMACIO
					elif areaofassignment.requested_in == "SURIGAO DEL SUR":
						Signatories = 81 #Arlene M. Ontua
					elif areaofassignment.requested_in == "AGUSAN DEL SUR":
						Signatories = 1 #Michael John ANDOHUYAN
					elif areaofassignment.requested_in == "DINAGAT ISLANDS":
						Signatories = 1 #
					elif areaofassignment.requested_in == "SURIGAO DEL NORTE":
						Signatories = 1 #THESA MUSA
					data = Transaction.objects.filter(id=transaction_id).update(
						signatories_id = Signatories, 
					)
				elif integer_value >= 50001 and integer_value <= 75000:
					data = Transaction.objects.filter(id=transaction_id).update(
						signatories_id = 18, #JESSIE CATHERINE B. ARANAS
					)
				elif integer_value >= 75001 and integer_value <= 100000:
					data = Transaction.objects.filter(id=transaction_id).update(
						signatories_id = 19, #ARDO
					)
				else:
					data = Transaction.objects.filter(id=transaction_id).update(
						signatories_id = 20, #RD
					)
				if integer_value > 10000:
					Transaction.objects.filter(tracking_number=request.POST.get("tracking_number")).update(
						is_case_study=2,
						total_amount=request.POST.get("final_total")
					)
				else:
					Transaction.objects.filter(tracking_number=request.POST.get("tracking_number")).update(
						is_case_study=1,
						total_amount=request.POST.get("final_total")
					)

				return JsonResponse({'data': 'success',
								'msg': 'The total amount {} confirmed.'.format(total)})
	except ConnectionError as ce:
		# Handle loss of connection (e.g., log the error)
		handle_error(ce, "CONNECTION ERROR IN CONFIRM AMOUNT", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a problem within your connection, please refresh'})
	except RequestException as re:
		# Handle other network-related errors (e.g., log the error)
		handle_error(re, "NETWORK RELATED ISSUE IN CONFIRM AMOUNT", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a problem with network, please refresh'})
	except Exception as e:
		# Handle other unexpected errors (e.g., log the error)
		handle_error(e, "EXCEPTION ERROR IN CONFIRM AMOUNT", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was an unexpected error, please refresh'})


@csrf_exempt
def removeTransactionData(request):
	if request.method == "POST":
		with transaction.atomic():
			transaction_id = transaction_description.objects.filter(id=request.POST.get('id')).first()
			Transaction.objects.filter(tracking_number=transaction_id.tracking_number.tracking_number).update(
				total_amount=None
			)
			transaction_description.objects.filter(id=transaction_id.id).delete()
	return JsonResponse({'data': 'success'})

@login_required
@groups_only('Social Worker', 'Super Administrator')
def printGIS(request, pk):
	transaction = Transaction.objects.filter(id=pk).first()
	transaction_data = AssessmentProblemPresented.objects.filter(transaction_id=pk).first()
	transactionStartEnd = TransactionStatus1.objects.filter(transaction_id=pk).first()
	display_family_roster = ClientBeneficiaryFamilyComposition.objects.filter(clientbene_id=transaction.bene_id)[:2]
	display_provided_data = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number)
	calculate = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number).aggregate(total_payment=Sum('total'))
	purpose_assessment = AssessmentProblemPresented.objects.filter(transaction_id=pk).first()
	
	esig = SignatoriesTbl.objects.filter(signatories_id=transaction.signatories, status=1).first()
	context = {
		'data': transaction,
		'roster': display_family_roster,
		'categoryMedical': TypeOfAssistance.objects.filter(type_assistance_id=1,status=1),
		'provided_data': display_provided_data,
		'transactionStartEnd':transactionStartEnd,
		'transaction_data': transaction_data,
		'calculate': calculate,
		'purpose_assessment': purpose_assessment,
		'esignature':esig,
	}
	return render(request,"requests/printGIS.html", context)

@login_required
@groups_only('Social Worker', 'Super Administrator')
def printCEGL(request, pk):
	transaction = Transaction.objects.filter(id=pk).first()
	transactionStartEnd = TransactionStatus1.objects.filter(transaction_id=pk).first()
	display_family_roster = ClientBeneficiaryFamilyComposition.objects.filter(clientbene_id=transaction.bene_id).all()
	display_provided_data = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number)
	calculate = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number).aggregate(total_payment=Sum('total'))
	
	esig = SignatoriesTbl.objects.filter(signatories_id=transaction.signatories, status=1).first()
	purpose_assessment = AssessmentProblemPresented.objects.filter(transaction_id=pk).first()
	context = {
		'data': transaction,
		'roster': display_family_roster,
		'categoryMedical': TypeOfAssistance.objects.filter(type_assistance_id=1,status=1),
		'provided_data': display_provided_data,
		'transactionStartEnd':transactionStartEnd,
		'calculate': calculate,
		'esignature':esig,
		'purpose_assessment':purpose_assessment,
	}
	return render(request,"requests/printCEGL.html", context)

@login_required
@groups_only('Social Worker', 'Super Administrator')
def printCECASH(request, pk):
	transaction = Transaction.objects.filter(id=pk).first()
	transactionStartEnd = TransactionStatus1.objects.filter(transaction_id=pk).first()
	display_family_roster = ClientBeneficiaryFamilyComposition.objects.filter(clientbene_id=transaction.bene_id).all()
	display_provided_data = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number)
	calculate = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number).aggregate(total_payment=Sum('total'))

	esig = SignatoriesTbl.objects.filter(signatories_id=transaction.signatories, status=1).first()
	purpose_assessment = AssessmentProblemPresented.objects.filter(transaction_id=pk).first()
	context = {
		'data': transaction,
		'roster': display_family_roster,
		'categoryMedical': TypeOfAssistance.objects.filter(type_assistance_id=1,status=1),
		'provided_data': display_provided_data,
		'transactionStartEnd':transactionStartEnd,
		'calculate': calculate,
		'esignature':esig,
		'purpose_assessment':purpose_assessment,
	}
	return render(request,"requests/printCECASH.html", context)

@login_required
@groups_only('Social Worker', 'Super Administrator')
def printGL(request, pk):
	import segno
	transaction = Transaction.objects.filter(id=pk).first()
	EndDate = transaction.date_entried.date() + timedelta(days=3)
	display_provider = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number).first() #DISPLAY ONLY SERVICE PROVIDER
	display_provided_data = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number).all()
	calculate = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number).aggregate(total_payment=Sum('total'))
	count = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number).count()
	rows = count + 1

	data = "The Client is {}. and the Benefiary is {} and the Social Worker is {}. The service provider is {} ".format(transaction.client.get_client_fullname,transaction.bene.get_client_fullname,transaction.swo.get_fullname, transaction.service_provider.name)
	qrcode = segno.make_qr(data)
	qrcode.save('./static/staticfiles/qrcode/GL.png', scale=10)

	context = {
		'data': transaction,
		'categoryMedical': TypeOfAssistance.objects.filter(type_assistance_id=1,status=1),
		'provided_data': display_provided_data,
		'display_provider': display_provider,
		'calculate': calculate,
		'validity':EndDate,
		'ct':rows,
	}
	return render(request,"requests/printGL.html", context)

@login_required
@groups_only('Social Worker', 'Super Administrator')
def printGLHead(request, pk):
	transaction = Transaction.objects.filter(id=pk).first()
	transactionStartEnd = TransactionStatus1.objects.filter(transaction_id=pk).first()
	EndDate = transactionStartEnd.verified_time_start.date() + timedelta(days=3)
	display_provider = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number).first() #DISPLAY ONLY SERVICE PROVIDER
	display_provided_data = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number).all()
	calculate = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number).aggregate(total_payment=Sum('total'))
	count = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number).count()
	rows = count + 1

	context = {
		'data': transaction,
		'categoryMedical': TypeOfAssistance.objects.filter(type_assistance_id=1,status=1),
		'provided_data': display_provided_data,
		'display_provider': display_provider,
		'transactionStartEnd':transactionStartEnd,
		'calculate': calculate,
		'validity':EndDate,
		'ct':rows,
	}
	return render(request,"requests/printGLHead.html", context)

@login_required
@groups_only('Social Worker', 'Super Administrator')
def printGLMEDCal(request, pk):
	import segno
	transaction = Transaction.objects.filter(id=pk).first()
	EndDate = transaction.date_entried.date() + timedelta(days=3)
	display_provider = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number).first() #DISPLAY ONLY SERVICE PROVIDER
	display_provided_data = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number).all()
	calculate = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number).aggregate(total_payment=Sum('total'))
	count = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number).count()
	rows = count + 1


	data = "The Client is {}. and the Benefiary is {}. and the Social Worker is {}. The service provider is {}. The Client Category is {}. The Client Sub-Category is {}.".format(transaction.client.get_client_fullname,transaction.bene.get_client_fullname,transaction.swo.get_fullname, transaction.service_provider.name, \
		transaction.client_category.acronym, transaction.client_sub_category.acronym)
	# qrcode = segno.make_qr(data)
	# qrcode.save('./static/staticfiles/qrcode/medical_qr.png', scale=10)


	context = {
		'data': transaction,
		'categoryMedical': TypeOfAssistance.objects.filter(type_assistance_id=1,status=1),
		'provided_data': display_provided_data,
		'display_provider': display_provider,
		'calculate': calculate,
		'validity':EndDate,
		'ct':rows,
		'datas':data,
	}
	return render(request,"requests/printGLMEDCal.html", context)

def printPettyCashVoucher(request, pk): #PettyCashVoucher
	transaction = Transaction.objects.filter(id=pk).first()
	EndDate = transaction.date_entried.date() + timedelta(days=3)
	display_provider = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number).first() #DISPLAY ONLY SERVICE PROVIDER
	display_provided_data = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number).all()
	calculate = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number).aggregate(total_payment=Sum('total'))
	count = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number).count()
	rows = count + 1

	context = {
		'data': transaction,
		'data': transaction,
		'categoryMedical': TypeOfAssistance.objects.filter(type_assistance_id=1,status=1),
		'provided_data': display_provided_data,
		'display_provider': display_provider,
		'calculate': calculate,
		'validity':EndDate,
		'ct':rows,
		'today':today,
	}
	return render(request, "requests/print_pettyCashVoucher.html", context)

def printPagPamatuod(request, pk): #PettyCashVoucher
	transaction = Transaction.objects.filter(id=pk).first()
	EndDate = transaction.date_entried.date() + timedelta(days=3)
	display_provider = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number).first() #DISPLAY ONLY SERVICE PROVIDER
	display_provided_data = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number).all()
	calculate = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number).aggregate(total_payment=Sum('total'))
	count = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number).count()
	rows = count + 1
	
	context = {
		'data': transaction,
		'service_provider': ServiceProvider.objects.filter(category="PHARMACY",status=1)[:17],
		'data': transaction,
		'categoryMedical': TypeOfAssistance.objects.filter(type_assistance_id=1,status=1),
		'provided_data': display_provided_data,
		'display_provider': display_provider,
		'calculate': calculate,
		'validity':EndDate,
		'ct':rows,
		'today':today,
	}
	return render(request, "requests/printPagpamatuod.html", context)

def printingModal(request, pk): #ForPrintingPurposesInAssessment
	data = Transaction.objects.filter(id=pk).first()
	context = {
		'transaction': data,
	}
	return render(request, "requests/printingModal.html", context)

def printQueueing(request, pk):
	data = TransactionStatus1.objects.filter(id=pk).first()
	context ={
		'dataID': data,
	}
	return render(request, "requests/queueungNumber.html", context)

def queueIngDisplay(request):
	active_sw = SocialWorker_Status.objects.filter(status=2,date_transaction=today)
	context = {
		'active_sw': active_sw
	}
	return render(request, "requests/queDisplay.html", context)

def transactions(request):
	return render(request, "Signatories/transactions.html")

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def viewSignatoriesTransactions(request, pk):
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
		'Problem_Assessment':AssessmentProblemPresented.objects.filter(transaction_id=pk).first()
	}
	return render(request, "Signatories/view_signatories.html", context)

@csrf_exempt
def approveTransactions(request):
	if request.method == "POST":
		TransactionStatus1.objects.filter(id=request.POST.get('id')).update(
			signatories_approved=1
		)
	return JsonResponse({'data': 'success'})

@login_required
@groups_only('Social Worker','Verifier', 'Super Administrator', 'Surveyor')
def view_online_swo_data(request):
	search = request.GET.get('search', '')
	page = request.GET.get('page', 1)
	rows = request.GET.get('rows', 10)
	
	# Filter queryset based on search query
	active_sw = SocialWorker_Status.objects.filter(
		Q(user__last_name__icontains=search, status=2, date_transaction=today) |
		Q(user__first_name__icontains=search, status=2, date_transaction=today)
	).order_by('-id')
	
	paginator = Paginator(active_sw, rows)
	active_sw_page = paginator.page(page)
	
	data = []
	for instance in active_sw_page.object_list:
		# total = instance.get_total  # Retrieve the value of the get_total property
		data.append({
			'table': instance.table,
			'user__first_name': instance.user.first_name,
			'user__last_name': instance.user.last_name,
			'pending': instance.get_total,
			'ongoing': instance.get_ongoing,
			'completed': instance.get_complete,
			'case_study': instance.case_study,
		})

	response = JsonResponse(data, safe=False)
	response['X-Pagination-Page'] = active_sw_page.number
	response['X-Pagination-Total-Pages'] = paginator.num_pages
	return response

@login_required
@groups_only('Social Worker','Verifier', 'Super Administrator', 'Surveyor')
def view_online_swo(request):
	context = {
		'user_details': AuthuserDetails.objects.filter(user_id=request.user.id).first(),
	}
	return render(request, 'requests/status_swo.html', context)




