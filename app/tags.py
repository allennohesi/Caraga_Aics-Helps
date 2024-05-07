import os
from django import template

from app.requests.models import TransactionServiceAssistance, Mail, TransactionStatus1, Transaction
from app.models import AuthUser, AuthUserGroups, AuthuserProfile

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
	return AuthUserGroups.objects.filter(user_id=user_id).first().group.name



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
	if province == "AGUSAN DEL NORTE":
		signatories = "ANA T. SEMACIO"
	elif province == "SURIGAO DEL SUR":
		signatories = "ARLENE M. ONTUA"
	return signatories