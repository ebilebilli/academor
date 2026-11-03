"""Bring the enquiries collected before the CRM existed into it as leads.

Only fresh unread ones land as "new"; anything older than 30 days (or already read in the
old admin) comes in as "contacted", so the board does not open with years of stale cards.
"""

import re
from datetime import timedelta

from django.db import migrations
from django.utils import timezone


def _key(phone):
    digits = re.sub(r'\D', '', phone or '')
    return digits[-9:] if len(digits) >= 7 else ''


def backfill(apps, schema_editor):
    Lead = apps.get_model('portals', 'Lead')
    Activity = apps.get_model('portals', 'LeadActivity')
    ContactInquiry = apps.get_model('projects', 'ContactInquiry')
    StudyAbroad = apps.get_model('projects', 'StudyAbroadApplication')
    UserResult = apps.get_model('projects', 'UserResult')
    cutoff = timezone.now() - timedelta(days=30)
    by_phone = {}

    def add(*, name, phone, email, source, interest, level, message, created_at, is_read, link):
        key = _key(phone)
        status = 'contacted' if (is_read or (created_at and created_at < cutoff)) else 'new'
        if key and key in by_phone:
            lead = by_phone[key]
            Activity.objects.create(lead=lead, kind='message', created_at=created_at or timezone.now(),
                                    text=f'Yenidən müraciət etdi — {interest}'.strip(' —'))
            for field, obj in link.items():
                if getattr(lead, f'{field}_id') is None:
                    setattr(lead, field, obj)
                    lead.save(update_fields=[field])
            return
        lead = Lead.objects.create(
            full_name=(name or '—')[:200], phone=(phone or '')[:40], email=email or '', source=source,
            interest=(interest or '')[:200], level=(level or '')[:20], message=message or '',
            status=status, created_at=created_at or timezone.now(), **link,
        )
        Activity.objects.create(lead=lead, kind='created', created_at=lead.created_at,
                                text='CRM-dən əvvəlki müraciət (köçürüldü)')
        if key:
            by_phone[key] = lead

    rows = []
    for o in ContactInquiry.objects.all():
        rows.append((o.created_at, dict(name=o.full_name, phone=o.mobile_number, email=o.email or '',
                     source='contact_form', interest=o.subject or '', level='', message=o.info or '',
                     is_read=o.is_read, link={'contact_inquiry': o})))
    for o in StudyAbroad.objects.all():
        rows.append((o.created_at, dict(name=o.full_name, phone=o.phone_number, email='',
                     source='study_abroad', interest='Xaricdə təhsil: ' + ', '.join(
                         b for b in (o.desired_country, o.desired_major) if b),
                     level='', message='', is_read=False, link={'study_abroad_application': o})))
    for o in UserResult.objects.all():
        rows.append((o.created_at, dict(name=f'{o.first_name} {o.last_name}'.strip(), phone=o.number,
                     email=o.email or '', source='level_test', interest='Səviyyə testi', level=o.level or '',
                     message=f'Səviyyə testi: {o.level} ({o.score} bal)', is_read=False,
                     link={'level_test_result': o})))
    rows.sort(key=lambda r: r[0] or timezone.now())
    for created_at, kw in rows:
        add(created_at=created_at, **kw)


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0124_crm_leads_and_billing'),
    ]

    operations = [
        migrations.RunPython(backfill, migrations.RunPython.noop),
    ]
