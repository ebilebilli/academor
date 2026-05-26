import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def _kapital_configured():
    return all([
        settings.KAPITAL_BASE_URL,
        settings.KAPITAL_USERNAME,
        settings.KAPITAL_PASSWORD,
        settings.KAPITAL_REDIRECT_URL,
    ])


def _parse_json_response(response):
    try:
        return response.json()
    except ValueError:
        snippet = (response.text or "")[:300]
        return {
            "error": f"Bank API-dən gözlənilməyən cavab (HTTP {response.status_code})",
            "raw": snippet,
        }


def create_order(amount, description="Ödəniş"):
    # TODO: müvəqqəti debug — testdən sonra print-ləri silin
    if not _kapital_configured():
        return {
            "ok": False,
            "error": "Ödəniş sistemi konfiqurasiya edilməyib (KAPITAL_* env dəyişənləri).",
        }

    url = f"{settings.KAPITAL_BASE_URL.rstrip('/')}/order"
    payload = {
        "order": {
            "typeRid": "Order_SMS",
            "amount": str(amount),
            "currency": "AZN",
            "language": "az",
            "description": description,
            "hppRedirectUrl": settings.KAPITAL_REDIRECT_URL,
        }
    }

    print("URL:", url, flush=True)
    print("USERNAME:", settings.KAPITAL_USERNAME, flush=True)
    print("PASSWORD:", settings.KAPITAL_PASSWORD, flush=True)

    try:
        response = requests.post(
            url,
            json=payload,
            auth=(settings.KAPITAL_USERNAME, settings.KAPITAL_PASSWORD),
            timeout=30,
        )
    except requests.RequestException:
        logger.exception("Kapital create_order failed")
        return {"ok": False, "error": "Bank API ilə əlaqə qurulmadı."}

    print("STATUS CODE:", response.status_code, flush=True)
    print("RESPONSE:", response.text[:500], flush=True)

    data = _parse_json_response(response)
    if not response.ok:
        return {
            "ok": False,
            "error": data.get("error") or data.get("message") or f"HTTP {response.status_code}",
            "detail": data,
        }

    order = data.get("order")
    if not order:
        return {
            "ok": False,
            "error": "Sifariş yaradılmadı",
            "detail": data,
        }

    return {"ok": True, "order": order}


def get_order(order_id):
    if not _kapital_configured():
        return {
            "ok": False,
            "error": "Ödəniş sistemi konfiqurasiya edilməyib (KAPITAL_* env dəyişənləri).",
        }

    url = f"{settings.KAPITAL_BASE_URL.rstrip('/')}/order/{order_id}"

    try:
        response = requests.get(
            url,
            auth=(settings.KAPITAL_USERNAME, settings.KAPITAL_PASSWORD),
            timeout=30,
        )
    except requests.RequestException:
        logger.exception("Kapital get_order failed")
        return {"ok": False, "error": "Bank API ilə əlaqə qurulmadı."}

    data = _parse_json_response(response)
    if not response.ok:
        return {
            "ok": False,
            "error": data.get("error") or data.get("message") or f"HTTP {response.status_code}",
            "detail": data,
        }

    return {"ok": True, "order": data.get("order"), "detail": data}


def build_hpp_redirect_url(order):
    hpp_url = (order.get("hppUrl") or "").rstrip("/")
    order_id = order.get("id")
    password = order.get("password")
    if not hpp_url or not order_id or not password:
        return None
    return f"{hpp_url}/flex?id={order_id}&password={password}"
