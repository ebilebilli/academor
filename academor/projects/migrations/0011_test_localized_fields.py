from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0010_team_description_richtext'),
    ]

    operations = [
        migrations.RenameField(
            model_name='test',
            old_name='title',
            new_name='title_en',
        ),
        migrations.RenameField(
            model_name='test',
            old_name='description',
            new_name='description_en',
        ),
        migrations.AddField(
            model_name='test',
            name='title_az',
            field=models.CharField(blank=True, max_length=200, verbose_name='Test title (AZ)'),
        ),
        migrations.AddField(
            model_name='test',
            name='title_ru',
            field=models.CharField(blank=True, max_length=200, verbose_name='Test title (RU)'),
        ),
        migrations.AddField(
            model_name='test',
            name='description_az',
            field=models.TextField(
                blank=True,
                null=True,
                validators=[django.core.validators.MaxLengthValidator(2000)],
                verbose_name='Description (AZ)',
            ),
        ),
        migrations.AddField(
            model_name='test',
            name='description_ru',
            field=models.TextField(
                blank=True,
                null=True,
                validators=[django.core.validators.MaxLengthValidator(2000)],
                verbose_name='Description (RU)',
            ),
        ),
    ]
