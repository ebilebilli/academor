# Generated manually for customer mock history backfill.

from django.db import migrations
from django.db.models import F
from django.utils import timezone


def abandon_stale_customer_in_progress(apps, schema_editor):
    IeltsMockTestAttempt = apps.get_model('portals', 'IeltsMockTestAttempt')
    now = timezone.now()
    (
        IeltsMockTestAttempt.objects.filter(
            customer_id__isnull=False,
            status='in_progress',
        ).update(
            status='abandoned',
            completed_at=F('started_at'),
        )
    )
    # Ensure completed_at is never null for abandoned rows that had no started_at edge case.
    IeltsMockTestAttempt.objects.filter(
        customer_id__isnull=False,
        status='abandoned',
        completed_at__isnull=True,
    ).update(completed_at=now)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0115_alter_studentprofile_lessons_per_month'),
    ]

    operations = [
        migrations.RunPython(abandon_stale_customer_in_progress, noop_reverse),
    ]
