from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0017_alter_lesson_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studentprofile',
            name='assigned_teacher',
        ),
        migrations.DeleteModel(
            name='StudentCourseSpecialization',
        ),
    ]
