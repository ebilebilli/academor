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
    path('leads/<int:pk>/convert/', v.lead_convert, name='lead_convert'),
    path('students/', v.students, name='students'),
    path('students/new/', v.student_new, name='student_new'),
    path('students/<int:pk>/', v.student_detail, name='student'),
    path('students/<int:pk>/edit/', v.student_edit, name='student_edit'),
    path('students/<int:pk>/password/', v.student_password, name='student_password'),
    path('students/<int:student_pk>/courses/new/', v.enrollment_new, name='enrollment_new'),
    path('courses/<int:pk>/', v.enrollment_edit, name='enrollment_edit'),
    path('payments/', v.payments, name='payments'),
    path('payments/new/', v.payment_new, name='payment_new'),
    path('payments/<int:pk>/', v.payment_edit, name='payment_edit'),
    path('payments/<int:pk>/receipt/', v.payment_receipt, name='payment_receipt'),
    path('payments/<int:pk>/teacher/', v.payment_teacher_status, name='payment_teacher_status'),
    path('charges/new/', v.charge_new, name='charge_new'),
    path('charges/<int:pk>/cancel/', v.charge_cancel, name='charge_cancel'),
    path('debts/', v.debts, name='debts'),
    path('teachers/', v.teachers, name='teachers'),
    path('teachers/new/', v.teacher_new, name='teacher_new'),
    path('reports/', v.reports, name='reports'),
    path('groups/', v.groups, name='groups'),
    path('groups/new/', v.group_form, name='group_new'),
    path('groups/<int:pk>/', v.group_form, name='group_edit'),
    path('attendance/', v.attendance, name='attendance'),
]
