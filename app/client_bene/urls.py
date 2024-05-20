from django.urls import path

from app.client_bene.views import client_beneficiary, view_client_bene_info, registration, modal_transaction, Modal_DirectRequest, \
    InsertDirectRequests, deactivate_client, activate_client

urlpatterns = [
    path('', client_beneficiary, name='client_beneficiary'),
    path('registration/', registration, name='client_bene_registration'),
    path('view/<str:pk>', view_client_bene_info, name='view_client_bene_info'),
    path('view_transaction/modal_for_transaction/<int:pk>', modal_transaction, name='modal_transaction'),
    path('direct_requests/modal_direct/<int:pk>', Modal_DirectRequest, name='Modal_DirectRequest'),
    path('InsertDirectRequests/', InsertDirectRequests,name='InsertDirectRequests'),
    path('activate_client/', activate_client, name='activate_client'),
    path('deactivate/', deactivate_client, name='deactivate_client'),
]