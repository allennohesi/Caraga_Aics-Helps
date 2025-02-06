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
from maintenance_mode.decorators import force_maintenance_mode_off, force_maintenance_mode_on

@force_maintenance_mode_on
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def monitoring(request):
	sp_details = AuthuserDetails.objects.filter(user_id=request.user.id).first()
	context = {
		'title': 'Monitoring',
		'sp_details': sp_details,
    }
	return render(request, 'service_provider/monitoring.html', context)

