from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0113_quiz_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentprofile',
            name='lessons_per_month',
            field=models.PositiveSmallIntegerField(
                blank=True,
                help_text='Expected lessons per month for this student (e.g. 8 or 12).',
                null=True,
                verbose_name='Lessons per month',
            ),
        ),
        migrations.AddField(
            model_name='studentprofile',
            name='program_month',
            field=models.PositiveSmallIntegerField(
                blank=True,
                help_text='Which month of the program the student is in (1, 2, 3…).',
                null=True,
                verbose_name='Program month',
            ),
        ),
    ]
