from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0060_quizresult_teacher_correct_answers'),
    ]

    operations = [
        migrations.AddField(
            model_name='listeningquestion',
            name='question_config',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='Word limits, alternatives, etc.',
                verbose_name='Question config',
            ),
        ),
        migrations.AlterField(
            model_name='listeningquestion',
            name='correct_answer',
            field=models.CharField(
                blank=True,
                help_text='Exact text for gap-fill tasks or the matching option label.',
                max_length=500,
                verbose_name='Correct answer',
            ),
        ),
    ]
