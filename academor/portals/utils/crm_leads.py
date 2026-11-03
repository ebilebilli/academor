"""Turn site forms into CRM leads (one pipeline for every way people reach Academor).

A repeat enquiry from a phone number that already has an open lead does not open a second
card: it is logged on the existing lead instead, so the team sees the whole history.
"""

from __future__ import annotations

import re

from django.db import transaction
from django.utils import timezone

from portals.models import Lead, LeadActivity

OPEN_STATUSES = (Lead.Status.NEW, Lead.Status.CONTACTED, Lead.Status.TRIAL)


def phone_key(phone: str) -> str:
    """Last 9 digits: +994 55 123 45 67, 055 123 45 67 and 551234567 are the same number."""
    digits = re.sub(r'\D', '', phone or '')
    return digits[-9:] if len(digits) >= 7 else ''


def find_open_lead(phone: str):
    key = phone_key(phone)
    if not key:
        return None
    for lead in Lead.objects.filter(status__in=OPEN_STATUSES).exclude(phone='').order_by('-created_at')[:500]:
        if phone_key(lead.phone) == key:
            return lead
    return None


@transaction.atomic
def capture_lead(*, full_name, phone='', email='', source, interest='', level='', message='',
                 created_at=None, link=None):
    """Create a lead, or log a repeat enquiry on the open lead with the same phone.

    link: {'contact_inquiry': obj} / {'study_abroad_application': obj} / {'level_test_result': obj}
    """
    link = link or {}
    created_at = created_at or timezone.now()
    existing = find_open_lead(phone)
    if existing is not None:
        LeadActivity.objects.create(
            lead=existing,
            kind=LeadActivity.Kind.MESSAGE,
            text='Yenidən müraciət etdi ({}){}{}'.format(
                Lead.Source(source).label,
                f' — {interest}' if interest else '',
                f'\n{message}' if message else '',
            ),
            created_at=created_at,
        )
        changed = []
        if level and not existing.level:
            existing.level = level
            changed.append('level')
        for field, obj in link.items():
            if getattr(existing, f'{field}_id') is None:
                setattr(existing, field, obj)
                changed.append(field)
        if changed:
            existing.save(update_fields=changed + ['updated_at'])
        return existing, False

    lead = Lead.objects.create(
        full_name=(full_name or '').strip()[:200] or '—',
        phone=(phone or '').strip()[:40],
        email=(email or '').strip(),
        source=source,
        interest=(interest or '')[:200],
        level=(level or '')[:20],
        message=message or '',
        created_at=created_at,
        **link,
    )
    LeadActivity.objects.create(
        lead=lead, kind=LeadActivity.Kind.CREATED,
        text=f'Müraciət gəldi: {Lead.Source(source).label}', created_at=created_at,
    )
    return lead, True


def lead_from_contact_inquiry(inquiry):
    return capture_lead(
        full_name=inquiry.full_name, phone=inquiry.mobile_number, email=inquiry.email or '',
        source=Lead.Source.CONTACT_FORM, interest=inquiry.subject or '', message=inquiry.info or '',
        created_at=inquiry.created_at, link={'contact_inquiry': inquiry},
    )


def lead_from_study_abroad(application):
    bits = [application.desired_country, application.desired_major]
    detail = [
        f'Səviyyə: {application.get_study_level_display()}' if application.study_level else '',
        f'Format: {application.get_consultation_format_display()}' if application.consultation_format else '',
        f'Büdcə: {application.get_tuition_budget_display()}' if application.tuition_budget else '',
        f'Sertifikatlar: {application.international_certificates}' if application.international_certificates else '',
    ]
    return capture_lead(
        full_name=application.full_name, phone=application.phone_number,
        source=Lead.Source.STUDY_ABROAD,
        interest='Xaricdə təhsil: ' + ', '.join(b for b in bits if b),
        message='\n'.join(d for d in detail if d),
        created_at=application.created_at, link={'study_abroad_application': application},
    )


def lead_from_level_test(result):
    name = f'{result.first_name} {result.last_name}'.strip()
    return capture_lead(
        full_name=name, phone=result.number, email=result.email or '',
        source=Lead.Source.LEVEL_TEST, interest=str(result.test) if result.test_id else '',
        level=result.level or '', message=f'Səviyyə testi: {result.level} ({result.score} bal)',
        created_at=result.created_at, link={'level_test_result': result},
    )
