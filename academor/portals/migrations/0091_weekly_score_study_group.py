from django.db import migrations, models
import django.db.models.deletion


def backfill_weekly_score_study_groups(apps, schema_editor):
    WeeklyStudentScore = apps.get_model('portals', 'WeeklyStudentScore')
    StudyGroup = apps.get_model('portals', 'StudyGroup')

    for score in WeeklyStudentScore.objects.all().iterator():
        if score.study_group_id:
            continue
        group = (
            StudyGroup.objects.filter(
                teacher_id=score.teacher_id,
                students__pk=score.student_id,
            )
            .order_by('id')
            .first()
        )
        if not group:
            continue
        WeeklyStudentScore.objects.filter(pk=score.pk).update(study_group_id=group.pk)


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0090_studentmockaccess_exam_program'),
    ]

    operations = [
        migrations.AddField(
            model_name='weeklystudentscore',
            name='study_group',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='weekly_scores',
                to='portals.studygroup',
                verbose_name='Study group',
                help_text='Weekly score applies to this group membership.',
            ),
        ),
        migrations.RunPython(backfill_weekly_score_study_groups, migrations.RunPython.noop),
        migrations.RemoveConstraint(
            model_name='weeklystudentscore',
            name='portals_weekly_score_unique_student_teacher_week',
        ),
        migrations.AddConstraint(
            model_name='weeklystudentscore',
            constraint=models.UniqueConstraint(
                fields=('student', 'teacher', 'study_group', 'week_start'),
                name='portals_weekly_score_unique_student_group_week',
            ),
        ),
        migrations.AlterField(
            model_name='weeklystudentscore',
            name='study_group',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='weekly_scores',
                to='portals.studygroup',
                verbose_name='Study group',
                help_text='Weekly score applies to this group membership.',
            ),
        ),
    ]
