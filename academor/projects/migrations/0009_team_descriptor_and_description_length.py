from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0008_tagline_localized_hero_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='description',
            field=models.TextField(
                null=True,
                blank=True,
                validators=[django.core.validators.MaxLengthValidator(4000)],
                verbose_name='Description',
            ),
        ),
        migrations.AddField(
            model_name='team',
            name='descriptor',
            field=models.FileField(
                upload_to='team/descriptors/',
                null=True,
                blank=True,
                verbose_name='Description file',
            ),
        ),
    ]

