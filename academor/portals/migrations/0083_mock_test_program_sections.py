from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0082_quiz_is_ielts_is_sat'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='is_math',
            field=models.BooleanField(
                default=False,
                help_text='SAT-style math with auto-scored answers. Only one quiz format can be active.',
                verbose_name='Math (auto-scored)',
            ),
        ),
        migrations.RemoveConstraint(
            model_name='quiz',
            name='portals_quiz_format_at_most_one',
        ),
        migrations.AddConstraint(
            model_name='quiz',
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(is_listening=False) | models.Q(is_essay=False)
                ) & (
                    models.Q(is_listening=False) | models.Q(is_speaking=False)
                ) & (
                    models.Q(is_listening=False) | models.Q(is_reading=False)
                ) & (
                    models.Q(is_essay=False) | models.Q(is_speaking=False)
                ) & (
                    models.Q(is_essay=False) | models.Q(is_reading=False)
                ) & (
                    models.Q(is_speaking=False) | models.Q(is_reading=False)
                ) & (
                    models.Q(is_math=False) | models.Q(is_listening=False)
                ) & (
                    models.Q(is_math=False) | models.Q(is_essay=False)
                ) & (
                    models.Q(is_math=False) | models.Q(is_speaking=False)
                ) & (
                    models.Q(is_math=False) | models.Q(is_reading=False)
                ),
                name='portals_quiz_format_at_most_one',
            ),
        ),
        migrations.AddField(
            model_name='ieltsmocktestattempt',
            name='exam_program',
            field=models.CharField(
                choices=[('ielts', 'IELTS'), ('sat', 'SAT')],
                db_index=True,
                default='ielts',
                max_length=16,
                verbose_name='Exam program',
            ),
        ),
        migrations.AlterField(
            model_name='ieltsmocktestattempt',
            name='current_section',
            field=models.CharField(
                choices=[
                    ('listening', 'Listening'),
                    ('reading', 'Reading'),
                    ('writing', 'Writing'),
                    ('speaking', 'Speaking'),
                    ('reading_writing', 'Reading and Writing'),
                    ('math', 'Math'),
                ],
                default='listening',
                max_length=20,
                verbose_name='Current section',
            ),
        ),
        migrations.AlterField(
            model_name='ieltsmocktestattempt',
            name='listening_quiz',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='mock_listening_attempts',
                to='portals.quiz',
                verbose_name='Listening quiz',
            ),
        ),
        migrations.AlterField(
            model_name='ieltsmocktestattempt',
            name='writing_quiz',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='mock_writing_attempts',
                to='portals.quiz',
                verbose_name='Writing quiz',
            ),
        ),
        migrations.AlterField(
            model_name='ieltsmocktestattempt',
            name='speaking_quiz',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='mock_speaking_attempts',
                to='portals.quiz',
                verbose_name='Speaking quiz',
            ),
        ),
        migrations.AddField(
            model_name='ieltsmocktestattempt',
            name='math_quiz',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='mock_math_attempts',
                to='portals.quiz',
                verbose_name='Math quiz',
            ),
        ),
        migrations.AddField(
            model_name='ieltsmocktestattempt',
            name='math_result',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='mock_math_for',
                to='portals.quizresult',
                verbose_name='Math result',
            ),
        ),
        migrations.AlterModelOptions(
            name='ieltsmocktestattempt',
            options={
                'ordering': ('-started_at', '-id'),
                'verbose_name': 'Mock test attempt',
                'verbose_name_plural': 'Mock test attempts',
            },
        ),
    ]
