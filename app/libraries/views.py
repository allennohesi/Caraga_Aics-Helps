from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, F, Value, CharField
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from app.global_variable import groups_only
from app.libraries.models import Category, ModeOfAdmission, ModeOfAssistance, ServiceProvider, SubCategory, \
    TypeOfAssistance, Relation, Sex, Suffix, Province, City, Barangay, FocalServiceProvider, Tribe, region, FundSource, \
    SignatoriesTbl, occupation_tbl
from app.requests.models import ClientBeneficiary
from app.models import AuthUser, AuthUserGroups
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
def signatories(request):
    if request.method == "POST":
        signatories_id=request.POST.get('signatories')
        check = SignatoriesTbl.objects.filter(signatories_id=request.POST.get('signatories'))
        if not check:
            SignatoriesTbl.objects.create(
                signatories_id=signatories_id,
                signature_file=request.FILES.get('file'),
                status=True,
            )
            return JsonResponse({'error': False, 'msg': "New signatories has been added"})
        else:
            return JsonResponse({'error': True, 'msg': "The signatories already exists"})
    return render(request, 'libraries/signatories.html')

@login_required
def update_signatories(request):
    if request.method == "POST":
        esig_id = request.POST.get('edit-id')
        check = SignatoriesTbl.objects.filter(id=esig_id)
        if check:
            SignatoriesTbl.objects.update(
                status=True if request.POST.get('edit-status') else False,
            )
            return JsonResponse({'error': False, 'msg': "Signatories has been updated"})
        else:
            return JsonResponse({'error': True, 'msg': "ID does not exists"})

@login_required
def fund_source(request):
    if request.method == "POST":
        name=request.POST.get('fund_source')
        check = FundSource.objects.filter(name=request.POST.get('fund_source'))
        if not check:
            FundSource.objects.create(
                name=name,
                updated_by_id=request.user.id,
                status=True,
                date_updated=datetime.now()
            )
            return JsonResponse({'error': False, 'msg': "New Fund Source '{}' has been added successfully.".format(name)})
        else:
            return JsonResponse({'error': True, 'msg': "Fund Source '{}' is already existed.".format(name)})
        
    context = {
        'title': 'Fund-Source'
    }
    return render(request, 'libraries/fund_source.html', context)
    
def edit_fund_source(request):
    if request.method == "POST":
        name = request.POST.get('edit-name')
        FundSource.objects.filter(id=request.POST.get('edit-id')).update(
            name=name,
            updated_by_id=request.user.id,
            status=True if request.POST.get('edit-status') else False
        )
        return JsonResponse({'error': False, 'msg': "Fund source has '{}' has been added successfully.".format(name)})

@login_required
@groups_only('Super Administrator')
def category(request):
    if request.method == "POST":
        name = request.POST.get('name')
        acronym = request.POST.get('acronym')

        check = Category.objects.filter(name=name)
        if not check:
            Category.objects.create(
                name=name,
                acronym=acronym,
                updated_by_id=request.user.id,
                status=True
            )

            return JsonResponse({'error': False, 'msg': "New Category '{}' has been added successfully.".format(name)})
        else:
            return JsonResponse({'error': True, 'msg': "Category '{}' is already existed.".format(name)})
    context = {
        'title': 'Category'
    }
    return render(request, 'libraries/category.html', context)


@login_required
@groups_only('Super Administrator')
def edit_category(request):
    if request.method == "POST":
        id = request.POST.get('edit-id')
        name = request.POST.get('edit-name')
        acronym = request.POST.get('edit-acronym')

        check = Category.objects.filter(name=name, id=id)
        if check: # If no changes only status
            Category.objects.filter(id=id).update(
                name=name,
                acronym=acronym,
                updated_by_id=request.user.id,
                date_updated=datetime.now(),
                status=True if request.POST.get('edit-status') else False
            )
            return JsonResponse({'error': False, 'msg': "Category '{}' has been updated successfully.".format(name)})
        else:
            check = Category.objects.filter(name=name)
            if not check:
                Category.objects.filter(id=id).update(
                    name=name,
                    acronym=acronym,
                    updated_by_id=request.user.id,
                    date_updated=datetime.now(),
                    status=True if request.POST.get('edit-status') else False
                )
                return JsonResponse({'error': False, 'msg': "New Category '{}' has been added successfully.".format(name)})
            else:
                return JsonResponse({'error': True, 'msg': "Category '{}' is already existed.".format(name)})


@login_required
@groups_only('Super Administrator')
def mode_of_admission(request):
    if request.method == "POST":
        name = request.POST.get('name')
        acronym = request.POST.get('acronym')

        check = ModeOfAdmission.objects.filter(name=name)
        if not check:
            ModeOfAdmission.objects.create(
                name=name,
                acronym=acronym,
                updated_by_id=request.user.id,
                status=True
            )

            return JsonResponse({'error': False, 'msg': "New Mode of Admission '{}' has been added successfully.".format(name)})
        else:
            return JsonResponse({'error': True, 'msg': "Mode of Admission '{}' is already existed.".format(name)})
    context = {
        'title': 'Mode of Admission'
    }
    return render(request, 'libraries/mode_of_admission.html', context)

@login_required
@groups_only('Super Administrator')
def edit_mode_of_admission(request):
    if request.method == "POST":
        id = request.POST.get('edit-id')
        name = request.POST.get('edit-name')
        acronym = request.POST.get('edit-acronym')

        check = ModeOfAdmission.objects.filter(name=name, id=id)
        if check: # If no changes only status
            ModeOfAdmission.objects.filter(id=id).update(
                name=name,
                acronym=acronym,
                updated_by_id=request.user.id,
                date_updated=datetime.now(),
                status=True if request.POST.get('edit-status') else False
            )
            return JsonResponse({'error': False, 'msg': "Mode of Admission '{}' has been updated successfully.".format(name)})
        else:
            check = ModeOfAdmission.objects.filter(name=name)
            if not check:
                ModeOfAdmission.objects.filter(id=id).update(
                    name=name,
                    acronym=acronym,
                    updated_by_id=request.user.id,
                    date_updated=datetime.now(),
                    status=True if request.POST.get('edit-status') else False
                )
                return JsonResponse({'error': False, 'msg': "New Mode of Admission '{}' has been added successfully.".format(name)})
            else:
                return JsonResponse({'error': True, 'msg': "Mode of Admission '{}' is already existed.".format(name)})


@login_required
@groups_only('Super Administrator')
def mode_of_assistance(request):
    if request.method == "POST":
        name = request.POST.get('name')
        acronym = request.POST.get('acronym')

        check = ModeOfAssistance.objects.filter(name=name)
        if not check:
            ModeOfAssistance.objects.create(
                name=name,
                acronym=acronym,
                updated_by_id=request.user.id,
                status=True
            )

            return JsonResponse({'error': False, 'msg': "New Mode of Assistance '{}' has been added successfully.".format(name)})
        else:
            return JsonResponse({'error': True, 'msg': "Mode of Assistance '{}' is already existed.".format(name)})
    context = {
        'title': 'Mode of Assistance'
    }
    return render(request, 'libraries/mode_of_assistance.html', context)


@login_required
@groups_only('Super Administrator')
def edit_mode_of_assistance(request):
    if request.method == "POST":
        id = request.POST.get('edit-id')
        name = request.POST.get('edit-name')
        acronym = request.POST.get('edit-acronym')

        check = ModeOfAssistance.objects.filter(name=name, id=id)
        if check: # If no changes only status
            ModeOfAssistance.objects.filter(id=id).update(
                name=name,
                acronym=acronym,
                updated_by_id=request.user.id,
                date_updated=datetime.now(),
                status=True if request.POST.get('edit-status') else False
            )
            return JsonResponse({'error': False, 'msg': "Mode of Admission '{}' has been updated successfully.".format(name)})
        else:
            check = ModeOfAssistance.objects.filter(name=name)
            if not check:
                ModeOfAssistance.objects.filter(id=id).update(
                    name=name,
                    acronym=acronym,
                    updated_by_id=request.user.id,
                    date_updated=datetime.now(),
                    status=True if request.POST.get('edit-status') else False
                )
                return JsonResponse({'error': False, 'msg': "New Mode of Assistance '{}' has been added successfully.".format(name)})
            else:
                return JsonResponse({'error': True, 'msg': "Mode of Assistance '{}' is already existed.".format(name)})


@login_required #ORIGINAL CODE
@csrf_exempt
def get_all_user(request):
    search_term = request.GET.get('searchTerm', '')
    
    if search_term:
        users = AuthUser.objects.filter(
            (Q(first_name__icontains=search_term) | Q(last_name__icontains=search_term)) & Q(is_active=1)
        ).order_by('last_name')[:6]

        json_data = [{'id': user.id, 'text': user.get_fullname} for user in users]
        return JsonResponse(json_data, safe=False)

    return JsonResponse([], safe=False)


@login_required
@csrf_exempt
def get_all_client_beneficiary(request):
    search_term = request.GET.get('searchTerm', '')
    if search_term:
        clients_query = (
            ClientBeneficiary.objects
            .filter(client_bene_fullname__icontains=search_term, is_validated=1)
            .order_by('client_bene_fullname')
            .values_list('id', 'client_bene_fullname')[:6]
        )
        
        json_data = [{'id': client[0], 'text': client[1]} for client in clients_query]
        return JsonResponse(json_data, safe=False)
    
    return JsonResponse([], safe=False)

# @login_required #ORIGINAL CODE
# @csrf_exempt
# def get_all_client_beneficiary(request):
#     search_term = request.GET.get('searchTerm', '')
    
#     if search_term:
#         clients = (
#             ClientBeneficiary.objects
#             .filter(Q(client_bene_fullname__icontains=search_term) & Q(is_validated=1))
#             .order_by('client_bene_fullname')[:10]
#             .values_list('id', 'client_bene_fullname')
#         )

#         json_data = [{'id': id, 'text': client_bene_fullname} for id, client_bene_fullname in clients]
#         return JsonResponse(json_data, safe=False)
    
#     return JsonResponse([], safe=False)

# @login_required
# @csrf_exempt
# def get_all_client_beneficiary(request):
#     search_term = request.GET.get('searchTerm', '')
#     if search_term:
#         clients = (
#             ClientBeneficiary.objects
#             .filter((Q(first_name__icontains=search_term) | Q(last_name__icontains=search_term)) & Q(is_validated=1))
#             .order_by('last_name')[:20]
#             .values('id', 'first_name', 'middle_name', 'last_name', 'suffix__name')
#         )
#         json_data = [
#             {
#                 'id': client['id'],
#                 'text': get_client_fullname(client['first_name'], client['middle_name'], client['last_name'], client['suffix__name'])
#             } for client in clients
#         ]
#         return JsonResponse(json_data, safe=False)
    
#     return JsonResponse([], safe=False)

# def get_client_fullname(first_name, middle_name, last_name, suffix_name):
#     suffix_name = suffix_name if suffix_name else ""
#     return "{} {}. {} {}".format(first_name, middle_name[:1], last_name, suffix_name) if middle_name else "{} {} {}".format(first_name, last_name, suffix_name)


# @login_required #SECOND CODE
# @csrf_exempt
# def get_all_client_beneficiary(request):
#     search_term = request.GET.get('searchTerm', '')
#     if search_term:
#         clients = (
#             ClientBeneficiary.objects
#             .filter((Q(first_name__icontains=search_term) | Q(last_name__icontains=search_term)) & Q(is_validated=1))
#             .order_by('last_name')[:20]
#             .values_list('id', flat=True)
#         )

#         json_data = [{'id': client_id, 'text': ClientBeneficiary.objects.get(id=client_id).get_client_fullname} for client_id in clients]
#         return JsonResponse(json_data, safe=False)
#     return JsonResponse([], safe=False)


# @login_required #ORIGINAL CODE
# @csrf_exempt
# def get_all_client_beneficiary(request):
#     json = []
#     if request.GET.get('searchTerm', ''):
#         client = ClientBeneficiary.objects.filter((Q(first_name__icontains=request.GET.get('searchTerm')) |
#                                         Q(last_name__icontains=request.GET.get('searchTerm'))) & Q(is_validated=1)).order_by('last_name')[:20]
#         if client:
#             for row in client:
#                 json.append({'id': row.id, 'text': row.get_client_fullname })

#         return JsonResponse(json, safe=False)
#     else:
#         return JsonResponse(json, safe=False)


@login_required
@csrf_exempt
def get_all_service_provider(request):
    json = []
    if request.GET.get('searchTerm', ''):
        client = ServiceProvider.objects.filter(Q(name__icontains=request.GET.get('searchTerm')) |
                                        Q(acronym__icontains=request.GET.get('searchTerm'))).order_by('name')[:10]
        if client:
            for row in client:
                json.append({'id': row.id, 'text': row.name })

        return JsonResponse(json, safe=False)
    else:
        return JsonResponse(json, safe=False)

@login_required
def service_provider(request):
    if request.method == "POST":
        name=request.POST.get('service_provider')
        check = ServiceProvider.objects.filter(name=request.POST.get('service_provider'))
        if not check:
            ServiceProvider.objects.create(
                name=name,
                acronym=request.POST.get('acronym'),
                address=request.POST.get('address'),
                contact_number=request.POST.get('contactnumber'),
                updated_by_id=request.user.id,
                status=True,
                date_updated=datetime.now()
            )
            return JsonResponse({'error': False, 'msg': "New service provider '{}' has been added successfully.".format(name)})
        else:
            return JsonResponse({'error': True, 'msg': "Fund service provider '{}' is already existed.".format(name)})
        
    context = {
        'title': 'Service-Provider'
    }
    return render(request, 'libraries/service_provider.html', context)

@login_required
@groups_only('Super Administrator')
def edit_service_provider(request, pk):
    if request.method == "POST":
        name = request.POST.get('edit-name')
        acronym = request.POST.get('edit-acronym')
        address = request.POST.get('address')
        contact_number = request.POST.get('contactnumber')
        category = request.POST.get('category')
        check = ServiceProvider.objects.filter(id=pk)
        if check: # If no changes only status
            ServiceProvider.objects.filter(id=pk).update(
                name=name,
                acronym=acronym,
                address=address,
                contact_number=contact_number,
                updated_by_id=request.user.id,
                date_updated=datetime.now(),
                category=category if category else "",
                status=True if request.POST.get('edit-status') else False
            )
            return JsonResponse({'error': False, 'msg': "Service Provider '{}' has been updated successfully.".format(name)})
    context = {
        'service_provider': ServiceProvider.objects.filter(id=pk).first(),
    }
    return render(request, 'libraries/edit_service_provider.html', context)


@login_required
@csrf_exempt
@groups_only('Super Administrator')
def delete_focal_service_provider(request):
    if request.method == "POST":
        data = FocalServiceProvider.objects.filter(id=request.POST.get('id'))
        focal_person = data.first().user.get_fullname
        data.delete()

        return JsonResponse({'error': False, 'msg': "Focal Person '{}' has been deleted successfully.".format(focal_person)})


@login_required
@groups_only('Super Administrator')
def sub_category(request):
    if request.method == "POST":
        name = request.POST.get('name')
        acronym = request.POST.get('acronym')

        check = SubCategory.objects.filter(name=name)
        if not check:
            SubCategory.objects.create(
                name=name,
                acronym=acronym,
                updated_by_id=request.user.id,
                status=True
            )

            return JsonResponse({'error': False, 'msg': "New Sub-Category '{}' has been added successfully.".format(name)})
        else:
            return JsonResponse({'error': True, 'msg': "Sub-Category '{}' is already existed.".format(name)})
    context = {
        'title': 'Sub-Category'
    }
    return render(request, 'libraries/sub_category.html', context)


@login_required
@groups_only('Super Administrator')
def edit_sub_category(request):
    if request.method == "POST":
        id = request.POST.get('edit-id')
        name = request.POST.get('edit-name')
        acronym = request.POST.get('edit-acronym')

        check = SubCategory.objects.filter(name=name, id=id)
        if check: # If no changes only status
            SubCategory.objects.filter(id=id).update(
                name=name,
                acronym=acronym,
                updated_by_id=request.user.id,
                date_updated=datetime.now(),
                status=True if request.POST.get('edit-status') else False
            )
            return JsonResponse({'error': False, 'msg': "Sub-Category '{}' has been updated successfully.".format(name)})
        else:
            check = SubCategory.objects.filter(name=name)
            if not check:
                SubCategory.objects.filter(id=id).update(
                    name=name,
                    acronym=acronym,
                    updated_by_id=request.user.id,
                    date_updated=datetime.now(),
                    status=True if request.POST.get('edit-status') else False
                )
                return JsonResponse({'error': False, 'msg': "New Sub-Category '{}' has been added successfully.".format(name)})
            else:
                return JsonResponse({'error': True, 'msg': "Sub-Category '{}' is already existed.".format(name)})


@login_required
@groups_only('Super Administrator')
def type_of_assistance(request):
    if request.method == "POST":
        name = request.POST.get('name')
        acronym = request.POST.get('acronym')

        check = TypeOfAssistance.objects.filter(name=name)
        if not check:
            TypeOfAssistance.objects.create(
                name=name,
                acronym=acronym,
                updated_by_id=request.user.id,
                status=True
            )

            return JsonResponse({'error': False, 'msg': "New Type of Assistance '{}' has been added successfully.".format(name)})
        else:
            return JsonResponse({'error': True, 'msg': "Type of Assistance '{}' is already existed.".format(name)})
    context = {
        'title': 'Type of Assistance'
    }
    return render(request, 'libraries/type_of_assistance.html', context)


@login_required
@groups_only('Super Administrator')
def edit_type_of_assistance(request):
    if request.method == "POST":
        id = request.POST.get('edit-id')
        name = request.POST.get('edit-name')
        acronym = request.POST.get('edit-acronym')

        check = TypeOfAssistance.objects.filter(name=name, id=id)
        if check: # If no changes only status
            TypeOfAssistance.objects.filter(id=id).update(
                name=name,
                acronym=acronym,
                updated_by_id=request.user.id,
                date_updated=datetime.now(),
                status=True if request.POST.get('edit-status') else False
            )
            return JsonResponse({'error': False, 'msg': "Type of Assistance '{}' has been updated successfully.".format(name)})
        else:
            check = TypeOfAssistance.objects.filter(name=name)
            if not check:
                TypeOfAssistance.objects.filter(id=id).update(
                    name=name,
                    acronym=acronym,
                    updated_by_id=request.user.id,
                    date_updated=datetime.now(),
                    status=True if request.POST.get('edit-status') else False
                )
                return JsonResponse({'error': False, 'msg': "New Type of Assistance '{}' has been added successfully.".format(name)})
            else:
                return JsonResponse({'error': True, 'msg': "Type of Assistance '{}' is already existed.".format(name)})


@login_required
@groups_only('Super Administrator')
def relation(request):
    if request.method == "POST":
        name = request.POST.get('name')

        check = Relation.objects.filter(name=name)
        if not check:
            Relation.objects.create(
                name=name,
                updated_by_id=request.user.id,
                status=True
            )

            return JsonResponse({'error': False, 'msg': "New Relation '{}' has been added successfully.".format(name)})
        else:
            return JsonResponse({'error': True, 'msg': "Relation '{}' is already existed.".format(name)})
    context = {
        'title': 'Relation'
    }
    return render(request, 'libraries/relation.html', context)


@login_required
@groups_only('Super Administrator')
def edit_relation(request):
    if request.method == "POST":
        id = request.POST.get('edit-id')
        name = request.POST.get('edit-name')

        check = Relation.objects.filter(name=name, id=id)
        if check: # If no changes only status
            Relation.objects.filter(id=id).update(
                name=name,
                updated_by_id=request.user.id,
                date_updated=datetime.now(),
                status=True if request.POST.get('edit-status') else False
            )
            return JsonResponse({'error': False, 'msg': "Relation '{}' has been updated successfully.".format(name)})
        else:
            check = Relation.objects.filter(name=name)
            if not check:
                Relation.objects.filter(id=id).update(
                    name=name,
                    updated_by_id=request.user.id,
                    date_updated=datetime.now(),
                    status=True if request.POST.get('edit-status') else False
                )
                return JsonResponse({'error': False, 'msg': "New Relation '{}' has been added successfully.".format(name)})
            else:
                return JsonResponse({'error': True, 'msg': "Relation '{}' is already existed.".format(name)})


@login_required
@groups_only('Super Administrator')
def sex(request):
    if request.method == "POST":
        name = request.POST.get('name')

        check = Sex.objects.filter(name=name)
        if not check:
            Sex.objects.create(
                name=name,
                updated_by_id=request.user.id,
                status=True
            )

            return JsonResponse({'error': False, 'msg': "New Sex '{}' has been added successfully.".format(name)})
        else:
            return JsonResponse({'error': True, 'msg': "Sex '{}' is already existed.".format(name)})
    context = {
        'title': 'Sex'
    }
    return render(request, 'libraries/sex.html', context)


@login_required
@groups_only('Super Administrator')
def edit_sex(request):
    if request.method == "POST":
        id = request.POST.get('edit-id')
        name = request.POST.get('edit-name')

        check = Sex.objects.filter(name=name, id=id)
        if check: # If no changes only status
            Sex.objects.filter(id=id).update(
                name=name,
                updated_by_id=request.user.id,
                date_updated=datetime.now(),
                status=True if request.POST.get('edit-status') else False
            )
            return JsonResponse({'error': False, 'msg': "Sex '{}' has been updated successfully.".format(name)})
        else:
            check = Sex.objects.filter(name=name)
            if not check:
                Sex.objects.filter(id=id).update(
                    name=name,
                    updated_by_id=request.user.id,
                    date_updated=datetime.now(),
                    status=True if request.POST.get('edit-status') else False
                )
                return JsonResponse({'error': False, 'msg': "New Sex '{}' has been added successfully.".format(name)})
            else:
                return JsonResponse({'error': True, 'msg': "Sex '{}' is already existed.".format(name)})


@login_required
@groups_only('Super Administrator')
def suffix(request):
    if request.method == "POST":
        name = request.POST.get('name')

        check = Suffix.objects.filter(name=name)
        if not check:
            Suffix.objects.create(
                name=name,
                updated_by_id=request.user.id,
                status=True
            )

            return JsonResponse({'error': False, 'msg': "New Suffix '{}' has been added successfully.".format(name)})
        else:
            return JsonResponse({'error': True, 'msg': "Suffix '{}' is already existed.".format(name)})
    context = {
        'title': 'Suffix'
    }
    return render(request, 'libraries/suffix.html', context)


@login_required
@groups_only('Super Administrator')
def edit_suffix(request):
    if request.method == "POST":
        id = request.POST.get('edit-id')
        name = request.POST.get('edit-name')

        check = Suffix.objects.filter(name=name, id=id)
        if check: # If no changes only status
            Suffix.objects.filter(id=id).update(
                name=name,
                updated_by_id=request.user.id,
                date_updated=datetime.now(),
                status=True if request.POST.get('edit-status') else False
            )
            return JsonResponse({'error': False, 'msg': "Suffix '{}' has been updated successfully.".format(name)})
        else:
            check = Suffix.objects.filter(name=name)
            if not check:
                Suffix.objects.filter(id=id).update(
                    name=name,
                    updated_by_id=request.user.id,
                    date_updated=datetime.now(),
                    status=True if request.POST.get('edit-status') else False
                )
                return JsonResponse({'error': False, 'msg': "New Suffix '{}' has been added successfully.".format(name)})
            else:
                return JsonResponse({'error': True, 'msg': "Suffix '{}' is already existed.".format(name)})


@login_required
@groups_only('Super Administrator')
def tribe(request):
    if request.method == "POST":
        name = request.POST.get('name')

        check = Tribe.objects.filter(name=name)
        if not check:
            Tribe.objects.create(
                name=name,
                updated_by_id=request.user.id,
                status=True
            )

            return JsonResponse({'error': False, 'msg': "New Tribe '{}' has been added successfully.".format(name)})
        else:
            return JsonResponse({'error': True, 'msg': "Tribe '{}' is already existed.".format(name)})
    context = {
        'title': 'Tribe'
    }
    return render(request, 'libraries/tribe.html', context)


@login_required
@groups_only('Super Administrator')
def edit_tribe(request):
    if request.method == "POST":
        id = request.POST.get('edit-id')
        name = request.POST.get('edit-name')

        check = Tribe.objects.filter(name=name, id=id)
        if check: # If no changes only status
            Tribe.objects.filter(id=id).update(
                name=name,
                updated_by_id=request.user.id,
                date_updated=datetime.now(),
                status=True if request.POST.get('edit-status') else False
            )
            return JsonResponse({'error': False, 'msg': "Tribe '{}' has been updated successfully.".format(name)})
        else:
            check = Tribe.objects.filter(name=name)
            if not check:
                Tribe.objects.filter(id=id).update(
                    name=name,
                    updated_by_id=request.user.id,
                    date_updated=datetime.now(),
                    status=True if request.POST.get('edit-status') else False
                )
                return JsonResponse({'error': False, 'msg': "New Tribe '{}' has been added successfully.".format(name)})
            else:
                return JsonResponse({'error': True, 'msg': "Tribe '{}' is already existed.".format(name)})


@login_required
@groups_only('Super Administrator')
def province(request):
    if request.method == "POST":
        name = request.POST.get('name')
        prov_code = request.POST.get('prov_code')
        check = Province.objects.filter(prov_code=prov_code,prov_name=name)
        if not check:
            Province.objects.create(
                prov_name=name,
                prov_code=prov_code,
                region_code_id=request.POST.get('Region'),
                is_active=None
            )

            return JsonResponse({'error': False, 'msg': "New Province '{}' has been added successfully.".format(name)})
        else:
            return JsonResponse({'error': True, 'msg': "Province '{}' is already existed.".format(name)})
    context = {
        'title': 'Province',
        'region': region.objects.all().order_by('-id')
    }
    return render(request, 'libraries/province.html', context)


@login_required
@groups_only('Super Administrator')
def edit_province(request):
    if request.method == "POST":
        id = request.POST.get('edit-id')
        name = request.POST.get('edit-name')

        check = Province.objects.filter(name=name, id=id)
        if check: # If no changes only status
            Province.objects.filter(id=id).update(
                name=name,
                updated_by_id=request.user.id,
                date_updated=datetime.now(),
                status=True if request.POST.get('edit-status') else False
            )
            return JsonResponse({'error': False, 'msg': "Province '{}' has been updated successfully.".format(name)})
        else:
            check = Province.objects.filter(name=name)
            if not check:
                Province.objects.filter(id=id).update(
                    name=name,
                    updated_by_id=request.user.id,
                    date_updated=datetime.now(),
                    status=True if request.POST.get('edit-status') else False
                )
                return JsonResponse({'error': False, 'msg': "New Province '{}' has been added successfully.".format(name)})
            else:
                return JsonResponse({'error': True, 'msg': "Province '{}' is already existed.".format(name)})


@login_required
@groups_only('Super Administrator')
def city(request):
    if request.method == "POST":
        name = request.POST.get('name')
        code = request.POST.get('code')
        province = request.POST.get('province')

        check = City.objects.filter(prov_code_id=code,city_name=name)
        if not check:
            City.objects.create(
                city_name=name,
                city_code=code,
                prov_code_id=province,
                is_urban=0,
                is_active=0
            )

            return JsonResponse({'error': False, 'msg': "New City '{}' has been added successfully.".format(name)})
        else:
            return JsonResponse({'error': True, 'msg': "City '{}' is already existed.".format(name)})
    context = {
        'title': 'City',
        'province': Province.objects.order_by('prov_name')
    }
    return render(request, 'libraries/city.html', context)


@login_required
@groups_only('Super Administrator')
def edit_city(request):
    if request.method == "POST":
        id = request.POST.get('edit-id')
        name = request.POST.get('edit-name')
        code = request.POST.get('edit-code')
        province = request.POST.get('province')

        check = City.objects.filter(name=name, id=id)
        if check: # If no changes only status
            City.objects.filter(id=id).update(
                name=name,
                code=code,
                prov_code_id=province,
                updated_by_id=request.user.id,
                date_updated=datetime.now(),
                status=True if request.POST.get('edit-status') else False
            )
            return JsonResponse({'error': False, 'msg': "City '{}' has been updated successfully.".format(name)})
        else:
            check = City.objects.filter(name=name)
            if not check:
                City.objects.filter(id=id).update(
                    name=name,
                    code=code,
                    prov_code_id=province,
                    updated_by_id=request.user.id,
                    date_updated=datetime.now(),
                    status=True if request.POST.get('edit-status') else False
                )
                return JsonResponse({'error': False, 'msg': "New City '{}' has been added successfully.".format(name)})
            else:
                return JsonResponse({'error': True, 'msg': "City '{}' is already existed.".format(name)})


@login_required
@groups_only('Super Administrator')
def barangay(request):
    if request.method == "POST":
        name = request.POST.get('name')
        city = request.POST.get('city')
        psgc = request.POST.get('psgc')
        urb_rur = request.POST.get('urb_rur')

        check = Barangay.objects.filter(brgy_code=psgc,brgy_name=name)
        if not check:
            Barangay.objects.create(
                brgy_name=name,
                brgy_code=psgc,
                city_code_id=city,
                is_active=True,
                urb_rur = urb_rur,
            )

            return JsonResponse({'error': False, 'msg': "New Barangay '{}' has been added successfully.".format(name)})
        else:
            return JsonResponse({'error': True, 'msg': "Barangay '{}' is already existed.".format(name)})
    context = {
        'title': 'Barangay',
        'region': region.objects.filter(is_active=1).order_by('region_name'),
        'province': Province.objects.all().order_by('prov_name')
    }
    return render(request, 'libraries/barangay.html', context)


@login_required
@groups_only('Super Administrator')
def edit_barangay(request):
    if request.method == "POST":
        id = request.POST.get('edit-id')
        name = request.POST.get('edit-name')
        city = request.POST.get('city')

        check = Barangay.objects.filter(brgy_name=name, id=id)
        if check: # If no changes only status
            Barangay.objects.filter(id=id).update(
                brgy_name=name,
                city_code_id=city,
                is_active=True if request.POST.get('edit-status') else False
            )
            return JsonResponse({'error': False, 'msg': "Barangay '{}' has been updated successfully.".format(name)})
        else:
            check = Barangay.objects.filter(brgy_name=name)
            if not check:
                Barangay.objects.filter(id=id).update(
                    brgy_name=name,
                    city_code_id=city,
                    is_active=True if request.POST.get('edit-status') else False
                )
                return JsonResponse({'error': False, 'msg': "New Barangay '{}' has been added successfully.".format(name)})
            else:
                return JsonResponse({'error': True, 'msg': "Barangay '{}' is already existed.".format(name)})


@login_required
def get_province_name(request, pk):
    pk = str(pk)  # Convert pk to string
    if len(pk) == 8:
        pk = '0' + pk
    province = Province.objects.filter(region_code=pk).values('prov_code', 'prov_name').order_by('prov_name')
    json = []
    for row in province:
        json.append({row['prov_code']: row['prov_name'].title()})
    return JsonResponse(json, safe=False)


@login_required
def get_city_name(request, pk):
    pk = str(pk)  # Convert pk to string
    if len(pk) == 8:
        pk = '0' + pk
    citymuns = City.objects.filter(prov_code_id=pk).values('city_code', 'city_name').order_by('city_name')
    json = []
    for row in citymuns:
        json.append({row['city_code']: row['city_name'].title()})
    return JsonResponse(json, safe=False)


@login_required
def get_barangay_name(request, pk):
    pk = str(pk)  # Convert pk to string
    if len(pk) == 8:
        pk = '0' + pk
    barangay = Barangay.objects.filter(city_code_id=pk).values('brgy_code', 'brgy_name').order_by('brgy_name')
    json = []
    for row in barangay:
        json.append({row['brgy_code']: row['brgy_name'].title()})
    return JsonResponse(json, safe=False)

@login_required
def occupation(request):
    if request.method == "POST":
        name = request.POST.get('name')
        check = occupation_tbl.objects.filter(occupation_name=name)
        if not check:
            occupation_tbl.objects.create(
                occupation_name=name,
                user_id=request.user.id,
                is_active=1
            )
            return JsonResponse({'error': False, 'msg': "New Occupation '{}' has been added successfully.".format(name)})
        else:
            return JsonResponse({'error': True, 'msg': "Occupation '{}' is already existed.".format(name)})
    context = {
        'title': 'Occupation'
    }
    return render(request, 'libraries/occupation.html', context)