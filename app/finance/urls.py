from django.urls import path

from app.finance.views import financial_transaction, finance_assessment, voucher_modal, get_all_transaction, get_data_transaction, \
    remove_voucherData, print_voucher, print_service_provider,view_dv_number, finance_modal_provided, export_fund_summary, \
    update_amount, voucher_outside_fo, edit_outside_fo, remove_data_outside_fo, list_outside_fo, printStateofAccount, \
    dibursement_voucher, disbursement_voucher_data, get_all_soa, printdvobs, removeSoa, get_transaction_advance_search, \
    confirmVoucher, confirmSoa

urlpatterns = [
    path('transaction/', financial_transaction, name='financial_transaction'),
    path('assessment/view/<int:pk>', finance_assessment, name='finance_assessment'),
    path('voucher_modal/modal/<int:pk>', voucher_modal,name='voucher_modal'),
    path('get_transaction/', get_all_transaction, name='get_all_transaction'),
    path('get_transaction_advance_search/', get_transaction_advance_search, name='get_transaction_advance_search'),
    path('get_data_transaction/<int:pk>', get_data_transaction, name='get_data_transaction'),
    path('remove_voucherData/',remove_voucherData, name='remove_voucherData'),

    path('print/soa/<int:pk>',printStateofAccount, name='printStateofAccount'),
    path('print_voucher/<int:pk>', print_voucher,name='print_voucher'),
    path('print/service-provider/', print_service_provider, name='print_service_provider'),

    path('edit_outside_fo/<int:pk>', edit_outside_fo,name='edit_outside_fo'),
    path('oustside/field-office/', list_outside_fo, name='list_outside_fo'),
    path('remove_data_outside_fo/', remove_data_outside_fo, name='remove_data_outside_fo'),
    path('outside/fo/voucher/<int:pk>',voucher_outside_fo, name='voucher_outside_fo'),
    
    path('view_dv_number/<int:pk>', view_dv_number,name='view_dv_number'),
    path('confirmSoa/<int:pk>', confirmSoa, name='confirmSoa'),
    path('finance_modal_provided/<int:pk>',finance_modal_provided,name='finance_modal_provided'),
    path('update_amount/<int:pk>', update_amount, name='update_amount'),

    path('export/fund/summary/', export_fund_summary,name='export_fund_summary'),

    path('dibursement/voucher', dibursement_voucher, name='dibursement_voucher'),
    path('get_all_soa/', get_all_soa, name='get_all_soa'),
    path('disbursement/data/<int:pk>', disbursement_voucher_data,name='disbursement_voucher_data'),
    path('confirm/voucher/<int:pk>', confirmVoucher, name='confirmVoucher'),
    path('printdvobs/<int:pk>', printdvobs, name='printdvobs'),
    path('removesoa/', removeSoa, name='removeSoa'),

]