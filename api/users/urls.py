from django.urls import path

from api.users.views import UserViews, ActiveSwoView, ErrorViews, FeedbackViews

urlpatterns = [
    path('list/', UserViews.as_view(), name='api_user_list'),
    path('active/swo/', ActiveSwoView.as_view(), name='api_swo_user_list'),
    path('ErrorViews/', ErrorViews.as_view(), name='api_error_list'),
    path('FeedbackViews/', FeedbackViews.as_view(), name='api_FeedbackViews')
]