from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0111_quiz_shared_media'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizquestion',
            name='is_dropdown',
            field=models.BooleanField(
                default=False,
                help_text='Show answer choices in a dropdown menu instead of a list. Use this when there are too many options for radio buttons.',
                verbose_name='Dropdown answers',
            ),
        ),
    ]
