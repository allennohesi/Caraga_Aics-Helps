from django.contrib.auth import authenticate,logout, login as auth_login
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.http import JsonResponse
from django.shortcuts import render, redirect
from app.requests.models import SocialWorker_Status, TransactionStatus1
from app.models import AuthUser, AuthUserGroups, AuthGroup
from django.db.models import Value, Sum, Count
from datetime import date
from app.libraries.models import Category

import xlwt
from django.http import HttpResponse
from openpyxl import Workbook
from datetime import datetime
currentDateAndTime = datetime.now()
from openpyxl.writer.excel import save_virtual_workbook
from openpyxl.styles import Font, PatternFill


today = date.today()
month = today.strftime("%m")
year = today.strftime("%Y")

def landingpage(request):
    context = {
        'title': 'Home'
    }
    return render(request, 'landingpage.html', context)


def login(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'), request=request)
        if user is not None and user.is_active:
            auth_login(request, user)
            return JsonResponse({'data': 'success'})
        else:
            return JsonResponse({'msg': 'Invalid username and password.'})
    return render(request, 'login.html') 

def log_out(request):
    logout(request)
    request.session.flush()  # Clear session data
    return redirect('login')


def media_access(request, path):    
    return render(request, '404.html')

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dashboard(request):
    am = AuthUserGroups.objects.all().filter(group_id=3).count() #adminCount
    swo = AuthUserGroups.objects.all().filter(group_id=2).count() #SwoCount
    sp = AuthUserGroups.objects.all().filter(group_id=4).count() #ServiceProvider
    vr = AuthUserGroups.objects.all().filter(group_id=1).count() #verifier

    active_emp = AuthUser.objects.filter(is_active=1).count()
    inactive_emp = AuthUser.objects.filter(is_active=0).count()

    active_emp = AuthUser.objects.filter(is_active=1).count()

    fa = TransactionStatus1.objects.filter(transaction_id__lib_type_of_assistance_id__type_name="Financial Assistance").count()
    ma = TransactionStatus1.objects.filter(transaction_id__lib_type_of_assistance_id__type_name="Material Assistance").count()
    psych = TransactionStatus1.objects.filter(transaction_id__lib_type_of_assistance_id__type_name="Psychosocial").count()

    pending = TransactionStatus1.objects.filter(status=1).count()
    ongoing = TransactionStatus1.objects.filter(status=2).count()
    completed = TransactionStatus1.objects.filter(status=6).count()
    hold = TransactionStatus1.objects.filter(status=4).count()
    cancelled = TransactionStatus1.objects.filter(status=5).count()
    
    countingHotmeal = AuthUserGroups.objects.filter(group_id=2).order_by('id')


    context = {
        'title': 'Home',
        'am':am,
        'swo':swo,
        'sp':sp,
        'vr':vr,
        'active_emp':active_emp,
        'inactive_emp':inactive_emp,

        'financial': fa,
        'material': ma,
        'psychological':psych,

        'pending':pending,
        'ongoing':ongoing,
        'completed':completed,
        'hold':hold,
        'cancelled':cancelled,
        'countingHotmeal':countingHotmeal,

    }
    return render(request, 'home.html', context)

@login_required
def status_activation(request,pk):
    if request.method == "POST":
        user = pk
        status = request.POST.get('status')
        date = request.POST.get('date')

        filter = SocialWorker_Status.objects.filter(user_id=pk).first()
        if filter:
            SocialWorker_Status.objects.filter(user_id__id=pk).update(
                status=status,
                date_transaction=date
            )
            return JsonResponse({'data': 'success', 'msg': 'You are now active.'})
        else:

            SocialWorker_Status.objects.create(
                user_id=user,
                status=status,
                date_transaction=date
            )          
            return JsonResponse({'data': 'success', 'msg': 'Action completed.'})


@login_required
def mail(request):
    return render(request, 'mail.html')


@login_required
def layout_404(request):
    return render(request, '404.html')


@login_required
def print_ProvidedBYSWO(request):
    context = {
        'countingHotmeal':AuthUserGroups.objects.filter(group_id=2).order_by('id')
    }
    return render(request, 'provided_swo.html', context)

def generateTransactions(request):
    from openpyxl.styles import NamedStyle
    today = datetime.today()
    year = today.strftime("%Y")
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'USER AVAIL ' + year
    wsrow = 2

    
    blue = PatternFill(start_color='92D4F0',
                    end_color='92D4F0',
                    fill_type='solid')

    worksheet['A1'] = 'Code'
    worksheet['B1'] = 'PCN'
    worksheet['C1'] = 'Time of Transaction'
    worksheet['D1'] = 'Date of Transaction'

    worksheet['A1'].fill = blue
    worksheet['B1'].fill = blue
    worksheet['C1'].fill = blue
    worksheet['D1'].fill = blue

    darkblue = PatternFill(start_color='AAC4F2',
                    end_color='AAC4F2',
                    fill_type='solid')

    worksheet['E1'] = 'BENE LAST NAME'
    worksheet['F1'] = 'BENE FIRST NAME'
    worksheet['G1'] = 'BENE MIDDLE NAME'
    worksheet['H1'] = 'BENE EXT'
    worksheet['I1'] = 'BENE BIRTH DATE'
    worksheet['J1'] = 'BENE PUROK'
    worksheet['K1'] = 'BENE BARANGAY'
    worksheet['L1'] = 'BENE MUNICIPALITY'
    worksheet['M1'] = 'BENE DISTRICT'
    worksheet['N1'] = 'BENE PROVINCE'
    worksheet['O1'] = 'BENE REGION'
    worksheet['P1'] = 'BENE CONTACT NUMBER'
    worksheet['Q1'] = 'BENE SEX'
    worksheet['R1'] = 'BENE OCCUPATION'
    worksheet['S1'] = 'BENE MONTHLY INCOME'

    worksheet['E1'].fill = darkblue
    worksheet['F1'].fill = darkblue
    worksheet['G1'].fill = darkblue
    worksheet['H1'].fill = darkblue
    worksheet['I1'].fill = darkblue
    worksheet['J1'].fill = darkblue
    worksheet['K1'].fill = darkblue
    worksheet['L1'].fill = darkblue
    worksheet['M1'].fill = darkblue
    worksheet['N1'].fill = darkblue
    worksheet['O1'].fill = darkblue
    worksheet['P1'].fill = darkblue
    worksheet['Q1'].fill = darkblue
    worksheet['R1'].fill = darkblue
    worksheet['S1'].fill = darkblue

    worksheet['T1'] = 'ADDRESS'
    worksheet['U1'] = 'CLIENTS RELATIONSHIP TO BENE'
    worksheet['V1'] = 'ID PRESENTED'
    worksheet['W1'] = 'TYPE OF ASSISTANCE'
    worksheet['X1'] = 'PURPOSE'
    worksheet['Y1'] = 'AMOUNT'
    worksheet['AA1'] = 'FUND SOURCE'
    worksheet['BB2'] = 'SERVICE PROVIDER'

    worksheet['CC3'] = 'CLIENT DISTRICT'
    worksheet['DD4'] = 'CLIENT PROVINCE'
    worksheet['EE5'] = 'CLIENT REGION'
    worksheet['FF6'] = 'CLIENT SEX'
    worksheet['GG7'] = 'CLIENT OCCUPATION'
    worksheet['HH8'] = 'CLIENT INCOME'





    worksheet['A1'].font = Font(bold=True)
    worksheet['B1'].font = Font(bold=True)
    worksheet['C1'].font = Font(bold=True)
    worksheet['D1'].font = Font(bold=True)
    worksheet['E1'].font = Font(bold=True)
    worksheet['F1'].font = Font(bold=True)
    worksheet['G1'].font = Font(bold=True)
    worksheet['H1'].font = Font(bold=True)
    worksheet['I1'].font = Font(bold=True)
    worksheet['J1'].font = Font(bold=True)
    worksheet['K1'].font = Font(bold=True)
    worksheet['L1'].font = Font(bold=True)
    worksheet['M1'].font = Font(bold=True)
    worksheet['N1'].font = Font(bold=True)
    worksheet['O1'].font = Font(bold=True)
    worksheet['P1'].font = Font(bold=True)
    worksheet['Q1'].font = Font(bold=True)
    worksheet['R1'].font = Font(bold=True)
    worksheet['S1'].font = Font(bold=True)
    worksheet['T1'].font = Font(bold=True)
    worksheet['U1'].font = Font(bold=True)
    worksheet['V1'].font = Font(bold=True)
    worksheet['W1'].font = Font(bold=True)
    worksheet['X1'].font = Font(bold=True)
    worksheet['Y1'].font = Font(bold=True)
    worksheet['Z1'].font = Font(bold=True)

    
    transaction = TransactionStatus1.objects.filter(status=6).values('transaction__tracking_number','verified_time_start','transaction__bene__last_name','transaction__bene__first_name', \
        'transaction__bene__middle_name', 'transaction__bene__contact_number','transaction__bene__suffix__name','transaction__bene__birthdate','transaction__bene__street','transaction__bene__house_no', 'transaction__bene__barangay__brgy_name', \
            'transaction__bene__barangay__city_code__city_name', 'transaction__bene__barangay__city_code__prov_code__prov_name','transaction__bene__barangay__city_code__prov_code__region_code__region_name', \
                'transaction__bene__occupation__occupation_name','transaction__bene__salary','transaction__bene__sex__name', 'transaction__client__last_name','transaction__client__first_name', \
                    'transaction__client__middle_name','transaction__client__suffix__name','transaction__client__birthdate','transaction__client__street','transaction__client__house_no', 'transaction__client__barangay__brgy_name', \
                        'transaction__client__barangay__city_code__city_name', 'transaction__client__barangay__city_code__prov_code__prov_name','transaction__client__barangay__city_code__prov_code__region_code__region_name', \
                            'transaction__client__occupation__occupation_name','transaction__client__salary','transaction__client__sex__name','upload_time_end','transaction__relation__name')
    if transaction:
        for indx, row in enumerate(transaction):
            dateoftransaction = row['verified_time_start'].strftime("%I:%M %p")
            transactionDate = row['verified_time_start'].strftime("%B %d, %Y")
            birth_date = row['transaction__bene__birthdate'].strftime("%B %d, %Y")

            client_birth_date = row['transaction__client__birthdate'].strftime("%B %d, %Y")

            worksheet['A' + str(wsrow)] = row['transaction__tracking_number']
            worksheet['B' + str(wsrow)] = "00000000000000"
            worksheet['C' + str(wsrow)] = dateoftransaction
            worksheet['D' + str(wsrow)] = transactionDate
            worksheet['E' + str(wsrow)] = row['transaction__bene__last_name']
            worksheet['F' + str(wsrow)] = row['transaction__bene__first_name']
            worksheet['G' + str(wsrow)] = row['transaction__bene__middle_name']
            worksheet['H' + str(wsrow)] = row['transaction__bene__suffix__name']
            worksheet['I' + str(wsrow)] = birth_date
            worksheet['J' + str(wsrow)] = row['transaction__bene__house_no']
            worksheet['K' + str(wsrow)] = row['transaction__bene__barangay__brgy_name']
            worksheet['L' + str(wsrow)] = row['transaction__bene__barangay__city_code__city_name']
            worksheet['M' + str(wsrow)] = row['transaction__bene__street']
            worksheet['N' + str(wsrow)] = row['transaction__bene__barangay__city_code__prov_code__prov_name']
            worksheet['O' + str(wsrow)] = row['transaction__bene__barangay__city_code__prov_code__region_code__region_name']
            worksheet['P' + str(wsrow)] = row['transaction__bene__contact_number']
            worksheet['Q' + str(wsrow)] = row['transaction__bene__sex__name']
            worksheet['R' + str(wsrow)] = row['transaction__bene__occupation__occupation_name']
            worksheet['S' + str(wsrow)] = row['transaction__bene__salary']

            worksheet['T' + str(wsrow)] = row['transaction__bene__house_no'] + ", " + row['transaction__bene__barangay__brgy_name'] + ", " + row['transaction__bene__barangay__city_code__city_name'] + " " + row['transaction__bene__barangay__city_code__prov_code__prov_name'] + " " + row['transaction__bene__barangay__city_code__prov_code__region_code__region_name']
            worksheet['U' + str(wsrow)] = row['transaction__relation__name']
            worksheet['V' + str(wsrow)] = row['transaction__client__middle_name']
            worksheet['W' + str(wsrow)] = row['transaction__client__middle_name']
            worksheet['X' + str(wsrow)] = row['transaction__client__middle_name']
            worksheet['Y' + str(wsrow)] = row['transaction__client__middle_name']
            worksheet['Z' + str(wsrow)] = row['transaction__client__middle_name']
            worksheet['AA' + str(wsrow)] = row['transaction__client__barangay__city_code__prov_code__prov_name']
            


            wsrow = wsrow + 1
        response = HttpResponse(content=save_virtual_workbook(workbook), content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=All Transactions' + ' (' + year + ').xlsx'
        return response
    else:
        return render(request, '404.html')


def generate_testXLS(request,pk):
    from openpyxl.styles import NamedStyle
    today = datetime.today()
    year = today.strftime("%Y")
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'USER AVAIL ' + year
    wsrow = 2

    
    blue = PatternFill(start_color='92D4F0',
                    end_color='92D4F0',
                    fill_type='solid')

    worksheet['A1'] = 'Transaction No'
    worksheet['B1'] = 'Time of Transaction'
    worksheet['C1'] = 'Date of Transaction'

    worksheet['A1'].fill = blue
    worksheet['B1'].fill = blue
    worksheet['C1'].fill = blue

    darkblue = PatternFill(start_color='AAC4F2',
                    end_color='AAC4F2',
                    fill_type='solid')

    worksheet['D1'] = 'BENE LAST NAME'
    worksheet['E1'] = 'BENE FIRST NAME'
    worksheet['F1'] = 'BENE MIDDLE NAME'
    worksheet['G1'] = 'BENE EXT'
    worksheet['H1'] = 'BENE BIRTH DATE'
    worksheet['I1'] = 'BENE PUROK'
    worksheet['J1'] = 'BENE BARANGAY'
    worksheet['K1'] = 'BENE MUNICIPALITY'
    worksheet['L1'] = 'BENE DISTRICT'
    worksheet['M1'] = 'BENE PROVINCE'
    worksheet['N1'] = 'BENE REGION'
    worksheet['O1'] = 'BENE SEX'
    worksheet['P1'] = 'BENE OCCUPATION'
    worksheet['Q1'] = 'BENE INCOME'
    worksheet['R1'] = 'BENE INCOME'
    worksheet['S1'] = 'BENE OCCUPATION'

    worksheet['T1'] = 'CLIENT LAST NAME'
    worksheet['U1'] = 'CLIENT FIRST NAME'
    worksheet['V1'] = 'CLIENT MIDDLE NAME'
    worksheet['W1'] = 'CLIENT EXT'
    worksheet['X1'] = 'CLIENT BIRTH DATE'
    worksheet['Y1'] = 'CLIENT PUROK'
    worksheet['Z1'] = 'CLIENT BARANGAY'
    worksheet['AA1'] = 'CLIENT MUNICIPALITY'
    worksheet['BB1'] = 'CLIENT DISTRICT'
    worksheet['CC1'] = 'CLIENT PROVINCE'
    worksheet['DD1'] = 'CLIENT REGION'
    worksheet['EE1'] = 'CLIENT SEX'
    worksheet['FF1'] = 'CLIENT OCCUPATION'
    worksheet['GG1'] = 'CLIENT INCOME'


    worksheet['D1'].fill = darkblue
    worksheet['E1'].fill = darkblue
    worksheet['F1'].fill = darkblue
    worksheet['G1'].fill = darkblue
    worksheet['H1'].fill = darkblue
    worksheet['I1'].fill = darkblue
    worksheet['J1'].fill = darkblue
    worksheet['K1'].fill = darkblue
    worksheet['L1'].fill = darkblue
    worksheet['M1'].fill = darkblue
    worksheet['N1'].fill = darkblue
    worksheet['O1'].fill = darkblue
    worksheet['P1'].fill = darkblue
    worksheet['Q1'].fill = darkblue

    worksheet['A1'].font = Font(bold=True)
    worksheet['B1'].font = Font(bold=True)
    worksheet['C1'].font = Font(bold=True)
    worksheet['D1'].font = Font(bold=True)
    worksheet['E1'].font = Font(bold=True)
    worksheet['F1'].font = Font(bold=True)
    worksheet['G1'].font = Font(bold=True)
    worksheet['H1'].font = Font(bold=True)
    worksheet['I1'].font = Font(bold=True)
    worksheet['J1'].font = Font(bold=True)
    worksheet['K1'].font = Font(bold=True)
    worksheet['L1'].font = Font(bold=True)
    worksheet['M1'].font = Font(bold=True)
    worksheet['N1'].font = Font(bold=True)
    worksheet['O1'].font = Font(bold=True)
    worksheet['P1'].font = Font(bold=True)
    worksheet['Q1'].font = Font(bold=True)
    worksheet['R1'].font = Font(bold=True)
    worksheet['S1'].font = Font(bold=True)
    worksheet['T1'].font = Font(bold=True)
    worksheet['U1'].font = Font(bold=True)
    worksheet['V1'].font = Font(bold=True)
    worksheet['W1'].font = Font(bold=True)
    worksheet['X1'].font = Font(bold=True)
    worksheet['Y1'].font = Font(bold=True)
    worksheet['Z1'].font = Font(bold=True)

    
    transaction = TransactionStatus1.objects.filter(status=6,transaction__swo_id=pk).values('transaction__tracking_number','verified_time_start','transaction__bene__last_name','transaction__bene__first_name', \
        'transaction__bene__middle_name','transaction__bene__suffix__name','transaction__bene__birthdate','transaction__bene__street','transaction__bene__house_no', 'transaction__bene__barangay__brgy_name', \
            'transaction__bene__barangay__city_code__city_name', 'transaction__bene__barangay__city_code__prov_code__prov_name','transaction__bene__barangay__city_code__prov_code__region_code__region_name', \
                'transaction__bene__occupation__occupation_name','transaction__bene__salary','transaction__bene__sex__name', 'transaction__client__last_name','transaction__client__first_name', \
                    'transaction__client__middle_name','transaction__client__suffix__name','transaction__client__birthdate','transaction__client__street','transaction__client__house_no', 'transaction__client__barangay__brgy_name', \
                        'transaction__client__barangay__city_code__city_name', 'transaction__client__barangay__city_code__prov_code__prov_name','transaction__client__barangay__city_code__prov_code__region_code__region_name', \
                            'transaction__client__occupation__occupation_name','transaction__client__salary','transaction__client__sex__name','upload_time_end')
    if transaction:
        for indx, row in enumerate(transaction):
            print("START", row['verified_time_start'].strftime("%I:%M %p"))
            print("END", row['upload_time_end'].strftime("%I:%M %p"))
            dateoftransaction = row['verified_time_start'].strftime("%I:%M %p")
            transactionDate = row['verified_time_start'].strftime("%B %d, %Y")
            birth_date = row['transaction__bene__birthdate'].strftime("%B %d, %Y")

            client_birth_date = row['transaction__client__birthdate'].strftime("%B %d, %Y")

            worksheet['A' + str(wsrow)] = row['transaction__tracking_number']
            worksheet['B' + str(wsrow)] = dateoftransaction
            worksheet['C' + str(wsrow)] = transactionDate
            worksheet['D' + str(wsrow)] = row['transaction__bene__last_name']
            worksheet['E' + str(wsrow)] = row['transaction__bene__first_name']
            worksheet['F' + str(wsrow)] = row['transaction__bene__middle_name']
            worksheet['G' + str(wsrow)] = row['transaction__bene__suffix__name']
            worksheet['H' + str(wsrow)] = birth_date
            worksheet['I' + str(wsrow)] = row['transaction__bene__house_no']
            worksheet['J' + str(wsrow)] = row['transaction__bene__barangay__brgy_name']
            worksheet['K' + str(wsrow)] = row['transaction__bene__barangay__city_code__city_name']
            worksheet['L' + str(wsrow)] = row['transaction__bene__street']
            worksheet['M' + str(wsrow)] = row['transaction__bene__barangay__city_code__prov_code__prov_name']
            worksheet['N' + str(wsrow)] = row['transaction__bene__barangay__city_code__prov_code__region_code__region_name']
            worksheet['O' + str(wsrow)] = row['transaction__bene__sex__name']
            worksheet['P' + str(wsrow)] = row['transaction__bene__occupation__occupation_name']
            worksheet['Q' + str(wsrow)] = row['transaction__bene__salary']

            worksheet['R' + str(wsrow)] = row['transaction__client__last_name']
            worksheet['S' + str(wsrow)] = row['transaction__client__first_name']           
            worksheet['T' + str(wsrow)] = row['transaction__client__middle_name']
            worksheet['U' + str(wsrow)] = row['transaction__client__suffix__name']
            worksheet['V' + str(wsrow)] = client_birth_date
            worksheet['W' + str(wsrow)] = row['transaction__client__house_no']
            worksheet['X' + str(wsrow)] = row['transaction__client__barangay__brgy_name']
            worksheet['Y' + str(wsrow)] = row['transaction__client__barangay__city_code__city_name']
            worksheet['Z' + str(wsrow)] = row['transaction__client__street']
            worksheet['AA' + str(wsrow)] = row['transaction__client__barangay__city_code__prov_code__prov_name']
            worksheet['BB' + str(wsrow)] = row['transaction__client__barangay__city_code__prov_code__region_code__region_name']
            worksheet['CC' + str(wsrow)] = row['transaction__client__sex__name']
            worksheet['DD' + str(wsrow)] = row['transaction__client__occupation__occupation_name']
            worksheet['EE' + str(wsrow)] = row['transaction__client__salary']

            wsrow = wsrow + 1
        response = HttpResponse(content=save_virtual_workbook(workbook), content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=Personal User Transaction' + ' (' + year + ').xlsx'
        return response
    else:
        return render(request, '404.html')

@login_required
def generateByUser(request):
    if request.method == "POST":
        clientCategory = request.POST.get('clientCategory')
        clientCategoryCheckbox = request.POST.get('Client_category_checkbox')
        service_provider = request.POST.get('service_provider')
    
        today = datetime.today()
        year = today.strftime("%Y")
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = 'USER AVAIL ' + year
        wsrow = 2

        blue = PatternFill(start_color='92D4F0',
                        end_color='92D4F0',
                        fill_type='solid')

        worksheet['A1'] = 'Transaction No'
        worksheet['B1'] = 'Time of Transaction'
        worksheet['C1'] = 'Date of Transaction'

        worksheet['A1'].fill = blue
        worksheet['B1'].fill = blue
        worksheet['C1'].fill = blue

        darkblue = PatternFill(start_color='AAC4F2',
                        end_color='AAC4F2',
                        fill_type='solid')

        worksheet['D1'] = 'BENE LAST NAME'
        worksheet['E1'] = 'BENE FIRST NAME'
        worksheet['F1'] = 'BENE MIDDLE NAME'
        worksheet['G1'] = 'BENE EXT'
        worksheet['H1'] = 'BENE BIRTH DATE'
        worksheet['I1'] = 'BENE PUROK'
        worksheet['J1'] = 'BENE BARANGAY'
        worksheet['K1'] = 'BENE MUNICIPALITY'
        worksheet['L1'] = 'BENE DISTRICT'
        worksheet['M1'] = 'BENE PROVINCE'
        worksheet['N1'] = 'BENE REGION'
        worksheet['O1'] = 'BENE SEX'
        worksheet['P1'] = 'BENE OCCUPATION'
        worksheet['Q1'] = 'BENE INCOME'
        worksheet['R1'] = 'BENE INCOME'
        worksheet['S1'] = 'BENE OCCUPATION'

        worksheet['T1'] = 'CLIENT LAST NAME'
        worksheet['U1'] = 'CLIENT FIRST NAME'
        worksheet['V1'] = 'CLIENT MIDDLE NAME'
        worksheet['W1'] = 'CLIENT EXT'
        worksheet['X1'] = 'CLIENT BIRTH DATE'
        worksheet['Y1'] = 'CLIENT PUROK'
        worksheet['Z1'] = 'CLIENT BARANGAY'
        worksheet['AA1'] = 'CLIENT MUNICIPALITY'
        worksheet['BB1'] = 'CLIENT DISTRICT'
        worksheet['CC1'] = 'CLIENT PROVINCE'
        worksheet['DD1'] = 'CLIENT REGION'
        worksheet['EE1'] = 'CLIENT SEX'
        worksheet['FF1'] = 'CLIENT OCCUPATION'
        worksheet['GG1'] = 'CLIENT INCOME'


        worksheet['D1'].fill = darkblue
        worksheet['E1'].fill = darkblue
        worksheet['F1'].fill = darkblue
        worksheet['G1'].fill = darkblue
        worksheet['H1'].fill = darkblue
        worksheet['I1'].fill = darkblue
        worksheet['J1'].fill = darkblue
        worksheet['K1'].fill = darkblue
        worksheet['L1'].fill = darkblue
        worksheet['M1'].fill = darkblue
        worksheet['N1'].fill = darkblue
        worksheet['O1'].fill = darkblue
        worksheet['P1'].fill = darkblue
        worksheet['Q1'].fill = darkblue

        worksheet['A1'].font = Font(bold=True)
        worksheet['B1'].font = Font(bold=True)
        worksheet['C1'].font = Font(bold=True)
        worksheet['D1'].font = Font(bold=True)
        worksheet['E1'].font = Font(bold=True)
        worksheet['F1'].font = Font(bold=True)
        worksheet['G1'].font = Font(bold=True)
        worksheet['H1'].font = Font(bold=True)
        worksheet['I1'].font = Font(bold=True)
        worksheet['J1'].font = Font(bold=True)
        worksheet['K1'].font = Font(bold=True)
        worksheet['L1'].font = Font(bold=True)
        worksheet['M1'].font = Font(bold=True)
        worksheet['N1'].font = Font(bold=True)
        worksheet['O1'].font = Font(bold=True)
        worksheet['P1'].font = Font(bold=True)
        worksheet['Q1'].font = Font(bold=True)
        worksheet['R1'].font = Font(bold=True)
        worksheet['S1'].font = Font(bold=True)
        worksheet['T1'].font = Font(bold=True)
        worksheet['U1'].font = Font(bold=True)
        worksheet['V1'].font = Font(bold=True)
        worksheet['W1'].font = Font(bold=True)
        worksheet['X1'].font = Font(bold=True)
        worksheet['Y1'].font = Font(bold=True)
        worksheet['Z1'].font = Font(bold=True)

        if clientCategoryCheckbox == "Client_category":
            transaction = TransactionStatus1.objects.filter(status=6,transaction__client_category_id=clientCategory).values('transaction__tracking_number','verified_time_start','transaction__bene__last_name','transaction__bene__first_name', \
                'transaction__bene__middle_name','transaction__bene__suffix__name','transaction__bene__birthdate','transaction__bene__street','transaction__bene__house_no', 'transaction__bene__barangay__brgy_name', \
                    'transaction__bene__barangay__city_code__city_name', 'transaction__bene__barangay__city_code__prov_code__prov_name','transaction__bene__barangay__city_code__prov_code__region_code__region_name', \
                        'transaction__bene__occupation__occupation_name','transaction__bene__salary','transaction__bene__sex__name', 'transaction__client__last_name','transaction__client__first_name', \
                            'transaction__client__middle_name','transaction__client__suffix__name','transaction__client__birthdate','transaction__client__street','transaction__client__house_no', 'transaction__client__barangay__brgy_name', \
                                'transaction__client__barangay__city_code__city_name', 'transaction__client__barangay__city_code__prov_code__prov_name','transaction__client__barangay__city_code__prov_code__region_code__region_name', \
                                    'transaction__client__occupation__occupation_name','transaction__client__salary','transaction__client__sex__name')
            if transaction:
                for indx, row in enumerate(transaction):
                    dateoftransaction = row['verified_time_start'].strftime("%H:%M %p")
                    transactionDate = row['verified_time_start'].strftime("%B %d, %Y")
                    birth_date = row['transaction__bene__birthdate'].strftime("%B %d, %Y")

                    client_birth_date = row['transaction__client__birthdate'].strftime("%B %d, %Y")

                    worksheet['A' + str(wsrow)] = row['transaction__tracking_number']
                    worksheet['B' + str(wsrow)] = dateoftransaction
                    worksheet['C' + str(wsrow)] = transactionDate
                    worksheet['D' + str(wsrow)] = row['transaction__bene__last_name']
                    worksheet['E' + str(wsrow)] = row['transaction__bene__first_name']
                    worksheet['F' + str(wsrow)] = row['transaction__bene__middle_name']
                    worksheet['G' + str(wsrow)] = row['transaction__bene__suffix__name']
                    worksheet['H' + str(wsrow)] = birth_date
                    worksheet['I' + str(wsrow)] = row['transaction__bene__house_no']
                    worksheet['J' + str(wsrow)] = row['transaction__bene__barangay__brgy_name']
                    worksheet['K' + str(wsrow)] = row['transaction__bene__barangay__city_code__city_name']
                    worksheet['L' + str(wsrow)] = row['transaction__bene__street']
                    worksheet['M' + str(wsrow)] = row['transaction__bene__barangay__city_code__prov_code__prov_name']
                    worksheet['N' + str(wsrow)] = row['transaction__bene__barangay__city_code__prov_code__region_code__region_name']
                    worksheet['O' + str(wsrow)] = row['transaction__bene__sex__name']
                    worksheet['P' + str(wsrow)] = row['transaction__bene__occupation__occupation_name']
                    worksheet['Q' + str(wsrow)] = row['transaction__bene__salary']

                    worksheet['R' + str(wsrow)] = row['transaction__client__last_name']
                    worksheet['S' + str(wsrow)] = row['transaction__client__first_name']           
                    worksheet['T' + str(wsrow)] = row['transaction__client__middle_name']
                    worksheet['U' + str(wsrow)] = row['transaction__client__suffix__name']
                    worksheet['V' + str(wsrow)] = client_birth_date
                    worksheet['W' + str(wsrow)] = row['transaction__client__house_no']
                    worksheet['X' + str(wsrow)] = row['transaction__client__barangay__brgy_name']
                    worksheet['Y' + str(wsrow)] = row['transaction__client__barangay__city_code__city_name']
                    worksheet['Z' + str(wsrow)] = row['transaction__client__street']
                    worksheet['AA' + str(wsrow)] = row['transaction__client__barangay__city_code__prov_code__prov_name']
                    worksheet['BB' + str(wsrow)] = row['transaction__client__barangay__city_code__prov_code__region_code__region_name']
                    worksheet['CC' + str(wsrow)] = row['transaction__client__sex__name']
                    worksheet['DD' + str(wsrow)] = row['transaction__client__occupation__occupation_name']
                    worksheet['EE' + str(wsrow)] = row['transaction__client__salary']

                    wsrow = wsrow + 1
                response = HttpResponse(content=save_virtual_workbook(workbook), content_type='application/ms-excel')
                response['Content-Disposition'] = 'attachment; filename=Client Category' + ' (' + year + ').xlsx'
                return response
            else:
                return render(request, '404.html')
        elif clientCategoryCheckbox == "Sex":
            sex_disagregated = request.POST.get('sex_disagregated')
            if sex_disagregated == "male":
                transaction = TransactionStatus1.objects.filter(status=6,transaction__client__sex__name=sex_disagregated).values('transaction__tracking_number','verified_time_start','transaction__bene__last_name','transaction__bene__first_name', \
                    'transaction__bene__middle_name','transaction__bene__suffix__name','transaction__bene__birthdate','transaction__bene__street','transaction__bene__house_no', 'transaction__bene__barangay__brgy_name', \
                        'transaction__bene__barangay__city_code__city_name', 'transaction__bene__barangay__city_code__prov_code__prov_name','transaction__bene__barangay__city_code__prov_code__region_code__region_name', \
                            'transaction__bene__occupation__occupation_name','transaction__bene__salary','transaction__bene__sex__name', 'transaction__client__last_name','transaction__client__first_name', \
                                'transaction__client__middle_name','transaction__client__suffix__name','transaction__client__birthdate','transaction__client__street','transaction__client__house_no', 'transaction__client__barangay__brgy_name', \
                                    'transaction__client__barangay__city_code__city_name', 'transaction__client__barangay__city_code__prov_code__prov_name','transaction__client__barangay__city_code__prov_code__region_code__region_name', \
                                        'transaction__client__occupation__occupation_name','transaction__client__salary','transaction__client__sex__name')
                if transaction:
                    for indx, row in enumerate(transaction):
                        dateoftransaction = row['verified_time_start'].strftime("%H:%M %p")
                        transactionDate = row['verified_time_start'].strftime("%B %d, %Y")
                        birth_date = row['transaction__bene__birthdate'].strftime("%B %d, %Y")

                        client_birth_date = row['transaction__client__birthdate'].strftime("%B %d, %Y")

                        worksheet['A' + str(wsrow)] = row['transaction__tracking_number']
                        worksheet['B' + str(wsrow)] = dateoftransaction
                        worksheet['C' + str(wsrow)] = transactionDate
                        worksheet['D' + str(wsrow)] = row['transaction__bene__last_name']
                        worksheet['E' + str(wsrow)] = row['transaction__bene__first_name']
                        worksheet['F' + str(wsrow)] = row['transaction__bene__middle_name']
                        worksheet['G' + str(wsrow)] = row['transaction__bene__suffix__name']
                        worksheet['H' + str(wsrow)] = birth_date
                        worksheet['I' + str(wsrow)] = row['transaction__bene__house_no']
                        worksheet['J' + str(wsrow)] = row['transaction__bene__barangay__brgy_name']
                        worksheet['K' + str(wsrow)] = row['transaction__bene__barangay__city_code__city_name']
                        worksheet['L' + str(wsrow)] = row['transaction__bene__street']
                        worksheet['M' + str(wsrow)] = row['transaction__bene__barangay__city_code__prov_code__prov_name']
                        worksheet['N' + str(wsrow)] = row['transaction__bene__barangay__city_code__prov_code__region_code__region_name']
                        worksheet['O' + str(wsrow)] = row['transaction__bene__sex__name']
                        worksheet['P' + str(wsrow)] = row['transaction__bene__occupation__occupation_name']
                        worksheet['Q' + str(wsrow)] = row['transaction__bene__salary']

                        worksheet['R' + str(wsrow)] = row['transaction__client__last_name']
                        worksheet['S' + str(wsrow)] = row['transaction__client__first_name']           
                        worksheet['T' + str(wsrow)] = row['transaction__client__middle_name']
                        worksheet['U' + str(wsrow)] = row['transaction__client__suffix__name']
                        worksheet['V' + str(wsrow)] = client_birth_date
                        worksheet['W' + str(wsrow)] = row['transaction__client__house_no']
                        worksheet['X' + str(wsrow)] = row['transaction__client__barangay__brgy_name']
                        worksheet['Y' + str(wsrow)] = row['transaction__client__barangay__city_code__city_name']
                        worksheet['Z' + str(wsrow)] = row['transaction__client__street']
                        worksheet['AA' + str(wsrow)] = row['transaction__client__barangay__city_code__prov_code__prov_name']
                        worksheet['BB' + str(wsrow)] = row['transaction__client__barangay__city_code__prov_code__region_code__region_name']
                        worksheet['CC' + str(wsrow)] = row['transaction__client__sex__name']
                        worksheet['DD' + str(wsrow)] = row['transaction__client__occupation__occupation_name']
                        worksheet['EE' + str(wsrow)] = row['transaction__client__salary']

                        wsrow = wsrow + 1
                    response = HttpResponse(content=save_virtual_workbook(workbook), content_type='application/ms-excel')
                    response['Content-Disposition'] = 'attachment; filename=Sex disaggregated data (MALE ONLY)' + ' (' + year + ').xlsx'
                    return response
                else:
                    return render(request, '404.html')
            elif sex_disagregated == "female":
                transaction = TransactionStatus1.objects.filter(status=6,transaction__client__sex__name=sex_disagregated).values('transaction__tracking_number','verified_time_start','transaction__bene__last_name','transaction__bene__first_name', \
                    'transaction__bene__middle_name','transaction__bene__suffix__name','transaction__bene__birthdate','transaction__bene__street','transaction__bene__house_no', 'transaction__bene__barangay__brgy_name', \
                        'transaction__bene__barangay__city_code__city_name', 'transaction__bene__barangay__city_code__prov_code__prov_name','transaction__bene__barangay__city_code__prov_code__region_code__region_name', \
                            'transaction__bene__occupation__occupation_name','transaction__bene__salary','transaction__bene__sex__name', 'transaction__client__last_name','transaction__client__first_name', \
                                'transaction__client__middle_name','transaction__client__suffix__name','transaction__client__birthdate','transaction__client__street','transaction__client__house_no', 'transaction__client__barangay__brgy_name', \
                                    'transaction__client__barangay__city_code__city_name', 'transaction__client__barangay__city_code__prov_code__prov_name','transaction__client__barangay__city_code__prov_code__region_code__region_name', \
                                        'transaction__client__occupation__occupation_name','transaction__client__salary','transaction__client__sex__name')
                if transaction:
                    for indx, row in enumerate(transaction):
                        dateoftransaction = row['verified_time_start'].strftime("%H:%M %p")
                        transactionDate = row['verified_time_start'].strftime("%B %d, %Y")
                        birth_date = row['transaction__bene__birthdate'].strftime("%B %d, %Y")

                        client_birth_date = row['transaction__client__birthdate'].strftime("%B %d, %Y")

                        worksheet['A' + str(wsrow)] = row['transaction__tracking_number']
                        worksheet['B' + str(wsrow)] = dateoftransaction
                        worksheet['C' + str(wsrow)] = transactionDate
                        worksheet['D' + str(wsrow)] = row['transaction__bene__last_name']
                        worksheet['E' + str(wsrow)] = row['transaction__bene__first_name']
                        worksheet['F' + str(wsrow)] = row['transaction__bene__middle_name']
                        worksheet['G' + str(wsrow)] = row['transaction__bene__suffix__name']
                        worksheet['H' + str(wsrow)] = birth_date
                        worksheet['I' + str(wsrow)] = row['transaction__bene__house_no']
                        worksheet['J' + str(wsrow)] = row['transaction__bene__barangay__brgy_name']
                        worksheet['K' + str(wsrow)] = row['transaction__bene__barangay__city_code__city_name']
                        worksheet['L' + str(wsrow)] = row['transaction__bene__street']
                        worksheet['M' + str(wsrow)] = row['transaction__bene__barangay__city_code__prov_code__prov_name']
                        worksheet['N' + str(wsrow)] = row['transaction__bene__barangay__city_code__prov_code__region_code__region_name']
                        worksheet['O' + str(wsrow)] = row['transaction__bene__sex__name']
                        worksheet['P' + str(wsrow)] = row['transaction__bene__occupation__occupation_name']
                        worksheet['Q' + str(wsrow)] = row['transaction__bene__salary']

                        worksheet['R' + str(wsrow)] = row['transaction__client__last_name']
                        worksheet['S' + str(wsrow)] = row['transaction__client__first_name']           
                        worksheet['T' + str(wsrow)] = row['transaction__client__middle_name']
                        worksheet['U' + str(wsrow)] = row['transaction__client__suffix__name']
                        worksheet['V' + str(wsrow)] = client_birth_date
                        worksheet['W' + str(wsrow)] = row['transaction__client__house_no']
                        worksheet['X' + str(wsrow)] = row['transaction__client__barangay__brgy_name']
                        worksheet['Y' + str(wsrow)] = row['transaction__client__barangay__city_code__city_name']
                        worksheet['Z' + str(wsrow)] = row['transaction__client__street']
                        worksheet['AA' + str(wsrow)] = row['transaction__client__barangay__city_code__prov_code__prov_name']
                        worksheet['BB' + str(wsrow)] = row['transaction__client__barangay__city_code__prov_code__region_code__region_name']
                        worksheet['CC' + str(wsrow)] = row['transaction__client__sex__name']
                        worksheet['DD' + str(wsrow)] = row['transaction__client__occupation__occupation_name']
                        worksheet['EE' + str(wsrow)] = row['transaction__client__salary']

                        wsrow = wsrow + 1
                    response = HttpResponse(content=save_virtual_workbook(workbook), content_type='application/ms-excel')
                    response['Content-Disposition'] = 'attachment; filename=Sex disaggregated data (FEMALE ONLY)' + ' (' + year + ').xlsx'
                    return response
                else:
                    return render(request, '404.html')
                
        elif service_provider:
            print(service_provider)
        else:
            return render(request, '404.html')
    context = {
        'ClientCategory': Category.objects.all()
    }
    return render(request, 'GeneratebyUser.html', context)