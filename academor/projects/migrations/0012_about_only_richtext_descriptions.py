import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0011_test_localized_fields'),
    ]

    operations = [
        migrations.RemoveField(model_name='about', name='main_title_az'),
        migrations.RemoveField(model_name='about', name='main_title_en'),
        migrations.RemoveField(model_name='about', name='main_title_ru'),
        migrations.RemoveField(model_name='about', name='second_title_az'),
        migrations.RemoveField(model_name='about', name='second_title_en'),
        migrations.RemoveField(model_name='about', name='second_title_ru'),
        migrations.AlterField(
            model_name='about',
            name='description_az',
            field=ckeditor.fields.RichTextField(verbose_name='Text (AZ)'),
        ),
        migrations.AlterField(
            model_name='about',
            name='description_en',
            field=ckeditor.fields.RichTextField(verbose_name='Text (EN)'),
        ),
        migrations.AlterField(
            model_name='about',
            name='description_ru',
            field=ckeditor.fields.RichTextField(verbose_name='Text (RU)'),
        ),
    ]
