from django.urls import path

from app.requests.views import requests, get_client_info, incoming, view_incoming, assessment, view_assessment, \
    save_assessment, get_bene_info, show_assistance_category, show_sub_category, get_assistance_category, \
    get_assistance_sub_category, printGIS, printGL, modal_provided, StartTime, \
    trackingModal, removeTransactionData, printCEGL, printingModal, printCECASH, printGLHead, printGLMEDCal, \
    printQueueing, queueIngDisplay, printPettyCashVoucher, assessmentStatusModal, confirmAmount, \
    transactions, viewSignatoriesTransactions, approveTransactions, remove_family_composition, \
    printPagPamatuod, view_online_swo, all_transactions, submitCaseStudy, removeCaseStudy, view_online_swo_data

urlpatterns = [
    path('new/', requests, name='new_requests'),
    path('get-client-information/<int:pk>', get_client_info, name='get_client_info'),
    path('get-beneficiary-information/<int:pk>', get_bene_info, name='get_bene_info'),
    path('incoming/', incoming, name='incoming'),
    path('incoming/view/<int:pk>', view_incoming, name='view_incoming'),
    path('assessment/', assessment, name='assessment'),
    path('assessment/view/<int:pk>', view_assessment, name='view_assessment'),
    path('assessment/save/<int:pk>', save_assessment, name='save_assessment'),
    path('show_assistance_category/', show_assistance_category, name='show_assistance_category'),
    path('show_sub_category/', show_sub_category, name='show_sub_category'),
    path('category/get/<int:pk>', get_assistance_category, name='get_assistance_category'),
    path('sub_category/get/<int:pk>', get_assistance_sub_category, name='get_assistance_sub_category'),
    path('printGIS/print/<int:pk>',printGIS, name='printGIS'),
    path('printGL/print/<int:pk>',printGL, name='printGL'),
    path('provided/<int:pk>',modal_provided, name='modal_provided'),
    path('start_time/<int:pk>',StartTime, name='StartTime'),
    path('tracking/<int:pk>', trackingModal, name='trackingModal'),
    path('removeTransactionData', removeTransactionData, name='removeTransactionData'),
    path('printCEGL/<int:pk>', printCEGL, name='printCEGL'),
    path('printCECASH/<int:pk>', printCECASH, name='printCECASH'),
    path('printingModal/<int:pk>', printingModal, name='printingModal'),
    path('assessmentStatusModal/<int:pk>', assessmentStatusModal, name='assessmentStatusModal'),
    path('printGLHead/<int:pk>',printGLHead,name='printGLHead'),
    path('printGLMEDCal/<int:pk>',printGLMEDCal,name='printGLMEDCal'),
    path('printQueueing/<int:pk>', printQueueing, name='printQueueing'),
    path('queueIngDisplay', queueIngDisplay, name='queueIngDisplay'),
    path('printPettyCashVoucher/<int:pk>/', printPettyCashVoucher, name='printPettyCashVoucher'),
    path('confirmAmount', confirmAmount, name='confirmAmount'),
    path('remove_family_composition', remove_family_composition,name='remove_family_composition'),
    path('print/Pag-Pamatuod/<int:pk>',printPagPamatuod,name='printPagPamatuod'),
    path('view_online_swo/',view_online_swo, name='view_online_swo'),
    path('view_online_swo_data', view_online_swo_data, name='view_online_swo_data'),
    path('all_transactions/',all_transactions, name='all_transactions'),
    #SubmitCaseStudy
    path('submitCaseStudy', submitCaseStudy, name='submitCaseStudy'),
    path('removeCaseStudy', removeCaseStudy, name='removeCaseStudy'),
    #SIGNATORIES
    path('transactions/', transactions, name='transactions'),
    path('transactions/signatories/view/<int:pk>', viewSignatoriesTransactions, name='viewSignatoriesTransactions'),
    path('approveTransactions/', approveTransactions,name='approveTransactions'),


]