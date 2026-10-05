from django.db import migrations, models
import django.db.models.deletion


def backfill_attendance_group(apps, schema_editor):
    Attendance = apps.get_model('portals', 'Attendance')
    for row in Attendance.objects.select_related('schedule').iterator():
        if row.schedule_id and not row.group_id:
            Attendance.objects.filter(pk=row.pk).update(group_id=row.schedule.group_id)


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0118_split_sat_verbal_math_categories'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='group',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='group_attendances',
                to='portals.studygroup',
                verbose_name='Group',
            ),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='schedule',
            field=models.ForeignKey(
                blank=True,
                help_text='Optional class slot. Monthly register marks may have no slot.',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='attendances',
                to='portals.schedule',
                verbose_name='Schedule',
            ),
        ),
        migrations.RunPython(backfill_attendance_group, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name='attendance',
            constraint=models.UniqueConstraint(
                condition=models.Q(('schedule__isnull', True)),
                fields=('group', 'student', 'session_date'),
                name='portals_attendance_unique_register_day',
            ),
        ),
        migrations.AddConstraint(
            model_name='attendance',
            constraint=models.CheckConstraint(
                condition=models.Q(('schedule__isnull', False), ('group__isnull', False), _connector='OR'),
                name='portals_attendance_schedule_or_group',
            ),
        ),
    ]
