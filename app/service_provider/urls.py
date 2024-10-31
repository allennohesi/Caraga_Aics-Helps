from django.urls import path

from app.service_provider.views import monitoring

urlpatterns = [
    path('monitoring/', monitoring, name='get_monitoring'),

]