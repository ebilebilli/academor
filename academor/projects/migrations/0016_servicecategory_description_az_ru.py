import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0015_remove_academy_statistic'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicecategory',
            name='description_az',
            field=ckeditor.fields.RichTextField(blank=True, verbose_name='Description (AZ)'),
        ),
        migrations.AddField(
            model_name='servicecategory',
            name='description_ru',
            field=ckeditor.fields.RichTextField(blank=True, verbose_name='Description (RU)'),
        ),
    ]
