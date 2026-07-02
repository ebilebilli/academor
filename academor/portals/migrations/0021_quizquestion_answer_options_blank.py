from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0020_quiz_manual_grading_modes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizquestion',
            name='answer_options',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='List of answer choices shown to the student. Not used for manual-review quizzes.',
                verbose_name='Answer options',
            ),
        ),
    ]
