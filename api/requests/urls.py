from django.urls import path

from api.requests.views import TransactionDescriptionViews, CompletedTransactionViews, TransactionPerSession, AdvanceFinanceFilterViews, FinanceVoucherViews, \
    VoucherDataViews, SignatoriesTransactionsViews, TransactionPerSessionAllViews, CashTransactionViews, OutsideFoDataViews, adminMonitoring, TransactionIncoming, \
    kioskAPI, queuingAPI, CaseStudyDeadline, ServiceProviderMonitoring, TransactionAdvanceSearch, DisbursementDataViews, DisbursementVoucherDataViews


urlpatterns = [
    #admin_site
    path('admin_monitoring/list/',adminMonitoring.as_view(), name='api_adminMonitoring'),

    # path('transaction/list/', TransactionViews.as_view(), name='api_transaction_list'), #filter only not assessed by swo
    path('transactionDescription/list/',TransactionDescriptionViews.as_view(), name='api_transaction_description'),
    path('completed/transaction/list/', CompletedTransactionViews.as_view(), name='api_completed_transaction_list'),
    path('transaction/session/',TransactionPerSession.as_view(), name='api_TransactionPerSession'),
    path('transaction/all/session/', TransactionPerSessionAllViews.as_view(), name='api_transactionPerSessionAll_list'),
    path('transaction/incoming/list/', TransactionIncoming.as_view(), name='api_TransactionIncoming'),
    path('case_study/deadline/', CaseStudyDeadline.as_view(), name='api_CaseStudyDeadline'),
    path('trasanction/queuing/', queuingAPI.as_view(), name='api_queuing_system'), # AGUSAN DEL NORTE ONLY
    path('transaction/advance/search/', TransactionAdvanceSearch.as_view(), name='api_advance_search'),
    #FINANCE
    path('finance/search/',AdvanceFinanceFilterViews.as_view(), name='api_AdvanceFinanceFilterViews'),
    path('finance/voucher/', FinanceVoucherViews.as_view(), name='api_FinanceList'),
    path('finance/voucher/data/', VoucherDataViews.as_view(), name='api_FinanceVoucherData'),
    path('finance/outside/fo/', OutsideFoDataViews.as_view(), name='api_OutsideFoDataViews'),
    path('finance/disbursement/list/', DisbursementDataViews.as_view(), name='api_DisbursementDataViews'),
    path('finance/disbursement/voucher/data/', DisbursementVoucherDataViews.as_view(), name='api_DisbursementVoucherDataViews'),
    #Cash
    path('cash/transaction/', CashTransactionViews.as_view(), name='api_CashTransactionViews'),

    #SIGNATORIES
    path('signatories/data/',SignatoriesTransactionsViews.as_view(), name='api_Signatories'),

    #KIOSKAPI
    path('transaction/kiosk/list/', kioskAPI.as_view(), name='api_kioskAPI'),

    #SERVICE PROVIDER
    path('service/monitoring/', ServiceProviderMonitoring.as_view(), name='api_ServiceProviderMonitoring')
]