from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0008_lesson_subject'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lesson',
            name='title',
        ),
        migrations.AlterField(
            model_name='lesson',
            name='subject',
            field=models.CharField(
                choices=[
                    ('general_english', 'General English'),
                    ('speaking', 'Speaking'),
                    ('ielts', 'IELTS'),
                    ('gmat', 'GMAT'),
                    ('gre', 'GRE'),
                    ('sat', 'SAT'),
                    ('yos', 'YÖS'),
                    ('ales', 'ALES'),
                    ('study_abroad', 'Study abroad'),
                    ('other', 'Other'),
                ],
                db_index=True,
                max_length=32,
                verbose_name='Topic',
            ),
        ),
    ]
