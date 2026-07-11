from django.db import migrations, models
from django.db.models import Q


def migrate_legacy_is_mock_test(apps, schema_editor):
    Service = apps.get_model('projects', 'Service')
    Service.objects.filter(
        is_mock_test=True,
        ielts_mock_test=False,
        sat_mock_test=False,
    ).update(ielts_mock_test=True)


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0019_service_mock_flags_coursepricepackage_credits'),
    ]

    operations = [
        migrations.RunPython(migrate_legacy_is_mock_test, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='service',
            name='is_mock_test',
        ),
        migrations.AddConstraint(
            model_name='service',
            constraint=models.CheckConstraint(
                condition=~Q(ielts_mock_test=True, sat_mock_test=True),
                name='service_single_mock_test_type',
            ),
        ),
        migrations.AlterField(
            model_name='coursepricepackage',
            name='credits',
            field=models.PositiveIntegerField(
                blank=True,
                help_text='Required when the selected course is an IELTS or SAT mock test service.',
                null=True,
                verbose_name='Mock test credits',
            ),
        ),
        migrations.AlterField(
            model_name='service',
            name='ielts_mock_test',
            field=models.BooleanField(
                default=False,
                help_text='If enabled, this service appears under Mock tests and uses IELTS mock pricing.',
                verbose_name='IELTS mock test',
            ),
        ),
        migrations.AlterField(
            model_name='service',
            name='sat_mock_test',
            field=models.BooleanField(
                default=False,
                help_text='If enabled, this service appears under Mock tests and uses SAT mock pricing.',
                verbose_name='SAT mock test',
            ),
        ),
    ]
