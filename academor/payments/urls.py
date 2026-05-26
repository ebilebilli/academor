from django.urls import path

from . import views

urlpatterns = [
    path("start/<int:amount>/", views.payment_start, name="payment_start"),
    # Köhnə linklər (kurs adı URL-də): /payment/start/150/Kurs adı/
    path(
        "start/<int:amount>/<str:description>/",
        views.payment_start,
        name="payment_start_with_description",
    ),
    path("result/", views.payment_result, name="payment_result"),
]
