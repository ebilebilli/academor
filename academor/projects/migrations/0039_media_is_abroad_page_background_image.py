# Generated manually for Study Abroad page header background

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0038_remove_servicecategory_lesson_hours_az_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='is_abroad_page_background_image',
            field=models.BooleanField(
                default=False,
                verbose_name='Study abroad page background image',
            ),
        ),
    ]
