from django.urls import path

from app.requests.views import management, registration, new_transaction, get_client_info, list_of_transaction, \
    view_transaction, case_record_uploading

urlpatterns = [
    path('', management, name='management'),
    path('registration/', registration, name='registration'),
    path('requests/', new_transaction, name='new_transaction'),
    path('requests/list/', list_of_transaction, name='list_of_transaction'),
    path('requests/view/<int:pk>', view_transaction, name='view_transaction'),
    path('requests/file/uploading/<int:pk>', case_record_uploading, name='case_record_uploading'),
    path('get-client-information/<int:pk>', get_client_info, name='get_client_info')
]