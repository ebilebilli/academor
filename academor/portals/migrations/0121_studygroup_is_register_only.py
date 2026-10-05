from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0120_attendance_register_guest'),
    ]

    operations = [
        migrations.AddField(
            model_name='studygroup',
            name='is_register_only',
            field=models.BooleanField(
                default=False,
                help_text='Manual register group — not shown in schedule/lessons lists.',
                verbose_name='Attendance register only',
            ),
        ),
    ]
