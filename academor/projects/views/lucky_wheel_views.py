from datetime import timedelta
import json
import random
import re

from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.http import require_POST

from projects.forms.forms_v1 import LuckyWheelPhoneForm
from projects.models import LuckyWheelPrize, LuckyWheelSpin
from projects.utils.normalize_phone_number import normalize_az_phone
from projects.utils.queries import (
    get_background_image,
    get_contact,
    get_language_from_request,
    serialize_contact,
)

SPIN_COOLDOWN = timedelta(hours=24)


def _normalize_phone_key(phone: str) -> str:
    az = normalize_az_phone(phone)
    if az:
        return az
    return re.sub(r'\D', '', (phone or '').strip())


def _active_prizes():
    return list(
        LuckyWheelPrize.objects.filter(is_active=True).order_by('order', 'id')
    )


def _pick_weighted_prize(prizes):
    weights = [max(1, int(p.weight or 1)) for p in prizes]
    return random.choices(prizes, weights=weights, k=1)[0]


def _phone_on_cooldown(phone_normalized: str) -> bool:
    """
    True if this phone already has a final (non-respin) spin within the last 24 hours.
    After 24 hours they may spin again. Respin outcomes do not start the cooldown.
    """
    cutoff = timezone.now() - SPIN_COOLDOWN
    return LuckyWheelSpin.objects.filter(
        phone_normalized=phone_normalized,
        prize__is_respin=False,
        created_at__gte=cutoff,
    ).exists()


class LuckyWheelPageView(View):
    template_name = 'lucky-wheel.html'

    def get(self, request):
        lang = get_language_from_request(request)
        prizes = _active_prizes()
        prizes_payload = [p.to_wheel_dict(lang) for p in prizes]
        prize_list = [
            {
                'title': p.result_title(lang),
                'respin': bool(p.is_respin),
            }
            for p in prizes
        ]
        ui = {
            'headline': _("Spin Academor's wheel, win a gift!"),
            'lead': _(
                'Enter your mobile number and spin the wheel. '
                'Our character will spin the wheel for you. '
                'Whatever gift your luck brings, our team will contact you to present it!'
            ),
            'phone_label': _('Mobile number'),
            'phone_placeholder': _('Mobile number'),
            'spin_btn': _('Spin the wheel'),
            'spinning_btn': _('Spinning…'),
            'spin_again_btn': _('Spin again'),
            'note': _(
                'With each mobile number you can spin the wheel only once within 24 hours.'
            ),
            'close': _('Close'),
            'ok': _('OK'),
            'phone_invalid': _('Please enter a valid phone number.'),
            'already_spun': _(
                'This mobile number has already spun within the last 24 hours. '
                'Please try again later.'
            ),
            'no_prizes': _('The lucky wheel is not available right now.'),
            'prizes_heading': _('Possible prizes'),
            'win_prefix': _('Congratulations!'),
            'win_gift': _('You won a gift!'),
            'win_contact': _('You can contact our team.'),
            'whatsapp_btn': _('WhatsApp'),
            'respin_help': _('You can spin the wheel one more time.'),
            'lose_title': _('Next time :('),
            'lose_help': _('Please try again in 24 hours.'),
            'network_error': _('Something went wrong. Please try again.'),
        }
        contact = serialize_contact(get_contact(lang), lang)
        wa_digits = ''
        if contact:
            wa_digits = contact.get('whatsapp_number_me') or contact.get('whatsapp_number_2_me') or ''
        whatsapp_url = f'https://wa.me/{wa_digits}' if wa_digits else ''
        ui['whatsapp_url'] = whatsapp_url
        context = {
            'language': lang,
            'background_image': get_background_image('about'),
            'page_title': _('Lucky Wheel'),
            'prizes_json': json.dumps(prizes_payload, ensure_ascii=False),
            'ui_json': json.dumps(ui, ensure_ascii=False),
            'spin_url': reverse('projects:lucky-wheel-spin'),
            'has_prizes': bool(prizes),
            'prize_list': prize_list,
            'phone_form': LuckyWheelPhoneForm(),
            'whatsapp_url': whatsapp_url,
        }
        return render(request, self.template_name, context)


@method_decorator(require_POST, name='dispatch')
class LuckyWheelSpinView(View):
    """Validate phone, pick a prize server-side, persist spin, return result."""

    def post(self, request):
        lang = get_language_from_request(request)

        content_type = (request.content_type or '').lower()
        if 'application/json' in content_type:
            try:
                payload = json.loads(request.body.decode('utf-8') or '{}')
            except (TypeError, ValueError, UnicodeDecodeError):
                payload = {}
            form = LuckyWheelPhoneForm({'phone': payload.get('phone', '')})
        else:
            form = LuckyWheelPhoneForm(request.POST)

        if not form.is_valid():
            err = form.errors.get('phone')
            message = err[0] if err else _('Please enter a valid phone number.')
            return JsonResponse({'ok': False, 'error': message}, status=400)

        phone = form.cleaned_data['phone']
        phone_key = _normalize_phone_key(phone)
        if not phone_key:
            return JsonResponse(
                {'ok': False, 'error': _('Please enter a valid phone number.')},
                status=400,
            )

        if _phone_on_cooldown(phone_key):
            return JsonResponse(
                {
                    'ok': False,
                    'error': _(
                        'This mobile number has already spun within the last 24 hours. '
                        'Please try again later.'
                    ),
                },
                status=409,
            )

        prizes = _active_prizes()
        if not prizes:
            return JsonResponse(
                {'ok': False, 'error': _('The lucky wheel is not available right now.')},
                status=503,
            )

        prize = _pick_weighted_prize(prizes)
        index = next((i for i, p in enumerate(prizes) if p.pk == prize.pk), 0)
        title = prize.result_title(lang)
        code = (prize.code or '').strip()

        LuckyWheelSpin.objects.create(
            phone=phone,
            phone_normalized=phone_key,
            prize=prize,
            prize_title=title,
            prize_code=code,
        )

        data = prize.to_wheel_dict(lang)
        data['index'] = index
        return JsonResponse({'ok': True, 'prize': data})
