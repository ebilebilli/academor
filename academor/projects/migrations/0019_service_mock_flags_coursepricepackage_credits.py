from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0018_media_portal_background_flag'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='is_mock_test',
            field=models.BooleanField(
                default=False,
                help_text='If enabled, this service appears under Mock tests (not in general courses/services).',
                verbose_name='Mock test service',
            ),
        ),
        migrations.AddField(
            model_name='service',
            name='ielts_mock_test',
            field=models.BooleanField(
                default=False,
                help_text='Enable IELTS mock test pricing and portal packages for this service.',
                verbose_name='IELTS mock test',
            ),
        ),
        migrations.AddField(
            model_name='service',
            name='sat_mock_test',
            field=models.BooleanField(
                default=False,
                help_text='Enable SAT mock test pricing and portal packages for this service.',
                verbose_name='SAT mock test',
            ),
        ),
        migrations.AddField(
            model_name='coursepricepackage',
            name='credits',
            field=models.PositiveIntegerField(
                blank=True,
                help_text='Number of mock test credits granted after purchase. Used when the parent service is a mock test service.',
                null=True,
                verbose_name='Mock test credits',
            ),
        ),
    ]
