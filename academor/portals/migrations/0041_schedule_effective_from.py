from datetime import date

from django.db import migrations, models
from django.utils import timezone


def populate_effective_from(apps, schema_editor):
    Schedule = apps.get_model('portals', 'Schedule')
    for schedule in Schedule.objects.select_related('group').iterator():
        start = getattr(schedule.group, 'start_date', None)
        schedule.effective_from = start or date(2000, 1, 1)
        schedule.save(update_fields=['effective_from'])


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0040_alter_lessoncategory_service'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='effective_from',
            field=models.DateField(
                default=date(2000, 1, 1),
                help_text=(
                    'First calendar date when this weekly slot appears. '
                    'Past weeks and months before this date will not show the slot.'
                ),
                verbose_name='Active from',
            ),
        ),
        migrations.RunPython(populate_effective_from, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='schedule',
            name='effective_from',
            field=models.DateField(
                default=timezone.localdate,
                help_text=(
                    'First calendar date when this weekly slot appears. '
                    'Past weeks and months before this date will not show the slot.'
                ),
                verbose_name='Active from',
            ),
        ),
    ]
