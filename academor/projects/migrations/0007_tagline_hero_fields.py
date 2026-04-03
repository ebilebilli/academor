from django.db import migrations, models
from django.core.validators import MaxLengthValidator


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0006_media_courses_tests_bg_remove_footer_bg'),
    ]

    operations = [
        migrations.AddField(
            model_name='tagline',
            name='heading_small',
            field=models.CharField(
                max_length=150,
                blank=True,
                verbose_name='Hero small heading',
            ),
        ),
        migrations.AddField(
            model_name='tagline',
            name='heading_main',
            field=models.CharField(
                max_length=200,
                blank=True,
                verbose_name='Hero main heading',
            ),
        ),
        migrations.AddField(
            model_name='tagline',
            name='body',
            field=models.TextField(
                validators=[MaxLengthValidator(400)],
                blank=True,
                verbose_name='Hero description text',
            ),
        ),
    ]

