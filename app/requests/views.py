from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.db import transaction
from datetime import timedelta, date, datetime, timedelta, time #DATE TIME
from app.forms import ImageForm
from app.global_variable import groups_only
from app.libraries.models import FileType, Relation, Category, SubCategory, ServiceProvider, ServiceAssistance, \
	TypeOfAssistance, Purpose, ModeOfAssistance, ModeOfAdmission, FundSource, SubModeofAssistance, TypeOfAssistance, \
	SubModeofAssistance, LibAssistanceType, PriorityLine, region, medicine, AssistanceProvided, SignatoriesTbl
from app.requests.models import ClientBeneficiary, ClientBeneficiaryFamilyComposition, \
	 Transaction, TransactionServiceAssistance, Mail, transaction_description, requirements_client, \
	uploadfile, TransactionStatus1, SocialWorker_Status, AssessmentProblemPresented
from django.contrib.sessions.models import Session
from app.models import AuthUser, AuthUserGroups
from django.db.models import Value, Sum, Count
from django.utils import timezone
from django.contrib.auth.models import User
from django.views.decorators.cache import cache_control
import uuid 
import os
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
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@groups_only('Verifier', 'Social Worker', 'Super Administrator')
def requests(request):
	today = date.today()
	active_swo = SocialWorker_Status.objects.all()
	for row in active_swo:
		if row.date_transaction != today:
			SocialWorker_Status.objects.filter(user_id=row.user_id).update(
				status=1 #2 = active, 1 inactive
			)    
	if request.method == "POST":
		check_transaction = TransactionStatus1.objects.filter(transaction_id__client_id=request.POST.get('client'),transaction_id__lib_assistance_category_id=request.POST.get('assistance_category'),status=6).last()
		if check_transaction:
			entriedDate1 = check_transaction.swo_time_end.date()
			threemonths1 = timedelta(3*365/12)
			result1 = (entriedDate1 + threemonths1).isoformat()
			convertedDate = date.fromisoformat(result1)
			present = datetime.now().date()
			dateStr = convertedDate.strftime("%d %b, %Y")
			if present > convertedDate:
				with transaction.atomic():
					lasttrack = Transaction.objects.order_by('-tracking_number').first()
					track_num = generate_serial_string(lasttrack.tracking_number) if lasttrack else \
						generate_serial_string(None, 'AICS')

					data = Transaction(
						tracking_number=track_num,
						relation_id=request.POST.get('relationship'),
						client_id=request.POST.get('client'),
						bene_id=request.POST.get('beneficiary'),
						client_category_id=request.POST.get('clients_category'),
						client_sub_category_id=request.POST.get('clients_subcategory'),
						bene_category_id=request.POST.get('bene_category'),
						bene_sub_category_id=request.POST.get('bene_subcategory'),
						lib_type_of_assistance_id=request.POST.get('assistance_type'),
						lib_assistance_category_id=request.POST.get('assistance_category'),
						date_entried=request.POST.get('date_entried'),
						swo_id=request.POST.get('user'),
						is_case_study=request.POST.get('case_study'),
						priority_id=request.POST.get('priority_name'),
						is_return_new=request.POST.get('status'), 
						is_onsite_offsite=request.POST.get('site'),
						is_online=request.POST.get('online') if request.POST.get('online') else None,
						is_walkin=request.POST.get('walkin') if request.POST.get('walkin') else None,
						is_referral=request.POST.get('referral') if request.POST.get('referral') else None,
						is_gl=request.POST.get('guarantee_letter') if request.POST.get('guarantee_letter') else 0,
						is_cv=request.POST.get('cash_voucher') if request.POST.get('cash_voucher') else 0,
						is_pcv=request.POST.get('petty_cash') if request.POST.get('petty_cash') else 0,
						is_ce_cash=request.POST.get('ce_cash') if request.POST.get('ce_cash') else 0,
						is_ce_gl=request.POST.get('ce_gl') if request.POST.get('ce_gl') else 0,
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
						status="1"
					)
					return JsonResponse({'data': 'success', 'msg': 'New requests has been created. Please wait for the reviewal of your requests and copy the generated reference number.',
										'tracking_number': track_num})
			else:
				return JsonResponse({'error': True,
                                         'msg': 'The assistance you get is not yet available, please wait for another 3 months DATE: ' + dateStr + ' Thank you!'})

		else:
			with transaction.atomic():
				lasttrack = Transaction.objects.order_by('-tracking_number').first()
				track_num = generate_serial_string(lasttrack.tracking_number) if lasttrack else \
					generate_serial_string(None, 'AICS')

				data = Transaction(
					tracking_number=track_num,
					relation_id=request.POST.get('relationship'),
					client_id=request.POST.get('client'),
					bene_id=request.POST.get('beneficiary'),
					client_category_id=request.POST.get('clients_category'),
					client_sub_category_id=request.POST.get('clients_subcategory'),
					bene_category_id=request.POST.get('bene_category'),
					bene_sub_category_id=request.POST.get('bene_subcategory'),
					lib_type_of_assistance_id=request.POST.get('assistance_type'),
					lib_assistance_category_id=request.POST.get('assistance_category'),
					date_entried=request.POST.get('date_entried'),
					swo_id=request.POST.get('user'),
					is_case_study=request.POST.get('case_study'),
					priority_id=request.POST.get('priority_name'),
					is_return_new=request.POST.get('status'), 
					is_onsite_offsite=request.POST.get('site'),
					is_online=request.POST.get('online') if request.POST.get('online') else None,
					is_walkin=request.POST.get('walkin') if request.POST.get('walkin') else None,
					is_referral=request.POST.get('referral') if request.POST.get('referral') else None,
					is_gl=request.POST.get('guarantee_letter') if request.POST.get('guarantee_letter') else 0,
					is_cv=request.POST.get('cash_voucher') if request.POST.get('cash_voucher') else 0,
					is_pcv=request.POST.get('petty_cash') if request.POST.get('petty_cash') else 0,
					is_ce_cash=request.POST.get('ce_cash') if request.POST.get('ce_cash') else 0,
					is_ce_gl=request.POST.get('ce_gl') if request.POST.get('ce_gl') else 0,
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
					status="1"
				)
				return JsonResponse({'data': 'success', 'msg': 'New requests has been created. Please wait for the reviewal of your requests and copy the generated reference number.',
									'tracking_number': track_num})

	active_sw = SocialWorker_Status.objects.filter(status=2,date_transaction=today)

	context = {
		'title': 'New Requests',
		'file_type': FileType.objects.filter(status=1, is_required=1),
		'relation': Relation.objects.filter(status=1),
		'category': Category.objects.filter(status=1),
		'sub_category': SubCategory.objects.filter(status=1),
		'service_provider': ServiceProvider.objects.filter(status=1),
		'type_of_assistance': TypeOfAssistance.objects.filter(status=1),
		'sub_category_assistsance': SubModeofAssistance.objects.filter(status=1),
		'assistance_type': LibAssistanceType.objects.filter(is_active=1).order_by('type_name'),
		'PriorityLine': PriorityLine.objects.filter(is_active=1).order_by('id'),
		'active_swo':active_sw,
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
							TransactionStatus1.objects.filter(transaction_id__client_id=pk,status=6).order_by('-id')]

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
@groups_only('Verifier', 'Super Administrator', 'Surveyor')
def incoming(request):
	context = {
		'title': 'Incoming'
	}
	return render(request, 'requests/incoming.html', context)



@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@groups_only('Verifier', 'Super Administrator', 'Surveyor')
def view_incoming(request, pk):
	if request.method == "POST":
		client_b_id = Transaction.objects.filter(id=pk).first()
		delete = uploadfile.objects.filter(client_bene_id=client_b_id.client_id).delete()
		split_tup = os.path.splitext(str(request.FILES.get('file')))
		file_extension = split_tup[1]
		if file_extension == ".jpg" or file_extension == ".jpeg" or file_extension == ".png":
			insert2 = uploadfile.objects.create(
				file_field1=request.FILES.get('file'),
				client_bene_id=client_b_id.client_id,
				)
			update = TransactionStatus1.objects.filter(id=pk).update(
				is_upload_photo=1,
				uploader_verifier_id=request.user.id,
				upload_time_end=datetime.now(),
				status=6
			)
			return JsonResponse({'data': 'success', 'msg': 'You successfully uploaded a picture.'})
		else:
			return JsonResponse({'error': True, 'msg': "File Type is not Valid"})

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
		'calculate':calculate,
		'PriorityLine': PriorityLine.objects.filter(is_active=1).order_by('id'),
		'Problem_Assessment':AssessmentProblemPresented.objects.filter(transaction_id=pk).first()

	}
	return render(request, 'requests/view_incoming.html', context)


@login_required
def trackingModal(request,pk):
	context = {
		'transaction_status': TransactionStatus1.objects.filter(transaction_id=pk).first()
	}
	
	return render(request,'requests/TrackingModal.html', context)


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@groups_only('Social Worker', 'Super Administrator')
def assessment(request):
	context = {
		'title': 'Assessment'
	}
	return render(request, 'requests/assessment.html', context)

@login_required
def assessmentStatusModal(request,pk):
	if request.method == "POST":
		data = TransactionStatus1.objects.filter(transaction_id=pk).update(
			status=request.POST.get("change_status"),
			status_remarks=request.POST.get("remarks_transaction")
		)
		status = request.POST.get("change_status")
		if status == "2":
			data = "Assess"
			# return JsonResponse({'data': 'success', 'msg': 'The transaction can now be {}'.format(data)})
		elif status == "4":
			data = "On-hold"
			# return JsonResponse({'data': 'success', 'msg': 'The transaction is now {}'.format(data)})
		else:
			data = "Cancelled"
			# return JsonResponse({'data': 'success', 'msg': 'The transaction is {}'.format(data)})

	transactionStatus = TransactionStatus1.objects.filter(transaction_id=pk).first()
	data = Transaction.objects.filter(id=pk).first()
	context = {
		'TransactionData': data,
		'TransactionStatus': transactionStatus,
	}
	return render(request, "requests/statusModal.html", context)

@login_required
@groups_only('Social Worker', 'Super Administrator')
def view_assessment(request, pk):

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
	return render(request, 'requests/view_assessment.html', context)


def StartTime(request,pk):
	if request.method == "POST":
		data = TransactionStatus1.objects.filter(transaction_id=pk).update(
			swo_time_start=datetime.now(),
			status=2
		)
		return JsonResponse({'data': 'success', 'msg': 'You successfully start the transaction'})

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
	if request.method == "POST":
		with transaction.atomic():
			print("TEST", request.POST.get('case_study'))
			check = Transaction.objects.filter(id=pk)
			check.update(
				swo_id=request.user.id,
				priority=request.POST.get('priority_name'),
				is_case_study=request.POST.get('case_study'),
				client_category_id=request.POST.get('client_category'),
				client_sub_category_id=request.POST.get('client_subcategory'),
				bene_category_id=request.POST.get('beneficiary_category'),
				bene_sub_category_id=request.POST.get('bene_subcategory'),
				lib_type_of_assistance_id=request.POST.get('assistance_type'),
				lib_assistance_category_id=request.POST.get('assistance_category'),

				fund_source_id=request.POST.get('fund_source'),
				is_gl=request.POST.get('guarantee_letter') if request.POST.get('guarantee_letter') else 0,
				is_cv=request.POST.get('cash_voucher') if request.POST.get('cash_voucher') else 0,
				is_pcv=request.POST.get('petty_cash') if request.POST.get('petty_cash') else 0,
				is_ce_cash=request.POST.get('ce_cash') if request.POST.get('ce_cash') else 0,
				is_ce_gl=request.POST.get('ce_gl') if request.POST.get('ce_gl') else 0,
				provided_hotmeal = request.POST.get('hot_meals') if request.POST.get('hot_meals') else 0,
				provided_foodpack = request.POST.get('food_packs') if request.POST.get('food_packs') else 0,
				provided_hygienekit = request.POST.get('hygiene_kit') if request.POST.get('hygiene_kit') else 0,
			)
			AssessmentProblemPresented.objects.filter(transaction_id=pk).update(
				sw_assessment=request.POST.get('sw_asessment'),
			)
			Check_exists = TransactionStatus1.objects.filter(transaction_id=pk).first()
			if Check_exists.swo_time_end == None:
				TransactionStatus1.objects.filter(transaction_id=pk).update(
					is_swo="1",
					swo_time_end=datetime.now(),
					status="3",
					end_assessment=today
				)
			else:
				TransactionStatus1.objects.filter(transaction_id=pk).update(
					is_swo="1",
					end_assessment=today,
					status="3",
				)
			return JsonResponse({'data': 'success',
								 'msg': 'You have successfully submitted the assessment for tracking number {}.'.format(check.first().tracking_number)})
		return JsonResponse({'error': True, 'msg': 'Internal Error. An uncaught exception was raised.'})


def modal_provided(request,pk):
	transaction_id = Transaction.objects.filter(id=pk).first()
	if request.method == "POST":
		with transaction.atomic():
			check = Transaction.objects.filter(id=pk)
			transaction_description.objects.create(
				tracking_number_id=transaction_id.tracking_number,
				provided_data=request.POST.get('provided'),
				regular_price=request.POST.get('regprice'),
				regular_quantity=request.POST.get('qty'),
				discount_price=request.POST.get('dsc'),
				discount_quantity=request.POST.get('qty1'),
				total=request.POST.get('tot'),
				user_id=request.user.id,
			)
			provider = Transaction.objects.filter(id=pk)

			if transaction_id.service_provider is None:
				provider.update(
					service_provider_id=request.POST.get('service_provider'),
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
	}
	return render(request,"requests/modal_provided.html",context)

def confirmAmount(request):
	if request.method == "POST":
		total = request.POST.get('final_total')
		transaction_id = request.POST.get('transaction_id')
		float_value = float(total)
		integer_value = int(float_value)

		#client = Transaction.objects.filter(id=transaction_id).first()
		#print(client.client.barangay.city_code.prov_code.id)
		#print(client.client.barangay.city_code.prov_code.prov_name)
		#78 ADN
		#79 ADS
		#80 SDN
		#81 SDS
		#82 DINAGAT

		if integer_value <= 5000:
			data = Transaction.objects.filter(id=transaction_id).update(
				signatories_id = 17, #ANA T. SEMACIO
			)
		elif integer_value >= 5001 and integer_value <= 75000:
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
		return JsonResponse({'data': 'success',
						'msg': 'The total amount {} confirmed.'.format(total)})


@csrf_exempt
def removeTransactionData(request):
	if request.method == "POST":
		transaction_description.objects.filter(id=request.POST.get('id')).delete()
	return JsonResponse({'data': 'success'})

@login_required
@groups_only('Social Worker', 'Super Administrator')
def printGIS(request, pk):
	transaction = Transaction.objects.filter(id=pk).first()
	transaction_data = AssessmentProblemPresented.objects.filter(transaction_id=pk).first()
	transactionStartEnd = TransactionStatus1.objects.filter(transaction_id=pk).first()
	display_family_roster = ClientBeneficiaryFamilyComposition.objects.filter(clientbene_id=transaction.bene_id).all()
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
	context = {
		'data': transaction,
		'roster': display_family_roster,
		'categoryMedical': TypeOfAssistance.objects.filter(type_assistance_id=1,status=1),
		'provided_data': display_provided_data,
		'transactionStartEnd':transactionStartEnd,
		'calculate': calculate,
		'esignature':esig,
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
	context = {
		'data': transaction,
		'roster': display_family_roster,
		'categoryMedical': TypeOfAssistance.objects.filter(type_assistance_id=1,status=1),
		'provided_data': display_provided_data,
		'transactionStartEnd':transactionStartEnd,
		'calculate': calculate,
		'esignature':esig,
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
	print("TEST",data)
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
	EndDate = transaction.date_entried.date() + timedelta(days=3)
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
	# sample = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number).values('tracking_number').aggregate(total=Sum('total'))
	# sample = transaction_description.objects.all().filter(tracking_number_id=transaction.tracking_number).values('tracking_number').annotate(total=Count('tracking_number'))
	count = transaction_description.objects.filter(tracking_number_id=transaction.tracking_number).count()
	rows = count + 1


	data = "The Client is {}. and the Benefiary is {}. and the Social Worker is {}. The service provider is {}. The Client Category is {}. The Client Sub-Category is {}.".format(transaction.client.get_client_fullname,transaction.bene.get_client_fullname,transaction.swo.get_fullname, transaction.service_provider.name, \
		transaction.client_category.acronym, transaction.client_sub_category.acronym)
	print(data)
	qrcode = segno.make_qr(data)
	qrcode.save('./static/staticfiles/qrcode/medical_qr.png', scale=10)


	context = {
		'data': transaction,
		'categoryMedical': TypeOfAssistance.objects.filter(type_assistance_id=1,status=1),
		'provided_data': display_provided_data,
		'display_provider': display_provider,
		'calculate': calculate,
		'validity':EndDate,
		'ct':rows,
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