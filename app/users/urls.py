from django.urls import path

from app.users.views import user_list, edit_user, get_role, change_password

urlpatterns = [
    path('list/', user_list, name='user_list'),
    path('edit/<int:pk>', edit_user, name='edit_user'),
    path('role/<int:pk>', get_role, name='get_role'),
    path('change_password/', change_password, name='change_password')
]