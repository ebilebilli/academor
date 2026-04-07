from django.db import migrations
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0025_alter_servicehighlight_description_200'),
    ]

    operations = [
        migrations.AddField(
            model_name='abroadmodel',
            name='description_az',
            field=ckeditor.fields.RichTextField(blank=True, verbose_name='Description (AZ)'),
        ),
        migrations.AddField(
            model_name='abroadmodel',
            name='description_en',
            field=ckeditor.fields.RichTextField(blank=True, verbose_name='Description (EN)'),
        ),
        migrations.AddField(
            model_name='abroadmodel',
            name='description_ru',
            field=ckeditor.fields.RichTextField(blank=True, verbose_name='Description (RU)'),
        ),
    ]
