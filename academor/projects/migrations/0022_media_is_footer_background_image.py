from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0021_merge_0020_conflict'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='is_footer_background_image',
            field=models.BooleanField(default=False, verbose_name='Footer background image'),
        ),
    ]
