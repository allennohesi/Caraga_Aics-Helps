from functools import wraps

from django.core.mail import send_mail
from django.shortcuts import redirect

from aics_helps.settings import EMAIL_HOST_USER


def send_on_gmail(subject, message, recipient):
    send_mail(subject, message, EMAIL_HOST_USER, [recipient], fail_silently=True)


def groups_only(*groups):
    def inner(view_func):
        @wraps(view_func)
        def wrapper_func(request, *args, **kwargs):
            if request.user.groups.filter(name__in=groups).exists():
                return view_func(request, *args, **kwargs)
            else:
                return redirect('layout_404')
        return wrapper_func
    return inner
