from django.urls import path

from api.requests.views import TransactionDescriptionViews, CompletedTransactionViews, TransactionPerSession, AdvanceFinanceFilterViews, FinanceVoucherViews, \
    VoucherDataViews, SignatoriesTransactionsViews, TransactionPerSessionAllViews, CashTransactionViews, OutsideFoDataViews, adminMonitoring, TransactionIncoming, \
    kioskAPI


urlpatterns = [
    #admin_site
    path('admin_monitoring/list/',adminMonitoring.as_view(), name='api_adminMonitoring'),

    # path('transaction/list/', TransactionViews.as_view(), name='api_transaction_list'), #filter only not assessed by swo
    path('transactionDescription/list/',TransactionDescriptionViews.as_view(), name='api_transaction_description'),
    path('completed/transaction/list/', CompletedTransactionViews.as_view(), name='api_completed_transaction_list'),
    path('transaction/session/',TransactionPerSession.as_view(), name='api_TransactionPerSession'),
    path('transaction/all/session/', TransactionPerSessionAllViews.as_view(), name='api_transactionPerSessionAll_list'),
    path('transaction/incoming/list/', TransactionIncoming.as_view(), name='api_TransactionIncoming'),
    
    #FINANCE
    path('finance/search/',AdvanceFinanceFilterViews.as_view(), name='api_AdvanceFinanceFilterViews'),
    path('finance/voucher/', FinanceVoucherViews.as_view(), name='api_FinanceList'),
    path('finance/voucher/data/', VoucherDataViews.as_view(), name='api_FinanceVoucherData'),
    path('finance/outside/fo/', OutsideFoDataViews.as_view(), name='api_OutsideFoDataViews'),

    #Cash
    path('cash/transaction/', CashTransactionViews.as_view(), name='api_CashTransactionViews'),

    #SIGNATORIES
    path('signatories/data/',SignatoriesTransactionsViews.as_view(), name='api_Signatories'),

    #KIOSKAPI
    path('transaction/kiosk/list/', kioskAPI.as_view(), name='api_kioskAPI'),
]