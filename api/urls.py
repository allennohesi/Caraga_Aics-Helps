from django.urls import include, path

from api.views import MailViews

urlpatterns = [
    path('mail/', MailViews.as_view(), name='api_mail'),
    path('libraries/', include('api.libraries.urls')),
    path('requests/', include('api.requests.urls')),
    path('client-beneficiary/', include('api.client_bene.urls')),
    path('user/', include('api.users.urls'))
]