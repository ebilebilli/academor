from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0028_alter_servicehighlight_title_az_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='media',
            name='image_focal_point',
        ),
    ]
