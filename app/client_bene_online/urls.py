from django.urls import path

from app.client_bene_online.views import registrationOnline, requestsOnline

urlpatterns = [
    path('registrationOnline/', registrationOnline, name='registrationOnline'),
    path('requestsOnline/',requestsOnline,name='requestsOnline')
]