from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.crypto import get_random_string

from app.libraries.models import Suffix, Sex, CivilStatus, Province, Relation, Category, SubCategory, FileType, \
    ServiceAssistance, TypeOfAssistance, Purpose, ModeOfAssistance, FundSource, ModeOfAdmission
from app.management.models import ClientBeneficiary, ClientBeneficiaryFamilyComposition, Transaction, TransactionFiles, \
     TransactionServiceAssistance


def management(request):
    context = {
        'title': 'Management',
    }
    return render(request, 'management/management.html', context)


@login_required
def registration(request):
    if request.method == "POST":
        with transaction.atomic():
            check_if_name_exists = ClientBeneficiary.objects.filter(Q(last_name__icontains=request.POST.get('last_name')) &
                                                     Q(first_name__icontains=request.POST.get('first_name')) &
                                                     Q(middle_name__icontains=request.POST.get('middle_name')) &
                                                     Q(suffix_id=request.POST.get('suffix') if request.POST.get('suffix') else 0) &
                                                     Q(birthdate=request.POST.get('birthdate')))
            if not check_if_name_exists:
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
                    tribu=request.POST.get('tribe'),
                    barangay_id=request.POST.get('barangay'),
                    street=request.POST.get('street'),
                    house_no=request.POST.get('house_no'),
                    village=request.POST.get('village'),
                    is_4ps=True if request.POST.get('4ps_member') == "1" else False,
                    number_4ps_id_number=request.POST.get('4ps_id_number'),
                    unique_id_number=get_random_string(8).upper(),
                    updated_by_id=request.user.id,
                    is_validated=False,
                    registered_by_id=request.user.id,
                    occupation=request.POST.get('occupation'),
                    salary=request.POST.get('salary')
                )

                clientbene.save()

                full_name = request.POST.getlist('full_name[]')
                birthdate = request.POST.getlist('birthdate[]')
                occupation = request.POST.getlist('occupation[]')
                salary = request.POST.getlist('salary[]')
                if not full_name == [''] and not birthdate == [''] and not occupation == [''] and not salary == ['']:
                    data = [
                        {'full_name': fn, 'birthdate': b, 'occupation': o, 'salary': s}
                        for fn, b, o, s in zip(full_name, birthdate, occupation, salary)
                    ]

                    for row in data:
                        ClientBeneficiaryFamilyComposition.objects.create(
                            full_name=row['full_name'],
                            birthdate=row['birthdate'],
                            occupation=row['occupation'],
                            salary=row['salary'],
                            clientbene_id=clientbene.id
                        )
                else:
                    return JsonResponse({'error': True, 'msg': 'You have provided information in Family Composistion. Please fill in or leave the form blank if not applicable. Thank you!'})
                return JsonResponse({'data': 'success',
                                     'msg': 'You have successfully registered. Please wait for the confirmation of your account.'})
            else:
                return JsonResponse({'error': True, 'msg': 'A client or beneficiary with this name already exists.'})
        return JsonResponse({'error': True, 'msg': 'Internal Error. An uncaught exception was raised.'})
    context = {
        'suffix': Suffix.objects.filter(status=1).order_by('name'),
        'sex': Sex.objects.filter(status=1).order_by('name'),
        'civil_status': CivilStatus.objects.filter(status=1).order_by('name'),
        'province': Province.objects.filter(status=1).order_by('name'),
    }
    return render(request, 'management/registration.html', context)


@login_required
def new_transaction(request):
    context = {
        'file_type': FileType.objects.filter(status=1, is_required=1),
        'relation': Relation.objects.filter(status=1),
        'category': Category.objects.filter(status=1),
        'sub_category': SubCategory.objects.filter(status=1)
    }
    return render(request, 'management/requests.html', context)


@login_required
def list_of_transaction(request):
    return render(request, 'management/list_of_transaction.html')


@login_required
def view_transaction(request, pk):
    if request.method == "POST":
        with transaction.atomic():
            check = Transaction.objects.filter(id=pk)
            check.update(
                client_category_id=request.POST.get('client_category'),
                client_sub_category_id=request.POST.get('client_subcategory'),
                bene_category_id=request.POST.get('bene_category'),
                bene_sub_category_id=request.POST.get('bene_subcategory'),
                problem_presented=request.POST.get('problem'),
                sw_assessment=request.POST.get('assessment'),
                mode_of_admission_id=request.POST.get('moadm'),
                mode_of_assistance_id=request.POST.get('moass'),
                fund_source_id=request.POST.get('fund_source'),
                amount_of_assistance=request.POST.get('amount_of_assistance'),
                purpose_id=request.POST.get('purpose'),
                type_of_assistance_id=request.POST.get('type_of_assistance'),
                service_provider_id=request.POST.get('service_provider')
            )

            service_assistance = request.POST.getlist('service_assistance[]')
            sa_list = []
            for row in ServiceAssistance.objects.filter(status=1):
                sa_list.append(row.id)

            sa_list_compare = []
            for row in sa_list:
                if str(row) in service_assistance:
                    sa_list_compare.append(row)
                else:
                    sa_list_compare.append('')
            is_specify = request.POST.getlist('is_specify[]')

            sa = [
                {'service_assistance': sa, 'is_specify': iss, 'is_checked': salc}
                for sa, iss, salc in zip(sa_list, is_specify, sa_list_compare)
            ]

            tsa = TransactionServiceAssistance.objects.filter(transaction_id=pk)
            store = [row.id for row in tsa]
            if tsa:
                y = 1
                x = 0
                for row in sa:
                    TransactionServiceAssistance.objects.filter(id=store[x]).update(
                        transaction_id=pk,
                        service_assistance_id=row['service_assistance'],
                        specify=row['is_specify'],
                        is_checked=1 if row['is_checked'] != '' else 0
                    )
                    y += 1
                    x += 1
            else:
                for row in sa:
                    TransactionServiceAssistance.objects.create(
                        transaction_id=pk,
                        service_assistance_id=row['service_assistance'],
                        specify=row['is_specify'],
                        is_checked=1 if row['is_checked'] != '' else 0
                    )

            return JsonResponse({'data': 'success', 'msg': 'You have successfully updated requests {}.'.format(check.first().tracking_number)})
        return JsonResponse({'error': True, 'msg': 'Internal Error. An uncaught exception was raised.'})
    data = Transaction.objects.filter(id=pk).first()
    context = {
        'requests': data,
        'transaction_files': TransactionFiles.objects.filter(transaction_id=pk),
        'file_type': FileType.objects.filter(status=1).order_by('name'),
        'category': Category.objects.filter(status=1).order_by('name'),
        'sub_category': SubCategory.objects.filter(status=1).order_by('name'),
        'family_composistion': ClientBeneficiaryFamilyComposition.objects.filter(clientbene_id=data.bene_id),
        'service_assistance': ServiceAssistance.objects.filter(status=1).order_by('name'),
        'type_of_assistance': TypeOfAssistance.objects.filter(status=1).order_by('name'),
        'purpose': Purpose.objects.filter(status=1).order_by('name'),
        'moass': ModeOfAssistance.objects.filter(status=1).order_by('name'),
        'moadm': ModeOfAdmission.objects.filter(status=1).order_by('name'),
        'fund_source': FundSource.objects.filter(status=1).order_by('name')
    }
    return render(request, 'management/view_transaction.html', context)


@login_required
def case_record_uploading(request, pk):
    if request.method == "POST":
        file = request.FILES.getlist('file[]')
        file_type = request.POST.getlist('file_type[]')
        if not file == [''] and not file_type == ['']:
            files = [
                {'file': f, 'id': i}
                for f, i in zip(file, file_type)
            ]

            for row in files:
                TransactionFiles.objects.create(
                    transaction_id=pk,
                    file=row['file'],
                    file_type_id=row['id'],
                    status=0
                )
        return JsonResponse({'data': 'success', 'msg': 'You have successfully uploaded case record file(s).'})