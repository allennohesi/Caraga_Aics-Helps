from django.urls import path

from api.users.views import UserViews

urlpatterns = [
    path('list/', UserViews.as_view(), name='api_user_list')
]