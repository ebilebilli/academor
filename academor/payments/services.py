import logging
from datetime import datetime, timedelta

import requests
from django.conf import settings
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)

_token = None
_token_expiry = None
_config_logged = False

_UNITED_PAYMENT_KEYS = (
    'UNITED_PAYMENT_AUTH_URL',
    'UNITED_PAYMENT_USERNAME',
    'UNITED_PAYMENT_PASSWORD',
    'UNITED_PAYMENT_BASE_URL',
    'UNITED_PAYMENT_SUCCESS_URL',
    'UNITED_PAYMENT_CANCEL_URL',
    'UNITED_PAYMENT_DECLINE_URL',
)


def _configured():
    return all([
        settings.UNITED_PAYMENT_AUTH_URL,
        settings.UNITED_PAYMENT_USERNAME,
        settings.UNITED_PAYMENT_PASSWORD,
        settings.UNITED_PAYMENT_BASE_URL,
        settings.UNITED_PAYMENT_SUCCESS_URL,
        settings.UNITED_PAYMENT_CANCEL_URL,
        settings.UNITED_PAYMENT_DECLINE_URL,
    ])


def _is_set(value) -> bool:
    return bool((value or '').strip())


def _mask_username(value: str) -> str:
    value = (value or '').strip()
    if not value:
        return '(empty)'
    if '@' in value:
        local, _, domain = value.partition('@')
        if len(local) <= 2:
            masked_local = '*'
        else:
            masked_local = f'{local[0]}***{local[-1]}'
        return f'{masked_local}@{domain}'
    return f'{value[:2]}***' if len(value) > 2 else '***'


def _payment_environment_label() -> str:
    base = (settings.UNITED_PAYMENT_BASE_URL or '').lower()
    auth = (settings.UNITED_PAYMENT_AUTH_URL or '').lower()
    if 'test-vpos' in base or 'test-vpos' in auth:
        return 'test'
    if base or auth:
        return 'production'
    return 'unset'


def united_payment_config_snapshot() -> dict:
    """Safe summary for logs — never includes passwords or tokens."""
    missing = [
        key for key in _UNITED_PAYMENT_KEYS
        if not _is_set(getattr(settings, key, None))
    ]
    return {
        'environment': _payment_environment_label(),
        'configured': _configured(),
        'missing_keys': missing,
        'auth_url': (settings.UNITED_PAYMENT_AUTH_URL or '').strip() or None,
        'base_url': (settings.UNITED_PAYMENT_BASE_URL or '').strip() or None,
        'username': _mask_username(settings.UNITED_PAYMENT_USERNAME),
        'password_set': _is_set(settings.UNITED_PAYMENT_PASSWORD),
        'success_url': (settings.UNITED_PAYMENT_SUCCESS_URL or '').strip() or None,
        'cancel_url': (settings.UNITED_PAYMENT_CANCEL_URL or '').strip() or None,
        'decline_url': (settings.UNITED_PAYMENT_DECLINE_URL or '').strip() or None,
    }


def log_united_payment_config(reason: str = 'startup') -> None:
    global _config_logged
    if _config_logged:
        return
    _config_logged = True
    snapshot = united_payment_config_snapshot()
    if snapshot['configured']:
        logger.info(
            'United Payment config (%s): environment=%s auth_url=%s base_url=%s '
            'username=%s password_set=%s callbacks=%s',
            reason,
            snapshot['environment'],
            snapshot['auth_url'],
            snapshot['base_url'],
            snapshot['username'],
            snapshot['password_set'],
            {
                'success': snapshot['success_url'],
                'cancel': snapshot['cancel_url'],
                'decline': snapshot['decline_url'],
            },
        )
    else:
        logger.warning(
            'United Payment config (%s): NOT CONFIGURED missing_keys=%s '
            'environment=%s auth_url=%s base_url=%s',
            reason,
            snapshot['missing_keys'],
            snapshot['environment'],
            snapshot['auth_url'],
            snapshot['base_url'],
        )


def _parse_json(response):
    try:
        return response.json()
    except ValueError:
        return {
            'error': _('Unexpected response from payment API (HTTP %(code)s).') % {
                'code': response.status_code,
            },
        }


def _api_headers(token):
    if token.startswith('Bearer '):
        header_value = token
    else:
        header_value = token
    return {
        'x-auth-token': header_value,
        'Content-Type': 'application/json',
    }


def _extract_token(data):
    if not isinstance(data, dict):
        return None
    for key in ('token', 'accessToken', 'access_token', 'jwt'):
        value = data.get(key)
        if value:
            return value
    nested = data.get('data')
    if isinstance(nested, dict):
        return _extract_token(nested)
    return None


def _extract_payment_url(data):
    if not isinstance(data, dict):
        return None
    for key in ('url', 'redirectUrl', 'paymentUrl', 'link', 'checkoutUrl'):
        value = data.get(key)
        if value:
            return value
    nested = data.get('data')
    if isinstance(nested, dict):
        return _extract_payment_url(nested)
    return None


def _extract_transaction_id(data):
    if not isinstance(data, dict):
        return None
    for key in ('transactionId', 'transaction_id', 'id', 'trxId'):
        value = data.get(key)
        if value is not None:
            return str(value)
    nested = data.get('data')
    if isinstance(nested, dict):
        return _extract_transaction_id(nested)
    return None


def _transaction_id_payload(transaction_id):
    tid = str(transaction_id)
    if tid.isdigit():
        return {'transactionId': int(tid)}
    return {'transactionId': tid}


def _interpret_status(data):
    """
    United Payment status payload (simple and detailed):
    - isSuccess: true
    - orderStatus / status: APPROVED
    - errorCode / status: 00
    """
    if not isinstance(data, dict):
        return {
            'status_label': '',
            'is_success': False,
            'is_cancelled': False,
            'is_declined': False,
        }

    if data.get('isSuccess') is True:
        return {
            'status_label': str(data.get('orderStatus') or data.get('status') or 'APPROVED'),
            'is_success': True,
            'is_cancelled': False,
            'is_declined': False,
        }

    order_status = str(data.get('orderStatus') or '').upper()
    status = str(data.get('status') or '').upper()
    error_code = str(data.get('errorCode') or '')

    is_success = (
        order_status == 'APPROVED'
        or status == 'APPROVED'
        or error_code == '00'
        or status == '00'
    )

    cancelled = status in {'CANCELLED', 'CANCELED', 'CANCEL'} or order_status in {'CANCELLED', 'CANCELED'}
    declined = status in {'DECLINED', 'FAILED', 'ERROR'} or order_status in {'DECLINED', 'FAILED'}

    label = order_status or status or error_code
    return {
        'status_label': label,
        'is_success': is_success,
        'is_cancelled': cancelled and not is_success,
        'is_declined': declined and not is_success,
    }


def get_token():
    global _token, _token_expiry

    log_united_payment_config(reason='get_token')

    if not _configured():
        snapshot = united_payment_config_snapshot()
        logger.warning(
            'United Payment auth skipped: missing_keys=%s snapshot=%s',
            snapshot['missing_keys'],
            snapshot,
        )
        return {
            'ok': False,
            'error': _('Payment system is not configured (UNITED_PAYMENT_*).'),
        }

    if _token and _token_expiry and datetime.now() < _token_expiry:
        logger.debug('United Payment auth: reusing cached token')
        return {'ok': True, 'token': _token}

    auth_url = settings.UNITED_PAYMENT_AUTH_URL
    logger.info(
        'United Payment auth request environment=%s url=%s username=%s',
        _payment_environment_label(),
        auth_url,
        _mask_username(settings.UNITED_PAYMENT_USERNAME),
    )

    payload = {
        'email': settings.UNITED_PAYMENT_USERNAME,
        'username': settings.UNITED_PAYMENT_USERNAME,
        'password': settings.UNITED_PAYMENT_PASSWORD,
    }

    try:
        response = requests.post(
            auth_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30,
        )
    except requests.RequestException:
        logger.exception(
            'United Payment login failed environment=%s url=%s',
            _payment_environment_label(),
            auth_url,
        )
        return {'ok': False, 'error': _('Could not connect to the payment system.')}

    data = _parse_json(response)
    if not response.ok:
        error = data.get('message') or data.get('error') or f'HTTP {response.status_code}'
        logger.warning(
            'United Payment auth failed environment=%s status=%s url=%s error=%s response=%s',
            _payment_environment_label(),
            response.status_code,
            auth_url,
            error,
            data,
        )
        return {
            'ok': False,
            'error': error,
            'detail': data,
        }

    token = _extract_token(data)
    if not token:
        logger.warning(
            'United Payment auth missing token environment=%s url=%s response=%s',
            _payment_environment_label(),
            auth_url,
            data,
        )
        return {'ok': False, 'error': _('JWT token was not received.'), 'detail': data}

    _token = token
    _token_expiry = datetime.now() + timedelta(minutes=55)
    logger.info(
        'United Payment auth ok environment=%s url=%s token_received=true',
        _payment_environment_label(),
        auth_url,
    )
    return {'ok': True, 'token': token}


def create_transaction(
    amount,
    success_url,
    cancel_url,
    decline_url,
    language='AZ',
    description=None,
    client_order_id=None,
    currency='944',
):
    log_united_payment_config(reason='create_transaction')

    token_result = get_token()
    if not token_result.get('ok'):
        logger.warning(
            'United Payment create_transaction skipped environment=%s error=%s config=%s',
            _payment_environment_label(),
            token_result.get('error'),
            united_payment_config_snapshot(),
        )
        return token_result

    url = f"{settings.UNITED_PAYMENT_BASE_URL.rstrip('/')}/transactions/checkout"
    payload = {
        'amount': str(amount),
        'language': language,
        'successUrl': success_url,
        'cancelUrl': cancel_url,
        'declineUrl': decline_url,
        'currency': currency,
    }
    if description:
        payload['description'] = description
    if client_order_id is not None:
        payload['clientOrderId'] = str(client_order_id)

    logger.info(
        'United Payment checkout request environment=%s url=%s client_order_id=%s amount=%s '
        'currency=%s callbacks=%s',
        _payment_environment_label(),
        url,
        client_order_id,
        amount,
        currency,
        {
            'success': success_url,
            'cancel': cancel_url,
            'decline': decline_url,
        },
    )

    try:
        response = requests.post(
            url,
            json=payload,
            headers=_api_headers(token_result['token']),
            timeout=30,
        )
    except requests.RequestException:
        logger.exception(
            'United Payment create_transaction failed environment=%s url=%s client_order_id=%s',
            _payment_environment_label(),
            url,
            client_order_id,
        )
        return {'ok': False, 'error': _('Payment transaction could not be created.')}

    data = _parse_json(response)
    if not response.ok:
        error = data.get('message') or data.get('error') or f'HTTP {response.status_code}'
        logger.warning(
            'United Payment checkout failed environment=%s status=%s url=%s '
            'client_order_id=%s amount=%s error=%s detail=%s',
            _payment_environment_label(),
            response.status_code,
            url,
            client_order_id,
            amount,
            error,
            data,
        )
        return {
            'ok': False,
            'error': error,
            'detail': data,
        }

    payment_url = _extract_payment_url(data)
    transaction_id = _extract_transaction_id(data)
    if not payment_url or not transaction_id:
        logger.warning(
            'United Payment checkout incomplete environment=%s url=%s '
            'client_order_id=%s amount=%s response=%s',
            _payment_environment_label(),
            url,
            client_order_id,
            amount,
            data,
        )
        return {
            'ok': False,
            'error': _('Payment link or transaction ID was not received.'),
            'detail': data,
        }

    logger.info(
        'United Payment checkout ok environment=%s client_order_id=%s transaction_id=%s '
        'payment_url=%s',
        _payment_environment_label(),
        client_order_id,
        transaction_id,
        payment_url,
    )

    return {
        'ok': True,
        'payment_url': payment_url,
        'transaction_id': transaction_id,
        'detail': data,
    }


def get_transaction_status(transaction_id):
    """POST /transactions/transaction-status-by-trx-id-detailed"""
    token_result = get_token()
    if not token_result.get('ok'):
        return token_result

    url = (
        f"{settings.UNITED_PAYMENT_BASE_URL.rstrip('/')}"
        '/transactions/transaction-status-by-trx-id-detailed'
    )

    try:
        response = requests.post(
            url,
            json=_transaction_id_payload(transaction_id),
            headers=_api_headers(token_result['token']),
            timeout=30,
        )
    except requests.RequestException:
        logger.exception('United Payment get_transaction_status failed')
        return {'ok': False, 'error': _('Transaction status could not be verified.')}

    data = _parse_json(response)
    if not response.ok:
        return {
            'ok': False,
            'error': data.get('message') or data.get('error') or f'HTTP {response.status_code}',
            'detail': data,
        }

    interpreted = _interpret_status(data)
    return {
        'ok': True,
        'status': interpreted['status_label'],
        'detail': data,
        **interpreted,
    }


def get_transaction_status_by_client_order(client_order_id):
    """POST /transactions/transaction-status-by-order-id-detailed"""
    token_result = get_token()
    if not token_result.get('ok'):
        return token_result

    url = (
        f"{settings.UNITED_PAYMENT_BASE_URL.rstrip('/')}"
        '/transactions/transaction-status-by-order-id-detailed'
    )
    payload = {'clientOrderId': str(client_order_id)}

    try:
        response = requests.post(
            url,
            json=payload,
            headers=_api_headers(token_result['token']),
            timeout=30,
        )
    except requests.RequestException:
        logger.exception('United Payment status by client order failed')
        return {'ok': False, 'error': _('Transaction status could not be verified.')}

    data = _parse_json(response)
    if not response.ok:
        return {
            'ok': False,
            'error': data.get('message') or data.get('error') or f'HTTP {response.status_code}',
            'detail': data,
        }

    interpreted = _interpret_status(data)
    if data.get('transactionId'):
        interpreted['transaction_id'] = str(data['transactionId'])

    return {
        'ok': True,
        'status': interpreted['status_label'],
        'detail': data,
        **interpreted,
    }


def payment_status_from_api(result):
    if isinstance(result, dict):
        if result.get('is_success'):
            return 'success'
        if result.get('is_cancelled'):
            return 'cancelled'
        if result.get('is_declined'):
            return 'declined'
        status_text = result.get('status') or ''
    else:
        status_text = str(result or '')

    normalized = status_text.lower()
    if normalized in {'approved', 'success', 'completed', 'paid', 'ok', '00'}:
        return 'success'
    if normalized in {'cancelled', 'canceled', 'cancel'}:
        return 'cancelled'
    if normalized in {'declined', 'decline', 'failed', 'error'}:
        return 'declined'
    return 'failed'
