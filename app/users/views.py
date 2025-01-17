from datetime import datetime

from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from app.libraries.models import Province, region, City, Barangay, OfficeStation
from app.models import AuthUser, AuthUserGroups, AuthGroup, AuthuserDetails, AuthuserProfile, AuthFeedback
from app.requests.models import ErrorLogData, ClientBeneficiary, uploadfile, ClientBeneficiaryUpdateHistory
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from requests.exceptions import RequestException

def handle_error(error, location, user): #ERROR HANDLING
	ErrorLogData.objects.create(
		error_log=error,
		location=location,
		user_id=user,
	)

def userFeedback(request):
	context = {
		'title': "feedback",
	}
	return render(request, 'users/userfeedback.html', context)

@login_required
def user_list(request):
	if request.method == "POST":
		check_username = AuthUser.objects.filter(username=request.POST.get('username'))
		check_email = AuthUser.objects.filter(email=request.POST.get('email'))
		if check_email:
			return JsonResponse({'error': True, 'msg': "Email '{}' is already existed.".format(request.POST.get('email'))})
		else:
			if not check_username:
				with transaction.atomic():
					middle_initial = request.POST.get('middle_name', '')
					mi = middle_initial[0].upper() if middle_initial else ''  # Default to empty string if middle_name is not provided
					user_fullname = request.POST.get('first_name') + " " + (mi + ". " if mi else '') + request.POST.get('last_name')
					user = AuthUser(
						first_name=request.POST.get('first_name'),
						middle_name=request.POST.get('middle_name'),
						last_name=request.POST.get('last_name'),
						email=request.POST.get('email'),
						username=request.POST.get('username'),
						password=make_password(request.POST.get('password')),
						is_superuser=True if request.POST.get('is_superuser') else False,
						is_staff=True if request.POST.get('is_staff') else False,
						is_active=1,
						updated_by_id=request.user.id,
						fullname=user_fullname
					)
					user.save()
					AuthuserDetails.objects.create(
						user_id=user.id,
						barangay_id=request.POST.get('barangay'),
						service_provider_id=request.POST.get('service_provider_id'),
					)
					AuthUserGroups.objects.create(
						user_id=user.id,
						group_id=request.POST.get('group')
					)
					return JsonResponse({'data': 'success', 'msg': "New user '{}' has been added successfully.".format(request.POST.get('username'))})
				return JsonResponse({'error': True, 'msg': 'Internal Error. An uncaught exception was raised.'})
			return JsonResponse({'error': True, 'msg': "User '{}' is already existed.".format(request.POST.get('username'))})
	context = {
		'title': 'User List',
		'group': AuthGroup.objects.all().order_by('name'),
		'region': region.objects.filter(is_active=1).order_by('region_name'),
	}
	return render(request, 'users/list.html', context)

@login_required
def feedbackRequest(request):
	if request.method == 'POST':
		feedback = AuthFeedback.objects.create(
			subject=request.POST.get('subject'),
			message=request.POST.get('message'),
			mood=request.POST.get('mood'),
			user_id=request.user.id
		)
		return JsonResponse({'data': 'success','msg':'You successfully submitted your feedback'})

@login_required
def get_role(request, pk):
	return JsonResponse({'data': AuthUserGroups.objects.filter(user_id=pk).first().group.name })

@login_required
def change_password(request):
	if request.method == 'POST':
		# Create a PasswordChangeForm with the target user
		target_user = AuthUser.objects.filter(id=request.POST.get('empid')).update(
			password = make_password(request.POST.get('password'))
		)
		return JsonResponse({'data': 'success','msg':'Password has been updated'})
		
@login_required
def edit_user(request, pk):
	if request.method == "POST":
		check = AuthUser.objects.filter(Q(username=request.POST.get('username')) | Q(email=request.POST.get('email')) |
										Q(first_name=request.POST.get('first_name')) | Q(last_name=request.POST.get('last_name')))
		check_if_details_exists = AuthuserDetails.objects.filter(user_id=pk)
		if check:
			with transaction.atomic():
				middle_initial = request.POST.get('middle_name', '')
				mi = middle_initial[0].upper() if middle_initial else ''  # Default to empty string if middle_name is not provided
				user_fullname = request.POST.get('first_name') + " " + (mi + ". " if mi else '') + request.POST.get('last_name')
				AuthUser.objects.filter(id=pk).update(
					first_name=request.POST.get('first_name'),
					middle_name=request.POST.get('middle_name'),
					last_name=request.POST.get('last_name'),
					email=request.POST.get('email'),
					username=request.POST.get('username'),
					is_superuser=True if request.POST.get('is_superuser') else False,
					is_staff=True if request.POST.get('is_staff') else False,
					is_active=True if request.POST.get('is_active') else False,
					updated_by_id=request.user.id,
					date_updated=datetime.now(),
					fullname=user_fullname
				)
				AuthuserDetails.objects.update_or_create(
					user_id=pk,  # Lookup field (find by user_id)
					defaults={
						'barangay_id': request.POST.get('barangay'),  # Update or set this field
						'service_provider_id':request.POST.get('sp_name')
					}
				)
				AuthUserGroups.objects.update_or_create(
					user_id=pk,  # This is the lookup field
					defaults={
						'group_id': request.POST.get('group')  # This will be updated or set when creating
					}
				)
				return JsonResponse({'data': 'success', 'msg': "User '{}' has been updated successfully.".format(
					request.POST.get('username'))})
		else:
			return JsonResponse(
					{'error': True, 'msg': "User '{}' is already existed.".format(request.POST.get('username'))})
		
	context = {
		'user': AuthUser.objects.filter(id=pk).first(),
		'information': AuthuserDetails.objects.filter(user_id=pk).first(),
		'region': region.objects.filter(is_active=1).order_by('region_name'),
		'user_group': AuthUserGroups.objects.filter(user_id=pk).first(),
		'group': AuthGroup.objects.all().order_by('name')
	}
	return render(request, 'users/edit_user.html', context)

@login_required
def user_profile(request):
	user_data = AuthUser.objects.filter(id=request.user.id).first()
	check_if_details_exists = AuthuserDetails.objects.filter(user_id=request.user.id)
	restriction = request.user.groups.filter(name__in=['Super Administrator', 'Social Worker']).exists()
	if request.method == "POST":
		try:
			#CHANGE THE PASSWORD ONLY
			if request.POST.get('verification') == "changepassword":
				target_user = AuthUser.objects.filter(id=request.user.id).update(
					password = make_password(request.POST.get('password'))
				)
				return JsonResponse({'data': 'success','msg':'Password has been updated'})

			#CHANGE THE PROFILE PICTURE
			elif request.POST.get('verification') == "changeprofile":
				AuthuserProfile.objects.filter(user_id=request.user.id).delete()
				AuthuserProfile.objects.create(
					profile_pict=request.FILES.get('file_name'),
					user_id=request.user.id,
				)
			else:
				#CHANGING OF FULL NAME AND DETAILS
				first_name = request.POST.get('first_name', '')
				middle_name = request.POST.get('middle_name', '')
				last_name = request.POST.get('last_name', '')
	
				# Get the first letter of each part of the first name and middle name
				first_initials = ''.join([name[0] for name in first_name.split()]) if first_name else ''
				middle_initials = ''.join([name[0] for name in middle_name.split()]) if middle_name else ''
				last_initials = last_name if last_name else ''

				username = (first_initials + middle_initials + last_initials).lower()
				AuthUser.objects.filter(id=request.user.id).update(
					first_name = first_name,
					middle_name = middle_name,
					last_name = last_name,
					username = username,
				)
				AuthuserDetails.objects.update_or_create(
					user_id=request.user.id, #FILTERING ONLY
					defaults={
						'barangay_id': request.POST.get('barangay'),
						'license_no': request.POST.get('license_no'),
						'OfficeStationLib_id': request.POST.get('OfficeStation')
					}
				)
				return JsonResponse({'data': 'success','msg':'Information has been updated'})
			
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
			

	context = {
		'user_data': user_data,
		'OfficeStation': OfficeStation.objects.filter(is_active=1),
		'profile_picture':AuthuserProfile.objects.filter(user_id=request.user.id).first(),
		'information': AuthuserDetails.objects.filter(user_id=request.user.id).first(),
		'region': region.objects.filter(is_active=1).order_by('region_name'),
		'province': Province.objects.filter(is_active=1).order_by('prov_name'),
		'city': City.objects.filter(is_active=1).order_by('city_name'),
		'barangay': Barangay.objects.filter(is_active=1).order_by('brgy_name'),
		'restriction': restriction,
	}
	return render(request, 'users/user_profile.html', context)

@login_required
def error_logs(request):
	return render(request, 'users/error_logs.html')

@login_required
def clientupdatehistory(request):
	return render(request, 'client_bene/clientupdatehistory.html')

@login_required
def clienthistorymodal(request, pk):
	information = ClientBeneficiaryUpdateHistory.objects.filter(id=pk).first()
	data = ClientBeneficiary.objects.filter(unique_id_number=information.unique_id_number_id).first()
	picture = uploadfile.objects.filter(client_bene_id=data.id).first()

	context = {
		'pict': picture,
		'data': data,
		'update_history': ClientBeneficiaryUpdateHistory.objects.filter(unique_id_number_id=information.unique_id_number_id)
	}
	return render(request, 'client_bene/clientupdatehistorymodal.html', context)