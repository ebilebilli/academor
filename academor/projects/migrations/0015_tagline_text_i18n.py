from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0014_remove_full_package_tab'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tagline',
            old_name='text',
            new_name='text_az',
        ),
        migrations.AddField(
            model_name='tagline',
            name='text_en',
            field=models.TextField(
                blank=True,
                validators=[django.core.validators.MaxLengthValidator(400)],
                verbose_name='Description (EN)',
            ),
        ),
        migrations.AddField(
            model_name='tagline',
            name='text_ru',
            field=models.TextField(
                blank=True,
                validators=[django.core.validators.MaxLengthValidator(400)],
                verbose_name='Description (RU)',
            ),
        ),
        migrations.AlterField(
            model_name='tagline',
            name='text_az',
            field=models.TextField(
                blank=True,
                validators=[django.core.validators.MaxLengthValidator(400)],
                verbose_name='Description (AZ)',
            ),
        ),
    ]
