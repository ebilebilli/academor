from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET

from .services import build_hpp_redirect_url, create_order, get_order


def _payment_error(request, message, status=200):
    return render(
        request,
        "payment/error.html",
        {
            "message": message,
            "page_title": "Ödəniş xətası",
            "seo_noindex": True,
        },
        status=status,
    )


@require_GET
def payment_start(request, amount, description=None):
    if amount <= 0:
        return _payment_error(request, "Ödəniş məbləği düzgün deyil.")

    description = (
        description
        or request.GET.get("description")
        or "Ödəniş"
    )

    result = create_order(amount=amount, description=description)
    if not result.get("ok"):
        message = result.get("error") or "Sifariş yaradılmadı"
        return _payment_error(request, message)

    order = result["order"]
    hpp_url = build_hpp_redirect_url(order)
    if not hpp_url:
        return _payment_error(request, "Bank ödəniş səhifəsinin linki alınmadı.")

    return redirect(hpp_url)


@require_GET
def payment_result(request):
    order_id = request.GET.get("ID")
    if not order_id:
        return _payment_error(request, "Sifariş tapılmadı")

    result = get_order(order_id)
    if not result.get("ok"):
        message = result.get("error") or "Sifariş yoxlanıla bilmədi"
        return _payment_error(request, message)

    real_status = (result.get("order") or {}).get("status")
    context = {
        "page_title": "Ödəniş nəticəsi",
        "seo_noindex": True,
    }

    if real_status == "FullyPaid":
        context["order_id"] = order_id
        return render(request, "payment/success.html", context)

    context["status"] = real_status or request.GET.get("STATUS") or "naməlum"
    return render(request, "payment/failed.html", context)
