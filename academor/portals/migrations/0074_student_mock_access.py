from django.db import migrations, models
import django.db.models.deletion


def seed_mock_access(apps, schema_editor):
    StudentCourseSpecialization = apps.get_model('portals', 'StudentCourseSpecialization')
    StudentMockAccess = apps.get_model('portals', 'StudentMockAccess')

    student_ids = (
        StudentCourseSpecialization.objects.filter(
            is_active=True,
            course_type='ielts',
        )
        .values_list('student_id', flat=True)
        .distinct()
    )
    batch = [
        StudentMockAccess(student_id=student_id, is_active=True)
        for student_id in student_ids
    ]
    if batch:
        StudentMockAccess.objects.bulk_create(batch, ignore_conflicts=True)


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0073_quiz_assignment'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentMockAccess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'is_active',
                    models.BooleanField(
                        default=False,
                        help_text='When enabled, the IELTS student can start a mock test.',
                        verbose_name='Active',
                    ),
                ),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                (
                    'assigned_by',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='mock_access_granted',
                        to='portals.teacherprofile',
                        verbose_name='Assigned by',
                    ),
                ),
                (
                    'student',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='mock_access',
                        to='portals.studentprofile',
                        verbose_name='Student',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Student mock access',
                'verbose_name_plural': 'Student mock access',
                'ordering': ('-updated_at', 'id'),
            },
        ),
        migrations.RunPython(seed_mock_access, migrations.RunPython.noop),
    ]
