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
	uploadfile, TransactionStatus1, SocialWorker_Status, AssessmentProblemPresented
from app.libraries.models import Suffix, Sex, CivilStatus, Province, Tribe, region, occupation_tbl, Relation, presented_id
from django.contrib.sessions.models import Session
from app.models import AuthUser, AuthUserGroups
from django.db.models import Value, Sum, Count
from datetime import datetime, timedelta, time, date
from django.utils import timezone
from django.contrib.auth.models import User
# import qrcode
import uuid 
import os
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
def registrationOnline(request):
	if request.method == "POST":
		if request.POST.get('unique_idnumber') =="":
			with transaction.atomic():
				if request.POST.get('suffix'):
					suffix = Suffix.objects.filter(id=request.POST.get('suffix')).first()
					if request.POST.get('middle_name'):
						middle_name = request.POST.get('middle_name')
						middle_initial = middle_name[0].upper()
						client_bene_fullname = request.POST.get('first_name') + " " + middle_initial + ". " + request.POST.get('last_name') + ", " + suffix.name
					else:
						client_bene_fullname = request.POST.get('first_name') + " " + request.POST.get('last_name') + " " + suffix.name
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
					sex_id=request.POST.get('sex'),
					contact_number=request.POST.get('contact_number'),
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
					user_data_id=request.user.id,
					client_bene_fullname=client_bene_fullname,
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
					client_bene_fullname = request.POST.get('first_name') + " " + middle_initial + ". " + request.POST.get('last_name')
				else:
					client_bene_fullname = request.POST.get('first_name') + " " + request.POST.get('last_name')
					
			client = ClientBeneficiary.objects.filter(unique_id_number=request.POST.get('unique_idnumber'))
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
					presented_id=request.POST.get('id_presented'),
					presented_id_no=request.POST.get('presented_id_no'),
					client_bene_fullname=client_bene_fullname,
				)
			first_name = request.POST.getlist('first_name[]')
			middle_name = request.POST.getlist('middle_name[]')
			last_name = request.POST.getlist('last_name[]')
			suffix = request.POST.getlist('suffix[]')
			rosterSex = request.POST.getlist('rosterSex[]')
			birthdate = request.POST.getlist('birthdate[]')
			relation = request.POST.getlist('relation[]')
			occupation = request.POST.getlist('occupation[]')
			salary = request.POST.getlist('salary[]')

			if not first_name == [''] and not last_name == [''] and not birthdate == [''] and not occupation == [
				''] and not salary == [''] and not rosterSex == ['']:
				data = [
					{'first_name': fn, 'middle_name': mn, 'last_name': ln, 'suffix': sx, 'birthdate': b, 'occupation': o,
					'salary': s, 'relation': rl, 'rosterSex': rs}
					for fn, mn, ln, sx, b, o, s, rl, rs in
					zip(first_name, middle_name, last_name, suffix, birthdate, occupation, salary, relation, rosterSex)
				]
				family_composition = ClientBeneficiaryFamilyComposition.objects.filter(clientbene__unique_id_number=request.POST.get('unique_idnumber'))
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
								birthdate=row['birthdate'],
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
								birthdate=row['birthdate'],
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
							birthdate=row['birthdate'],
							relation_id=row['relation'],
							occupation_id=row['occupation'],
							salary=row['salary'],
							clientbene_id=request.user.id
						)
			else:
				return JsonResponse({'error': True, 'msg': 'You have provided information in Family Composistion. Please fill in or leave the form blank if not applicable. Thank you!'})
			return JsonResponse({'data': 'success','msg': 'You successfully updated your information'})

	data_uuid = ClientBeneficiary.objects.filter(user_data_id=request.user.id).first()
	if data_uuid:
		data=data_uuid.unique_id_number
		title='Online Registration'
	else:
		data=0
		title='Admin'
	context = {
		'title': title,
		'suffix': Suffix.objects.filter(status=1).order_by('name'),
		'sex': Sex.objects.filter(status=1).order_by('name'),
		'tribe': Tribe.objects.filter(status=1).order_by('name'),
		'civil_status': CivilStatus.objects.filter(status=1).order_by('name'),
		'province': Province.objects.filter(is_active=1).order_by('prov_name'),
		'region': region.objects.filter(is_active=1).order_by('region_name'),
		'occupation': occupation_tbl.objects.filter(is_active=1).order_by('id'),
		'Relation': Relation.objects.filter(status=1),
		'presented_id':presented_id.objects.all(),
		'information': ClientBeneficiary.objects.filter(unique_id_number=data).first(),
		'family_composistion': ClientBeneficiaryFamilyComposition.objects.filter(clientbene__unique_id_number=data),


	}
	return render(request, "client_bene_online/registration.html", context)

@login_required
def requestsOnline(request):
	user_data = ClientBeneficiary.objects.filter(user_data_id=request.user.id).first()
	if user_data:
		user_id=user_data.id
		user_uuid=user_data.unique_id_number
		title='New Requests'
	else:
		user_id=0
		user_uuid=0
		title='Admin'

	if request.method =="POST":
		with transaction.atomic():
			lasttrack = Transaction.objects.order_by('-tracking_number').first()
			track_num = generate_serial_string(lasttrack.tracking_number) if lasttrack else \
				generate_serial_string(None, 'AICS')
			data = Transaction(
				tracking_number=track_num,
				relation_id=request.POST.get('relationship'),
				client_id=user_data.id,
				bene_id=user_data.id,
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
				verified_time_start=data.date_entried,
				is_verified = "1",
				verifier_id=request.user.id,
				verified_time_end=data.date_entried,
				status="1"
			)
			requirements_client.objects.create(
				requirements_uploaded=request.FILES.get('requirements'),
				transaction_id=data.id,
			)
			return JsonResponse({'data': 'success', 'msg': 'New requests has been created. Please wait for the reviewal of your requests and copy the generated reference number.',
								'tracking_number': track_num})

	checking = Transaction.objects.filter(client_id=request.user.id).first() #CHECKING IF CLIENT IS NEW OR RETURNING
	context = {
		'user_id': user_id,
		'title': title,
		'file_type': FileType.objects.filter(status=1, is_required=1),
		'relation': Relation.objects.filter(status=1),
		'category': Category.objects.filter(status=1),
		'sub_category': SubCategory.objects.filter(status=1),
		'service_provider': ServiceProvider.objects.filter(status=1),
		'type_of_assistance': TypeOfAssistance.objects.filter(status=1),
		'sub_category_assistsance': SubModeofAssistance.objects.filter(status=1),
		'assistance_type': LibAssistanceType.objects.filter(is_active=1).order_by('type_name'),
		'PriorityLine': PriorityLine.objects.filter(is_active=1).order_by('id'),
		'presented_id':presented_id.objects.all(),
		'information': ClientBeneficiary.objects.filter(unique_id_number=user_uuid).first(),
		'tribe': Tribe.objects.filter(status=1).order_by('name'),
		'checking': checking,
	}
	return render(request,"client_bene_online/requests.html", context)