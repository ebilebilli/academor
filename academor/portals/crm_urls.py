from django.urls import path

from portals.views import crm_views as v

app_name = 'crm'

urlpatterns = [
    path('', v.dashboard, name='dashboard'),
    path('search/', v.search, name='search'),
    path('leads/', v.leads, name='leads'),
    path('leads/new/', v.lead_new, name='lead_new'),
    path('leads/<int:pk>/', v.lead_detail, name='lead'),
    path('leads/<int:pk>/move/', v.lead_move, name='lead_move'),
    path('students/', v.students, name='students'),
    path('students/<int:pk>/', v.student_detail, name='student'),
    path('payments/', v.payments, name='payments'),
    path('payments/new/', v.payment_new, name='payment_new'),
    path('payments/<int:pk>/receipt/', v.payment_receipt, name='payment_receipt'),
    path('charges/new/', v.charge_new, name='charge_new'),
    path('charges/<int:pk>/cancel/', v.charge_cancel, name='charge_cancel'),
    path('charges/generate/', v.charges_generate, name='charges_generate'),
    path('debts/', v.debts, name='debts'),
    path('groups/', v.groups, name='groups'),
    path('attendance/', v.attendance, name='attendance'),
]
