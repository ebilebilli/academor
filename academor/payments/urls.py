from django.urls import path

from . import views

urlpatterns = [
    path(
        'course/<slug:slug>/',
        views.payment_start_course,
        name='payment_start_course',
    ),
    path(
        'checkout/course/<slug:slug>/',
        views.payment_start_course,
        name='payment_checkout_course',
    ),
    path('start/<int:amount>/', views.payment_start, name='payment_start'),
    path(
        'start/<int:amount>/<str:description>/',
        views.payment_start,
        name='payment_start_with_description',
    ),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('decline/', views.payment_decline, name='payment_decline'),
]
