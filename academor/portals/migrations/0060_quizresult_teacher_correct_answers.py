from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0059_remove_quizresult_unique_attempt'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizresult',
            name='teacher_correct_answers',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='Reading review: map of question id → teacher-entered correct answer.',
                verbose_name='Teacher correct answers',
            ),
        ),
    ]
