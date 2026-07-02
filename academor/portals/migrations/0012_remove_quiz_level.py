from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0011_remove_profile_name_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quiz',
            name='level',
        ),
    ]
