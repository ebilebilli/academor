from django.db import migrations, models


def copy_parent_student_to_m2m(apps, schema_editor):
    ParentProfile = apps.get_model('portals', 'ParentProfile')
    for profile in ParentProfile.objects.exclude(student_id__isnull=True).iterator():
        profile.students.add(profile.student_id)


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0009_remove_lesson_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='parentprofile',
            name='students',
            field=models.ManyToManyField(
                related_name='parent_profiles',
                to='portals.studentprofile',
                verbose_name='Students',
            ),
        ),
        migrations.RunPython(copy_parent_student_to_m2m, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='parentprofile',
            name='student',
        ),
    ]
