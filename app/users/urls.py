from django.urls import path

from app.users.views import user_list, edit_user, get_role, change_password, user_profile, feedbackRequest, error_logs, clientupdatehistory, clienthistorymodal, \
                            userFeedback

urlpatterns = [
    path('list/', user_list, name='user_list'),
    path('feedback/', userFeedback, name='userFeedback'),
    path('edit/<int:pk>', edit_user, name='edit_user'),
    path('role/<int:pk>', get_role, name='get_role'),
    path('change-password/', change_password, name='change_password'),
    path('user-profile/', user_profile, name='user_profile'),
    path('feedback/request/', feedbackRequest, name='feedbackRequest'),
    path('error-logs/', error_logs, name='error_logs'),
    path('clientupdatehistory/', clientupdatehistory, name='clientupdatehistory'),
    path('clienthistorymodal/modal/<int:pk>', clienthistorymodal, name='clienthistorymodal')
]