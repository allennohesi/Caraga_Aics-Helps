from django.urls import path

from app.cash.views import cash, view_transaction
urlpatterns = [
    path('cash/', cash, name='cash'),
    path('transaction/view/<int:pk>', view_transaction, name='view_transaction')

]