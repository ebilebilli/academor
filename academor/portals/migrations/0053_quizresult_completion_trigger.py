from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0052_listeningquestion_variant_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizresult',
            name='completion_trigger',
            field=models.CharField(
                choices=[
                    ('manual', 'Submitted by student'),
                    ('time_limit', 'Auto-submitted when time ran out'),
                    ('auto_leave', 'Auto-submitted when student left'),
                ],
                default='manual',
                max_length=20,
                verbose_name='Completion trigger',
            ),
        ),
    ]
