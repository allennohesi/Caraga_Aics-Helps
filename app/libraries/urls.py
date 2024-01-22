from django.urls import path

from app.libraries.views import category, edit_category, mode_of_admission, edit_mode_of_admission, mode_of_assistance, \
    edit_mode_of_assistance, edit_service_provider, sub_category, edit_sub_category, \
    type_of_assistance, edit_type_of_assistance, relation, edit_relation, sex, edit_sex, suffix, edit_suffix, province, \
    edit_province, city, edit_city, barangay, get_city_name, edit_barangay, get_all_user, delete_focal_service_provider, \
    get_barangay_name, get_all_client_beneficiary, get_all_service_provider, tribe, edit_tribe, get_province_name, fund_source, \
    service_provider, signatories, update_signatories, edit_fund_source, occupation

urlpatterns = [
    path('category/', category, name='category'),
    path('category/edit/', edit_category, name='edit_category'),
    path('mode-of-admission/', mode_of_admission, name='mode_of_admission'),
    path('mode-of-admission/edit/', edit_mode_of_admission, name='edit_mode_of_admission'),
    path('mode-of-assistance/', mode_of_assistance, name='mode_of_assistance'),
    path('mode-of-assistance/edit/', edit_mode_of_assistance, name='edit_mode_of_assistance'),
    path('get-all-users/', get_all_user, name='get_all_user'),
    path('get-client-beneficiary/', get_all_client_beneficiary, name='get_all_client_beneficiary'),
    path('get-all-service-provider/', get_all_service_provider, name='get_all_service_provider'),
    path('service-provider/edit/<int:pk>', edit_service_provider, name='edit_service_provider'),
    path('service-provider/focal/delete/', delete_focal_service_provider, name='delete_focal_service_provider'),
    path('sub-category/', sub_category, name='sub_category'),
    path('sub-category/edit/', edit_sub_category, name='edit_sub_category'),
    path('type-of-assistance/', type_of_assistance, name='type_of_assistance'),
    path('type-of-assistance/edit/', edit_type_of_assistance, name='edit_type_of_assistance'),
    path('relation/', relation, name='relation'),
    path('relation/edit/', edit_relation, name='edit_relation'),
    path('sex/', sex, name='sex'),
    path('sex/edit/', edit_sex, name='edit_sex'),
    path('suffix/', suffix, name='suffix'),
    path('suffix/edit/', edit_suffix, name='edit_suffix'),
    path('tribe/', tribe, name='tribe'),
    path('tribe/edit/', edit_tribe, name='edit_tribe'),
    path('province/', province, name='province'),
    path('province/edit/', edit_province, name='edit_province'),
    path('city/', city, name='city'),
    path('city/edit/', edit_city, name='edit_city'),
    path('barangay/', barangay, name='barangay'),
    path('barangay/edit/', edit_barangay, name='edit_barangay'),
    
    path('fund-source/', fund_source, name='fund_source'),
    path('update/fund-source', edit_fund_source,name='edit_fund_source'),
    path('service-provider/', service_provider, name='service_provider'),
    path('signatories', signatories, name='signatories'),
    path('update_signatories/', update_signatories, name='update_signatories'),

    path('province/get/<int:pk>', get_province_name, name='get_province_name'),
    path('city/get/<int:pk>', get_city_name, name='get_city_name'),
    path('barangay/get/<int:pk>', get_barangay_name, name='get_barangay_name'),

    path('occupation', occupation,name='occupation')
]