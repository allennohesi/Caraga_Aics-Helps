import os
from django import template

from app.requests.models import TransactionServiceAssistance, Mail, TransactionStatus1, Transaction
from app.models import AuthUser, AuthUserGroups, AuthuserProfile, AuthuserDetails
from app.libraries.models import OfficeStation, Purpose
from num2words import num2words

register = template.Library()


@register.filter
def check_group_permission(user, group_name):
	if user.groups.filter(name=group_name).exists():
		return True
	return False


@register.simple_tag
def profile_picture_dashboard(user_id):
	profile = AuthuserProfile.objects.filter(user_id=user_id).first()  # Use .first() to get a single object
	return profile


@register.filter
def filename(value):
	return os.path.basename(value.file.name)

@register.simple_tag
def get_profile_pict(user_id=None):
	if user_id is not None:
		data = AuthuserProfile.objects.filter(user_id=user_id).first()
		if data:
			return data.profile_pict.url
	return None

@register.simple_tag
def get_user_info(user_id):
	return AuthUser.objects.filter(id=user_id).first().get_fullname


@register.simple_tag
def get_user_role(user_id):
	# Fetch the first AuthUserGroups object for the given user_id
    user_groups = AuthUserGroups.objects.filter(user_id=user_id).select_related('group')

    # Extract group names as a list
    roles = [ug.group.name for ug in user_groups]

    # Return a comma-separated string of roles (or a default message if none found)
    return ", ".join(roles) if roles else "No Role Assigned"




@register.simple_tag
def get_transaction_service_assistance(transaction_id, sa_id):
	return TransactionServiceAssistance.objects.filter(transaction_id=transaction_id, service_assistance_id=sa_id).first()

@register.simple_tag
def get_count_mail():
	return TransactionStatus1.objects.filter(is_swo=None).count()


@register.simple_tag
def count_pending():
	return TransactionStatus1.objects.filter(is_verified=1).count()

@register.simple_tag
def count_assessment_all():
	return TransactionStatus1.objects.filter(is_swo=None).count()

@register.simple_tag
def count_ongoing():
	return TransactionStatus1.objects.filter(status=2).count()


@register.filter(name='number_to_words')
def number_to_words(value):
	# Remove commas from the value
	value = str(value).replace(',', '')

	# Split the value into integer and decimal parts
	integer_part, _, decimal_part = str(value).partition('.')

	# Convert the integer part to words
	words = num2words(int(integer_part), lang='en').title()

	# Check if there is a decimal part
	if decimal_part and decimal_part != '00':
		# Append 'Pesos' and the decimal part as a fraction
		words = words.replace(' And', '')
		AndFor = "Pesos And"
		words = f"{words} {AndFor} {decimal_part} / 100"
		# words += f" Pesos {decimal_part} / 100"
	else:
		# If no decimal part, append 'Pesos' directly
		data = words.replace(' And', '')
		words = data + " Pesos"

	return words

@register.filter
def subtract(value, arg):
	return value - arg

@register.simple_tag
def get_signatories(province): 
	signatories = ""
	data = OfficeStation.objects.filter(region=province).first()
	signatories = data.main_signatories
	return signatories

@register.simple_tag
def get_head(province): #ONLY GIS SIGNATORIES IF GL
	signatories = ""
	data = OfficeStation.objects.filter(region=province).first()
	signatories = data.head
	return signatories

@register.simple_tag
def get_office_stations():
	return OfficeStation.objects.all()

@register.simple_tag
def get_Purpose():
	return Purpose.objects.all()

@register.simple_tag
def get_office_station_signatories(user_id):
	"""
	Retrieves the office station signatory details for the given user.
	"""
	try:
		# Fetch the AuthuserDetails instance for the given user_id
		data = AuthuserDetails.objects.get(user_id=user_id).OfficeStationLib.main_signatories
	except AuthuserDetails.DoesNotExist:
		# Return None or a default value if no matching record is found
		data = None
	
	return data

@register.simple_tag
def get_office_station_head_and_designation(user_id):
    """
    Retrieves the office station signatory details (head and designation) for the given user.
    """
    try:
        # Fetch the AuthuserDetails instance for the given user_id
        data = AuthuserDetails.objects.get(user_id=user_id).OfficeStationLib
        head = data.head
        designation = data.designation
    except AuthuserDetails.DoesNotExist:
        # Return None or default values if no matching record is found
        head = None
        designation = None
    
    return {'head': head, 'designation': designation}

@register.simple_tag(takes_context=True)
def get_user_details(context):
	request = context['request']
	check_user_details = AuthuserDetails.objects.filter(user_id=request.user.id).first()
	data = check_user_details.OfficeStationLib if check_user_details else None
	return data  # or any other value you want to return