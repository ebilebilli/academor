from django.db import migrations


def clear_student_service_enrollments(apps, schema_editor):
    """Remove auto-filled enrollments from migration 0044 backfill; assign manually in admin."""
    StudentCourseSpecialization = apps.get_model('portals', 'StudentCourseSpecialization')
    StudentCourseSpecialization.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0044_student_course_specialization'),
    ]

    operations = [
        migrations.RunPython(clear_student_service_enrollments, migrations.RunPython.noop),
    ]
