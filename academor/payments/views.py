import base64
import json
import uuid
from decimal import Decimal
from urllib.parse import urlencode, urlsplit, urlunsplit, parse_qsl

from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods
from django.utils import timezone
from django.utils.translation import get_language, gettext as _

from .catalog import (
    CourseNotPayableError,
    PricePackageNotFoundError,
    course_display_name,
    course_payment_description,
    get_payable_course,
    get_payable_price_package,
    package_amount,
)
from .forms import CoursePaymentForm
from .enrollment import fulfill_course_enrollment
from .models import CourseEnrollment, Payment
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
            'page_title': _('Payment error'),
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
        if value:
            return value

    up_data = _data_from_up_param(request)
    order_id = (
        up_data.get('clientOrderId')
        or up_data.get('OrderId')
        or up_data.get('orderId')
    )
    if order_id is not None:
        return str(order_id)
    return None


def _find_payment(request):
    transaction_id = _transaction_id_from_request(request)
    if transaction_id:
        payment = Payment.objects.filter(transaction_id=transaction_id).first()
        if payment:
            return payment

    client_order_id = _client_order_id_from_request(request)
    if client_order_id:
        payment = Payment.objects.filter(client_order_id=client_order_id).first()
        if payment:
            return payment
        # Legacy payments used Django pk as clientOrderId before UUID migration.
        if client_order_id.isdigit():
            payment = Payment.objects.filter(pk=int(client_order_id)).first()
            if payment:
                return payment

    return None


def _course_detail_url(slug: str) -> str:
    return reverse('projects:course-detail', kwargs={'slug': slug}) + '#course-pay'


def _is_ajax(request) -> bool:
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def _form_errors_payload(form: CoursePaymentForm) -> dict:
    return {field: [str(error) for error in errors] for field, errors in form.errors.items()}


def _redirect_course_payment_form_errors(request, slug: str, form: CoursePaymentForm):
    if request.POST.get('return_to') == 'home':
        request.session['home_payment_form_data'] = form.data
        for field_errors in form.errors.values():
            for error in field_errors:
                messages.error(request, error)
        return redirect(reverse('projects:home-page') + '#home-featured-prices')
    request.session['course_payment_form_data'] = form.data
    for field_errors in form.errors.values():
        for error in field_errors:
            messages.error(request, error)
    return redirect(_course_detail_url(slug))


def _append_query_params(url: str, params: dict) -> str:
    """
    Ensure United Payment callbacks contain a stable identifier.
    Some providers may not send transactionId back reliably, so we include clientOrderId ourselves.
    """
    if not url:
        return url
    parts = urlsplit(url)
    existing = dict(parse_qsl(parts.query, keep_blank_values=True))
    for k, v in (params or {}).items():
        if v is None:
            continue
        existing[str(k)] = str(v)
    query = urlencode(existing, doseq=True)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))


def _start_payment(
    *,
    amount: Decimal,
    description: str,
    course=None,
    price_package=None,
    buyer_email: str | None = None,
    buyer_name: str = '',
    buyer_phone: str = '',
    contract_number: str = '',
    contract_language: str = 'az',
    product_type=Payment.ProductType.GENERIC,
):
    client_order_id = str(uuid.uuid4())

    payment = Payment.objects.create(
        transaction_id=f'pending-{uuid.uuid4().hex}',
        client_order_id=client_order_id,
        amount=amount,
        description=description[:255],
        status=Payment.Status.PENDING,
        product_type=product_type,
        course=course,
        price_package=price_package,
        buyer_email=buyer_email,
        buyer_name=buyer_name,
        buyer_phone=buyer_phone,
        contract_number=contract_number,
        contract_language=(contract_language or 'az')[:2],
    )

    # Include our clientOrderId in callback URLs so we can always find the Payment record
    # even if the provider omits transactionId in the redirect query.
    success_url = _append_query_params(
        settings.UNITED_PAYMENT_SUCCESS_URL,
        {'clientOrderId': client_order_id},
    )
    cancel_url = _append_query_params(
        settings.UNITED_PAYMENT_CANCEL_URL,
        {'clientOrderId': client_order_id},
    )
    decline_url = _append_query_params(
        settings.UNITED_PAYMENT_DECLINE_URL,
        {'clientOrderId': client_order_id},
    )

    result = create_transaction(
        amount=amount,
        success_url=success_url,
        cancel_url=cancel_url,
        decline_url=decline_url,
        description=description,
        client_order_id=client_order_id,
    )

    if not result.get('ok'):
        payment.status = Payment.Status.FAILED
        payment.save(update_fields=['status', 'updated_at'])
        return None, result

    payment.transaction_id = result['transaction_id']
    payment.save(update_fields=['transaction_id', 'updated_at'])
    return payment, result


def _sync_payment_from_api(payment):
    if str(payment.transaction_id).startswith('pending-') and payment.client_order_id:
        result = get_transaction_status_by_client_order(payment.client_order_id)
    else:
        result = get_transaction_status(payment.transaction_id)

    if not result.get('ok'):
        return result

    api_tx_id = result.get('transaction_id')
    if api_tx_id and str(payment.transaction_id).startswith('pending-'):
        payment.transaction_id = api_tx_id

    payment.status = payment_status_from_api(result)
    payment.save(update_fields=['transaction_id', 'status', 'updated_at'])

    if payment.status == Payment.Status.SUCCESS:
        fulfill_course_enrollment(payment)

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
        'title': failed_title if status != Payment.Status.SUCCESS else _('Payment result'),
    }
    if payment.course_id:
        params['course_id'] = str(payment.course_id)
        if payment.course:
            params['course_slug'] = payment.course.slug
    enrollment = CourseEnrollment.objects.filter(payment_id=payment.pk).first()
    if enrollment:
        params['enrollment_id'] = str(enrollment.pk)
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

    enrollment = CourseEnrollment.objects.filter(payment_id=payment.pk).first()
    course_name = ''
    if payment.course_id and payment.course:
        course_name = course_display_name(payment.course, get_language()[:2])

    if payment.status == Payment.Status.SUCCESS:
        if enrollment and course_name:
            message = _('Payment completed. You are enrolled in «%(course)s».') % {
                'course': course_name,
            }
            message = (
                f'{message} '
                + _('Our team will contact you shortly to confirm the next steps.')
            )
        else:
            message = _(
                'Your payment was successful. We will contact you if any further '
                'steps are required.'
            )
        return render(
            request,
            'payment/success.html',
            {
                'page_title': _('Payment result'),
                'seo_noindex': True,
                'order_id': payment.transaction_id,
                'message': message,
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


@require_http_methods(['GET', 'POST'])
def payment_start_course(request, slug):
    if request.method == 'GET':
        return redirect(_course_detail_url(slug))

    ajax = _is_ajax(request)
    lang = (get_language() or 'az')[:2]

    try:
        course = get_payable_course(slug)
    except CourseNotPayableError as exc:
        if ajax:
            return JsonResponse({'success': False, 'message': str(exc)}, status=400)
        messages.error(request, str(exc))
        return redirect(reverse('projects:courses-page'))

    form = CoursePaymentForm(request.POST, request=request)
    if not form.is_valid():
        if ajax:
            payload = {'success': False, 'errors': _form_errors_payload(form)}
            non_field = form.non_field_errors()
            if non_field:
                payload['message'] = str(non_field[0])
            return JsonResponse(payload, status=400)
        return _redirect_course_payment_form_errors(request, slug, form)

    try:
        price_package = get_payable_price_package(
            course,
            form.cleaned_data['price_package_id'],
        )
    except PricePackageNotFoundError as exc:
        if ajax:
            return JsonResponse({'success': False, 'message': str(exc)}, status=400)
        messages.error(request, str(exc))
        return redirect(_course_detail_url(slug))

    amount = package_amount(price_package)
    description = course_payment_description(course, price_package, lang)
    payment, result = _start_payment(
        amount=amount,
        description=description,
        course=course,
        price_package=price_package,
        buyer_name=form.cleaned_data['buyer_name'],
        buyer_email=form.cleaned_data.get('buyer_email'),
        buyer_phone=form.cleaned_data['buyer_phone'],
        contract_number=form.cleaned_data['contract_number'],
        contract_language=(get_language() or 'az')[:2],
        product_type=Payment.ProductType.COURSE,
    )
    if payment is None:
        message = result.get('error') or _('Order could not be created.')
        if ajax:
            return JsonResponse({'success': False, 'message': message}, status=502)
        messages.error(request, message)
        return redirect(_course_detail_url(slug))

    request.session.pop('course_payment_form_data', None)
    redirect_url = result['payment_url']
    if ajax:
        return JsonResponse({'success': True, 'redirect_url': redirect_url})
    return redirect(redirect_url)


@require_GET
def payment_start(request, amount, description=None):
    """Deprecated amount-in-URL entry point; no longer supported."""
    return _payment_error(
        request,
        _(
            'This payment link is outdated. Please use the Pay button on the course page.'
        ),
    )


@require_GET
def payment_success(request):
    payment = _find_payment(request)
    if not payment:
        return _payment_error(request, _('Order not found.'))

    result = _sync_payment_from_api(payment)
    if not result.get('ok'):
        message = result.get('error') or _('Order could not be verified.')
        return _payment_error(request, message)

    return _render_callback_result(request, payment, result, _('Payment result'))


@require_GET
def payment_cancel(request):
    payment = _find_payment(request)
    if not payment:
        return _payment_error(request, _('Order not found.'))

    result = _sync_payment_from_api(payment)
    if not result.get('ok'):
        message = result.get('error') or _('Order could not be verified.')
        return _payment_error(request, message)

    return _render_callback_result(request, payment, result, _('Payment cancelled'))


@require_GET
def payment_decline(request):
    payment = _find_payment(request)
    if not payment:
        return _payment_error(request, _('Order not found.'))

    result = _sync_payment_from_api(payment)
    if not result.get('ok'):
        message = result.get('error') or _('Order could not be verified.')
        return _payment_error(request, message)

    return _render_callback_result(request, payment, result, _('Payment declined'))
