from django.urls import path

from api.client_bene.views import ClientBeneficiaryViews, AdvanceFilterViews, ClientBeneficiaryUpdateHistoryViews

urlpatterns = [
    path('', ClientBeneficiaryViews.as_view(), name='api_client_beneficiary'),
    path('AdvanceFilterViews/', AdvanceFilterViews.as_view(), name='api_advance_filter'),
    path('ClientBeneficiaryUpdateHistoryViews/', ClientBeneficiaryUpdateHistoryViews.as_view(), name='api_ClientBeneficiaryUpdateHistoryViews')
]