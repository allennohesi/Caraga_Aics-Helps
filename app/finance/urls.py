from django.urls import path

from app.finance.views import financial_transaction, finance_assessment, voucher_modal, get_all_transaction, get_data_transaction, \
    remove_voucherData, print_voucher, print_service_provider

urlpatterns = [
    path('transaction/', financial_transaction, name='financial_transaction'),
    path('assessment/view/<int:pk>', finance_assessment, name='finance_assessment'),
    path('voucher_modal/modal/<int:pk>', voucher_modal,name='voucher_modal'),
    path('get_transaction/', get_all_transaction, name='get_all_transaction'),
    path('get_data_transaction/<int:pk>', get_data_transaction, name='get_data_transaction'),
    path('remove_voucherData/',remove_voucherData, name='remove_voucherData'),
    path('print_voucher/<int:pk>', print_voucher,name='print_voucher'),
    path('print/service-provider/', print_service_provider, name='print_service_provider'),
]