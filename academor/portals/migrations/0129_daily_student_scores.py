"""Weekly scores become daily scores.

``week_start`` is renamed to ``score_date`` (the column is renamed, no data is lost):
a score saved for a week keeps that week's Monday as its day. ``study_group`` becomes
optional so a student without a group can be scored too; one score a day per teacher
and student is enforced for those rows by a conditional unique constraint.
"""

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0128_student_services_from_groups_and_register_students'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='weeklystudentscore',
            name='portals_weekly_score_unique_student_group_week',
        ),
        migrations.RenameField(
            model_name='weeklystudentscore',
            old_name='week_start',
            new_name='score_date',
        ),
        migrations.AlterField(
            model_name='weeklystudentscore',
            name='score_date',
            field=models.DateField(db_index=True, help_text='Day the score is for.', verbose_name='Date'),
        ),
        migrations.AlterField(
            model_name='weeklystudentscore',
            name='study_group',
            field=models.ForeignKey(
                blank=True,
                help_text='Group the score was given in; empty for a student without a group.',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='weekly_scores',
                to='portals.studygroup',
                verbose_name='Study group',
            ),
        ),
        migrations.AlterField(
            model_name='weeklystudentscore',
            name='score',
            field=models.DecimalField(
                decimal_places=1,
                help_text='Score out of 10 for the day.',
                max_digits=4,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(10),
                ],
                verbose_name='Score',
            ),
        ),
        migrations.AlterModelOptions(
            name='weeklystudentscore',
            options={
                'ordering': ('-score_date', '-updated_at', '-id'),
                'verbose_name': 'Daily student score',
                'verbose_name_plural': 'Daily student scores',
            },
        ),
        migrations.AddConstraint(
            model_name='weeklystudentscore',
            constraint=models.UniqueConstraint(
                fields=('student', 'teacher', 'study_group', 'score_date'),
                name='portals_weekly_score_unique_student_group_week',
            ),
        ),
        migrations.AddConstraint(
            model_name='weeklystudentscore',
            constraint=models.UniqueConstraint(
                condition=models.Q(study_group__isnull=True),
                fields=('student', 'teacher', 'score_date'),
                name='portals_daily_score_unique_student_no_group_day',
            ),
        ),
    ]
