from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0022_classroom_services'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='is_time_limited',
            field=models.BooleanField(
                default=False,
                help_text='When enabled, set a time limit in minutes for the student attempt.',
                verbose_name='Time limited',
            ),
        ),
        migrations.AddField(
            model_name='quiz',
            name='time_limit_minutes',
            field=models.PositiveIntegerField(
                blank=True,
                help_text='Required when time limited is enabled.',
                null=True,
                verbose_name='Time limit (minutes)',
            ),
        ),
    ]
