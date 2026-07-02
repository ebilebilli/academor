from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0036_studygroup_services_m2m'),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='studygroup',
            old_name='services',
            new_name='courses',
        ),
        migrations.RemoveField(
            model_name='studygroup',
            name='level',
        ),
    ]
