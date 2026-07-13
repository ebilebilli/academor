from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0022_service_bullet_list'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='is_mock_tests_page_background_image',
            field=models.BooleanField(
                default=False,
                verbose_name='Mock tests page background image',
            ),
        ),
    ]
