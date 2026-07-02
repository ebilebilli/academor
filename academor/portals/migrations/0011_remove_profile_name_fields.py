from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0010_parent_students_m2m'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studentprofile',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='studentprofile',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='parentprofile',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='parentprofile',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='teacherprofile',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='teacherprofile',
            name='last_name',
        ),
        migrations.AlterModelOptions(
            name='studentprofile',
            options={
                'ordering': ('user__username', 'id'),
                'verbose_name': 'Student profile',
                'verbose_name_plural': 'Student profiles',
            },
        ),
        migrations.AlterModelOptions(
            name='parentprofile',
            options={
                'ordering': ('user__username', 'id'),
                'verbose_name': 'Parent profile',
                'verbose_name_plural': 'Parent profiles',
            },
        ),
        migrations.AlterModelOptions(
            name='teacherprofile',
            options={
                'ordering': ('user__username', 'id'),
                'verbose_name': 'Teacher profile',
                'verbose_name_plural': 'Teacher profiles',
            },
        ),
    ]
