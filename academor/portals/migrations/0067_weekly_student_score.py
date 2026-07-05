from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0066_alter_quiz_is_essay'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeeklyStudentScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week_start', models.DateField(db_index=True, help_text='Monday of the scored week.', verbose_name='Week start')),
                (
                    'score',
                    models.DecimalField(
                        decimal_places=1,
                        help_text='Score out of 10 for the week.',
                        max_digits=4,
                        validators=[
                            MinValueValidator(0),
                            MaxValueValidator(10),
                        ],
                        verbose_name='Score',
                    ),
                ),
                ('comment', models.TextField(blank=True, verbose_name='Comment')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                (
                    'student',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='weekly_scores',
                        to='portals.studentprofile',
                        verbose_name='Student',
                    ),
                ),
                (
                    'teacher',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='weekly_scores_given',
                        to='portals.teacherprofile',
                        verbose_name='Teacher',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Weekly student score',
                'verbose_name_plural': 'Weekly student scores',
                'ordering': ('-week_start', '-updated_at', '-id'),
            },
        ),
        migrations.AddConstraint(
            model_name='weeklystudentscore',
            constraint=models.UniqueConstraint(
                fields=('student', 'teacher', 'week_start'),
                name='portals_weekly_score_unique_student_teacher_week',
            ),
        ),
    ]
