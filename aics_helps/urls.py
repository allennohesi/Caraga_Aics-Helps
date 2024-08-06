from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView

from app.views import login, dashboard, mail, layout_404, status_activation, landingpage, media_access, print_ProvidedBYSWO, \
                    log_out, generateTransactions, generateAICSData, generate_case_study, personalData, generatePWD, queuing, withDvTransactions, \
                    transactionDashboard, ExportBilledUnbilled

urlpatterns = [
    path('', landingpage, name='landingpage'),
    path('queuing/', queuing, name='queuing'),
    # path('sse/', sse_view, name='sse_view'),
    path('404/', layout_404, name='layout_404'),
    path('login/', login, name='login'),
    path('logout/', log_out, name='logout'),

    path('dashboard/', dashboard, name='home'),
    path('transaction/dashboard/', transactionDashboard, name='transactionDashboard'),

    path('mail/', mail, name='mail'),
    path('activate/<int:pk>', status_activation, name='status_activation'),
    path('print_ProvidedBYSWO', print_ProvidedBYSWO, name='print_ProvidedBYSWO'),

    path('personalData/', personalData,name='personalData'),
    path('withDvTransactions/', withDvTransactions, name='withDvTransactions'),
    path('generatePWD/', generatePWD, name='generatePWD'),
    path('generateTransactions/', generateTransactions, name='generateTransactions'),
    path('generateAICSData/',generateAICSData, name='generateAICSData'),
    path('generate_case_study',generate_case_study,name='generate_case_study'),
    path('generate/billed/unbilled', ExportBilledUnbilled, name='ExportBilledUnbilled'),

    path('media/cis/<str:path>', media_access, name='media'),

    #FOR MODULES
    path('cash-transaction/', include('app.cash.urls')), 
    path('financial-transaction/', include('app.finance.urls')), 
    path('libraries/', include('app.libraries.urls')),
    path('client-beneficiary/', include('app.client_bene.urls')),
    path('requests/', include('app.requests.urls')),
    path('online-request/', include('app.client_bene_online.urls')),
    path('users/', include('app.users.urls')),

    #FOR API
    path('api/', include('api.urls')), 
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# handler404 = 'app.views.dashboard'