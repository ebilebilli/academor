from django.db import migrations, models
from django.core.validators import MaxLengthValidator


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0007_tagline_hero_fields'),
    ]

    operations = [
        # Localized hero fields
        migrations.AddField(
            model_name='tagline',
            name='heading_small_az',
            field=models.CharField(
                max_length=150,
                blank=True,
                verbose_name='Hero small heading (AZ)',
            ),
        ),
        migrations.AddField(
            model_name='tagline',
            name='heading_small_en',
            field=models.CharField(
                max_length=150,
                blank=True,
                verbose_name='Hero small heading (EN)',
            ),
        ),
        migrations.AddField(
            model_name='tagline',
            name='heading_small_ru',
            field=models.CharField(
                max_length=150,
                blank=True,
                verbose_name='Hero small heading (RU)',
            ),
        ),
        migrations.AddField(
            model_name='tagline',
            name='heading_main_az',
            field=models.CharField(
                max_length=200,
                blank=True,
                verbose_name='Hero main heading (AZ)',
            ),
        ),
        migrations.AddField(
            model_name='tagline',
            name='heading_main_en',
            field=models.CharField(
                max_length=200,
                blank=True,
                verbose_name='Hero main heading (EN)',
            ),
        ),
        migrations.AddField(
            model_name='tagline',
            name='heading_main_ru',
            field=models.CharField(
                max_length=200,
                blank=True,
                verbose_name='Hero main heading (RU)',
            ),
        ),
        migrations.AddField(
            model_name='tagline',
            name='body_az',
            field=models.TextField(
                validators=[MaxLengthValidator(400)],
                blank=True,
                verbose_name='Hero description (AZ)',
            ),
        ),
        migrations.AddField(
            model_name='tagline',
            name='body_en',
            field=models.TextField(
                validators=[MaxLengthValidator(400)],
                blank=True,
                verbose_name='Hero description (EN)',
            ),
        ),
        migrations.AddField(
            model_name='tagline',
            name='body_ru',
            field=models.TextField(
                validators=[MaxLengthValidator(400)],
                blank=True,
                verbose_name='Hero description (RU)',
            ),
        ),
        # Remove old generic + legacy fields
        migrations.RemoveField(
            model_name='tagline',
            name='text_az',
        ),
        migrations.RemoveField(
            model_name='tagline',
            name='text_en',
        ),
        migrations.RemoveField(
            model_name='tagline',
            name='text_ru',
        ),
        migrations.RemoveField(
            model_name='tagline',
            name='heading_small',
        ),
        migrations.RemoveField(
            model_name='tagline',
            name='heading_main',
        ),
        migrations.RemoveField(
            model_name='tagline',
            name='body',
        ),
    ]

