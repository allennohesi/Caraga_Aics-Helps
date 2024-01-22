from django.urls import path

from api.libraries.views import CategoryViews, MOAViews, MOASSViews, ServiceProviderViews, SubCategoryViews, \
    TypeOfAssistanceViews, RelationViews, SexViews, SuffixViews, ProvinceViews, CityViews, BarangayViews, TribeViews, \
    SignatoriesViews, FundSourceViews, OccupationViews

urlpatterns = [
    path('category/', CategoryViews.as_view(), name='api_category'),
    path('mode-of-admission/', MOAViews.as_view(), name='api_moa'),
    path('mode-of-assistance/', MOASSViews.as_view(), name='api_moass'),
    path('service-provider/', ServiceProviderViews.as_view(), name='api_service_provider'),
    path('sub-category/', SubCategoryViews.as_view(), name='api_sub_category'),
    path('type-of-assistance/', TypeOfAssistanceViews.as_view(), name='api_type_of_assistance'),
    path('relation/', RelationViews.as_view(), name='api_relation'),
    path('sex/', SexViews.as_view(), name='api_sex'),
    path('suffix/', SuffixViews.as_view(), name='api_suffix'),
    path('tribe/', TribeViews.as_view(), name='api_tribe'),
    path('province/', ProvinceViews.as_view(), name='api_province'),
    path('city/', CityViews.as_view(), name='api_city'),
    path('barangay/', BarangayViews.as_view(), name='api_barangay'),
    path('signatories/', SignatoriesViews.as_view(), name='api_signatories'),
    path('fund-source/',FundSourceViews.as_view(), name='api_fundsource'),
    path('occupation/', OccupationViews.as_view(), name='api_occupation'),
]