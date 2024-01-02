from datetime import datetime

from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect

from app.models import AuthUser, AuthUserGroups, AuthGroup
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password

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
                        updated_by_id=request.user.id
                    )

                    user.save()

                    AuthUserGroups.objects.create(
                        user_id=user.id,
                        group_id=request.POST.get('group')
                    )
                    return JsonResponse({'data': 'success', 'msg': "New user '{}' has been added successfully.".format(request.POST.get('username'))})
                return JsonResponse({'error': True, 'msg': 'Internal Error. An uncaught exception was raised.'})
            return JsonResponse({'error': True, 'msg': "User '{}' is already existed.".format(request.POST.get('username'))})
    context = {
        'title': 'User List',
        'group': AuthGroup.objects.all().order_by('name')
    }
    return render(request, 'users/list.html', context)


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

    # try:
    #     target_user = AuthUser.objects.get(pk=request.POST.get('empid'))
    # except AuthUser.DoesNotExist:
    #     messages.error(request, 'User does not exist.')
    #     return redirect('user_list')  # Redirect to your user list view

    # if request.method == 'POST':
    #         new_password = request.POST.get('password')

    #         # Check if the new password is not empty
    #         if new_password:
    #             # Hash the new password manually
    #             hashed_password = make_password(new_password)

    #             # Set the hashed password for the user
    #             target_user.password = hashed_password
    #             target_user.save()

    #             # If desired, update the user's session to prevent logout
    #             update_session_auth_hash(request, target_user)

    #             messages.success(request, f'Password for {target_user.username} was successfully updated!')
    #             return redirect('user_list')  # Redirect to your user list view
    #         else:
    #             messages.error(request, 'New password cannot be empty.')
        
    # return render(request, 'change_password_without_form.html', {'target_user': target_user})
    # if request.method == 'POST':
    #     # Create a PasswordChangeForm with the target user
    #     print("ID", request.POST.get('empid'))
    #     target_user = AuthUser.objects.filter(id=request.POST.get('empid')).update(
    #         password = set_password(request.POST.get('password'))
    #     )
    #     print("END")
    #     return JsonResponse({'data': 'success'})
        
        

@login_required
def edit_user(request, pk):
    if request.method == "POST":
        check = AuthUser.objects.filter(Q(username=request.POST.get('username')) | Q(email=request.POST.get('email')) |
                                        Q(first_name=request.POST.get('first_name')) | Q(last_name=request.POST.get('last_name')))
        if check:
            with transaction.atomic():
                AuthUser.objects.filter(id=pk).update(
                    first_name=request.POST.get('first_name'),
                    middle_name=request.POST.get('middle_name'),
                    last_name=request.POST.get('last_name'),
                    email=request.POST.get('email'),
                    username=request.POST.get('username'),
                    is_superuser=True if request.POST.get('is_superuser') else False,
                    is_staff=True if request.POST.get('is_staff') else False,
                    is_active=1,
                    updated_by_id=request.user.id,
                    date_updated=datetime.now()
                )

                AuthUserGroups.objects.filter(user_id=pk).update(
                    group_id=request.POST.get('group')
                )

                return JsonResponse({'data': 'success', 'msg': "User '{}' has been updated successfully.".format(
                    request.POST.get('username'))})
            return JsonResponse({'error': True, 'msg': 'Internal Error. An uncaught exception was raised.'})
        else:
            check_username = AuthUser.objects.filter(username=request.POST.get('username'))
            check_email = AuthUser.objects.filter(email=request.POST.get('email'))
            if check_email:
                return JsonResponse(
                    {'error': True, 'msg': "Email '{}' is already existed.".format(request.POST.get('email'))})
            else:
                if not check_username:
                    with transaction.atomic():
                        AuthUser.objects.filter(id=pk).update(
                            first_name=request.POST.get('first_name'),
                            middle_name=request.POST.get('middle_name'),
                            last_name=request.POST.get('last_name'),
                            email=request.POST.get('email'),
                            username=request.POST.get('username'),
                            is_superuser=True if request.POST.get('is_superuser') else False,
                            is_staff=True if request.POST.get('is_staff') else False,
                            is_active=1,
                            updated_by_id=request.user.id,
                            date_updated=datetime.now()
                        )

                        AuthUserGroups.objects.filter(user_id=pk).update(
                            group_id=request.POST.get('group')
                        )

                        return JsonResponse({'data': 'success', 'msg': "User '{}' has been updated successfully.".format(request.POST.get('username'))})
                    return JsonResponse({'error': True, 'msg': 'Internal Error. An uncaught exception was raised.'})
                return JsonResponse(
                    {'error': True, 'msg': "User '{}' is already existed.".format(request.POST.get('username'))})
    context = {
        'user': AuthUser.objects.filter(id=pk).first(),
        'user_group': AuthUserGroups.objects.filter(user_id=pk).first(),
        'group': AuthGroup.objects.all().order_by('name')
    }
    return render(request, 'users/edit_user.html', context)