import uuid
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from datetime import timedelta, date, datetime
from app.global_variable import groups_only
from app.libraries.models import Suffix, Sex, CivilStatus, Province, Tribe, region, occupation_tbl, Relation, presented_id
from app.requests.models import ClientBeneficiaryFamilyComposition, ClientBeneficiary, Transaction, uploadfile, TransactionStatus1, SocialWorker_Status, \
	FileType,Category,SubCategory,ServiceProvider,TypeOfAssistance,SubModeofAssistance,LibAssistanceType,PriorityLine, ErrorLogData, ClientBeneficiaryUpdateHistory
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from requests.exceptions import RequestException

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
@groups_only('Verifier', 'Service Provider','Social Worker', 'Super Administrator')
def client_beneficiary(request):
	context = {
		'title': 'Client / Beneficiary',
	}
	return render(request, 'client_bene/client_beneficiary.html', context)

@csrf_exempt
def activate_client(request):
	if request.method == "POST":
		ClientBeneficiary.objects.filter(id=request.POST.get('id')).update(
			is_validated=True,
		)
	return JsonResponse({'data': 'success'})


@csrf_exempt
def deactivate_client(request):
	if request.method == "POST":
		ClientBeneficiary.objects.filter(id=request.POST.get('id')).update(
			is_validated=False,
		)
	return JsonResponse({'data': 'success'})

@login_required
@groups_only('Verifier', 'Service Provider', 'Social Worker', 'Super Administrator')
def view_client_bene_info(request, pk):
	updated_client = ClientBeneficiary.objects.get(unique_id_number=pk)
	if request.method == "POST":
		if request.POST.get('suffix'):
			suffix = Suffix.objects.filter(id=request.POST.get('suffix')).first()
			if request.POST.get('middle_name'):
				middle_name = request.POST.get('middle_name')
				middle_initial = middle_name[0].upper()
				client_bene_fullname = request.POST.get('first_name') + " " + middle_initial + ". " + request.POST.get('last_name') + ", " + suffix.name
			else:
				client_bene_fullname = request.POST.get('first_name') + " " + request.POST.get('last_name') + ", " + suffix.name
		else:
			if request.POST.get('middle_name'):
				middle_name = request.POST.get('middle_name')
				middle_initial = middle_name[0].upper()
				client_bene_fullname = request.POST.get('first_name') + " " + middle_initial + ". " + request.POST.get('last_name')
			else:
				client_bene_fullname = request.POST.get('first_name') + " " + request.POST.get('last_name')

		if updated_client.client_bene_fullname != client_bene_fullname:
			ClientBeneficiaryUpdateHistory.objects.create(
				unique_id_number_id=pk,
				last_name=updated_client.last_name,
				first_name=updated_client.first_name,
				middle_name=updated_client.middle_name,
				suffix_id=updated_client.suffix_id,
				updated_by_id=request.user.id
			)

		client = ClientBeneficiary.objects.filter(unique_id_number=pk)
		client.update(
			last_name=request.POST.get('last_name'),
			first_name=request.POST.get('first_name'),
			middle_name=request.POST.get('middle_name'),
			suffix_id=request.POST.get('suffix'),
			birthdate=request.POST.get('birthdate'),
			sex_id=request.POST.get('sex'),
			contact_number=request.POST.get('contact_number'),
			civil_status_id=request.POST.get('civil_status'),
			is_indi=True if request.POST.get('indi') == "1" else False,
			tribu_id=request.POST.get('tribe'),
			barangay_id=request.POST.get('barangay'),
			street=request.POST.get('street'),
			house_no=request.POST.get('house_no'),
			village=request.POST.get('village'),
			is_4ps=True if request.POST.get('4ps_member') == "1" else False,
			number_4ps_id_number=request.POST.get('4ps_id_number'),
			updated_by_id=request.user.id,
			is_validated=True,
			registered_by_id=request.user.id,
			occupation_id=request.POST.get('occupation_data'),
			salary=request.POST.get('salary'),
			presented=request.POST.get('IDPresented'),
			presented_id_no=request.POST.get('IDPNo'),
			client_bene_fullname=client_bene_fullname
		)
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
			family_composition = ClientBeneficiaryFamilyComposition.objects.filter(clientbene__unique_id_number=pk)
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
							clientbene_id=client.first().id
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
						clientbene_id=client.first().id
					)
		else:
			return JsonResponse({'error': True, 'msg': 'You have provided information in Family Composistion. Please fill in or leave the form blank if not applicable. Thank you!'})
		return JsonResponse({'data': 'success','msg': 'A client / beneficiary with ID Number: {} has been updated successfully.'.format(pk)})
	
	picture = uploadfile.objects.filter(client_bene_id=updated_client.id).first()
	context = {
		'pict':picture,
		'information': ClientBeneficiary.objects.filter(unique_id_number=pk).first(),
		'family_composistion': ClientBeneficiaryFamilyComposition.objects.filter(clientbene__unique_id_number=pk),
		'suffix': Suffix.objects.filter(status=1).order_by('name'),
		'sex': Sex.objects.filter(status=1).order_by('name'),
		'tribe': Tribe.objects.filter(status=1).order_by('name'),
		'civil_status': CivilStatus.objects.filter(status=1).order_by('name'),
		'region_name': region.objects.filter(is_active=1).order_by('region_name'),
		'occupation': occupation_tbl.objects.filter(is_active=1).order_by('id'),
		'Relation': Relation.objects.filter(status=1),
		'Presented': presented_id.objects.all(),
		'client_history': ClientBeneficiaryUpdateHistory.objects.filter(unique_id_number=pk)
	}
	return render(request, 'client_bene/view_information.html', context)

@login_required
def registration(request):
	try:
		if request.method == "POST":
			with transaction.atomic():
				check_if_name_exists = ClientBeneficiary.objects.filter(
					Q(last_name__icontains=request.POST.get('last_name')) &
					Q(first_name__icontains=request.POST.get('first_name')) &
					Q(middle_name__icontains=request.POST.get('middle_name')) &
					Q(suffix_id=request.POST.get('suffix') if request.POST.get('suffix') else None) &
					Q(birthdate=request.POST.get('birthdate')))
				if not check_if_name_exists:
					if request.POST.get('suffix'):
						suffix = Suffix.objects.filter(id=request.POST.get('suffix')).first()
						if request.POST.get('middle_name'):
							middle_name = request.POST.get('middle_name')
							middle_initial = middle_name[0].upper()
							client_bene_fullname = request.POST.get('first_name') + " " + middle_initial + ". " + request.POST.get('last_name') + ", " + suffix.name
						else:
							client_bene_fullname = request.POST.get('first_name') + " " + request.POST.get('last_name') + ", " + suffix.name
					else:
						if request.POST.get('middle_name'):
							middle_name = request.POST.get('middle_name')
							middle_initial = middle_name[0].upper()
							client_bene_fullname = request.POST.get('first_name') + " " + middle_initial + ". " + request.POST.get('last_name')
						else:
							client_bene_fullname = request.POST.get('first_name') + " " + request.POST.get('last_name')
							
					unique_id = uuid.uuid4()
					clientbene = ClientBeneficiary(
						last_name=request.POST.get('last_name'),
						first_name=request.POST.get('first_name'),
						middle_name=request.POST.get('middle_name'),
						suffix_id=request.POST.get('suffix'),
						birthdate=request.POST.get('birthdate'),
						age=request.POST.get('calculated_age'),
						sex_id=request.POST.get('sex'),
						contact_number=request.POST.get('contact_number') if request.POST.get('contact_number') else None,
						civil_status_id=request.POST.get('civil_status'),
						is_indi=True if request.POST.get('indi') == "1" else False,
						tribu_id=request.POST.get('tribe'),
						barangay_id=request.POST.get('barangay'),
						street=request.POST.get('street') if request.POST.get('street') else None,
						house_no=request.POST.get('house_no') if request.POST.get('house_no') else None,
						village=request.POST.get('village') if request.POST.get('street') else None,
						is_4ps=True if request.POST.get('4ps_member') == "1" else False,
						number_4ps_id_number=request.POST.get('4ps_id_number'),
						unique_id_number=str(unique_id).upper(),
						updated_by_id=request.user.id,
						is_validated=True,
						registered_by_id=request.user.id,
						occupation_id=request.POST.get('occupation_data'),
						salary=request.POST.get('salary'),
						presented_id=request.POST.get('id_presented'),
						presented_id_no=request.POST.get('presented_id_no'),
						client_bene_fullname=client_bene_fullname
					)

					clientbene.save()

					first_name = request.POST.getlist('first_name[]')
					middle_name = request.POST.getlist('middle_name[]')
					last_name = request.POST.getlist('last_name[]')
					suffix = request.POST.getlist('suffix[]')
					birthdate = request.POST.getlist('birthdate[]')
					occupation = request.POST.getlist('occupation[]')
					salary = request.POST.getlist('salary[]')
					relation = request.POST.getlist('relation[]')
					rosterSex = request.POST.getlist('rosterSex[]')

					if not first_name == [''] and not last_name == [''] and not birthdate == [''] and not occupation == [
						''] and not salary == [''] and not relation == [''] and not rosterSex == ['']:
						data = [
							{'first_name': fn, 'middle_name': mn, 'last_name': ln, 'suffix': sx, 'birthdate': b,
							'occupation': o, 'salary': s, 'relation': rl, 'rosterSex': rs}
							for fn, mn, ln, sx, b, o, s, rl, rs in
							zip(first_name, middle_name, last_name, suffix, birthdate, occupation, salary, relation, rosterSex)
						]

						for row in data:
							ClientBeneficiaryFamilyComposition.objects.create(
								first_name=row['first_name'],
								middle_name=row['middle_name'],
								last_name=row['last_name'],
								suffix_id=row['suffix'],
								sex_id=row['rosterSex'],
								birthdate=row['birthdate'],
								relation_id=row['relation'],
								occupation_id=row['occupation'],
								salary=row['salary'],
								clientbene_id=clientbene.id
							)
					else:
						return JsonResponse({'error': True,
											'msg': 'You have provided information in Family Composistion. Please fill in or leave the form blank if not applicable. Thank you!'})
					return JsonResponse({'data': 'success',
										'msg': 'You have successfully registered a client / beneficiary. You can now proceed to make a new request for assistance.'})
				else:
					return JsonResponse({'error': True, 'msg': 'A client or beneficiary with this name already exists.'})
			return JsonResponse({'error': True, 'msg': 'Internal Error. An uncaught exception was raised.'})
	
	except ConnectionError as ce:
		handle_error(ce, "CONNECTION ERROR IN REGISTRATION PAGE", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a problem within your connection, please refresh'})
	except ValidationError as e:
		handle_error(e, "VALIDATION ERROR IN REGISTRATION TRANSACTION", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a data validation error, please refresh'})
	except IntegrityError as e:
		handle_error(e, "INTEGRITY ERROR IN REGISTRATION TRANSACTION", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a data inconsistency, please refresh'})
	except RequestException as re:
		handle_error(re, "NETWORK NETWORK ERROR IN REGISTRATION PAGE", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was a problem with network, please refresh'})
	except Exception as e:
		handle_error(e, "EXCEPTION ERROR IN REGISTRATION PAGE", request.user.id)
		return JsonResponse({'error': True, 'msg': 'There was an unexpected error, please refresh'})

	context = {
		'title': 'Client / Beneficiary Registration',
		'suffix': Suffix.objects.filter(status=1).order_by('name'),
		'sex': Sex.objects.filter(status=1).order_by('name'),
		'tribe': Tribe.objects.filter(status=1).order_by('name'),
		'civil_status': CivilStatus.objects.filter(status=1).order_by('name'),
		'province': Province.objects.filter(is_active=1).order_by('prov_name'),
		'region': region.objects.filter(is_active=1).order_by('region_name'),
		'occupation': occupation_tbl.objects.filter(is_active=1).order_by('id'),
		'Relation': Relation.objects.filter(status=1),
		'presented_id':presented_id.objects.all(),
	}
	return render(request, 'client_bene/registration.html', context)

def modal_transaction(request,pk):
	transactionClientSide = TransactionStatus1.objects.filter(transaction_id__client_id=pk).order_by('-id')
	transactionBeneside = TransactionStatus1.objects.filter(transaction_id__bene_id=pk).order_by('-id')

	picture = uploadfile.objects.filter(client_bene_id=pk).first()
	data = ClientBeneficiary.objects.filter(id=pk).first()
	context = {
		'transactionClientData':transactionClientSide,
		'transactionBeneData':transactionBeneside,
		# 'clientNextTransaction':result1,
		# 'beneNextTransaction':result2,
		'pict':picture,
		'transaction':data,
	}
	return render(request,'client_bene/transaction_modal.html', context)

def Modal_DirectRequest(request,pk):
	today = date.today()
	active_swo = SocialWorker_Status.objects.all()
	for row in active_swo:
		if row.date_transaction != today:
			checking = SocialWorker_Status.objects.filter(user_id=row.user_id).update(
				status=1 #asofnow2pa, 1means logout
			)    
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
		'client_id':ClientBeneficiary.objects.filter(id=pk).first()
	}
	return render(request,'client_bene/direct_request.html',context)



def InsertDirectRequests(request):
	if request.method == "POST":
		with transaction.atomic():
			lasttrack = Transaction.objects.order_by('-tracking_number').first()
			track_num = generate_serial_string(lasttrack.tracking_number) if lasttrack else \
				generate_serial_string(None, 'AICS')
			if request.POST.get('same_with_client'):
				data = Transaction(
					tracking_number=track_num,
					relation_id=request.POST.get('relationship'),
					client_id=request.POST.get('client_bene_same'),
					client_category_id=request.POST.get('clients_category'),
					client_sub_category_id=request.POST.get('clients_subcategory'),
					bene_id=request.POST.get('client_bene_same'),
					bene_category_id=request.POST.get('bene_category'),
					bene_sub_category_id=request.POST.get('bene_subcategory'),
					problem_presented=request.POST.get('problem'),
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

				TransactionStatus1.objects.create(
					transaction_id=data.id,
					verified_time_start=data.date_entried,
					is_verified = "1",
					verifier_id=request.user.id,
					verified_time_end=data.date_entried,
					status="1"
				)
				
				return JsonResponse({'data': 'success', 'msg': 'New requests has been created. Please wait for the reviewal of your requests and copy the generated reference number.',
									'tracking_number': track_num})   
			else:
				data = Transaction(
					tracking_number=track_num,
					relation_id=request.POST.get('relationship'),
					client_id=request.POST.get('client_bene_same'),
					client_category_id=request.POST.get('clients_category'),
					client_sub_category_id=request.POST.get('clients_subcategory'),
					bene_id=request.POST.get('beneficiary'),
					bene_category_id=request.POST.get('bene_category'),
					bene_sub_category_id=request.POST.get('bene_subcategory'),
					problem_presented=request.POST.get('problem'),
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

				TransactionStatus1.objects.create(
					transaction_id=data.id,
					verified_time_start=data.date_entried,
					is_verified = "1",
					verifier_id=request.user.id,
					verified_time_end=data.date_entried,
					status="1"
				)
				return JsonResponse({'data': 'success', 'msg': 'New requests has been created. Please wait for the reviewal of your requests and copy the generated reference number.',
					'tracking_number': track_num})  


def filter_search(request):
	search = request.GET.get('search','')
	if request.GET.get('search'):
		print(search)
