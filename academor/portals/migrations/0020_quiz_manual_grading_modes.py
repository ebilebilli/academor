from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0019_quiz_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='is_essay',
            field=models.BooleanField(
                default=False,
                help_text='Written work — teacher grades and replies with corrections.',
                verbose_name='Essay (manual review)',
            ),
        ),
        migrations.AddField(
            model_name='quiz',
            name='is_listening',
            field=models.BooleanField(
                default=False,
                help_text=(
                    'Teacher reviews the submission and writes feedback. '
                    'No multiple-choice variants — only one manual mode can be active.'
                ),
                verbose_name='Listening (manual review)',
            ),
        ),
        migrations.AddField(
            model_name='quiz',
            name='is_speaking',
            field=models.BooleanField(
                default=False,
                help_text='Speaking task — teacher grades and replies with corrections.',
                verbose_name='Speaking (manual review)',
            ),
        ),
        migrations.AddField(
            model_name='quizresult',
            name='reviewed_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Reviewed at'),
        ),
        migrations.AddField(
            model_name='quizresult',
            name='student_submission',
            field=models.TextField(
                blank=True,
                help_text='Essay / listening / speaking response from the student.',
                verbose_name='Student submission',
            ),
        ),
        migrations.AddField(
            model_name='quizresult',
            name='teacher_feedback',
            field=models.TextField(
                blank=True,
                help_text='Corrections, reply, and comments from the teacher.',
                verbose_name='Teacher feedback',
            ),
        ),
        migrations.AlterField(
            model_name='quizresult',
            name='given_answers',
            field=models.JSONField(
                default=dict,
                help_text='Map of question id → selected answer (variant quizzes) or free text.',
                verbose_name='Given answers',
            ),
        ),
        migrations.AlterField(
            model_name='quizresult',
            name='total_score',
            field=models.FloatField(
                blank=True,
                help_text='Set by teacher for manual-review quizzes.',
                null=True,
                verbose_name='Total score',
            ),
        ),
        migrations.AddConstraint(
            model_name='quiz',
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(is_listening=False) | models.Q(is_essay=False)
                ) & (
                    models.Q(is_listening=False) | models.Q(is_speaking=False)
                ) & (
                    models.Q(is_essay=False) | models.Q(is_speaking=False)
                ),
                name='portals_quiz_manual_mode_at_most_one',
            ),
        ),
    ]
