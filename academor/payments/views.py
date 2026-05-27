import base64
import json
import uuid
from decimal import Decimal
from urllib.parse import urlencode, urlsplit, urlunsplit, parse_qsl

from django.conf import settings
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET
from django.utils import timezone

from .models import Payment
from .services import (
    create_transaction,
    get_transaction_status,
    get_transaction_status_by_client_order,
    payment_status_from_api,
)


def _payment_error(request, message, status=200):
    return render(
        request,
        'payment/error.html',
        {
            'message': message,
            'page_title': 'Ödəniş xətası',
            'seo_noindex': True,
        },
        status=status,
    )


def _sanitize_query_value(value):
    if not value:
        return None
    return value.split('?')[0].split('&')[0].strip()


def _raw_up_payload(request):
    up = request.GET.get('up')
    if up:
        return up
    raw_client_order = request.GET.get('clientOrderId') or ''
    if '?up=' in raw_client_order:
        return raw_client_order.split('?up=', 1)[1]
    return None


def _data_from_up_param(request):
    up = _raw_up_payload(request)
    if not up:
        return {}
    try:
        padded = up + '=' * (-len(up) % 4)
        raw = base64.b64decode(padded).decode('utf-8')
        return json.loads(raw)
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return {}


def _transaction_id_from_request(request):
    for key in (
        'transactionId',
        'transaction_id',
        'TransactionId',
        'Transaction',
        'trxId',
        'ID',
    ):
        value = _sanitize_query_value(request.GET.get(key))
        if value:
            return value

    up_data = _data_from_up_param(request)
    tx = up_data.get('Transaction') or up_data.get('transactionId')
    if tx is not None:
        return str(tx)
    return None


def _client_order_id_from_request(request):
    for key in ('clientOrderId', 'client_order_id', 'orderId', 'OrderId'):
        value = _sanitize_query_value(request.GET.get(key))
        if value and value.isdigit():
            return int(value)

    up_data = _data_from_up_param(request)
    order_id = up_data.get('OrderId') or up_data.get('orderId')
    if order_id is not None:
        try:
            return int(order_id)
        except (TypeError, ValueError):
            pass
    return None


def _find_payment(request):
    transaction_id = _transaction_id_from_request(request)
    if transaction_id:
        payment = Payment.objects.filter(transaction_id=transaction_id).first()
        if payment:
            return payment

    client_order_id = _client_order_id_from_request(request)
    if client_order_id is not None:
        payment = Payment.objects.filter(pk=client_order_id).first()
        if payment:
            return payment

    return None


def _sync_payment_from_api(payment):
    if str(payment.transaction_id).startswith('pending-'):
        result = get_transaction_status_by_client_order(payment.pk)
    else:
        result = get_transaction_status(payment.transaction_id)

    if not result.get('ok'):
        return result

    api_tx_id = result.get('transaction_id')
    if api_tx_id and str(payment.transaction_id).startswith('pending-'):
        payment.transaction_id = api_tx_id

    payment.status = payment_status_from_api(result)
    payment.save(update_fields=['transaction_id', 'status', 'updated_at'])
    return result


def _store_callback_payload(request, payment):
    raw_up = _raw_up_payload(request)
    if not raw_up:
        return
    payment.callback_up = raw_up
    payment.callback_payload = _data_from_up_param(request) or {}
    payment.callback_received_at = timezone.now()
    payment.save(update_fields=['callback_up', 'callback_payload', 'callback_received_at', 'updated_at'])


def _build_frontend_redirect_url(payment, failed_title):
    base = (getattr(settings, 'PAYMENT_FRONTEND_RETURN_URL', '') or '').strip()
    if not base:
        return None

    status = payment.status
    params = {
        'payment_id': str(payment.pk),
        'transaction_id': payment.transaction_id,
        'status': status,
        'title': failed_title if status != Payment.Status.SUCCESS else 'Ödəniş nəticəsi',
    }
    if payment.callback_up:
        params['up'] = payment.callback_up

    parts = urlsplit(base)
    existing = dict(parse_qsl(parts.query, keep_blank_values=True))
    existing.update({k: v for k, v in params.items() if v is not None})
    query = urlencode(existing, doseq=True)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))


def _render_callback_result(request, payment, result, failed_title):
    _store_callback_payload(request, payment)
    frontend_url = _build_frontend_redirect_url(payment, failed_title)
    if frontend_url:
        return redirect(frontend_url)

    if payment.status == Payment.Status.SUCCESS:
        return render(
            request,
            'payment/success.html',
            {
                'page_title': 'Ödəniş nəticəsi',
                'seo_noindex': True,
                'order_id': payment.transaction_id,
            },
        )

    return render(
        request,
        'payment/failed.html',
        {
            'page_title': failed_title,
            'seo_noindex': True,
            'status': result.get('status') or payment.status,
        },
    )


@require_GET
def payment_start(request, amount, description=None):
    if amount <= 0:
        return _payment_error(request, 'Ödəniş məbləği düzgün deyil.')

    description = (
        description
        or request.GET.get('description')
        or 'Ödəniş'
    )

    payment = Payment.objects.create(
        transaction_id=f'pending-{uuid.uuid4().hex}',
        amount=Decimal(amount),
        description=description[:255],
        status=Payment.Status.PENDING,
    )

    # Callback URL-lərə ?clientOrderId= əlavə etməyin — bank özü ?up=... qoyur.
    result = create_transaction(
        amount=amount,
        success_url=settings.UNITED_PAYMENT_SUCCESS_URL,
        cancel_url=settings.UNITED_PAYMENT_CANCEL_URL,
        decline_url=settings.UNITED_PAYMENT_DECLINE_URL,
        description=description,
        client_order_id=payment.pk,
    )

    if not result.get('ok'):
        payment.status = Payment.Status.FAILED
        payment.save(update_fields=['status', 'updated_at'])
        message = result.get('error') or 'Sifariş yaradılmadı'
        return _payment_error(request, message)

    payment.transaction_id = result['transaction_id']
    payment.client_order_id = str(payment.pk)
    payment.save(update_fields=['transaction_id', 'client_order_id', 'updated_at'])

    return redirect(result['payment_url'])


@require_GET
def payment_success(request):
    payment = _find_payment(request)
    if not payment:
        return _payment_error(request, 'Sifariş tapılmadı')

    result = _sync_payment_from_api(payment)
    if not result.get('ok'):
        message = result.get('error') or 'Sifariş yoxlanıla bilmədi'
        return _payment_error(request, message)

    return _render_callback_result(request, payment, result, 'Ödəniş nəticəsi')


@require_GET
def payment_cancel(request):
    payment = _find_payment(request)
    if not payment:
        return _payment_error(request, 'Sifariş tapılmadı')

    result = _sync_payment_from_api(payment)
    if not result.get('ok'):
        message = result.get('error') or 'Sifariş yoxlanıla bilmədi'
        return _payment_error(request, message)

    return _render_callback_result(request, payment, result, 'Ödəniş ləğv edildi')


@require_GET
def payment_decline(request):
    payment = _find_payment(request)
    if not payment:
        return _payment_error(request, 'Sifariş tapılmadı')

    result = _sync_payment_from_api(payment)
    if not result.get('ok'):
        message = result.get('error') or 'Sifariş yoxlanıla bilmədi'
        return _payment_error(request, message)

    return _render_callback_result(request, payment, result, 'Ödəniş rədd edildi')
